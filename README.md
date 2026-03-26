# Assignment Assist

An agentic chatbot that lets teachers query their classes, students, and assignments via a chat interface. Powered by FastAPI, OpenAI Agents SDK, Prisma, and React.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (for PostgreSQL)
- [pyenv](https://github.com/pyenv/pyenv) + Python 3.10
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Node.js 20+

## Setup

### 1. Start the database

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
```

Copy the example env file and fill in your OpenAI API key:

```bash
cp .env.example .env
```

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/assignmentassist
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Install dependencies, run migrations, and seed the database:

```bash
uv sync
uv run prisma generate
uv run prisma db push
uv run python seed.py
```

Start the backend:

```bash
uv run uvicorn app.main:app --reload
```

API is available at `http://localhost:8000`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App is available at `http://localhost:5173`.

## Reset and reseed the database

To wipe all data and reseed from scratch (from the `backend` directory):

```bash
uv run prisma db push --force-reset && uv run python seed.py
```

## Seed data

The seed creates:
- 1 teacher (`seed_teacher_id`)
- 3 students: Alice Chen, Ben Tan, Clara Wong
- 2 history assignments with 3 graded submissions each:
  - *Causes of World War One Essay*
  - *The Rise of Nazi Germany*
- Inline comments highlighting factual and argument mistakes in each submission
