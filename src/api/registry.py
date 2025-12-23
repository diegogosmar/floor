"""
Agent Registry API endpoints per OFP 1.0.0
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import structlog

from src.agent_registry.registry import AgentRegistry
from src.agent_registry.capabilities import AgentCapabilities, CapabilityType

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/agents", tags=["Agent Registry"])

# Global registry instance (in production, use dependency injection)
_agent_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get agent registry instance"""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry();
    return _agent_registry


class RegisterAgentRequest(BaseModel):
    """Register agent request model"""
    speakerUri: str
    serviceUrl: Optional[str] = None
    agent_name: str
    agent_version: str = "1.0.0"
    capabilities: List[str]  # List of CapabilityType values
    custom_capabilities: Optional[List[str]] = None
    organization: Optional[str] = None
    conversationalName: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    synopsis: Optional[str] = None


class HeartbeatRequest(BaseModel):
    """Heartbeat request model"""
    speakerUri: str


@router.post("/register", response_model=dict)
async def register_agent(
    request: RegisterAgentRequest,
    registry: AgentRegistry = Depends(get_agent_registry)
) -> dict:
    """
    Register an agent with capabilities per OFP 1.0.0
    
    Implements agent manifest registration
    """
    try:
        # Convert string capabilities to CapabilityType enum
        capability_types = [];
        for cap_str in request.capabilities:
            try:
                capability_types.append(CapabilityType(cap_str));
            except ValueError:
                logger.warning("Unknown capability type", capability=cap_str);

        capabilities = AgentCapabilities(
            speakerUri=request.speakerUri,
            serviceUrl=request.serviceUrl,
            agent_name=request.agent_name,
            agent_version=request.agent_version,
            capabilities=capability_types,
            custom_capabilities=request.custom_capabilities,
            organization=request.organization,
            conversationalName=request.conversationalName,
            department=request.department,
            role=request.role,
            synopsis=request.synopsis
        );

        success = await registry.register_agent(capabilities);

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to register agent (registry may be full)"
            );

        logger.info("Agent registered", speakerUri=request.speakerUri);

        return {
            "success": True,
            "speakerUri": request.speakerUri,
            "capabilities": capabilities.to_dict()
        };
    except Exception as e:
        logger.error("Error registering agent", error=str(e));
        raise HTTPException(status_code=400, detail=str(e));


@router.post("/heartbeat", response_model=dict)
async def update_heartbeat(
    request: HeartbeatRequest,
    registry: AgentRegistry = Depends(get_agent_registry)
) -> dict:
    """
    Update agent heartbeat
    """
    success = await registry.update_heartbeat(request.speakerUri);

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        );

    return {
        "success": True,
        "speakerUri": request.speakerUri
    };


@router.get("/{speakerUri}", response_model=dict)
async def get_agent(
    speakerUri: str,
    registry: AgentRegistry = Depends(get_agent_registry)
) -> dict:
    """
    Get agent capabilities by speakerUri
    """
    agent = await registry.get_agent(speakerUri);

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        );

    return agent.to_dict();


@router.get("/capability/{capability}", response_model=List[dict])
async def find_agents_by_capability(
    capability: str,
    registry: AgentRegistry = Depends(get_agent_registry)
) -> List[dict]:
    """
    Find agents by capability type per OFP 1.0.0 discovery
    
    Implements getManifests/publishManifests pattern
    """
    try:
        capability_type = CapabilityType(capability);
        agents = await registry.find_agents_by_capability(capability_type);

        return [agent.to_dict() for agent in agents];
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid capability type: {capability}"
        );


@router.get("/", response_model=List[dict])
async def list_agents(
    registry: AgentRegistry = Depends(get_agent_registry)
) -> List[dict]:
    """
    List all registered agents
    """
    agents = await registry.list_agents();
    return [agent.to_dict() for agent in agents];


@router.delete("/{speakerUri}", response_model=dict)
async def unregister_agent(
    speakerUri: str,
    registry: AgentRegistry = Depends(get_agent_registry)
) -> dict:
    """
    Unregister an agent
    """
    success = await registry.unregister_agent(speakerUri);

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        );

    return {
        "success": True,
        "speakerUri": speakerUri
    };

