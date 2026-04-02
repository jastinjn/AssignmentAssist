import os

# Set required env vars before any app module is imported.
# conftest.py is loaded by pytest before test files, so these values
# are available when app.config.Settings() is constructed at import time.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/testdb")
os.environ.setdefault("OPENAI_API_KEY", "test-key-xxxx")
os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")
os.environ.setdefault("TEACHER_USER_ID", "seed_teacher_id")
