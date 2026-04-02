# Research: Performance Insights

**Feature**: 001-performance-insights
**Date**: 2026-04-02

---

## Decision 1: How to implement comment theme analysis

**Decision**: Let the AI agent synthesize comment themes through LLM reasoning over raw
comment text retrieved by the existing `get_assignment_comments` tool. No separate
clustering algorithm or pre-classification system.

**Rationale**: The `get_assignment_comments` tool already returns the full comment content
and highlighted text for every approved comment on an assignment. Modern LLMs (GPT-4o)
can reliably group these into categories (factual errors, argument weaknesses, clarity
issues, commendations) within a single reasoning pass. Adding a separate classification
layer would violate Principle V (Simplicity) without meaningfully improving accuracy.

**Alternatives considered**:
- Pre-tag comments in the DB with a `category` enum field → Rejected: requires schema
  change, manual tagging workflow, and adds no value since the LLM can infer categories
  from the text.
- Separate embedding + clustering pass on comment text → Rejected: over-engineered for
  14–50 comments per assignment; adds a new dependency and complexity for no perceptible
  quality gain.

---

## Decision 2: How to identify at-risk students efficiently

**Decision**: Add one new agent tool `get_class_performance_summary(class_id)` that
returns all students' total marks per assignment in a class. This gives the agent
everything it needs to compare students against the class average and rank them.

**Rationale**: The existing `get_student_performance` tool requires one call per student
to aggregate class-wide data. With 20–30 students, this would exhaust the agent's 25-turn
limit before any synthesis happens. A single tool call returning all students at once is
both more efficient and more reliable.

**Alternatives considered**:
- Call `get_student_performance` for each student in the agent loop → Rejected: scales
  poorly, unreliable within turn limits, and produces fragmented data the agent must
  re-aggregate.
- Add a separate analytics endpoint outside the agent → Rejected: violates Principle I
  (Agentic-First); data queries must go through the agent layer.
- Return per-construct breakdown in the new tool → Deferred: total marks per assignment
  is sufficient for at-risk identification; per-construct detail can be fetched with the
  existing `get_student_performance` tool as a follow-up if needed.

---

## Decision 3: How to identify low scorers per construct for assignment breakdown

**Decision**: Add one new agent tool `get_assignment_student_scores(assignment_id)` that
returns each student's per-construct marks for a specific assignment, alongside the
class average. This enables US1 (assignment breakdown with low-scorer identification).

**Rationale**: The existing `get_assignment_performance` tool returns only aggregated
statistics (avg/min/max per construct) — it cannot identify *which students* scored in
the lowest band. This tool fills that gap without replicating the existing aggregation
logic; it returns individual scores alongside the aggregate for direct comparison.

**Alternatives considered**:
- Expand `get_assignment_performance` to also return per-student scores → Rejected:
  changes a tool that existing conversations already rely on; better to add a new tool.
- Use `get_student_performance` for each student → Rejected: same turn-count problem as
  Decision 2; also `get_student_performance` returns totals, not per-construct scores.

---

## Decision 4: Tool for student-specific comments

**Decision**: No new tool needed. The existing `get_assignment_comments` returns all
comments for an assignment including the student name. The agent can filter by student
name when answering US2 individual insight queries.

**Rationale**: With ≤30 students and ≤3 comments per student per assignment, the total
payload is small enough that returning all comments and filtering mentally is efficient.
Adding a filtered tool adds complexity without meaningful performance benefit.

**Alternatives considered**:
- `get_student_assignment_comments(student_id, assignment_id)` → Rejected: YAGNI; the
  agent can filter the existing tool's output. Can be added later if needed at scale.

---

## Decision 5: System prompt enhancements

**Decision**: Enhance the teacher agent system prompt with explicit guidance on:
(a) how to structure insight responses using markdown (headers, bullets, bold labels),
(b) comment theme grouping categories (factual errors, argument weaknesses, clarity,
commendations),
(c) the definition of "at-risk" (consistently below class average or scoring in band 1–2).

**Rationale**: The agent has all the tools needed but currently produces inconsistent
response formatting. Codifying insight-specific formatting in the system prompt ensures
FR-009 (structured output) is reliably satisfied without requiring frontend changes.

**Alternatives considered**:
- Response post-processing on the backend → Rejected: fragile, adds complexity, and
  loses the agent's natural language flexibility.
- Custom tool that wraps the insight formatting → Rejected: over-engineered; the LLM
  already produces markdown natively with appropriate instruction.

---

## Decision 6: Frontend changes

**Decision**: Update the quick-action suggestion buttons in `ChatPanel.tsx` empty state
to include insight-oriented prompts that directly map to the three user stories.

**Rationale**: The current suggestions ("Which of my students need help?", "What are
common mistakes?", "How is my class performing?") are already insight-oriented but are
generic. Updating them to more specific, actionable prompts lowers the barrier to
discovering insights for the first time.

**Alternatives considered**:
- Add a separate "Insights" tab or panel → Rejected: violates Principle V (Simplicity)
  and the spec assumption that chat is the only UI.
- Add structured insight cards alongside chat → Rejected: out of spec scope; adds
  frontend complexity beyond what's needed.

---

## Summary of new work required

| Area | Change | Size |
|------|--------|------|
| `backend/app/agent/tools.py` | Add `get_class_performance_summary` tool | Small |
| `backend/app/agent/tools.py` | Add `get_assignment_student_scores` tool | Small |
| `backend/app/agent/teacher_agent.py` | Enhance system prompt with insight guidance | Small |
| `frontend/src/components/chat/ChatPanel.tsx` | Update quick-action prompts | Trivial |

No new dependencies, no schema changes, no new endpoints.
