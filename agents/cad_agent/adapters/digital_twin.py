"""
Digital Twin Adapter
Lightweight in-memory representation of CAD parts.

Implements Rule: Section 6 - The Shadow Copy pattern.
AI calculates on this "Twin" instantly, only opens SolidWorks when building.

Packages Used: None (pure Python)
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger("cad_agent.digital-twin")


@dataclass
class Feature:
    """A feature in the digital twin."""
    id: str
    type: str  # sketch, extrude, revolve, fillet, etc.
    params: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    suppressed: bool = False


@dataclass 
class Sketch:
    """A sketch with geometry."""
    id: str
    plane: str  # Front, Top, Right, or feature face
    entities: List[Dict] = field(default_factory=list)  # circles, lines, arcs
    constraints: List[Dict] = field(default_factory=list)
    dimensions: List[Dict] = field(default_factory=list)


@dataclass
class DigitalTwin:
    """Digital twin of a CAD part."""
    part_number: str
    name: str
    material: str = "Steel"
    units: str = "mm"
    features: List[Feature] = field(default_factory=list)
    sketches: Dict[str, Sketch] = field(default_factory=dict)
    mass_kg: float = 0.0
    bounding_box: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_sketch(self, sketch_id: str, plane: str) -> Sketch:
        """Add a new sketch to the twin."""
        sketch = Sketch(id=sketch_id, plane=plane)
        self.sketches[sketch_id] = sketch
        return sketch
        
    def add_feature(self, feature_type: str, params: Dict, 
                    parent_id: str = None) -> Feature:
        """Add a feature to the twin."""
        feature_id = f"{feature_type}_{len(self.features)+1}"
        feature = Feature(
            id=feature_id,
            type=feature_type,
            params=params,
            parent_id=parent_id
        )
        self.features.append(feature)
        self._recalculate()
        return feature
        
    def _recalculate(self):
        """Recalculate mass and bounding box (simplified)."""
        # This is a simplified estimation
        # Real calculation would need geometry engine
        volume = 0.0
        
        for feature in self.features:
            if feature.suppressed:
                continue
            if feature.type == "extrude":
                # Estimate volume from extrude
                depth = feature.params.get("depth", 0)
                # Would need sketch area - using placeholder
                area = feature.params.get("area", 100)  # mm²
                volume += area * depth
                
        # Convert to kg (assuming steel: 7850 kg/m³)
        densities = {
            "Steel": 7850,
            "Aluminum": 2700,
            "Plastic": 1200,
        }
        density = densities.get(self.material, 7850)
        self.mass_kg = (volume / 1e9) * density  # mm³ to m³
        
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "part_number": self.part_number,
            "name": self.name,
            "material": self.material,
            "units": self.units,
            "features": [asdict(f) for f in self.features],
            "sketches": {k: asdict(v) for k, v in self.sketches.items()},
            "mass_kg": self.mass_kg,
            "bounding_box": self.bounding_box,
            "metadata": self.metadata
        }
        
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
        
    @classmethod
    def from_dict(cls, data: Dict) -> "DigitalTwin":
        """Create from dictionary."""
        twin = cls(
            part_number=data["part_number"],
            name=data["name"],
            material=data.get("material", "Steel"),
            units=data.get("units", "mm")
        )
        twin.mass_kg = data.get("mass_kg", 0)
        twin.bounding_box = data.get("bounding_box", {})
        twin.metadata = data.get("metadata", {})
        
        for f_data in data.get("features", []):
            twin.features.append(Feature(**f_data))
            
        for s_id, s_data in data.get("sketches", {}).items():
            twin.sketches[s_id] = Sketch(**s_data)
            
        return twin


class DigitalTwinAdapter:
    """
    Manages digital twins for instant AI calculations.
    
    Usage:
        adapter = DigitalTwinAdapter()
        twin = adapter.create("PN-001", "Flange")
        twin.add_feature("extrude", {"depth": 10, "area": 500})
        
        # Instant calculation without opening CAD
        print(f"Estimated mass: {twin.mass_kg} kg")
        
        # When ready to build, export to CAD
        cad_commands = adapter.to_cad_commands(twin)
    """
    
    def __init__(self, storage_dir: str = "storage/twins"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.twins: Dict[str, DigitalTwin] = {}
        
    def create(self, part_number: str, name: str, **kwargs) -> DigitalTwin:
        """Create a new digital twin."""
        twin = DigitalTwin(part_number=part_number, name=name, **kwargs)
        self.twins[part_number] = twin
        logger.info(f"🔮 Created twin: {part_number}")
        return twin
        
    def get(self, part_number: str) -> Optional[DigitalTwin]:
        """Get a twin by part number."""
        return self.twins.get(part_number)
        
    def save(self, part_number: str) -> Path:
        """Save twin to file."""
        twin = self.twins.get(part_number)
        if not twin:
            raise ValueError(f"Twin not found: {part_number}")
            
        filepath = self.storage_dir / f"{part_number}.json"
        filepath.write_text(twin.to_json())
        logger.info(f"💾 Saved twin: {filepath}")
        return filepath
        
    def load(self, part_number: str) -> DigitalTwin:
        """Load twin from file."""
        filepath = self.storage_dir / f"{part_number}.json"
        if not filepath.exists():
            raise FileNotFoundError(f"Twin file not found: {filepath}")
            
        data = json.loads(filepath.read_text())
        twin = DigitalTwin.from_dict(data)
        self.twins[part_number] = twin
        return twin
        
    def to_cad_commands(self, twin: DigitalTwin) -> List[Dict]:
        """
        Convert twin to CAD execution commands.
        These commands are sent to desktop_server for actual building.
        """
        commands = [
            {"action": "new_part", "params": {"name": twin.name}}
        ]
        
        for sketch_id, sketch in twin.sketches.items():
            commands.append({
                "action": "create_sketch",
                "params": {"plane": sketch.plane}
            })
            for entity in sketch.entities:
                commands.append({
                    "action": f"draw_{entity['type']}",
                    "params": entity
                })
            commands.append({"action": "close_sketch", "params": {}})
            
        for feature in twin.features:
            if not feature.suppressed:
                commands.append({
                    "action": feature.type,
                    "params": feature.params
                })
                
        commands.append({
            "action": "save",
            "params": {"filename": f"{twin.part_number}.sldprt"}
        })
        
        return commands


# Singleton
_adapter: Optional[DigitalTwinAdapter] = None

def get_digital_twin_adapter() -> DigitalTwinAdapter:
    global _adapter
    if _adapter is None:
        _adapter = DigitalTwinAdapter()
    return _adapter
