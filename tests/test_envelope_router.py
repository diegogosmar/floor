"""
Tests for Envelope Router per OFP 1.0.0
"""

import pytest
from src.envelope_router.router import EnvelopeRouter
from src.envelope_router.envelope import (
    OpenFloorEnvelope,
    EventType,
    EventObject,
    SchemaObject,
    ConversationObject,
    SenderObject,
    ToObject
)


@pytest.mark.asyncio
async def test_register_route() -> None:
    """Test route registration"""
    router = EnvelopeRouter();
    speakerUri = "tag:test.com,2025:agent_1";

    async def handler(envelope: OpenFloorEnvelope) -> None:
        pass

    await router.register_route(speakerUri, handler);
    await router.unregister_route(speakerUri);


@pytest.mark.asyncio
async def test_route_envelope() -> None:
    """Test envelope routing"""
    router = EnvelopeRouter();
    speakerUri = "tag:test.com,2025:agent_1";
    received_envelopes = [];

    async def handler(envelope: OpenFloorEnvelope) -> None:
        received_envelopes.append(envelope);

    await router.register_route(speakerUri, handler);

    envelope = OpenFloorEnvelope(
        schema=SchemaObject(version="1.0.0"),
        conversation=ConversationObject(id="conv_1"),
        sender=SenderObject(speakerUri="tag:test.com,2025:agent_0"),
        events=[
            EventObject(
                to=ToObject(speakerUri=speakerUri),
                eventType=EventType.UTTERANCE,
                parameters={"text": "test"}
            )
        ]
    );

    success = await router.route_envelope(envelope);
    assert success is True;
    assert len(received_envelopes) == 1;
    assert received_envelopes[0].conversation.id == "conv_1"


@pytest.mark.asyncio
async def test_send_utterance() -> None:
    """Test sending utterance"""
    router = EnvelopeRouter();
    speakerUri = "tag:test.com,2025:agent_1";
    received_envelopes = [];

    async def handler(envelope: OpenFloorEnvelope) -> None:
        received_envelopes.append(envelope);

    await router.register_route(speakerUri, handler);

    envelope = await router.send_utterance(
        conversation_id="conv_1",
        sender_speakerUri="tag:test.com,2025:agent_0",
        sender_serviceUrl=None,
        target_speakerUri=speakerUri,
        target_serviceUrl=None,
        text="Hello, world!"
    );

    assert len(envelope.events) == 1;
    assert envelope.events[0].eventType == EventType.UTTERANCE;
    assert len(received_envelopes) == 1
