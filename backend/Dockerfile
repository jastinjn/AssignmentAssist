FROM python:3.10-slim

WORKDIR /app

# Install uv
RUN pip install uv --quiet

# Install dependencies (cached layer)
COPY pyproject.toml .
RUN uv sync --no-dev

# Copy prisma schema and generate client
COPY prisma/ prisma/
RUN uv run prisma generate

# Copy application code
COPY app/ app/
COPY seed.py .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
