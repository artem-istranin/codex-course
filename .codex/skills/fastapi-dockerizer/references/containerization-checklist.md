# Containerization Checklist

Use this checklist when dockerizing or maintaining this FastAPI app.

## Before Editing

- Read root `AGENTS.md`.
- Read `backend/AGENTS.md` before backend code, tests, or dependency changes.
- Identify the FastAPI app import path.
- Identify how frontend assets are served.
- Confirm dependencies are managed by `backend/pyproject.toml` and `backend/uv.lock`.
- Ask the user which local host port to use before adding or updating Docker run commands.

## Required Files

- Maintain a root `Dockerfile`.
- Maintain a root `.dockerignore`.
- Maintain a root `justfile`.
- Do not add `requirements.txt` unless explicitly requested.

## FastAPI Health Check

- Ensure `GET /health` exists.
- Return stable JSON, for example `{"status": "ok"}`.
- Add or update backend tests when tests exist.
- Point smoke checks at `/health`.

## Dockerfile

- Use a Python version compatible with `backend/pyproject.toml`.
- Install uv in the image.
- Copy `backend/pyproject.toml` and `backend/uv.lock` before copying the rest of the source.
- Run `uv sync --frozen --no-dev`.
- Copy backend and frontend files needed at runtime.
- Expose the container port used by uvicorn.
- Bind uvicorn to `0.0.0.0`.
- Prefer a non-root user for runtime when practical.

## .dockerignore

- Exclude VCS and editor metadata.
- Exclude Python caches and virtual environments.
- Exclude uv caches and test caches.
- Exclude local environment files and secrets.
- Exclude build artifacts that are not required by the runtime image.

## justfile

- Include a `build` recipe.
- Include a `run` recipe with local port mapping confirmed by the user.
- Include an `inspect` recipe for image or container metadata.
- Include a `smoke` recipe that calls `http://127.0.0.1:<port>/health`.
- Use variables for image name, container name, local port, and container port.

## Validation

- Run backend tests after backend changes.
- Build the container image when Docker is available.
- Run the container and call `/health` when a local port has been provided.
- Report any validation step that could not be run, including the command and reason.
