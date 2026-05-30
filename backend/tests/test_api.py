from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_frontend_index_is_served(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Wheel Winner" in response.text


def test_frontend_static_assets_are_served(client: TestClient) -> None:
    css_response = client.get("/styles.css")
    js_response = client.get("/app.js")

    assert css_response.status_code == 200
    assert "text/css" in css_response.headers["content-type"]
    assert js_response.status_code == 200
    assert "javascript" in js_response.headers["content-type"]


def test_pick_winner_returns_participant_from_list(client: TestClient) -> None:
    participants = ["Alice", "Bob", "Clara"]

    response = client.post("/api/pick-winner", json={"participants": participants})

    assert response.status_code == 200
    body = response.json()
    assert body["participants"] == participants
    assert body["winner"] in participants
    assert body["winner_index"] == participants.index(body["winner"])


def test_pick_winner_rejects_empty_participant_list(client: TestClient) -> None:
    response = client.post("/api/pick-winner", json={"participants": []})

    assert response.status_code == 422


def test_pick_winner_rejects_blank_participant_name(client: TestClient) -> None:
    response = client.post("/api/pick-winner", json={"participants": ["Alice", " "]})

    assert response.status_code == 422
    assert response.json()["detail"] == "Participant names must be non-empty strings."
