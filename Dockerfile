FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_FROZEN=1

# Install dependencies first (better layer caching).
COPY pyproject.toml uv.lock /app/
RUN uv sync --no-dev --no-install-project

# Copy application code.
COPY src /app/src
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
# Needed because `pyproject.toml` sets `project.readme = "README.md"`, and the build backend
# may read it when installing the project (`uv sync --no-dev`).
# If you don't publish this as a library, remove `project.readme` and you can delete this COPY.
COPY README.md /app/README.md

# Install the project itself.
RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
