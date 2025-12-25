# Project Vulcan: Active Task List

**Status**: Phase 25 - Drawing Checker System (STANDARDS COMPLETE)
**Last Updated**: Dec 25, 2025
**Overall Health**: 10/10 (Production Deployment Ready)

---

## Progress Summary

| Category | Complete | Remaining | % Done |
|----------|----------|-----------|--------|
| Phase 19-23 (Foundation) | 57/58 | 1 (blocked) | 98% |
| Phase 24 (ACHE Design Assistant) | 0/340 | 340 | 0% |
| Phase 25 (Drawing Checker) | 80/150 | 70 | 53% |
| **Standards Database** | **199/199** | **0** | **100%** |

---

## Completed Validators (199/199 checks)

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

## Phase 25 Remaining Tasks (70 tasks)

### 25.3-25.13 Implementation Tasks
- 25.3 Fabrication Feasibility (~8 tasks)
- 25.4 Welding (~6 tasks)
- 25.5 Machining/Shaft (~3 tasks)
- 25.6 Materials & Finishing (~8 tasks)
- 25.7 Hardware & Fasteners (~6 tasks)
- 25.8 Handling & Erection (~2 tasks)
- 25.9 Inspection & QC (~10 tasks)
- 25.10 Documentation (~8 tasks)
- 25.11 Safety & Code (~6 tasks)
- 25.12 Cross-Part Reference (~5 tasks)
- 25.13 Report Generation (~5 tasks)

---

## Phase 24: ACHE Design Assistant (340 tasks) - NOT STARTED

Major feature areas:
- Auto-Launch System
- Model Overview Tab
- Properties Extraction
- Analysis & Calculations
- Structural Components
- Walkways, Handrails, Ladders
- AI Features & Integration
- Field Erection Support

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

**Standards Database: 100% COMPLETE (199 checks)**

**Next Priority**: Phase 25.3-25.13 implementation tasks, then Phase 24

**Last Updated**: Dec 25, 2025
