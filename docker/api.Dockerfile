FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir poetry

# Copy only dependency definitions first (better caching)
COPY pyproject.toml ./
# If poetry.lock exists, copy it too (won't fail if not present in some docker versions)
# Prefer having poetry.lock committed; if you don't have it yet, it's still okay.
COPY poetry.lock* ./

# Install deps into the container (no venv)
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

# Now copy the rest of the project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "rimas.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
