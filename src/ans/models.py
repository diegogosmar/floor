"""
Data models for Manifest Server
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ManifestStatus(str, Enum):
    """Manifest status"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    INACTIVE = "inactive"


class ConversantIdentification(BaseModel):
    """Conversant identification per OFP 1.0.1"""
    speakerUri: str = Field(..., description="Unique URI identifying the agent")
    serviceUrl: Optional[str] = Field(None, description="URL of the agent service")
    organization: Optional[str] = None
    conversationalName: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    synopsis: Optional[str] = None


class ManifestCapability(BaseModel):
    """Agent capability"""
    name: str = Field(..., description="Capability name (e.g., 'text_generation')")
    description: Optional[str] = None
    version: Optional[str] = None


class ManifestData(BaseModel):
    """Manifest data structure"""
    identification: ConversantIdentification
    capabilities: List[str] = Field(default_factory=list, description="List of capability names")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class Manifest(BaseModel):
    """Stored manifest with metadata"""
    id: Optional[int] = None
    speaker_uri: str
    service_url: Optional[str] = None
    organization: Optional[str] = None
    conversational_name: Optional[str] = None
    role: Optional[str] = None
    synopsis: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    status: ManifestStatus = ManifestStatus.ACTIVE
    published_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def from_manifest_data(cls, manifest_data: ManifestData) -> "Manifest":
        """Create Manifest from ManifestData"""
        ident = manifest_data.identification
        return cls(
            speaker_uri=ident.speakerUri,
            service_url=ident.serviceUrl,
            organization=ident.organization,
            conversational_name=ident.conversationalName,
            role=ident.role,
            synopsis=ident.synopsis,
            capabilities=manifest_data.capabilities,
            metadata=manifest_data.metadata or {},
            published_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    def to_manifest_data(self) -> ManifestData:
        """Convert to ManifestData"""
        return ManifestData(
            identification=ConversantIdentification(
                speakerUri=self.speaker_uri,
                serviceUrl=self.service_url,
                organization=self.organization,
                conversationalName=self.conversational_name,
                role=self.role,
                synopsis=self.synopsis
            ),
            capabilities=self.capabilities,
            metadata=self.metadata
        )


class ManifestFilters(BaseModel):
    """Filters for manifest search"""
    capabilities: Optional[List[str]] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    speaker_uri: Optional[str] = None
    status: Optional[ManifestStatus] = ManifestStatus.ACTIVE


class PublishManifestsRequest(BaseModel):
    """Request to publish manifests"""
    manifests: List[ManifestData] = Field(..., description="List of manifests to publish")


class GetManifestsRequest(BaseModel):
    """Request to get manifests"""
    filters: Optional[ManifestFilters] = Field(None, description="Search filters")


class GetManifestsResponse(BaseModel):
    """Response with manifests"""
    manifests: List[ManifestData] = Field(..., description="List of found manifests")
    count: int = Field(..., description="Total count")

