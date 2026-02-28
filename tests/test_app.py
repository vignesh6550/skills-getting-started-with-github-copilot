import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

# keep an untouched snapshot of the original data so each test starts
# with the same state.
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the activities dict before each test."""
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield


@pytest.fixture
def client():
    """FastAPI test client for the app."""
    return TestClient(app)


def test_get_activities(client):
    res = client.get("/activities")
    assert res.status_code == 200
    assert res.json() == original_activities


def test_signup_success(client):
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    res = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert res.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_already_registered(client):
    activity = "Chess Club"
    existing = original_activities[activity]["participants"][0]
    res = client.post(f"/activities/{activity}/signup", params={"email": existing})
    assert res.status_code == 400


def test_signup_missing_activity(client):
    res = client.post("/activities/Nonexistent/signup", params={"email": "x@x.com"})
    assert res.status_code == 404


def test_remove_participant_success(client):
    activity = "Chess Club"
    participant = original_activities[activity]["participants"][0]
    res = client.delete(f"/activities/{activity}/participants", params={"email": participant})
    assert res.status_code == 200
    assert participant not in activities[activity]["participants"]


def test_remove_nonexistent_participant(client):
    res = client.delete("/activities/Chess Club/participants", params={"email": "ghost@mergington.edu"})
    assert res.status_code == 404


def test_remove_nonexistent_activity(client):
    res = client.delete("/activities/NoClub/participants", params={"email": "a@b.com"})
    assert res.status_code == 404
