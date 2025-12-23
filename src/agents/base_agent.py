"""
Base Agent - Base class for OFP 1.0.0 agents
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import structlog

from src.agent_registry.capabilities import AgentCapabilities, CapabilityType
from src.envelope_router.envelope import OpenFloorEnvelope, EventType, EventObject

logger = structlog.get_logger()


class BaseAgent(ABC):
    """
    Base class for Open Floor Protocol 1.0.0 agents
    Uses speakerUri and serviceUrl per OFP 1.0.0 specification
    """

    def __init__(
        self,
        speakerUri: str,
        agent_name: str,
        serviceUrl: Optional[str] = None,
        agent_version: str = "1.0.0",
        capabilities: Optional[list[CapabilityType]] = None
    ) -> None:
        """
        Initialize base agent

        Args:
            speakerUri: Unique URI identifying the agent (per OFP 1.0.0)
            agent_name: Human-readable agent name
            serviceUrl: Optional service URL
            agent_version: Agent version
            capabilities: List of agent capabilities
        """
        self.speakerUri = speakerUri;
        self.serviceUrl = serviceUrl;
        self.agent_name = agent_name;
        self.agent_version = agent_version;
        self.capabilities_list = capabilities or [];

    def get_capabilities(self) -> AgentCapabilities:
        """
        Get agent capabilities definition

        Returns:
            Agent capabilities object
        """
        return AgentCapabilities(
            speakerUri=self.speakerUri,
            serviceUrl=self.serviceUrl,
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            capabilities=self.capabilities_list
        );

    @abstractmethod
    async def handle_envelope(
        self,
        envelope: OpenFloorEnvelope
    ) -> Optional[OpenFloorEnvelope]:
        """
        Handle incoming conversation envelope

        Args:
            envelope: Open Floor envelope to handle

        Returns:
            Response envelope or None
        """
        pass

    @abstractmethod
    async def process_utterance(
        self,
        conversation_id: str,
        utterance_text: str,
        sender_speakerUri: str
    ) -> Optional[str]:
        """
        Process an utterance

        Args:
            conversation_id: Conversation identifier
            utterance_text: Text of the utterance
            sender_speakerUri: Speaker URI of the sender

        Returns:
            Response text or None
        """
        pass

    async def start(self) -> None:
        """Start agent"""
        logger.info("Agent started", speakerUri=self.speakerUri);

    async def stop(self) -> None:
        """Stop agent"""
        logger.info("Agent stopped", speakerUri=self.speakerUri);
