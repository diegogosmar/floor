"""
Tests for Agents
"""

import pytest
from src.agents.base_agent import BaseAgent
from src.agents.example_agent import ExampleAgent
from src.envelope_router.envelope import ConversationEnvelope, EnvelopeType
from src.agent_registry.capabilities import CapabilityType


@pytest.mark.asyncio
async def test_example_agent_initialization() -> None:
    """Test example agent initialization"""
    agent = ExampleAgent(
        agent_id="test_agent",
        agent_name="Test Agent"
    );

    assert agent.agent_id == "test_agent";
    assert agent.agent_name == "Test Agent";
    assert CapabilityType.TEXT_GENERATION in agent.capabilities_list


@pytest.mark.asyncio
async def test_example_agent_capabilities() -> None:
    """Test example agent capabilities"""
    agent = ExampleAgent();
    capabilities = agent.get_capabilities();

    assert capabilities.agent_id == agent.agent_id;
    assert capabilities.agent_name == agent.agent_name;
    assert len(capabilities.capabilities) > 0


@pytest.mark.asyncio
async def test_example_agent_process_message() -> None:
    """Test example agent message processing"""
    agent = ExampleAgent();

    message = {"content": "Hello, world!"};
    response = await agent.process_message("conv_1", message);

    assert response["status"] == "processed";
    assert response["agent_id"] == agent.agent_id;
    assert "Hello, world!" in response["response"]


@pytest.mark.asyncio
async def test_example_agent_handle_envelope() -> None:
    """Test example agent envelope handling"""
    agent = ExampleAgent();

    envelope = ConversationEnvelope(
        envelope_id="test_1",
        conversation_id="conv_1",
        envelope_type=EnvelopeType.MESSAGE,
        from_agent="agent_0",
        to_agent=agent.agent_id,
        payload={"content": "test message"}
    );

    response = await agent.handle_envelope(envelope);
    assert response is not None;
    assert response.to_agent == "agent_0";
    assert response.from_agent == agent.agent_id

