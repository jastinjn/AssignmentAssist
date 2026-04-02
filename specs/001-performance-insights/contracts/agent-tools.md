# Agent Tool Contracts: Performance Insights

**Feature**: 001-performance-insights
**Date**: 2026-04-02

These are the two new agent tools to be added to
`backend/app/agent/tools.py`. They follow the same `@function_tool` decorator
pattern as the existing 8 tools.

---

## New Tool 1: `get_assignment_student_scores`

### Purpose
Returns each student's per-construct scores for a specific assignment, alongside the
class average per construct. Enables the agent to identify which students scored in low
bands and to present a complete assignment performance breakdown (US1).

### Signature

```python
async def get_assignment_student_scores(assignment_id: str) -> dict:
```

### Input

| Parameter | Type | Description |
|-----------|------|-------------|
| `assignment_id` | `str` | The ID of the assignment to query |

### Output

```json
{
  "assignmentTitle": "Causes of World War One Essay",
  "constructNames": ["Knowledge & Understanding", "Analysis & Argument"],
  "classAverages": {
    "Knowledge & Understanding": 4.33,
    "Analysis & Argument": 5.33
  },
  "students": [
    {
      "studentName": "Alice Chen",
      "scores": {
        "Knowledge & Understanding": 4,
        "Analysis & Argument": 3
      },
      "bandLevels": {
        "Knowledge & Understanding": 2,
        "Analysis & Argument": 1
      }
    },
    {
      "studentName": "Ben Tan",
      "scores": {
        "Knowledge & Understanding": 2,
        "Analysis & Argument": 6
      },
      "bandLevels": {
        "Knowledge & Understanding": 1,
        "Analysis & Argument": 3
      }
    },
    {
      "studentName": "Clara Wong",
      "scores": {
        "Knowledge & Understanding": 7,
        "Analysis & Argument": 7
      },
      "bandLevels": {
        "Knowledge & Understanding": 3,
        "Analysis & Argument": 3
      }
    }
  ]
}
```

### Error cases

- If `assignment_id` does not exist or has no marked submissions: return
  `{"error": "No marked submissions found for this assignment"}`
- If a student's submission is not marked: include them with `scores: null` and
  `bandLevels: null` to indicate incomplete data

### DB query approach

1. Find the Assignment by `assignment_id`, include its Questions and each Question's
   Construct name
2. Find all Submissions for the assignment where `isMarked = true`, include the
   student name and each QuestionResponse's ConstructGrades (with Band level and
   marksAwarded) and the Construct name
3. Compute class average per construct across all marked submissions
4. Return structured result as above

---

## New Tool 2: `get_class_performance_summary`

### Purpose
Returns all students' total marks per assignment in a class, including the class average
per assignment. Enables the agent to rank students by performance and identify at-risk
students (US3).

### Signature

```python
async def get_class_performance_summary(class_id: str) -> dict:
```

### Input

| Parameter | Type | Description |
|-----------|------|-------------|
| `class_id` | `str` | The ID of the class to query |

### Output

```json
{
  "className": "Secondary 3A Humanities",
  "assignments": [
    {
      "assignmentId": "clxxx1",
      "assignmentTitle": "Causes of World War One Essay",
      "dueDate": "2024-10-15T00:00:00.000Z",
      "maxPossibleMarks": 20,
      "classAverage": 9.67
    },
    {
      "assignmentId": "clxxx2",
      "assignmentTitle": "The Rise of Nazi Germany",
      "dueDate": "2024-11-12T00:00:00.000Z",
      "maxPossibleMarks": 20,
      "classAverage": 10.33
    }
  ],
  "students": [
    {
      "studentId": "clyyy1",
      "studentName": "Alice Chen",
      "assignmentScores": {
        "clxxx1": {
          "totalMarks": 7,
          "isMarked": true,
          "percentageScore": 35.0
        },
        "clxxx2": {
          "totalMarks": 8,
          "isMarked": true,
          "percentageScore": 40.0
        }
      },
      "overallAverage": 7.5
    },
    {
      "studentId": "clyyy2",
      "studentName": "Ben Tan",
      "assignmentScores": {
        "clxxx1": {
          "totalMarks": 8,
          "isMarked": true,
          "percentageScore": 40.0
        },
        "clxxx2": {
          "totalMarks": 10,
          "isMarked": true,
          "percentageScore": 50.0
        }
      },
      "overallAverage": 9.0
    },
    {
      "studentId": "clyyy3",
      "studentName": "Clara Wong",
      "assignmentScores": {
        "clxxx1": {
          "totalMarks": 14,
          "isMarked": true,
          "percentageScore": 70.0
        },
        "clxxx2": {
          "totalMarks": 13,
          "isMarked": true,
          "percentageScore": 65.0
        }
      },
      "overallAverage": 13.5
    }
  ]
}
```

### Error cases

- If `class_id` does not exist: return `{"error": "Class not found"}`
- If the class has no assignments: return `{"className": "...", "assignments": [], "students": []}`
- Assignments with no marked submissions: include assignment with `classAverage: null`
- Students with no submissions for an assignment: include
  `{"totalMarks": null, "isMarked": false, "percentageScore": null}`

### DB query approach

1. Find the SchoolClass by `class_id`, include its name
2. Find all Assignments for this class, ordered by dueDate
3. For each assignment, find all Submissions (including student name), and for each
   submission sum up ConstructGrade.marksAwarded to get totalMarks
4. Compute maxPossibleMarks from the sum of Band.maxMarks for the top band of each
   Construct on the assignment's rubric
5. Compute classAverage per assignment from marked submissions only
6. Return structured result as above

---

## Modified: `teacher_agent.py` — System Prompt Additions

The system prompt in `backend/app/agent/teacher_agent.py` should be extended with
insight-specific guidance. Add the following section after the existing guidelines:

```
Insight Response Guidelines:
- When asked for an assignment performance overview, always:
  1. Show a score summary: average marks per rubric construct (with min/max if useful)
  2. Group comments into themes: factual errors, argument weaknesses, clarity issues, and commendations
  3. Name specific students who scored in band 1 or 2 for any construct
  4. Use markdown headers (##) and bullet lists for readability

- When asked about an individual student's performance:
  1. Show their scores across assignments (table or list format)
  2. Identify any rubric constructs where they consistently score low
  3. Summarise recurring themes in their feedback comments
  4. Note if there is insufficient data for trend analysis (< 2 assignments)

- When asked which students need support or are at risk:
  1. Use get_class_performance_summary to get all students' data at once
  2. Rank students from most to least support needed (lowest overall average first)
  3. For the top 2–3 students, include supporting evidence (score below average, recurring comment themes)
  4. Define "at risk" as: overall average more than 20% below class average, OR scoring in band 1–2 on 2+ constructs

- Always clarify before generating insights if:
  - The assignment or student name is ambiguous
  - No marked submissions exist for the requested scope
```

---

## Modified: `ChatPanel.tsx` — Quick-Action Prompts

Update the quick-action suggestion buttons in
`frontend/src/components/chat/ChatPanel.tsx` to:

```
Current:
- "Which of my students need help?"
- "What are common mistakes?"
- "How is my class performing?"

Updated:
- "How did my class perform on the WWI essay?"
- "Which students need the most support?"
- "Give me a breakdown of Alice's performance"
- "What are the most common mistakes on the Nazi Germany essay?"
```

This directly maps to the three user stories and primes teachers to use
insight-oriented queries from the start.
