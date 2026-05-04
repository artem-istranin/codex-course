from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_frontend_index_is_served() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Wheel Winner" in response.text


def test_frontend_static_assets_are_served() -> None:
    css_response = client.get("/styles.css")
    js_response = client.get("/app.js")

    assert css_response.status_code == 200
    assert "text/css" in css_response.headers["content-type"]
    assert js_response.status_code == 200
    assert "javascript" in js_response.headers["content-type"]


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
