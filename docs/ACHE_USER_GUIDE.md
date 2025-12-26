# ACHE Design Assistant - User Guide

## Overview

The ACHE Design Assistant is a comprehensive tool for Air Cooled Heat Exchanger design per API 661 / ISO 13706. It provides automated calculations, structural design, compliance checking, and field erection support.

## Quick Start

### Starting the Server

```bash
cd desktop_server
python -m uvicorn server:app --host 0.0.0.0 --port 8000
```

### Base URL

```
http://localhost:8000/ache
```

---

## Core Features

### 1. Thermal Calculations

Calculate ACHE thermal performance using LMTD or NTU-effectiveness methods.

**Endpoint:** `POST /ache/calculate/thermal`

```json
{
  "duty_kw": 1000,
  "process_inlet_temp_c": 120,
  "process_outlet_temp_c": 60,
  "air_inlet_temp_c": 35,
  "air_flow_kg_s": 100,
  "surface_area_m2": 500,
  "u_clean_w_m2_k": 45.0,
  "fouling_factor": 0.0002
}
```

### 2. Fan Performance

Calculate fan power and tip speed per API 661.

**Endpoint:** `POST /ache/calculate/fan`

```json
{
  "air_flow_m3_s": 50,
  "static_pressure_pa": 200,
  "fan_diameter_m": 3.0,
  "fan_rpm": 300,
  "fan_efficiency": 0.75
}
```

**API 661 Limits:**
- Maximum tip speed: 61 m/s (200 ft/s)
- Noise level warning if > 90 dBA

### 3. Pressure Drop Calculations

#### Tube-Side
**Endpoint:** `POST /ache/calculate/pressure-drop/tube`

#### Air-Side
**Endpoint:** `POST /ache/calculate/pressure-drop/air`

API 661 typical limit: 250 Pa maximum

### 4. Preliminary Sizing

**Endpoint:** `POST /ache/calculate/size`

```json
{
  "duty_kw": 1000,
  "process_inlet_temp_c": 120,
  "process_outlet_temp_c": 60,
  "air_inlet_temp_c": 35
}
```

---

## Structural Design

### Frame Design

**Endpoint:** `POST /ache/design/frame`

Designs complete support structure per AISC including:
- Columns with slenderness check (KL/r ≤ 200)
- Beams with deflection limit (L/240)
- Load combinations (D+L, D+W, D+L+W, D+E)

### Individual Component Design

| Endpoint | Description |
|----------|-------------|
| `POST /ache/design/column` | Column design per AISC |
| `POST /ache/design/beam` | Beam design per AISC |
| `POST /ache/design/anchor-bolts` | Anchor bolt design |

### Access System Design

**Endpoint:** `POST /ache/design/access`

Designs per OSHA requirements:
- Platforms (minimum 450mm width)
- Handrails (minimum 1070mm height)
- Ladders (cage required > 6.1m)
- Toe plates (minimum 89mm)

---

## Compliance Checking

### API 661 Compliance

**Endpoint:** `POST /ache/compliance/check`

Checks design against API 661 / ISO 13706 requirements:

| Check | Requirement | Reference |
|-------|-------------|-----------|
| Tube length | ≤ 12.0 m | 5.1.1 |
| Tube wall | ≥ 2.11 mm | 5.1.3 |
| Fan tip speed | ≤ 61 m/s | 6.1.1 |
| Blade clearance | ≥ 12.7 mm | Table 6 |
| Header split | Required if ΔT > 110°C | 7.1.6.1.2 |

---

## AI-Powered Features

### Design Recommendations

**Endpoint:** `POST /ache/ai/recommendations`

Get optimization suggestions based on current design.

### Troubleshooting

**Endpoint:** `GET /ache/ai/troubleshoot/{problem}`

Example: `/ache/ai/troubleshoot/high%20temperature`

Returns:
- Possible causes
- Diagnostic steps
- Solutions

### Knowledge Base

**Endpoint:** `GET /ache/ai/knowledge?query=tube%20selection`

Query the ACHE engineering knowledge base.

### Optimization

**Endpoint:** `POST /ache/optimize/suggestions`

```json
{
  "optimization_targets": ["cost", "efficiency", "footprint"]
}
```

---

## Field Erection Support

### Complete Erection Plan

**Endpoint:** `POST /ache/erection/plan`

Generates:
- Shipping split recommendations
- Lifting lug design per ASME BTH-1
- Rigging plan with crane selection
- Erection sequence with safety notes

### Lifting Lug Design

**Endpoint:** `POST /ache/erection/lifting-lug`

Designs per ASME BTH-1 with checks for:
- Bearing capacity
- Tearout capacity
- Tension capacity
- Weld capacity

---

## Export Features

### Datasheet Export

**Endpoint:** `POST /ache/export/datasheet`

Generates API 661 compliant datasheet in JSON format.

### Bill of Materials

**Endpoint:** `POST /ache/export/bom`

Generates equipment BOM with:
- Tube bundle items
- Fan system components
- Structural steel
- Accessories

---

## Standards Reference

### Quick Reference

**Endpoint:** `GET /ache/standards/api661`

Returns API 661 key requirements for quick lookup.

### Key API 661 Requirements

| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Max tube length | 12.0 m | 5.1.1 |
| Min tube wall | 2.11 mm (BWG 14) | 5.1.3 |
| Header split | Required if ΔT > 110°C | 7.1.6.1.2 |
| Max fan tip speed | 61 m/s | 6.1.1 |
| Min blade clearance | 12.7 mm | Table 6 |
| Max air-side ΔP | 250 Pa typical | 6.2.1 |

### OSHA Requirements (1910)

| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Walkway width | ≥ 450 mm | 1910.22 |
| Handrail height | ≥ 1070 mm | 1910.29 |
| Ladder cage | Required > 6.1 m | 1910.28 |
| Toe plate | ≥ 89 mm | 1910.29 |

---

## Batch Operations

### Batch Fan Calculations

**Endpoint:** `POST /ache/calculate/batch/fan`

Calculate multiple fan configurations in one request:

```json
{
  "calculations": [
    {"air_flow_m3_s": 30, "static_pressure_pa": 200, "fan_diameter_m": 3.0, "fan_rpm": 300, "fan_efficiency": 0.75},
    {"air_flow_m3_s": 50, "static_pressure_pa": 200, "fan_diameter_m": 3.0, "fan_rpm": 300, "fan_efficiency": 0.75}
  ]
}
```

---

## Error Handling

All endpoints return standard HTTP error codes:

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - No active model |
| 422 | Validation Error - Missing or invalid fields |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Module not loaded |

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

---

## Python Module Usage

The ACHE assistant modules can also be used directly in Python:

```python
from agents.cad_agent.ache_assistant import (
    ACHECalculator,
    StructuralDesigner,
    AccessoryDesigner,
    ACHEAssistant,
    ErectionPlanner,
)

# Calculate fan performance
calc = ACHECalculator()
result = calc.calculate_fan_performance(
    air_flow_m3_s=50,
    static_pressure_pa=200,
    fan_diameter_m=3.0,
    fan_rpm=300,
    fan_efficiency=0.75,
)
print(f"Shaft power: {result.shaft_power_kw:.2f} kW")
print(f"Tip speed: {result.tip_speed_m_s:.2f} m/s")

# Design a column
struct = StructuralDesigner()
column = struct.design_column(
    axial_load_kn=200,
    height_m=4.0,
    moment_kn_m=20,
    k_factor=1.0,
)
print(f"Profile: {column.profile}")
print(f"Utilization: {column.utilization:.2%}")

# Check API 661 compliance
assistant = ACHEAssistant()
result = assistant.check_api661_compliance({
    "tube_bundle": {"tube_length_m": 10},
    "fan_system": {"tip_speed_m_s": 55}
})
print(f"Compliant: {result.is_compliant}")
```

---

## Test Suite

Run the Phase 24 test suite:

```bash
cd Project_Vulcan
python -m pytest tests/test_phase24_ache.py -v
```

Current test coverage: **70 tests, all passing**

---

## Support

For issues or feature requests, see the Project Vulcan repository.

**Last Updated:** December 26, 2025
