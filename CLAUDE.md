# ai-first Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-02

## Active Technologies

- Python 3.10 (backend), Node.js 20+ (frontend tooling) + FastAPI, OpenAI Agents SDK, Prisma (Python), React 18, Vercel AI SDK v6 (001-performance-insights)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

```bash
# Backend
cd backend
uv sync                          # install dependencies
uv run prisma generate           # regenerate Prisma client
uv run prisma db push            # apply schema changes
uv run python seed.py            # seed database
uv run uvicorn app.main:app --reload  # start dev server (port 8000)

# Frontend
cd frontend
npm install
npm run dev                      # start dev server (port 5173)

# Database
docker compose up -d             # start PostgreSQL
```

## Code Style

Python 3.10 (backend), Node.js 20+ (frontend tooling): Follow standard conventions

## Recent Changes

- 001-performance-insights: Added Python 3.10 (backend), Node.js 20+ (frontend tooling) + FastAPI, OpenAI Agents SDK, Prisma (Python), React 18, Vercel AI SDK v6

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
