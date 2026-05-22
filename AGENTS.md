# Repository Guidelines

## Project Structure & Module Organization

This repository contains a small FastAPI backend and a static frontend for a random winner wheel.

- `backend/app/` contains backend application code:
  - `main.py` wires routes, API endpoints, and frontend static serving.
  - `schemas.py` defines request and response models.
  - `randomizer.py` contains winner-selection logic.
- `backend/tests/` contains pytest tests for API behavior and pure randomizer logic.
- `frontend/` contains the served UI: `index.html`, `styles.css`, and `app.js`.
- `backend/pyproject.toml` and `backend/uv.lock` define Python dependencies and test configuration.

## Build, Test, and Development Commands

Run backend commands from `backend/`.

```bash
UV_CACHE_DIR=.uv-cache uv sync --dev
```

Installs runtime and development dependencies using the locked `uv` environment.

```bash
UV_CACHE_DIR=.uv-cache uv run uvicorn app.main:app --reload
```

Starts the FastAPI app locally. Open `http://127.0.0.1:8000/` for the frontend; API routes live under `/api`.

```bash
UV_CACHE_DIR=.uv-cache uv run pytest
```

Runs the full test suite configured by `backend/pyproject.toml`.

## Coding Style & Naming Conventions

Use Python 3.13+ conventions with 4-space indentation, type hints for public functions, and small modules with focused responsibilities. Prefer descriptive snake_case names for functions and variables, and PascalCase for classes such as test stubs or Pydantic models.

Keep frontend code dependency-free unless there is a clear reason to add tooling. Use semantic HTML, plain CSS, and straightforward JavaScript in `frontend/app.js`.

## Testing Guidelines

Tests use `pytest` and FastAPI's `TestClient`. Place tests in `backend/tests/` with filenames matching `test_*.py` and test functions named `test_<behavior>()`.

Cover both API behavior and pure logic. For random behavior, inject a stub randomizer as shown in `test_randomizer.py` so assertions stay deterministic. Run `UV_CACHE_DIR=.uv-cache uv run pytest` before submitting changes.

## Commit & Pull Request Guidelines

The current history uses concise Conventional Commit-style messages, for example `feat: implement frontend`. Continue with prefixes such as `feat:`, `fix:`, `test:`, or `docs:`.

Pull requests should include a short description of the change, the commands run for verification, and screenshots or screen recordings for visible frontend changes. Link related issues when available and call out any API contract changes under `/api`.

## Security & Configuration Tips

Do not commit local caches, virtual environments, or generated artifacts. Keep `UV_CACHE_DIR=.uv-cache` local to `backend/` when syncing or testing. Validate participant input at the schema or route boundary before it reaches selection logic.
