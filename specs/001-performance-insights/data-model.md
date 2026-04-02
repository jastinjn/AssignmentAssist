# Data Model: Performance Insights

**Feature**: 001-performance-insights
**Date**: 2026-04-02

---

## Schema Changes

**None.** The existing Prisma schema fully supports all three user stories. No new
models, fields, or migrations are required.

---

## Existing Entities Used

### Assignment
Represents an essay task assigned to a class.

- `id` — unique identifier
- `title` — human-readable name (used for disambiguation in queries)
- `dueDate` — when the assignment was due
- `classes` — many-to-many: which classes have this assignment
- `submissions` — one-to-many: student submissions

### Submission
Represents one student's attempt at an assignment.

- `id` — unique identifier
- `studentId` — which student submitted
- `assignmentId` — which assignment
- `classId` — which class context
- `isMarked` — whether marking is complete (only marked submissions used for insights)
- `questionResponses` — one-to-many: responses per question

### QuestionResponse
Represents a student's written response to a specific question within a submission.

- `id` — unique identifier
- `submissionId` — parent submission
- `content` — the student's essay text
- `overallFeedback` — optional overall feedback from the marker
- `comments` — one-to-many: inline comments on this response
- `constructGrades` — one-to-many: rubric grades for this response

### Comment
Represents inline feedback on a highlighted passage within a student's response.

- `id` — unique identifier
- `content` — the marker's comment text (main source for theme analysis)
- `highlightedText` — the excerpt the comment refers to (context for theme analysis)
- `status` — `approved | rejected | deleted` (only `approved` used for insights)
- `questionResponseId` — parent response

### ConstructGrade
Represents a student's score on one rubric construct for one question response.

- `id` — unique identifier
- `constructId` — which rubric construct (e.g., "Knowledge & Understanding")
- `bandId` — which performance band the student achieved
- `marksAwarded` — the numeric score (nullable; only used when non-null)
- `questionResponseId` — parent response

### Construct
A dimension of assessment within a rubric.

- `id` — unique identifier
- `name` — e.g., "Knowledge & Understanding", "Analysis & Argument"
- `order` — display ordering within the rubric
- `bands` — one-to-many: performance levels

### Band
A performance level within a construct.

- `id` — unique identifier
- `level` — integer (1 = lowest, 4 = highest in current seed)
- `minMarks`, `maxMarks` — mark range for this band
- `descriptor` — prose description of what this performance level looks like

---

## New Derived Structures (Tool Return Shapes)

These are not persisted — they are computed by new agent tools and returned to the agent.

### `get_assignment_student_scores` return shape

Used for US1 (assignment breakdown including low-scorer identification).

```
{
  "assignmentTitle": str,
  "constructNames": [str, ...],          # ordered list of construct names
  "classAverages": {
    "<construct_name>": float,           # class average marks for this construct
    ...
  },
  "students": [
    {
      "studentName": str,
      "scores": {
        "<construct_name>": int | null,  # marks awarded (null if not graded)
        ...
      },
      "bandLevels": {
        "<construct_name>": int | null,  # band level (1–4), null if not graded
        ...
      }
    },
    ...
  ]
}
```

### `get_class_performance_summary` return shape

Used for US3 (at-risk student identification across assignments).

```
{
  "className": str,
  "classAverage": float,                # overall average across all assignments
  "assignments": [
    {
      "assignmentId": str,
      "assignmentTitle": str,
      "dueDate": str,                   # ISO 8601
      "maxPossibleMarks": int,          # sum of all construct maxMarks
      "classAverage": float             # average total marks for this assignment
    },
    ...
  ],
  "students": [
    {
      "studentId": str,
      "studentName": str,
      "assignmentScores": {
        "<assignment_id>": {
          "totalMarks": int | null,     # null if not marked
          "isMarked": bool,
          "percentageScore": float | null
        },
        ...
      },
      "overallAverage": float | null    # average across marked assignments
    },
    ...
  ]
}
```

---

## Data Flow for Each User Story

### US1 — Assignment Performance Breakdown

```
Teacher asks → Agent calls:
  1. get_assignment_student_scores(assignment_id)
     → per-student per-construct scores + class averages
  2. get_assignment_comments(assignment_id)
     → all approved comments with highlighted text
Agent synthesizes:
  → Score summary per construct (avg, low scorers)
  → Comment themes (factual errors, argument weaknesses, etc.)
  → Named students in lowest band per construct
```

### US2 — Individual Student Insight

```
Teacher asks → Agent calls:
  1. search_students_by_name(name, teacher_id)   [if needed for disambiguation]
  2. get_student_performance(student_id)
     → per-assignment total marks + mark counts
  3. get_assignment_comments(assignment_id)       [for each assignment]
     → all comments; agent filters by student name
Agent synthesizes:
  → Score trend across assignments
  → Recurring comment themes for this student
  → Constructs where student consistently scores low
```

### US3 — At-Risk Student Identification

```
Teacher asks → Agent calls:
  1. list_classes(teacher_id)                    [if class name ambiguous]
  2. get_class_performance_summary(class_id)
     → all students' total marks per assignment + class averages
  3. get_assignment_comments(assignment_id)       [for most recent or most relevant]
     → comment evidence to support at-risk reasoning
Agent synthesizes:
  → Ranked list of students below class average
  → Evidence from scores and comments per student
```
