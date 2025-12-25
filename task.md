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
- **NEW**: Complete ACHE Standards Database (69 checks across 8 standards)
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
| **Phase 25 (Drawing Checker)** | **51/150** | **99** | **34%** |
| **Phase 26 (Standards Database)** | **19/69** | **50** | **28%** |

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

#### Fixed Ladders (1910.23)
| Parameter | Requirement |
|-----------|-------------|
| Clear width | ≥ 16" (fixed), ≥ 11.5" (portable) |
| Rung spacing | 10-14" uniform |
| Offset from wall | 7" minimum |
| Side rail extension | 42" above landing |
| Cage required | > 20 ft unbroken |
| Cage start | 7-8 ft from base |
| Rest platform | Every 35 ft vertical |

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
| 2 | Standard hole size | J3.3 | ✅ Have |
| 3 | Oversized hole size | J3.3 | ❌ MISSING |
| 4 | Short-slot dimensions (width × length) | J3.3 | ❌ MISSING |
| 5 | Long-slot dimensions (width × length) | J3.3 | ❌ MISSING |
| 6 | Edge distance - sheared edge | J3.4 | ⚠️ Partial |
| 7 | Edge distance - rolled/thermally cut edge | J3.4 | ❌ MISSING |
| 8 | C₂ increment for slotted/oversized holes | J3.5 | ❌ MISSING |
| 9 | Min spacing (2.67d) | J3.3 | ✅ Have |
| 10 | Preferred spacing (3d) noted | J3.3 | ❌ MISSING |
| 11 | Max spacing (12t or 6") | J3.5 | ❌ MISSING |
| 12 | Clear distance Lc calculation | J3.10 | ❌ MISSING |
| 13 | Bearing capacity check | J3.10 | ❌ MISSING |
| 14 | Tearout capacity check | J3.10 | ❌ MISSING |
| 15 | Block shear (net area with hole + 1/8") | J4.3 | ❌ MISSING |
| 16 | Slot orientation vs load direction | J3.3 | ❌ MISSING |

#### AWS D1.1 Checks (8 total)
| # | Check | Reference | Current Status |
|---|-------|-----------|----------------|
| 1 | Min fillet weld size vs thickness | Table 5.8 | ⚠️ General note only |
| 2 | Max fillet weld size at edge | Table 2.1 | ❌ MISSING |
| 3 | Weld code referenced | - | ✅ Have |
| 4 | Prequalified joint details | Figs 5.1-5.5 | ❌ MISSING |
| 5 | Matching filler metal | Table 5.4 | ❌ MISSING |
| 6 | Preheat requirements | Table 5.11 | ❌ MISSING |
| 7 | Interpass temperature | 5.6 | ❌ MISSING |
| 8 | WPS/PQR requirements noted | - | ❌ MISSING |

#### API 661 Checks (10 total)
| # | Check | Reference | Current Status |
|---|-------|-----------|----------------|
| 1 | Fan tip clearance | Table 6 | ❌ MISSING |
| 2 | Tube support spacing ≤ 6 ft | 5.1.5.1 | ❌ MISSING |
| 3 | Tube keeper bolted | 5.1.5.3 | ❌ MISSING |
| 4 | Bundle lateral movement | 5.1.1.3 | ❌ MISSING |
| 5 | Condenser tube slope | 5.1.1.4 | ❌ MISSING |
| 6 | Header type vs pressure | 5.2 | ❌ MISSING |
| 7 | Motor bearing L10 ≥ 40,000 hrs | 7.2.4.1 | ❌ MISSING |
| 8 | Shaft bearing L10 ≥ 50,000 hrs | 7.2.5 | ❌ MISSING |
| 9 | Belt drive service factor | 7.2.4.5 | ❌ MISSING |
| 10 | Nozzle size (≥DN40 flanged) | 5.3.1 | ❌ MISSING |

#### OSHA Checks (10 total)
| # | Check | Reference | Current Status |
|---|-------|-----------|----------------|
| 1 | Guardrail height 42" ± 3" | 1910.29(b) | ❌ MISSING |
| 2 | Mid rail present | 1910.29(b) | ❌ MISSING |
| 3 | Toe board ≥ 3.5" | 1910.29(b) | ❌ MISSING |
| 4 | Opening ≤ 19" | 1910.29(b) | ❌ MISSING |
| 5 | Ladder width ≥ 16" | 1910.23(b) | ❌ MISSING |
| 6 | Rung spacing uniform 10-14" | 1910.23(b) | ❌ MISSING |
| 7 | Side rail extension 42" | 1910.23(d) | ❌ MISSING |
| 8 | Cage required check (>20 ft) | 1910.28(b) | ❌ MISSING |
| 9 | Self-closing gate at ladder | 1910.29(b) | ❌ MISSING |
| 10 | Platform min 24"×30" | 1910.29(g) | ❌ MISSING |

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
| AISC Holes/Bolts | 16 | 3 | **13** |
| AWS Welding | 8 | 2 | **6** |
| API 661 ACHE | 10 | 0 | **10** |
| ASME VIII | 8 | 0 | **8** |
| TEMA | 6 | 0 | **6** |
| OSHA Safety | 10 | 2 | **8** |
| NEMA Motors | 5 | 0 | **5** |
| SSPC Coating | 6 | 0 | **6** |
| **TOTAL** | **69** | **7** | **62** |

**Current Coverage: ~10%** — Significant expansion required for full standards compliance.

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


class OSHASafetyStandards:
    """OSHA 1910 - Walking-Working Surfaces"""
    
    TOP_RAIL_HEIGHT_MIN = 39
    TOP_RAIL_HEIGHT_MAX = 45
    TOE_BOARD_MIN = 3.5
    MAX_OPENING = 19
    LADDER_WIDTH_MIN = 16
    RUNG_SPACING_MIN = 10
    RUNG_SPACING_MAX = 14
    SIDE_RAIL_EXTENSION = 42
    CAGE_TRIGGER_HEIGHT = 240
```

---

### Priority Implementation Order

| Priority | Standard | Checks to Add | Impact |
|----------|----------|---------------|--------|
| 🔴 1 | AISC J3 - Slotted holes | 5 checks | Prevents assembly failures |
| 🔴 2 | AISC J3.5 - Max spacing | 2 checks | Prevents corrosion issues |
| 🔴 3 | API 661 - Fan clearance | 1 check | Prevents fan damage |
| 🟡 4 | OSHA 1910.29 - Guardrails | 5 checks | Safety compliance |
| 🟡 5 | AWS D1.1 - Preheat | 2 checks | Weld quality |
| 🟡 6 | SSPC - Surface prep | 3 checks | Coating durability |
| 🟢 7 | NEMA - Motor frames | 4 checks | Interchangeability |
| 🟢 8 | TEMA - Bundle specs | 3 checks | HX performance |

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
- [ ] Edge distances vs AISC J3.4 minimum
- [ ] Edge distances vs material thickness rules
- [ ] Hole spacing/pitch (min 2.67d per AISC)
- [ ] Hole-to-hole alignment (same part)
- [ ] **Cross-part hole alignment** (mating parts) ⭐ CRITICAL
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

- [ ] Net section at holes (reduced area)
- [ ] Bolt bearing capacity check
- [ ] Bolt shear capacity check
- [ ] Weld size adequate for load
- [ ] Member capacity verification (channels, angles)
- [ ] Connection capacity check
- [ ] Block shear verification at hole groups
- [ ] Deflection limits specified
- [ ] Vibration/resonance consideration (rotating equip)
- [ ] Fatigue consideration (cyclic loading)

---

### 25.3 Fabrication Feasibility (16 tasks)

#### Cutting
- [ ] Plasma/laser kerf allowance
- [ ] Minimum inside radius for cutting method
- [ ] Cut edge quality specification (ASME/AWS)
- [ ] Thermal distortion control notes

#### Forming
- [ ] Press brake capacity check
- [ ] Bend sequence verification
- [ ] Die marks acceptance criteria

#### Drilling/Punching
- [x] Punch capacity (t × 1.5 max hole)
- [ ] Drill vs punch specification
- [ ] Sub-punch and ream requirements

#### Fit-Up
- [ ] Root gap specification
- [ ] Fit-up tolerance specification
- [ ] Tack weld requirements
- [ ] Strongback/jigging notes
- [ ] Assembly sequence notes
- [ ] Sub-assembly identification

---

### 25.4 Welding (16 tasks)

#### Weld Design
- [x] Weld code referenced (AWS D1.1, CSA W59)
- [x] Default weld size specified
- [ ] Weld symbols on detail drawings
- [ ] Weld throat adequate for load
- [ ] Weld length adequate
- [ ] Weld type appropriate (fillet vs groove)
- [ ] Intermittent weld spacing (if applicable)

#### Weld Quality
- [ ] WPS/PQR requirements noted
- [ ] Welder qualification requirements
- [ ] Preheat requirements (>3/4" base metal)
- [ ] Interpass temperature limits
- [ ] PWHT requirements
- [ ] NDE requirements (RT, UT, MT, PT)

#### Weld Access
- [ ] Welder access to joints
- [ ] Electrode angle possible
- [ ] Backgouge access (if CJP required)
- [ ] Weld sequence for distortion control

---

### 25.5-25.13 (Remaining sections same as original)

See original task.md for complete Phase 25 task breakdown.

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

**Total Tasks**: 559 (340 ACHE + 150 Drawing Checker + 69 Standards)
**Estimated Effort**: 560-670 hours (~14-17 weeks)
**Last Updated**: Dec 25, 2025
