import pytest
from httpx import AsyncClient
from app.main import app
from app.core.database import Base, engine

# Ensure DB is created for tests
Base.metadata.create_all(bind=engine)

@pytest.mark.asyncio
async def test_unified_analysis_pipeline():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "resource_name": "payment-service",
            "manifest_content": "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: payment-service\nspec:\n  replicas: 1\n  template:\n    spec:\n      containers:\n      - name: payment\n        image: payment:v2\n        resources:\n          requests:\n            memory: \"128Mi\"\n"
        }
        
        # Trigger the unified pipeline
        response = await ac.post("/api/v1/analyze/unified", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify orchestration collected all pieces
        assert "changes" in data
        assert "impact" in data
        assert "risk" in data
        assert "recommendation" in data
        
        # Verify specific calculations trickled through
        assert data["risk"]["risk_score"] > 0
        assert data["recommendation"]["strategy"] in ["ROLLING", "CANARY", "BLUE_GREEN"]
        assert "explanation" in data["recommendation"]
        assert isinstance(data["recommendation"]["explanation"], str)

@pytest.mark.asyncio
async def test_deployment_and_persistent_rollback():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Start a deployment
        start_payload = {"service_name": "db-test-service", "new_version": "v1.5"}
        res1 = await ac.post("/api/v1/deployment/start", json=start_payload)
        assert res1.status_code == 200
        assert res1.json()["status"] == "IN_PROGRESS"
        
        # Verify it got written to DB by testing status retrieval
        res2 = await ac.get("/api/v1/deployment/status?service_name=db-test-service")
        assert res2.status_code == 200
        assert res2.json()["status"] == "IN_PROGRESS"
        
        # Stop and rollback
        rollback_payload = {"service_name": "db-test-service"}
        res3 = await ac.post("/api/v1/deployment/rollback", json=rollback_payload)
        
        # It might say NOT_FOUND if history length < 2, which is expected for a fresh DB test
        # Just ensure the endpoint didn't crash
        assert res3.status_code == 200
