"""
Base Agent - Base class for OFP agents
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import structlog

from src.agent_registry.capabilities import AgentCapabilities, CapabilityType
from src.envelope_router.envelope import ConversationEnvelope, EnvelopeType

logger = structlog.get_logger()


class BaseAgent(ABC):
    """
    Base class for Open Floor Protocol agents
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        agent_version: str = "1.0.0",
        capabilities: Optional[list[CapabilityType]] = None,
        endpoint_url: Optional[str] = None
    ) -> None:
        """
        Initialize base agent

        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            agent_version: Agent version
            capabilities: List of agent capabilities
            endpoint_url: Agent endpoint URL
        """
        self.agent_id = agent_id;
        self.agent_name = agent_name;
        self.agent_version = agent_version;
        self.capabilities_list = capabilities or [];
        self.endpoint_url = endpoint_url;

    def get_capabilities(self) -> AgentCapabilities:
        """
        Get agent capabilities definition

        Returns:
            Agent capabilities object
        """
        return AgentCapabilities(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            capabilities=self.capabilities_list,
            endpoint_url=self.endpoint_url
        );

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    async def send_message(
        self,
        conversation_id: str,
        to_agent: str,
        payload: Dict[str, Any]
    ) -> ConversationEnvelope:
        """
        Send message to another agent

        Args:
            conversation_id: Conversation identifier
            to_agent: Target agent ID
            payload: Message payload

        Returns:
            Sent envelope
        """
        logger.info(
            "Sending message",
            from_agent=self.agent_id,
            to_agent=to_agent,
            conversation_id=conversation_id
        );
        # This would be implemented by the router integration
        raise NotImplementedError("Router integration required")

    async def start(self) -> None:
        """Start agent"""
        logger.info("Agent started", agent_id=self.agent_id);

    async def stop(self) -> None:
        """Stop agent"""
        logger.info("Agent stopped", agent_id=self.agent_id);

