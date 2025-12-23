"""
Conversation Envelope - OFP 1.0.0 envelope format
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class EnvelopeType(str, Enum):
    """Envelope type enumeration"""
    MESSAGE = "message"
    CONTROL = "control"
    HEARTBEAT = "heartbeat"
    ACK = "ack"


class ConversationEnvelope(BaseModel):
    """
    Conversation envelope following OFP 1.0.0 specification
    """

    envelope_id: str = Field(..., description="Unique envelope identifier")
    conversation_id: str = Field(..., description="Conversation identifier")
    envelope_type: EnvelopeType = Field(..., description="Type of envelope")
    from_agent: str = Field(..., alias="from", description="Source agent ID")
    to_agent: Optional[str] = Field(None, alias="to", description="Target agent ID")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Envelope timestamp"
    )
    payload: Dict[str, Any] = Field(..., description="Envelope payload")
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata"
    )
    retry_count: int = Field(0, description="Retry attempt count")
    priority: int = Field(0, description="Delivery priority")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_dict(self) -> dict:
        """Convert envelope to dictionary"""
        return self.model_dump(by_alias=True, exclude_none=True)

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationEnvelope":
        """Create envelope from dictionary"""
        return cls(**data)

