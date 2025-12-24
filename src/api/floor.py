"""
Floor Management API endpoints per OFP 1.0.1
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import structlog

from src.floor_manager.floor_control import FloorControl
from src.config import settings

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/floor", tags=["Floor Management"])

# Global floor control instance (in production, use dependency injection)
_floor_control: Optional[FloorControl] = None


def get_floor_control() -> FloorControl:
    """Get floor control instance"""
    global _floor_control
    if _floor_control is None:
        _floor_control = FloorControl();
    return _floor_control


class FloorRequest(BaseModel):
    """Request floor model"""
    conversation_id: str
    speakerUri: str
    priority: int = 0


class FloorRelease(BaseModel):
    """Release floor model"""
    conversation_id: str
    speakerUri: str


class FloorResponse(BaseModel):
    """Floor response model"""
    conversation_id: str
    granted: bool
    holder: Optional[str] = None
    queue_position: Optional[int] = None


@router.post("/request", response_model=FloorResponse)
async def request_floor(
    request: FloorRequest,
    floor_control: FloorControl = Depends(get_floor_control)
) -> FloorResponse:
    """
    Request floor for a conversation per OFP 1.0.1
    
    Implements requestFloor event behavior
    """
    logger.info(
        "Floor request API",
        conversation_id=request.conversation_id,
        speakerUri=request.speakerUri
    );

    granted = await floor_control.request_floor(
        request.conversation_id,
        request.speakerUri,
        request.priority
    );

    holder = await floor_control.get_floor_holder(request.conversation_id);

    return FloorResponse(
        conversation_id=request.conversation_id,
        granted=granted,
        holder=holder if granted else None
    );


@router.post("/release", response_model=dict)
async def release_floor(
    release: FloorRelease,
    floor_control: FloorControl = Depends(get_floor_control)
) -> dict:
    """
    Release floor for a conversation per OFP 1.0.1
    
    Implements yieldFloor event behavior
    """
    logger.info(
        "Floor release API",
        conversation_id=release.conversation_id,
        speakerUri=release.speakerUri
    );

    released = await floor_control.release_floor(
        release.conversation_id,
        release.speakerUri
    );

    if not released:
        raise HTTPException(
            status_code=400,
            detail="Floor not held by this agent"
        );

    return {
        "conversation_id": release.conversation_id,
        "released": True
    };


@router.get("/holder/{conversation_id}", response_model=dict)
async def get_floor_holder(
    conversation_id: str,
    floor_control: FloorControl = Depends(get_floor_control)
) -> dict:
    """
    Get current floor holder for a conversation
    """
    holder = await floor_control.get_floor_holder(conversation_id);
    
    # Get conversation metadata per OFP 1.0.1 (includes assignedFloorRoles and floorGranted)
    metadata = floor_control.get_conversation_metadata(conversation_id);

    return {
        "conversation_id": conversation_id,
        "holder": holder,
        "has_floor": holder is not None,
        "assignedFloorRoles": metadata.get("assignedFloorRoles"),
        "floorGranted": metadata.get("floorGranted")
    };

