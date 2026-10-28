import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

def build_manifest(replicas=3, memory="512Mi", probes=True):
    probe_yaml = """
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
""" if probes else ""
    
    return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
spec:
  replicas: {replicas}
  template:
    spec:
      containers:
      - name: payment
        image: payment:v2
        resources:
          requests:
            memory: "{memory}"{probe_yaml}
"""

@pytest.mark.asyncio
async def test_case_1_no_significant_change():
    # Only changing image version
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        manifest = build_manifest(replicas=3, memory="512Mi", probes=True)
        res = await ac.post("/api/v1/analyze/unified", json={
            "resource_name": "unknown-service-no-dependencies",
            "manifest_content": manifest
        })
        data = res.json()
        assert data["risk"]["risk_level"] == "LOW"
        assert data["recommendation"]["strategy"] == "ROLLING"

@pytest.mark.asyncio
async def test_case_2_moderate_configuration_change():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Dropping probe
        manifest = build_manifest(replicas=3, memory="512Mi", probes=False)
        res = await ac.post("/api/v1/analyze/unified", json={
            "resource_name": "unknown-service-no-dependencies",
            "manifest_content": manifest
        })
        data = res.json()
        # Missing probe is +15, but we need it to be medium. 
        # If it's a known service, it might get external traffic (+15).
        # Let's target payment-service which has HIGH criticality (+20). 20+15 = 35 -> MEDIUM
        res = await ac.post("/api/v1/analyze/unified", json={
            "resource_name": "payment-service",
            "manifest_content": manifest
        })
        data = res.json()
        assert data["risk"]["risk_level"] == "MEDIUM"
        assert data["recommendation"]["strategy"] == "CANARY"

@pytest.mark.asyncio
async def test_case_3_replica_reduction():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        old_manifest = build_manifest(replicas=3, memory="512Mi", probes=True)
        manifest = build_manifest(replicas=1, memory="512Mi", probes=True)
        res = await ac.post("/api/v1/analyze/unified", json={
            "resource_name": "order-service",
            "manifest_content": manifest,
            "old_manifest_content": old_manifest
        })
        data = res.json()
        factors = [f["factor"] for f in data["risk"]["risk_factors"]]
        assert "Replica Reduction" in factors

@pytest.mark.asyncio
async def test_case_4_memory_reduction():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        old_manifest = build_manifest(replicas=3, memory="512Mi", probes=True)
        manifest = build_manifest(replicas=3, memory="128Mi", probes=True)
        res = await ac.post("/api/v1/analyze/unified", json={
            "resource_name": "order-service",
            "manifest_content": manifest,
            "old_manifest_content": old_manifest
        })
        data = res.json()
        factors = [f["factor"] for f in data["risk"]["risk_factors"]]
        assert "Memory Reduction" in factors

@pytest.mark.asyncio
async def test_case_5_multiple_dangerous_changes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        old_manifest = build_manifest(replicas=3, memory="512Mi", probes=True)
        manifest = build_manifest(replicas=1, memory="128Mi", probes=False)
        res = await ac.post("/api/v1/analyze/unified", json={
            "resource_name": "payment-service", # payment-service has Criticality=HIGH (+20) and External Traffic (+15)
            "manifest_content": manifest,
            "old_manifest_content": old_manifest
        })
        data = res.json()
        
        # Factors: Replica Reduction (+20) + Memory Reduction (+20) + Missing Probe (+15) + Critical (+20) + Traffic (+15) = 90
        assert data["risk"]["risk_level"] in ["HIGH", "CRITICAL"]

@pytest.mark.asyncio
async def test_case_6_healthy_canary():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/deployment/start", json={"service_name": "healthy-canary", "new_version": "v2"})
        assert res.json()["current_percentage"] == 10
        
        res = await ac.post("/api/v1/deployment/promote", json={"service_name": "healthy-canary"})
        assert res.json()["current_percentage"] == 25
        
        res = await ac.post("/api/v1/deployment/promote", json={"service_name": "healthy-canary"})
        assert res.json()["current_percentage"] == 50
        
        res = await ac.post("/api/v1/deployment/promote", json={"service_name": "healthy-canary"})
        assert res.json()["current_percentage"] == 100
        assert res.json()["status"] == "SUCCESS"

@pytest.mark.asyncio
async def test_case_7_failed_canary_rollback():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Starting with 'unhealthy' in the name triggers the mock to fail health checks
        res = await ac.post("/api/v1/deployment/start", json={"service_name": "unhealthy-canary", "new_version": "v2"})
        
        # The engine should immediately detect the failure and trigger a rollback
        assert res.json()["status"] == "ROLLED_BACK"

@pytest.mark.asyncio
async def test_case_8_dependency_impact():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        manifest = build_manifest(replicas=3, memory="512Mi", probes=True)
        res = await ac.post("/api/v1/analyze/unified", json={
            "resource_name": "payment-service",
            "manifest_content": manifest
        })
        data = res.json()
        affected_services = data["risk"]["affected_services"]
        assert "order-service" in affected_services
        assert "api-gateway" not in affected_services
