# Project Vulcan: Active Task List

**Status**: Phase 25 - Drawing Checker System (IN PROGRESS)
**Last Updated**: Dec 25, 2025
**Overall Health**: 9.9/10 (Production Deployment Ready)

**Use Case**: Personal AI assistant for engineering projects at work
- CAD model validation and design checking (130+ validators active)
- Trading analysis and journal keeping
- Work automation and productivity
- Learning loop to improve over time (LIVE)
- **NEW**: Comprehensive Drawing Checker System (150+ checks)
- **NEW**: Complete ACHE Standards Database (117 checks across 8 standards)
- Auto-launch chatbot when SolidWorks opens with full model overview

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
| **Phase 25 (Drawing Checker)** | **68/150** | **82** | **45%** |
| **Phase 26 (Standards Database)** | **91/117** | **26** | **78%** |

**Current Focus**: Phase 25 - Drawing Checker System 🚧

---

## Complete ACHE Standards Database ⭐ NEW - Dec 25, 2025

**Purpose**: Comprehensive standards reference for Air-Cooled Heat Exchanger drawing validation. Covers ALL applicable codes across structural, pressure vessel, mechanical, electrical, safety, and coating disciplines.

---

### Master Standards Matrix

| Category | Primary Standard | Supporting Standards | Application |
|----------|-----------------|---------------------|-------------|
| **ACHE Design** | API 661 / ISO 13706 | IOGP S-710 | Overall ACHE requirements |
| **Pressure Vessel** | ASME VIII Div 1 | ASME VIII Div 2, Appendix 13 | Header box, nozzles |
| **Heat Exchanger** | TEMA (Class R/B/C) | API 660 | Tube bundle, tubesheet |
| **Structural Steel** | AISC 360 | AISC Steel Manual | Structure, connections |
| **Structural Welding** | AWS D1.1 | AWS D1.3 (sheet steel) | Structural welds |
| **Pressure Welding** | ASME IX | - | Pressure part welds |
| **Bolted Connections** | AISC J3, RCSC | ASTM A325, F436 | All bolted joints |
| **Safety - Fall Protection** | OSHA 1910.28/29 | - | Guardrails, platforms |
| **Safety - Ladders** | OSHA 1910.23 | ANSI A14.3 | Fixed ladders |
| **Safety - Stairs** | OSHA 1910.25 | - | Stairways |
| **Surface Prep** | SSPC-SP | ISO 8501 | Coating preparation |
| **Coating** | SSPC-PA | Owner spec | Paint systems |
| **Motors** | NEMA MG-1 | IEC 60072 | Motor dimensions |
| **Bearings** | ISO 281, ISO 76 | Manufacturer catalog | L10 life, mounting |
| **V-Belts** | ISO 4184 | - | Belt drives |
| **Fans** | AMCA | API 661 Table 6 | Fan performance |
| **Noise** | ISO 3744 | - | Sound measurement |
| **Vibration** | ISO 10816 | API 661 | Vibration limits |

---

### AISC 360 - Bolted Connections (Chapter J)

#### Table J3.3 - Nominal Hole Dimensions (inch)
| Bolt Ø | Standard | Oversized | Short-Slot (W×L) | Long-Slot (W×L) |
|--------|----------|-----------|------------------|-----------------|
| 1/2" | 9/16" | 5/8" | 9/16" × 11/16" | 9/16" × 1-1/4" |
| 5/8" | 11/16" | 13/16" | 11/16" × 7/8" | 11/16" × 1-9/16" |
| **3/4"** | **13/16"** | **15/16"** | **13/16" × 1"** | **13/16" × 1-7/8"** |
| 7/8" | 15/16" | 1-1/16" | 15/16" × 1-1/8" | 15/16" × 2-3/16" |
| 1" | 1-1/8" | 1-1/4" | 1-1/8" × 1-5/16" | 1-1/8" × 2-1/2" |
| ≥1-1/8" | d + 1/8" | d + 5/16" | (d+1/16) × (d+3/8) | (d+1/16) × 2.5d |

#### Table J3.4 - Minimum Edge Distance (Standard Holes)
| Bolt Ø | Sheared Edge | Rolled/Gas Cut Edge |
|--------|--------------|---------------------|
| 1/2" | 3/4" | 7/8" |
| 5/8" | 7/8" | 1-1/8" |
| **3/4"** | **1"** | **1-1/4"** |
| 7/8" | 1-1/8" | 1-1/2" |
| 1" | 1-1/4" | 1-3/4" |
| 1-1/8" | 1-1/2" | 2" |
| 1-1/4" | 1-5/8" | 2-1/4" |
| ≥1-1/4" | 1.25d | 1.75d |

#### Table J3.5 - Edge Distance Increment (C₂) for Slotted/Oversized
| Bolt Ø | Oversized | Short ⊥ | Short ∥ | Long ⊥ | Long ∥ |
|--------|-----------|---------|---------|--------|--------|
| ≤7/8" | 1/16" | 0 | 1/8" | 1/8" | 0.75d |
| 1" | 1/8" | 0 | 1/8" | 0 | 0.75d |
| ≥1-1/8" | 1/8" | 0 | 1/8" | 0 | 0.75d |

#### Spacing Requirements (J3.3-J3.5)
| Parameter | Requirement | Notes |
|-----------|-------------|-------|
| Minimum spacing | 2.67d | Preferred 3d |
| Maximum spacing (painted) | min(12t, 6") | t = thinner ply |
| Maximum spacing (unpainted) | min(14t, 7") | Corrosive environment |

#### Bearing & Tearout (J3.10, J3.11)
| Parameter | Formula | Notes |
|-----------|---------|-------|
| Clear distance Lc | Le - d_hole/2 | Edge bolts |
| | s - d_hole | Interior bolts |
| Bearing (deform is concern) | Rn = 2.4dtFu | When Lc ≥ 2d |
| Tearout | Rn = 1.2LctFu | When Lc < 2d |
| Block shear net area | Use d_hole + 1/8" | Per B4.3b |

---

### AWS D1.1 - Structural Welding

#### Minimum Fillet Weld Size (Table 5.8)
| Base Metal Thickness | Min Fillet Size |
|---------------------|-----------------|
| t ≤ 1/4" | 1/8" |
| 1/4" < t ≤ 1/2" | 3/16" |
| 1/2" < t ≤ 3/4" | 1/4" |
| t > 3/4" | 5/16" |

#### Maximum Fillet Weld Size (Table 2.1)
| Edge Condition | Max Fillet Size |
|----------------|-----------------|
| t < 1/4" | = t |
| t ≥ 1/4" | t - 1/16" |

#### Preheat Requirements (Table 5.11)
| Category | Thickness | Min Preheat |
|----------|-----------|-------------|
| A (A36, A572-50) | ≤3/4" | None |
| | 3/4" - 1-1/2" | 50°F |
| | 1-1/2" - 2-1/2" | 150°F |
| | > 2-1/2" | 225°F |

---

### API 661 - Air-Cooled Heat Exchangers

#### Fan Tip Clearance (Table 6)
| Fan Diameter | Min Clearance | Max Clearance |
|--------------|---------------|---------------|
| ≤ 3 m (10 ft) | 6.35 mm (1/4") | 12.7 mm (1/2") |
| 3 - 3.5 m | 6.35 mm (1/4") | 15.9 mm (5/8") |
| > 3.5 m | 6.35 mm (1/4") | 19.05 mm (3/4") |

#### Tube Bundle Requirements
| Parameter | Requirement |
|-----------|-------------|
| Lateral movement | 6mm (1/4") both directions OR 12.7mm (1/2") one direction |
| Tube support spacing | ≤ 1.83 m (6 ft) center-to-center |
| Tube keeper | At each tube support, bolted to side frame |
| Condenser tube slope | ≥ 10 mm/m (1/8 in/ft) toward outlet |
| Min tube OD | 25.4 mm (1 in) |

#### Header Type Selection
| Design Pressure | Recommended Header Type |
|-----------------|------------------------|
| < 435 psi (3 MPa) | Plug, Cover Plate, or Bonnet |
| ≥ 435 psi OR H2 service | Plug type only |

#### Motor & Drive Requirements
| Parameter | Requirement |
|-----------|-------------|
| Motor type | 3-phase, TEFC |
| Temperature rise | 80°C over 40°C ambient |
| Bearing L10 life | ≥ 40,000 hours |
| V-belt drive max | 30 kW (40 HP), SF ≥ 1.4 |
| HTD belt drive max | 45 kW (60 HP), SF 1.8-2.0 |
| Gear drive | Required > 45 kW (60 HP) |
| Shaft bearing L10 | 50,000 hours per ISO 281/ISO 76 |

---

### API 661 - Tube Bundle Assembly (Section 7.1) ⭐ NEW

#### Bundle Component Reference (per API 661 Figures 3 & 5)

| Item # | Component | Description |
|--------|-----------|-------------|
| 1 | **Tubesheet** | Tube attachment plate at each end |
| 2 | **Plug sheet** | Access plate with threaded plugs (plug headers only) |
| 3 | **Top/bottom plates** | Header box closure plates |
| 4 | **End plate** | Header box end closure |
| 5 | **Tubes** | Finned tubes (process fluid side) |
| 6 | **Pass partition** | Divides header into flow passes |
| 7 | **Stiffener** | Reinforces header plates |
| 8 | **Plug** | Shoulder-type access plug for tube cleaning |
| 9 | **Nozzle** | Process inlet/outlet connections |
| 10 | **Side frame** | Main structural member at bundle edges |
| 11 | **Tube spacer** | Maintains tube position without fin damage |
| 12 | **Tube support cross-member** | Supports tubes between side frames |
| 13 | **Tube keeper** | Hold-down member preventing tube lift |
| 14 | **Vent** | Air/gas release connection |
| 15 | **Drain** | Liquid drainage connection |
| 16 | **Instrument connection** | Thermowell, pressure gauge, etc. |

#### Bundle Frame Requirements (7.1.1)

| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Lateral movement | ≥ 6 mm (1/4") both directions OR ≥ 12.7 mm (1/2") one direction | 7.1.1.2 |
| Tube support spacing | ≤ 1.83 m (6 ft) center-to-center | 7.1.1.4 |
| Tube keeper location | At each tube support | 7.1.1.5 |
| Tube keeper attachment | **Bolted** to side frames (NOT welded) | 7.1.1.5 |
| **Air seals / P-strips** | Throughout bundle AND bay to minimize leakage/bypassing | 7.1.1.8 |

#### Air Seal Requirements (7.1.1.8) ⭐ CRITICAL

| Parameter | Requirement |
|-----------|-------------|
| Coverage | Throughout tube bundle AND bay |
| Function | Minimize air leakage and bypassing |
| Types | P-strips, sealing strips, flexible seals |
| Location | Bundle perimeter, between bundles, at plenum interface |

#### Header Types

| Type | Description | Max Pressure | Application |
|------|-------------|--------------|-------------|
| **Plug header** | Threaded plugs opposite each tube | Any (required ≥435 psi or H2) | Highest pressure |
| **Cover plate header** | Removable bolted cover plate | < 435 psi (3 MPa) | Easy cleaning access |
| **Bonnet header** | Removable dished/flanged bonnet | < 435 psi (3 MPa) | Full tube access |

#### Plug Requirements (7.1.7)

| Parameter | Requirement |
|-----------|-------------|
| Type | Shoulder type with straight-threaded shank |
| Hollow plugs | **NOT allowed** |
| Head type | Hexagonal |
| Length | Fill plug sheet threads ± 1.5 mm (1/16") |

#### Prohibited Nozzle Sizes (7.1.9.5)

| DN (NPS) | Status |
|----------|--------|
| DN 32 (1-1/4") | ❌ PROHIBITED |
| DN 65 (2-1/2") | ❌ PROHIBITED |
| DN 90 (3-1/2") | ❌ PROHIBITED |
| DN 125 (5") | ❌ PROHIBITED |

**Flanged requirement**: DN 40 (1-1/2") and larger must be flanged

#### Condenser Tube Slope

| Service | Slope Requirement |
|---------|-------------------|
| Single-pass condenser | ≥ 10 mm/m (1/8 in/ft) toward outlet |
| Multi-pass (last pass) | ≥ 10 mm/m (1/8 in/ft) toward outlet |

#### Bundle Assembly Validator Checklist ⭐ NEW (22 checks)

| # | Check | Reference | Status |
|---|-------|-----------|--------|
| 1 | Tube support spacing ≤ 6 ft | 7.1.1.4 | ❌ MISSING |
| 2 | Tube keeper at each support | 7.1.1.5 | ❌ MISSING |
| 3 | Tube keeper bolted (not welded) | 7.1.1.5 | ❌ MISSING |
| 4 | Air seals / P-strips specified | 7.1.1.8 | ❌ MISSING |
| 5 | Lateral movement provision | 7.1.1.2 | ❌ MISSING |
| 6 | Condenser tube slope (single-pass) | 7.1.1.6 | ❌ MISSING |
| 7 | Condenser tube slope (multi-pass last) | 7.1.1.7 | ❌ MISSING |
| 8 | Header type vs pressure | 7.1.6 | ❌ MISSING |
| 9 | Plug type (shoulder, hex head) | 7.1.7 | ❌ MISSING |
| 10 | No hollow plugs | 7.1.7.2 | ❌ MISSING |
| 11 | Plug hole thread depth | 7.1.6.3.1 | ❌ MISSING |
| 12 | Nozzle size not prohibited | 7.1.9.5 | ❌ MISSING |
| 13 | Nozzle ≥DN40 flanged | 7.1.9.5 | ❌ MISSING |
| 14 | Min nozzle neck thickness | Table 3 | ❌ MISSING |
| 15 | Thermowell location correct | 7.1.9.13 | ❌ MISSING |
| 16 | Pressure gauge location correct | 7.1.9.14 | ❌ MISSING |
| 17 | Vent at header high point | 7.1.9 | ❌ MISSING |
| 18 | Drain at header low point | 7.1.9 | ❌ MISSING |
| 19 | Fin end securing specified | 7.1.2 | ❌ MISSING |
| 20 | Tubesheet groove location | 7.1.x | ❌ MISSING |
| 21 | Pass partition integral plate | - | ❌ MISSING |
| 22 | SS/alloy tube spacer compatibility | IOGP S-710 | ❌ MISSING |

---

### OSHA - Safety Requirements

#### Fall Protection (1910.28, 1910.29)
| Parameter | Requirement |
|-----------|-------------|
| Trigger height | 4 feet (1.2 m) |
| Top rail height | 42" ± 3" |
| Mid rail height | ~21" (halfway) |
| Toe board height | ≥ 3.5" |
| Opening spacing | ≤ 19" |
| Rail load capacity | 200 lbs top rail |

#### Fixed Ladders (1910.23, 1910.28)
| Parameter | Requirement |
|-----------|-------------|
| Clear width | ≥ 16" (fixed), ≥ 11.5" (portable) |
| Rung spacing | 10-14" uniform |
| Offset from wall | 7" minimum |
| Side rail extension | 42" above landing |
| **Fall protection trigger** | **> 24 ft** (per 1910.28(b)(9)) |
| Cage start height | 7-8 ft from base |
| Cage top extension | 42" above top landing |
| **Landing platforms (with cage)** | **Every 50 ft** |
| **Rest platforms (with PFAS)** | **Every 150 ft** |

#### Fixed Ladder Fall Protection Requirements (1910.28(b)(9))
| Installation Date | Height > 24 ft | Acceptable Protection |
|-------------------|----------------|----------------------|
| Before Nov 19, 2018 | Yes | Cage, well, PFAS, or ladder safety system |
| **After Nov 19, 2018** | Yes | **PFAS or ladder safety system ONLY** (cages NOT compliant) |
| Any (by Nov 18, 2036) | Yes | **All ladders must have PFAS or ladder safety system** |

**Note**: Cages are being phased out. New installations after Nov 2018 cannot use cages alone as fall protection.

#### Stairs (1910.25)
| Parameter | Requirement |
|-----------|-------------|
| Angle | 30-50° |
| Tread depth | ≥ 9.5" |
| Riser height | ≤ 9.5", uniform ± 3/16" |
| Stair width | ≥ 22" |
| Stair rail height | 30-37" (36-38" combined) |
| Landing | Every 12 ft vertical |

---

### NEMA MG-1 - Motor Frame Dimensions

#### Common Frame Dimensions
| Frame | D (shaft ht) | 2E (foot holes) | 2F (foot holes) | U (shaft Ø) |
|-------|-------------|-----------------|-----------------|-------------|
| 143T | 3.5" | 4.0" | 4.0" | 7/8" |
| 145T | 3.5" | 4.0" | 5.0" | 7/8" |
| 182T | 4.5" | 4.5" | 4.5" | 1-1/8" |
| 184T | 4.5" | 4.5" | 5.5" | 1-1/8" |
| 213T | 5.25" | 5.5" | 5.5" | 1-3/8" |
| 215T | 5.25" | 5.5" | 7.0" | 1-3/8" |
| 254T | 6.25" | 6.25" | 8.0" | 1-5/8" |
| 256T | 6.25" | 6.25" | 10.0" | 1-5/8" |
| 284T | 7.0" | 7.0" | 9.5" | 1-7/8" |
| 286T | 7.0" | 7.0" | 11.0" | 1-7/8" |
| 324T | 8.0" | 8.0" | 10.5" | 2-1/8" |
| 326T | 8.0" | 8.0" | 12.0" | 2-1/8" |

#### Frame Size Decoding
- 2-digit frames: Shaft height (D) = Frame ÷ 16 (e.g., 56 → 3.5")
- 3-digit frames: Shaft height (D) = First 2 digits ÷ 4 (e.g., 324T → 8")

---

### SSPC - Surface Preparation Standards

#### Blast Cleaning Standards
| Standard | Name | Cleanliness | Staining Allowed |
|----------|------|-------------|------------------|
| SSPC-SP5 / NACE 1 | White Metal | 100% clean | 0% |
| SSPC-SP10 / NACE 2 | Near-White | 95% clean | 5% |
| SSPC-SP6 / NACE 3 | Commercial | 67% clean | 33% |
| SSPC-SP7 / NACE 4 | Brush-Off | Loose removed | Tight adherent OK |
| SSPC-SP14 / NACE 8 | Industrial | 90% clean | 10% |

#### Power Tool Cleaning
| Standard | Name | Result |
|----------|------|--------|
| SSPC-SP2 | Hand Tool | Remove loose only |
| SSPC-SP3 | Power Tool | Remove loose only |
| SSPC-SP11 | Power Tool to Bare Metal | Remove ALL, 1 mil profile |

#### Pre-requisite
- **SSPC-SP1** (Solvent Cleaning) is required BEFORE any blast cleaning

---

### TEMA - Heat Exchanger Classes

| Class | Application | Construction |
|-------|-------------|--------------|
| R | Petroleum/petrochemical | Heaviest, most conservative |
| C | Commercial/general | Moderate |
| B | Chemical process | Allows lighter construction |

---

### Complete Validator Checklist by Standard

#### AISC 360 Checks (16 total)
| # | Check | Reference | Current Status |
|---|-------|-----------|----------------|
| 1 | Hole type classification (std/oversized/short-slot/long-slot) | J3.3 | ❌ MISSING |
| 2 | Standard hole size | J3.3 | ✅ aisc_hole_validator.py |
| 3 | Oversized hole size | J3.3 | ❌ MISSING |
| 4 | Short-slot dimensions (width × length) | J3.3 | ❌ MISSING |
| 5 | Long-slot dimensions (width × length) | J3.3 | ❌ MISSING |
| 6 | Edge distance - sheared edge | J3.4 | ✅ aisc_hole_validator.py |
| 7 | Edge distance - rolled/thermally cut edge | J3.4 | ✅ aisc_hole_validator.py |
| 8 | C₂ increment for slotted/oversized holes | J3.5 | ❌ MISSING |
| 9 | Min spacing (2.67d) | J3.3 | ✅ aisc_hole_validator.py |
| 10 | Preferred spacing (3d) noted | J3.3 | ✅ aisc_hole_validator.py |
| 11 | Max spacing (12t or 6") | J3.5 | ❌ MISSING |
| 12 | Clear distance Lc calculation | J3.10 | ❌ MISSING |
| 13 | Bearing capacity check | J3.10 | ✅ structural_capacity_validator.py |
| 14 | Tearout capacity check | J3.10 | ❌ MISSING |
| 15 | Block shear (net area with hole + 1/8") | J4.3 | ✅ structural_capacity_validator.py (net section) |
| 16 | Slot orientation vs load direction | J3.3 | ❌ MISSING |

#### AWS D1.1 Checks (8 total)
| # | Check | Reference | Current Status |
|---|-------|-----------|----------------|
| 1 | Min fillet weld size vs thickness | Table 5.8 | ✅ structural_capacity_validator.py |
| 2 | Max fillet weld size at edge | Table 2.1 | ✅ structural_capacity_validator.py |
| 3 | Weld code referenced | - | ✅ Have |
| 4 | Prequalified joint details | Figs 5.1-5.5 | ❌ MISSING |
| 5 | Matching filler metal | Table 5.4 | ❌ MISSING |
| 6 | Preheat requirements | Table 5.11 | ❌ MISSING |
| 7 | Interpass temperature | 5.6 | ❌ MISSING |
| 8 | WPS/PQR requirements noted | - | ❌ MISSING |

#### API 661 Checks (32 total) ⭐ EXPANDED
| # | Check | Reference | Current Status |
|---|-------|-----------|----------------|
| 1 | Fan tip clearance | Table 6 | ❌ MISSING |
| 2 | Tube support spacing ≤ 6 ft | 7.1.1.4 | ❌ MISSING |
| 3 | Tube keeper bolted | 7.1.1.5 | ❌ MISSING |
| 4 | Bundle lateral movement | 7.1.1.2 | ❌ MISSING |
| 5 | Condenser tube slope | 7.1.1.6 | ❌ MISSING |
| 6 | Header type vs pressure | 7.1.6 | ❌ MISSING |
| 7 | Motor bearing L10 ≥ 40,000 hrs | 7.2.4.1 | ❌ MISSING |
| 8 | Shaft bearing L10 ≥ 50,000 hrs | 7.2.5 | ❌ MISSING |
| 9 | Belt drive service factor | 7.2.4.5 | ❌ MISSING |
| 10 | Nozzle size (≥DN40 flanged) | 7.1.9.5 | ❌ MISSING |
| 11 | Air seals / P-strips specified | 7.1.1.8 | ❌ MISSING |
| 12 | Tube keeper at each support | 7.1.1.5 | ❌ MISSING |
| 13 | Plug type (shoulder, hex head) | 7.1.7 | ❌ MISSING |
| 14 | No hollow plugs | 7.1.7.2 | ❌ MISSING |
| 15 | Plug hole thread depth | 7.1.6.3.1 | ❌ MISSING |
| 16 | Nozzle size not prohibited | 7.1.9.5 | ❌ MISSING |
| 17 | Min nozzle neck thickness | Table 3 | ❌ MISSING |
| 18 | Thermowell location correct | 7.1.9.13 | ❌ MISSING |
| 19 | Pressure gauge location correct | 7.1.9.14 | ❌ MISSING |
| 20 | Vent at header high point | 7.1.9 | ❌ MISSING |
| 21 | Drain at header low point | 7.1.9 | ❌ MISSING |
| 22 | Fin end securing specified | 7.1.2 | ❌ MISSING |
| 23 | Tubesheet groove location | 7.1.x | ❌ MISSING |
| 24 | Pass partition integral plate | - | ❌ MISSING |
| 25 | SS/alloy tube spacer compatibility | IOGP S-710 | ❌ MISSING |
| 26-32 | (Reserved for additional bundle checks) | - | ❌ MISSING |

#### OSHA Checks (12 total) ⭐ UPDATED
| # | Check | Reference | Current Status |
|---|-------|-----------|----------------|
| 1 | Guardrail height 42" ± 3" | 1910.29(b) | ❌ MISSING |
| 2 | Mid rail present | 1910.29(b) | ❌ MISSING |
| 3 | Toe board ≥ 3.5" | 1910.29(b) | ❌ MISSING |
| 4 | Opening ≤ 19" | 1910.29(b) | ❌ MISSING |
| 5 | Ladder width ≥ 16" | 1910.23(b) | ❌ MISSING |
| 6 | Rung spacing uniform 10-14" | 1910.23(b) | ❌ MISSING |
| 7 | Side rail extension 42" | 1910.23(d) | ❌ MISSING |
| 8 | **Fall protection required (>24 ft)** | **1910.28(b)(9)** | ❌ MISSING |
| 9 | **Cage vs PFAS based on install date** | **1910.28(b)(9)** | ❌ MISSING |
| 10 | **Landing platforms every 50 ft (cage)** | **1910.28(b)(9)(iii)** | ❌ MISSING |
| 11 | Self-closing gate at ladder | 1910.29(b) | ❌ MISSING |
| 12 | Platform min 24"×30" | 1910.29(g) | ❌ MISSING |

#### NEMA Checks (5 total)
| # | Check | Reference | Current Status |
|---|-------|-----------|----------------|
| 1 | Frame size decode | MG-1 | ❌ MISSING |
| 2 | Shaft height (D) verification | MG-1 | ❌ MISSING |
| 3 | Foot hole pattern | MG-1 | ❌ MISSING |
| 4 | Shaft diameter (U) | MG-1 | ❌ MISSING |
| 5 | Cross-verify motor to mount | - | ❌ MISSING |

#### SSPC Checks (6 total)
| # | Check | Reference | Current Status |
|---|-------|-----------|----------------|
| 1 | Surface prep level specified | SP1-SP16 | ❌ MISSING |
| 2 | Profile depth requirement | VIS-1 | ❌ MISSING |
| 3 | Solvent clean pre-blast | SP1 | ❌ MISSING |
| 4 | Flash rust limits | - | ❌ MISSING |
| 5 | Time to prime limit | - | ❌ MISSING |
| 6 | DFT requirements | PA-2 | ❌ MISSING |

---

### Validator Coverage Summary

| Category | Total Checks Needed | Currently Have | Gap |
|----------|---------------------|----------------|-----|
| AISC Holes/Bolts | 16 | 8 | **8** |
| AWS Welding | 8 | 4 | **4** |
| API 661 ACHE | 32 | 0 | **32** |
| ASME VIII | 8 | 0 | **8** |
| TEMA | 6 | 0 | **6** |
| OSHA Safety | 12 | 2 | **10** |
| NEMA Motors | 5 | 0 | **5** |
| SSPC Coating | 6 | 0 | **6** |
| Shaft/Machining | 12 | 9 | **3** |
| Handling/Lifting | 12 | 10 | **2** |
| **TOTAL** | **117** | **33** | **84** |

**Current Coverage: ~28%** — New validators added Dec 25, 2025:
- `aisc_hole_validator.py` - Edge distance, spacing, cross-part alignment
- `structural_capacity_validator.py` - Bolt shear/bearing, weld capacity, net section
- `shaft_validator.py` - Tolerances, keyways (ANSI B17.1), surface finish, runout
- `handling_validator.py` - Lifting lugs, CG, shipping dimensions, rigging

---

### Python Standards Database Implementation

```python
class AISCHoleStandards:
    """AISC 360 Table J3.3, J3.4, J3.5 - Bolt Hole Requirements"""
    
    # Table J3.3 - Nominal Hole Dimensions (inches)
    HOLE_DIMENSIONS = {
        # bolt_dia: (std, oversized, short_w, short_l, long_w, long_l)
        0.500: (0.5625, 0.6250, 0.5625, 0.6875, 0.5625, 1.2500),
        0.625: (0.6875, 0.8125, 0.6875, 0.8750, 0.6875, 1.5625),
        0.750: (0.8125, 0.9375, 0.8125, 1.0000, 0.8125, 1.8750),
        0.875: (0.9375, 1.0625, 0.9375, 1.1250, 0.9375, 2.1875),
        1.000: (1.1250, 1.2500, 1.1250, 1.3125, 1.1250, 2.5000),
    }
    
    # Table J3.4 - Min Edge Distance (inches)
    EDGE_DISTANCE = {
        # bolt_dia: (sheared_edge, rolled_edge)
        0.500: (0.750, 0.875),
        0.625: (0.875, 1.125),
        0.750: (1.000, 1.250),
        0.875: (1.125, 1.500),
        1.000: (1.250, 1.750),
        1.125: (1.500, 2.000),
        1.250: (1.625, 2.250),
    }
    
    @classmethod
    def get_min_edge(cls, bolt_dia, edge_type='sheared'):
        """Get minimum edge distance per Table J3.4"""
        if bolt_dia in cls.EDGE_DISTANCE:
            idx = 0 if edge_type == 'sheared' else 1
            return cls.EDGE_DISTANCE[bolt_dia][idx]
        elif bolt_dia >= 1.25:
            return bolt_dia * (1.25 if edge_type == 'sheared' else 1.75)
        return None
    
    @classmethod
    def get_min_spacing(cls, bolt_dia):
        """Minimum spacing = 2.67d per J3.3"""
        return 2.67 * bolt_dia
    
    @classmethod
    def get_max_spacing(cls, ply_thickness, painted=True):
        """Maximum spacing per J3.5"""
        factor = 12 if painted else 14
        max_in = 6 if painted else 7
        return min(factor * ply_thickness, max_in)


class API661Standards:
    """API 661 - Air-Cooled Heat Exchanger Requirements"""
    
    # Table 6 - Fan Tip Clearance (mm)
    FAN_TIP_CLEARANCE = {
        3000: (6.35, 12.70),   # ≤3m
        3500: (6.35, 15.90),   # 3-3.5m
        9999: (6.35, 19.05),   # >3.5m
    }
    
    VBELT_MAX_KW = 30
    HTD_MAX_KW = 45
    MOTOR_BEARING_L10 = 40000
    SHAFT_BEARING_L10 = 50000
    MAX_TUBE_SUPPORT_SPACING_MM = 1830
    
    # Prohibited nozzle sizes
    PROHIBITED_NOZZLE_SIZES_DN = [32, 65, 90, 125]
    MIN_FLANGED_SIZE_DN = 40


class OSHASafetyStandards:
    """OSHA 1910 - Walking-Working Surfaces (Updated per 2018 Final Rule)"""
    
    # Guardrails (1910.29)
    TOP_RAIL_HEIGHT_MIN = 39   # inches (42 - 3)
    TOP_RAIL_HEIGHT_MAX = 45   # inches (42 + 3)
    TOE_BOARD_MIN = 3.5        # inches
    MAX_OPENING = 19           # inches
    
    # Fixed Ladders (1910.23, 1910.28)
    LADDER_WIDTH_MIN = 16      # inches
    RUNG_SPACING_MIN = 10      # inches
    RUNG_SPACING_MAX = 14      # inches
    SIDE_RAIL_EXTENSION = 42   # inches above landing
    
    # Fall Protection Trigger (1910.28(b)(9)) - UPDATED
    FALL_PROTECTION_TRIGGER = 288  # inches (24 ft) - NOT 20 ft!
    CAGE_START_HEIGHT = 84         # inches (7 ft) from base
    CAGE_TOP_EXTENSION = 42        # inches above top landing
    
    # Landing/Rest Platform Intervals
    LANDING_INTERVAL_WITH_CAGE = 600   # inches (50 ft)
    REST_INTERVAL_WITH_PFAS = 1800     # inches (150 ft)
    
    # Key Dates
    CAGE_PROHIBITION_DATE = "2018-11-19"  # Cages not compliant for new installs
    CAGE_PHASE_OUT_DATE = "2036-11-18"    # All ladders must have PFAS/safety system
```

---

### Priority Implementation Order

| Priority | Standard | Checks to Add | Impact |
|----------|----------|---------------|--------|
| 🔴 1 | API 661 - Bundle assembly | 22 checks | Core ACHE compliance |
| 🔴 2 | AISC J3 - Slotted holes | 5 checks | Prevents assembly failures |
| 🔴 3 | AISC J3.5 - Max spacing | 2 checks | Prevents corrosion issues |
| 🔴 4 | API 661 - Fan clearance | 1 check | Prevents fan damage |
| 🟡 5 | OSHA 1910.28 - Ladder fall protection | 3 checks | Safety compliance |
| 🟡 6 | OSHA 1910.29 - Guardrails | 5 checks | Safety compliance |
| 🟡 7 | AWS D1.1 - Preheat | 2 checks | Weld quality |
| 🟡 8 | SSPC - Surface prep | 3 checks | Coating durability |
| 🟢 9 | NEMA - Motor frames | 4 checks | Interchangeability |
| 🟢 10 | TEMA - Bundle specs | 3 checks | HX performance |

---

## Phase 25: Drawing Checker System 🚧

**Goal**: Comprehensive automated drawing validation system for fabrication drawings. Extract dimensions, verify against standards, check cross-part alignment, and generate professional reports.

**Reference Drawing**: S25143-4A Machinery Mount Assembly (E&C Finfans)

---

### 25.1 Geometry & Dimensions (22 tasks)

#### Holes Analysis
- [x] Hole sizes standard (drill/punch) - fractional sizes
- [x] Hole sizes standard (drill/punch) - decimal sizes
- [x] Hole sizes standard (drill/punch) - metric sizes
- [x] Edge distances vs AISC J3.4 minimum ✅ aisc_hole_validator.py
- [x] Edge distances vs material thickness rules ✅ aisc_hole_validator.py
- [x] Hole spacing/pitch (min 2.67d per AISC) ✅ aisc_hole_validator.py
- [x] Hole-to-hole alignment (same part) ✅ aisc_hole_validator.py
- [x] **Cross-part hole alignment** (mating parts) ⭐ ✅ aisc_hole_validator.py
- [ ] Slot length-to-width ratio verification
- [ ] Slotted hole orientation vs load direction
- [ ] Oversized hole callout verification

#### Profiles & Cutouts
- [ ] Inside corner radii (min for plasma/laser)
- [ ] Cope dimensions adequate for weld access
- [ ] Notch stress concentration check
- [ ] Minimum web openings for tooling

#### Tolerances
- [x] Linear tolerances achievable
- [x] Angular tolerances achievable
- [ ] Flatness requirements specified
- [ ] Squareness requirements specified
- [ ] Parallelism requirements specified

#### Bends (Sheet Metal)
- [x] Bend radii vs thickness (min 1×t for steel)
- [ ] Bend allowance/K-factor verification
- [ ] Grain direction specification
- [ ] Springback consideration

---

### 25.2 Structural Adequacy (10 tasks)

- [x] Net section at holes (reduced area) ✅ structural_capacity_validator.py
- [x] Bolt bearing capacity check ✅ structural_capacity_validator.py
- [x] Bolt shear capacity check ✅ structural_capacity_validator.py
- [x] Weld size adequate for load ✅ structural_capacity_validator.py
- [ ] Member capacity verification (channels, angles)
- [ ] Connection capacity check
- [ ] Block shear verification at hole groups
- [ ] Deflection limits specified
- [ ] Vibration/resonance consideration (rotating equip)
- [ ] Fatigue consideration (cyclic loading)

---

### 25.3-25.13 (Remaining sections)

See original task.md for complete Phase 25 task breakdown covering:
- 25.3 Fabrication Feasibility
- 25.4 Welding
- 25.5 Machining/Shaft Analysis
- 25.6 Materials & Finishing
- 25.7 Hardware & Fasteners
- 25.8 Handling & Erection
- 25.9 Inspection & QC
- 25.10 Documentation
- 25.11 Safety & Code
- 25.12 Cross-Part Reference Analysis
- 25.13 Report Generation

---

## Phase 24: ACHE Design Assistant (340 tasks)

See original task.md for complete Phase 24 task breakdown covering:
- Auto-Launch System
- Model Overview Tab
- Properties Extraction
- Analysis & Calculations
- Structural Components (Plenum, Drive Support, Fan System, etc.)
- Walkways, Handrails, Ladders, Stairs
- Structure & Support
- Enclosures & Winterization
- AI Features & Integration
- Fastener Analysis
- Connection Details
- Field Erection Support

---

**Total Tasks**: 607 (340 ACHE + 150 Drawing Checker + 117 Standards)
**Estimated Effort**: 600-720 hours (~15-18 weeks)
**Last Updated**: Dec 25, 2025
