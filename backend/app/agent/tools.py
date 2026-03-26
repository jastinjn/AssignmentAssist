import logging
from collections import defaultdict

from agents import function_tool

from app.db import get_db

logger = logging.getLogger(__name__)


@function_tool
async def list_classes(teacher_user_id: str) -> list[dict]:
    """List all classes taught by this teacher, including student counts."""
    try:
        db = await get_db()
        classes = await db.schoolclass.find_many(
            where={"teachers": {"some": {"id": teacher_user_id}}},
            include={"students": True},
        )
        return [
            {
                "id": c.id,
                "name": c.name,
                "code": c.code,
                "level": c.level,
                "studentCount": len(c.students) if c.students else 0,
            }
            for c in classes
        ]
    except Exception:
        logger.exception("list_classes failed")
        raise


@function_tool
async def list_students_in_class(class_id: str) -> list[dict]:
    """Return all students enrolled in a specific class."""
    try:
        db = await get_db()
        students = await db.user.find_many(
            where={"classesJoined": {"some": {"id": class_id}}, "role": "student"},
            order={"name": "asc"},
        )
        return [{"id": s.id, "name": s.name, "email": s.email} for s in students]
    except Exception:
        logger.exception("list_students_in_class failed")
        raise


@function_tool
async def list_assignments_in_class(class_id: str) -> list[dict]:
    """List all assignments for a class with due dates and submission counts."""
    try:
        db = await get_db()
        assignments = await db.assignment.find_many(
            where={"classes": {"some": {"id": class_id}}, "deletedAt": None},
            include={"submissions": True},
            order={"dueDate": "asc"},
        )
        return [
            {
                "id": a.id,
                "title": a.title,
                "dueDate": a.dueDate.isoformat(),
                "submissionCount": len(a.submissions) if a.submissions else 0,
                "isMarkedCount": sum(1 for s in (a.submissions or []) if s.isMarked),
            }
            for a in assignments
        ]
    except Exception:
        logger.exception("list_assignments_in_class failed")
        raise


@function_tool
async def get_assignment_performance(assignment_id: str) -> dict:
    """
    Get grade statistics for an assignment: average, min, max marks awarded
    per rubric construct across all marked submissions.
    """
    try:
        db = await get_db()
        grades = await db.constructgrade.find_many(
            where={
                "questionResponse": {
                    "submission": {"assignmentId": assignment_id, "isMarked": True}
                }
            },
            include={"rubricConstruct": True},
        )
        if not grades:
            return {"message": "No graded submissions found for this assignment."}

        by_construct: dict[str, list[int]] = defaultdict(list)
        construct_names: dict[str, str] = {}
        for g in grades:
            if g.marksAwarded is not None:
                by_construct[g.constructId].append(g.marksAwarded)
                construct_names[g.constructId] = (
                    g.rubricConstruct.name if g.rubricConstruct else g.constructId
                )

        result = {}
        for cid, marks in by_construct.items():
            result[construct_names[cid]] = {
                "mean": round(sum(marks) / len(marks), 2),
                "min": min(marks),
                "max": max(marks),
                "count": len(marks),
            }
        return result
    except Exception:
        logger.exception("get_assignment_performance failed")
        raise


@function_tool
async def get_student_performance(student_id: str, class_id: str | None = None) -> dict:
    """
    Return a summary of a student's submissions and marks across assignments.
    Optionally filter to a specific class.
    """
    try:
        db = await get_db()
        where: dict = {"studentId": student_id, "isMarked": True}
        if class_id:
            where["classId"] = class_id

        submissions = await db.submission.find_many(
            where=where,
            include={
                "assignment": True,
                "questionResponses": {
                    "include": {"constructGrades": {"include": {"rubricConstruct": True}}}
                },
            },
            order={"createdAt": "desc"},
        )
        student = await db.user.find_unique(where={"id": student_id})

        result = {
            "studentName": student.name if student else student_id,
            "submissions": [],
        }
        for sub in submissions:
            all_marks = [
                g.marksAwarded
                for qr in (sub.questionResponses or [])
                for g in (qr.constructGrades or [])
                if g.marksAwarded is not None
            ]
            result["submissions"].append(
                {
                    "assignmentTitle": sub.assignment.title if sub.assignment else sub.assignmentId,
                    "dueDate": sub.assignment.dueDate.isoformat() if sub.assignment else None,
                    "totalMarks": sum(all_marks),
                    "markCount": len(all_marks),
                }
            )
        return result
    except Exception:
        logger.exception("get_student_performance failed")
        raise


@function_tool
async def get_assignment_comments(assignment_id: str) -> list[dict]:
    """
    Retrieve all approved comments left on student responses for a given assignment.
    Each entry includes the highlighted text that was commented on and the comment
    content, allowing the AI to identify patterns and common mistakes across the class.
    """
    try:
        db = await get_db()
        responses = await db.questionresponse.find_many(
            where={"submission": {"assignmentId": assignment_id}},
            include={
                "comments": {"where": {"status": "approved"}},
                "submission": {"include": {"student": True}},
            },
        )

        results = []
        for resp in responses:
            student_name = (
                resp.submission.student.name
                if resp.submission and resp.submission.student
                else "Unknown"
            )
            for comment in resp.comments or []:
                results.append(
                    {
                        "studentName": student_name,
                        "highlightedText": comment.highlightedText,
                        "comment": comment.content,
                    }
                )
        return results
    except Exception:
        logger.exception("get_assignment_comments failed")
        raise


@function_tool
async def search_students_by_name(name_query: str, teacher_user_id: str) -> list[dict]:
    """Search for students by name across all of this teacher's classes."""
    try:
        db = await get_db()
        students = await db.user.find_many(
            where={
                "name": {"contains": name_query, "mode": "insensitive"},
                "classesJoined": {"some": {"teachers": {"some": {"id": teacher_user_id}}}},
                "role": {"equals": "student"},
            },
            order={"name": "asc"},
        )
        return [{"id": s.id, "name": s.name, "email": s.email} for s in students]
    except Exception:
        logger.exception("search_students_by_name failed")
        raise


@function_tool
async def get_rubric_for_assignment(assignment_id: str) -> dict:
    """Return the rubric constructs and marking bands for a given assignment."""
    try:
        db = await get_db()
        questions = await db.question.find_many(
            where={"assignmentId": assignment_id},
            include={"rubric": {"include": {"constructs": {"include": {"bands": True}}}}},
        )
        rubrics_seen: set[str] = set()
        result: list[dict] = []
        for q in questions:
            if q.rubric and q.rubric.id not in rubrics_seen:
                rubrics_seen.add(q.rubric.id)
                result.append(
                    {
                        "rubricName": q.rubric.name,
                        "constructs": [
                            {
                                "name": c.name,
                                "bands": [
                                    {
                                        "level": b.level,
                                        "minMarks": b.minMarks,
                                        "maxMarks": b.maxMarks,
                                        "descriptor": b.descriptor[:150] if b.descriptor else "",
                                    }
                                    for b in sorted(c.bands or [], key=lambda x: x.level)
                                ],
                            }
                            for c in sorted(q.rubric.constructs, key=lambda x: x.order)
                        ],
                    }
                )
        return {"rubrics": result} if result else {"message": "No rubric found for this assignment."}
    except Exception:
        logger.exception("get_rubric_for_assignment failed")
        raise
