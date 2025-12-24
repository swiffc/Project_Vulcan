"""
Strategies Module - Digital Twin and Learning System

This module contains:
- Product models (Digital Twins)
- Strategy schemas
- Template management
"""

from .schema import PartStrategy, Feature, Extrude, Revolve
from .product_models import (
    ProductType,
    FeatureType,
    MaterialSpec,
    Dimension,
    Constraint,
    Feature as ProductFeature,
    SuccessMetrics,
    BaseProduct,
    WeldmentStrategy,
    SheetMetalStrategy,
    MachiningStrategy,
    AssemblyStrategy,
    SolidStrategy,
    create_strategy,
)

__all__ = [
    # Legacy schema
    "PartStrategy",
    "Feature",
    "Extrude",
    "Revolve",
    # New product models
    "ProductType",
    "FeatureType",
    "MaterialSpec",
    "Dimension",
    "Constraint",
    "ProductFeature",
    "SuccessMetrics",
    "BaseProduct",
    "WeldmentStrategy",
    "SheetMetalStrategy",
    "MachiningStrategy",
    "AssemblyStrategy",
    "SolidStrategy",
    "create_strategy",
]
