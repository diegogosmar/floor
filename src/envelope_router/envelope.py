"""
Conversation Envelope - OFP 1.0.0 Interoperable Conversation Envelope Specification
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event type enumeration per OFP 1.0.0"""
    # Speaking or sending multi-media events
    UTTERANCE = "utterance"
    CONTEXT = "context"
    
    # Joining or leaving conversations
    INVITE = "invite"
    UNINVITE = "uninvite"
    DECLINE_INVITE = "declineInvite"
    BYE = "bye"
    
    # Discovering other agents
    GET_MANIFESTS = "getManifests"
    PUBLISH_MANIFESTS = "publishManifests"
    
    # Floor management
    REQUEST_FLOOR = "requestFloor"
    GRANT_FLOOR = "grantFloor"
    REVOKE_FLOOR = "revokeFloor"
    YIELD_FLOOR = "yieldFloor"


class SchemaObject(BaseModel):
    """Schema object per OFP 1.0.0"""
    version: str = Field("1.0.0", description="Schema version")
    url: Optional[str] = Field(
        None,
        description="URL to JSON schema for validation"
    )


class ConversantIdentification(BaseModel):
    """Conversant identification per OFP 1.0.0"""
    speakerUri: str = Field(..., description="Unique URI identifying the agent")
    serviceUrl: Optional[str] = Field(None, description="URL of the agent service")
    organization: Optional[str] = None
    conversationalName: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    synopsis: Optional[str] = None


class ConversantObject(BaseModel):
    """Conversant object per OFP 1.0.0"""
    identification: ConversantIdentification = Field(..., description="Agent identification")
    persistentState: Optional[Dict[str, Any]] = Field(
        None,
        description="Persistent state for this conversant"
    )


class ConversationObject(BaseModel):
    """Conversation object per OFP 1.0.0"""
    id: str = Field(..., description="Unique conversation identifier")
    conversants: Optional[List[ConversantObject]] = Field(
        None,
        description="List of conversants in the conversation"
    )


class SenderObject(BaseModel):
    """Sender object per OFP 1.0.0"""
    speakerUri: str = Field(..., description="Unique URI identifying the sender")
    serviceUrl: Optional[str] = Field(
        None,
        description="URL of the sender service"
    )


class ToObject(BaseModel):
    """To object for event addressing per OFP 1.0.0"""
    speakerUri: Optional[str] = Field(None, description="URI of intended recipient")
    serviceUrl: Optional[str] = Field(None, description="URL of intended recipient")
    private: bool = Field(False, description="Whether event is private")


class EventObject(BaseModel):
    """Event object per OFP 1.0.0"""
    to: Optional[ToObject] = Field(
        None,
        description="Target recipient (optional, if absent event is for all)"
    )
    eventType: EventType = Field(..., description="Type of event")
    reason: Optional[str] = Field(
        None,
        description="Reason for sending event (may contain @tokens)"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Event-specific parameters"
    )


class OpenFloorEnvelope(BaseModel):
    """
    Open Floor Conversation Envelope per OFP 1.0.0 specification
    
    Structure:
    {
      "openFloor": {
        "schema": {...},
        "conversation": {...},
        "sender": {...},
        "events": [...]
      }
    }
    """

    schema: SchemaObject = Field(..., description="Schema version and URL")
    conversation: ConversationObject = Field(..., description="Conversation information")
    sender: SenderObject = Field(..., description="Sender information")
    events: List[EventObject] = Field(..., description="List of events")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_dict(self) -> dict:
        """Convert envelope to dictionary with openFloor wrapper"""
        return {"openFloor": self.model_dump(exclude_none=True)}

    @classmethod
    def from_dict(cls, data: dict) -> "OpenFloorEnvelope":
        """Create envelope from dictionary"""
        if "openFloor" in data:
            return cls(**data["openFloor"]);
        return cls(**data)

    def get_events_for_agent(
        self,
        speakerUri: str,
        serviceUrl: Optional[str] = None
    ) -> List[EventObject]:
        """
        Get events intended for a specific agent
        
        Args:
            speakerUri: Agent speaker URI
            serviceUrl: Optional service URL for matching
            
        Returns:
            List of events for this agent
        """
        events = [];
        for event in self.events:
            # If no 'to' section, event is for all recipients
            if event.to is None:
                events.append(event);
                continue

            # Check if event is addressed to this agent
            if (
                event.to.speakerUri == speakerUri
                or (serviceUrl and event.to.serviceUrl == serviceUrl)
            ):
                events.append(event);

        return events


# Alias for backward compatibility
ConversationEnvelope = OpenFloorEnvelope
