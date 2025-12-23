"""
Floor Control - Manages floor control primitives per OFP 1.0.0
"""

from datetime import datetime, timedelta
from typing import Optional
from enum import Enum
import structlog

from src.config import settings

logger = structlog.get_logger()


class FloorState(Enum):
    """Floor state enumeration"""
    IDLE = "idle"
    GRANTED = "granted"
    REQUESTED = "requested"
    RELEASED = "released"


class FloorControl:
    """
    Manages floor control for conversations
    Implements OFP 1.0.0 floor control primitives
    """

    def __init__(self) -> None:
        """Initialize floor control"""
        self._floor_holders: dict[str, dict] = {}
        self._floor_requests: dict[str, list] = {}
        self._floor_timeout = settings.FLOOR_TIMEOUT
        self._max_hold_time = settings.FLOOR_MAX_HOLD_TIME

    async def request_floor(
        self,
        conversation_id: str,
        speakerUri: str,
        priority: int = 0
    ) -> bool:
        """
        Request floor for a conversation per OFP 1.0.0

        Args:
            conversation_id: Unique conversation identifier
            speakerUri: Speaker URI requesting the floor
            priority: Request priority (higher = more priority)

        Returns:
            True if floor granted immediately, False if queued
        """
        logger.info(
            "Floor request",
            conversation_id=conversation_id,
            speakerUri=speakerUri,
            priority=priority
        )

        # Check if floor is available
        if conversation_id not in self._floor_holders:
            await self._grant_floor(conversation_id, speakerUri);
            return True

        # Add to request queue
        if conversation_id not in self._floor_requests:
            self._floor_requests[conversation_id] = []

        request = {
            "speakerUri": speakerUri,
            "priority": priority,
            "timestamp": datetime.utcnow()
        }
        self._floor_requests[conversation_id].append(request);
        self._floor_requests[conversation_id].sort(
            key=lambda x: (-x["priority"], x["timestamp"])
        );

        return False

    async def release_floor(self, conversation_id: str, speakerUri: str) -> bool:
        """
        Release floor for a conversation (yieldFloor per OFP 1.0.0)

        Args:
            conversation_id: Unique conversation identifier
            speakerUri: Speaker URI releasing the floor

        Returns:
            True if floor was released, False if agent didn't hold floor
        """
        logger.info(
            "Floor release",
            conversation_id=conversation_id,
            speakerUri=speakerUri
        )

        if conversation_id not in self._floor_holders:
            return False

        holder = self._floor_holders[conversation_id];
        if holder["speakerUri"] != speakerUri:
            return False

        del self._floor_holders[conversation_id];

        # Grant floor to next requester
        await self._process_queue(conversation_id);

        return True

    async def get_floor_holder(self, conversation_id: str) -> Optional[str]:
        """
        Get current floor holder for a conversation

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            Speaker URI holding the floor, or None
        """
        if conversation_id not in self._floor_holders:
            return None

        holder = self._floor_holders[conversation_id];
        # Check if floor grant has expired
        if datetime.utcnow() - holder["granted_at"] > timedelta(
            seconds=self._max_hold_time
        ):
            await self._revoke_floor(conversation_id);
            return None

        return holder["speakerUri"]

    async def _grant_floor(self, conversation_id: str, speakerUri: str) -> None:
        """Grant floor to an agent per OFP 1.0.0 grantFloor event"""
        self._floor_holders[conversation_id] = {
            "speakerUri": speakerUri,
            "granted_at": datetime.utcnow()
        };
        logger.info(
            "Floor granted",
            conversation_id=conversation_id,
            speakerUri=speakerUri
        );

    async def _revoke_floor(self, conversation_id: str) -> None:
        """Revoke floor due to timeout per OFP 1.0.0 revokeFloor event"""
        if conversation_id in self._floor_holders:
            speakerUri = self._floor_holders[conversation_id]["speakerUri"];
            del self._floor_holders[conversation_id];
            logger.warning(
                "Floor revoked due to timeout",
                conversation_id=conversation_id,
                speakerUri=speakerUri
            );
            await self._process_queue(conversation_id);

    async def _process_queue(self, conversation_id: str) -> None:
        """Process floor request queue"""
        if (
            conversation_id not in self._floor_requests
            or not self._floor_requests[conversation_id]
        ):
            return

        next_request = self._floor_requests[conversation_id].pop(0);
        await self._grant_floor(conversation_id, next_request["speakerUri"]);

        if not self._floor_requests[conversation_id]:
            del self._floor_requests[conversation_id];

