"""
Test backend server for Playwright E2E tests.

Starts the real FastAPI app on port 8001 with Runner.run_streamed patched so no
OpenAI API calls are made. All other behaviour (routing, DB, chat history, SSE
streaming) is real.

Prerequisites: Docker PostgreSQL running, schema pushed (prisma db push).
Usage: uv run python test_server.py
"""

import os
import sys

# Set required env vars before any app module is imported.
# BaseSettings reads from os.environ first, so these override .env values.
os.environ.setdefault(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5430/teacherbot"
)
os.environ.setdefault("OPENAI_API_KEY", "sk-test-e2e-key")
os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")
os.environ.setdefault("TEACHER_USER_ID", "seed_teacher_id")

# Import the app now so all modules (including app.routers.chat) are loaded and
# their module-level names are bound. We patch after import so the patch targets
# the already-bound 'Runner' name in app.routers.chat's namespace.
from app.main import app  # noqa: E402  (must come after os.environ setup)
from unittest.mock import MagicMock, patch  # noqa: E402

MOCK_RESPONSE = "Based on recent scores and comments, Alice Chen needs the most support — she scored below the class average on both Knowledge & Understanding and Analysis & Argument."


async def _stream_events():
    """Async generator that yields a single text-delta event."""

    class _RawData:
        type = "response.output_text.delta"
        delta = MOCK_RESPONSE

    class _Event:
        type = "raw_response_event"
        data = _RawData()

    yield _Event()


if __name__ == "__main__":
    import uvicorn

    _mock_result = MagicMock()
    _mock_result.stream_events = _stream_events

    _mock_runner = MagicMock()
    _mock_runner.run_streamed.return_value = _mock_result

    # Patch Runner in the chat router's module namespace for the lifetime of the process.
    patcher = patch("app.routers.chat.Runner", _mock_runner)
    patcher.start()

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")
