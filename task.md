# Project Vulcan: Active Task List

**Status**: Phase 25 - Drawing Checker System (COMPLETE) | Phase 24 - NEXT
**Last Updated**: Dec 26, 2025
**Overall Health**: 10/10 (Production Deployment Ready)

---

## Progress Summary

| Category | Complete | Remaining | % Done |
|----------|----------|-----------|--------|
| Phase 19-23 (Foundation) | 57/58 | 1 (blocked) | 98% |
| Phase 24 (ACHE Design Assistant) | 0/213 | 213 | 0% |
| Phase 25 (Drawing Checker) | 150/150 | 0 | **100%** |
| **Standards Database** | **213/213** | **0** | **100%** |

---

## Completed Validators (213/213 checks)

| Validator | Checks | Status |
|-----------|--------|--------|
| `aisc_hole_validator.py` | 16 | ✅ Complete |
| `aws_d1_1_validator.py` | 14 | ✅ Complete |
| `api661_bundle_validator.py` | 32 | ✅ Complete |
| `api661_full_scope_validator.py` | 82 | ✅ **NEW - Full Scope** |
| `osha_validator.py` | 12 | ✅ Complete |
| `nema_motor_validator.py` | 5 | ✅ Complete |
| `sspc_coating_validator.py` | 6 | ✅ Complete |
| `asme_viii_validator.py` | 8 | ✅ Complete |
| `tema_validator.py` | 6 | ✅ Complete |
| `geometry_profile_validator.py` | 4 | ✅ Complete |
| `tolerance_validator.py` | 3 | ✅ Complete |
| `sheet_metal_validator.py` | 3 | ✅ Complete |
| `member_capacity_validator.py` | 2 | ✅ Complete |
| `structural_capacity_validator.py` | 6 | ✅ Complete |
| `shaft_validator.py` | - | ✅ Complete |
| `handling_validator.py` | - | ✅ Complete |
| `bom_validator.py` | - | ✅ Complete |
| `dimension_validator.py` | - | ✅ Complete |
| `gdt_validator.py` | 14 | ✅ **NEW - Full ASME Y14.5-2018** |

---

## GD&T Validator - Full ASME Y14.5-2018 Coverage (14 symbols) ✅ NEW

### Form Tolerances (No datum required)
- [x] **Flatness** - Surface deviation from perfect plane
- [x] **Straightness** - Line element or axis deviation
- [x] **Circularity** - Roundness at any cross-section
- [x] **Cylindricity** - Entire cylinder surface control

### Orientation Tolerances (Datum required)
- [x] **Perpendicularity** - 90° to datum reference
- [x] **Angularity** - Specified angle to datum
- [x] **Parallelism** - Parallel to datum surface/axis

### Location Tolerances (Datum required)
- [x] **Position** - True position with bonus tolerance (MMC/LMC)
- [x] **Concentricity** - Axis coaxiality (rarely used)
- [x] **Symmetry** - Center plane symmetry (rarely used)

### Runout Tolerances (Datum axis required)
- [x] **Circular Runout** - FIM at each circular element
- [x] **Total Runout** - FIM over entire surface

### Profile Tolerances (Datum optional)
- [x] **Profile of a Line** - 2D outline control
- [x] **Profile of a Surface** - 3D shape control

### Advanced Features
- [x] MMC/LMC/RFS material condition modifiers
- [x] Bonus tolerance calculations
- [x] Virtual/Resultant condition calculations
- [x] Feature Control Frame (FCF) validation
- [x] Datum reference frame validation
- [x] Composite position tolerancing (PLTZF/FRTZF)
- [x] Process capability validation

---

## API 661 Full-Scope Coverage (82 checks) ✅ NEW

### Bundle Assembly (22 checks)
- [x] Lateral movement ≥6mm both directions OR ≥12.7mm one direction
- [x] Tube support spacing ≤1.83m (6 ft)
- [x] Tube keeper BOLTED (not welded) at each support
- [x] Air seals/P-strips throughout bundle
- [x] Condenser tube slope ≥10 mm/m (single-pass: all tubes, multi-pass: last pass)
- [x] Min tube OD ≥25.4mm, wall thickness per Table 5
- [x] Fin specs: gap ≥6.35mm, OD tol ±1mm, density ≤3%

### Header Box Design (18 checks)
- [x] **Split header REQUIRED when ΔT > 110°C (200°F)** per 7.1.6.1.2
- [x] Restraint relief calculations required regardless of ΔT
- [x] Header types: Plug (any P), Cover plate (<435 psi), Bonnet (prohibited S-710)
- [x] Design codes: ASME VIII App 13, WRC 107/297, FEA
- [x] Cover plate NOT allowed >435 psig
- [x] Through-bolts min Ø20mm, jackscrews required

### Plug Requirements (8 checks)
- [x] Shoulder type with straight-threaded shank
- [x] NO hollow plugs (7.1.7.2)
- [x] Hexagonal head, size ≥shoulder Ø
- [x] Spacing per Table 2

### Nozzle Requirements (12 checks)
- [x] Prohibited sizes: DN 32, 65, 90, 125, <20
- [x] Min size DN 20, flanged if ≥DN 40
- [x] H2 service: ALL connections flanged
- [x] NO threaded nozzles (IOGP S-710)
- [x] Nozzle loads per Table 4 (forces/moments by size)

### Tube-to-Tubesheet Joints (8 checks)
- [x] Joint types: Expanded only, Seal welded, Strength welded
- [x] Two grooves, 3mm wide per IOGP S-710
- [x] Expansion full tubesheet thickness
- [x] Strength weld qual per ASME IX QW-193

### Fan System (10 checks)
- [x] Tip clearance per Table 6 (by fan diameter)
- [x] Min coverage 40%, max dispersion 45°
- [x] 10% airflow reserve at rated speed
- [x] Guard mesh: ≤1.8m: 1.5mm, >1.8m: 2.0mm

### Drive System (4 checks)
- [x] Motor bearing L10 ≥40,000 hrs
- [x] Shaft bearing L10 ≥50,000 hrs
- [x] Belt SF: V-belt ≥1.4, HTD 1.8-2.0
- [x] Gear drive REQUIRED if >45kW

---

## Phase 25 Validators - ALL COMPLETE ✅

### 25.3-25.13 Implementation Status

| Phase | Validator | Lines | Endpoint | Status |
|-------|-----------|-------|----------|--------|
| 25.3 | `fabrication_feasibility_validator.py` | 713 | `/phase25/check-fabrication` | ✅ |
| 25.4 | `aws_d1_1_validator.py` | 300+ | `/phase25/check-weld` | ✅ |
| 25.5 | `shaft_validator.py` | 400+ | `/phase25/check-shaft` | ✅ |
| 25.6 | `materials_finishing_validator.py` | 552 | `/phase25/check-materials` | ✅ |
| 25.7 | `fastener_validator.py` | 565 | `/phase25/check-fasteners` | ✅ |
| 25.8 | `rigging_validator.py` | 558 | `/phase25/check-rigging` | ✅ |
| 25.9 | `inspection_qc_validator.py` | 609 | `/phase25/check-inspection` | ✅ |
| 25.10 | `documentation_validator.py` | 672 | `/phase25/check-documentation` | ✅ |
| 25.11 | `osha_validator.py` | 400+ | `/phase25/check-osha` | ✅ |
| 25.12 | `cross_part_validator.py` | 611 | `/phase25/check-cross-part` | ✅ |
| 25.13 | `report_generator.py` | 612 | `/phase25/generate-report` | ✅ |

**Total: 36 validator files, 29 API endpoints, 4,892+ lines of validation logic**

---

## Phase 24: ACHE Design Assistant (213 tasks) - IN PROGRESS

See full PRD: `docs/prds/PRD-024-ACHE-DESIGN-ASSISTANT.md`

### Phase 24.1 - Auto-Launch System (8 tasks)
- [ ] 24.1.1 SolidWorks event listener for model open
- [ ] 24.1.2 ACHE model detection (custom property/filename)
- [ ] 24.1.3 Assistant panel auto-launch
- [ ] 24.1.4 User preference for auto-launch on/off
- [ ] 24.1.5 Integration with desktop server

### Phase 24.2 - Model Overview Tab (15 tasks)
- [ ] 24.2.1 Custom property extraction
- [ ] 24.2.2 Mass properties display
- [ ] 24.2.3 Bounding box dimensions
- [ ] 24.2.4 Configuration management
- [ ] 24.2.5 Real-time property refresh
- [ ] 24.2.6 Export to Excel/PDF

### Phase 24.3 - Properties Extraction (20 tasks)
- [ ] 24.3.1 Header box dimensions
- [ ] 24.3.2 Tube bundle parameters
- [ ] 24.3.3 Fan system parameters
- [ ] 24.3.4 Structural frame dimensions
- [ ] 24.3.5 Nozzle schedule extraction
- [ ] 24.3.6 Material takeoff (MTO)
- [ ] 24.3.7 Weight summary
- [ ] 24.3.8 Assembly hierarchy

### Phase 24.4 - Analysis & Calculations (25 tasks)
- [ ] 24.4.1 Thermal performance (API 661)
- [ ] 24.4.2 Pressure drop calculations
- [ ] 24.4.3 Tube bundle weight
- [ ] 24.4.4 Fan power consumption
- [ ] 24.4.5 Integration with Phase 25 validators
- [ ] 24.4.6 Calculation report generation

### Phase 24.5 - Structural Components (40 tasks)
- [ ] 24.5.1 Column design per AISC
- [ ] 24.5.2 Beam design per AISC
- [ ] 24.5.3 Bracing system design
- [ ] 24.5.4 Base plate design
- [ ] 24.5.5 Anchor bolt layout
- [ ] 24.5.6 Wind/Seismic analysis interface
- [ ] 24.5.7 Connection design
- [ ] 24.5.8 Unity check calculations

### Phase 24.6 - Walkways, Handrails, Ladders (35 tasks)
- [ ] 24.6.1 Platform grating design
- [ ] 24.6.2 Handrail design (OSHA 1910.29)
- [ ] 24.6.3 Ladder design (OSHA 1910.23)
- [ ] 24.6.4 Cage/safety climb requirements
- [ ] 24.6.5 Toe board requirements
- [ ] 24.6.6 Maintenance access verification
- [ ] 24.6.7 Load rating verification

### Phase 24.7 - AI Features & Integration (30 tasks)
- [ ] 24.7.1 Natural language query
- [ ] 24.7.2 Design recommendations
- [ ] 24.7.3 Similar project lookup (RAG)
- [ ] 24.7.4 Chat integration
- [ ] 24.7.5 Voice command support

### Phase 24.8 - Field Erection Support (40 tasks)
- [ ] 24.8.1 Erection sequence generator
- [ ] 24.8.2 Lifting lug design (AISC DG 29)
- [ ] 24.8.3 Rigging diagram generator
- [ ] 24.8.4 Shipping split recommendations
- [ ] 24.8.5 Field weld map
- [ ] 24.8.6 Torque sequence documentation
- [ ] 24.8.7 QC checkpoint definition

---

## API Endpoints Summary

### Phase 25 Drawing Checker Endpoints

| Endpoint | Validator | Checks |
|----------|-----------|--------|
| `/phase25/check-holes` | AISC Hole | 16 |
| `/phase25/check-weld` | AWS D1.1 | 14 |
| `/phase25/check-api661-bundle` | API 661 | 32 |
| `/phase25/check-api661-full` | API 661 Full | 82 |
| `/phase25/check-osha` | OSHA | 12 |
| `/phase25/check-nema-motor` | NEMA MG-1 | 5 |
| `/phase25/check-sspc-coating` | SSPC | 6 |
| `/phase25/check-asme-viii` | ASME VIII | 8 |
| `/phase25/check-tema` | TEMA R/B/C | 6 |
| `/phase25/check-geometry` | Geometry/Profile | 4 |
| `/phase25/check-tolerances` | GD&T | 3 |
| `/phase25/check-gdt` | Full GD&T Y14.5 | 14 |
| `/phase25/check-sheet-metal` | Sheet Metal | 3 |
| `/phase25/check-member-capacity` | Structural | 2 |
| `/phase25/check-structural` | Connections | 6 |
| `/phase25/check-shaft` | Machining | - |
| `/phase25/check-handling` | Handling | - |
| `/phase25/check-bom` | BOM | - |
| `/phase25/check-dimensions` | Dimensions | - |
| `/phase25/check-completeness` | Completeness | - |

---

## Quick Reference Tables

### API 661 - Split Header Requirement (7.1.6.1.2)
| Condition | Header Configuration | Notes |
|-----------|---------------------|-------|
| ΔT ≤ 110°C (200°F) | Unified allowed | Analysis still required |
| **ΔT > 110°C (200°F)** | **Split REQUIRED** | U-tube or strain relief |

### API 661 - Condenser Tube Slope (7.1.1.6/7)
| Configuration | Requirement |
|---------------|-------------|
| Single-pass | ALL tubes slope ≥10 mm/m toward outlet |
| Multi-pass | LAST PASS only slopes ≥10 mm/m |

### API 661 - Header Type Selection
| Condition | Header Type | Reference |
|-----------|-------------|-----------|
| P ≥ 435 psi or H2 | Plug (required) | 7.1.6, S-710 |
| P < 435 psi, fouling | Cover plate | 7.1.6 |
| Removable bonnet | **NOT ALLOWED** | IOGP S-710 |

### API 661 - Fan Tip Clearance (Table 6)
| Fan Dia | Min | Max |
|---------|-----|-----|
| ≤3m (10 ft) | 6.35mm | 12.7mm |
| 3-3.5m (10-11.5 ft) | 6.35mm | 15.9mm |
| >3.5m (11.5 ft) | 6.35mm | 19.05mm |

### API 661 - Nozzle Loads (Table 4 excerpt)
| Size | Fx (N) | Fy (N) | Fz (N) | Mx (N·m) | My (N·m) | Mz (N·m) |
|------|--------|--------|--------|----------|----------|----------|
| DN 50 | 1800 | 900 | 1350 | 1350 | 2050 | 1350 |
| DN 100 | 3600 | 1800 | 2700 | 4050 | 5400 | 4050 |
| DN 150 | 5400 | 2700 | 4050 | 8100 | 10800 | 8100 |

### API 661 - Bearing Life Requirements
| Component | L10 Life (hrs) | Standard |
|-----------|----------------|----------|
| Motor bearings | ≥40,000 | ISO 281 |
| Shaft bearings | ≥50,000 | ISO 76 |

### API 661 - Fin Types & Temperature Limits
| Type | Max Temp | Application |
|------|----------|-------------|
| L-footed | ~175°C (350°F) | Standard service |
| LL (overlapped) | ~175°C | Corrosive atmosphere |
| KL (knurled) | ~230°C | Higher temp, better bond |
| Embedded | ~400°C (750°F) | High temp, cyclic |
| Extruded | ~315°C (600°F) | High temp, corrosive |

### AISC J3.3 - Hole Dimensions
| Bolt | Std | Oversized | Short-Slot | Long-Slot |
|------|-----|-----------|------------|-----------|
| 3/4" | 13/16" | 15/16" | 13/16"×1" | 13/16"×1-7/8" |
| 7/8" | 15/16" | 1-1/16" | 15/16"×1-1/8" | 15/16"×2-3/16" |
| 1" | 1-1/8" | 1-1/4" | 1-1/8"×1-5/16" | 1-1/8"×2-1/2" |

### AWS D1.1 - Min Fillet Size
| Thickness | Min Fillet |
|-----------|------------|
| ≤1/4" | 1/8" |
| 1/4"-1/2" | 3/16" |
| 1/2"-3/4" | 1/4" |
| >3/4" | 5/16" |

### OSHA Ladder (2018 Final Rule)
| Parameter | Requirement |
|-----------|-------------|
| Fall protection trigger | >24 ft (not 20 ft) |
| New installs after 11/19/2018 | PFAS or LAD only (no cages) |
| All ladders by 11/18/2036 | Must have PFAS/LAD |

### ASME VIII - Wall Thickness (UG-27)
| Material | Max Allowable Stress (psi) at 650°F |
|----------|-------------------------------------|
| SA-516-70 | 17,500 |
| SA-516-60 | 15,000 |
| SA-240-304 | 15,600 |
| SA-240-316 | 16,300 |

### TEMA Tubesheet Thickness Factor
| Class | Factor × Tube OD |
|-------|------------------|
| R (Petroleum) | 0.75 |
| C (Commercial) | 0.625 |
| B (Chemical) | 0.50 |

### Sheet Metal K-Factors
| Bend Method | K-Factor |
|-------------|----------|
| Air Bend | 0.33 |
| Bottoming | 0.42 |
| Coining | 0.50 |

### Deflection Limits
| Application | Limit |
|-------------|-------|
| Floor Live Load | L/360 |
| Floor Total | L/240 |
| Roof Live | L/240 |
| Equipment Support | L/600 |
| Crane Runway | L/600 |

---

## Standards Files

| File | Location | Content |
|------|----------|---------|
| `api661_full_scope.md` | `/standards/` | 82 validator checks, complete API 661 |
| `ache_header_tube_configurations.svg` | `/diagrams/` | Split headers, tube slope, header types |

---

**Standards Database: 100% COMPLETE (213 checks)**

**Next Priority**: Phase 24.1 (Auto-Launch System) - 8 tasks

**Last Updated**: Dec 26, 2025
