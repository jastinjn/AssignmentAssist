# Testing

This project has two layers of tests:

| Layer | Tool | Location | OpenAI | Database |
|---|---|---|---|---|
| Backend unit | pytest | `backend/tests/` | Mocked | Mocked |
| End-to-end | Playwright | `frontend/e2e/` | Mocked | Real (Docker) |

---

## Backend Unit Tests

**Tool**: pytest  
**File**: `backend/tests/test_chat_router.py`

Tests the three chat API endpoints in isolation. Every external dependency — the database, the OpenAI Agents SDK `Runner`, and all service functions — is replaced with in-process mocks. No network calls are made and no database needs to be running.

### What is mocked

| Dependency | How |
|---|---|
| `Runner.run_streamed` | Returns a synthetic async event stream with configurable text chunks |
| `get_db()` | Returns a `MagicMock` Prisma client |
| `load_history` / `create_history` / `append_messages` | `AsyncMock` replacing the service layer |

### Test scenarios

#### `POST /api/chat/stream` (17 tests)

| Test | What it checks |
|---|---|
| `test_returns_200_and_sse_content_type` | Response is 200 with `text/event-stream` content type |
| `test_response_includes_required_sse_headers` | `x-vercel-ai-ui-message-stream`, `x-chat-history-id`, and `cache-control` headers are present |
| `test_sse_body_contains_expected_event_types` | SSE body contains `start-step`, `text-start`, `text-delta`, `text-end`, `finish-step`, and `[DONE]` |
| `test_text_delta_chunks_contain_correct_content` | Each `text-delta` event carries the correct delta string |
| `test_text_start_and_text_end_share_same_id` | `text-start` and `text-end` events reference the same stream ID |
| `test_new_conversation_creates_history` | When no `historyId` is provided, `create_history` is called and `load_history` is not |
| `test_new_conversation_history_id_in_header` | The newly created history ID is returned in the `x-chat-history-id` header |
| `test_existing_conversation_loads_history_not_create` | When a `historyId` is provided, `load_history` is called and `create_history` is not |
| `test_existing_conversation_echoes_history_id_in_header` | The provided `historyId` is echoed back in the response header |
| `test_prior_messages_prepended_to_agent_input` | Prior messages from history are prepended to the agent input before the new user message |
| `test_messages_persisted_after_stream_completes` | `append_messages` is called once after streaming with the correct `history_id`, `user_message`, and `assistant_message` |
| `test_persisted_assistant_message_is_full_concatenated_response` | All streamed delta chunks are concatenated into the persisted assistant message |
| `test_max_turns_exceeded_streams_fallback_message` | When `MaxTurnsExceeded` is raised, a fallback message containing "too many steps" is streamed |
| `test_max_turns_exceeded_still_persists_messages` | Messages are still persisted even when `MaxTurnsExceeded` is raised |
| `test_non_output_delta_events_produce_no_text_delta_chunks` | Non-text events from the agent (e.g. `agent_updated_stream_event`) are filtered and produce no `text-delta` chunks |
| `test_empty_messages_list_sends_empty_user_message` | An empty `messages` array results in an empty string being sent to the agent |
| `test_agent_called_with_max_turns_25` | `Runner.run_streamed` is always called with `max_turns=25` |

#### `GET /api/chat/histories` (9 tests)

| Test | What it checks |
|---|---|
| `test_returns_200_with_list` | Response is 200 with a JSON array |
| `test_returns_history_with_expected_fields` | Each item has `id`, `createdAt`, `updatedAt`, and `preview` fields |
| `test_preview_is_first_message_content` | The `preview` field contains the content of the first message |
| `test_preview_truncated_to_80_chars` | Previews longer than 80 characters are truncated |
| `test_preview_is_new_conversation_when_no_messages` | Histories with no messages show `"New conversation"` as the preview |
| `test_returns_empty_list_when_no_histories` | Returns `[]` when the teacher has no chat histories |
| `test_queries_by_teacher_user_id` | Database query filters by the configured `teacher_user_id` |
| `test_queries_limited_to_50_ordered_by_updated_desc` | Query uses `take=50` and orders by `updatedAt` descending |
| `test_returns_multiple_histories` | Multiple histories are returned in the correct order |

#### `GET /api/chat/histories/{history_id}/messages` (5 tests)

| Test | What it checks |
|---|---|
| `test_returns_200_with_list` | Response is 200 with a JSON array |
| `test_returns_messages_with_correct_fields` | Each message has `role`, `content`, and `timestamp` fields with correct values |
| `test_queries_by_the_provided_history_id` | Database query filters by the history ID from the URL |
| `test_messages_fetched_in_ascending_timestamp_order` | Query orders by `timestamp` ascending |
| `test_returns_both_user_and_assistant_messages` | Both `user` and `assistant` role messages are returned |

### Setup

Install test dependencies (first time only):

```bash
cd backend
uv sync --extra test
```

### Running

```bash
cd backend
uv run pytest
```

Verbose output with test names:

```bash
uv run pytest -v
```

Run a single test class:

```bash
uv run pytest tests/test_chat_router.py::TestStreamEndpoint -v
```

---

## End-to-End Tests

**Tool**: Playwright (Chromium)  
**File**: `frontend/e2e/chat.spec.ts`

Tests the full request path from browser through the frontend, backend, and database. OpenAI is the only thing mocked — everything else (routing, SSE streaming, chat history writes to PostgreSQL) is real.

### Architecture

```
Playwright
    │
    ▼
Frontend  (port 5174)       ← started by Playwright with API_TARGET set
    │  /api/* proxied
    ▼
Test backend  (port 8001)   ← real FastAPI + real DB + Runner patched
    │
    ├── PostgreSQL (real)   ← Docker, port 5430
    └── OpenAI (mocked)     ← Runner.run_streamed returns a fixed response
```

The test backend is `backend/test_server.py`. It starts the real FastAPI application and patches `Runner.run_streamed` at the module level before `uvicorn.run()` is called, so the patch persists for the entire server lifetime. The frontend runs on port `5174` (separate from the regular dev server on `5173`) to avoid reusing a stale instance that may point to the wrong backend.

### What is mocked

| Dependency | How |
|---|---|
| `Runner.run_streamed` | Patched in `backend/test_server.py` using `unittest.mock.patch.start()`; returns a fixed assistant response |

### Test scenario

**`user sends a message and receives a response in the chat`**

1. Navigate to the app root
2. Locate the chat textarea by its placeholder text
3. Click the textarea and fill it with `"Which students need the most support?"`
4. Submit by pressing Enter
5. Assert the user message appears in the chat
6. Assert the mocked backend response appears in a chat bubble (10 second timeout)
7. Assert the textarea is cleared after sending

### Setup

**Prerequisites** (must be done once before running E2E tests):

1. Start PostgreSQL:
   ```bash
   docker compose up -d
   ```

2. Apply the schema and seed the database (from the `backend` directory):
   ```bash
   cd backend
   uv run prisma db push
   uv run python seed.py
   ```

3. Install Playwright browsers (first time only, from the `frontend` directory):
   ```bash
   cd frontend
   npx playwright install chromium
   ```

### Running

```bash
cd frontend
npm run test:e2e
```

Interactive UI mode (shows browser, lets you step through tests):

```bash
npm run test:e2e:ui
```

> Playwright starts both servers automatically. If port `8001` or `5174` is already in use from a previous run, stop those processes before re-running.
