"""
Tests for Floor Manager
"""

import pytest
from src.floor_manager.floor_control import FloorControl, FloorState


@pytest.mark.asyncio
async def test_request_floor_immediate_grant() -> None:
    """Test immediate floor grant when available"""
    floor_control = FloorControl();
    conversation_id = "conv_1";
    agent_id = "agent_1";

    granted = await floor_control.request_floor(conversation_id, agent_id);
    assert granted is True;

    holder = await floor_control.get_floor_holder(conversation_id);
    assert holder == agent_id


@pytest.mark.asyncio
async def test_request_floor_queue() -> None:
    """Test floor request queuing"""
    floor_control = FloorControl();
    conversation_id = "conv_1";
    agent_1 = "agent_1";
    agent_2 = "agent_2";

    # First agent gets floor
    granted_1 = await floor_control.request_floor(conversation_id, agent_1);
    assert granted_1 is True;

    # Second agent queued
    granted_2 = await floor_control.request_floor(conversation_id, agent_2);
    assert granted_2 is False;

    holder = await floor_control.get_floor_holder(conversation_id);
    assert holder == agent_1


@pytest.mark.asyncio
async def test_release_floor() -> None:
    """Test floor release"""
    floor_control = FloorControl();
    conversation_id = "conv_1";
    agent_1 = "agent_1";
    agent_2 = "agent_2";

    await floor_control.request_floor(conversation_id, agent_1);
    await floor_control.request_floor(conversation_id, agent_2);

    released = await floor_control.release_floor(conversation_id, agent_1);
    assert released is True;

    holder = await floor_control.get_floor_holder(conversation_id);
    assert holder == agent_2


@pytest.mark.asyncio
async def test_release_floor_wrong_agent() -> None:
    """Test releasing floor by wrong agent"""
    floor_control = FloorControl();
    conversation_id = "conv_1";
    agent_1 = "agent_1";
    agent_2 = "agent_2";

    await floor_control.request_floor(conversation_id, agent_1);

    released = await floor_control.release_floor(conversation_id, agent_2);
    assert released is False

