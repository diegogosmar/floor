"""
Envelope Router - Routes conversation envelopes between agents
"""

from typing import Optional, Dict, Callable
import asyncio
import structlog
from uuid import uuid4

from src.config import settings
from src.envelope_router.envelope import ConversationEnvelope, EnvelopeType

logger = structlog.get_logger()


class EnvelopeRouter:
    """
    Routes conversation envelopes between agents
    Implements OFP 1.0.0 envelope routing
    """

    def __init__(self) -> None:
        """Initialize envelope router"""
        self._routes: Dict[str, Callable] = {};
        self._queue: asyncio.Queue = asyncio.Queue(
            maxsize=settings.ROUTER_QUEUE_SIZE
        );
        self._max_retries = settings.ROUTER_MAX_RETRIES;
        self._timeout = settings.ROUTER_TIMEOUT;
        self._running = False

    async def register_route(
        self,
        agent_id: str,
        handler: Callable[[ConversationEnvelope], None]
    ) -> None:
        """
        Register routing handler for an agent

        Args:
            agent_id: Agent identifier
            handler: Async handler function for envelopes
        """
        self._routes[agent_id] = handler;
        logger.info("Route registered", agent_id=agent_id);

    async def unregister_route(self, agent_id: str) -> None:
        """
        Unregister routing handler for an agent

        Args:
            agent_id: Agent identifier
        """
        if agent_id in self._routes:
            del self._routes[agent_id];
            logger.info("Route unregistered", agent_id=agent_id);

    async def route_envelope(self, envelope: ConversationEnvelope) -> bool:
        """
        Route envelope to target agent

        Args:
            envelope: Conversation envelope to route

        Returns:
            True if routed successfully, False otherwise
        """
        if not envelope.to_agent:
            logger.error("Envelope missing target agent", envelope_id=envelope.envelope_id);
            return False

        if envelope.to_agent not in self._routes:
            logger.warning(
                "No route found for agent",
                agent_id=envelope.to_agent,
                envelope_id=envelope.envelope_id
            );
            return False

        try:
            await asyncio.wait_for(
                self._routes[envelope.to_agent](envelope),
                timeout=self._timeout
            );
            logger.debug(
                "Envelope routed",
                envelope_id=envelope.envelope_id,
                to_agent=envelope.to_agent
            );
            return True
        except asyncio.TimeoutError:
            logger.error(
                "Routing timeout",
                envelope_id=envelope.envelope_id,
                to_agent=envelope.to_agent
            );
            return False
        except Exception as e:
            logger.error(
                "Routing error",
                envelope_id=envelope.envelope_id,
                to_agent=envelope.to_agent,
                error=str(e)
            );
            return False

    async def send_envelope(
        self,
        conversation_id: str,
        from_agent: str,
        to_agent: str,
        payload: dict,
        envelope_type: EnvelopeType = EnvelopeType.MESSAGE,
        priority: int = 0
    ) -> ConversationEnvelope:
        """
        Create and send envelope

        Args:
            conversation_id: Conversation identifier
            from_agent: Source agent ID
            to_agent: Target agent ID
            payload: Envelope payload
            envelope_type: Type of envelope
            priority: Delivery priority

        Returns:
            Created envelope
        """
        envelope = ConversationEnvelope(
            envelope_id=str(uuid4()),
            conversation_id=conversation_id,
            envelope_type=envelope_type,
            from_agent=from_agent,
            to_agent=to_agent,
            payload=payload,
            priority=priority
        );

        success = await self.route_envelope(envelope);

        if not success and envelope.retry_count < self._max_retries:
            envelope.retry_count += 1;
            await asyncio.sleep(1);  # Brief delay before retry
            success = await self.route_envelope(envelope);

        if not success:
            logger.error(
                "Failed to route envelope after retries",
                envelope_id=envelope.envelope_id
            );

        return envelope

    async def broadcast_envelope(
        self,
        conversation_id: str,
        from_agent: str,
        payload: dict,
        envelope_type: EnvelopeType = EnvelopeType.MESSAGE,
        exclude_agents: Optional[list] = None
    ) -> list[ConversationEnvelope]:
        """
        Broadcast envelope to all registered agents

        Args:
            conversation_id: Conversation identifier
            from_agent: Source agent ID
            payload: Envelope payload
            envelope_type: Type of envelope
            exclude_agents: List of agent IDs to exclude

        Returns:
            List of created envelopes
        """
        exclude_agents = exclude_agents or [];
        envelopes = [];

        for agent_id in self._routes.keys():
            if agent_id == from_agent or agent_id in exclude_agents:
                continue

            envelope = await self.send_envelope(
                conversation_id=conversation_id,
                from_agent=from_agent,
                to_agent=agent_id,
                payload=payload,
                envelope_type=envelope_type
            );
            envelopes.append(envelope);

        return envelopes

    async def start(self) -> None:
        """Start router processing"""
        self._running = True;
        logger.info("Envelope router started");

    async def stop(self) -> None:
        """Stop router processing"""
        self._running = False;
        logger.info("Envelope router stopped");

