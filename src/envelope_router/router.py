"""
Envelope Router - Routes conversation envelopes between agents per OFP 1.0.1

Per OFP 1.0.1: Privacy flag is only respected for utterance events.
For all other events, the privacy flag is ignored.
"""

from typing import Optional, Dict, Callable, List
import asyncio
import structlog
from uuid import uuid4

from src.config import settings
from src.envelope_router.envelope import (
    OpenFloorEnvelope,
    EventType,
    EventObject,
    SchemaObject,
    ConversationObject,
    SenderObject,
    ToObject
)

logger = structlog.get_logger()


class EnvelopeRouter:
    """
    Routes conversation envelopes between agents
    Implements OFP 1.0.1 envelope routing
    """

    def __init__(self) -> None:
        """Initialize envelope router"""
        # Routes indexed by speakerUri
        self._routes: Dict[str, Callable] = {};
        self._queue: asyncio.Queue = asyncio.Queue(
            maxsize=settings.ROUTER_QUEUE_SIZE
        );
        self._max_retries = settings.ROUTER_MAX_RETRIES;
        self._timeout = settings.ROUTER_TIMEOUT;
        self._running = False

    async def register_route(
        self,
        speakerUri: str,
        handler: Callable[[OpenFloorEnvelope], None]
    ) -> None:
        """
        Register routing handler for an agent

        Args:
            speakerUri: Agent speaker URI
            handler: Async handler function for envelopes
        """
        self._routes[speakerUri] = handler;
        logger.info("Route registered", speakerUri=speakerUri);

    async def unregister_route(self, speakerUri: str) -> None:
        """
        Unregister routing handler for an agent

        Args:
            speakerUri: Agent speaker URI
        """
        if speakerUri in self._routes:
            del self._routes[speakerUri];
            logger.info("Route unregistered", speakerUri=speakerUri);

    async def route_envelope(self, envelope: OpenFloorEnvelope) -> bool:
        """
        Route envelope to target agents based on events per OFP 1.0.1

        Args:
            envelope: Open Floor envelope to route

        Returns:
            True if routed successfully, False otherwise
        """
        routed = False;

        for event in envelope.events:
            # OFP 1.0.1: Privacy flag only respected for utterance events
            is_private = (
                event.to is not None
                and event.to.private
                and event.eventType == EventType.UTTERANCE
            );

            # If no 'to' section, event is for all recipients
            if event.to is None:
                # Broadcast to all registered agents except sender
                for speakerUri, handler in self._routes.items():
                    if speakerUri == envelope.sender.speakerUri:
                        continue;
                    try:
                        await asyncio.wait_for(
                            handler(envelope),
                            timeout=self._timeout
                        );
                        routed = True;
                    except Exception as e:
                        logger.error(
                            "Routing error",
                            speakerUri=speakerUri,
                            error=str(e)
                        );
                continue;

            # Route to specific agent
            target_speakerUri = event.to.speakerUri;
            if not target_speakerUri:
                logger.warning("Event has 'to' section but no speakerUri");
                continue;

            # For private utterance events, only route to intended recipient
            if is_private:
                if target_speakerUri not in self._routes:
                    logger.warning(
                        "No route found for private event recipient",
                        speakerUri=target_speakerUri
                    );
                    continue;
                
                try:
                    await asyncio.wait_for(
                        self._routes[target_speakerUri](envelope),
                        timeout=self._timeout
                    );
                    routed = True;
                    logger.debug(
                        "Private utterance routed",
                        speakerUri=target_speakerUri
                    );
                except Exception as e:
                    logger.error(
                        "Private routing error",
                        speakerUri=target_speakerUri,
                        error=str(e)
                    );
                continue;

            # For non-utterance events or non-private utterances:
            # Privacy flag is ignored per OFP 1.0.1
            # Route to intended recipient
            if target_speakerUri not in self._routes:
                logger.warning(
                    "No route found for agent",
                    speakerUri=target_speakerUri
                );
                continue;

            try:
                await asyncio.wait_for(
                    self._routes[target_speakerUri](envelope),
                    timeout=self._timeout
                );
                routed = True;
                logger.debug(
                    "Envelope routed",
                    speakerUri=target_speakerUri,
                    eventType=event.eventType
                );
            except asyncio.TimeoutError:
                logger.error(
                    "Routing timeout",
                    speakerUri=target_speakerUri
                );
            except Exception as e:
                logger.error(
                    "Routing error",
                    speakerUri=target_speakerUri,
                    error=str(e)
                );

        return routed

    async def create_envelope(
        self,
        conversation_id: str,
        sender_speakerUri: str,
        sender_serviceUrl: Optional[str] = None,
        events: Optional[List[EventObject]] = None
    ) -> OpenFloorEnvelope:
        """
        Create a new Open Floor envelope

        Args:
            conversation_id: Conversation identifier
            sender_speakerUri: Sender speaker URI
            sender_serviceUrl: Optional sender service URL
            events: List of events (defaults to empty list)

        Returns:
            Created envelope
        """
        schema = SchemaObject(version="1.0.1");
        conversation = ConversationObject(id=conversation_id);
        sender = SenderObject(
            speakerUri=sender_speakerUri,
            serviceUrl=sender_serviceUrl
        );

        return OpenFloorEnvelope(
            schema_obj=schema,
            conversation=conversation,
            sender=sender,
            events=events or []
        );

    async def send_utterance(
        self,
        conversation_id: str,
        sender_speakerUri: str,
        sender_serviceUrl: Optional[str],
        target_speakerUri: Optional[str],
        target_serviceUrl: Optional[str],
        text: str,
        private: bool = False
    ) -> OpenFloorEnvelope:
        """
        Send an utterance event

        Args:
            conversation_id: Conversation identifier
            sender_speakerUri: Sender speaker URI
            sender_serviceUrl: Optional sender service URL
            target_speakerUri: Optional target speaker URI
            target_serviceUrl: Optional target service URL
            text: Utterance text
            private: Whether utterance is private

        Returns:
            Created envelope
        """
        to_obj = None;
        if target_speakerUri:
            to_obj = ToObject(
                speakerUri=target_speakerUri,
                serviceUrl=target_serviceUrl,
                private=private
            );

        event = EventObject(
            to=to_obj,
            eventType=EventType.UTTERANCE,
            parameters={
                "dialogEvent": {
                    "speakerUri": sender_speakerUri,
                    "features": {
                        "text": {
                            "mimeType": "text/plain",
                            "tokens": [{"token": text}]
                        }
                    }
                }
            }
        );

        envelope = await self.create_envelope(
            conversation_id=conversation_id,
            sender_speakerUri=sender_speakerUri,
            sender_serviceUrl=sender_serviceUrl,
            events=[event]
        );

        await self.route_envelope(envelope);
        return envelope

    async def start(self) -> None:
        """Start router processing"""
        self._running = True;
        logger.info("Envelope router started");

    async def stop(self) -> None:
        """Stop router processing"""
        self._running = False;
        logger.info("Envelope router stopped");
