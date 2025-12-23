"""
Agent Registry - Manages agent registration and capability discovery per OFP 1.0.0
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import structlog

from src.config import settings
from src.agent_registry.capabilities import AgentCapabilities, CapabilityType

logger = structlog.get_logger()


class AgentRegistry:
    """
    Manages agent registration and capability discovery
    Implements OFP 1.0.0 agent registry
    Uses speakerUri as unique identifier per specification
    """

    def __init__(self) -> None:
        """Initialize agent registry"""
        # Indexed by speakerUri
        self._agents: Dict[str, AgentCapabilities] = {};
        self._max_agents = settings.REGISTRY_MAX_AGENTS;
        self._heartbeat_timeout = settings.REGISTRY_HEARTBEAT_TIMEOUT;
        self._cleanup_interval = settings.REGISTRY_CLEANUP_INTERVAL;
        self._cleanup_task: Optional[asyncio.Task] = None

    async def register_agent(self, capabilities: AgentCapabilities) -> bool:
        """
        Register an agent with its capabilities

        Args:
            capabilities: Agent capabilities definition

        Returns:
            True if registered successfully
        """
        if len(self._agents) >= self._max_agents:
            logger.warning(
                "Registry full",
                max_agents=self._max_agents,
                speakerUri=capabilities.speakerUri
            );
            return False

        self._agents[capabilities.speakerUri] = capabilities;
        logger.info(
            "Agent registered",
            speakerUri=capabilities.speakerUri,
            agent_name=capabilities.agent_name,
            capabilities=capabilities.capabilities
        );

        return True

    async def unregister_agent(self, speakerUri: str) -> bool:
        """
        Unregister an agent

        Args:
            speakerUri: Agent speaker URI

        Returns:
            True if unregistered successfully
        """
        if speakerUri not in self._agents:
            return False

        del self._agents[speakerUri];
        logger.info("Agent unregistered", speakerUri=speakerUri);
        return True

    async def update_heartbeat(self, speakerUri: str) -> bool:
        """
        Update agent heartbeat

        Args:
            speakerUri: Agent speaker URI

        Returns:
            True if heartbeat updated
        """
        if speakerUri not in self._agents:
            return False

        self._agents[speakerUri].update_heartbeat();
        logger.debug("Heartbeat updated", speakerUri=speakerUri);
        return True

    async def get_agent(self, speakerUri: str) -> Optional[AgentCapabilities]:
        """
        Get agent capabilities

        Args:
            speakerUri: Agent speaker URI

        Returns:
            Agent capabilities or None
        """
        return self._agents.get(speakerUri)

    async def find_agents_by_capability(
        self,
        capability: CapabilityType
    ) -> List[AgentCapabilities]:
        """
        Find agents with specific capability

        Args:
            capability: Capability type to search for

        Returns:
            List of agents with the capability
        """
        agents = [];
        for agent in self._agents.values():
            if agent.has_capability(capability):
                agents.append(agent);
        return agents

    async def list_agents(self) -> List[AgentCapabilities]:
        """
        List all registered agents

        Returns:
            List of all agent capabilities
        """
        return list(self._agents.values())

    async def cleanup_stale_agents(self) -> int:
        """
        Remove agents that haven't sent heartbeat

        Returns:
            Number of agents removed
        """
        now = datetime.utcnow();
        timeout = timedelta(seconds=self._heartbeat_timeout);
        stale_agents = [];

        for speakerUri, agent in self._agents.items():
            if now - agent.last_heartbeat > timeout:
                stale_agents.append(speakerUri);

        for speakerUri in stale_agents:
            await self.unregister_agent(speakerUri);

        if stale_agents:
            logger.info(
                "Cleaned up stale agents",
                count=len(stale_agents),
                speakerUris=stale_agents
            );

        return len(stale_agents)

    async def start_cleanup_task(self) -> None:
        """Start periodic cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            return

        async def cleanup_loop() -> None:
            while True:
                await asyncio.sleep(self._cleanup_interval);
                await self.cleanup_stale_agents();

        self._cleanup_task = asyncio.create_task(cleanup_loop());
        logger.info("Cleanup task started", interval=self._cleanup_interval);

    async def stop_cleanup_task(self) -> None:
        """Stop periodic cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel();
            try:
                await self._cleanup_task;
            except asyncio.CancelledError:
                pass
            logger.info("Cleanup task stopped");
