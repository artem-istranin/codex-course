FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/backend/.venv/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.9.13 /uv /uvx /bin/

COPY backend/pyproject.toml backend/uv.lock /app/backend/

WORKDIR /app/backend
RUN uv sync --frozen --no-dev --no-install-project

WORKDIR /app
COPY backend /app/backend
COPY frontend /app/frontend

RUN addgroup --system app && adduser --system --ingroup app app \
    && chown -R app:app /app

USER app
WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
