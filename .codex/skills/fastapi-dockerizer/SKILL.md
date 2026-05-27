---
name: fastapi-dockerizer
description: Dockerize and maintain containerization for FastAPI applications that use uv dependency management, especially projects with backend/pyproject.toml and backend/uv.lock. Use when Codex needs to add or update Dockerfiles, .dockerignore, justfiles, local Docker build/run/inspect/smoke-test commands, /health endpoints, or deployment pipeline container steps for prompts like "Dockerize this FastAPI app", "Make this app ready to run in a container", "Add or update local Docker commands", "Update justfile smoke checks to call /health", or "Update app deployment pipeline".
---

# FastAPI Dockerizer

## Workflow

1. Inspect the repository before editing:
   - Read root `AGENTS.md`.
   - Read `backend/AGENTS.md` before changing backend code, tests, or dependency files.
   - Confirm dependency sources in `backend/pyproject.toml` and `backend/uv.lock`.
   - Identify the FastAPI import path and current static-file behavior.

2. Ask which local host port to use before creating or updating any Docker run command, `just run` recipe, smoke-test URL, README command, or deployment instruction that maps a local port.
   - Do not assume `8000`, even if the app listens on container port `8000`.
   - If an existing run command already has a local port, still ask before changing or reproducing it.

3. Keep uv as the dependency manager:
   - Install dependencies from `backend/pyproject.toml` and `backend/uv.lock`.
   - Prefer `uv sync --frozen --no-dev` for runtime images.
   - Avoid introducing `requirements.txt`, Poetry, Pipenv, or ad hoc `pip install` flows unless the user explicitly requests it.

4. Ensure the FastAPI app exposes `GET /health`.
   - Return a small stable JSON body, such as `{"status": "ok"}`.
   - Add or update a backend test when backend tests exist.
   - Update container smoke checks to call `/health`.

5. Add or maintain root container support:
   - Root `Dockerfile`, unless the project already has a better established location.
   - Root `.dockerignore`.
   - Root `justfile` with recipes to build, run, inspect, and smoke-test the local image.
   - Use clear names for image, container, and port variables so the user can override them.

6. Validate the result:
   - Run backend tests when backend code changed.
   - Build the Docker image when Docker is available.
   - Start the container and run the `/health` smoke test when the user has provided a local port and Docker is available.
   - If Docker is unavailable or blocked, report the exact command that could not run and what was verified instead.

## Dockerfile Guidance

- Use a Python base image compatible with the project's Python version.
- Set `WORKDIR` to an app directory such as `/app`.
- Copy `backend/pyproject.toml` and `backend/uv.lock` before installing dependencies to preserve Docker layer caching.
- Copy application files after dependency installation.
- Run FastAPI with `uvicorn` bound to `0.0.0.0` on the container port.
- Keep frontend static assets available if the backend serves them.
- Prefer non-root runtime users when it does not conflict with the app's filesystem needs.

## justfile Guidance

Include recipes that demonstrate local container operations:

- `build`: build the image.
- `run`: run the container with an explicit local-to-container port mapping.
- `inspect`: show useful image or container metadata.
- `smoke`: call `GET /health` on the chosen local port.

Use variables for values that users commonly override, for example:

```just
image := "wheel-winner"
container := "wheel-winner"
port := "8000"
container_port := "8000"
```

Always confirm the `port` value with the user before creating or changing these recipes.

## References

- Read `references/containerization-checklist.md` for the implementation checklist.
