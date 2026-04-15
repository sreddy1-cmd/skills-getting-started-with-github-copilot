import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset activities to initial state before each test
    for activity in activities.values():
        activity['participants'].clear()
    activity_defaults = {
        "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
        "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
        "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"]
    }
    for name, emails in activity_defaults.items():
        if name in activities:
            activities[name]['participants'].extend(emails)

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert "Signed up test@mergington.edu for Chess Club" in response.json()["message"]
    # Should now be in participants
    resp2 = client.get("/activities")
    assert "test@mergington.edu" in resp2.json()["Chess Club"]["participants"]

def test_signup_duplicate():
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_not_found():
    response = client.post("/activities/Nonexistent/signup?email=someone@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_success():
    # Add a participant first
    client.post("/activities/Chess Club/signup?email=remove@mergington.edu")
    response = client.delete("/activities/Chess Club/unregister?email=remove@mergington.edu")
    assert response.status_code == 200
    assert "Removed remove@mergington.edu from Chess Club" in response.json()["message"]
    # Should not be in participants
    resp2 = client.get("/activities")
    assert "remove@mergington.edu" not in resp2.json()["Chess Club"]["participants"]

def test_unregister_not_found():
    response = client.delete("/activities/Chess Club/unregister?email=notfound@mergington.edu")
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]

def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent/unregister?email=someone@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
