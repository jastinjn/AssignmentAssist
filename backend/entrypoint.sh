#!/bin/sh
set -e

echo "▶ Running Prisma migrations..."
uv run prisma db push --skip-generate

echo "▶ Seeding database..."
uv run python seed.py

echo "▶ Starting FastAPI..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
