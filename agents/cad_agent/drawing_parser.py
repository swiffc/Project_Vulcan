"""
Drawing Parser Adapter
======================
Advanced parser for engineering drawings (PDF/DWG/DXF).

Features:
- Extracts dimensions and tolerances from PDF drawings
- Parses DXF/DWG files for geometric entities
- Identifies title block metadata (part number, revision, date)
- Validates notes against specifications
- Extracts BOM tables from drawings
- Compares drawing dimensions to 3D model
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

logger = logging.getLogger("vulcan.cad.drawing_parser")


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class DrawingMetadata:
    """Title block information extracted from drawing."""
    part_number: str = ""
    revision: str = ""
    title: str = ""
    author: Optional[str] = None
    date: Optional[str] = None
    material: Optional[str] = None
    finish: Optional[str] = None
    scale: Optional[str] = None
    sheet: Optional[str] = None
    project: Optional[str] = None


@dataclass
class Dimension:
    """A single dimension extracted from drawing."""
    value: float
    unit: str = "in"
    tolerance_upper: float = 0.0
    tolerance_lower: float = 0.0
    type: str = "linear"  # linear, angular, radial, diameter
    text: str = ""
    location: Optional[Tuple[float, float]] = None


@dataclass
class Note:
    """A note or annotation from the drawing."""
    number: int
    text: str
    category: str = "general"  # general, material, welding, finish, gdt


@dataclass
class BOMItem:
    """Bill of Materials line item."""
    item_no: int
    part_number: str
    description: str
    qty: int
    material: Optional[str] = None


@dataclass
class DrawingData:
    """Complete parsed drawing data."""
    file_path: str
    format: str
    metadata: DrawingMetadata = field(default_factory=DrawingMetadata)
    dimensions: List[Dimension] = field(default_factory=list)
    notes: List[Note] = field(default_factory=list)
    bom: List[BOMItem] = field(default_factory=list)
    layers: List[str] = field(default_factory=list)
    raw_text: str = ""
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "format": self.format,
            "metadata": {
                "part_number": self.metadata.part_number,
                "revision": self.metadata.revision,
                "title": self.metadata.title,
                "author": self.metadata.author,
                "date": self.metadata.date,
                "material": self.metadata.material,
                "scale": self.metadata.scale,
            },
            "dimensions": [
                {"value": d.value, "unit": d.unit, "type": d.type, "text": d.text}
                for d in self.dimensions
            ],
            "notes": [{"number": n.number, "text": n.text, "category": n.category} for n in self.notes],
            "bom": [
                {"item": b.item_no, "pn": b.part_number, "desc": b.description, "qty": b.qty}
                for b in self.bom
            ],
            "layers": self.layers,
            "errors": self.errors,
        }


# =============================================================================
# Regex Patterns for Extraction
# =============================================================================

# Dimension patterns (imperial and metric)
DIMENSION_PATTERNS = [
    # Standard decimal: 12.500, .250, 0.125
    r"(\d*\.?\d+)\s*(?:±\s*(\d*\.?\d+))?",
    # Fractional: 1/2, 3/4, 1-1/2
    r"(\d+)?-?(\d+)/(\d+)",
    # With tolerance: 12.500 +.005/-.003
    r"(\d*\.?\d+)\s*\+\s*(\d*\.?\d+)\s*/\s*-\s*(\d*\.?\d+)",
    # Diameter symbol: Ø1.500
    r"[ØⲴ∅]\s*(\d*\.?\d+)",
    # Angular: 45°, 90.5°
    r"(\d*\.?\d+)\s*[°º]",
]

# Title block patterns
TITLE_BLOCK_PATTERNS = {
    "part_number": [
        r"(?:PART\s*(?:NO|NUMBER|#)?|P/?N|ITEM\s*NO)[:\s]*([A-Z0-9][-A-Z0-9_.]+)",
        r"(?:DWG\s*(?:NO|NUMBER)?|DRAWING)[:\s]*([A-Z0-9][-A-Z0-9_.]+)",
    ],
    "revision": [
        r"(?:REV(?:ISION)?|ECN)[:\s]*([A-Z0-9]+)",
    ],
    "material": [
        r"(?:MATERIAL|MAT'?L?|MATL)[:\s]*([A-Z0-9][-A-Z0-9\s,./]+)",
        r"(?:SA|ASTM|AISI|UNS)[-\s]?(\d+[-A-Z0-9]*)",
    ],
    "date": [
        r"(?:DATE|DATED?)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
    ],
    "scale": [
        r"(?:SCALE)[:\s]*([\d]+\s*[:/]\s*[\d]+|FULL|NTS|NONE)",
    ],
}

# Note patterns
NOTE_PATTERN = r"(?:NOTE|N)[:\s]*(\d+)[:\.\s]*(.+?)(?=(?:NOTE|N)[:\s]*\d+|$)"

# BOM patterns
BOM_PATTERNS = [
    r"(\d+)\s+([A-Z0-9][-A-Z0-9_.]+)\s+(.+?)\s+(\d+)",
]


# =============================================================================
# Drawing Parser Class
# =============================================================================


class DrawingParser:
    """
    Parses engineering drawings (PDF/DXF) to extract validation data.

    Supports:
    - PDF drawings (via pypdf)
    - DXF files (via ezdxf)
    - DWG files (requires conversion to DXF first)
    """

    def __init__(self):
        self.supported_formats = [".pdf", ".dwg", ".dxf"]
        self._pypdf_available = self._check_pypdf()
        self._ezdxf_available = self._check_ezdxf()

    def _check_pypdf(self) -> bool:
        """Check if pypdf is available."""
        try:
            import pypdf
            return True
        except ImportError:
            logger.warning("pypdf not installed. PDF parsing disabled. Install with: pip install pypdf")
            return False

    def _check_ezdxf(self) -> bool:
        """Check if ezdxf is available."""
        try:
            import ezdxf
            return True
        except ImportError:
            logger.warning("ezdxf not installed. DXF parsing disabled. Install with: pip install ezdxf")
            return False

    def parse_file(self, file_path: str) -> DrawingData:
        """
        Main entry point to parse a drawing file.

        Args:
            file_path: Path to drawing file (PDF, DXF, or DWG)

        Returns:
            DrawingData object with extracted content
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Drawing not found: {file_path}")

        ext = path.suffix.lower()

        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext == ".dxf":
            return self._parse_dxf(file_path)
        elif ext == ".dwg":
            return self._parse_dwg(file_path)
        else:
            raise ValueError(f"Unsupported format: {ext}. Supported: {self.supported_formats}")

    # =========================================================================
    # PDF Parsing
    # =========================================================================

    def _parse_pdf(self, path: str) -> DrawingData:
        """Extract text and data from PDF drawing."""
        logger.info(f"Parsing PDF drawing: {path}")

        data = DrawingData(file_path=path, format="pdf")

        if not self._pypdf_available:
            data.errors.append("pypdf not installed - cannot parse PDF")
            return data

        try:
            import pypdf

            with open(path, "rb") as f:
                reader = pypdf.PdfReader(f)

                # Extract text from all pages
                all_text = []
                for page in reader.pages:
                    text = page.extract_text() or ""
                    all_text.append(text)

                data.raw_text = "\n".join(all_text)

                # Extract metadata from PDF properties
                if reader.metadata:
                    data.metadata.title = reader.metadata.get("/Title", "") or ""
                    data.metadata.author = reader.metadata.get("/Author", "") or ""

                # Parse the extracted text
                self._extract_title_block(data)
                self._extract_dimensions(data)
                self._extract_notes(data)
                self._extract_bom(data)

                logger.info(f"PDF parsed: {len(data.dimensions)} dimensions, {len(data.notes)} notes")

        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            data.errors.append(f"PDF parse error: {str(e)}")

        return data

    # =========================================================================
    # DXF Parsing
    # =========================================================================

    def _parse_dxf(self, path: str) -> DrawingData:
        """Extract entities from DXF file."""
        logger.info(f"Parsing DXF drawing: {path}")

        data = DrawingData(file_path=path, format="dxf")

        if not self._ezdxf_available:
            data.errors.append("ezdxf not installed - cannot parse DXF")
            return data

        try:
            import ezdxf

            doc = ezdxf.readfile(path)
            msp = doc.modelspace()

            # Get all layers
            data.layers = [layer.dxf.name for layer in doc.layers]

            # Extract dimensions
            for entity in msp.query("DIMENSION"):
                try:
                    dim = Dimension(
                        value=entity.dxf.actual_measurement if hasattr(entity.dxf, 'actual_measurement') else 0,
                        text=entity.dxf.text if hasattr(entity.dxf, 'text') else "",
                        type=self._get_dimension_type(entity),
                    )
                    data.dimensions.append(dim)
                except Exception as e:
                    logger.debug(f"Could not parse dimension: {e}")

            # Extract text entities for notes
            note_num = 1
            for entity in msp.query("TEXT MTEXT"):
                text = ""
                if entity.dxftype() == "TEXT":
                    text = entity.dxf.text
                elif entity.dxftype() == "MTEXT":
                    text = entity.text if hasattr(entity, 'text') else ""

                if text and len(text) > 10:  # Filter short labels
                    # Check if it's a note
                    if re.match(r"(?:NOTE|N)[:\s]*\d+", text, re.I):
                        match = re.search(NOTE_PATTERN, text, re.I | re.DOTALL)
                        if match:
                            data.notes.append(Note(
                                number=int(match.group(1)),
                                text=match.group(2).strip(),
                                category=self._categorize_note(match.group(2))
                            ))
                    else:
                        # Add as general note
                        data.notes.append(Note(
                            number=note_num,
                            text=text.strip(),
                            category=self._categorize_note(text)
                        ))
                        note_num += 1

            # Try to extract title block from block references
            for block_ref in msp.query("INSERT"):
                block_name = block_ref.dxf.name.upper()
                if "TITLE" in block_name or "BORDER" in block_name:
                    self._extract_title_from_block(doc, block_ref, data)

            logger.info(f"DXF parsed: {len(data.dimensions)} dimensions, {len(data.notes)} notes, {len(data.layers)} layers")

        except Exception as e:
            logger.error(f"Error parsing DXF: {e}")
            data.errors.append(f"DXF parse error: {str(e)}")

        return data

    def _parse_dwg(self, path: str) -> DrawingData:
        """Handle DWG files (requires conversion or ODA File Converter)."""
        logger.info(f"Parsing DWG drawing: {path}")

        data = DrawingData(file_path=path, format="dwg")
        data.errors.append(
            "DWG format requires conversion to DXF. "
            "Use ODA File Converter or save as DXF from CAD software."
        )

        # Check for DXF version
        dxf_path = Path(path).with_suffix(".dxf")
        if dxf_path.exists():
            logger.info(f"Found DXF version: {dxf_path}")
            return self._parse_dxf(str(dxf_path))

        return data

    # =========================================================================
    # Extraction Helpers
    # =========================================================================

    def _extract_title_block(self, data: DrawingData) -> None:
        """Extract title block metadata from raw text."""
        text = data.raw_text.upper()

        for field, patterns in TITLE_BLOCK_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    value = match.group(1).strip()
                    setattr(data.metadata, field, value)
                    break

    def _extract_dimensions(self, data: DrawingData) -> None:
        """Extract dimensions from raw text."""
        text = data.raw_text

        # Find all decimal dimensions
        for match in re.finditer(r"(\d+\.?\d*)\s*(?:±\s*(\d*\.?\d+))?", text):
            try:
                value = float(match.group(1))
                if 0.001 < value < 1000:  # Filter unreasonable values
                    dim = Dimension(
                        value=value,
                        tolerance_upper=float(match.group(2)) if match.group(2) else 0,
                        tolerance_lower=float(match.group(2)) if match.group(2) else 0,
                        text=match.group(0),
                    )
                    data.dimensions.append(dim)
            except ValueError:
                continue

        # Find diameter dimensions
        for match in re.finditer(r"[ØⲴ∅]\s*(\d*\.?\d+)", text):
            try:
                dim = Dimension(
                    value=float(match.group(1)),
                    type="diameter",
                    text=match.group(0),
                )
                data.dimensions.append(dim)
            except ValueError:
                continue

    def _extract_notes(self, data: DrawingData) -> None:
        """Extract notes from raw text."""
        text = data.raw_text

        # Find numbered notes
        for match in re.finditer(NOTE_PATTERN, text, re.I | re.DOTALL):
            note = Note(
                number=int(match.group(1)),
                text=match.group(2).strip(),
                category=self._categorize_note(match.group(2))
            )
            data.notes.append(note)

    def _extract_bom(self, data: DrawingData) -> None:
        """Extract Bill of Materials from raw text."""
        text = data.raw_text

        # Look for BOM table patterns
        for pattern in BOM_PATTERNS:
            for match in re.finditer(pattern, text):
                try:
                    item = BOMItem(
                        item_no=int(match.group(1)),
                        part_number=match.group(2),
                        description=match.group(3).strip(),
                        qty=int(match.group(4))
                    )
                    data.bom.append(item)
                except (ValueError, IndexError):
                    continue

    def _categorize_note(self, text: str) -> str:
        """Categorize a note based on content."""
        text_upper = text.upper()

        if any(kw in text_upper for kw in ["MATERIAL", "MATL", "SA-", "ASTM", "AISI"]):
            return "material"
        elif any(kw in text_upper for kw in ["WELD", "AWS", "FILLET", "GROOVE"]):
            return "welding"
        elif any(kw in text_upper for kw in ["FINISH", "PAINT", "COAT", "GALV"]):
            return "finish"
        elif any(kw in text_upper for kw in ["GD&T", "DATUM", "TOLERANCE", "POSITION"]):
            return "gdt"
        elif any(kw in text_upper for kw in ["HEAT TREAT", "HT", "HARDNESS"]):
            return "heat_treatment"
        else:
            return "general"

    def _get_dimension_type(self, entity) -> str:
        """Determine dimension type from DXF entity."""
        dim_type = getattr(entity.dxf, 'dimtype', 0) if hasattr(entity.dxf, 'dimtype') else 0

        type_map = {
            0: "linear",
            1: "aligned",
            2: "angular",
            3: "diameter",
            4: "radius",
            5: "angular3point",
            6: "ordinate",
        }
        return type_map.get(dim_type, "linear")

    def _extract_title_from_block(self, doc, block_ref, data: DrawingData) -> None:
        """Extract title block info from a block reference."""
        try:
            block = doc.blocks.get(block_ref.dxf.name)
            if block:
                for entity in block:
                    if entity.dxftype() in ["TEXT", "MTEXT", "ATTRIB"]:
                        text = ""
                        if entity.dxftype() == "ATTRIB":
                            text = entity.dxf.text
                            tag = entity.dxf.tag.upper()
                            if "PART" in tag or "DWG" in tag:
                                data.metadata.part_number = text
                            elif "REV" in tag:
                                data.metadata.revision = text
                            elif "DATE" in tag:
                                data.metadata.date = text
                            elif "TITLE" in tag:
                                data.metadata.title = text
                            elif "MATERIAL" in tag or "MATL" in tag:
                                data.metadata.material = text
        except Exception as e:
            logger.debug(f"Could not extract title block: {e}")

    # =========================================================================
    # Validation Methods
    # =========================================================================

    def validate_title_block(
        self,
        data: DrawingData,
        expected: Dict[str, str]
    ) -> List[str]:
        """
        Validate extracted metadata against expected values.

        Args:
            data: Parsed drawing data
            expected: Dictionary of expected values

        Returns:
            List of validation errors
        """
        errors = []

        if expected.get("part_number"):
            if data.metadata.part_number != expected["part_number"]:
                errors.append(
                    f"Part number mismatch: '{data.metadata.part_number}' != '{expected['part_number']}'"
                )

        if expected.get("revision"):
            if data.metadata.revision != expected["revision"]:
                errors.append(
                    f"Revision mismatch: '{data.metadata.revision}' != '{expected['revision']}'"
                )

        if expected.get("material"):
            if expected["material"].upper() not in (data.metadata.material or "").upper():
                errors.append(
                    f"Material mismatch: '{data.metadata.material}' != '{expected['material']}'"
                )

        return errors

    def validate_dimensions(
        self,
        data: DrawingData,
        model_dimensions: List[Dict[str, float]],
        tolerance: float = 0.001
    ) -> List[str]:
        """
        Compare drawing dimensions against 3D model dimensions.

        Args:
            data: Parsed drawing data
            model_dimensions: List of dimension dicts from 3D model
            tolerance: Comparison tolerance

        Returns:
            List of dimension mismatches
        """
        errors = []

        drawing_values = {d.value for d in data.dimensions}

        for model_dim in model_dimensions:
            value = model_dim.get("value", 0)
            name = model_dim.get("name", "Unknown")

            # Check if dimension exists in drawing
            found = any(abs(v - value) <= tolerance for v in drawing_values)
            if not found:
                errors.append(
                    f"Dimension '{name}' = {value} not found in drawing"
                )

        return errors

    def validate_notes(
        self,
        data: DrawingData,
        required_notes: List[str]
    ) -> List[str]:
        """
        Check that required notes are present.

        Args:
            data: Parsed drawing data
            required_notes: List of required note keywords

        Returns:
            List of missing notes
        """
        errors = []
        all_note_text = " ".join(n.text.upper() for n in data.notes)

        for required in required_notes:
            if required.upper() not in all_note_text:
                errors.append(f"Required note missing: '{required}'")

        return errors


# =============================================================================
# Factory Function
# =============================================================================


_parser: Optional[DrawingParser] = None


def get_drawing_parser() -> DrawingParser:
    """Get or create drawing parser singleton."""
    global _parser
    if _parser is None:
        _parser = DrawingParser()
    return _parser
