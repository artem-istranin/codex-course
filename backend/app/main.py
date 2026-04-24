from fastapi import FastAPI, HTTPException

from app.randomizer import pick_winner_index
from app.schemas import PickWinnerRequest, PickWinnerResponse


app = FastAPI(title="Wheel Winner API")


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
