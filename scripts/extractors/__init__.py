"""
Structured Data Extractors

Specialized extractors for different page types:
- Location Table Extractor
- Specification Table Extractor
- Design Rule Extractor
- Drawing Reference Extractor
"""

from .base_extractor import BaseExtractor
from .location_table_extractor import LocationTableExtractor
from .specification_table_extractor import SpecificationTableExtractor
from .design_rule_extractor import DesignRuleExtractor
from .drawing_reference_extractor import DrawingReferenceExtractor

__all__ = [
    'BaseExtractor',
    'LocationTableExtractor',
    'SpecificationTableExtractor',
    'DesignRuleExtractor',
    'DrawingReferenceExtractor',
]

