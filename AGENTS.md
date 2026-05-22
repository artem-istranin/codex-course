# Repository Guidelines

## Project Structure & Module Organization

This repository contains a one-page Wheel Winner app with a FastAPI backend and dependency-free static frontend.

- `frontend/`: static assets served by the backend (`index.html`, `styles.css`, `app.js`).
- `backend/`: Python API, tests, and dependency metadata.
- `README.md`: project overview and usage notes.
- `AGENTS.md`: repository-wide contributor guidance.

Keep frontend-only changes in `frontend/`. See `backend/AGENTS.md` before changing Python API behavior, tests, or dependencies.

## Build, Test, and Development Commands

Run backend commands from `backend/`.

```bash
UV_CACHE_DIR=.uv-cache uv sync --dev
```

Installs backend runtime and development dependencies from `backend/uv.lock`.

```bash
UV_CACHE_DIR=.uv-cache uv run uvicorn app.main:app --reload
```

Starts the FastAPI server and serves the frontend at `http://127.0.0.1:8000/`.

```bash
UV_CACHE_DIR=.uv-cache uv run pytest
```

Runs the backend pytest suite.

## Coding Style & Naming Conventions

For frontend changes, use semantic HTML, plain CSS, and vanilla JavaScript. Keep the app dependency-free unless a new tool clearly pays for itself.

Use clear, descriptive names for DOM IDs, CSS classes, and JavaScript functions. Match existing formatting in `frontend/index.html`, `frontend/styles.css`, and `frontend/app.js`.

## Testing Guidelines

Run `UV_CACHE_DIR=.uv-cache uv run pytest` after backend changes. For frontend-visible changes, manually verify the served page at `http://127.0.0.1:8000/`.

Add backend tests for API contract changes. Keep frontend behavior simple enough to validate without adding a build step unless project requirements change.

## Commit & Pull Request Guidelines

The current history uses Conventional Commit-style messages, for example `feat: implement frontend` and `feat: add FastAPI wheel winner backend with tests`. Continue using short imperative messages with prefixes such as `feat:`, `fix:`, `test:`, or `docs:`.

Pull requests should include a brief summary, testing performed, and screenshots or screen recordings for visible frontend changes. Link related issues when available and call out API contract changes explicitly.

## Security & Configuration Tips

Do not commit local caches, virtual environments, editor metadata, or secrets. Keep dependency changes inside `backend/pyproject.toml` and `backend/uv.lock`, and prefer local cache usage with `UV_CACHE_DIR=.uv-cache`.
