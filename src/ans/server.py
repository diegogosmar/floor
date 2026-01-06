"""
ANS: Agent Name Server - FastAPI application

Agent Name Server provides OFP-compliant endpoints for agent discovery:
- publishManifests: Agents publish their manifests
- getManifests: Agents discover other agents

ANS acts as a public directory service (similar to DNS) for OFP agents.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import structlog

from src.config import settings
from src.ans.models import (
    Manifest,
    ManifestData,
    ManifestFilters,
    PublishManifestsRequest,
    GetManifestsRequest,
    GetManifestsResponse
)
from src.ans.storage import get_storage, ManifestStorage
from src.floor_manager.envelope import OpenFloorEnvelope, EventType

logger = structlog.get_logger()

app = FastAPI(
    title="ANS: Agent Name Server",
    version="1.0.0",
    description="Public directory service for OFP-compliant agent discovery (like DNS for agents)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Public server - allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentNameServer:
    """ANS: Agent Name Server implementation
    
    Acts as a public directory service for OFP-compliant agent discovery.
    Similar to DNS (Domain Name Server) but for agents.
    """
    
    def __init__(self, storage: ManifestStorage):
        self.storage = storage
        self.server_speaker_uri = "tag:ans.openfloorprotocol.org,2025:server"
    
    async def publish_manifests(self, manifests: List[ManifestData]) -> List[Manifest]:
        """
        Publish manifests to the server.
        
        Args:
            manifests: List of manifests to publish
        
        Returns:
            List of stored manifests
        """
        stored = []
        for manifest_data in manifests:
            manifest = Manifest.from_manifest_data(manifest_data)
            stored_manifest = await self.storage.store(manifest)
            stored.append(stored_manifest)
            logger.info(
                "Manifest published",
                speaker_uri=manifest.speaker_uri,
                capabilities=manifest.capabilities
            )
        return stored
    
    async def get_manifests(self, filters: Optional[ManifestFilters] = None) -> List[ManifestData]:
        """
        Get manifests matching filters.
        
        Args:
            filters: Search filters
        
        Returns:
            List of matching manifests
        """
        manifests = await self.storage.search(filters)
        return [m.to_manifest_data() for m in manifests]


def get_ans_server(storage: ManifestStorage = Depends(get_storage)) -> AgentNameServer:
    """Get ANS (Agent Name Server) instance"""
    return AgentNameServer(storage)


@app.get("/")
async def root() -> dict:
    """Root endpoint"""
    return {
        "name": "ANS: Agent Name Server",
        "version": "1.0.0",
        "description": "Public directory service for OFP-compliant agent discovery (like DNS for agents)",
        "acronym": "ANS",
        "endpoints": {
            "publish": "/api/v1/manifests/publish",
            "get": "/api/v1/manifests/get",
            "search": "/api/v1/manifests/search",
            "health": "/health"
        }
    }


@app.get("/health")
async def health() -> dict:
    """Health check"""
    storage = get_storage()
    count = await storage.count()
    return {
        "status": "healthy",
        "manifests_count": count
    }


@app.post("/api/v1/manifests/publish")
async def publish_manifests(
    envelope: OpenFloorEnvelope,
    server: AgentNameServer = Depends(get_ans_server)
) -> dict:
    """
    Publish manifests using OFP envelope format.
    
    Expects envelope with publishManifests event.
    """
    # Find publishManifests event
    publish_event = None
    for event in envelope.events:
        if event.eventType == EventType.PUBLISH_MANIFESTS:
            publish_event = event
            break
    
    if not publish_event:
        raise HTTPException(
            status_code=400,
            detail="No publishManifests event found in envelope"
        )
    
    # Extract manifests from event parameters
    if not publish_event.parameters or "manifests" not in publish_event.parameters:
        raise HTTPException(
            status_code=400,
            detail="No manifests in event parameters"
        )
    
    manifests_data = publish_event.parameters["manifests"]
    
    # Convert to ManifestData objects
    manifests = []
    for m in manifests_data:
        try:
            manifest_data = ManifestData(**m)
            manifests.append(manifest_data)
        except Exception as e:
            logger.warning("Invalid manifest data", error=str(e))
            continue
    
    if not manifests:
        raise HTTPException(
            status_code=400,
            detail="No valid manifests found"
        )
    
    # Store manifests
    stored = await server.publish_manifests(manifests)
    
    # Return OFP-compliant response envelope
    from src.floor_manager.envelope import (
        OpenFloorEnvelope,
        SchemaObject,
        ConversationObject,
        SenderObject,
        EventObject
    )
    
    response_envelope = OpenFloorEnvelope(
        schema_obj=SchemaObject(version="1.0.1"),
        conversation=ConversationObject(id=envelope.conversation.id),
        sender=SenderObject(speakerUri=server.server_speaker_uri),
        events=[
            EventObject(
                eventType=EventType.PUBLISH_MANIFESTS,
                parameters={
                    "manifests": [m.to_manifest_data().model_dump() for m in stored],
                    "status": "published",
                    "count": len(stored)
                }
            )
        ]
    )
    
    return response_envelope.model_dump(exclude_none=True)


@app.post("/api/v1/manifests/get")
async def get_manifests(
    envelope: OpenFloorEnvelope,
    server: AgentNameServer = Depends(get_ans_server)
) -> dict:
    """
    Get manifests using OFP envelope format.
    
    Expects envelope with getManifests event.
    """
    # Find getManifests event
    get_event = None
    for event in envelope.events:
        if event.eventType == EventType.GET_MANIFESTS:
            get_event = event
            break
    
    if not get_event:
        raise HTTPException(
            status_code=400,
            detail="No getManifests event found in envelope"
        )
    
    # Extract filters from event parameters
    filters = None
    if get_event.parameters and "filters" in get_event.parameters:
        filters_data = get_event.parameters["filters"]
        try:
            filters = ManifestFilters(**filters_data)
        except Exception as e:
            logger.warning("Invalid filters", error=str(e))
    
    # Search manifests
    manifests_data = await server.get_manifests(filters)
    count = len(manifests_data)
    
    # Return OFP-compliant response envelope
    from src.floor_manager.envelope import (
        OpenFloorEnvelope,
        SchemaObject,
        ConversationObject,
        SenderObject,
        EventObject
    )
    
    response_envelope = OpenFloorEnvelope(
        schema_obj=SchemaObject(version="1.0.1"),
        conversation=ConversationObject(id=envelope.conversation.id),
        sender=SenderObject(speakerUri=server.server_speaker_uri),
        events=[
            EventObject(
                eventType=EventType.PUBLISH_MANIFESTS,
                parameters={
                    "manifests": [m.model_dump() for m in manifests_data],
                    "count": count
                }
            )
        ]
    )
    
    return response_envelope.model_dump(exclude_none=True)


@app.get("/api/v1/manifests/search")
async def search_manifests(
    capabilities: Optional[str] = None,
    organization: Optional[str] = None,
    role: Optional[str] = None,
    speaker_uri: Optional[str] = None,
    server: AgentNameServer = Depends(get_ans_server)
) -> GetManifestsResponse:
    """
    REST API endpoint for searching manifests (non-OFP, for convenience).
    
    Query parameters:
    - capabilities: Comma-separated list (e.g., "text_generation,translation")
    - organization: Filter by organization
    - role: Filter by role
    - speaker_uri: Filter by speaker URI
    """
    filters = ManifestFilters(
        capabilities=capabilities.split(",") if capabilities else None,
        organization=organization,
        role=role,
        speaker_uri=speaker_uri
    )
    
    manifests_data = await server.get_manifests(filters)
    count = len(manifests_data)
    
    return GetManifestsResponse(
        manifests=manifests_data,
        count=count
    )


@app.get("/api/v1/manifests/list")
async def list_manifests(
    server: AgentNameServer = Depends(get_ans_server)
) -> dict:
    """
    List all active manifests (REST API, for convenience).
    """
    storage = get_storage()
    manifests = await storage.list_all()
    
    return {
        "manifests": [m.to_manifest_data().model_dump() for m in manifests],
        "count": len(manifests)
    }

