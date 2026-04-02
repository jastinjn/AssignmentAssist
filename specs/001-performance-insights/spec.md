# Feature Specification: Performance Insights for Teachers

**Feature Branch**: `001-performance-insights`
**Created**: 2026-04-02
**Status**: Draft
**Input**: User description: "Build an application that allows teachers to discover insights on their classes' and students' performance by analyzing comments and scores of their essay assignments."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assignment Performance Breakdown (Priority: P1)

A teacher wants to understand how their class performed on a specific essay assignment.
They ask the chatbot about the assignment and receive a structured breakdown that covers:
score distribution across rubric constructs, recurring themes in marker comments
(common mistakes, common strengths), and which students struggled most.

**Why this priority**: This is the core insight teachers need after marking — understanding
the class as a whole before deciding on follow-up teaching actions. It delivers immediate,
actionable value and exercises both score and comment data.

**Independent Test**: Can be fully tested by asking the chatbot "How did the class perform
on [assignment name]?" and verifying the response includes score summaries, comment themes,
and identification of low performers — without needing any other story to be implemented.

**Acceptance Scenarios**:

1. **Given** a teacher has a marked assignment with at least 2 submissions,
   **When** the teacher asks the chatbot for an overview of that assignment's performance,
   **Then** the chatbot returns: average marks per rubric construct, the most common mistakes
   identified across inline comments, the most common strengths noted, and the names of
   students who scored in the lowest band for any construct.

2. **Given** a teacher asks about an assignment with no marked submissions,
   **When** the chatbot processes the request,
   **Then** the chatbot informs the teacher that no marked submissions are available yet.

3. **Given** a teacher asks about an assignment by a partial or ambiguous name,
   **When** the chatbot processes the request,
   **Then** the chatbot asks the teacher to clarify which assignment they mean before
   proceeding.

---

### User Story 2 - Individual Student Insight (Priority: P2)

A teacher wants to understand a specific student's performance across their essay
assignments — not just their scores, but patterns in the feedback they receive. They ask
the chatbot about a student and receive a consolidated view of that student's strengths,
recurring weaknesses, and progress across assignments.

**Why this priority**: Teachers need to tailor support to individual students. Understanding
patterns in feedback for a specific student allows targeted intervention. Builds naturally
on the assignment-level insights in US1.

**Independent Test**: Can be fully tested by asking "What can you tell me about [student
name]'s performance?" and verifying the response covers score trends, recurring comment
themes, and identifies areas needing improvement — without requiring US3.

**Acceptance Scenarios**:

1. **Given** a student has at least 2 marked submissions,
   **When** the teacher asks for an insight on that student,
   **Then** the chatbot returns: a summary of marks per assignment, recurring topics in
   comments (both praise and critique), and any rubric constructs where the student
   consistently scores low.

2. **Given** a student has only one marked submission,
   **When** the teacher asks for an insight on that student,
   **Then** the chatbot provides what data is available and notes that trends cannot yet
   be identified from a single submission.

3. **Given** the teacher asks by a student's first name that matches multiple students,
   **When** the chatbot processes the request,
   **Then** the chatbot lists the matching students and asks the teacher to confirm which
   one they mean.

---

### User Story 3 - At-Risk Student Identification (Priority: P3)

A teacher wants to know which students across a class need attention. They ask the chatbot
to surface students who are struggling based on low scores or patterns of negative
feedback, so the teacher can prioritise who to follow up with.

**Why this priority**: Proactive identification of at-risk students supports earlier
intervention and better learning outcomes. Builds on US1 and US2 but focuses on the
comparative, whole-class dimension.

**Independent Test**: Can be fully tested by asking "Which students in [class name] need
the most support?" and verifying the response surfaces students with consistently low
scores or repeated negative comment patterns, in priority order.

**Acceptance Scenarios**:

1. **Given** a class has at least 2 assignments with marked submissions,
   **When** the teacher asks which students need support,
   **Then** the chatbot returns a ranked list of students who score consistently below
   average, with a brief explanation referencing their scores and recurring comment themes.

2. **Given** only one assignment has been marked in the class,
   **When** the teacher asks the same question,
   **Then** the chatbot uses that single assignment's data and explicitly notes the insight
   is based on limited evidence.

3. **Given** all students in the class are performing at or above average,
   **When** the teacher asks which students need support,
   **Then** the chatbot communicates that no students show clear signs of struggling, and
   optionally surfaces the relatively lowest performers as an informational note.

---

### Edge Cases

- What happens when a class has no assignments?
  → The chatbot informs the teacher there is no data to analyse yet.
- What happens when an assignment has comments but no scores (submissions not yet marked)?
  → The chatbot notes the marking is incomplete and only uses available data.
- What happens when comments are very sparse (e.g., only 1 comment per submission)?
  → The chatbot reports what comments exist without inferring themes from insufficient data.
- What happens when a teacher asks a vague insight question not tied to a specific
  assignment, student, or class?
  → The chatbot asks a clarifying question to scope the analysis before proceeding.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow a teacher to request a performance breakdown for any
  assignment they teach, receiving score summaries and comment-based insights in a single
  response.
- **FR-002**: The system MUST identify and surface recurring themes in inline comments
  (both positive and negative) across all submissions for an assignment.
- **FR-003**: The system MUST present per-rubric-construct score averages when analysing
  assignment performance, with min/max scores where relevant.
- **FR-004**: The system MUST allow a teacher to request a consolidated performance insight
  for a named student, covering all their marked essay submissions the teacher has access to.
- **FR-005**: The system MUST identify rubric constructs where a student consistently scores
  in low bands across multiple submissions, when sufficient data exists.
- **FR-006**: The system MUST allow a teacher to ask which students in a class need
  attention, receiving a prioritised list supported by score and comment evidence.
- **FR-007**: The system MUST handle ambiguous queries (partial student names, unclear
  assignment references) by asking a targeted clarifying question before generating an
  insight.
- **FR-008**: The system MUST communicate clearly when data is insufficient to generate a
  meaningful insight (e.g., no marked submissions, only one submission for trend analysis).
- **FR-009**: Insight responses MUST use structured formatting — such as sections, bullet
  lists, or organised groupings — rather than unstructured prose alone, so teachers can
  scan key findings quickly.

### Key Entities

- **Assignment**: An essay task assigned to a class, assessed against a rubric with
  multiple constructs and marking bands. Has many student submissions.
- **Submission**: A student's response to an assignment; may be marked (with scores per
  construct) or unmarked. Contains inline comments.
- **Comment**: Inline feedback attached to a highlighted portion of a student's response,
  approved by a marker. Captures specific mistakes or commendations.
- **Construct Grade**: The score a student received on a specific rubric construct for a
  given submission. Basis for score-based insights.
- **Student**: A learner enrolled in one or more classes. Subject of individual performance
  insights.
- **Class**: A group of students taught by a teacher. Unit for class-wide analysis.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A teacher can receive a complete assignment performance breakdown — covering
  score summaries and comment themes — in a single conversation turn, without needing to
  ask multiple follow-up questions for the same assignment.
- **SC-002**: A teacher can identify the top struggling students in a class within 2
  conversation turns (one question plus at most one follow-up).
- **SC-003**: Insight responses accurately reference only real comments and scores from
  the data — no fabricated names, scores, or comment content appears in any response.
- **SC-004**: When data is insufficient for a meaningful insight, the chatbot communicates
  that limitation in 100% of such cases — no silent failures or empty responses.
- **SC-005**: At least 90% of teacher insight queries against assignments with sufficient
  data are answered without the teacher needing to repeat or significantly rephrase their
  question.

## Assumptions

- The teacher is already authenticated and the system knows which teacher is active;
  no login or multi-user switching is in scope for this feature.
- All student submissions the teacher can query are either fully marked or explicitly
  identifiable as unmarked — there is no ambiguous partial-marking state to handle.
- Comment theme identification is performed by the AI agent through reasoning over the
  comment text, not by a separate algorithm or manual tagging process.
- The chat interface remains the primary UI for accessing insights — no separate analytics
  dashboard or exportable report is in scope for this feature.
- Mobile support is out of scope; the chat interface is used on desktop browsers.
- All assignments referenced in this feature are essay-type assignments with rubric-based
  marking and inline comments, matching the existing data and marking model.
- The seed data (2 assignments, 3 students, graded submissions with inline comments)
  provides sufficient realistic data to validate all three user stories during development.
