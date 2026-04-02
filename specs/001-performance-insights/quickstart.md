# Quickstart: Validate Performance Insights

**Feature**: 001-performance-insights
**Date**: 2026-04-02

Use this guide to validate all three user stories after implementation.

---

## Prerequisites

1. Docker running with PostgreSQL:
   ```bash
   docker compose up -d
   ```

2. Backend running with seed data:
   ```bash
   cd backend
   uv run prisma db push --force-reset
   uv run python seed.py
   uv run uvicorn app.main:app --reload
   ```

3. Frontend running:
   ```bash
   cd frontend
   npm run dev
   ```

4. Open `http://localhost:5173` in a browser.

---

## Validation: User Story 1 — Assignment Performance Breakdown

**Goal**: Verify the agent returns score summaries + comment themes + low-scorer
identification in a single response.

**Test query** (type into chat):
```
How did my class perform on the Causes of World War One essay?
```

**Expected response must include**:
- [ ] Per-construct average marks (Knowledge & Understanding, Analysis & Argument)
- [ ] Identified comment themes (e.g., factual errors about Triple Alliance, weak
  argument structure)
- [ ] Named students who scored in band 1–2 (Alice and Ben for K&U; Alice for A&A)
- [ ] Structured formatting with markdown headers or bullet lists
- [ ] Response delivered in a single turn (no follow-up needed)

**Edge case test**:
```
How did my class perform on the history essay?
```
Expected: Agent asks for clarification (two assignments match "history essay").

---

## Validation: User Story 2 — Individual Student Insight

**Goal**: Verify the agent returns score trends + recurring comment themes for a
specific student.

**Test query**:
```
Tell me about Alice's performance across her assignments
```

**Expected response must include**:
- [ ] Alice's scores for both assignments (Assignment 1: 7/20, Assignment 2: 8/20)
- [ ] Identification that K&U and A&A are both consistently low (band 1–2)
- [ ] Recurring comment themes: factual errors and weak argument structure
- [ ] Note that the trend is based on 2 assignments

**Edge case test**:
```
How is Ben doing?
```
Expected: Agent returns Ben's scores (8/20 and 10/20), notes A&A is stronger than K&U,
and references factual errors in comments.

---

## Validation: User Story 3 — At-Risk Student Identification

**Goal**: Verify the agent returns a ranked list of struggling students with evidence.

**Test query**:
```
Which students in my class need the most support?
```

**Expected response must include**:
- [ ] Ranked list with Alice first (lowest overall: 7.5/20 average)
- [ ] Ben second (9/20 average, K&U consistently low)
- [ ] Clara noted as performing well
- [ ] Evidence cited for each: marks below class average + comment themes
- [ ] Response delivered without needing more than one follow-up

**Edge case test**:
```
Which students need help with Analysis & Argument?
```
Expected: Agent uses `get_assignment_student_scores` to identify Alice (band 1 on A&A in
Assignment 1) and surfaces relevant comments.

---

## Validation: Quick-Action Prompts (Frontend)

Open a fresh chat. Verify the empty state shows 4 updated suggestion buttons:
- [ ] "How did my class perform on the WWI essay?"
- [ ] "Which students need the most support?"
- [ ] "Give me a breakdown of Alice's performance"
- [ ] "What are the most common mistakes on the Nazi Germany essay?"

Click each button and verify it populates the input and sends a meaningful query.

---

## Validation: Edge Cases

**No marked submissions**:
Temporarily update a submission's `isMarked` to `false` in DB and ask:
```
How did my class perform on the WWI essay?
```
Expected: Agent reports that no marked submissions are available.

**Ambiguous student name**:
Add a second student named "Alice" to the seed and ask:
```
Tell me about Alice's performance
```
Expected: Agent asks which Alice before proceeding.

---

## Sign-off Checklist

- [ ] US1: Assignment performance breakdown works with score + comment data
- [ ] US2: Individual student insight returns trends and recurring feedback themes
- [ ] US3: At-risk student list is ranked with supporting evidence
- [ ] All edge cases handled gracefully (no silent failures, no hallucinated data)
- [ ] Responses use structured markdown formatting (headers, lists)
- [ ] Quick-action prompts updated in frontend empty state
