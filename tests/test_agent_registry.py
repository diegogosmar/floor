"""
Tests for Agent Registry per OFP 1.0.0
"""

import pytest
from datetime import datetime, timedelta
from src.agent_registry.registry import AgentRegistry
from src.agent_registry.capabilities import AgentCapabilities, CapabilityType


@pytest.mark.asyncio
async def test_register_agent() -> None:
    """Test agent registration"""
    registry = AgentRegistry();

    capabilities = AgentCapabilities(
        speakerUri="tag:test.com,2025:agent_1",
        agent_name="Test Agent",
        agent_version="1.0.0",
        capabilities=[CapabilityType.TEXT_GENERATION]
    );

    success = await registry.register_agent(capabilities);
    assert success is True;

    agent = await registry.get_agent("tag:test.com,2025:agent_1");
    assert agent is not None;
    assert agent.speakerUri == "tag:test.com,2025:agent_1"


@pytest.mark.asyncio
async def test_unregister_agent() -> None:
    """Test agent unregistration"""
    registry = AgentRegistry();

    capabilities = AgentCapabilities(
        speakerUri="tag:test.com,2025:agent_1",
        agent_name="Test Agent",
        agent_version="1.0.0",
        capabilities=[CapabilityType.TEXT_GENERATION]
    );

    await registry.register_agent(capabilities);
    success = await registry.unregister_agent("tag:test.com,2025:agent_1");
    assert success is True;

    agent = await registry.get_agent("tag:test.com,2025:agent_1");
    assert agent is None


@pytest.mark.asyncio
async def test_find_agents_by_capability() -> None:
    """Test finding agents by capability"""
    registry = AgentRegistry();

    agent_1 = AgentCapabilities(
        speakerUri="tag:test.com,2025:agent_1",
        agent_name="Text Agent",
        agent_version="1.0.0",
        capabilities=[CapabilityType.TEXT_GENERATION]
    );

    agent_2 = AgentCapabilities(
        speakerUri="tag:test.com,2025:agent_2",
        agent_name="Image Agent",
        agent_version="1.0.0",
        capabilities=[CapabilityType.IMAGE_GENERATION]
    );

    await registry.register_agent(agent_1);
    await registry.register_agent(agent_2);

    text_agents = await registry.find_agents_by_capability(
        CapabilityType.TEXT_GENERATION
    );
    assert len(text_agents) == 1;
    assert text_agents[0].speakerUri == "tag:test.com,2025:agent_1"


@pytest.mark.asyncio
async def test_update_heartbeat() -> None:
    """Test heartbeat update"""
    registry = AgentRegistry();

    capabilities = AgentCapabilities(
        speakerUri="tag:test.com,2025:agent_1",
        agent_name="Test Agent",
        agent_version="1.0.0",
        capabilities=[CapabilityType.TEXT_GENERATION]
    );

    await registry.register_agent(capabilities);
    original_heartbeat = capabilities.last_heartbeat;

    await registry.update_heartbeat("tag:test.com,2025:agent_1");
    agent = await registry.get_agent("tag:test.com,2025:agent_1");
    assert agent is not None;
    assert agent.last_heartbeat > original_heartbeat
