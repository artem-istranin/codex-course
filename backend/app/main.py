from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.randomizer import pick_winner_index
from app.schemas import PickWinnerRequest, PickWinnerResponse


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(title="Wheel Winner API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/api/pick-winner", response_model=PickWinnerResponse)
def pick_winner(payload: PickWinnerRequest) -> PickWinnerResponse:
    cleaned_participants = [participant.strip() for participant in payload.participants]

    if any(not participant for participant in cleaned_participants):
        raise HTTPException(
            status_code=422,
            detail="Participant names must be non-empty strings.",
        )

    winner_index = pick_winner_index(cleaned_participants)
    winner = cleaned_participants[winner_index]

    return PickWinnerResponse(
        winner=winner,
        winner_index=winner_index,
        participants=cleaned_participants,
    )


app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
