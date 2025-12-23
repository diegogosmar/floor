"""
Tests for Floor Manager per OFP 1.0.0
"""

import pytest
from src.floor_manager.floor_control import FloorControl


@pytest.mark.asyncio
async def test_request_floor_immediate_grant() -> None:
    """Test immediate floor grant when available"""
    floor_control = FloorControl();
    conversation_id = "conv_1";
    speakerUri = "tag:test.com,2025:agent_1";

    granted = await floor_control.request_floor(conversation_id, speakerUri);
    assert granted is True;

    holder = await floor_control.get_floor_holder(conversation_id);
    assert holder == speakerUri


@pytest.mark.asyncio
async def test_request_floor_queue() -> None:
    """Test floor request queuing"""
    floor_control = FloorControl();
    conversation_id = "conv_1";
    speakerUri_1 = "tag:test.com,2025:agent_1";
    speakerUri_2 = "tag:test.com,2025:agent_2";

    # First agent gets floor
    granted_1 = await floor_control.request_floor(conversation_id, speakerUri_1);
    assert granted_1 is True;

    # Second agent queued
    granted_2 = await floor_control.request_floor(conversation_id, speakerUri_2);
    assert granted_2 is False;

    holder = await floor_control.get_floor_holder(conversation_id);
    assert holder == speakerUri_1


@pytest.mark.asyncio
async def test_release_floor() -> None:
    """Test floor release"""
    floor_control = FloorControl();
    conversation_id = "conv_1";
    speakerUri_1 = "tag:test.com,2025:agent_1";
    speakerUri_2 = "tag:test.com,2025:agent_2";

    await floor_control.request_floor(conversation_id, speakerUri_1);
    await floor_control.request_floor(conversation_id, speakerUri_2);

    released = await floor_control.release_floor(conversation_id, speakerUri_1);
    assert released is True;

    holder = await floor_control.get_floor_holder(conversation_id);
    assert holder == speakerUri_2


@pytest.mark.asyncio
async def test_release_floor_wrong_agent() -> None:
    """Test releasing floor by wrong agent"""
    floor_control = FloorControl();
    conversation_id = "conv_1";
    speakerUri_1 = "tag:test.com,2025:agent_1";
    speakerUri_2 = "tag:test.com,2025:agent_2";

    await floor_control.request_floor(conversation_id, speakerUri_1);

    released = await floor_control.release_floor(conversation_id, speakerUri_2);
    assert released is False
