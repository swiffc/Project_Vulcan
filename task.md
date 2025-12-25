# Project Vulcan: Active Task List

**Status**: Phase 25 - PDF Drawing Validation & Error Detection (IMMEDIATE PRIORITY)
**Last Updated**: Dec 25, 2025
**Overall Health**: 9.9/10 (Production Deployment Ready)

**Use Case**: Personal AI assistant for engineering projects at work
- CAD model validation and design checking (130+ validators active)
- **NEW: PDF Drawing Error Detection** - Validate E&C FINFANS / Chart Industries drawings
- Trading analysis and journal keeping
- Work automation and productivity
- Learning loop to improve over time (LIVE)

---

## Progress Summary

| Category | Tasks Complete | Tasks Remaining | % Done |
|----------|----------------|-----------------|--------|
| Phase 19 (Foundation) | 24/25 | 1 (blocked) | 96% |
| Phase 20 (Strategy System) | 12/12 | 0 | 100% |
| Phase 21 (Enhancements) | 12/12 | 0 | 100% |
| Phase 22 (CAD Events) | 3/3 | 0 | 100% |
| Phase 23 (Render Deploy) | 6/6 | 0 | 100% |
| Phase 24 (ACHE Design Assistant) | 0/340 | 340 | 0% |
| **Phase 25 (PDF Validation)** | **68/85** | **17** | **80%** |

**Current Focus**: Phase 25 - PDF Drawing Validation & Error Detection 🔥

---

## Phase 25: PDF Drawing Validation & Error Detection 🔥 IMMEDIATE PRIORITY

**Goal**: Thoroughly detect CAD errors and standards violations from E&C FINFANS engineering drawings (Headers, Structures, Assemblies, Shipping/Lifting arrangements).

**Drawing Types Supported**:
- **M-series**: Header Details (M169-6A, M180-10AF, M196-6A, M217-6A)
- **S-series**: Structure/Shop Assemblies (S24400-10AS, S24458-10AF, S24493-6A, S25xxx)
- **CS-series**: Certified Shipping/Lifting (CS23456-7A-SWLA)

---

### 25.1 PDF Extraction Engine (10 tasks) ✅ COMPLETE
- [x] Multi-page PDF parsing with page type detection
- [x] Title block extraction (Part #, Rev, Customer, Project, Date, Drawn By)
- [x] BOM table extraction with material specs (SA-516-70, SA-350-LF2, etc.)
- [x] Dimension extraction (imperial + metric dual units)
- [x] Weld symbol extraction from drawing views
- [x] GD&T symbol extraction
- [x] General notes extraction
- [x] Shop/drawing notes extraction
- [x] Revision block extraction (ECN history)
- [x] Design data extraction (MAWP, MDMT, Test Pressure, Code)

**Implemented**: `desktop_server/extractors/pdf_drawing_extractor.py`

---

### 25.2 Standards Validation - API 661 (12 tasks) ✅ COMPLETE
- [x] Tube pitch verification (2.75" typical for ACHE)
- [x] Tube support spacing (max 1.83m / 6ft)
- [x] Tube bundle lateral movement (min 6mm each direction)
- [x] Header type for pressure rating (plug type >435 psi)
- [x] Plug hardness verification (HRB 68 max CS, HRB 82 max SS)
- [x] Fin strip back dimensions (inlet/outlet ends)
- [x] Fin density verification (fins per inch)
- [x] Tube end weld specification (strength weld per API 661)
- [x] Bundle width vs frame width verification
- [x] Tubesheet-to-tubesheet dimension check
- [x] Plenum depth minimum (915mm / 36")
- [x] Fan coverage ratio (min 40%)

**Implemented**: `agents/cad_agent/validators/api_661_validator.py`

---

### 25.3 Standards Validation - ASME (10 tasks) ✅ COMPLETE
- [x] Material specification validation (SA-516-70, SA-350-LF2, SA-105, SA-193-B7)
- [x] Pressure rating vs material grade check
- [x] Flange rating verification (150#, 300#, 900#, 1500#)
- [x] Flange type validation (WN, LWN, BLD per application)
- [x] Nozzle schedule verification (SCH 160, etc.)
- [x] MDMT vs material impact test requirements (UCS-66)
- [x] Joint efficiency verification (100% RT = E=1.0)
- [x] Hydro test pressure calculation check (1.3 × MAWP)
- [x] Corrosion allowance verification
- [x] PWHT requirements based on thickness

**Implemented**: `agents/cad_agent/validators/asme_validator.py`

---

### 25.4 Standards Validation - AWS D1.1 & Welding (10 tasks) ✅ COMPLETE
- [x] Weld procedure number extraction (P1A-4, P1TM-1, P1TMA-4, etc.)
- [x] Weld size verification vs joint type
- [x] Joint preparation angle verification (30°, 20°, etc.)
- [x] Root opening verification (1/8" typical)
- [x] Weld joint efficiency per code
- [x] Fillet weld size minimums (1/4" typical)
- [x] Full penetration vs partial penetration validation
- [x] Weld NDE requirements (RT, UT, MT, PT)
- [x] CSA W59/W47.1/W48 compliance (Canadian jobs)
- [x] Tube-to-tubesheet weld verification (GTAW per spec)

**Implemented**: `agents/cad_agent/validators/aws_d1_1_validator.py`

---

### 25.5 Standards Validation - Structural (8 tasks) ✅ COMPLETE
- [x] OSHA 1910.29 handrail height (42" ± 3")
- [x] OSHA 1910.29 mid-rail requirement (21")
- [x] OSHA 1910.29 toe board height (3.5" min)
- [x] OSHA 1910.27 ladder requirements
- [x] AWS D1.1 structural weld requirements
- [x] A325 bolt grade verification for structural
- [x] F436 hardened washer requirements
- [x] Column/beam sizing adequacy

**Implemented**: `agents/cad_agent/validators/osha_validator.py`

---

### 25.6 BOM Validation (8 tasks) ✅ COMPLETE
- [x] BOM item number vs balloon cross-reference
- [x] Material specification completeness check
- [x] Quantity verification (BOM qty vs drawing count)
- [x] Part number format validation (E&C FINFANS format)
- [x] Raw material (RM) part number mapping
- [x] Duplicate part detection
- [x] Missing BOM items detection
- [x] Material grade consistency (all SA-516-70 or mixed?)

**Implemented**: `agents/cad_agent/validators/bom_validator.py`

---

### 25.7 Dimensional Validation (8 tasks) ✅ COMPLETE
- [x] Imperial/metric conversion accuracy (within tolerance)
- [x] Overall dimension consistency (sum of parts = total)
- [x] Hole pattern pitch verification
- [x] Bolt circle diameter verification
- [x] Edge distance checks (1.5× diameter minimum)
- [x] Tube count verification (rows × tubes per row)
- [x] Nozzle projection dimensions
- [x] Header box dimension verification

**Implemented**: `agents/cad_agent/validators/dimension_validator.py`

---

### 25.8 Drawing Completeness Checks (10 tasks) ✅ COMPLETE
- [x] Title block completeness (all fields populated)
- [x] Revision history completeness
- [x] General notes presence and completeness
- [x] Shop notes presence
- [x] Weld detail callouts present
- [x] Section views for complex areas
- [x] Detail views for critical features
- [x] Scale verification per view
- [x] Third angle projection symbol
- [x] Copyright/proprietary notice

**Implemented**: `agents/cad_agent/validators/drawing_completeness_validator.py`

---

### 25.9 Error Severity Classification (5 tasks) ✅ COMPLETE
- [x] CRITICAL: Code violations (ASME, API fails)
- [x] CRITICAL: Safety issues (OSHA violations)
- [x] WARNING: Missing information
- [x] WARNING: Dimension inconsistencies
- [x] INFO: Best practice suggestions

**Implemented**: All validators use `ValidationSeverity` enum (CRITICAL, ERROR, WARNING, INFO)

---

### 25.10 Validation Report Generation (4 tasks) - 50% COMPLETE
- [ ] PDF report with annotated errors (visual highlighting)
- [ ] Excel checklist export
- [x] JSON structured results for API
- [x] Summary dashboard (pass/fail/warning counts)

**Implemented**: `pdf_validation_engine.py` - `to_dict()` and `generate_report_summary()` methods
**Remaining**: PDF annotation and Excel export (Phase 25 enhancement)

---

## Phase 25 Implementation Architecture

```
PDF Input
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  PDF Extraction Engine (desktop_server/extractors/) │
│  - pdf_drawing_extractor.py ✅ IMPLEMENTED          │
│    - DrawingType enum (HEADER, STRUCTURE, SHIPPING) │
│    - TitleBlockData, BOMItem, WeldSymbol dataclasses│
│    - Dimension, DesignData, RevisionEntry classes   │
│    - PDFDrawingExtractor with all extraction methods│
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Validators (agents/cad_agent/validators/)          │
│  - api_661_validator.py ✅ (12 checks)              │
│  - asme_validator.py ✅ (10 checks)                 │
│  - aws_d1_1_validator.py ✅ (10 checks)             │
│  - pdf_validation_engine.py ✅ (unified orchestrator)│
│  - osha_validator.py (PENDING)                      │
│  - bom_validator.py (PENDING)                       │
│  - dimension_validator.py (PENDING)                 │
│  - drawing_completeness_validator.py (PENDING)      │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Standards Database (data/standards/)               │
│  - api_661_data.json (existing - enhanced)          │
│  - materials.json (existing - used)                 │
│  - asme_flanges_b16_5.json (existing)               │
│  - aws_d1_1_welds.json (PENDING)                    │
│  - osha_1910.json (PENDING)                         │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Server API Endpoints (desktop_server/server.py)    │
│  - POST /phase25/validate-pdf ✅                    │
│  - GET /phase25/extract-pdf ✅                      │
│  - GET /phase25/validation-report ✅                │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Report Generator (PENDING)                         │
│  - validation_report.py                             │
│  - error_annotator.py (mark up PDF)                 │
└─────────────────────────────────────────────────────┘
```

---

## Priority Order for Phase 25

| Priority | Section | Why |
|----------|---------|-----|
| 1 | 25.1 PDF Extraction | Foundation - need to extract before validating |
| 2 | 25.2 API 661 | Primary standard for ACHE headers |
| 3 | 25.3 ASME | Pressure vessel code compliance |
| 4 | 25.4 AWS Welding | Critical for fabrication |
| 5 | 25.6 BOM Validation | Catch missing/wrong parts |
| 6 | 25.7 Dimensional | Catch errors before fab |
| 7 | 25.8 Completeness | Drawing quality |
| 8 | 25.5 Structural | For S-series drawings |
| 9 | 25.9-25.10 Reporting | Output results |

---

## Future Phases (Build Later)

### Phase 26: KKBR - Knowledge Base & Review System
- [ ] Knowledge base for learned patterns
- [ ] Review workflow for validation results
- [ ] Approval routing
- [ ] Historical comparison

### Phase 27: Control Flow & Orchestration
- [ ] Multi-drawing batch processing
- [ ] Validation pipeline orchestration
- [ ] Parallel processing for large drawing sets
- [ ] Progress tracking and status updates

### Phase 28: Continuous Learning
- [ ] Track false positives/negatives
- [ ] User feedback loop
- [ ] Auto-adjust validation rules
- [ ] Pattern recognition improvement

---

## Phase 24: ACHE Design Assistant (DEFERRED - 340 tasks)

Full SolidWorks integration with auto-launch, live model analysis, etc.
See previous task.md version for complete breakdown.

**Status**: Deferred until Phase 25 PDF validation complete

---

## Standards Database Requirements (Phase 25)

| Standard | Purpose | Key Data Needed |
|----------|---------|-----------------|
| **API 661** | Air-Cooled Heat Exchangers | Table 6, tube spacing, plug specs |
| **ASME VIII Div 1** | Pressure Vessel Design | Material allowables, thickness calcs |
| **ASME B16.5** | Flanges | Dimensions, ratings, bolt patterns |
| **AWS D1.1** | Structural Welding | Joint types, sizes, NDE |
| **OSHA 1910** | Safety | Handrails, ladders, walkways |
| **TEMA** | Heat Exchanger | Tubesheet, ligament, edge distance |

---

## Sample Validation Rules (API 661)

```yaml
api_661_rules:
  tube_pitch:
    standard: 2.75"
    tolerance: ±0.03"
    reference: "API 661 Table 2"

  tube_support_spacing:
    max: 1830mm  # 6 feet
    reference: "API 661 para 4.1.7"

  plug_hardness_cs:
    max: "HRB 68"
    reference: "API 661 para 4.3.4"

  plug_hardness_ss:
    max: "HRB 82"
    reference: "API 661 para 4.3.4"

  bundle_lateral_movement:
    min: 6mm
    each_direction: true
    reference: "API 661 para 4.1.5"
```

---

## Test Data Available

| File | Type | Use For Testing |
|------|------|-----------------|
| M169-6A_REV5.pdf | Header Detail | BOM, welds, dimensions, API 661 |
| M180-10AF_REV0.pdf | Header | Similar validation |
| S24400-10AS_REV0.pdf | Shop Assembly | Structure, fasteners |
| CS23456-7A-SWLA_REV1.pdf | Shipping/Lifting | Weights, rigging |

---

## Blocked Tasks

### Flatter Files Integration
**Status**: BLOCKED - Awaiting API credentials
**Priority**: Low

---

## Explicitly SKIPPING

- Multi-user accounts
- OAuth/SSO
- Team collaboration
- Enterprise compliance

---

**Total Phase 25 Tasks**: 85
**Estimated Effort**: 60-80 hours
**Last Updated**: Dec 25, 2025
