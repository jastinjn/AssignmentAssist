import os

from agents import Agent

from app.agent.tools import (
    get_assignment_comments,
    get_assignment_performance,
    get_rubric_for_assignment,
    get_student_performance,
    list_assignments_in_class,
    list_classes,
    list_students_in_class,
    search_students_by_name,
)
from app.config import settings

SYSTEM_PROMPT = """You are an AI assistant for a teacher. You have access to data about their \
classes, students, assignments, submissions, and grades stored in a school database.

Your role is to help teachers gain insights quickly — such as identifying struggling students, \
understanding common mistakes across a class, or reviewing assignment performance.

Guidelines:
- Always use the available tools to retrieve real data before answering questions about \
  students, classes, or assignments.
- Be concise and data-driven in your responses.
- When presenting numbers or statistics, format them clearly.
- If a question is ambiguous (e.g. "my class" without specifying which one), use list_classes \
  to find the teacher's classes first.
- The teacher's user ID is: {teacher_user_id}
"""

os.environ["OPENAI_API_KEY"] = settings.openai_api_key

teacher_agent = Agent(
    name="TeacherAssistant",
    model=settings.openai_model,
    instructions=SYSTEM_PROMPT.format(teacher_user_id=settings.teacher_user_id),
    tools=[
        list_classes,
        list_students_in_class,
        list_assignments_in_class,
        get_assignment_performance,
        get_student_performance,
        get_assignment_comments,
        search_students_by_name,
        get_rubric_for_assignment,
    ],
)
