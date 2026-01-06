"""
ANS storage implementation (in-memory for prototype, can be extended to PostgreSQL)
"""

from typing import List, Optional, Dict
from datetime import datetime
from src.ans.models import Manifest, ManifestFilters, ManifestStatus
import structlog

logger = structlog.get_logger()


class ManifestStorage:
    """In-memory manifest storage (prototype)"""
    
    def __init__(self):
        self._manifests: Dict[str, Manifest] = {}  # speaker_uri -> Manifest
        logger.info("ManifestStorage initialized (in-memory)")
    
    async def store(self, manifest: Manifest) -> Manifest:
        """
        Store or update a manifest.
        
        Args:
            manifest: Manifest to store
        
        Returns:
            Stored manifest with ID
        """
        # Check if exists
        if manifest.speaker_uri in self._manifests:
            # Update existing
            existing = self._manifests[manifest.speaker_uri]
            manifest.id = existing.id
            manifest.published_at = existing.published_at
            manifest.updated_at = datetime.utcnow()
            logger.info("Updating manifest", speaker_uri=manifest.speaker_uri)
        else:
            # New manifest
            manifest.id = len(self._manifests) + 1
            manifest.published_at = datetime.utcnow()
            manifest.updated_at = datetime.utcnow()
            logger.info("Storing new manifest", speaker_uri=manifest.speaker_uri)
        
        self._manifests[manifest.speaker_uri] = manifest
        return manifest
    
    async def get(self, speaker_uri: str) -> Optional[Manifest]:
        """Get manifest by speaker URI"""
        return self._manifests.get(speaker_uri)
    
    async def search(self, filters: Optional[ManifestFilters] = None) -> List[Manifest]:
        """
        Search manifests with filters.
        
        Args:
            filters: Search filters
        
        Returns:
            List of matching manifests
        """
        results = list(self._manifests.values())
        
        if not filters:
            # Return all active manifests
            return [m for m in results if m.status == ManifestStatus.ACTIVE]
        
        # Apply filters
        if filters.status:
            results = [m for m in results if m.status == filters.status]
        elif filters.status is None:
            # Default: only active
            results = [m for m in results if m.status == ManifestStatus.ACTIVE]
        
        if filters.speaker_uri:
            results = [m for m in results if m.speaker_uri == filters.speaker_uri]
        
        if filters.organization:
            results = [m for m in results if m.organization == filters.organization]
        
        if filters.role:
            results = [m for m in results if m.role == filters.role]
        
        if filters.capabilities:
            # Manifest must have ALL requested capabilities
            required_caps = set(filters.capabilities)
            results = [
                m for m in results
                if required_caps.issubset(set(m.capabilities))
            ]
        
        return results
    
    async def list_all(self, status: Optional[ManifestStatus] = ManifestStatus.ACTIVE) -> List[Manifest]:
        """List all manifests (optionally filtered by status)"""
        if status:
            return [m for m in self._manifests.values() if m.status == status]
        return list(self._manifests.values())
    
    async def delete(self, speaker_uri: str) -> bool:
        """Delete a manifest"""
        if speaker_uri in self._manifests:
            del self._manifests[speaker_uri]
            logger.info("Deleted manifest", speaker_uri=speaker_uri)
            return True
        return False
    
    async def count(self, filters: Optional[ManifestFilters] = None) -> int:
        """Count manifests matching filters"""
        results = await self.search(filters)
        return len(results)


# Global storage instance
_storage: Optional[ManifestStorage] = None


def get_storage() -> ManifestStorage:
    """Get storage instance (singleton)"""
    global _storage
    if _storage is None:
        _storage = ManifestStorage()
    return _storage

