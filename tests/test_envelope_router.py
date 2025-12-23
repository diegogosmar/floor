"""
Tests for Envelope Router
"""

import pytest
from src.envelope_router.router import EnvelopeRouter
from src.envelope_router.envelope import ConversationEnvelope, EnvelopeType


@pytest.mark.asyncio
async def test_register_route() -> None:
    """Test route registration"""
    router = EnvelopeRouter();
    agent_id = "agent_1";

    async def handler(envelope: ConversationEnvelope) -> None:
        pass

    await router.register_route(agent_id, handler);
    await router.unregister_route(agent_id);


@pytest.mark.asyncio
async def test_route_envelope() -> None:
    """Test envelope routing"""
    router = EnvelopeRouter();
    agent_id = "agent_1";
    received_envelopes = [];

    async def handler(envelope: ConversationEnvelope) -> None:
        received_envelopes.append(envelope);

    await router.register_route(agent_id, handler);

    envelope = ConversationEnvelope(
        envelope_id="test_1",
        conversation_id="conv_1",
        envelope_type=EnvelopeType.MESSAGE,
        from_agent="agent_0",
        to_agent=agent_id,
        payload={"content": "test"}
    );

    success = await router.route_envelope(envelope);
    assert success is True;
    assert len(received_envelopes) == 1;
    assert received_envelopes[0].envelope_id == "test_1"


@pytest.mark.asyncio
async def test_send_envelope() -> None:
    """Test sending envelope"""
    router = EnvelopeRouter();
    agent_id = "agent_1";
    received_envelopes = [];

    async def handler(envelope: ConversationEnvelope) -> None:
        received_envelopes.append(envelope);

    await router.register_route(agent_id, handler);

    envelope = await router.send_envelope(
        conversation_id="conv_1",
        from_agent="agent_0",
        to_agent=agent_id,
        payload={"content": "test"}
    );

    assert envelope.to_agent == agent_id;
    assert len(received_envelopes) == 1

