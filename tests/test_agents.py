"""
Tests for Agents per OFP 1.0.0
"""

import pytest
from src.agents.example_agent import ExampleAgent
from src.envelope_router.envelope import (
    OpenFloorEnvelope,
    EventType,
    EventObject,
    SchemaObject,
    ConversationObject,
    SenderObject,
    ToObject
)
from src.agent_registry.capabilities import CapabilityType


@pytest.mark.asyncio
async def test_example_agent_initialization() -> None:
    """Test example agent initialization"""
    agent = ExampleAgent(
        speakerUri="tag:test.com,2025:test_agent",
        agent_name="Test Agent"
    );

    assert agent.speakerUri == "tag:test.com,2025:test_agent";
    assert agent.agent_name == "Test Agent";
    assert CapabilityType.TEXT_GENERATION in agent.capabilities_list


@pytest.mark.asyncio
async def test_example_agent_capabilities() -> None:
    """Test example agent capabilities"""
    agent = ExampleAgent();
    capabilities = agent.get_capabilities();

    assert capabilities.speakerUri == agent.speakerUri;
    assert capabilities.agent_name == agent.agent_name;
    assert len(capabilities.capabilities) > 0


@pytest.mark.asyncio
async def test_example_agent_process_utterance() -> None:
    """Test example agent utterance processing"""
    agent = ExampleAgent();

    response = await agent.process_utterance(
        "conv_1",
        "Hello, world!",
        "tag:test.com,2025:sender"
    );

    assert response is not None;
    assert "Hello, world!" in response


@pytest.mark.asyncio
async def test_example_agent_handle_envelope() -> None:
    """Test example agent envelope handling"""
    agent = ExampleAgent();
    sender_speakerUri = "tag:test.com,2025:sender";

    envelope = OpenFloorEnvelope(
        schema=SchemaObject(version="1.0.0"),
        conversation=ConversationObject(id="conv_1"),
        sender=SenderObject(speakerUri=sender_speakerUri),
        events=[
            EventObject(
                to=ToObject(speakerUri=agent.speakerUri),
                eventType=EventType.UTTERANCE,
                parameters={
                    "dialogEvent": {
                        "speakerUri": sender_speakerUri,
                        "features": {
                            "text": {
                                "mimeType": "text/plain",
                                "tokens": [{"token": "test message"}]
                            }
                        }
                    }
                }
            )
        ]
    );

    response = await agent.handle_envelope(envelope);
    assert response is not None;
    assert len(response.events) > 0;
    assert response.sender.speakerUri == agent.speakerUri
