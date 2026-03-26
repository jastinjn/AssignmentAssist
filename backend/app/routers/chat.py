import json
import logging
import uuid

from agents import Runner
from agents.exceptions import MaxTurnsExceeded
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

from app.agent.teacher_agent import teacher_agent
from app.config import settings
from app.db import get_db
from app.services.chat_history import append_messages, create_history, load_history

router = APIRouter()


def _chunk(obj: dict) -> str:
    """Encode a UIMessageChunk as an SSE data line."""
    return f"data: {json.dumps(obj)}\n\n"


@router.post("/stream")
async def stream_chat(request: Request):
    body = await request.json()
    history_id: str | None = body.get("historyId")

    # AI SDK v6 sends messages as UIMessage objects with parts
    messages = body.get("messages", [])
    last_msg = messages[-1] if messages else {}
    parts = last_msg.get("parts", [])
    user_message: str = next((p["text"] for p in parts if p.get("type") == "text"), "")

    db = await get_db()
    prior_messages = await load_history(db, history_id) if history_id else []

    # Create history upfront so we can put the ID in the response header
    if not history_id:
        history_id = await create_history(db, settings.teacher_user_id)

    agent_input = prior_messages + [{"role": "user", "content": user_message}]

    text_id = f"txt_{uuid.uuid4().hex}"
    final_history_id = history_id  # captured for closure

    async def generate():
        full_response = ""

        yield _chunk({"type": "start-step"})
        yield _chunk({"type": "text-start", "id": text_id})

        result = Runner.run_streamed(teacher_agent, input=agent_input, max_turns=25)

        try:
            async for event in result.stream_events():
                if event.type == "raw_response_event":
                    raw = event.data
                    if (
                        hasattr(raw, "type")
                        and raw.type == "response.output_text.delta"
                    ):
                        delta = raw.delta
                        full_response += delta
                        yield _chunk({"type": "text-delta", "id": text_id, "delta": delta})
        except MaxTurnsExceeded:
            logger.warning("MaxTurnsExceeded for history %s", final_history_id)
            fallback = "I wasn't able to complete this request — it required too many steps. Try asking a more specific question."
            full_response += fallback
            yield _chunk({"type": "text-delta", "id": text_id, "delta": fallback})

        yield _chunk({"type": "text-end", "id": text_id})
        yield _chunk({"type": "finish-step"})
        yield "data: [DONE]\n\n"

        # Persist messages after streaming
        await append_messages(
            db=db,
            history_id=final_history_id,
            user_message=user_message,
            assistant_message=full_response,
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "x-vercel-ai-ui-message-stream": "v1",
            "x-chat-history-id": history_id,
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "x-accel-buffering": "no",
        },
    )


@router.get("/histories")
async def get_histories():
    db = await get_db()
    histories = await db.chathistory.find_many(
        where={"userId": settings.teacher_user_id},
        include={"messages": {"order_by": {"timestamp": "asc"}, "take": 1}},
        order={"updatedAt": "desc"},
        take=50,
    )
    return [
        {
            "id": h.id,
            "createdAt": h.createdAt.isoformat(),
            "updatedAt": h.updatedAt.isoformat(),
            "preview": (h.messages[0].content[:80] if h.messages else "New conversation"),
        }
        for h in histories
    ]


@router.get("/histories/{history_id}/messages")
async def get_history_messages(history_id: str):
    db = await get_db()
    messages = await db.chatmessage.find_many(
        where={"chatHistoryId": history_id},
        order={"timestamp": "asc"},
    )
    return [
        {"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()}
        for m in messages
    ]
