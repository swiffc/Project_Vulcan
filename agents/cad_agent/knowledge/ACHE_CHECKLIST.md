# PROJECT VULCAN - AIR-COOLED HEAT EXCHANGER (ACHE) COMPLETE CHECKLIST
## Fin Fan / Air Cooler - NOT Shell & Tube!
## Reference: Chart Industries, Hudson Products, Air-X-Changers
## Based on API 661, OSHA 1910, ASME, AISC
## Created: 2025-12-21 | Updated: 2025-12-21
## Referenced in: task.md (Phase 15: CAD Drawing Review Bot)

---

# TABLE OF CONTENTS

1. [Understanding: ACHE vs Shell & Tube](#section-1-understanding-ache-vs-shell--tube)
2. [ACHE Major Components](#section-2-ache-major-components)
3. [Plenum Assembly Checks](#section-3-plenum-assembly-checks)
4. [Header Box Checks](#section-4-header-box-checks)
5. [Tube Bundle Checks](#section-5-tube-bundle-checks)
6. [Fan & Drive System Checks](#section-6-fan--drive-system-checks)
7. [Structural Support Checks](#section-7-structural-support-checks)
8. [Cross-Check Requirements](#section-8-cross-check-requirements-critical)
9. [ACHE-Specific Failure Modes](#section-9-ache-specific-failure-modes)
10. [GitHub Repos & Resources](#section-10-github-repos-for-ache)
11. [Visual Verification Examples](#section-11-visual-verification-examples)
12. [Automatic Bot Checks](#section-12-what-the-bot-must-check-automatically)
13. [Accessories & Options](#section-13-ache-accessories--options)
14. [Access Structures](#section-14-access-structures---platforms-ladders-walkways)
15. [Structural Components Detail](#section-15-structural-components-detail)
16. [Instrumentation & Controls](#section-16-instrumentation--controls) *(NEW)*
17. [Electrical System](#section-17-electrical-system) *(NEW)*
18. [Piping Connections](#section-18-piping-connections) *(NEW)*
19. [Surface Prep & Coatings](#section-19-surface-prep--coatings) *(NEW)*
20. [Noise Requirements](#section-20-noise-requirements) *(NEW)*
21. [Testing Requirements](#section-21-testing-requirements) *(NEW)*
22. [Shipping & Handling](#section-22-shipping--handling) *(NEW)*
23. [Documentation Deliverables](#section-23-documentation-deliverables) *(NEW)*
24. [Maintenance Provisions](#section-24-maintenance-provisions) *(NEW)*
25. [Foundation Interface](#section-25-foundation-interface) *(NEW)*
26. [Nameplate & Tagging](#section-26-nameplate--tagging) *(NEW)*
27. [Spare Parts](#section-27-spare-parts) *(NEW)*
28. [Complete Master Checklist](#section-28-complete-master-checklist)

---

# SECTION 1: UNDERSTANDING ACHE vs Shell & Tube

```
┌─────────────────────────────────────────────────────────────────┐
│  ACHE (Fin Fan) - WHAT YOU HAVE:                               │
│                                                                 │
│        ┌─────────────────────────────────────────┐             │
│        │      TUBE BUNDLE (Finned Tubes)        │             │
│        │  ════════════════════════════════════  │             │
│        │  ════════════════════════════════════  │             │
│        │  ════════════════════════════════════  │             │
│        └───────────────┬─────────────────────────┘             │
│                        │                                        │
│        ┌───────────────┴─────────────────────────┐             │
│        │           PLENUM CHAMBER                │             │
│        │                                         │             │
│        │    ┌──────────┐    ┌──────────┐        │             │
│        │    │ FAN RING │    │ FAN RING │        │             │
│        │    │    ○     │    │    ○     │        │             │
│        │    │  (FAN)   │    │  (FAN)   │        │             │
│        │    └──────────┘    └──────────┘        │             │
│        └─────────────────────────────────────────┘             │
│                        │                                        │
│        ┌───────────────┴─────────────────────────┐             │
│        │     STRUCTURAL SUPPORT FRAME            │             │
│        │     (Columns, Beams, Bracing)           │             │
│        └─────────────────────────────────────────┘             │
│                                                                 │
│  This is what S25139-5A is - A PLENUM ASSEMBLY!                │
└─────────────────────────────────────────────────────────────────┘
```

---

# SECTION 2: ACHE MAJOR COMPONENTS

## 2.1 Component Hierarchy (Per API 661)

```
ACHE UNIT (BAY)
├── TUBE BUNDLE(S)
│   ├── Header Boxes (inlet/outlet)
│   │   ├── Plug sheet (tube access)
│   │   ├── Top/bottom plates
│   │   ├── Side plates (wrapper)
│   │   ├── Nozzles
│   │   └── Pass partitions
│   ├── Finned Tubes
│   │   ├── Bare tubes (process side)
│   │   └── Aluminum fins (air side)
│   ├── Tube Supports
│   │   └── Tube keeper bars
│   └── Bundle Frame
│       └── Side frames
│
├── PLENUM CHAMBER ← THIS IS S25139-5A!
│   ├── Plenum panels (walls)
│   ├── Plenum stiffeners
│   ├── Fan rings (fan openings)
│   ├── Floor panels
│   ├── Corner angles
│   ├── Divider panels
│   └── Access provisions
│
├── FAN ASSEMBLY
│   ├── Fan blades (FRP or aluminum)
│   ├── Hub
│   ├── Fan ring/shroud
│   └── Tip clearance seals
│
├── DRIVE SYSTEM
│   ├── Motor
│   ├── Speed reducer (V-belt, gear, HTD)
│   ├── Drive guard
│   └── Motor mounting
│
└── STRUCTURAL SUPPORT
    ├── Columns
    ├── Beams
    ├── Bracing
    ├── Floor grating
    └── Lifting lugs
```

---

# SECTION 3: PLENUM ASSEMBLY CHECKS

## 3.1 Plenum Panel Checks

| Check | Requirement | How to Verify |
|-------|-------------|---------------|
| Panel thickness | Per wind load calc | Check material callout |
| Panel material | Typically 10-14 ga carbon steel | Verify spec |
| Stiffener spacing | Per deflection requirement | Measure on drawing |
| Corner sealing | Continuous weld or gasket | Check weld symbols |
| Drain provisions | Slope to drain, weep holes | Verify details |

## 3.2 Fan Ring Checks

| Check | Standard | Requirement |
|-------|----------|-------------|
| Fan ring diameter | API 661 | Matches fan diameter + clearance |
| Fan ring shape | API 661 4.4.6 | Inlet bell or straight (prefer bell) |
| Ring material | - | Carbon steel, galvanized, or SS |
| Ring attachment | - | Bolted or welded to plenum floor |
| Tip clearance | API 661 Table 2 | See table below |

**API 661 Recommended Tip Clearances:**

| Fan Diameter | Max Radial Clearance |
|--------------|---------------------|
| 4' to 5' | 3/8" |
| 6' to 8' | 1/2" |
| 9' to 12' | 5/8" |
| 13' to 18' | 3/4" |
| 19' to 28' | 1" |
| > 28' | 1-1/4" |

## 3.3 Floor Panel Checks

| Check | Requirement | How to Verify |
|-------|-------------|---------------|
| Floor thickness | Min 10 ga (0.1345") per API | Check callout |
| Floor load | 50 psf min, 100 psf maint areas | Calculate capacity |
| Stiffener attachment | Bolted or welded | Check pattern |
| Hole alignment | Must match stiffener holes | **CROSS-CHECK!** |
| Splice alignment | Adjacent panels must align | **CROSS-CHECK!** |
| Drain slope | Min 1/8" per foot to drain | Verify |

## 3.4 Fan Coverage Check

```
Fan Coverage = (Total Fan Area) / (Bundle Face Area) × 100%

API 661 Minimum: 40%

Example:
- Bundle face = 12' × 30' = 360 sq ft
- Two fans @ 10' dia = 2 × π × 5² = 157 sq ft
- Coverage = 157/360 = 43.6% ✓ OK
```

---

# SECTION 4: HEADER BOX CHECKS

## 4.1 Header Types (Per API 661)

```
TYPE A - Removable Cover Plate:
┌──────────────────────┐
│    Cover Plate       │ ← Bolted, removable
├──────────────────────┤
│ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ ← Tube ends
│                      │
│    HEADER BOX        │
│                      │
│ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │
├──────────────────────┤
│    Plug Sheet        │ ← Threaded plugs for tube access
└──────────────────────┘

TYPE B - Plug Type (Most Common):
┌──────────────────────┐
│ ⊙ ⊙ ⊙ ⊙ ⊙ ⊙ ⊙ ⊙ ⊙ ⊙│ ← Threaded plugs
├──────────────────────┤
│ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ ← Tube ends
│                      │
│    HEADER BOX        │
│                      │
│ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │
├──────────────────────┤
│ ⊙ ⊙ ⊙ ⊙ ⊙ ⊙ ⊙ ⊙ ⊙ ⊙│ ← Threaded plugs
└──────────────────────┘

TYPE C - Bonnet:
    ┌──────────────────┐
    │                  │ ← Removable bonnet
    │    BONNET        │
    │                  │
    └────────┬─────────┘
             │
┌────────────┴────────────┐
│ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○    │ ← Tube ends
│                         │
└─────────────────────────┘
```

## 4.2 Header Plate Thickness

**Minimum per API 661 Table 1:**

| Material | Class R | Class C | Class B |
|----------|---------|---------|---------|
| Carbon Steel | 3/4" | 5/8" | 1/2" |
| Stainless | 5/8" | 1/2" | 3/8" |

## 4.3 Plug Sheet Checks

| Check | Requirement |
|-------|-------------|
| Plug hole diameter | Per tube OD (typically +1/16") |
| Thread depth | Full plug sheet or 2" max |
| Plug material | Same or compatible with header |
| Ligament | Min per ASME VIII |

---

# SECTION 5: TUBE BUNDLE CHECKS

## 5.1 Finned Tube Types

```
EXTRUDED FIN (Hudson Hy-Fin®):
    ┌─┬─┬─┬─┬─┬─┬─┬─┐
────┴─┴─┴─┴─┴─┴─┴─┴─┴────
    Aluminum sleeve extruded onto tube
    Best thermal bond, max 400°F

EMBEDDED FIN (L-Foot):
    ┌─┬─┬─┬─┬─┬─┬─┬─┐
────┴─┴─┴─┴─┴─┴─┴─┴─┴────
    Aluminum strip wound into groove
    Good to 750°F

TENSION WOUND:
    ┌─┬─┬─┬─┬─┬─┬─┬─┐
────┴─┴─┴─┴─┴─┴─┴─┴─┴────
    Aluminum strip under tension
    Economy option, max 250°F
```

## 5.2 Tube Specifications

| Parameter | Typical Range | API 661 Requirement |
|-----------|---------------|---------------------|
| Tube OD | 1" most common | Per design |
| Tube wall | 12-16 BWG | Per pressure + corrosion |
| Tube length | 6' to 60' | Per design |
| Fin height | 1/2" or 5/8" | Per thermal design |
| Fin density | 7-11 fins/inch | Per thermal design |
| Tube pitch | 2.375" or 2.5" | Per thermal design |

## 5.3 Tube Wall Minimum (API 661)

| Material | Min Wall (1" OD) | Min Wall (1.25" OD) |
|----------|------------------|---------------------|
| Carbon Steel | 0.083" (14 BWG) | 0.095" (12 BWG) |
| Admiralty | 0.065" (16 BWG) | 0.065" (16 BWG) |
| Stainless | 0.065" (16 BWG) | 0.065" (16 BWG) |
| CuNi 90/10 | 0.065" (16 BWG) | 0.065" (16 BWG) |

---

# SECTION 6: FAN & DRIVE SYSTEM CHECKS

## 6.1 Fan Types

| Type | Material | Max Temp | Application |
|------|----------|----------|-------------|
| Tuf-Lite® (FRP) | Fiberglass | 200°F | Standard forced draft |
| Aluminum | Cast aluminum | 300°F | Higher temp or corrosive |
| Adjustable pitch | Various | Various | Variable load applications |

## 6.2 Fan Checks

| Check | Standard | Requirement |
|-------|----------|-------------|
| Blade material | API 661 | Per temperature/environment |
| Number of blades | Design | Typically 4-6 |
| Blade pitch | Design | Adjustable or fixed |
| Hub material | API 661 | Compatible with blades |
| Balance grade | AMCA 204 | BV-3 for petrochemical |
| Tip speed | API 661 | Max 12,000 fpm typical |

## 6.3 Drive System Checks

| Component | Check | Requirement |
|-----------|-------|-------------|
| Motor HP | Calc | BHP × 1.1 service factor |
| Motor enclosure | Spec | TEFC, TEFC-XP per area class |
| V-belt type | API 661 | Matched set, positive drive |
| Sheave alignment | Install | Within 1/16" |
| Guard coverage | OSHA | Fully enclosed |
| Motor base | Design | Adjustable for belt tension |

## 6.4 Vibration Requirements (API 661)

| Component | Max Vibration | Notes |
|-----------|---------------|-------|
| Fan assembly | 0.15 in/s velocity | Field balanced |
| Motor | Per NEMA MG-1 | Check nameplate |
| Structure | No resonance | Avoid fan RPM harmonics |

---

# SECTION 7: STRUCTURAL SUPPORT CHECKS

## 7.1 Load Considerations

| Load Type | Source | Notes |
|-----------|--------|-------|
| Dead load | Structure + equipment | Include full water weight |
| Live load | Maintenance | 50 psf min |
| Wind load | Site specific | Per ASCE 7 |
| Seismic | Site specific | Per ASCE 7 |
| Thermal | Bundle expansion | Fixed point location |
| Operating | Fan forces | Dynamic loads |

## 7.2 Column Checks

| Check | Standard | Requirement |
|-------|----------|-------------|
| Base plate thickness | AISC | Per anchor bolt loads |
| Anchor bolt size | AISC | Per shear + tension |
| Anchor bolt edge dist | AISC J3.4 | Per bolt diameter |
| Column splice | AISC | Full penetration or bolted |
| Bracing connections | AISC | Gusset plates adequate |

## 7.3 Lifting Provisions

| Check | Requirement |
|-------|-------------|
| Lug capacity | Min 2× lifted weight |
| Lug edge distance | Per pin/shackle size |
| Weld size | Per calculated load |
| Monorail/davit | Per bundle weight |

---

# SECTION 8: CROSS-CHECK REQUIREMENTS (CRITICAL!)

## What MUST be cross-checked in an ACHE:

```
FOR PLENUM ASSEMBLY (Like S25139-5A):
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  FLOOR PANEL (5A-X) ──────── must align with ──────► STIFFENER (5A-W)
│         │                                                       │
│         └── holes at spacing X ◄─── must match ───► holes at X  │
│                                                                 │
│  FLOOR PANEL (5A-X) ──────── must align with ──────► SPLICE (5A-R)
│         │                                                       │
│         └── edge holes ◄─────── must match ───────► edge holes  │
│                                                                 │
│  WALL PANEL (5A-H) ──────── must align with ──────► STIFFENER (5A-P)
│         │                                                       │
│         └── holes ◄─────────── must match ─────────► holes      │
│                                                                 │
│  FAN RING (5A-U) ─────────── must align with ──────► FLOOR (5A-T/V)
│         │                                                       │
│         └── bolt circle ◄───── must match ─────────► bolt circle│
│                                                                 │
│  KNEE BRACE (5A-G) ────────── must align with ──────► COLUMN (5A-1)
│         │                                                       │
│         └── holes ◄─────────── must match ─────────► holes      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## For each mating pair, verify:

1. **Hole locations** - X-Y coordinates match within ±1/16"
2. **Hole sizes** - Same diameter for same bolt
3. **Hole quantity** - Same count at interface
4. **Pattern orientation** - Not mirrored incorrectly

---

# SECTION 9: ACHE-SPECIFIC FAILURE MODES

## What can go wrong - Bot should watch for:

| Issue | Cause | What to Check |
|-------|-------|---------------|
| Hot air recirculation | Forced draft, gaps in plenum | Panel fit-up, end seals |
| Fan vibration | Imbalance, resonance | Balance grade, natural freq |
| Tube leaks | Corrosion, expansion stress | Material, tube wall, fixed point |
| Fin deterioration | High temp, corrosion | Fin type vs temp rating |
| Belt failure | Misalignment, wear | Alignment provisions, guard |
| Structure fatigue | Vibration, thermal cycling | Connections, welds |
| Header leaks | Plug gasket, tube joint | Plug torque, expansion joint |

---

# SECTION 10: GITHUB REPOS FOR ACHE

## Available Resources:

| Resource | URL | What It Does |
|----------|-----|--------------|
| python-hvac | github.com/TomLXXVI/python-hvac | Fin-tube HX models, heat transfer |
| TORCHE | github topics/heat-exchanger | Cross-flow tube bundle calcs |
| calctoys | github.com/thepvguy/calctoys | ASME pressure vessel calcs |
| steelpy | pypi.org/project/steelpy | AISC shapes for structure |

## Commercial References:

| Company | Resource |
|---------|----------|
| Chart Industries | chartindustries.com - ACHE manuals, fan guides |
| Hudson Products | Basics of Axial Flow Fans (PDF) |
| Air-X-Changers | Spec sheets, model guides |
| API | API 661 standard (purchase required) |

## Chart Industries Technical Documents:

- "Basics of Air-Cooled Heat Exchangers" manual
- "Basics of Axial Flow Fans" manual
- "Performance Improvement of ACHEs" guide
- Tuf-Lite fan installation manuals

---

# SECTION 11: VISUAL VERIFICATION EXAMPLES

## ALWAYS show before/after when recommending changes:

### Example: Fan Ring Mounting

```
PROBLEM:                          SOLUTION:
┌──────────────────┐              ┌──────────────────┐
│     ○   ○   ○    │              │  ○  ○  ○  ○  ○   │
│   FAN RING       │              │    FAN RING      │
│  (only 3 bolts)  │              │   (5 bolts)      │
└──────────────────┘              └──────────────────┘
        │                                 │
        ▼                                 ▼
⚠️ Insufficient bolt           ✓ Adequate bolt pattern
   pattern for vibration          per API 661

Reference: API 661 para 4.4.6
```

---

# SECTION 12: WHAT THE BOT MUST CHECK AUTOMATICALLY

## Without user input, check ALL of the following:

### PLENUM:
- [ ] Panel thickness adequate for wind load
- [ ] Stiffener spacing per deflection requirement
- [ ] Floor panels - hole alignment with stiffeners
- [ ] Fan ring diameter correct for fan
- [ ] Tip clearance within limits
- [ ] Drain provisions included
- [ ] Access for maintenance

### BUNDLE:
- [ ] Header plate thickness per API 661 Table 1
- [ ] Tube wall thickness per API 661
- [ ] Plug hole alignment
- [ ] Nozzle reinforcement
- [ ] Thermal expansion provisions

### FANS:
- [ ] Fan coverage minimum 40%
- [ ] Blade material vs temperature
- [ ] Balance grade for application
- [ ] Tip clearance per API 661 Table 2

### DRIVE:
- [ ] Motor HP adequate (BHP × SF)
- [ ] Motor enclosure per area class
- [ ] Belt guard coverage
- [ ] Alignment provisions

### STRUCTURE:
- [ ] Column/beam sizes adequate
- [ ] Connection hole alignment
- [ ] Anchor bolt edge distances
- [ ] Lifting lug capacity

### CROSS-CHECKS (CRITICAL):
- [ ] All mating part holes align
- [ ] All mating part hole sizes match
- [ ] Assembly BOM complete
- [ ] All parts accounted for

---

# SECTION 13: ACHE ACCESSORIES & OPTIONS

## 13.1 Air Flow Control - Louvers

| Type | Application | Checks |
|------|-------------|--------|
| **Inlet Louvers** | Below bundle (forced draft) | Blade pitch, linkage, actuator |
| **Outlet Louvers** | Above bundle (induced draft) | Blade pitch, linkage, actuator |
| **Recirculation Louvers** | Winterization systems | Seal when closed, full open |
| **Parallel Blade** | On/off control | Simple, less precise |
| **Opposed Blade** | Modulating control | Better linear control |

**Louver Checks:**

| Check | Requirement |
|-------|-------------|
| Blade material | Extruded aluminum typical |
| Blade bushings | Teflon or bronze |
| Linkage material | Galvanized or SS |
| Actuator sizing | Per torque requirement |
| Leakage when closed | Max 2% per API 661 |
| Position indicator | Local and/or remote |

## 13.2 Weather Protection

### Hoods / Enclosures

| Component | Purpose | Checks |
|-----------|---------|--------|
| **Top Hood** (induced draft) | Rain/snow protection | Drainage, structural support |
| **Side Enclosure** | Wind protection | Panel thickness, fastening |
| **End Enclosure** | Wind/recirculation prevention | Access provisions |
| **Recirculation Chamber** | Winterization warm air return | Seal integrity, louver fit |

### Protective Screens

| Screen Type | Purpose | Checks |
|-------------|---------|--------|
| **Bug Screens** | Keep debris out of bundle | Mesh size (typically 16-20 mesh) |
| **Hail Guards** | Protect fins from hail damage | Open area (min 70%), frame strength |
| **Cottonwood Screens** | Block poplar fluff/seeds | Removable for cleaning |
| **Bird Screens** | Prevent nesting | Larger mesh, robust frame |
| **Sand/Dust Screens** | Desert environments | Fine mesh, cleanable |

**Screen Specifications:**

| Screen Type | Typical Mesh | Frame Material | Notes |
|-------------|--------------|----------------|-------|
| Bug screen | 16-20 mesh | Galvanized/SS | Removable panels |
| Hail guard | 1/2" - 3/4" | Galvanized steel | Min 70% open area |
| Cottonwood | 4-8 mesh | Aluminum | Hinged for cleaning |

## 13.3 Winterization Components

| Component | Function | Checks |
|-----------|----------|--------|
| **Steam Coils** | Pre-heat air before bundle | Coil capacity, trap, controls |
| **Electric Heaters** | Emergency startup heating | Wattage, enclosure rating |
| **Glycol Coils** | Freeze protection | Glycol concentration, pump |
| **Recirculation Ducts** | Return warm exhaust air | Duct size, louver control |
| **Insulated Panels** | Reduce heat loss | R-value, weather seal |
| **Louver Blankets** | Additional insulation | Attachment, storage |

---

# SECTION 14: ACCESS STRUCTURES - PLATFORMS, LADDERS, WALKWAYS

## 14.1 Platform Types

```
ACHE ACCESS STRUCTURE ARRANGEMENT:

                    HEADER WALKWAY
                   ┌─────────────────────────────────────┐
                   │  ▓▓▓▓▓▓▓▓ GRATING ▓▓▓▓▓▓▓▓         │
                   │  Access to header plugs/nozzles     │
                   └───────────┬─────────────────────────┘
                               │
    ┌──────────────────────────┴──────────────────────────┐
    │                   TUBE BUNDLE                        │
    │   ════════════════════════════════════════════════   │
    │   ════════════════════════════════════════════════   │
    └──────────────────────────┬──────────────────────────┘
                               │
    ┌──────────────────────────┴──────────────────────────┐
    │                   PLENUM                             │
    │        ┌────────┐          ┌────────┐               │
    │        │  FAN   │          │  FAN   │               │
    │        └────────┘          └────────┘               │
    └───────────────────────┬─────────────────────────────┘
                            │
    ────────────────────────┴─────────────────────────────
              MOTOR/DRIVE MAINTENANCE PLATFORM
              (Below fans for drive access)
    ──────────────────────────────────────────────────────
                            │
                       ┌────┴────┐
                       │ LADDER  │
                       │   TO    │
                       │ GRADE   │
                       └─────────┘

    ════════════════════════════════════════════════════
              BALLROOM WALKWAY (Between bays)
              1.5m - 2.0m wide for tool storage
    ════════════════════════════════════════════════════
```

## 14.2 Platform Requirements

| Platform Type | Width | Load | Grating | Handrail |
|---------------|-------|------|---------|----------|
| **Header Walkway** | 30" min (750mm) | 50 psf | 1" x 3/16" | 42" with midrail |
| **Motor Platform** | 36" min (900mm) | 75 psf | 1" x 3/16" | 42" with midrail |
| **Ballroom Walkway** | 60-80" (1.5-2.0m) | 100 psf | 1-1/4" x 3/16" | 42" with midrail |
| **Interconnecting** | 24" min (600mm) | 50 psf | 1" x 3/16" | 42" with midrail |

## 14.3 Ladder Requirements (OSHA 1910.23)

| Check | Requirement |
|-------|-------------|
| Rung spacing | 12" on center (uniform) |
| Rung diameter | 3/4" min |
| Side rail width | 16" min clear between |
| Cage required | > 20' unbroken climb |
| Landing required | Every 30' max |
| Extension above landing | 42" min |
| Clearance behind rungs | 7" min |

## 14.4 Stair Requirements (OSHA 1910.25)

| Check | Requirement |
|-------|-------------|
| Stair width | 22" min |
| Riser height | 6" - 7.5" (uniform) |
| Tread depth | 9.5" min |
| Handrail height | 30" - 37" |
| Stair angle | 30° - 50° |
| Landing every | 12' vertical rise |

## 14.5 Handrail & Guardrail (OSHA 1910.29)

| Component | Requirement |
|-----------|-------------|
| Top rail height | 42" ± 3" |
| Midrail height | 21" (between top and floor) |
| Toe board height | 4" min |
| Opening | Cannot pass 19" sphere |
| Post spacing | 8' max |
| Top rail load | 200 lb any direction |

## 14.6 Grating Specifications

| Type | Bar Size | Bearing Bar Spacing | Load Rating |
|------|----------|---------------------|-------------|
| Light duty | 1" x 3/16" | 1-3/16" | 50 psf |
| Standard | 1-1/4" x 3/16" | 1-3/16" | 75 psf |
| Heavy duty | 1-1/2" x 3/16" | 1-3/16" | 100 psf |
| Extra heavy | 2" x 3/16" | 1-3/16" | 150+ psf |

**Grating Checks:**

| Check | Requirement |
|-------|-------------|
| Bearing bar direction | Perpendicular to traffic |
| Span | Per manufacturer tables |
| Attachment | Clips or welded |
| Opening size | Max 1-1/4" (OSHA) |
| Surface | Plain, serrated, or grip-strut |
| Banding | On cut edges |

---

# SECTION 15: STRUCTURAL COMPONENTS DETAIL

## 15.1 Main Frame Components

| Component | Typical Material | Checks |
|-----------|-----------------|--------|
| **Main Columns** | W8, W10, W12 | Size per load, splices |
| **Header Beams** | W8, W10 | Bundle support, deflection |
| **Bundle Rails** | C-channel | For bundle removal |
| **Cross Bracing** | Angles, HSS | Connection adequacy |
| **Base Plates** | 3/4" - 1" plate | Anchor bolt pattern |

## 15.2 Secondary Steel

| Component | Purpose | Checks |
|-----------|---------|--------|
| **Grating Support** | Platform framing | Spacing, connections |
| **Handrail Posts** | Guard rail support | Base plate, weld |
| **Ladder Stringers** | Side rails | Material, splice |
| **Stair Stringers** | Stair support | Angle, material |
| **Pipe Supports** | Header piping | Load, location |

## 15.3 Connection Details

| Connection | Typical Design | Checks |
|------------|----------------|--------|
| Column base | Welded plate + anchor bolts | Bolt size, edge dist |
| Column splice | Bolted flange | Bolt pattern, grade |
| Beam to column | Clip angle or shear tab | Bolt count, weld |
| Brace to gusset | Bolted or welded | Gusset size, weld |
| Grating to frame | Grating clips | Clip spacing |

---

# SECTION 16: INSTRUMENTATION & CONTROLS *(NEW)*

## 16.1 Temperature Measurement

| Location | Sensor Type | Checks |
|----------|-------------|--------|
| Process inlet | RTD or thermocouple | Thermowell design, insertion depth |
| Process outlet | RTD or thermocouple | Thermowell design, insertion depth |
| Air inlet | RTD or thermostat | Location (ambient representative) |
| Air outlet | RTD array | Multiple points for uniformity |

## 16.2 Pressure Measurement

| Location | Instrument | Checks |
|----------|------------|--------|
| Header inlet | Pressure gauge/transmitter | Range, connection size |
| Header outlet | Pressure gauge/transmitter | Range, connection size |
| Differential | DP transmitter | Diaphragm seal if required |

## 16.3 Vibration Monitoring

| Component | Sensor Type | Setpoint |
|-----------|-------------|----------|
| Fan bearing | Vibration switch | 0.15 in/s alarm, 0.20 in/s trip |
| Motor bearing | Vibration transmitter | Per motor size |
| Structure | Accelerometer (optional) | Per resonance study |

## 16.4 Control Systems

| Control | Actuator | Logic |
|---------|----------|-------|
| Fan pitch | Pneumatic/electric | Outlet temp control |
| Louvers | Pneumatic/electric | Winterization, turndown |
| VFD | Electric | Fan speed modulation |
| Fan on/off | Motor starter | Staged operation |

## 16.5 Instrumentation Checks

| Check | Requirement |
|-------|-------------|
| Sensor nozzle size | Matches instrument |
| Thermowell insertion | Min 10× OD |
| Vibration switch wiring | Fail-safe (NC contact) |
| VFD harmonics | Filter if required |
| Control panel location | Accessible, area rated |
| Alarm/shutdown logic | Documented in P&ID |

---

# SECTION 17: ELECTRICAL SYSTEM *(NEW)*

## 17.1 Motor Electrical

| Component | Check | Requirement |
|-----------|-------|-------------|
| Motor voltage | Per site | 480V, 4160V typical |
| Motor HP | Calculation | BHP × 1.1 SF min |
| Motor enclosure | Area class | TEFC, TEFC-XP, etc. |
| Motor efficiency | Spec | Premium efficiency (IE3/IE4) |
| Service factor | API 661 | Min 1.15 |

## 17.2 Area Classification

| Class | Application | Motor Type |
|-------|-------------|------------|
| Unclassified | Non-hazardous | TEFC |
| Class I Div 2 | Flammable gases (rare) | XP or purged |
| Class I Div 1 | Flammable gases (normal) | XP or increased safety |
| Class II | Dust hazard | Dust-ignition proof |

## 17.3 Electrical Components

| Component | Check | Requirement |
|-----------|-------|-------------|
| Junction boxes | Rating | NEMA 4X or explosion-proof |
| Cable tray | Material | Galvanized or aluminum |
| Conduit | Size | Per NEC fill requirements |
| Grounding | Locations | All metal components |
| Bonding | Connections | Across flexible joints |
| Lighting | Coverage | 10 fc min on platforms |

## 17.4 Heat Tracing (Winterization)

| Check | Requirement |
|-------|-------------|
| Wattage | Per heat loss calc |
| Circuit type | Self-regulating preferred |
| Insulation | Over heat trace |
| Thermostat | Set point per fluid |
| Certification | Area class rated |

## 17.5 Electrical Checks

| Check | Requirement |
|-------|-------------|
| Motor terminal box orientation | Accessible |
| JB locations match conduit | Routing feasible |
| Cable tray supports | Per span table |
| Grounding lugs | Frame, motors, panels |
| Area classification boundary | Per hazard study |

---

# SECTION 18: PIPING CONNECTIONS *(NEW)*

## 18.1 Nozzle Specifications

| Parameter | Check | Standard |
|-----------|-------|----------|
| Flange rating | Per design pressure | ASME B16.5 |
| Flange facing | Raised face typical | RF or RTJ |
| Nozzle size | Per flow requirement | Process design |
| Projection | For bolting clearance | Min 4" from header |
| Reinforcement | Per ASME VIII | Pad or integral |

## 18.2 Flange Ratings (ASME B16.5)

| Class | Max Pressure @ 100°F | Typical Use |
|-------|---------------------|-------------|
| 150# | 285 psig | Low pressure |
| 300# | 740 psig | Standard |
| 600# | 1480 psig | High pressure |
| 900# | 2220 psig | Very high pressure |

## 18.3 Gasket Types

| Type | Application | Notes |
|------|-------------|-------|
| Spiral wound | Most common | 304SS/graphite |
| Sheet gasket | Low pressure | Compressed fiber |
| Ring joint (RTJ) | High pressure | Matched to flange |
| Kammprofile | High temp/pressure | Metal core + facing |

## 18.4 Piping Connections

| Connection | Check | Requirement |
|------------|-------|-------------|
| Vent connections | Location | High point of header |
| Drain connections | Location | Low point of header |
| Instrument connections | Size | 3/4" or 1" NPT typical |
| PSV connection | Size | Per relief requirement |
| Steam trap | If steam coil | Proper sizing |

## 18.5 Thermal Expansion

| Check | Requirement |
|-------|-------------|
| Fixed point location | One end of bundle |
| Sliding supports | Opposite end |
| Piping flexibility | Expansion loops or expansion joint |
| Nozzle loads | Within API 661 limits |

## 18.6 Piping Checks

| Check | Requirement |
|-------|-------------|
| Nozzle orientations | Match piping ISO |
| Vent/drain locations | Per plot plan |
| Nozzle projection | Clearance for bolting |
| Reinforcement pad | Size and thickness |
| Flange bolt holes | Straddle centerline |

---

# SECTION 19: SURFACE PREP & COATINGS *(NEW)*

## 19.1 Surface Preparation Standards

| Standard | Description | Application |
|----------|-------------|-------------|
| SSPC-SP1 | Solvent cleaning | All surfaces first |
| SSPC-SP6 | Commercial blast | Minimum standard |
| SSPC-SP10 | Near white blast | Petrochemical typical |
| SSPC-SP5 | White metal blast | Immersion service |

## 19.2 Coating Systems

### Carbon Steel (Exterior)

| Layer | Type | DFT | Color |
|-------|------|-----|-------|
| Prime | Inorganic zinc | 3-4 mils | Gray |
| Intermediate | Epoxy | 4-6 mils | Varies |
| Topcoat | Polyurethane | 2-3 mils | Per spec |
| **Total** | | **9-13 mils** | |

### Carbon Steel (High Temp >300°F)

| Layer | Type | DFT | Notes |
|-------|------|-----|-------|
| Single coat | Hi-temp silicone | 1-2 mils | To 1200°F |

### Stainless Steel

| Treatment | Application |
|-----------|-------------|
| Passivation | Required per ASTM A967 |
| No paint | Typically left bare |

## 19.3 Galvanizing

| Component | Typical Application |
|-----------|---------------------|
| Fan rings | Hot-dip galvanized |
| Grating | Hot-dip galvanized |
| Handrails | Hot-dip galvanized |
| Ladders | Hot-dip galvanized |
| Fasteners | Hot-dip or mechanically galv |

## 19.4 Coating Checks

| Check | Requirement |
|-------|-------------|
| Blast profile | 1.5-3.0 mils (angular) |
| DFT measurement | Per coat, total |
| Holiday testing | 67.5V/mil for thin film |
| Touch-up | Same system as original |
| Cure time | Per manufacturer |
| Temperature limits | Min/max application temp |

---

# SECTION 20: NOISE REQUIREMENTS *(NEW)*

## 20.1 Noise Limits

| Location | Typical Limit | Standard |
|----------|---------------|----------|
| Equipment (1m) | 85 dBA | OSHA 8-hr TWA |
| Property line | 55-65 dBA | Local ordinance |
| Residential area | 45-55 dBA | Night/day limits |

## 20.2 Noise Sources in ACHE

| Source | Contribution | Mitigation |
|--------|--------------|------------|
| Fan blades | Dominant (70-80%) | Low-noise blade design |
| Motor | 5-10% | Premium motor |
| Drive belts | 5-10% | HTD or direct drive |
| Air turbulence | 5-15% | Inlet bell, screens |

## 20.3 Noise Reduction Options

| Method | Reduction | Cost Impact |
|--------|-----------|-------------|
| Low-noise fan | 3-6 dBA | 15-20% premium |
| Reduced tip speed | 3-6 dBA | Larger fan |
| Direct drive | 2-4 dBA | Higher motor cost |
| Inlet silencer | 5-10 dBA | Significant |
| Barrier walls | 5-15 dBA | Major addition |

## 20.4 Noise Checks

| Check | Requirement |
|-------|-------------|
| Guaranteed Lw | Per specification |
| Measurement distance | Usually 1m from surface |
| Octave band data | If low frequency concern |
| Fan tip speed | Lower = quieter |
| Number of blades | More = smoother sound |

---

# SECTION 21: TESTING REQUIREMENTS *(NEW)*

## 21.1 Pressure Testing

| Test Type | Pressure | Hold Time | Standard |
|-----------|----------|-----------|----------|
| Hydrostatic | 1.5× MAWP | 30 min min | ASME VIII |
| Pneumatic | 1.1× MAWP | 10 min min | ASME VIII |
| Leak test | MAWP | Until verified | API 661 |

## 21.2 Mechanical Tests

| Test | Requirement | Standard |
|------|-------------|----------|
| Fan balance | BV-3 grade | AMCA 204 |
| Motor no-load | Check rotation | Before coupling |
| Mechanical run | 4 hours min | API 661 |
| Vibration | <0.15 in/s | API 661 |

## 21.3 Performance Testing

| Test | Requirement | Standard |
|------|-------------|----------|
| Thermal performance | Per data sheet | ASME PTC 30 |
| Air flow | Per design | AMCA 210 |
| Pressure drop | Per design | Test or calc |

## 21.4 NDE Requirements

| Method | Application | Standard |
|--------|-------------|----------|
| RT (Radiography) | Header welds | ASME VIII |
| UT (Ultrasonic) | Plate material | ASME VIII |
| PT (Dye penetrant) | Surface cracks | ASME VIII |
| MT (Magnetic particle) | Ferromagnetic | ASME VIII |
| VT (Visual) | All welds | AWS D1.1 |

## 21.5 Testing Checks

| Check | Requirement |
|-------|-------------|
| Test pressure | Calc per MAWP and temp |
| Test medium | Water (hydro), air/N2 (pneumatic) |
| Test gauges | Calibrated, range appropriate |
| Witness points | Per QA plan |
| Test reports | Signed by QC |

---

# SECTION 22: SHIPPING & HANDLING *(NEW)*

## 22.1 Shipping Configurations

| Configuration | Max Dimensions | Notes |
|---------------|----------------|-------|
| Truck (US) | 12' H × 8.5' W × 53' L | Standard trailer |
| Oversize truck | 14' H × 12' W × varies | Permits required |
| Barge | Unlimited | For coastal/river |
| Rail | 10.5' H × 10.5' W × varies | AAR clearances |

## 22.2 Shipping Splits

| Assembly | Ship As | Field Join |
|----------|---------|------------|
| Tube bundle | Complete | Lift into structure |
| Plenum | Sections | Bolted splice |
| Structure | Knockdown | Field erect |
| Fans/motors | Loose | Mount on site |
| Grating/handrail | Bundles | Clip or weld |

## 22.3 Preservation

| Component | Preservation | Duration |
|-----------|--------------|----------|
| Headers (CS) | N2 purge + desiccant | 6-12 months |
| Headers (SS) | Dry, plugged | Indefinite |
| Finned tubes | End caps | Until install |
| Motors | Shaft rotation monthly | Per manufacturer |
| Bearings | Grease filled | Per manufacturer |

## 22.4 Lifting & Handling

| Component | Lift Points | Capacity |
|-----------|-------------|----------|
| Tube bundle | Factory lugs | 2× bundle weight |
| Plenum section | Lift lugs | 2× section weight |
| Structure | Column splices | Per rigging plan |

## 22.5 Shipping Checks

| Check | Requirement |
|-------|-------------|
| Shipping splits | Marked on drawings |
| Max shipping dims | Within limits |
| Lift point locations | Adequate capacity |
| Preservation spec | Per storage duration |
| Flange protection | Blinds or covers |
| Fin protection | End caps/guards |

---

# SECTION 23: DOCUMENTATION DELIVERABLES *(NEW)*

## 23.1 Engineering Documents

| Document | Content | Timing |
|----------|---------|--------|
| API 661 Data Sheet | All thermal/mechanical data | At order |
| General Arrangement | Overall dims, connections | With approval |
| P&ID | Process flow, instruments | With approval |
| Bundle drawing | Tube layout, header details | For approval |
| Structural drawings | Steel details | For fabrication |
| Electrical single line | Motor circuits | For approval |

## 23.2 Fabrication Documents

| Document | Content | Timing |
|----------|---------|--------|
| Weld map | All weld locations, procedures | Before welding |
| WPS/PQR | Qualified procedures | Before welding |
| NDE plan | Required examinations | Before NDE |
| Inspection & Test Plan | QC hold points | Before fabrication |

## 23.3 Material Certifications

| Document | Content | Timing |
|----------|---------|--------|
| MTRs | Mill test reports, all pressure parts | At shipment |
| PMI | Positive material ID (alloys) | Before install |
| Coating certs | Batch numbers, application data | At shipment |
| Motor data | Nameplate, test reports | At shipment |

## 23.4 Test & Inspection Records

| Document | Content | Timing |
|----------|---------|--------|
| Hydro test report | Pressure, duration, witness | After test |
| NDE reports | RT film, UT scans, PT/MT records | After NDE |
| Dimensional report | Critical dimensions | Before shipment |
| Balance report | Fan balance data | After balance |

## 23.5 Final Documentation

| Document | Content | Timing |
|----------|---------|--------|
| U-1A form | ASME code data (if stamped) | At shipment |
| As-built drawings | Red-line corrections | 30 days after ship |
| O&M manual | Operating instructions | At shipment |
| Spare parts list | Recommended spares | At shipment |

## 23.6 Documentation Checks

| Check | Requirement |
|-------|-------------|
| Document register | All deliverables listed |
| Transmittal log | Track all submittals |
| Approval status | IFA, IFC, As-Built |
| Retention period | 10+ years typical |

---

# SECTION 24: MAINTENANCE PROVISIONS *(NEW)*

## 24.1 Bundle Removal

| Provision | Requirement |
|-----------|-------------|
| Bundle slide rails | C-channel in structure |
| Pulling clearance | Full bundle length + 2' |
| Removal tool pads | On bundle frame |
| Structure opening | Adequate for bundle |

## 24.2 Fan/Motor Access

| Provision | Requirement |
|-----------|-------------|
| Davit or monorail | Over each fan bay |
| Davit capacity | Motor + reducer + rigging |
| Swing radius | Clear fan opening |
| Platform around motor | 36" min clearance |

## 24.3 Tube Plugging

| Provision | Requirement |
|-----------|-------------|
| Plug access | Clear path to all plugs |
| Header walkway | 30" min width |
| Plug socket | Standard hex or special |
| Spare plugs | 5% of tube count |

## 24.4 Cleaning Provisions

| Method | Provisions |
|--------|------------|
| Pressure washing | Access, water supply |
| Chemical cleaning | CIP connections, drain |
| Steam cleaning | Steam supply, condensate |
| Air blow | Compressed air connection |

## 24.5 Maintenance Checks

| Check | Requirement |
|-------|-------------|
| Bundle slide rails | Present, aligned |
| Davit/monorail | Capacity adequate |
| Access platforms | All equipment reachable |
| Drain valves | At low points |
| Tool storage | On ballroom walkway |

---

# SECTION 25: FOUNDATION INTERFACE *(NEW)*

## 25.1 Foundation Types

| Type | Application | Notes |
|------|-------------|-------|
| Concrete piers | Most common | One per column |
| Concrete slab | Light duty | With embedded plates |
| Steel grillage | On pipe rack | Existing steel support |
| Pile supported | Poor soil | Deep foundations |

## 25.2 Anchor Bolt Design

| Parameter | Typical | Check |
|-----------|---------|-------|
| Bolt diameter | 3/4" - 1-1/2" | Per shear + tension |
| Embedment | 12× diameter | Per ACI 318 |
| Edge distance | 6× diameter min | Per ACI 318 |
| Projection | 4" above base plate | For leveling |
| Material | F1554 Gr 36/55/105 | Per load |

## 25.3 Base Plate Design

| Parameter | Typical | Check |
|-----------|---------|-------|
| Thickness | 3/4" - 1-1/2" | Per AISC |
| Size | Column + bolt pattern | Fit pier |
| Holes | Oversized 1/4" | For adjustment |
| Grout pocket | 1" - 1.5" | Non-shrink grout |

## 25.4 Foundation Checks

| Check | Requirement |
|-------|-------------|
| Anchor bolt template | Matches base plate |
| Pier size/location | Per structural |
| Grout pocket depth | 1" - 1.5" typical |
| Embedment depth | Per bolt calc |
| Leveling shim locations | On drawings |
| Anchor bolt projection | 4" min above plate |
| Pier reinforcing | Per civil drawings |

---

# SECTION 26: NAMEPLATE & TAGGING *(NEW)*

## 26.1 Equipment Nameplates

| Location | Information |
|----------|-------------|
| Main equipment tag | On main column, visible |
| ASME U-stamp | On each header (if code) |
| Bundle tag | On each bundle frame |
| Fan nameplate | On hub or guard |
| Motor nameplate | Visible from grade |

## 26.2 Nameplate Data (API 661 Data Sheet Info)

| Field | Example |
|-------|---------|
| Tag number | 123-E-456 |
| Service | Compressor discharge cooler |
| Design pressure | 150 psig |
| Design temperature | 350°F |
| Test pressure | 225 psig |
| MAWP/MDMT | 150 psig / -20°F |
| Year built | 2025 |
| Manufacturer | ABC Corporation |

## 26.3 U-Stamp Requirements (ASME)

| Requirement | Notes |
|-------------|-------|
| U-1A form | Manufacturer's data report |
| UM stamp | On each pressure part |
| Authorized inspector | Sign-off required |
| NB registration | National Board number |

## 26.4 Rotation Arrows

| Location | Purpose |
|----------|---------|
| Fan shroud | Indicate blade rotation |
| Motor shaft | Match fan |
| Pump (if any) | Flow direction |

## 26.5 Tagging Checks

| Check | Requirement |
|-------|-------------|
| Equipment tag | Matches P&ID |
| All nameplates | Securely attached |
| Data accurate | Matches data sheet |
| Rotation arrows | Correct direction |
| U-stamp (if ASME) | Legible, complete |

---

# SECTION 27: SPARE PARTS *(NEW)*

## 27.1 Commissioning Spares

| Item | Quantity | Notes |
|------|----------|-------|
| Header plugs | 5% of total | Same material |
| Header gaskets | 2 sets per header | Spiral wound |
| Nozzle gaskets | 2 sets | Match flange class |
| V-belts | 2 sets per drive | Matched sets |
| Fan blades | 1 set per fan type | Complete balance |

## 27.2 Operating Spares (2-Year)

| Item | Quantity | Notes |
|------|----------|-------|
| Motor bearings | 1 set per motor | Complete set |
| Vibration switches | 10% or 2 min | Same type |
| Louver actuators | 1 per type | If louvers provided |
| Control valves | 1 per type | If steam coils |
| Filters | 6-month supply | If filtered |

## 27.3 Capital Spares

| Item | Quantity | Notes |
|------|----------|-------|
| Spare motor | 1 per size | Interchangeable |
| Speed reducer | 1 per type | If gear drive |
| Fan hub | 1 per type | Long lead |
| Header plug sheet | 1 | If corrosive service |

## 27.4 Spare Parts Checks

| Check | Requirement |
|-------|-------------|
| Spare parts list | In O&M manual |
| Recommended qtys | Per MTBF analysis |
| Lead times | Noted for long-lead items |
| Interchangeability | Cross-reference to equipment |
| Storage requirements | Climate, preservation |

---

# SECTION 28: COMPLETE MASTER CHECKLIST

## The bot should check ALL of the following automatically:

### TUBE BUNDLE:
- [ ] Header plate thickness per API 661
- [ ] Plug sheet hole pattern
- [ ] Tube wall thickness
- [ ] Fin type vs temperature rating
- [ ] Tube support spacing
- [ ] Nozzle reinforcement
- [ ] Pass partition design
- [ ] Tube-to-tubesheet joint

### PLENUM:
- [ ] Panel thickness
- [ ] Stiffener spacing
- [ ] Floor panel alignment with stiffeners
- [ ] Fan ring diameter and tip clearance
- [ ] Drain provisions
- [ ] Corner sealing
- [ ] Access provisions

### FAN & DRIVE:
- [ ] Fan coverage minimum 40%
- [ ] Blade material vs temperature
- [ ] Balance grade (AMCA 204)
- [ ] Motor HP and service factor
- [ ] Belt/gear type
- [ ] Guard coverage
- [ ] Vibration switch

### LOUVERS:
- [ ] Blade material and type
- [ ] Actuator sizing
- [ ] Linkage material
- [ ] Position indication
- [ ] Seal when closed

### WEATHER PROTECTION:
- [ ] Hood/enclosure panels
- [ ] Bug screen mesh and frame
- [ ] Hail guard open area
- [ ] Recirculation duct sizing
- [ ] Steam coil capacity

### PLATFORMS & ACCESS:
- [ ] Header walkway width and load
- [ ] Motor platform width and load
- [ ] Ballroom walkway dimensions
- [ ] Ladder rung spacing (12" OC)
- [ ] Handrail height (42")
- [ ] Toe board height (4")
- [ ] Grating bearing bar direction
- [ ] Grating clip spacing

### STRUCTURAL:
- [ ] Column sizes
- [ ] Base plate and anchor bolts
- [ ] Beam sizes and deflection
- [ ] Bracing connections
- [ ] Lifting lug capacity

### INSTRUMENTATION & CONTROLS: *(NEW)*
- [ ] Temperature sensor locations match P&ID
- [ ] Pressure gauge/transmitter connections
- [ ] Vibration switch wiring provisions (NC contact)
- [ ] VFD provisions (if variable speed)
- [ ] Control panel location and area rating
- [ ] Alarm/shutdown logic documented

### ELECTRICAL: *(NEW)*
- [ ] Motor enclosure per area classification
- [ ] Junction box ratings (NEMA 4X, XP)
- [ ] Grounding lugs on frame, motors, panels
- [ ] Cable tray/conduit routing
- [ ] Platform lighting (10 fc min)
- [ ] Heat tracing (if winterization)

### PIPING: *(NEW)*
- [ ] Nozzle flange rating per design pressure
- [ ] Nozzle projection for bolting clearance
- [ ] Vent connections at high points
- [ ] Drain connections at low points
- [ ] Thermal expansion provisions (fixed point)
- [ ] Nozzle reinforcement per ASME

### COATINGS: *(NEW)*
- [ ] Surface prep specification (SSPC-SP10 typical)
- [ ] Coating system specified (prime, intermediate, topcoat)
- [ ] Total DFT requirement (9-13 mils typical)
- [ ] Galvanizing specified (grating, handrails, fan rings)
- [ ] Touch-up requirements

### NOISE: *(NEW)*
- [ ] Guaranteed sound level specified
- [ ] Measurement location defined
- [ ] Low-noise fan (if <85 dBA required)

### TESTING: *(NEW)*
- [ ] Hydrostatic test pressure (1.5× MAWP)
- [ ] Mechanical run test (4 hr min)
- [ ] NDE requirements specified
- [ ] Performance test (if required)
- [ ] Witness points defined

### SHIPPING: *(NEW)*
- [ ] Shipping splits marked on drawings
- [ ] Max dimensions within limits
- [ ] Lift points identified and rated
- [ ] Preservation requirements specified
- [ ] Flange protection

### DOCUMENTATION: *(NEW)*
- [ ] API 661 data sheet complete
- [ ] GA drawing for approval
- [ ] Weld map and WPS/PQR
- [ ] MTRs for pressure parts
- [ ] U-1A form (if ASME stamped)
- [ ] O&M manual

### MAINTENANCE: *(NEW)*
- [ ] Bundle slide rails in structure
- [ ] Davit/monorail over fan bays
- [ ] Adequate platform clearances
- [ ] Drain valves at low points

### FOUNDATION: *(NEW)*
- [ ] Anchor bolt pattern matches base plate
- [ ] Pier size and location per civil
- [ ] Grout pocket depth (1"-1.5")
- [ ] Bolt projection (4" min)

### NAMEPLATE: *(NEW)*
- [ ] Equipment tag matches P&ID
- [ ] ASME U-stamp (if code)
- [ ] Rotation arrows on fans
- [ ] All data accurate

### SPARE PARTS: *(NEW)*
- [ ] Spare parts list provided
- [ ] Header plugs (5%)
- [ ] V-belt sets (2 per drive)
- [ ] Gasket sets (2 per header)

### CROSS-CHECKS (CRITICAL):
- [ ] All mating part holes align
- [ ] All mating part hole sizes match
- [ ] Platform holes match frame holes
- [ ] Grating fits openings
- [ ] Ladder fits platform opening
- [ ] Handrail post holes match platform
- [ ] Assembly BOM complete
- [ ] All parts accounted for
- [ ] Sensor nozzle locations match P&ID
- [ ] JB locations match conduit routing
- [ ] Nozzle orientations match piping ISO
- [ ] Anchor bolt pattern matches civil

---

**END OF COMPLETE ACHE CHECKLIST V2**

This checklist covers ALL components of a complete Air-Cooled Heat Exchanger including:
- Tube bundle, Plenum, Fans, Drives
- Louvers, Hoods, Bug screens, Hail guards, Enclosures
- Winterization, Platforms, Ladders, Walkways, Handrails, Grating
- All Structural components
- **NEW: Instrumentation & Controls**
- **NEW: Electrical System**
- **NEW: Piping Connections**
- **NEW: Surface Prep & Coatings**
- **NEW: Noise Requirements**
- **NEW: Testing Requirements**
- **NEW: Shipping & Handling**
- **NEW: Documentation Deliverables**
- **NEW: Maintenance Provisions**
- **NEW: Foundation Interface**
- **NEW: Nameplate & Tagging**
- **NEW: Spare Parts**

**Reference Standards:**
- API 661 (Air-Cooled Heat Exchangers)
- ASME Section VIII (Pressure Vessels)
- ASME B16.5 (Flanges)
- AISC (Structural Steel)
- AWS D1.1 (Structural Welding)
- OSHA 1910 (Access, Platforms, Ladders)
- AMCA 204 (Fan Balance)
- SSPC (Surface Preparation)
- ACI 318 (Concrete/Anchors)
- NEC (Electrical)
- Chart Industries (Hudson, Air-X-Changers)
