from pydantic import BaseModel, Field


class PickWinnerRequest(BaseModel):
    participants: list[str] = Field(min_length=1)


class PickWinnerResponse(BaseModel):
    winner: str
    winner_index: int
    participants: list[str]
