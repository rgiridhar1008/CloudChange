from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_process_payment():
    response = client.post("/pay", json={"order_id": 123, "amount": 99.99})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
