"""
Desktop Server Extractors
=========================
Extract data from SolidWorks models (properties, BOM, mates, holes, etc.)
"""

from .properties import PropertiesExtractor
from .holes import HolePatternExtractor

__all__ = ["PropertiesExtractor", "HolePatternExtractor"]
