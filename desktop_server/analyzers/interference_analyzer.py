"""
Interference Analyzer
=====================
Detect and analyze interferences between components in assemblies.

Phase 24.10 Implementation
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("vulcan.analyzer.interference")


@dataclass
class InterferenceResult:
    """Information about a single interference."""
    component1_name: str = ""
    component2_name: str = ""
    volume_m3: float = 0.0
    volume_in3: float = 0.0
    is_coincident: bool = False
    location: tuple = (0.0, 0.0, 0.0)


@dataclass
class ClearanceResult:
    """Information about minimum clearance between components."""
    component1_name: str = ""
    component2_name: str = ""
    clearance_m: float = 0.0
    clearance_in: float = 0.0
    location1: tuple = (0.0, 0.0, 0.0)
    location2: tuple = (0.0, 0.0, 0.0)


@dataclass
class InterferenceAnalysisResult:
    """Complete interference analysis results."""
    total_interferences: int = 0
    total_coincident_faces: int = 0
    interferences: List[InterferenceResult] = field(default_factory=list)
    clearances: List[ClearanceResult] = field(default_factory=list)
    minimum_clearance_m: float = float("inf")
    analysis_time_sec: float = 0.0


class InterferenceAnalyzer:
    """
    Analyze assemblies for interferences and clearances.
    Uses SolidWorks Interference Detection API.
    """

    def __init__(self):
        self._sw_app = None
        self._doc = None

    def _connect(self) -> bool:
        """Connect to SolidWorks COM interface."""
        try:
            import win32com.client
            self._sw_app = win32com.client.GetActiveObject("SldWorks.Application")
            self._doc = self._sw_app.ActiveDoc
            return self._doc is not None and self._doc.GetType() == 2  # Assembly
        except Exception as e:
            logger.error(f"Failed to connect to SolidWorks: {e}")
            return False

    def run_interference_check(self) -> InterferenceAnalysisResult:
        """Run interference detection on the assembly."""
        import time
        start_time = time.time()
        result = InterferenceAnalysisResult()

        if not self._connect():
            logger.warning("Not connected to a SolidWorks assembly")
            return result

        try:
            # Get interference detection manager
            intf_mgr = self._doc.InterferenceDetectionManager

            if not intf_mgr:
                logger.warning("Interference detection not available")
                return result

            # Configure detection options
            intf_mgr.TreatCoincidenceAsInterference = True
            intf_mgr.TreatSubAssembliesAsComponents = True
            intf_mgr.IncludeMultibodyPartInterferences = True

            # Run detection
            interferences = intf_mgr.GetInterferences()

            if interferences:
                result.total_interferences = len(interferences)

                for intf in interferences:
                    try:
                        intf_result = InterferenceResult()

                        # Get components involved
                        comps = intf.Components
                        if comps and len(comps) >= 2:
                            intf_result.component1_name = comps[0].Name2
                            intf_result.component2_name = comps[1].Name2

                        # Get volume
                        intf_result.volume_m3 = intf.Volume
                        intf_result.volume_in3 = intf.Volume * 61023.7

                        # Check if coincident
                        intf_result.is_coincident = intf.IsCoincidentInterference
                        if intf_result.is_coincident:
                            result.total_coincident_faces += 1

                        result.interferences.append(intf_result)
                    except Exception as e:
                        logger.debug(f"Error processing interference: {e}")

        except Exception as e:
            logger.error(f"Interference check failed: {e}")

        result.analysis_time_sec = time.time() - start_time
        return result

    def check_clearances(self, min_clearance_m: float = 0.001) -> List[ClearanceResult]:
        """Check minimum clearances between components."""
        clearances = []

        if not self._connect():
            return clearances

        try:
            # Get all components
            components = self._doc.GetComponents(True)  # Top level only

            if not components or len(components) < 2:
                return clearances

            # Check clearance between each pair
            for i, comp1 in enumerate(components):
                for comp2 in components[i + 1:]:
                    try:
                        # Use minimum distance measure
                        result = self._doc.Extension.GetMinimumDistance(
                            comp1, comp2, None, None, None, None
                        )

                        if result and len(result) >= 1:
                            distance = result[0]
                            if distance < min_clearance_m:
                                clearances.append(ClearanceResult(
                                    component1_name=comp1.Name2,
                                    component2_name=comp2.Name2,
                                    clearance_m=distance,
                                    clearance_in=distance * 39.3701,
                                ))
                    except Exception:
                        pass

        except Exception as e:
            logger.error(f"Clearance check failed: {e}")

        return clearances

    def to_dict(self) -> Dict[str, Any]:
        """Run analysis and return results as dictionary."""
        result = self.run_interference_check()
        clearances = self.check_clearances()

        return {
            "total_interferences": result.total_interferences,
            "total_coincident_faces": result.total_coincident_faces,
            "analysis_time_sec": result.analysis_time_sec,
            "interferences": [
                {
                    "component1": i.component1_name,
                    "component2": i.component2_name,
                    "volume_m3": i.volume_m3,
                    "volume_in3": i.volume_in3,
                    "is_coincident": i.is_coincident,
                }
                for i in result.interferences
            ],
            "tight_clearances": [
                {
                    "component1": c.component1_name,
                    "component2": c.component2_name,
                    "clearance_m": c.clearance_m,
                    "clearance_in": c.clearance_in,
                }
                for c in clearances
            ],
        }
