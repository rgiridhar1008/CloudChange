from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.core.database import get_db

client = TestClient(app)

# Override the database dependency for tests
def override_get_db():
    class MockDB:
        def execute(self, query):
            pass
        def close(self):
            pass
    try:
        yield MockDB()
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "CloudChange API"
    assert data["database"] == "online"
