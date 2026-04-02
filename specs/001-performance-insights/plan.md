# Implementation Plan: Performance Insights for Teachers

**Branch**: `001-performance-insights` | **Date**: 2026-04-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-performance-insights/spec.md`

## Summary

Enable teachers to discover performance insights on their classes and students by
analyzing essay scores and marker comments through the existing chat interface. The agent
gains two new tools for efficient class-wide data retrieval, and the system prompt is
enhanced to guide structured, insight-oriented responses. No schema changes, no new
dependencies.

## Technical Context

**Language/Version**: Python 3.10 (backend), Node.js 20+ (frontend tooling)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, Prisma (Python), React 18, Vercel AI SDK v6
**Storage**: PostgreSQL (existing schema — no changes)
**Testing**: Not requested in spec
**Target Platform**: Desktop web browser
**Project Type**: Web service (backend) + web app (frontend)
**Performance Goals**: Single-turn insight responses; agent completes within 25 turns
**Constraints**: No new DB migrations; no new third-party dependencies; chat remains only UI
**Scale/Scope**: Single teacher, 1 class, ~30 students, ~10 assignments

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|-----------|-------|--------|
| I. Agentic-First | All data queries go through new agent tools, not direct DB calls from router | ✅ PASS |
| II. Full-Stack Separation | New tools are backend-only; frontend only receives chat messages; no shared state | ✅ PASS |
| III. Type Safety | New tools return typed dicts; Prisma query results are typed; no `any` added to frontend | ✅ PASS |
| IV. Database-First | No schema changes needed; all queries use existing Prisma models | ✅ PASS |
| V. Simplicity | 2 new tools + system prompt update + 4 UI strings; no new architecture layers | ✅ PASS |

**All gates pass. No Complexity Tracking required.**

## Project Structure

### Documentation (this feature)

```text
specs/001-performance-insights/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── agent-tools.md   # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── agent/
│   │   ├── tools.py              # ADD: get_assignment_student_scores,
│   │   │                         #      get_class_performance_summary
│   │   └── teacher_agent.py      # MODIFY: enhance system prompt with insight guidance
│   ├── routers/
│   │   └── chat.py               # NO CHANGES
│   ├── services/
│   │   └── chat_history.py       # NO CHANGES
│   ├── config.py                 # NO CHANGES
│   ├── db.py                     # NO CHANGES
│   └── main.py                   # NO CHANGES
└── prisma/
    └── schema.prisma             # NO CHANGES

frontend/
├── src/
│   ├── components/
│   │   └── chat/
│   │       ├── ChatPanel.tsx     # MODIFY: update 4 quick-action suggestion prompts
│   │       ├── ChatInput.tsx     # NO CHANGES
│   │       ├── MessageBubble.tsx # NO CHANGES
│   │       └── MessageList.tsx   # NO CHANGES
│   ├── hooks/
│   │   └── useHistories.ts       # NO CHANGES
│   └── lib/                      # NO CHANGES
└── ...
```

**Structure Decision**: Web application (Option 2). Backend and frontend already exist.
This feature modifies 3 files and adds no new files.

## Complexity Tracking

> No violations — all constitution gates pass cleanly.
