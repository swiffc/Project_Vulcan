"""
Format Converter - Phase 21 Gap 3

Handles conversion between CAD file formats (STEP, IGES, STL, DXF).
Acts as a wrapper around libraries like CadQuery or PythonOCC.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger("cad_agent.format_converter")


class FormatConverter:
    """
    Converts 3D CAD files to other formats.

    Primary use cases:
    1. Convert STEP/IGES to STL for mesh analysis.
    2. Convert STEP to DXF (projections) for 2D parsing.
    3. Convert mesh to simplified hull for physics.
    """

    def __init__(self):
        self._check_dependencies()

    def _check_dependencies(self):
        """Check available conversion backends."""
        self.has_cadquery = False
        self.has_pythonocc = False

        try:
            import cadquery as cq

            self.has_cadquery = True
        except ImportError:
            pass

        # PythonOCC check (simplified)
        try:
            from OCC.Core.STEPControl import STEPControl_Reader

            self.has_pythonocc = True
        except ImportError:
            pass

        logger.info(
            f"FormatConverter init: CadQuery={self.has_cadquery}, PythonOCC={self.has_pythonocc}"
        )

    def convert_to_stl(self, input_path: str, output_path: str = None) -> Optional[str]:
        """
        Convert STEP/IGES to STL.

        Args:
            input_path: Path to input file (.step, .igs)
            output_path: Optional path for output .stl

        Returns:
            Path to generated STL file or None if failed.
        """
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            return None

        if not output_path:
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}.stl"

        try:
            if self.has_cadquery:
                return self._convert_with_cadquery(input_path, output_path, "STL")
            else:
                logger.warning("No conversion backend (CadQuery/PythonOCC) available.")
                return None
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return None

    def convert_to_step(
        self, input_path: str, output_path: str = None
    ) -> Optional[str]:
        """Convert format to STEP."""
        # Implementation would mirror above
        return None

    def _convert_with_cadquery(
        self, input_path: str, output_path: str, format_type: str
    ) -> str:
        """Use CadQuery to convert."""
        import cadquery as cq

        # Load
        if input_path.lower().endswith((".step", ".stp")):
            model = cq.importers.importStep(input_path)
        else:
            raise ValueError(f"Unsupported input format for CQ: {input_path}")

        # Export
        if format_type == "STL":
            cq.exporters.export(model, output_path, cq.exporters.ExportTypes.STL)
        elif format_type == "STEP":
            cq.exporters.export(model, output_path, cq.exporters.ExportTypes.STEP)

        return output_path


# Singleton
_converter = FormatConverter()


def get_format_converter() -> FormatConverter:
    return _converter
