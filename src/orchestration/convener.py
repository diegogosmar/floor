"""
Convener-Based Orchestration Pattern per OFP 1.0.0

A convener agent explicitly manages the floor, inviting/disinviting participants
and granting floor to agents according to defined logic (round-robin, priority-based, context-aware).
Useful for structured workflows.
"""

from typing import List, Optional, Dict
from enum import Enum
import structlog

from src.floor_manager.floor_control import FloorControl
from src.agent_registry.registry import AgentRegistry
from src.envelope_router.envelope import (
    OpenFloorEnvelope,
    EventType,
    EventObject,
    ToObject
)

logger = structlog.get_logger()


class ConvenerStrategy(str, Enum):
    """Convener orchestration strategies"""
    ROUND_ROBIN = "round_robin"
    PRIORITY_BASED = "priority_based"
    CONTEXT_AWARE = "context_aware"


class ConvenerOrchestrator:
    """
    Convener-Based Orchestration per OFP 1.0.0
    
    A convener agent manages the floor explicitly, coordinating multi-agent conversations
    """

    def __init__(
        self,
        convener_speakerUri: str,
        floor_control: FloorControl,
        agent_registry: AgentRegistry,
        strategy: ConvenerStrategy = ConvenerStrategy.ROUND_ROBIN
    ) -> None:
        """
        Initialize convener orchestrator

        Args:
            convener_speakerUri: Speaker URI of the convener agent
            floor_control: Floor control instance
            agent_registry: Agent registry instance
            strategy: Orchestration strategy
        """
        self.convener_speakerUri = convener_speakerUri;
        self.floor_control = floor_control;
        self.agent_registry = agent_registry;
        self.strategy = strategy;
        self._participants: Dict[str, dict] = {};
        self._turn_order: List[str] = [];
        self._current_turn_index = 0

    async def invite_participant(
        self,
        conversation_id: str,
        participant_speakerUri: str,
        priority: int = 0
    ) -> bool:
        """
        Invite a participant to the conversation

        Args:
            conversation_id: Conversation identifier
            participant_speakerUri: Participant speaker URI
            priority: Participant priority

        Returns:
            True if invited successfully
        """
        agent = await self.agent_registry.get_agent(participant_speakerUri);
        if not agent:
            logger.warning(
                "Cannot invite unknown agent",
                speakerUri=participant_speakerUri
            );
            return False;

        self._participants[participant_speakerUri] = {
            "priority": priority,
            "invited": True
        };

        if self.strategy == ConvenerStrategy.ROUND_ROBIN:
            self._turn_order.append(participant_speakerUri);

        logger.info(
            "Participant invited",
            conversation_id=conversation_id,
            participant=participant_speakerUri
        );

        return True

    async def grant_floor_to_next(
        self,
        conversation_id: str
    ) -> Optional[str]:
        """
        Grant floor to next participant according to strategy

        Args:
            conversation_id: Conversation identifier

        Returns:
            Speaker URI of agent granted floor, or None
        """
        if not self._participants:
            return None;

        if self.strategy == ConvenerStrategy.ROUND_ROBIN:
            if not self._turn_order:
                return None;

            next_speakerUri = self._turn_order[
                self._current_turn_index % len(self._turn_order)
            ];
            self._current_turn_index += 1;

        elif self.strategy == ConvenerStrategy.PRIORITY_BASED:
            # Sort by priority (higher first)
            sorted_participants = sorted(
                self._participants.items(),
                key=lambda x: -x[1]["priority"]
            );
            next_speakerUri = sorted_participants[0][0];

        else:  # CONTEXT_AWARE - same as priority for now
            sorted_participants = sorted(
                self._participants.items(),
                key=lambda x: -x[1]["priority"]
            );
            next_speakerUri = sorted_participants[0][0];

        # Grant floor
        await self.floor_control.request_floor(
            conversation_id,
            next_speakerUri,
            priority=self._participants[next_speakerUri]["priority"]
        );

        logger.info(
            "Floor granted by convener",
            conversation_id=conversation_id,
            speakerUri=next_speakerUri,
            strategy=self.strategy
        );

        return next_speakerUri

    async def revoke_floor(
        self,
        conversation_id: str,
        speakerUri: str,
        reason: str = "@override"
    ) -> bool:
        """
        Revoke floor from a participant

        Args:
            conversation_id: Conversation identifier
            speakerUri: Participant speaker URI
            reason: Reason for revocation

        Returns:
            True if revoked successfully
        """
        # Check if agent has floor
        holder = await self.floor_control.get_floor_holder(conversation_id);
        if holder != speakerUri:
            return False;

        # Release floor (will trigger queue processing)
        await self.floor_control.release_floor(conversation_id, speakerUri);

        logger.info(
            "Floor revoked by convener",
            conversation_id=conversation_id,
            speakerUri=speakerUri,
            reason=reason
        );

        return True

    async def uninvite_participant(
        self,
        conversation_id: str,
        participant_speakerUri: str
    ) -> bool:
        """
        Remove participant from conversation

        Args:
            conversation_id: Conversation identifier
            participant_speakerUri: Participant speaker URI

        Returns:
            True if removed successfully
        """
        if participant_speakerUri not in self._participants:
            return False;

        # Revoke floor if they have it
        await self.revoke_floor(conversation_id, participant_speakerUri, "@uninvite");

        # Remove from participants
        del self._participants[participant_speakerUri];

        # Remove from turn order
        if participant_speakerUri in self._turn_order:
            self._turn_order.remove(participant_speakerUri);

        logger.info(
            "Participant uninvited",
            conversation_id=conversation_id,
            participant=participant_speakerUri
        );

        return True

