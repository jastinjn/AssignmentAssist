---
name: Project Architecture
description: Core stack, test layers, and key architectural patterns for the teacher chatbot app
type: project
---

FastAPI backend + React/Vite frontend. Two test layers:
- Backend unit tests: pytest, all deps mocked (Runner, DB, service layer), located in `backend/tests/`
- E2E tests: Playwright/Chromium, real DB (Docker on port 5430), real FastAPI, only Runner mocked via `backend/test_server.py`

**Why:** The layered strategy isolates streaming SSE logic (unit) from full request-path validation (E2E), while avoiding real OpenAI costs in CI.

**How to apply:** When reviewing test coverage, expect unit tests to mock at the service layer boundary and E2E tests to exercise the real database. Flag any unit test that hits the network or DB as an inconsistency.

Key patterns:
- SSE streaming via FastAPI `StreamingResponse` with Vercel AI SDK v6 chunk format
- Chat history stored in PostgreSQL via Prisma (Python client)
- `x-chat-history-id` response header is the mechanism for surfacing a newly created history ID to the frontend
- Frontend splits `ChatPanel` into outer loader shell (`ChatPanel`) and inner chat component (`ChatPanelInner`) — the `key={historyId ?? "new"}` prop on `ChatPanelInner` is intentional: it forces a full remount when switching conversations, resetting `useChat` state cleanly
- `Runner.run_streamed` is patched by name in `app.routers.chat`'s module namespace, not the `agents` package namespace
