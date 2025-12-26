"""
ACHE Design Assistant - Agent Module
Phase 24 - Air Cooled Heat Exchanger Design Automation

This module provides the agent-side ACHE design assistant:
- ACHE-specific property extraction
- Engineering calculations
- Structural design tools
- Accessory design (walkways, ladders, handrails)
- AI-powered design assistance
- Field erection support
"""

from .extractor import ACHEExtractor, ACHEProperties
from .calculator import ACHECalculator, ThermalResults, PressureDropResults
from .structural import StructuralDesigner, ColumnDesign, BeamDesign
from .accessories import AccessoryDesigner, PlatformDesign, LadderDesign, HandrailDesign
from .ai_assistant import ACHEAssistant
from .erection import ErectionPlanner, LiftingLugDesign, RiggingPlan

__all__ = [
    # Extraction
    "ACHEExtractor",
    "ACHEProperties",
    # Calculations
    "ACHECalculator",
    "ThermalResults",
    "PressureDropResults",
    # Structural
    "StructuralDesigner",
    "ColumnDesign",
    "BeamDesign",
    # Accessories
    "AccessoryDesigner",
    "PlatformDesign",
    "LadderDesign",
    "HandrailDesign",
    # AI
    "ACHEAssistant",
    # Erection
    "ErectionPlanner",
    "LiftingLugDesign",
    "RiggingPlan",
]
