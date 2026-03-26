from datetime import datetime, timezone

from prisma import Prisma


async def create_history(db: Prisma, teacher_id: str) -> str:
    """Create a new ChatHistory record and return its ID."""
    history = await db.chathistory.create(data={"userId": teacher_id})
    return history.id


async def load_history(db: Prisma, history_id: str) -> list[dict]:
    """Return chat messages as openai-agents input format, ordered by timestamp."""
    messages = await db.chatmessage.find_many(
        where={"chatHistoryId": history_id},
        order={"timestamp": "asc"},
    )
    return [{"role": m.role, "content": m.content} for m in messages]


async def append_messages(
    db: Prisma,
    history_id: str,
    user_message: str,
    assistant_message: str,
) -> None:
    """Append user and assistant messages to an existing ChatHistory."""
    now = datetime.now(timezone.utc)
    await db.chatmessage.create(
        data={
            "chatHistoryId": history_id,
            "role": "user",
            "content": user_message,
            "timestamp": now,
        }
    )
    await db.chatmessage.create(
        data={
            "chatHistoryId": history_id,
            "role": "assistant",
            "content": assistant_message,
            "timestamp": now,
        }
    )
    await db.chathistory.update(
        where={"id": history_id},
        data={"updatedAt": now},
    )
