import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activity participants to a clean state before each test."""
    original = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, participants in original.items():
        activities[name]["participants"] = participants


client = TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_all():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9


def test_get_activities_structure():
    response = client.get("/activities")
    data = response.json()
    for name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in response.json()["message"]


def test_signup_updates_participants():
    client.post("/activities/Chess Club/signup", params={"email": "test@mergington.edu"})
    response = client.get("/activities")
    assert "test@mergington.edu" in response.json()["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "michael@mergington.edu"  # already signed up
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_unknown_activity_returns_404():
    response = client.post(
        "/activities/Underwater Basket Weaving/signup",
        params={"email": "anyone@mergington.edu"},
    )
    assert response.status_code == 404


# --- DELETE /activities/{activity_name}/signup ---

def test_unregister_success():
    email = "michael@mergington.edu"  # pre-existing participant
    response = client.delete("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant():
    email = "daniel@mergington.edu"
    client.delete("/activities/Chess Club/signup", params={"email": email})
    response = client.get("/activities")
    assert email not in response.json()["Chess Club"]["participants"]


def test_unregister_not_signed_up_returns_400():
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "ghost@mergington.edu"},
    )
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_unknown_activity_returns_404():
    response = client.delete(
        "/activities/Nonexistent Activity/signup",
        params={"email": "anyone@mergington.edu"},
    )
    assert response.status_code == 404
