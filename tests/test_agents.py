"""
Tests for Agents per OFP 1.0.0
"""

import pytest
from src.agents.example_agent import ExampleAgent
from src.floor_manager.envelope import (
    OpenFloorEnvelope,
    EventType,
    EventObject,
    SchemaObject,
    ConversationObject,
    SenderObject,
    ToObject
)
# CapabilityType removed in OFP 1.0.1 refactoring


@pytest.mark.asyncio
async def test_example_agent_initialization() -> None:
    """Test example agent initialization per OFP 1.0.1"""
    agent = ExampleAgent(
        speakerUri="tag:test.com,2025:test_agent",
        agent_name="Test Agent"
    )

    assert agent.speakerUri == "tag:test.com,2025:test_agent"
    assert agent.agent_name == "Test Agent"
    # Note: capabilities removed in OFP 1.0.1 refactoring


@pytest.mark.asyncio
async def test_example_agent_process_utterance() -> None:
    """Test example agent utterance processing"""
    agent = ExampleAgent()

    response = await agent.process_utterance(
        "conv_1",
        "Hello, world!",
        "tag:test.com,2025:sender"
    )

    assert response is not None
    assert "Hello, world!" in response


@pytest.mark.asyncio
async def test_example_agent_handle_envelope() -> None:
    """Test example agent envelope handling per OFP 1.0.1"""
    agent = ExampleAgent()
    sender_speakerUri = "tag:test.com,2025:sender"

    envelope = OpenFloorEnvelope(
        schema_obj=SchemaObject(version="1.1.0"),
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
    )

    response = await agent.handle_envelope(envelope)
    assert response is not None
    assert len(response.events) > 0
    assert response.sender.speakerUri == agent.speakerUri
