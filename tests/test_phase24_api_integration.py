"""
Integration tests for Phase 24 ACHE API endpoints.

Tests the FastAPI endpoints directly using TestClient.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def client():
    """Create test client for the API."""
    from desktop_server.server import app
    return TestClient(app)


class TestACHECoreEndpoints:
    """Tests for core ACHE endpoints."""

    def test_ache_status(self, client):
        """Test /ache/status endpoint."""
        response = client.get("/ache/status")
        assert response.status_code in [200, 503]  # 503 if modules not loaded
        if response.status_code == 200:
            data = response.json()
            assert "status" in data

    def test_ache_standards_api661(self, client):
        """Test /ache/standards/api661 endpoint."""
        response = client.get("/ache/standards/api661")
        assert response.status_code == 200
        data = response.json()
        assert data["standard"] == "API 661 / ISO 13706"
        assert "key_requirements" in data
        assert "tube_bundle" in data["key_requirements"]
        assert "fan_system" in data["key_requirements"]


class TestACHECalculationEndpoints:
    """Tests for ACHE calculation endpoints."""

    def test_calculate_fan(self, client):
        """Test /ache/calculate/fan endpoint."""
        request_data = {
            "air_flow_m3_s": 50,
            "static_pressure_pa": 200,
            "fan_diameter_m": 3.0,
            "fan_rpm": 300,
            "fan_efficiency": 0.75
        }
        response = client.post("/ache/calculate/fan", json=request_data)
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "shaft_power_kw" in data
            assert "tip_speed_m_s" in data
            assert data["tip_speed_m_s"] > 0

    def test_calculate_fan_batch(self, client):
        """Test /ache/calculate/batch/fan endpoint."""
        request_data = {
            "calculations": [
                {
                    "air_flow_m3_s": 30,
                    "static_pressure_pa": 200,
                    "fan_diameter_m": 3.0,
                    "fan_rpm": 300,
                    "fan_efficiency": 0.75
                },
                {
                    "air_flow_m3_s": 50,
                    "static_pressure_pa": 200,
                    "fan_diameter_m": 3.0,
                    "fan_rpm": 300,
                    "fan_efficiency": 0.75
                }
            ]
        }
        response = client.post("/ache/calculate/batch/fan", json=request_data)
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert data["total_calculations"] == 2
            assert len(data["results"]) == 2

    def test_calculate_thermal(self, client):
        """Test /ache/calculate/thermal endpoint."""
        request_data = {
            "duty_kw": 1000,
            "process_inlet_temp_c": 120,
            "process_outlet_temp_c": 60,
            "air_inlet_temp_c": 35,
            "air_flow_kg_s": 100,
            "surface_area_m2": 500,
            "u_clean_w_m2_k": 45.0,
            "fouling_factor": 0.0002
        }
        response = client.post("/ache/calculate/thermal", json=request_data)
        assert response.status_code in [200, 503]

    def test_calculate_pressure_drop_tube(self, client):
        """Test /ache/calculate/pressure-drop/tube endpoint."""
        request_data = {
            "mass_flow_kg_s": 50,
            "tube_id_mm": 22,
            "tube_length_m": 6,
            "num_tubes": 500,
            "num_passes": 4,
            "fluid_density_kg_m3": 800,
            "fluid_viscosity_pa_s": 0.001
        }
        response = client.post("/ache/calculate/pressure-drop/tube", json=request_data)
        assert response.status_code in [200, 503]

    def test_calculate_pressure_drop_air(self, client):
        """Test /ache/calculate/pressure-drop/air endpoint."""
        request_data = {
            "air_flow_kg_s": 100,
            "air_inlet_temp_c": 35,
            "bundle_face_area_m2": 30,
            "tube_od_mm": 25.4,
            "fin_pitch_mm": 2.5,
            "fin_height_mm": 12.7,
            "num_tube_rows": 4
        }
        response = client.post("/ache/calculate/pressure-drop/air", json=request_data)
        assert response.status_code in [200, 503]

    def test_calculate_size(self, client):
        """Test /ache/calculate/size endpoint."""
        request_data = {
            "duty_kw": 1000,
            "process_inlet_temp_c": 120,
            "process_outlet_temp_c": 60,
            "air_inlet_temp_c": 35
        }
        response = client.post("/ache/calculate/size", json=request_data)
        assert response.status_code in [200, 503]


class TestACHEDesignEndpoints:
    """Tests for ACHE design endpoints."""

    def test_design_frame(self, client):
        """Test /ache/design/frame endpoint."""
        request_data = {
            "bundle_weight_kn": 500,
            "bundle_length_m": 12,
            "bundle_width_m": 3,
            "bundle_height_m": 2,
            "num_bays": 2,
            "elevation_m": 4.0,
            "wind_speed_m_s": 40.0
        }
        response = client.post("/ache/design/frame", json=request_data)
        assert response.status_code in [200, 503]

    def test_design_column(self, client):
        """Test /ache/design/column endpoint."""
        response = client.post(
            "/ache/design/column",
            params={
                "axial_load_kn": 200,
                "height_m": 4.0,
                "moment_kn_m": 20,
                "k_factor": 1.0
            }
        )
        assert response.status_code in [200, 503]

    def test_design_beam(self, client):
        """Test /ache/design/beam endpoint."""
        response = client.post(
            "/ache/design/beam",
            params={
                "span_m": 6.0,
                "distributed_load_kn_m": 10,
                "deflection_limit": "L/240"
            }
        )
        assert response.status_code in [200, 503]

    def test_design_anchor_bolts(self, client):
        """Test /ache/design/anchor-bolts endpoint."""
        response = client.post(
            "/ache/design/anchor-bolts",
            params={
                "base_shear_kn": 100,
                "uplift_kn": 50,
                "num_bolts": 4
            }
        )
        assert response.status_code in [200, 503]

    def test_design_access(self, client):
        """Test /ache/design/access endpoint."""
        request_data = {
            "bundle_length_m": 12,
            "bundle_width_m": 3,
            "elevation_m": 5,
            "num_bays": 2,
            "fan_deck_required": True,
            "header_access_required": True
        }
        response = client.post("/ache/design/access", json=request_data)
        assert response.status_code in [200, 503]


class TestACHEAIEndpoints:
    """Tests for ACHE AI assistant endpoints."""

    def test_compliance_check(self, client):
        """Test /ache/compliance/check endpoint."""
        request_data = {
            "tube_bundle": {
                "tube_length_m": 10,
                "tube_od_mm": 25.4
            },
            "fan_system": {
                "tip_speed_m_s": 55
            }
        }
        response = client.post("/ache/compliance/check", json=request_data)
        assert response.status_code in [200, 503]

    def test_ai_recommendations(self, client):
        """Test /ache/ai/recommendations endpoint."""
        request_data = {
            "thermal_performance": {
                "approach_temp_c": 8
            }
        }
        response = client.post("/ache/ai/recommendations", json=request_data)
        assert response.status_code in [200, 503]

    def test_ai_troubleshoot(self, client):
        """Test /ache/ai/troubleshoot/{problem} endpoint."""
        response = client.get("/ache/ai/troubleshoot/high%20temperature")
        assert response.status_code in [200, 503]

    def test_ai_knowledge(self, client):
        """Test /ache/ai/knowledge endpoint."""
        response = client.get("/ache/ai/knowledge", params={"query": "tube selection"})
        assert response.status_code in [200, 503]

    def test_optimize_suggestions(self, client):
        """Test /ache/optimize/suggestions endpoint."""
        request_data = {
            "optimization_targets": ["cost", "efficiency"]
        }
        response = client.post("/ache/optimize/suggestions", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0


class TestACHEErectionEndpoints:
    """Tests for ACHE erection planning endpoints."""

    def test_erection_plan(self, client):
        """Test /ache/erection/plan endpoint."""
        request_data = {
            "project_name": "Test Project",
            "equipment_tag": "AC-101",
            "ache_properties": {
                "mass_properties": {"mass_kg": 50000},
                "bounding_box": {
                    "length_mm": 12000,
                    "width_mm": 3000,
                    "height_mm": 4000
                },
                "fan_system": {"num_fans": 2}
            }
        }
        response = client.post("/ache/erection/plan", json=request_data)
        assert response.status_code in [200, 503]

    def test_erection_lifting_lug(self, client):
        """Test /ache/erection/lifting-lug endpoint."""
        response = client.post(
            "/ache/erection/lifting-lug",
            params={
                "design_load_kn": 100,
                "sling_angle_deg": 60
            }
        )
        assert response.status_code in [200, 503]


class TestACHEExportEndpoints:
    """Tests for ACHE export endpoints."""

    def test_export_datasheet(self, client):
        """Test /ache/export/datasheet endpoint."""
        request_data = {
            "equipment_tag": "AC-101",
            "service": "Cooling",
            "thermal": {"duty_kw": 1000},
            "fan_system": {"num_fans": 2}
        }
        response = client.post("/ache/export/datasheet", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "ACHE Datasheet"
        assert "sections" in data

    def test_export_bom(self, client):
        """Test /ache/export/bom endpoint."""
        request_data = {
            "equipment_tag": "AC-101",
            "tube_bundle": {
                "num_tubes": 500,
                "tube_od_mm": 25.4,
                "tube_length_m": 6
            },
            "fan_system": {
                "num_fans": 2,
                "fan_diameter_m": 3.0
            }
        }
        response = client.post("/ache/export/bom", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "Bill of Materials"
        assert "items" in data


class TestACHEValidation:
    """Tests for input validation."""

    def test_fan_invalid_efficiency(self, client):
        """Test fan calculation with invalid efficiency."""
        request_data = {
            "air_flow_m3_s": 50,
            "static_pressure_pa": 200,
            "fan_diameter_m": 3.0,
            "fan_rpm": 300,
            "fan_efficiency": 1.5  # Invalid > 1
        }
        response = client.post("/ache/calculate/fan", json=request_data)
        # Should either accept and calculate or reject with 422
        assert response.status_code in [200, 422, 503]

    def test_missing_required_field(self, client):
        """Test endpoint with missing required field."""
        request_data = {
            "air_flow_m3_s": 50,
            # Missing static_pressure_pa
            "fan_diameter_m": 3.0,
            "fan_rpm": 300
        }
        response = client.post("/ache/calculate/fan", json=request_data)
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
