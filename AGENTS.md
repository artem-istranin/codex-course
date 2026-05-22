# Repository Guidelines

## Project Structure & Module Organization

This repository contains a small FastAPI application with a static frontend.

- `backend/app/`: Python application code. `main.py` defines the FastAPI app and routes, `schemas.py` contains request/response models, and `randomizer.py` holds winner-selection logic.
- `backend/tests/`: pytest tests for API behavior and randomizer logic.
- `backend/pyproject.toml`: Python package metadata, dependencies, and pytest configuration.
- `frontend/`: static files for frontend.
- `README.md`: setup and usage instructions for users.

## Coding Style & Naming Conventions

Use Python 3.13+ and keep backend code typed where practical. Follow the existing style: 4-space indentation, snake_case functions and variables, PascalCase classes, and focused modules with business logic separated from route handlers. Test doubles should be simple local classes, as in `StubRandomizer`.

For frontend files, keep the implementation dependency-free unless there is a clear need. Use descriptive DOM names and keep styling in `frontend/styles.css`, behavior in `frontend/app.js`, and markup in `frontend/index.html`.

## Testing Guidelines

Use pytest. Place tests in `backend/tests/` and name files `test_*.py`. Test functions should describe behavior, for example `test_pick_winner_rejects_empty_participant_list`. Cover both API-level behavior through `fastapi.testclient.TestClient` and pure logic directly where possible. Add regression tests for validation rules, route changes, and randomizer behavior.

## Commit & Pull Request Guidelines

The current history uses Conventional Commit-style messages such as `feat: implement frontend`. Prefer short imperative subjects with a type prefix, for example `fix: reject duplicate blank names` or `test: cover static asset serving`.

Pull requests should include a concise summary, testing performed, and screenshots or short screen recordings for visible frontend changes. Link related issues when applicable and call out any API contract changes, validation changes, or dependency updates.

## Security & Configuration Tips

Do not commit local caches such as `.uv-cache/` or environment-specific files. Keep participant input validation on the backend even when frontend validation exists, since `/api/pick-winner` can be called directly.
