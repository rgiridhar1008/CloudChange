from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_user():
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"

def test_get_user_not_found():
    response = client.get("/users/999")
    assert response.status_code == 404
