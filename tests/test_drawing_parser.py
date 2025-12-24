"""
Tests for Drawing Parser (Phase 21 - Gap 1)

Tests:
- PDF parsing
- DXF parsing
- Title block extraction
- Dimension extraction
- Note extraction
- BOM extraction
- Validation methods
"""

import pytest
from pathlib import Path
import tempfile
import os


class TestDrawingParserInitialization:
    """Tests for DrawingParser initialization."""

    def test_parser_initialization(self):
        """Test DrawingParser class initialization."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()
        assert parser is not None
        assert parser.supported_formats == [".pdf", ".dwg", ".dxf"]

    def test_parser_singleton(self):
        """Test drawing parser singleton pattern."""
        from agents.cad_agent.drawing_parser import get_drawing_parser

        parser1 = get_drawing_parser()
        parser2 = get_drawing_parser()
        assert parser1 is parser2

    def test_check_pypdf_availability(self):
        """Test pypdf availability check."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()
        # Should return True or False without error
        assert isinstance(parser._pypdf_available, bool)

    def test_check_ezdxf_availability(self):
        """Test ezdxf availability check."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()
        # Should return True or False without error
        assert isinstance(parser._ezdxf_available, bool)


class TestDrawingDataClasses:
    """Tests for drawing data classes."""

    def test_drawing_metadata_defaults(self):
        """Test DrawingMetadata default values."""
        from agents.cad_agent.drawing_parser import DrawingMetadata

        meta = DrawingMetadata()
        assert meta.part_number == ""
        assert meta.revision == ""
        assert meta.title == ""
        assert meta.author is None
        assert meta.material is None

    def test_dimension_creation(self):
        """Test Dimension dataclass."""
        from agents.cad_agent.drawing_parser import Dimension

        dim = Dimension(
            value=12.5,
            unit="in",
            tolerance_upper=0.005,
            tolerance_lower=0.005,
            type="linear"
        )
        assert dim.value == 12.5
        assert dim.unit == "in"
        assert dim.type == "linear"

    def test_note_creation(self):
        """Test Note dataclass."""
        from agents.cad_agent.drawing_parser import Note

        note = Note(
            number=1,
            text="ALL WELDS PER AWS D1.1",
            category="welding"
        )
        assert note.number == 1
        assert note.category == "welding"

    def test_bom_item_creation(self):
        """Test BOMItem dataclass."""
        from agents.cad_agent.drawing_parser import BOMItem

        item = BOMItem(
            item_no=1,
            part_number="ABC-123",
            description="Steel Plate",
            qty=2,
            material="SA-516-70"
        )
        assert item.item_no == 1
        assert item.part_number == "ABC-123"
        assert item.qty == 2

    def test_drawing_data_to_dict(self):
        """Test DrawingData.to_dict() method."""
        from agents.cad_agent.drawing_parser import DrawingData, DrawingMetadata

        data = DrawingData(
            file_path="/test/drawing.pdf",
            format="pdf",
            metadata=DrawingMetadata(part_number="TEST-001", revision="A")
        )

        result = data.to_dict()
        assert result["file_path"] == "/test/drawing.pdf"
        assert result["format"] == "pdf"
        assert result["metadata"]["part_number"] == "TEST-001"
        assert result["metadata"]["revision"] == "A"


class TestNoteCategorization:
    """Tests for note categorization logic."""

    def test_categorize_material_note(self):
        """Test material note categorization."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()

        assert parser._categorize_note("MATERIAL: SA-516-70") == "material"
        assert parser._categorize_note("MATL: ASTM A36") == "material"
        assert parser._categorize_note("USE AISI 304 STAINLESS") == "material"

    def test_categorize_welding_note(self):
        """Test welding note categorization."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()

        assert parser._categorize_note("ALL WELDS PER AWS D1.1") == "welding"
        assert parser._categorize_note("FILLET WELD 1/4 BOTH SIDES") == "welding"
        assert parser._categorize_note("GROOVE WELD CJP") == "welding"

    def test_categorize_finish_note(self):
        """Test finish note categorization."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()

        assert parser._categorize_note("FINISH: PAINT RED OXIDE") == "finish"
        assert parser._categorize_note("HOT DIP GALVANIZED COATING") == "finish"

    def test_categorize_gdt_note(self):
        """Test GD&T note categorization."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()

        assert parser._categorize_note("GD&T PER ASME Y14.5") == "gdt"
        assert parser._categorize_note("DATUM A IS PRIMARY") == "gdt"
        assert parser._categorize_note("TOLERANCE +/- 0.005") == "gdt"

    def test_categorize_general_note(self):
        """Test general note categorization."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()

        assert parser._categorize_note("DO NOT SCALE DRAWING") == "general"
        assert parser._categorize_note("REMOVE ALL BURRS") == "general"


class TestTitleBlockPatterns:
    """Tests for title block extraction patterns."""

    def test_part_number_pattern(self):
        """Test part number extraction."""
        import re
        from agents.cad_agent.drawing_parser import TITLE_BLOCK_PATTERNS

        patterns = TITLE_BLOCK_PATTERNS["part_number"]

        test_cases = [
            ("PART NO: ABC-123-456", "ABC-123-456"),
            ("P/N: TEST-001", "TEST-001"),
            ("DRAWING: DWG-12345", "DWG-12345"),
        ]

        for text, expected in test_cases:
            matched = False
            for pattern in patterns:
                match = re.search(pattern, text, re.I)
                if match and match.group(1) == expected:
                    matched = True
                    break
            assert matched, f"Failed to match {text!r} -> {expected!r}"

    def test_revision_pattern(self):
        """Test revision extraction."""
        import re
        from agents.cad_agent.drawing_parser import TITLE_BLOCK_PATTERNS

        patterns = TITLE_BLOCK_PATTERNS["revision"]

        text = "REV: A"
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                assert match.group(1) == "A"
                break

    def test_material_pattern(self):
        """Test material extraction."""
        import re
        from agents.cad_agent.drawing_parser import TITLE_BLOCK_PATTERNS

        patterns = TITLE_BLOCK_PATTERNS["material"]

        test_cases = [
            ("MATERIAL: SA-516-70", True),
            ("SA-516-70", True),  # Pattern matches SA-nnn format
            ("MATL: AISI 304", True),
        ]

        for text, should_match in test_cases:
            found = False
            for pattern in patterns:
                if re.search(pattern, text, re.I):
                    found = True
                    break
            assert found == should_match, f"Expected {text!r} to {'match' if should_match else 'not match'}"


class TestValidationMethods:
    """Tests for drawing validation methods."""

    def test_validate_title_block_pass(self):
        """Test title block validation - pass case."""
        from agents.cad_agent.drawing_parser import (
            DrawingParser, DrawingData, DrawingMetadata
        )

        parser = DrawingParser()

        data = DrawingData(
            file_path="/test.pdf",
            format="pdf",
            metadata=DrawingMetadata(
                part_number="ABC-123",
                revision="A",
                material="SA-516-70"
            )
        )

        expected = {
            "part_number": "ABC-123",
            "revision": "A",
            "material": "SA-516"
        }

        errors = parser.validate_title_block(data, expected)
        assert len(errors) == 0

    def test_validate_title_block_fail(self):
        """Test title block validation - fail case."""
        from agents.cad_agent.drawing_parser import (
            DrawingParser, DrawingData, DrawingMetadata
        )

        parser = DrawingParser()

        data = DrawingData(
            file_path="/test.pdf",
            format="pdf",
            metadata=DrawingMetadata(
                part_number="ABC-123",
                revision="A"
            )
        )

        expected = {
            "part_number": "XYZ-999",  # Mismatch
            "revision": "B",  # Mismatch
        }

        errors = parser.validate_title_block(data, expected)
        assert len(errors) == 2
        assert "Part number mismatch" in errors[0]

    def test_validate_notes_pass(self):
        """Test notes validation - pass case."""
        from agents.cad_agent.drawing_parser import (
            DrawingParser, DrawingData, Note
        )

        parser = DrawingParser()

        data = DrawingData(
            file_path="/test.pdf",
            format="pdf",
            notes=[
                Note(number=1, text="MATERIAL SA-516-70"),
                Note(number=2, text="ALL WELDS PER AWS D1.1"),
            ]
        )

        required = ["SA-516", "AWS"]
        errors = parser.validate_notes(data, required)
        assert len(errors) == 0

    def test_validate_notes_fail(self):
        """Test notes validation - fail case."""
        from agents.cad_agent.drawing_parser import (
            DrawingParser, DrawingData, Note
        )

        parser = DrawingParser()

        data = DrawingData(
            file_path="/test.pdf",
            format="pdf",
            notes=[
                Note(number=1, text="GENERAL NOTE"),
            ]
        )

        required = ["HEAT TREATMENT", "PWHT"]
        errors = parser.validate_notes(data, required)
        assert len(errors) == 2

    def test_validate_dimensions(self):
        """Test dimension validation against model."""
        from agents.cad_agent.drawing_parser import (
            DrawingParser, DrawingData, Dimension
        )

        parser = DrawingParser()

        data = DrawingData(
            file_path="/test.pdf",
            format="pdf",
            dimensions=[
                Dimension(value=12.5),
                Dimension(value=6.0),
                Dimension(value=3.25),
            ]
        )

        model_dims = [
            {"name": "Length", "value": 12.5},
            {"name": "Width", "value": 6.0},
            {"name": "Height", "value": 4.0},  # Not in drawing
        ]

        errors = parser.validate_dimensions(data, model_dims, tolerance=0.01)
        assert len(errors) == 1
        assert "Height" in errors[0]


class TestDimensionTypeMapping:
    """Tests for dimension type mapping."""

    def test_get_dimension_type_linear(self):
        """Test linear dimension type detection."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()

        # Create mock entity with dimtype=0
        class MockDxf:
            dimtype = 0

        class MockEntity:
            dxf = MockDxf()

        dim_type = parser._get_dimension_type(MockEntity())
        assert dim_type == "linear"

    def test_get_dimension_type_angular(self):
        """Test angular dimension type detection."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()

        class MockDxf:
            dimtype = 2

        class MockEntity:
            dxf = MockDxf()

        dim_type = parser._get_dimension_type(MockEntity())
        assert dim_type == "angular"


class TestFileNotFound:
    """Tests for file not found handling."""

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file raises error."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()

        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/file.pdf")

    def test_unsupported_format(self):
        """Test unsupported format raises error."""
        from agents.cad_agent.drawing_parser import DrawingParser

        parser = DrawingParser()

        # Create a temp file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as excinfo:
                parser.parse_file(temp_path)
            assert "Unsupported format" in str(excinfo.value)
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
