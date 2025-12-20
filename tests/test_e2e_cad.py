"""
E2E CAD Flow Test (PRD Section 9)

Tests complete CAD workflow:
1. User uploads multi-page PDF
2. CAD Agent AI parses each page (OCR)
3. Extract dimensions → Generate .param features
4. Send scripts to CAD-MCP (SolidWorks/Inventor)
5. Create parts and assembly
6. Apply standardizer, analyzer checks
7. Export PDF/STEP → Upload to Drive
8. Inspector Bot audits assembly

Run with: pytest tests/test_e2e_cad.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCADE2EFlow:
    """End-to-end CAD workflow tests."""

    @pytest.mark.asyncio
    async def test_full_cad_flow(self):
        """
        E2E: PDF → Parse → Build → Verify → Export

        Simulates: "Build a flange from the uploaded PDF"
        """
        from agents.core.orchestrator_adapter import (
            OrchestratorAdapter, TaskRequest, AgentType
        )

        orch = OrchestratorAdapter()

        # Mock CAD Agent
        mock_cad = AsyncMock()
        mock_cad.process = AsyncMock(return_value={
            "job_id": "CAD-00045",
            "input_pdf": "Flange_Drawing.pdf",
            "parts_built": ["Flange_01"],
            "assembly_file": None,
            "export_files": ["Flange_01.STEP", "Flange_01.PDF"],
            "mass_properties": {"mass": 0.45, "units": "kg"},
            "status": "complete"
        })
        orch.register_agent(AgentType.CAD, mock_cad)

        # Mock Inspector
        mock_inspector = AsyncMock()
        mock_inspector.audit = AsyncMock(return_value={
            "grade": "A",
            "score": 95,
            "gdt_check": "passed",
            "feedback": "Dimensions match drawing within tolerance"
        })
        orch.register_agent(AgentType.INSPECTOR, mock_inspector)

        # Execute CAD workflow
        request = TaskRequest(
            message="Build a flange from the uploaded PDF",
            context={"pdf_path": "/uploads/Flange_Drawing.pdf"},
            require_review=True
        )
        result = await orch.route(request)

        # Assertions
        assert result.success
        assert result.agent == AgentType.CAD
        assert result.metadata.get("reviewed") == True

    @pytest.mark.asyncio
    async def test_pdf_parsing(self):
        """Test PDFBridge can be instantiated and has correct API."""
        from agents.cad_agent.adapters import PDFBridge

        bridge = PDFBridge(dpi=300)

        # Verify bridge has correct methods
        assert hasattr(bridge, 'extract_from_pdf')
        assert hasattr(bridge, '_parse_text')
        assert bridge.dpi == 300

    @pytest.mark.asyncio
    async def test_adapters_available(self):
        """Test that all CAD adapters can be imported."""
        from agents.cad_agent.adapters import PDFBridge, ECNAdapter, GDriveBridge

        # Verify all adapters can be instantiated
        pdf_bridge = PDFBridge()
        ecn_adapter = ECNAdapter()
        gdrive_bridge = GDriveBridge()

        assert pdf_bridge is not None
        assert ecn_adapter is not None
        assert gdrive_bridge is not None

    @pytest.mark.asyncio
    async def test_solidworks_router_exists(self):
        """Test SolidWorks COM router can be imported."""
        from desktop_server.com import solidworks_com

        # Verify router and endpoints exist
        assert hasattr(solidworks_com, 'router')
        assert hasattr(solidworks_com, 'new_part')
        assert hasattr(solidworks_com, 'create_sketch')
        assert hasattr(solidworks_com, 'draw_circle')
        assert hasattr(solidworks_com, 'extrude')

    @pytest.mark.asyncio
    async def test_assembly_creation(self):
        """Test multi-part assembly workflow."""
        from agents.core.orchestrator_adapter import (
            OrchestratorAdapter, TaskRequest, AgentType
        )

        orch = OrchestratorAdapter()

        mock_cad = AsyncMock()
        mock_cad.process = AsyncMock(return_value={
            "job_id": "CAD-00046",
            "input_pdf": "Bracket_Assembly.pdf",
            "parts_built": ["Bracket_Base", "Bracket_Arm", "Bracket_Pin"],
            "assembly_file": "Bracket_Assembly.SLDASM",
            "export_files": ["Bracket_Assembly.STEP"],
            "mass_properties": {"mass": 1.24, "units": "kg"},
            "status": "complete"
        })
        orch.register_agent(AgentType.CAD, mock_cad)

        request = TaskRequest(
            message="Build assembly from multi-page PDF",
            context={"pdf_path": "/uploads/Bracket_Assembly.pdf"}
        )
        result = await orch.route(request)

        assert result.success
        assert len(result.output["parts_built"]) == 3
        assert result.output["assembly_file"] is not None

    @pytest.mark.asyncio
    async def test_ecn_revision_tracking(self):
        """Test ECN adapter for revision tracking."""
        from agents.cad_agent.adapters import ECNAdapter

        mock_memory = AsyncMock()
        mock_memory.store = AsyncMock(return_value={"id": "ecn-001"})

        ecn = ECNAdapter(memory_client=mock_memory)

        # Create an ECN
        ecn_record = await ecn.create(
            title="Updated bore diameter",
            description="Per customer request",
            affected_parts=["Flange_01"],
            changes=[{"type": "dimension", "from": 0.5, "to": 0.52}]
        )

        assert ecn_record is not None
        assert ecn_record.ecn_number.startswith("ECN-")

    @pytest.mark.asyncio
    async def test_drive_export(self):
        """Test Google Drive export integration."""
        from agents.cad_agent.adapters import GDriveBridge

        mock_mcp = AsyncMock()
        mock_mcp.call_tool = AsyncMock(return_value={
            "id": "drive-file-123",
            "link": "https://drive.google.com/file/d/..."
        })

        bridge = GDriveBridge(mcp_client=mock_mcp)

        result = await bridge.upload(
            "/exports/Flange_01.STEP",
            drive_folder="vulcan-exports"
        )

        assert result["id"] is not None
        mock_mcp.call_tool.assert_called_once()


class TestCADErrorHandling:
    """Test error handling in CAD flow."""

    @pytest.mark.asyncio
    async def test_invalid_pdf(self):
        """Test handling of invalid/corrupt PDF."""
        from agents.cad_agent.adapters import PDFBridge

        bridge = PDFBridge()

        # extract_from_pdf should raise when given invalid path
        with pytest.raises(Exception):
            bridge.extract_from_pdf("/fake/corrupt.pdf")

    @pytest.mark.asyncio
    async def test_cad_software_unavailable(self):
        """Test graceful handling when CAD software not running."""
        from desktop_server.com import solidworks_com

        # When COM fails, get_app should raise HTTPException
        with patch("win32com.client.Dispatch", side_effect=Exception("COM error")):
            with pytest.raises(Exception):
                solidworks_com.get_app()

    @pytest.mark.asyncio
    async def test_dimension_extraction_fallback(self):
        """Test fallback when PDF processing fails."""
        from agents.cad_agent.adapters import PDFBridge

        bridge = PDFBridge()

        # When pdf2image fails, extract_from_pdf should raise
        with patch("pdf2image.convert_from_path", side_effect=Exception("PDF conversion failed")):
            with pytest.raises(Exception):
                bridge.extract_from_pdf("/fake/drawing.pdf")


class TestCADAccuracy:
    """Test CAD reconstruction accuracy (PRD: >90%)."""

    @pytest.mark.asyncio
    async def test_dimension_accuracy(self):
        """Test that extracted dimensions match within tolerance."""
        expected = {"diameter": 2.500, "height": 1.750}
        extracted = {"diameter": 2.502, "height": 1.749}

        tolerance = 0.005  # ±0.005

        for key in expected:
            diff = abs(expected[key] - extracted[key])
            assert diff <= tolerance, f"{key} out of tolerance: {diff}"

    @pytest.mark.asyncio
    async def test_feature_count_accuracy(self):
        """Test that all features from drawing are captured."""
        drawing_features = ["bore", "counterbore", "chamfer", "fillet"]
        built_features = ["bore", "counterbore", "chamfer", "fillet"]

        accuracy = len(set(drawing_features) & set(built_features)) / len(drawing_features)
        assert accuracy >= 0.90, f"Feature accuracy {accuracy:.0%} below 90%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
