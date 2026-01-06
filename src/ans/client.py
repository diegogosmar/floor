"""
ANS Client - Library for Floor Manager to interact with Agent Name Server

ANS (Agent Name Server) provides agent discovery services similar to DNS.
"""

import httpx
from typing import List, Optional, Dict, Any
from src.ans.models import ManifestData, ManifestFilters
from src.floor_manager.envelope import (
    OpenFloorEnvelope,
    EventType,
    SenderObject,
    EventObject,
    ConversationObject,
    SchemaObject
)
import structlog

logger = structlog.get_logger()


class ANSClient:
    """
    Client for interacting with ANS (Agent Name Server).
    
    ANS provides agent discovery services similar to DNS (Domain Name Server).
    
    Usage:
        client = ANSClient("http://localhost:8001")
        manifests = await client.get_manifests(filters={"capabilities": ["text_generation"]})
    """
    
    def __init__(
        self,
        server_url: str = "http://localhost:8001",
        client_speaker_uri: str = "tag:floor.manager,2025:manager"
    ):
        """
        Initialize ANS Client.
        
        Args:
            server_url: URL of ANS (Agent Name Server)
            client_speaker_uri: Speaker URI of the client (Floor Manager)
        """
        self.server_url = server_url.rstrip("/")
        self.client_speaker_uri = client_speaker_uri
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("ANSClient initialized", server_url=server_url)
    
    async def get_manifests(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ManifestData]:
        """
        Get manifests from server using OFP getManifests event.
        
        Args:
            filters: Optional filters dict with keys:
                - capabilities: List[str]
                - organization: str
                - role: str
                - speaker_uri: str
        
        Returns:
            List of ManifestData objects
        """
        # Build filters
        manifest_filters = None
        if filters:
            manifest_filters = ManifestFilters(**filters)
        
        # Create OFP envelope
        envelope = OpenFloorEnvelope(
            schema={"version": "1.0.1"},
            sender=SenderObject(speakerUri=self.client_speaker_uri),
            events=[
                EventObject(
                    eventType=EventType.GET_MANIFESTS,
                    parameters={
                        "filters": manifest_filters.model_dump(exclude_none=True) if manifest_filters else {}
                    }
                )
            ]
        )
        
        # Send request
        try:
            response = await self.client.post(
                f"{self.server_url}/api/v1/manifests/get",
                json=envelope.model_dump(exclude_none=True)
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Extract manifests from publishManifests event
            manifests = []
            for event in data.get("events", []):
                if event.get("eventType") == "publishManifests":
                    manifest_list = event.get("parameters", {}).get("manifests", [])
                    for m in manifest_list:
                        try:
                            manifest_data = ManifestData(**m)
                            manifests.append(manifest_data)
                        except Exception as e:
                            logger.warning("Invalid manifest in response", error=str(e))
            
            logger.info(
                "Manifests retrieved",
                count=len(manifests),
                filters=filters
            )
            
            return manifests
            
        except httpx.HTTPError as e:
            logger.error("HTTP error getting manifests", error=str(e))
            raise
        except Exception as e:
            logger.error("Error getting manifests", error=str(e))
            raise
    
    async def publish_manifest(self, manifest_data: ManifestData) -> bool:
        """
        Publish a manifest to the server.
        
        Args:
            manifest_data: ManifestData to publish
        
        Returns:
            True if successful
        """
        # Create OFP envelope (conversation is required but not used for publishing)
        envelope = OpenFloorEnvelope(
            schema_obj=SchemaObject(version="1.0.1"),
            conversation=ConversationObject(id="manifest_publish"),
            sender=SenderObject(
                speakerUri=manifest_data.identification.speakerUri,
                serviceUrl=manifest_data.identification.serviceUrl
            ),
            events=[
                EventObject(
                    eventType=EventType.PUBLISH_MANIFESTS,
                    parameters={
                        "manifests": [manifest_data.model_dump()]
                    }
                )
            ]
        )
        
        # Send request
        try:
            response = await self.client.post(
                f"{self.server_url}/api/v1/manifests/publish",
                json=envelope.model_dump(exclude_none=True)
            )
            response.raise_for_status()
            
            logger.info(
                "Manifest published",
                speaker_uri=manifest_data.identification.speakerUri
            )
            
            return True
            
        except httpx.HTTPError as e:
            logger.error("HTTP error publishing manifest", error=str(e))
            raise
        except Exception as e:
            logger.error("Error publishing manifest", error=str(e))
            raise
    
    async def search_by_capability(self, capability: str) -> List[ManifestData]:
        """
        Convenience method to search by single capability.
        
        Args:
            capability: Capability name (e.g., "text_generation")
        
        Returns:
            List of manifests with this capability
        """
        return await self.get_manifests(filters={"capabilities": [capability]})
    
    async def search_by_organization(self, organization: str) -> List[ManifestData]:
        """
        Convenience method to search by organization.
        
        Args:
            organization: Organization name
        
        Returns:
            List of manifests from this organization
        """
        return await self.get_manifests(filters={"organization": organization})
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

