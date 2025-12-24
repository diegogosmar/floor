"""
Floor Control - Manages floor control primitives per OFP 1.0.1

The Floor Manager acts as the Convener, making all floor decisions autonomously.
This implements the floor as an autonomous state machine per OFP 1.0.1.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
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
    Implements OFP 1.0.1 floor control primitives
    
    The Floor Manager IS the Convener per OFP 1.0.1:
    - All floor decisions are made autonomously by the convener
    - Floor state is managed as an autonomous state machine
    - Agents request/yield floor but do not make decisions
    """

    def __init__(self, convener_speakerUri: Optional[str] = None) -> None:
        """
        Initialize floor control (convener)
        
        Args:
            convener_speakerUri: Speaker URI of the convener (Floor Manager)
                                 If None, uses default from settings
        """
        self._floor_holders: dict[str, dict] = {}
        self._floor_requests: dict[str, list] = {}
        self._floor_timeout = settings.FLOOR_TIMEOUT
        self._max_hold_time = settings.FLOOR_MAX_HOLD_TIME
        # Convener identification per OFP 1.0.1
        self.convener_speakerUri = convener_speakerUri or "tag:floor.manager,2025:convener"
        self._conversation_metadata: dict[str, dict] = {}  # Track conversation metadata

    async def request_floor(
        self,
        conversation_id: str,
        speakerUri: str,
        priority: int = 0
    ) -> bool:
        """
        Request floor for a conversation per OFP 1.0.1
        
        The convener (Floor Manager) makes the decision autonomously.

        Args:
            conversation_id: Unique conversation identifier
            speakerUri: Speaker URI requesting the floor
            priority: Request priority (higher = more priority)

        Returns:
            True if floor granted immediately, False if queued
        """
        logger.info(
            "Floor request received by convener",
            conversation_id=conversation_id,
            speakerUri=speakerUri,
            priority=priority,
            convener=self.convener_speakerUri
        )

        # Initialize conversation metadata if needed
        if conversation_id not in self._conversation_metadata:
            self._conversation_metadata[conversation_id] = {
                "assignedFloorRoles": {"convener": self.convener_speakerUri}
            }

        # Check if floor is available (convener decision)
        if conversation_id not in self._floor_holders:
            await self._grant_floor(conversation_id, speakerUri);
            return True

        # Add to request queue (convener will process later)
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
        Release floor for a conversation (yieldFloor per OFP 1.0.1)
        
        The convener processes the yield and grants floor to next in queue.

        Args:
            conversation_id: Unique conversation identifier
            speakerUri: Speaker URI releasing the floor

        Returns:
            True if floor was released, False if agent didn't hold floor
        """
        logger.info(
            "Floor yield received by convener",
            conversation_id=conversation_id,
            speakerUri=speakerUri,
            convener=self.convener_speakerUri
        )

        if conversation_id not in self._floor_holders:
            return False

        holder = self._floor_holders[conversation_id];
        if holder["speakerUri"] != speakerUri:
            return False

        del self._floor_holders[conversation_id];
        
        # Clear floorGranted in conversation metadata
        if conversation_id in self._conversation_metadata:
            self._conversation_metadata[conversation_id].pop("floorGranted", None);

        # Convener grants floor to next requester
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
            await self._revoke_floor(conversation_id, reason="@timeout");
            return None

        return holder["speakerUri"]

    async def _grant_floor(self, conversation_id: str, speakerUri: str) -> None:
        """
        Grant floor to an agent per OFP 1.0.1 grantFloor event
        
        This is a convener decision. Updates floorGranted in conversation metadata.
        """
        granted_at = datetime.utcnow();
        self._floor_holders[conversation_id] = {
            "speakerUri": speakerUri,
            "granted_at": granted_at
        };
        
        # Update conversation metadata with floorGranted per OFP 1.0.1
        if conversation_id not in self._conversation_metadata:
            self._conversation_metadata[conversation_id] = {
                "assignedFloorRoles": {"convener": self.convener_speakerUri}
            };
        
        self._conversation_metadata[conversation_id]["floorGranted"] = {
            "speakerUri": speakerUri,
            "grantedAt": granted_at.isoformat()
        };
        
        logger.info(
            "Floor granted by convener",
            conversation_id=conversation_id,
            speakerUri=speakerUri,
            convener=self.convener_speakerUri,
            granted_at=granted_at
        );

    async def _revoke_floor(self, conversation_id: str, reason: str = "@timeout") -> None:
        """
        Revoke floor due to timeout or other reason per OFP 1.0.1 revokeFloor event
        
        This is a convener decision.
        """
        if conversation_id in self._floor_holders:
            speakerUri = self._floor_holders[conversation_id]["speakerUri"];
            del self._floor_holders[conversation_id];
            
            # Clear floorGranted in conversation metadata
            if conversation_id in self._conversation_metadata:
                self._conversation_metadata[conversation_id].pop("floorGranted", None);
            
            logger.warning(
                "Floor revoked by convener",
                conversation_id=conversation_id,
                speakerUri=speakerUri,
                reason=reason,
                convener=self.convener_speakerUri
            );
            await self._process_queue(conversation_id);
    
    def get_conversation_metadata(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation metadata including assignedFloorRoles and floorGranted
        
        Returns metadata per OFP 1.0.1 conversation object structure.
        """
        return self._conversation_metadata.get(conversation_id, {
            "assignedFloorRoles": {"convener": self.convener_speakerUri}
        });

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

