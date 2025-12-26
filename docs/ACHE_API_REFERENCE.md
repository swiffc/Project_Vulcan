# ACHE Design Assistant API Reference

Phase 24 - Air Cooled Heat Exchanger Design Automation

## Overview

The ACHE Design Assistant provides comprehensive engineering tools for Air Cooled Heat Exchanger design per API 661 / ISO 13706. All endpoints are prefixed with `/ache/`.

## Base URL

```
http://localhost:8000/ache
```

---

## Core Endpoints

### GET /ache/status

Get ACHE system status.

**Response:**
```json
{
  "ache_available": true,
  "listener_active": false,
  "current_model": null
}
```

### POST /ache/listener/start

Start SolidWorks model event listener for auto-detection.

### POST /ache/listener/stop

Stop the model event listener.

### GET /ache/detect

Detect if current model is an ACHE unit.

**Response:**
```json
{
  "is_ache": true,
  "confidence": 0.95,
  "detection_method": "custom_property",
  "components_found": ["header_box", "tube_bundle", "fan"]
}
```

### GET /ache/overview

Get model overview with basic properties.

### GET /ache/properties

Extract comprehensive ACHE properties from current model.

---

## Calculation Endpoints

### POST /ache/calculate/thermal

Calculate thermal performance using LMTD or NTU-effectiveness method.

**Request:**
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

**Response:**
```json
{
  "duty_kw": 1000,
  "lmtd_k": 42.5,
  "lmtd_correction_factor": 0.92,
  "overall_u_w_m2_k": 44.1,
  "effectiveness": 0.78,
  "ntu": 2.1,
  "air_outlet_temp_c": 47.2,
  "overdesign_percent": 15.3,
  "min_approach_temp_c": 12.8,
  "is_acceptable": true,
  "warnings": []
}
```

### POST /ache/calculate/fan

Calculate fan performance and power requirements per API 661.

**Request:**
```json
{
  "air_flow_m3_s": 50,
  "static_pressure_pa": 200,
  "fan_diameter_m": 3.0,
  "fan_rpm": 300,
  "fan_efficiency": 0.75
}
```

**Response:**
```json
{
  "air_flow_m3_s": 50,
  "air_flow_acfm": 105944,
  "static_pressure_pa": 200,
  "static_pressure_inwg": 0.803,
  "shaft_power_kw": 13.3,
  "motor_power_kw": 15.9,
  "tip_speed_m_s": 47.1,
  "tip_speed_acceptable": true,
  "noise_db_a": 82.5,
  "warnings": []
}
```

**API 661 Checks:**
- Maximum tip speed: 61 m/s (200 ft/s)
- Noise level warning if > 90 dBA

### POST /ache/calculate/pressure-drop/tube

Calculate tube-side pressure drop.

**Request:**
```json
{
  "mass_flow_kg_s": 50,
  "tube_id_mm": 22,
  "tube_length_m": 6,
  "num_tubes": 500,
  "num_passes": 4,
  "fluid_density_kg_m3": 800,
  "fluid_viscosity_pa_s": 0.001
}
```

**Response:**
```json
{
  "tube_side_dp_kpa": 45.2,
  "tube_friction_dp_kpa": 32.1,
  "tube_entrance_exit_dp_kpa": 8.5,
  "tube_return_bend_dp_kpa": 4.6,
  "is_within_limits": true,
  "warnings": []
}
```

### POST /ache/calculate/pressure-drop/air

Calculate air-side pressure drop across tube bundle.

**Request:**
```json
{
  "air_flow_kg_s": 100,
  "air_inlet_temp_c": 35,
  "bundle_face_area_m2": 30,
  "tube_od_mm": 25.4,
  "fin_pitch_mm": 2.5,
  "fin_height_mm": 12.7,
  "num_tube_rows": 4
}
```

**Response:**
```json
{
  "air_side_dp_pa": 185,
  "bundle_dp_pa": 154,
  "plenum_dp_pa": 31,
  "is_within_limits": true,
  "warnings": []
}
```

**API 661 Limit:** Maximum 250 Pa typical

### POST /ache/calculate/size

Preliminary ACHE sizing calculation.

**Request:**
```json
{
  "duty_kw": 1000,
  "process_inlet_temp_c": 120,
  "process_outlet_temp_c": 60,
  "air_inlet_temp_c": 35
}
```

**Response:**
```json
{
  "duty_kw": 1000,
  "air_outlet_temp_c": 50,
  "air_mass_flow_kg_s": 66.2,
  "air_volume_flow_m3_s": 57.4,
  "face_area_m2": 19.1,
  "surface_area_m2": 575,
  "estimated_tubes": 450,
  "tube_length_m": 6,
  "estimated_bays": 2,
  "num_fans": 2,
  "fan_diameter_m": 2.7,
  "lmtd_k": 42.5,
  "estimated_u_w_m2_k": 45
}
```

---

## Structural Design Endpoints

### POST /ache/design/frame

Design complete ACHE support frame per AISC.

**Request:**
```json
{
  "bundle_weight_kn": 500,
  "bundle_length_m": 12,
  "bundle_width_m": 3,
  "bundle_height_m": 2,
  "num_bays": 2,
  "elevation_m": 4,
  "wind_speed_m_s": 40
}
```

**Response:**
```json
{
  "num_columns": 9,
  "num_beams": 8,
  "total_steel_weight_kg": 2850,
  "max_utilization": 0.78,
  "governing_case": "D+L+W",
  "is_adequate": true,
  "columns": [
    {"profile": "HSS8x8x3/8", "height_m": 4, "utilization": 0.78, "is_adequate": true}
  ],
  "beams": [
    {"profile": "W10x33", "span_m": 6, "utilization": 0.65, "is_adequate": true}
  ],
  "warnings": []
}
```

**Load Combinations (LRFD):**
- D+L: 1.2D + 1.6L
- D+W: 1.2D + 1.0W
- D+L+W: 1.2D + 1.0L + 0.5W
- D+E: 1.2D + 1.0E

---

## Access Design Endpoints

### POST /ache/design/access

Design complete access system (platforms, ladders, handrails) per OSHA.

**Request:**
```json
{
  "bundle_length_m": 12,
  "bundle_width_m": 3,
  "elevation_m": 5,
  "num_bays": 2,
  "fan_deck_required": true,
  "header_access_required": true
}
```

**Response:**
```json
{
  "total_grating_m2": 32.4,
  "total_steel_kg": 1250,
  "platforms": [
    {"type": "Fan Deck Walkway", "quantity": 2, "length_m": 12, "width_m": 0.9}
  ],
  "ladders": [
    {"type": "Access Ladder", "quantity": 1, "height_m": 5}
  ],
  "handrails": [
    {"type": "Fan Deck Handrail", "quantity": 1, "length_m": 24}
  ],
  "bom_items": [...]
}
```

**OSHA Compliance:**
- Minimum walkway width: 450mm (18")
- Handrail height: 1070mm (42")
- Ladder cage required > 6.1m (20 ft)
- Toe plate height: 89mm (3.5")

---

## AI Assistant Endpoints

### POST /ache/compliance/check

Check design against API 661 requirements.

**Request:**
```json
{
  "ache_properties": {
    "tube_bundle": {
      "tube_length_m": 10,
      "tube_od_mm": 25.4,
      "tube_wall_mm": 2.5
    },
    "fan_system": {
      "tip_speed_m_s": 55,
      "blade_clearance_mm": 15
    }
  }
}
```

**Response:**
```json
{
  "standard": "API 661 / ISO 13706",
  "is_compliant": true,
  "total_checks": 8,
  "passed": 7,
  "failed": 0,
  "warnings": 1,
  "summary": "Design is API 661 compliant with 1 warnings",
  "issues": [
    {
      "code_reference": "API 661 5.1.1",
      "requirement": "Maximum tube length: 12.0m",
      "actual_value": "10m",
      "required_value": "<= 12.0m",
      "status": "compliant",
      "severity": "low",
      "recommendation": ""
    }
  ]
}
```

### POST /ache/ai/recommendations

Get AI-powered design recommendations.

**Request:**
```json
{
  "ache_properties": {
    "thermal_performance": {
      "approach_temp_c": 8,
      "overdesign_percent": 5
    }
  }
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "category": "Thermal Design",
      "recommendation": "Consider increasing approach temperature",
      "rationale": "Current approach of 8°C is below recommended 10°C minimum",
      "impact": "high",
      "references": ["API 661 Annex A"],
      "alternatives": ["Increase surface area", "Add more tube rows"]
    }
  ]
}
```

### GET /ache/ai/troubleshoot/{problem}

Get troubleshooting guidance.

**Example:** `/ache/ai/troubleshoot/high%20temperature`

**Response:**
```json
{
  "problem": "high temperature",
  "possible_causes": [
    "Insufficient air flow",
    "Fouled tubes",
    "Fan blade pitch incorrect"
  ],
  "diagnostic_steps": [
    "Check fan operation and blade angles",
    "Measure air flow rate",
    "Inspect tubes for fouling"
  ],
  "solutions": [
    "Increase fan speed or blade pitch",
    "Clean tube bundle"
  ]
}
```

### GET /ache/ai/knowledge

Query the ACHE knowledge base.

**Parameters:**
- `query` (required): Search query
- `category` (optional): Filter by category

**Example:** `/ache/ai/knowledge?query=tube%20selection`

---

## Erection Planning Endpoints

### POST /ache/erection/plan

Create complete erection plan.

**Request:**
```json
{
  "project_name": "Refinery Expansion",
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
```

**Response:**
```json
{
  "project_name": "Refinery Expansion",
  "equipment_tag": "AC-101",
  "total_weight_kg": 50000,
  "shipment_type": "modular",
  "is_feasible": true,
  "total_lift_hours": 12,
  "crane_days": 1.5,
  "lifting_lugs": [
    {
      "location": "Lug NE",
      "design_load_kn": 122.6,
      "plate_thickness_mm": 25.4,
      "hole_diameter_mm": 38.1,
      "utilization": 0.72,
      "is_adequate": true
    }
  ],
  "rigging_plan": {
    "num_slings": 4,
    "sling_diameter_mm": 25.4,
    "crane_capacity_tonnes": 68.8,
    "needs_spreader": false
  },
  "shipping_splits": [],
  "erection_sequence": [
    {
      "step": 1,
      "description": "Erect Support Structure",
      "weight_kg": 7500,
      "crane": "100T mobile",
      "duration_hours": 3,
      "safety_notes": ["Verify rigging before lift"]
    }
  ]
}
```

### POST /ache/erection/lifting-lug

Design individual lifting lug per ASME BTH-1.

**Parameters:**
- `design_load_kn` (required): Static design load
- `sling_angle_deg` (optional, default 60): Sling angle from horizontal

**Response:**
```json
{
  "design_load_kn": 100,
  "total_design_load_kn": 231,
  "hole_diameter_mm": 38.1,
  "plate_thickness_mm": 25.4,
  "plate_width_mm": 152,
  "plate_height_mm": 114,
  "weld_size_mm": 8,
  "bearing_capacity_kn": 345,
  "tearout_capacity_kn": 289,
  "tension_capacity_kn": 312,
  "weld_capacity_kn": 425,
  "utilization": 0.80,
  "is_adequate": true,
  "warnings": []
}
```

---

## Optimization Endpoints

### POST /ache/optimize/suggestions

Get AI-powered design optimization suggestions.

**Request:**
```json
{
  "ache_properties": {},
  "thermal_results": {},
  "optimization_targets": ["cost", "efficiency", "footprint"],
  "constraints": {}
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "category": "Cost Optimization",
      "suggestion": "Standardize tube and fin dimensions",
      "impact": "medium",
      "estimated_improvement": "5-8% cost reduction"
    },
    {
      "category": "Efficiency Optimization",
      "suggestion": "Increase fin density for better heat transfer",
      "impact": "high",
      "estimated_improvement": "10-15% thermal improvement"
    }
  ],
  "optimization_targets": ["cost", "efficiency", "footprint"],
  "constraints_applied": {}
}
```

### POST /ache/design/anchor-bolts

Design anchor bolts for ACHE support structure.

**Parameters:**
- `base_shear_kn` (required): Base shear load
- `uplift_kn` (required): Uplift load
- `num_bolts` (optional, default 4): Number of bolts
- `bolt_grade` (optional, default "F1554-36"): Bolt grade

**Response:**
```json
{
  "bolt_diameter_mm": 25.4,
  "bolt_grade": "F1554-36",
  "num_bolts": 4,
  "embedment_depth_mm": 305,
  "shear_capacity_kn": 150,
  "tension_capacity_kn": 120,
  "utilization": 0.75,
  "is_adequate": true,
  "base_plate_thickness_mm": 25.4,
  "warnings": []
}
```

### GET /ache/summary

Get complete ACHE design summary from current model.

**Response:**
```json
{
  "equipment_tag": "AC-101",
  "detected_type": "Air Cooled Heat Exchanger",
  "has_tube_bundle": true,
  "has_header_box": true,
  "has_fan_system": true,
  "has_support_structure": true,
  "compliance_status": "pending"
}
```

---

## Error Responses

All endpoints return standard HTTP error codes:

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - No active model |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Module not loaded |

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

---

## Standards Reference

### API 661 Key Requirements

| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Max tube length | 12.0 m | 5.1.1 |
| Min tube wall | 2.11 mm (BWG 14) | 5.1.3 |
| Header split | Required if ΔT > 110°C | 7.1.6.1.2 |
| Max fan tip speed | 61 m/s | 6.1.1 |
| Min blade clearance | 12.7 mm | Table 6 |

### OSHA Requirements

| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Walkway width | ≥ 450 mm | 1910.22 |
| Handrail height | ≥ 1070 mm | 1910.29 |
| Ladder cage | Required > 6.1 m | 1910.28 |
| Toe plate | ≥ 89 mm | 1910.29 |

### AISC Steel Design

| Parameter | Limit |
|-----------|-------|
| Column slenderness | KL/r ≤ 200 |
| Beam deflection | L/240 typical |
| Connection bolts | A325 or A490 |
