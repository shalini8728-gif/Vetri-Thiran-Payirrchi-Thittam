from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["application"] == "FitBuddy"


def test_api_docs():
    response = client.get("/docs")
    assert response.status_code == 200


def test_user_not_found():
    response = client.get("/api/users/nonexistent-user-123")

    assert response.status_code == 200
    assert response.json()["error"] == "User not found"