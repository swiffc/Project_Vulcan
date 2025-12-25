"""
Digital Twin Schema
Lightweight definitions of CAD strategies to allow AI to "think"
without opening SolidWorks.
"""

from typing import List, Literal
from pydantic import BaseModel, Field


class Feature(BaseModel):
    """Base feature definition."""

    name: str
    type: str


class Extrude(Feature):
    """Extrusion features."""

    type: Literal["extrude"] = "extrude"
    plane: str = "Front"
    sketch_shape: str = "circle"  # circle, rectangle, polygon
    dimension: float = Field(..., gt=0, description="Depth in mm")
    direction: str = "blind"


class Revolve(Feature):
    """Revolve features."""

    type: Literal["revolve"] = "revolve"
    axis: str
    angle: float = 360.0


class PartStrategy(BaseModel):
    """The Digital Twin of a SolidWorks Part."""

    name: str
    material: str = "AISI 304"
    features: List[Extrude | Revolve] = []

    def estimate_volume(self) -> float:
        """Estimate volume without opening CAD (Digital Twin calculation)."""
        vol = 0.0
        for f in self.features:
            if isinstance(f, Extrude):
                # Rough approximation for AI planning
                if f.sketch_shape == "circle":
                    # Assume simple cylinder for estimation
                    import math

                    # This logic would be expanded with actual sketch params
                    vol += math.pi * (10**2) * f.dimension
        return vol
