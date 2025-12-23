"""
Agent Capabilities - Capability definitions per OFP 1.0.0
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
    Agent capabilities definition per OFP 1.0.0
    
    Uses speakerUri (unique URI) and serviceUrl (service endpoint)
    as per specification section 0.6
    """

    speakerUri: str = Field(..., description="Unique URI identifying the agent")
    serviceUrl: Optional[str] = Field(None, description="URL of the agent service")
    agent_name: str = Field(..., description="Human-readable agent name")
    agent_version: str = Field("1.0.0", description="Agent version")
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
    # Additional fields per OFP 1.0.0 manifest specification
    organization: Optional[str] = Field(None, description="Organization name")
    conversationalName: Optional[str] = Field(None, description="Conversational name")
    department: Optional[str] = Field(None, description="Department")
    role: Optional[str] = Field(None, description="Role")
    synopsis: Optional[str] = Field(None, description="Agent synopsis")

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

    def to_identification(self) -> Dict[str, Any]:
        """
        Convert to identification object per OFP 1.0.0 conversant format
        
        Returns:
            Identification dictionary
        """
        return {
            "speakerUri": self.speakerUri,
            "serviceUrl": self.serviceUrl,
            "organization": self.organization,
            "conversationalName": self.conversationalName,
            "department": self.department,
            "role": self.role,
            "synopsis": self.synopsis
        }
