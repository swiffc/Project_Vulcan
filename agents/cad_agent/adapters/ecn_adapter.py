"""
ECN Adapter
Thin wrapper for Engineering Change Notice tracking.
Uses Memory Brain (ChromaDB) for persistent storage.

Packages Used (via pip - NOT in project):
- chromadb: Vector storage for ECN history
- Already in requirements.txt
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger("cad_agent.ecn")


@dataclass
class ECNRecord:
    ecn_number: str
    title: str
    description: str
    affected_parts: List[str]
    changes: List[Dict]
    status: str = "draft"  # draft, approved, implemented
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


class ECNAdapter:
    """
    Adapter for ECN tracking with Memory Brain integration.
    Tracks cumulative changes to parts/assemblies/drawings.
    """
    
    def __init__(self, memory_client=None):
        self.memory = memory_client
        self._counter = 0
        
    def _generate_number(self) -> str:
        """Generate unique ECN number."""
        self._counter += 1
        return f"ECN-{datetime.utcnow().strftime('%Y%m')}-{self._counter:04d}"
    
    async def create(self, title: str, description: str, 
                     affected_parts: List[str], changes: List[Dict]) -> ECNRecord:
        """Create and store a new ECN."""
        ecn = ECNRecord(
            ecn_number=self._generate_number(),
            title=title,
            description=description,
            affected_parts=affected_parts,
            changes=changes
        )
        
        # Store in memory brain if available
        if self.memory:
            await self.memory.store(
                key=f"ecn:{ecn.ecn_number}",
                content=f"ECN {ecn.ecn_number}: {title}. Parts: {', '.join(affected_parts)}",
                metadata=asdict(ecn)
            )
            
        logger.info(f"📝 Created: {ecn.ecn_number}")
        return ecn
    
    async def get_part_history(self, part_number: str) -> List[ECNRecord]:
        """Get all ECNs affecting a part (cumulative history)."""
        if not self.memory:
            return []
            
        results = await self.memory.search(
            query=f"ECN affecting part {part_number}",
            filter={"affected_parts": part_number}
        )
        
        return [
            ECNRecord(**r.metadata) 
            for r in results 
            if part_number in r.metadata.get("affected_parts", [])
        ]
    
    async def apply(self, ecn_number: str) -> Dict:
        """Mark ECN as implemented."""
        if self.memory:
            ecn_data = await self.memory.get(f"ecn:{ecn_number}")
            if ecn_data:
                ecn_data["status"] = "implemented"
                await self.memory.store(f"ecn:{ecn_number}", ecn_data)
                
        logger.info(f"✅ Applied: {ecn_number}")
        return {"ecn": ecn_number, "status": "implemented"}
