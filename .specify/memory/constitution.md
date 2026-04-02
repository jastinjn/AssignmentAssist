<!--
SYNC IMPACT REPORT
==================
Version change: [TEMPLATE] → 1.0.0 (initial ratification)
Modified principles: N/A — first population from template
Added sections: Core Principles (I–V), Tech Stack Constraints, Development Workflow, Governance
Removed sections: All placeholder tokens replaced
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ Constitution Check section references constitution gates; compatible
  - .specify/templates/spec-template.md ✅ No principle-driven mandatory sections added beyond existing template
  - .specify/templates/tasks-template.md ✅ Phase structure and test-optional guidance aligns with Principle V (Simplicity)
  - .specify/templates/agent-file-template.md ✅ No outdated references; generic enough
Follow-up TODOs: None — all placeholders resolved
-->

# Assignment Assist Constitution

## Core Principles

### I. Agentic-First

All data querying and natural-language reasoning MUST be routed through the OpenAI Agents SDK
agent layer. Direct database reads from API route handlers MUST only be used for non-agentic
operations (e.g., auth checks, health endpoints). The agent is the primary interface between
the teacher's intent and the data; bypassing it is not permitted for chat-driven features.

**Rationale**: The core value proposition of Assignment Assist is intelligent, conversational
access to teacher data. Routing queries outside the agent layer would fragment the intelligence
layer and make the system harder to reason about and extend.

### II. Full-Stack Separation

The backend (FastAPI) and frontend (React/TypeScript) MUST communicate only via documented
HTTP API contracts. No code, state, or business logic MUST be shared between layers.
API schemas MUST be defined with Pydantic on the backend; TypeScript types on the frontend
MUST be derived from or kept consistent with those schemas.

**Rationale**: Clean layer separation enables independent development, testing, and deployment
of each tier, and prevents the tight coupling that leads to cascading breakage.

### III. Type Safety

- Backend: All API request/response bodies MUST use Pydantic models; no raw `dict` returns from
  endpoints.
- Frontend: TypeScript strict mode MUST be enabled; `any` types are prohibited except in
  explicitly justified, narrowly scoped utility code.
- Database: All schema changes MUST be declared in the Prisma schema file first; no ad-hoc SQL
  that bypasses the ORM.

**Rationale**: Type safety at all layers surfaces contract mismatches at development time rather
than in production, and makes the codebase navigable as it grows.

### IV. Database-First Data Modeling

Schema changes MUST be defined in `backend/prisma/schema.prisma` and applied via
`prisma db push` (or a migration) before any application code references the new fields.
No application code MUST assume the existence of a DB column that has not been pushed.

**Rationale**: Decoupling schema from application code prevents hard-to-diagnose runtime
errors and ensures the schema is the single source of truth for data structure.

### V. Simplicity & YAGNI

Every implementation decision MUST solve a stated user requirement. Speculative features,
premature abstractions, and unnecessary indirection are prohibited. When two approaches both
satisfy the requirement, choose the simpler one. Complexity introduced MUST be justified in
the plan's Complexity Tracking table.

**Rationale**: This is a teaching-focused tool with a small, well-defined scope. Simplicity
keeps the codebase maintainable and features shippable without unnecessary overhead.

## Tech Stack Constraints

- **Language/Runtime**: Python 3.10 (backend), Node.js 20+ (frontend tooling)
- **Backend framework**: FastAPI with Uvicorn
- **AI layer**: OpenAI Agents SDK — MUST be used for all conversational agent logic
- **ORM**: Prisma (Python client) against PostgreSQL
- **Database**: PostgreSQL (Docker-managed in development)
- **Frontend**: React 18+ with TypeScript in strict mode; Vercel AI SDK v6 for chat UI
- **Package management**: `uv` for Python dependencies; `npm` for frontend
- **Environment config**: All secrets (API keys, DB URLs) MUST live in `.env` files;
  never committed to version control

Introducing a new dependency MUST be justified in the feature plan and MUST not duplicate
the capability of an existing listed dependency.

## Development Workflow

- **Local development**: `docker compose up -d` starts PostgreSQL; backend and frontend run
  separately on ports 8000 and 5173 respectively.
- **Database changes**: Run `uv run prisma db push` after any schema change; run
  `uv run python seed.py` to restore seed data after a reset.
- **Testing**: Tests are OPTIONAL and MUST only be included when explicitly requested in the
  feature specification. When included, tests MUST be written before implementation (TDD:
  Red → Green → Refactor).
- **Code review**: All feature branches MUST pass a Constitution Check (see plan template)
  before merging to `main`. Violations require a Complexity Tracking justification.
- **Commits**: Commit after each logical unit of work; commit messages MUST be descriptive
  and reference the feature/task ID where applicable.

## Governance

This constitution supersedes all other development practices and guidelines for
Assignment Assist. In the event of a conflict, the constitution takes precedence.

**Amendment procedure**:
1. Propose the change with rationale and impact analysis.
2. Update this file, incrementing the version per semantic versioning rules.
3. Run the consistency propagation checklist (re-run `/speckit.constitution`).
4. Document the change in the Sync Impact Report embedded in this file.

**Versioning policy**:
- MAJOR: Removal or redefinition of a principle that is backward incompatible.
- MINOR: New principle or section added, or materially expanded guidance.
- PATCH: Clarifications, wording fixes, non-semantic refinements.

**Compliance**: All PRs and agent-generated plans MUST include a Constitution Check section
verifying adherence to Principles I–V. Any violation MUST be recorded in the Complexity
Tracking table with a clear justification for why the simpler, compliant approach is
insufficient.

**Version**: 1.0.0 | **Ratified**: 2026-04-02 | **Last Amended**: 2026-04-02
