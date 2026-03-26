from prisma import Prisma

_db: Prisma | None = None


async def get_db() -> Prisma:
    global _db
    if _db is None:
        _db = Prisma()
        await _db.connect()
    return _db


async def disconnect_db() -> None:
    global _db
    if _db:
        await _db.disconnect()
        _db = None
