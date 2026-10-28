import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        assert "status" in res.json()

@pytest.mark.asyncio
async def test_analyze_unified_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Valid request
        payload = {
            "resource_name": "payment-service",
            "manifest_content": "apiVersion: apps/v1\nkind: Deployment\nspec:\n  replicas: 1\n"
        }
        res = await ac.post("/api/v1/analyze/unified", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "changes" in data
        assert "dependencies" not in data # The output maps graph via impact.dict(), check existing schema
        assert "impact" in data
        assert "risk" in data
        assert "recommendation" in data
        assert "risk_score" in data["risk"]
        assert "risk_level" in data["risk"]
        
        # 2. Missing fields
        res = await ac.post("/api/v1/analyze/unified", json={"resource_name": "x"})
        assert res.status_code == 422 # Pydantic validation error

@pytest.mark.asyncio
async def test_deployment_apis():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Start
        res = await ac.post("/api/v1/deployment/start", json={"service_name": "test", "new_version": "v2"})
        assert res.status_code == 200
        
        # Promote
        res = await ac.post("/api/v1/deployment/promote", json={"service_name": "test"})
        assert res.status_code == 200
        
        # Status
        res = await ac.get("/api/v1/deployment/status?service_name=test")
        assert res.status_code == 200
        
        # Rollback
        res = await ac.post("/api/v1/deployment/rollback", json={"service_name": "test"})
        assert res.status_code == 200

@pytest.mark.asyncio
async def test_monitoring_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/monitoring/health?service_name=test")
        assert res.status_code == 200
        assert "health_status" in res.json()
