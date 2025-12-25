"""
Desktop Server Analyzers
========================
Analyze SolidWorks models for DFM, bend radius, manufacturability, etc.
"""

from .bend_radius_analyzer import BendRadiusAnalyzer

__all__ = ["BendRadiusAnalyzer"]
