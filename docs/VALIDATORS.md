# Project Vulcan - Validation System Documentation

## Overview

Project Vulcan provides a comprehensive engineering validation system with 40+ validators covering structural, mechanical, and documentation standards. All validators are accessible via REST API endpoints.

## Quick Start

### Server Setup
```bash
cd desktop_server
python server.py
```
Server runs on `http://localhost:8000`

### API Health Check
```bash
curl http://localhost:8000/health
```

---

## Validator Categories

### 1. Manufacturing & Fabrication

#### Fabrication Feasibility
**Endpoint:** `POST /phase25/check-fabrication`

Validates manufacturing constraints for sheet metal and plate fabrication.

```json
{
  "thickness_in": 0.5,
  "length_in": 48,
  "width_in": 24,
  "holes": [
    {"diameter": 0.75, "x": 2, "y": 2}
  ],
  "slots": [{"width": 0.5, "length": 2, "x": 24, "y": 12}],
  "bends": [],
  "process": "plasma"
}
```

Checks:
- Minimum feature sizes
- Hole spacing (2.67x diameter min)
- Edge distances
- Bend radii (material-specific)

---

### 2. Structural Steel (AISC 360-16)

#### Beam Design
**Endpoint:** `POST /phase25/validate-beam`

```json
{
  "shape": "W16X77",
  "span_ft": 20,
  "unbraced_length_ft": 5,
  "moment_kip_ft": 100,
  "shear_kips": 30,
  "material": "A992",
  "deflection_limit": "floor_live"
}
```

Checks:
- Flexural capacity (AISC F2)
- Shear capacity (AISC G2)
- Lateral-torsional buckling (AISC F2.2)
- Deflection limits (IBC)
- Compact section (AISC B4.1)

#### Column Design
**Endpoint:** `POST /phase25/validate-column`

```json
{
  "shape": "W14X68",
  "height_ft": 12,
  "axial_load_kips": 200,
  "moment_x_kip_ft": 50,
  "k_factor": 1.0,
  "material": "A992"
}
```

Checks:
- Slenderness ratio (KL/r < 200)
- Compression capacity (AISC E3)
- Combined forces (AISC H1)

#### Steel Connections
**Endpoint:** `POST /phase25/validate-connection`

```json
{
  "connection_type": "bolted_shear",
  "load_kips": 30,
  "bolt_diameter": 0.75,
  "bolt_grade": "A325",
  "num_bolts": 4,
  "plate_thickness": 0.5
}
```

Connection types: `bolted_shear`, `bolted_moment`, `welded_shear`, `welded_moment`, `shear_tab`, `clip_angle`

#### Base Plate Design
**Endpoint:** `POST /phase25/validate-base-plate`

```json
{
  "plate_length": 14,
  "plate_width": 14,
  "plate_thickness": 1.0,
  "column_depth": 8,
  "column_bf": 8,
  "axial_load_kips": 150,
  "concrete_fc_psi": 3000
}
```

---

### 3. Materials & Finishing

#### Materials Validation
**Endpoint:** `POST /phase25/check-materials`

```json
{
  "material_spec": "A572-50",
  "thickness_in": 0.5,
  "coating_system": "C1",
  "surface_prep": "SP10",
  "service_environment": "severe"
}
```

---

### 4. Fasteners & Connections

#### Fastener Analysis
**Endpoint:** `POST /phase25/check-fasteners`

```json
{
  "bolts": [
    {"diameter": 0.75, "grade": "A325", "connection_type": "slip_critical"}
  ],
  "connection": {
    "grip_length": 1.5,
    "load_kips": 15,
    "load_type": "shear"
  }
}
```

#### Rigging & Lifting
**Endpoint:** `POST /phase25/check-rigging`

```json
{
  "lug": {
    "plate_thickness": 0.75,
    "plate_width": 6,
    "hole_diameter": 1.25,
    "rated_load_lbs": 10000,
    "sling_angle_deg": 60
  }
}
```

---

### 5. GD&T Validation (ASME Y14.5-2018)

#### Full GD&T Check
**Endpoint:** `POST /phase25/check-gdt`

Validates all 14 geometric tolerance symbols per ASME Y14.5-2018.

---

### 6. Welding (AWS D1.1)

#### Weld Validation
**Endpoint:** `POST /phase25/check-weld`

#### Inspection/QC
**Endpoint:** `POST /phase25/check-inspection`

```json
{
  "drawing_number": "DWG-001",
  "code": "AWS D1.1",
  "welds": [
    {"type": "fillet", "size": 0.25, "length": 12, "category": "critical"}
  ]
}
```

---

### 7. ACHE / Heat Exchangers

#### API 661 Bundle Validation
**Endpoint:** `POST /phase25/check-api661`

82+ checks for air-cooled heat exchanger design.

#### ASME VIII Pressure Vessel
**Endpoint:** `POST /phase25/check-asme-viii`

#### TEMA Heat Exchangers
**Endpoint:** `POST /phase25/check-tema`

---

### 8. Piping (ASME B31.3)

#### Pipe Design
**Endpoint:** `POST /phase25/check-b31-3`

```json
{
  "nominal_size_in": 4.0,
  "wall_thickness_in": 0.237,
  "material": "A106-B",
  "design_pressure_psig": 150,
  "design_temp_f": 300
}
```

---

### 9. Documentation

#### Drawing Documentation
**Endpoint:** `POST /phase25/check-documentation`

```json
{
  "title_block": {
    "drawing_number": "DWG-001",
    "revision": "B",
    "title": "Assembly Drawing"
  },
  "notes": {
    "general_notes": ["1. All dims in inches"]
  },
  "bom": [
    {"item": 1, "part_number": "P001", "qty": 1}
  ]
}
```

---

## Export Endpoints

### PDF Report
**Endpoint:** `POST /phase25/generate-pdf-report`

```json
{
  "drawing_number": "DWG-001",
  "validator_results": {
    "fabrication": {...},
    "materials": {...}
  },
  "include_charts": true,
  "summary_only": false
}
```

Returns base64-encoded PDF.

### Excel BOM Export
**Endpoint:** `POST /phase25/export-bom-excel`

```json
{
  "items": [
    {"part_number": "P001", "description": "Part 1", "qty": 2}
  ],
  "metadata": {
    "assembly_number": "ASSY-001",
    "project_name": "Project"
  }
}
```

### CSV BOM Export
**Endpoint:** `POST /phase25/export-bom-csv`

Same format as Excel export.

### Drawing Markup (SVG)
**Endpoint:** `POST /phase25/generate-markup`

```json
{
  "drawing_number": "DWG-001",
  "issues": [
    {"severity": "warning", "message": "Check dimension", "location": {"x": 100, "y": 200}}
  ]
}
```

---

## Response Format

All validators return:

```json
{
  "valid": true,
  "total_checks": 10,
  "passed": 9,
  "failed": 0,
  "warnings": 1,
  "critical_failures": 0,
  "issues": [
    {
      "severity": "warning",
      "check_type": "dimension",
      "message": "Tolerance tight for process",
      "suggestion": "Consider relaxing tolerance",
      "standard_reference": "ASME Y14.5"
    }
  ],
  "calculations": {
    "stress": 15.2,
    "capacity": 20.0,
    "dcr": 0.76
  }
}
```

---

## Standards Coverage

| Standard | Validator |
|----------|-----------|
| AISC 360-16 | Beam, Column, Connection, Base Plate |
| ASME Y14.5-2018 | GD&T, Tolerances |
| AWS D1.1 | Welding, Inspection |
| API 661 | ACHE Bundle, Thermal |
| ASME VIII Div.1 | Pressure Vessels |
| ASME B31.3 | Process Piping |
| TEMA | Shell & Tube HX |
| NEMA MG1 | Motors |
| SSPC | Coatings |
| OSHA 1910 | Rigging, Safety |

---

## Web Dashboard

Access the web dashboard at:
```
http://localhost:3000/cad
```

Features:
- Model Overview
- Drawing Validation
- All Validators Dashboard
- CAD Tools
- ACHE Design
- Validation History

---

## Running Tests

```bash
python -m pytest tests/test_validators_unit.py -v
python -m pytest tests/test_phase25_endpoints.py -v
```

---

## Support

For issues, check:
- Server logs in `logs/` directory
- API docs at `http://localhost:8000/docs`
