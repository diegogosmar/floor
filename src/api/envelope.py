"""
Conversation Envelope API endpoints per OFP 1.0.0
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import structlog

from src.envelope_router.router import EnvelopeRouter
from src.envelope_router.envelope import (
    OpenFloorEnvelope,
    EventType,
    EventObject,
    ToObject
)

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/envelopes", tags=["Envelope Routing"])

# Global router instance (in production, use dependency injection)
_envelope_router: Optional[EnvelopeRouter] = None


def get_envelope_router() -> EnvelopeRouter:
    """Get envelope router instance"""
    global _envelope_router
    if _envelope_router is None:
        _envelope_router = EnvelopeRouter();
    return _envelope_router


class SendEnvelopeRequest(BaseModel):
    """Send envelope request model"""
    envelope: Dict[str, Any]  # OpenFloorEnvelope as dict


class SendUtteranceRequest(BaseModel):
    """Send utterance request model"""
    conversation_id: str
    sender_speakerUri: str
    sender_serviceUrl: Optional[str] = None
    target_speakerUri: Optional[str] = None
    target_serviceUrl: Optional[str] = None
    text: str
    private: bool = False


@router.post("/send", response_model=dict)
async def send_envelope(
    request: SendEnvelopeRequest,
    envelope_router: EnvelopeRouter = Depends(get_envelope_router)
) -> dict:
    """
    Send a conversation envelope per OFP 1.0.0
    
    Accepts full OpenFloorEnvelope JSON structure
    """
    try:
        envelope = OpenFloorEnvelope.from_dict(request.envelope);
        logger.info(
            "Sending envelope",
            conversation_id=envelope.conversation.id,
            sender=envelope.sender.speakerUri,
            event_count=len(envelope.events)
        );

        success = await envelope_router.route_envelope(envelope);

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to route envelope"
            );

        return {
            "success": True,
            "conversation_id": envelope.conversation.id,
            "events_routed": len(envelope.events)
        };
    except Exception as e:
        logger.error("Error sending envelope", error=str(e));
        raise HTTPException(status_code=400, detail=str(e));


@router.post("/utterance", response_model=dict)
async def send_utterance(
    request: SendUtteranceRequest,
    envelope_router: EnvelopeRouter = Depends(get_envelope_router)
) -> dict:
    """
    Send an utterance event per OFP 1.0.0
    
    Simplified endpoint for sending text utterances
    """
    logger.info(
        "Sending utterance",
        conversation_id=request.conversation_id,
        sender=request.sender_speakerUri,
        target=request.target_speakerUri
    );

    envelope = await envelope_router.send_utterance(
        conversation_id=request.conversation_id,
        sender_speakerUri=request.sender_speakerUri,
        sender_serviceUrl=request.sender_serviceUrl,
        target_speakerUri=request.target_speakerUri,
        target_serviceUrl=request.target_serviceUrl,
        text=request.text,
        private=request.private
    );

    return {
        "success": True,
        "conversation_id": envelope.conversation.id,
        "envelope": envelope.to_dict()
    };


@router.post("/validate", response_model=dict)
async def validate_envelope(
    envelope: Dict[str, Any]
) -> dict:
    """
    Validate an envelope against OFP 1.0.0 schema
    """
    try:
        ofp_envelope = OpenFloorEnvelope.from_dict(envelope);
        return {
            "valid": True,
            "version": ofp_envelope.schema.version,
            "conversation_id": ofp_envelope.conversation.id
        };
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        };

