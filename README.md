# Randomizer Wheel

One-page wheel UI with a FastAPI backend for selecting a random winner from a submitted participant list.

## Project Structure

```text
randomizer-wheel/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── randomizer.py
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_randomizer.py
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── README.md
└── .gitignore
```

## Requirements

- Python 3.13+
- `uv`

## Backend Setup

```bash
cd backend
UV_CACHE_DIR=.uv-cache uv sync --dev
```

## Run The Application

```bash
cd backend
UV_CACHE_DIR=.uv-cache uv run uvicorn app.main:app --reload
```

Open the frontend at `http://127.0.0.1:8000/`.
The API is served under `http://127.0.0.1:8000/api`.

## Endpoint

### `POST /api/pick-winner`

Request body:

```json
{
  "participants": ["Alice", "Bob", "Clara"]
}
```

Example response:

```json
{
  "winner": "Bob",
  "winner_index": 1,
  "participants": ["Alice", "Bob", "Clara"]
}
```

Notes:

- `participants` must contain at least one item.
- Participant names must be non-empty strings.
- The winner is selected randomly on each request.

## Run Tests

```bash
cd backend
UV_CACHE_DIR=.uv-cache uv run pytest
```
