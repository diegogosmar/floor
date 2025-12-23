"""
Agent Capabilities - Capability definitions for OFP agents
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CapabilityType(str, Enum):
    """Capability type enumeration"""
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    CODE_EXECUTION = "code_execution"
    DATA_ANALYSIS = "data_analysis"
    WEB_SEARCH = "web_search"
    FILE_OPERATIONS = "file_operations"
    CUSTOM = "custom"


class AgentCapabilities(BaseModel):
    """
    Agent capabilities definition
    """

    agent_id: str = Field(..., description="Agent identifier")
    agent_name: str = Field(..., description="Human-readable agent name")
    agent_version: str = Field(..., description="Agent version")
    capabilities: List[CapabilityType] = Field(
        ...,
        description="List of capability types"
    )
    custom_capabilities: Optional[List[str]] = Field(
        None,
        description="Custom capability identifiers"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional agent metadata"
    )
    registered_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Registration timestamp"
    )
    last_heartbeat: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last heartbeat timestamp"
    )
    endpoint_url: Optional[str] = Field(
        None,
        description="Agent endpoint URL for communication"
    )

    def has_capability(self, capability: CapabilityType) -> bool:
        """
        Check if agent has specific capability

        Args:
            capability: Capability type to check

        Returns:
            True if agent has capability
        """
        return capability in self.capabilities

    def update_heartbeat(self) -> None:
        """Update heartbeat timestamp"""
        self.last_heartbeat = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert capabilities to dictionary"""
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_dict(cls, data: dict) -> "AgentCapabilities":
        """Create capabilities from dictionary"""
        return cls(**data)

