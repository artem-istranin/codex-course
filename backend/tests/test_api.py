from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_pick_winner_returns_participant_from_list() -> None:
    participants = ["Alice", "Bob", "Clara"]

    response = client.post("/api/pick-winner", json={"participants": participants})

    assert response.status_code == 200
    body = response.json()
    assert body["participants"] == participants
    assert body["winner"] in participants
    assert body["winner_index"] == participants.index(body["winner"])


def test_pick_winner_rejects_empty_participant_list() -> None:
    response = client.post("/api/pick-winner", json={"participants": []})

    assert response.status_code == 422


def test_pick_winner_rejects_blank_participant_name() -> None:
    response = client.post("/api/pick-winner", json={"participants": ["Alice", " "]})

    assert response.status_code == 422
    assert response.json()["detail"] == "Participant names must be non-empty strings."
