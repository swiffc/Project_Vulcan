"""
ACHE Design Assistant - Desktop Server Module
Phase 24 - Air Cooled Heat Exchanger Design Automation

This module provides:
- SolidWorks event listeners for model detection
- ACHE model property extraction
- Real-time model analysis
"""

from .event_listener import ACHEEventListener, ModelOpenEvent
from .detector import ACHEModelDetector
from .property_reader import ACHEPropertyReader

__all__ = [
    "ACHEEventListener",
    "ModelOpenEvent",
    "ACHEModelDetector",
    "ACHEPropertyReader",
]
