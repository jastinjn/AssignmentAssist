from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import disconnect_db
from app.routers import chat


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await disconnect_db()


app = FastAPI(title="Assignment Assist API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-chat-history-id"],
)

app.include_router(chat.router, prefix="/api/chat")
