# Repository Guidelines

## Project Structure & Module Organization

This repository contains a small FastAPI backend for the Wheel Winner app.

- `app/`: Python application code. `main.py` defines the FastAPI app and routes, `schemas.py` contains request and response models, and `randomizer.py` holds winner-selection logic.
- `tests/`: pytest tests for API behavior and randomizer logic.
- `pyproject.toml`: package metadata, runtime dependencies, development dependencies, and pytest configuration.
- `uv.lock`: locked dependency versions for reproducible installs.

The static frontend lives in the sibling repository directory `../frontend/`, with markup, styles, and browser behavior separated into `index.html`, `styles.css`, and `app.js`.

## Build, Test, and Development Commands

Run backend commands from this `backend/` directory.

```bash
UV_CACHE_DIR=.uv-cache uv sync --dev
```

Installs runtime and development dependencies using `uv`.

```bash
UV_CACHE_DIR=.uv-cache uv run pytest
```

Runs the full backend test suite.

```bash
UV_CACHE_DIR=.uv-cache uv run uvicorn app.main:app --reload
```

Starts the local FastAPI app with reload enabled. Open `http://127.0.0.1:8000/`; API routes are under `/api`.

## Coding Style & Naming Conventions

Use Python 3.13+ and keep code typed where practical. Follow the existing style: 4-space indentation, `snake_case` functions and variables, `PascalCase` classes, and focused modules with business logic kept out of route handlers. Keep validation in schemas or route boundaries where appropriate, and keep winner-selection behavior in `randomizer.py`.

For frontend changes in `../frontend/`, keep the implementation dependency-free unless there is a clear need.

## Testing Guidelines

Use pytest. Place tests in `tests/` and name files `test_*.py`. Test functions should describe behavior, for example `test_pick_winner_rejects_empty_participant_list`.

Cover API behavior with `fastapi.testclient.TestClient` and pure winner-selection logic directly. Add regression tests for validation changes, route behavior, and randomizer edge cases.

## Commit & Pull Request Guidelines

The project history uses Conventional Commit-style messages. Prefer short imperative subjects with a type prefix, such as `fix: reject duplicate blank names` or `test: cover static asset serving`.

Pull requests should include a concise summary, testing performed, and screenshots or short screen recordings for visible frontend changes. Link related issues when applicable and call out API contract changes, validation changes, or dependency updates.

## Security & Configuration Tips

Do not commit local caches such as `.uv-cache/`, virtual environments, or environment-specific files. Keep participant input validation on the backend even when frontend validation exists, since `/api/pick-winner` can be called directly.
