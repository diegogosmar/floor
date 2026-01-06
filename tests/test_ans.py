"""
Test suite for ANS (Agent Name Server)

Run: pytest tests/test_ans.py -v
"""

import pytest
import httpx
import asyncio
from src.ans.client import ANSClient
from src.ans.models import ManifestData, ConversantIdentification


@pytest.fixture
async def ans_client():
    """Fixture: ANS client pointing to test server"""
    client = ANSClient("http://localhost:8001")
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_ans_health_check():
    """Test: ANS health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8001/health", timeout=5.0)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ANS"


@pytest.mark.asyncio
async def test_ans_list_empty():
    """Test: List manifests when empty"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8001/api/v1/manifests/list", timeout=5.0)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_ans_publish_manifest(ans_client):
    """Test: Publish a manifest"""
    manifest = ManifestData(
        identification=ConversantIdentification(
            speakerUri="tag:test.example.com,2025:test_agent",
            serviceUrl="http://localhost:8002",
            organization="Test Corp",
            conversationalName="Test Agent",
            role="Tester"
        ),
        capabilities=["testing", "automation"]
    )
    
    success = await ans_client.publish_manifest(manifest)
    assert success is True


@pytest.mark.asyncio
async def test_ans_search_by_capability(ans_client):
    """Test: Search agents by capability"""
    # First, publish a manifest
    manifest = ManifestData(
        identification=ConversantIdentification(
            speakerUri="tag:test.example.com,2025:search_agent",
            serviceUrl="http://localhost:8003",
            conversationalName="Search Test Agent"
        ),
        capabilities=["search", "discovery"]
    )
    
    await ans_client.publish_manifest(manifest)
    
    # Then search
    results = await ans_client.search_by_capability("search")
    assert len(results) > 0
    assert any(m.identification.speakerUri == "tag:test.example.com,2025:search_agent" for m in results)


@pytest.mark.asyncio
async def test_ans_get_all_manifests(ans_client):
    """Test: Get all manifests"""
    # Publish a manifest
    manifest = ManifestData(
        identification=ConversantIdentification(
            speakerUri="tag:test.example.com,2025:list_agent",
            serviceUrl="http://localhost:8004",
            conversationalName="List Test Agent"
        ),
        capabilities=["listing"]
    )
    
    await ans_client.publish_manifest(manifest)
    
    # Get all
    all_manifests = await ans_client.get_manifests()
    assert len(all_manifests) > 0
    assert any(m.identification.speakerUri == "tag:test.example.com,2025:list_agent" for m in all_manifests)


@pytest.mark.asyncio
async def test_ans_workflow_complete(ans_client):
    """Test: Complete workflow - publish, search, retrieve"""
    # Step 1: Publish multiple manifests
    agents = [
        ManifestData(
            identification=ConversantIdentification(
                speakerUri=f"tag:test.example.com,2025:workflow_agent_{i}",
                serviceUrl=f"http://localhost:{8005 + i}",
                conversationalName=f"Workflow Agent {i}"
            ),
            capabilities=["workflow", f"capability_{i}"]
        )
        for i in range(3)
    ]
    
    for agent in agents:
        success = await ans_client.publish_manifest(agent)
        assert success is True
    
    # Step 2: Search by capability
    workflow_agents = await ans_client.search_by_capability("workflow")
    assert len(workflow_agents) >= 3
    
    # Step 3: Get all manifests
    all_manifests = await ans_client.get_manifests()
    assert len(all_manifests) >= 3
    
    # Step 4: Verify specific agent exists
    found = any(
        m.identification.speakerUri == "tag:test.example.com,2025:workflow_agent_0"
        for m in all_manifests
    )
    assert found is True


@pytest.mark.asyncio
async def test_ans_rest_api_search():
    """Test: REST API search endpoint"""
    async with httpx.AsyncClient() as client:
        # First publish via client
        ans_client = ANSClient("http://localhost:8001")
        manifest = ManifestData(
            identification=ConversantIdentification(
                speakerUri="tag:test.example.com,2025:rest_agent",
                serviceUrl="http://localhost:8008",
                conversationalName="REST Test Agent"
            ),
            capabilities=["rest_api", "testing"]
        )
        await ans_client.publish_manifest(manifest)
        await ans_client.close()
        
        # Then search via REST API
        response = await client.get(
            "http://localhost:8001/api/v1/manifests/search",
            params={"capability": "rest_api"},
            timeout=5.0
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


if __name__ == "__main__":
    print("🧪 ANS Test Suite")
    print("=" * 50)
    print("\n⚠️  Make sure ANS server is running:")
    print("   uvicorn src.ans.main:app --port 8001")
    print("\nRun tests with: pytest tests/test_ans.py -v")

