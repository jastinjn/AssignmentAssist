---
description: Run all backend unit tests and frontend E2E tests. On failure, identify the root cause and suggest targeted fixes.
---

## User Input

```text
$ARGUMENTS
```

If the user specifies a scope (e.g. "backend", "e2e", "unit"), run only that subset. Otherwise run everything.

## Execution Steps

### 1. Determine scope

Read `$ARGUMENTS`:
- `backend` or `unit` → run backend tests only (Step 2)
- `e2e` or `frontend` → run E2E tests only (Step 3)
- empty or `all` → run both (Steps 2 and 3)

### 2. Run backend unit tests

From the repo root run:

```bash
cd backend && uv run pytest -v 2>&1
```

Capture the full output. Note:
- Which tests passed / failed / errored
- Any import errors or missing fixture errors
- The exact assertion or exception message for each failure

### 3. Run frontend E2E tests

From the repo root run:

```bash
cd frontend && npm run test:e2e 2>&1
```

Capture the full output. Note:
- Which specs passed / failed / timed-out
- Playwright error messages (strict-mode violations, element-not-found, timeout)
- Any web server startup errors (backend or Vite)

### 4. Report results

Print a concise summary table:

| Suite | Tests | Passed | Failed | Skipped |
|-------|-------|--------|--------|---------|

If all suites are green, output **All tests passed** and stop.

### 5. Diagnose failures

For each failed test:

1. **Quote the exact error** (assertion message, stack trace first-frame, or Playwright locator expression).
2. **Identify the root cause** — categorise as one of:
   - `assertion` — logic/value mismatch in the test itself
   - `selector` — Playwright can't locate an element (wrong locator, timing)
   - `network` — fetch/SSE to backend failed or timed out
   - `server-startup` — web server didn't become ready in time
   - `schema` — Prisma / DB shape mismatch
   - `import` — missing module, bad path, env var not set
   - `logic` — bug in application code exposed by the test
3. **Pinpoint the source** — name the file and line number(s) most likely responsible.

### 6. Suggest fixes

For each diagnosed failure provide a concrete, minimal fix:
- Quote the current code snippet that needs to change.
- Show exactly what it should be replaced with.
- Explain in one sentence why this resolves the root cause.

Do **not** apply the fixes automatically. Present them clearly and ask:
> "Would you like me to apply these fixes?"

If the user says yes (or types "apply"), apply every suggested fix using the Edit tool, then re-run the affected test suite to confirm green.

## Constraints

- Never modify test files to suppress a legitimate failure — fix the root cause in application code or fix a genuinely wrong assertion/selector.
- Do not skip or mark tests as `skip`/`xfail` as a workaround.
- If a failure requires a DB migration (`prisma db push`) or seed data (`python seed.py`), say so explicitly rather than guessing.
- Limit output to what is actionable — do not dump full logs unless a failure cannot be diagnosed without them.
