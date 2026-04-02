"""
Tests for the chat router (/api/chat/*).

Mocking strategy:
- get_db      → AsyncMock returning a mock Prisma client
- load_history / create_history / append_messages → AsyncMock (service layer)
- Runner.run_streamed → mock that yields synthetic SSE events (no real OpenAI calls)
"""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def chat_body(text: str, history_id: str | None = None) -> dict:
    """Build the request body that the Vercel AI SDK sends to /stream."""
    body: dict = {
        "messages": [
            {"role": "user", "parts": [{"type": "text", "text": text}]}
        ]
    }
    if history_id:
        body["historyId"] = history_id
    return body


def parse_sse(body: str) -> list[dict]:
    """Parse an SSE response body into a list of event dicts."""
    events = []
    for block in body.split("\n\n"):
        block = block.strip()
        if not block.startswith("data: "):
            continue
        payload = block[6:]
        if payload == "[DONE]":
            events.append({"type": "__done__"})
        else:
            events.append(json.loads(payload))
    return events


class _RawDelta:
    """Mimics the raw event data object from the OpenAI Agents SDK."""
    def __init__(self, delta: str):
        self.type = "response.output_text.delta"
        self.delta = delta


class _Event:
    """Mimics an event yielded by RunResultStreaming.stream_events()."""
    def __init__(self, event_type: str, data=None):
        self.type = event_type
        self.data = data


def make_runner(responses: list[str]):
    """
    Return a mock Runner whose run_streamed() streams the given text chunks.

    Usage:
        with patch("app.routers.chat.Runner", make_runner(["Hello ", "world"])):
            ...
    """
    async def _stream_events():
        for text in responses:
            yield _Event("raw_response_event", _RawDelta(text))

    result = MagicMock()
    result.stream_events = _stream_events

    runner = MagicMock()
    runner.run_streamed.return_value = result
    return runner


def make_history(history_id: str = "hist-1", messages: list | None = None):
    h = MagicMock()
    h.id = history_id
    h.createdAt = datetime(2024, 1, 1, tzinfo=timezone.utc)
    h.updatedAt = datetime(2024, 1, 2, tzinfo=timezone.utc)
    h.messages = messages or []
    return h


def make_message(role: str, content: str, ts: datetime | None = None):
    m = MagicMock()
    m.role = role
    m.content = content
    m.timestamp = ts or datetime(2024, 1, 1, tzinfo=timezone.utc)
    return m


# ---------------------------------------------------------------------------
# POST /api/chat/stream
# ---------------------------------------------------------------------------

class TestStreamEndpoint:

    def test_returns_200_and_sse_content_type(self, client):
        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="h-1")),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", make_runner(["Hi"])),
        ):
            response = client.post("/api/chat/stream", json=chat_body("Hello"))

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

    def test_response_includes_required_sse_headers(self, client):
        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="new-id")),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", make_runner(["Hi"])),
        ):
            response = client.post("/api/chat/stream", json=chat_body("Hello"))

        assert response.headers["x-vercel-ai-ui-message-stream"] == "v1"
        assert response.headers["x-chat-history-id"] == "new-id"
        assert response.headers["cache-control"] == "no-cache"

    def test_sse_body_contains_expected_event_types(self, client):
        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="h-1")),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", make_runner(["Hello"])),
        ):
            response = client.post("/api/chat/stream", json=chat_body("Hi"))

        types = {e["type"] for e in parse_sse(response.text)}
        assert {"start-step", "text-start", "text-delta", "text-end", "finish-step", "__done__"}.issubset(types)

    def test_text_delta_chunks_contain_correct_content(self, client):
        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="h-1")),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", make_runner(["Hello ", "teacher"])),
        ):
            response = client.post("/api/chat/stream", json=chat_body("Hi"))

        deltas = [e["delta"] for e in parse_sse(response.text) if e.get("type") == "text-delta"]
        assert deltas == ["Hello ", "teacher"]

    def test_text_start_and_text_end_share_same_id(self, client):
        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="h-1")),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", make_runner(["Hi"])),
        ):
            response = client.post("/api/chat/stream", json=chat_body("Hi"))

        events = parse_sse(response.text)
        start_id = next(e["id"] for e in events if e.get("type") == "text-start")
        end_id = next(e["id"] for e in events if e.get("type") == "text-end")
        assert start_id == end_id

    # --- history creation ---

    def test_new_conversation_creates_history(self, client):
        mock_create = AsyncMock(return_value="created-hist")
        mock_load = AsyncMock()

        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=mock_load),
            patch("app.routers.chat.create_history", new=mock_create),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", make_runner([])),
        ):
            client.post("/api/chat/stream", json=chat_body("Hello"))

        mock_create.assert_awaited_once()
        mock_load.assert_not_awaited()

    def test_new_conversation_history_id_in_header(self, client):
        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="brand-new")),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", make_runner([])),
        ):
            response = client.post("/api/chat/stream", json=chat_body("Hello"))

        assert response.headers["x-chat-history-id"] == "brand-new"

    # --- existing conversation ---

    def test_existing_conversation_loads_history_not_create(self, client):
        mock_load = AsyncMock(return_value=[{"role": "user", "content": "prev"}])
        mock_create = AsyncMock()

        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=mock_load),
            patch("app.routers.chat.create_history", new=mock_create),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", make_runner(["Reply"])),
        ):
            client.post("/api/chat/stream", json=chat_body("Follow up", history_id="old-hist"))

        mock_load.assert_awaited_once()
        mock_create.assert_not_awaited()

    def test_existing_conversation_echoes_history_id_in_header(self, client):
        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock()),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", make_runner([])),
        ):
            response = client.post(
                "/api/chat/stream", json=chat_body("Hi", history_id="existing-99")
            )

        assert response.headers["x-chat-history-id"] == "existing-99"

    def test_prior_messages_prepended_to_agent_input(self, client):
        prior = [{"role": "user", "content": "earlier question"}]
        runner = make_runner(["ok"])

        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=prior)),
            patch("app.routers.chat.create_history", new=AsyncMock()),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", runner),
        ):
            client.post("/api/chat/stream", json=chat_body("New question", history_id="h-x"))

        _, kwargs = runner.run_streamed.call_args
        agent_input = kwargs["input"]
        assert agent_input[0] == {"role": "user", "content": "earlier question"}
        assert agent_input[-1] == {"role": "user", "content": "New question"}

    # --- message persistence ---

    def test_messages_persisted_after_stream_completes(self, client):
        mock_append = AsyncMock()

        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="h-persist")),
            patch("app.routers.chat.append_messages", new=mock_append),
            patch("app.routers.chat.Runner", make_runner(["Hello ", "world"])),
        ):
            client.post("/api/chat/stream", json=chat_body("Save this"))

        mock_append.assert_awaited_once()
        kwargs = mock_append.call_args.kwargs
        assert kwargs["history_id"] == "h-persist"
        assert kwargs["user_message"] == "Save this"
        assert kwargs["assistant_message"] == "Hello world"

    def test_persisted_assistant_message_is_full_concatenated_response(self, client):
        mock_append = AsyncMock()

        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="h-1")),
            patch("app.routers.chat.append_messages", new=mock_append),
            patch("app.routers.chat.Runner", make_runner(["Chunk1", " Chunk2", " Chunk3"])),
        ):
            client.post("/api/chat/stream", json=chat_body("Question"))

        assert mock_append.call_args.kwargs["assistant_message"] == "Chunk1 Chunk2 Chunk3"

    # --- max turns exceeded ---

    def test_max_turns_exceeded_streams_fallback_message(self, client):
        from agents.exceptions import MaxTurnsExceeded

        async def _stream_raises():
            yield _Event("raw_response_event", _RawDelta("Partial..."))
            raise MaxTurnsExceeded("limit hit")

        result = MagicMock()
        result.stream_events = _stream_raises
        runner = MagicMock()
        runner.run_streamed.return_value = result

        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="h-max")),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", runner),
        ):
            response = client.post("/api/chat/stream", json=chat_body("Complex task"))

        assert response.status_code == 200
        deltas = [e["delta"] for e in parse_sse(response.text) if e.get("type") == "text-delta"]
        full_text = "".join(deltas)
        assert "too many steps" in full_text

    def test_max_turns_exceeded_still_persists_messages(self, client):
        from agents.exceptions import MaxTurnsExceeded

        async def _stream_raises():
            yield _Event("raw_response_event", _RawDelta("Start"))
            raise MaxTurnsExceeded("limit hit")

        result = MagicMock()
        result.stream_events = _stream_raises
        runner = MagicMock()
        runner.run_streamed.return_value = result
        mock_append = AsyncMock()

        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="h-max")),
            patch("app.routers.chat.append_messages", new=mock_append),
            patch("app.routers.chat.Runner", runner),
        ):
            client.post("/api/chat/stream", json=chat_body("Hard task"))

        mock_append.assert_awaited_once()

    # --- non-text events from the agent ---

    def test_non_output_delta_events_produce_no_text_delta_chunks(self, client):
        async def _other_events():
            yield _Event("agent_updated_stream_event")
            yield _Event("run_item_stream_event")
            yield _Event("raw_response_event", _RawDelta("real"))

        result = MagicMock()
        result.stream_events = _other_events
        runner = MagicMock()
        runner.run_streamed.return_value = result

        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="h-1")),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", runner),
        ):
            response = client.post("/api/chat/stream", json=chat_body("Hi"))

        deltas = [e["delta"] for e in parse_sse(response.text) if e.get("type") == "text-delta"]
        assert deltas == ["real"]

    # --- edge cases ---

    def test_empty_messages_list_sends_empty_user_message(self, client):
        mock_append = AsyncMock()

        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="h-1")),
            patch("app.routers.chat.append_messages", new=mock_append),
            patch("app.routers.chat.Runner", make_runner([])),
        ):
            response = client.post("/api/chat/stream", json={"messages": []})

        assert response.status_code == 200
        assert mock_append.call_args.kwargs["user_message"] == ""

    def test_agent_called_with_max_turns_25(self, client):
        runner = make_runner(["ok"])

        with (
            patch("app.routers.chat.get_db", new=AsyncMock(return_value=MagicMock())),
            patch("app.routers.chat.load_history", new=AsyncMock(return_value=[])),
            patch("app.routers.chat.create_history", new=AsyncMock(return_value="h-1")),
            patch("app.routers.chat.append_messages", new=AsyncMock()),
            patch("app.routers.chat.Runner", runner),
        ):
            client.post("/api/chat/stream", json=chat_body("Hello"))

        _, kwargs = runner.run_streamed.call_args
        assert kwargs["max_turns"] == 25


# ---------------------------------------------------------------------------
# GET /api/chat/histories
# ---------------------------------------------------------------------------

class TestGetHistories:

    def test_returns_200_with_list(self, client):
        mock_db = MagicMock()
        mock_db.chathistory.find_many = AsyncMock(return_value=[])

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            response = client.get("/api/chat/histories")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_returns_history_with_expected_fields(self, client):
        hist = make_history("h-1", messages=[make_message("user", "Hello")])
        mock_db = MagicMock()
        mock_db.chathistory.find_many = AsyncMock(return_value=[hist])

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            response = client.get("/api/chat/histories")

        item = response.json()[0]
        assert item["id"] == "h-1"
        assert "createdAt" in item
        assert "updatedAt" in item
        assert "preview" in item

    def test_preview_is_first_message_content(self, client):
        hist = make_history("h-1", messages=[make_message("user", "Tell me about Alice")])
        mock_db = MagicMock()
        mock_db.chathistory.find_many = AsyncMock(return_value=[hist])

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            response = client.get("/api/chat/histories")

        assert response.json()[0]["preview"] == "Tell me about Alice"

    def test_preview_truncated_to_80_chars(self, client):
        long_msg = make_message("user", "A" * 120)
        hist = make_history("h-1", messages=[long_msg])
        mock_db = MagicMock()
        mock_db.chathistory.find_many = AsyncMock(return_value=[hist])

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            response = client.get("/api/chat/histories")

        assert response.json()[0]["preview"] == "A" * 80

    def test_preview_is_new_conversation_when_no_messages(self, client):
        hist = make_history("h-1", messages=[])
        mock_db = MagicMock()
        mock_db.chathistory.find_many = AsyncMock(return_value=[hist])

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            response = client.get("/api/chat/histories")

        assert response.json()[0]["preview"] == "New conversation"

    def test_returns_empty_list_when_no_histories(self, client):
        mock_db = MagicMock()
        mock_db.chathistory.find_many = AsyncMock(return_value=[])

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            response = client.get("/api/chat/histories")

        assert response.json() == []

    def test_queries_by_teacher_user_id(self, client):
        mock_db = MagicMock()
        mock_db.chathistory.find_many = AsyncMock(return_value=[])

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            client.get("/api/chat/histories")

        kwargs = mock_db.chathistory.find_many.call_args.kwargs
        assert kwargs["where"]["userId"] == "seed_teacher_id"

    def test_queries_limited_to_50_ordered_by_updated_desc(self, client):
        mock_db = MagicMock()
        mock_db.chathistory.find_many = AsyncMock(return_value=[])

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            client.get("/api/chat/histories")

        kwargs = mock_db.chathistory.find_many.call_args.kwargs
        assert kwargs["take"] == 50
        assert kwargs["order"] == {"updatedAt": "desc"}

    def test_returns_multiple_histories(self, client):
        hists = [
            make_history("h-1", messages=[make_message("user", "Q1")]),
            make_history("h-2", messages=[make_message("user", "Q2")]),
        ]
        mock_db = MagicMock()
        mock_db.chathistory.find_many = AsyncMock(return_value=hists)

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            response = client.get("/api/chat/histories")

        assert len(response.json()) == 2
        assert response.json()[0]["id"] == "h-1"
        assert response.json()[1]["id"] == "h-2"


# ---------------------------------------------------------------------------
# GET /api/chat/histories/{history_id}/messages
# ---------------------------------------------------------------------------

class TestGetHistoryMessages:

    def test_returns_200_with_list(self, client):
        mock_db = MagicMock()
        mock_db.chatmessage.find_many = AsyncMock(return_value=[])

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            response = client.get("/api/chat/histories/h-1/messages")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_messages_with_correct_fields(self, client):
        ts = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        msgs = [
            make_message("user", "Hello", ts),
            make_message("assistant", "Hi there", ts),
        ]
        mock_db = MagicMock()
        mock_db.chatmessage.find_many = AsyncMock(return_value=msgs)

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            response = client.get("/api/chat/histories/h-1/messages")

        data = response.json()
        assert len(data) == 2
        assert data[0] == {"role": "user", "content": "Hello", "timestamp": ts.isoformat()}
        assert data[1] == {"role": "assistant", "content": "Hi there", "timestamp": ts.isoformat()}

    def test_queries_by_the_provided_history_id(self, client):
        mock_db = MagicMock()
        mock_db.chatmessage.find_many = AsyncMock(return_value=[])

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            client.get("/api/chat/histories/target-id/messages")

        kwargs = mock_db.chatmessage.find_many.call_args.kwargs
        assert kwargs["where"]["chatHistoryId"] == "target-id"

    def test_messages_fetched_in_ascending_timestamp_order(self, client):
        mock_db = MagicMock()
        mock_db.chatmessage.find_many = AsyncMock(return_value=[])

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            client.get("/api/chat/histories/h-1/messages")

        kwargs = mock_db.chatmessage.find_many.call_args.kwargs
        assert kwargs["order"] == {"timestamp": "asc"}

    def test_returns_both_user_and_assistant_messages(self, client):
        ts = datetime(2024, 6, 1, tzinfo=timezone.utc)
        msgs = [
            make_message("user", "Question", ts),
            make_message("assistant", "Answer", ts),
            make_message("user", "Follow-up", ts),
            make_message("assistant", "More detail", ts),
        ]
        mock_db = MagicMock()
        mock_db.chatmessage.find_many = AsyncMock(return_value=msgs)

        with patch("app.routers.chat.get_db", new=AsyncMock(return_value=mock_db)):
            response = client.get("/api/chat/histories/h-conv/messages")

        data = response.json()
        assert len(data) == 4
        roles = [m["role"] for m in data]
        assert roles == ["user", "assistant", "user", "assistant"]
