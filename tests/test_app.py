import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_and_unregister():
    # Use a unique email for testing
    test_email = "testuser@mergington.edu"
    activity = "Chess Club"
    # Unregister first if present
    client.post(f"/activities/{activity}/unregister?email={test_email}")
    # Sign up
    response = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert response.status_code == 200
    assert f"Signed up {test_email}" in response.json()["message"]
    # Double sign up should fail
    response2 = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert response2.status_code == 400
    # Unregister
    response3 = client.post(f"/activities/{activity}/unregister?email={test_email}")
    assert response3.status_code == 200
    assert f"Removed {test_email}" in response3.json()["message"]
    # Unregister again should fail
    response4 = client.post(f"/activities/{activity}/unregister?email={test_email}")
    assert response4.status_code == 404

def test_signup_full_activity():
    activity = "Mathletes"
    # Temporär alle Plätze belegen
    original_participants = app.activities[activity]["participants"][:]
    app.activities[activity]["participants"] = [f"user{i}@mergington.edu" for i in range(app.activities[activity]["max_participants"])]
    response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert "No spots available" in response.json()["detail"]
    # Restore
    app.activities[activity]["participants"] = original_participants
