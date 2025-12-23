"""
Example Agent - Example implementation of BaseAgent
"""

from typing import Optional, Dict, Any
import structlog

from src.agents.base_agent import BaseAgent
from src.agent_registry.capabilities import CapabilityType
from src.envelope_router.envelope import ConversationEnvelope, EnvelopeType

logger = structlog.get_logger()


class ExampleAgent(BaseAgent):
    """
    Example agent implementation
    """

    def __init__(
        self,
        agent_id: str = "example_agent",
        agent_name: str = "Example Agent",
        agent_version: str = "1.0.0"
    ) -> None:
        """Initialize example agent"""
        super().__init__(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_version=agent_version,
            capabilities=[CapabilityType.TEXT_GENERATION]
        );

    async def handle_envelope(
        self,
        envelope: ConversationEnvelope
    ) -> Optional[ConversationEnvelope]:
        """
        Handle incoming conversation envelope

        Args:
            envelope: Conversation envelope to handle

        Returns:
            Response envelope or None
        """
        logger.info(
            "Handling envelope",
            agent_id=self.agent_id,
            envelope_id=envelope.envelope_id,
            envelope_type=envelope.envelope_type
        );

        if envelope.envelope_type == EnvelopeType.MESSAGE:
            response_payload = await self.process_message(
                envelope.conversation_id,
                envelope.payload
            );

            return ConversationEnvelope(
                envelope_id=f"response_{envelope.envelope_id}",
                conversation_id=envelope.conversation_id,
                envelope_type=EnvelopeType.MESSAGE,
                from_agent=self.agent_id,
                to_agent=envelope.from_agent,
                payload=response_payload
            );

        return None

    async def process_message(
        self,
        conversation_id: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a message

        Args:
            conversation_id: Conversation identifier
            message: Message payload

        Returns:
            Response payload
        """
        logger.info(
            "Processing message",
            agent_id=self.agent_id,
            conversation_id=conversation_id
        );

        # Example processing logic
        response = {
            "status": "processed",
            "agent_id": self.agent_id,
            "original_message": message,
            "response": f"Echo: {message.get('content', '')}"
        };

        return response

