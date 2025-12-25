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
| **Phase 25 (Drawing Checker)** | **27/150** | **123** | **18%** |

**Current Focus**: Phase 25 - Drawing Checker System 🚧

---

## Phase 25: Drawing Checker System 🚧 NEW

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

### 25.5 Machining - Shaft Analysis (13 tasks)

- [x] Diameter tolerances specified
- [x] Length tolerances specified
- [x] Keyway width tolerance
- [x] Keyway depth tolerance
- [ ] **Keyway angular location** ⭐ MISSING
- [ ] **Surface finish Ra specified** ⭐ CRITICAL - MISSING
- [ ] Runout/TIR specification
- [ ] Concentricity specification
- [ ] Chamfers on shaft ends
- [ ] **Retaining ring groove width** ⚠️ VERIFY vs catalog
- [ ] Thread callouts (if applicable)
- [ ] Heat treatment requirements (C1045)
- [ ] Hardness requirements

---

### 25.6 Materials & Finishing (14 tasks)

#### Material Specifications
- [x] Material grades specified (ASTM)
- [x] Material forms correct (plate, channel, bar)
- [ ] MTR (Mill Test Report) requirements
- [ ] Charpy impact requirements (cold service)
- [ ] Z-direction properties (lamellar tearing)
- [ ] Dual certification requirements

#### Coating & Finishing
- [ ] Coating spec referenced ⚠️ S25143-C1 NOT INCLUDED
- [ ] Surface prep specification (SSPC)
- [ ] Primer specification
- [ ] Intermediate coat specification
- [ ] Topcoat specification
- [ ] DFT (Dry Film Thickness) requirements
- [ ] **Masking requirements** ⭐ CRITICAL for bearings
- [ ] Galvanizing specification (if required)

---

### 25.7 Hardware & Fasteners (11 tasks)

- [ ] **Bolt grade specified** ⭐ MISSING
- [ ] Bolt length specified
- [ ] Nut type specified
- [ ] Washer requirements
- [ ] Lock washer/Nyloc requirements
- [ ] **Torque values** ⭐ MISSING
- [ ] Pretension requirements (slip-critical)
- [ ] Thread lubricant specification
- [ ] Bearing mounting hardware
- [ ] Motor mounting hardware
- [ ] Set screw specifications (bearings)

---

### 25.8 Handling & Erection (12 tasks)

- [ ] **Lifting lugs shown** ⭐ CRITICAL - NOT SHOWN (5,605 lbs!)
- [ ] Lifting lug capacity rated
- [ ] **Center of gravity marked** ⭐ MISSING
- [ ] Rigging diagram provided
- [ ] Shipping splits identified
- [ ] Max shipping dimensions verified
- [ ] Tie-down points shown
- [ ] Skid/crating requirements
- [ ] Shop vs field assembly scope
- [ ] Erection sequence notes
- [ ] Shimming requirements
- [ ] Grouting requirements

---

### 25.9 Inspection & QC (10 tasks)

- [ ] Dimensional inspection points identified
- [ ] Critical dimensions flagged
- [ ] Hold points specified
- [ ] Witness points specified
- [ ] NDE requirements (RT/UT/MT/PT)
- [ ] Visual weld inspection (VT per AWS)
- [ ] Hydro/pressure test (if applicable)
- [ ] Balance requirements (rotating shaft)
- [ ] Runout verification requirements
- [ ] Documentation package requirements

---

### 25.10 Documentation (12 tasks)

- [x] Drawing number unique
- [x] Revision level shown
- [ ] Revision history complete
- [ ] Approval signatures present
- [x] Scale indicated
- [x] All sheets numbered
- [x] Cross-references complete
- [x] Notes legible and clear
- [x] Notes not conflicting
- [x] BOM complete
- [x] BOM matches detail drawings
- [ ] Specification references included ⚠️ Coating spec missing

---

### 25.11 Safety & Code Compliance (8 tasks)

- [ ] Sharp edge callout (break edges)
- [x] Pinch point guards (belt guard)
- [ ] Guard opening size per OSHA
- [x] Rotating equipment guard
- [ ] Lock-out/tag-out provisions
- [ ] Warning label locations
- [ ] Nameplate location
- [ ] PE stamp (if required by jurisdiction)

---

### 25.12 Cross-Part Reference Analysis ⭐ NEW CRITICAL

#### Hole Pattern Verification Matrix
| Part A | Part B | Connection | Hole Size | Status |
|--------|--------|------------|-----------|--------|
| 4A-4 (Mounting Angle) | Plenum Floor | Bolted | Ø11/16" | ❓ NEED MATING DWG |
| 4A-K (Hanger) | Plenum Wall | Bolted | Ø11/16" | ❓ NEED MATING DWG |
| 4A-A (Stringer LH) | 4A-K (Hanger) | Welded | N/A | ✅ N/A |
| 4A-N (Motor Mount) | Motor Base | Bolted | Ø3/4", Ø11/16" | ❓ VERIFY MOTOR FRAME |

#### Dimensional Fit-Up Verification
| Assembly | Part A Dim | Part B Dim | Gap/Fit | Status |
|----------|------------|------------|---------|--------|
| Stringer Spacing | 4'-4" (inside) | Cross Stiff 4'-4" | Match | ✅ PASS |
| Motor Mount Width | 4'-10 13/16" | Stringer + overhang | 3.4" each side | ✅ PASS |
| Bearing Tower Span | 4'-4" | Top Channel 4'-4" | Match | ✅ PASS |
| Belt Guard Frame | 5'-11 5/8" | Exp Metal 5'-10 3/8" | Frame wraps | ✅ PASS |

#### Tasks
- [ ] Extract all hole patterns to coordinate system
- [ ] Build mating part relationship matrix
- [ ] Calculate hole-to-hole deltas
- [ ] Verify within tolerance (±1/16" structural)
- [ ] Flag misalignments with visual callout
- [ ] Generate cross-reference report
- [ ] Request missing mating drawings (RFI)

---

### 25.13 Drawing Checker Report Generation (8 tasks)

- [x] Generate Excel report with all findings
- [x] Generate HTML dashboard with visual status
- [ ] Generate PDF annotated drawing with markups
- [ ] Color-code findings (Red/Yellow/Green)
- [ ] Include AISC/AWS standard references
- [ ] Auto-generate RFI for missing items
- [ ] Track resolution status
- [ ] Archive reports with drawing revision

---

## Drawing Checker Report Template

### Report Sections
1. **Executive Summary** - Pass/Warn/Fail counts, verdict
2. **Project Information** - Drawing number, customer, project
3. **Critical Findings** - Must-fix items before fabrication
4. **Hole Analysis** - Size, edge distance, spacing, alignment
5. **Material Verification** - Thickness, spec, finish
6. **Tolerance Analysis** - Achievability check
7. **Cross-Part Alignment** - Mating hole verification
8. **Checklist Summary** - All 150+ checks by category
9. **Recommendations** - Prioritized action items
10. **Standards Referenced** - AISC, AWS, OSHA, ASME

### Status Symbols
| Symbol | Meaning |
|--------|---------|
| ✅ | Checked - PASS |
| ⚠️ | Checked - ISSUE FOUND |
| ❓ | NOT YET CHECKED |
| ❌ | MISSING FROM DRAWING |

---

## Sample Analysis: S25143-4A Machinery Mount Assembly

### Assembly Overview
- **Drawing**: S25143-4A (26 sheets)
- **Customer**: Industrial Technologies & Services LLC
- **Project**: 119JAO / P.O. 12406404
- **Weight**: 5,604.91 lbs
- **Material**: A572-50, C1045, A53, A1011-33

### Check Results Summary
| Category | Checked | Issues | Not Checked | Missing |
|----------|---------|--------|-------------|---------|
| Geometry & Dimensions | 8 | 2 | 8 | 4 |
| Structural Adequacy | 0 | 0 | 9 | 1 |
| Fabrication Feasibility | 2 | 0 | 8 | 6 |
| Welding | 2 | 1 | 8 | 5 |
| Machining (Shaft) | 4 | 1 | 2 | 6 |
| Materials & Finishing | 2 | 1 | 0 | 9 |
| Hardware & Fasteners | 0 | 0 | 2 | 9 |
| Handling & Erection | 0 | 0 | 4 | 8 |
| Inspection & QC | 0 | 0 | 4 | 6 |
| Documentation | 7 | 2 | 2 | 0 |
| Safety & Code | 2 | 0 | 2 | 4 |
| **TOTAL** | **27** | **7** | **49** | **58** |

### Top 10 Critical Missing Items
| Priority | Item | Impact |
|----------|------|--------|
| 1 | Lifting lugs/CG location | Safety - 5,605 lb assembly |
| 2 | Surface finish on shaft journals | Bearing life/failure |
| 3 | Bolt specifications | Assembly/maintenance |
| 4 | Coating specification (S25143-C1) | Corrosion protection |
| 5 | NDE requirements | Weld quality assurance |
| 6 | Shaft runout/concentricity | Vibration/bearing wear |
| 7 | Masking requirements | Coating on bearing seats |
| 8 | Preheat requirements | Weld quality |
| 9 | Torque values | Proper assembly |
| 10 | Plenum interface drawings | Hole alignment verification |

### Hole Analysis Summary
| Drawing | Part | Hole Size | Standard? | Edge Dist | Status |
|---------|------|-----------|-----------|-----------|--------|
| 4A-4 | Mounting Angle | Ø11/16" | ✅ Yes | 1-13/16" | ✅ PASS |
| 4A-A | Stringer LH | Ø3/4" | ✅ Yes | 1-1/2" | ✅ PASS |
| 4A-K | Hanger PRC | Ø11/16" | ✅ Yes | 3/4" | ⚠️ TIGHT |
| 4A-J | Bearing Top | Ø1/2" | ✅ Yes | 1/2" | ⚠️ CHECK |
| 4A-N | Motor Mount | Ø11/16" | ✅ Yes | 7/8" | ⚠️ CHECK |

### Material Verification
| Part | Material | Thickness | Standard | Status |
|------|----------|-----------|----------|--------|
| Stringers | C15×33.9 A572-50 | Web 0.400" | AISC | ✅ PASS |
| Plates | A572-50 | 1/4" | ASTM | ✅ PASS |
| Shaft | C1045 | Ø2-15/16" | SAE | ✅ PASS |
| Sheet | 10GA A1011-33 | 0.1345" | ASTM | ✅ PASS |
| Exp Metal | 13GA | 0.090" | - | ✅ PASS |

### Bend Radii Check
| Part | Material | Thickness | Bend R | Min (1×t) | Status |
|------|----------|-----------|--------|-----------|--------|
| 4A-U | 10GA Steel | 0.1345" | R1/4" | R0.135" | ✅ PASS (1.9×t) |

---

## Phase 24: ACHE Design Assistant (COMPLETE SCOPE) 🚧

**Goal**: Auto-launch chatbot when SolidWorks opens with comprehensive model overview, checks, and AI-powered design recommendations for Air-Cooled Heat Exchangers - covering EVERY component.

---

### 24.1 Auto-Launch System (5 tasks)
- [ ] SolidWorks process watcher
- [ ] Auto-open chatbot URL when SW detected
- [ ] Document change detection (Part/Assembly/Drawing switch)
- [ ] WebSocket real-time updates to web UI
- [ ] Tailscale connection handling

---

### 24.2 Model Overview Tab (8 tasks)
- [ ] Visual Preview (screenshots: isometric, front, side, top views)
- [ ] Quick Stats dashboard (parts count, weight, dimensions, fasteners)
- [ ] ACHE Bundle Structure Diagram visualization
- [ ] Warnings Summary (quick view of issues)
- [ ] Linked Documents list
- [ ] Configuration selector
- [ ] Real-time refresh indicator
- [ ] Export overview as PDF

---

### 24.3-24.7 Properties Extraction (65 tasks)
Standard, Mass, Custom, ACHE-Specific, Additional properties - see detailed breakdown in previous version.

---

### 24.8-24.21 Analysis & Calculations (156 tasks)
Component Analysis, Mates, Interference, Sheet Metal, Holes, Calculations, Thermal, Instrumentation, Nozzles, Welds, Drawings, Manufacturing, Shipping, QC - see detailed breakdown in previous version.

---

## STRUCTURAL COMPONENTS (COMPLETE)

### 24.22 Plenum Chamber Analysis (15 tasks)
- [ ] Plenum type identification (box type, slope-sided)
- [ ] Plenum depth verification (min 915mm / 36" per API 661)
- [ ] Plenum material and thickness
- [ ] Plenum volume calculation
- [ ] Air distribution uniformity analysis
- [ ] Plenum drains, access doors, seals
- [ ] Plenum-to-bundle connection
- [ ] Plenum structural bracing
- [ ] Plenum coating/galvanizing
- [ ] Plenum lifting lugs
- [ ] Plenum partition plates (multi-service)
- [ ] Plenum rain hood integration

---

### 24.23 Mechanical Drive Support System (18 tasks)

#### Motor Mount & Support Structure
- [ ] **Mechanical drive support system** - steel structural system for fan drive
- [ ] **Motor support beam(s)** - beam that motor mounts to
- [ ] Motor support beam span and connection verification
- [ ] **Drive mount / machinery mount** - platform where motor/speed reducer mounts
- [ ] **Drive pedestal** (induced draft - motor below bundle)
- [ ] Motor/gearbox **common structure** (per API 661 for gear drives)
- [ ] Vibration isolator pads/mounts

#### Fan Support Structure (Induced Draft)
- [ ] **Fan bridge / cross beam** - structural beam across plenum for induced draft
- [ ] Fan ring support structure
- [ ] **Hub assembly platform / machinery housing** - structure supporting fan hub
- [ ] **Extended drive shaft** (induced draft - motor below, fan above)
- [ ] **Shaft bearing housing** and supports
- [ ] Shaft guard / coupling guard
- [ ] Pony motor / jack shaft arrangement (if applicable)

#### Maintenance & Removal Provisions
- [ ] **Lifting beams / motor removal beams** - permanent beams for removal
- [ ] **Monorail and hoist arrangement** - for fan/motor/gearbox maintenance
- [ ] **Trolley beam** for component removal
- [ ] Davit crane or jib crane provisions
- [ ] Component weights for lifting (per API 661 drawing requirements)

---

### 24.24 Fan System Analysis (20 tasks)

#### Fan Assembly
- [ ] Fan diameter, blade material (aluminum, FRP, steel)
- [ ] Number of blades, pitch (fixed vs adjustable)
- [ ] Fan blade tip clearance (per API 661 Table 6)
- [ ] Fan ring/shroud diameter and material
- [ ] Fan coverage ratio (min 40%), dispersion angle (max 45°)
- [ ] Fan hub seal disc, inlet bell/rounded ring

#### Fan Drive
- [ ] Motor type, size (HP/kW), enclosure (TEFC, Ex-proof)
- [ ] V-belt drive (max 30kW/40HP per API 661)
- [ ] HTD timing belt drive (max 45kW/60HP)
- [ ] Right-angle gear drive (required >45kW/60HP)
- [ ] Belt guard / transmission guard
- [ ] Service factor (V-belt: 1.4, HTD: 1.8-2.0)

---

### 24.25 Fan Control Systems (15 tasks)
- [ ] Auto-variable pitch hub, pneumatic/electric/hydraulic actuators
- [ ] Pitch range (positive and negative step)
- [ ] VFD compatibility, enclosure rating (NEMA 3R, 4X)
- [ ] Two-speed motor, on/off sequencing
- [ ] Vibration switch/transmitter verification

---

### 24.26 Louver System Analysis (20 tasks)
- [ ] Inlet louvers (forced draft), outlet louvers (induced draft)
- [ ] Louver blade type (parallel, opposed action)
- [ ] Frame material, TFE bushings, torque tube
- [ ] Manual, pneumatic, electric actuators
- [ ] Fail-safe position, control signal, position feedback

---

### 24.27 Screens & Guards Analysis (18 tasks)
- [ ] Hail guards - material, mesh, mounting, pressure drop
- [ ] Bug/insect screens - 16-20 mesh, 2× clean pressure drop per API 661
- [ ] Lint/cottonwood screens
- [ ] Fan guards - OSHA compliant, personnel protection
- [ ] Belt guards - enclosed, non-sparking material

---

### 24.28 Walkways & Platforms (25 tasks) ⭐ EXPANDED

#### Header Walkway (Piperack End)
- [ ] Walkway width (min 18" clear per OSHA)
- [ ] Walkway length and elevation
- [ ] Walkway structural support

#### Fan Maintenance Walkway / Catwalk
- [ ] Catwalk width (min 18" per OSHA)
- [ ] Catwalk load rating (50 psf minimum)
- [ ] Catwalk material (steel grating, checkered plate)

#### Actuator Walkway (Separate Level) ⭐ NEW
- [ ] Actuator walkway location and dimensions
- [ ] Actuator walkway support structure
- [ ] Actuator walkway grating layout

#### Walkway Supports ⭐ NEW (from M180)
- [ ] **WW_SUPPORT** - main walkway support members
- [ ] **WW_SUPPORT_BRACE** - diagonal bracing for walkway supports
- [ ] **WW_SUPPORT_BEAM** - horizontal beam connecting supports
- [ ] Support-to-column tab connections
- [ ] Support-to-plenum tab connections
- [ ] Support gusset plates

#### Flooring / Grating
- [ ] Grating type (welded bar, press-lock)
- [ ] Grating bar size and spacing
- [ ] Grating bearing bar direction
- [ ] Grating load rating
- [ ] Grating material (galvanized, painted, aluminum)
- [ ] **Grating clips (B-CLIP)** - quantity and type ⭐ NEW
- [ ] Grating layout drawings (mechanical walkway vs actuator walkway) ⭐ NEW
- [ ] Checkered plate locations (solid flooring areas)
- [ ] Slip-resistant surface verification

---

### 24.29 Handrails & Safety (22 tasks) ⭐ EXPANDED

#### Top Rail
- [ ] Top rail height (42" ± 3" per OSHA 1910.29)
- [ ] Top rail material (pipe, tube, angle)
- [ ] Top rail diameter (1.25" - 2" graspable)
- [ ] Top rail smooth surface (no snag hazards)

#### Mid Rail
- [ ] Mid rail height (21" typical - midway)
- [ ] Mid rail material and spacing

#### Toe Board / Kick Plate
- [ ] Toe board height (min 3.5" per OSHA)
- [ ] Toe board material
- [ ] Toe board gap to floor (max 0.25")
- [ ] **Toe guard support angle** ⭐ NEW (from M180)

#### Safety Gates
- [ ] Self-closing gate at ladder access (e.g., Intrepid UDG-27)
- [ ] Gate swing direction (away from opening)
- [ ] Gate latch mechanism
- [ ] Gate top rail and mid rail

#### Corner Posts & Supports
- [ ] Post spacing (max 8 ft typical)
- [ ] Post material and size
- [ ] Post base plate mounting
- [ ] Post splice connections
- [ ] Handrail-to-platform connections
- [ ] Toe guard-to-handrail post connections

---

### 24.30 Ladders (15 tasks)

#### Vertical Ladders
- [ ] Ladder width (min 16" clear)
- [ ] Rung spacing (max 12" uniform)
- [ ] Rung diameter (0.75" - 1.125")
- [ ] Side rail extension (42" above landing)
- [ ] Ladder offset from wall (7" min)

#### Ladder Cage
- [ ] Cage required (>20 ft unbroken length)
- [ ] Cage start height (7-8 ft from base)
- [ ] Cage hoop spacing (max 4 ft)
- [ ] Cage vertical bar spacing (max 9.5")
- [ ] Rest platform spacing (max 35 ft vertical)

#### Ladder Safety & Mounting
- [ ] Ladder angle (75-90° from horizontal)
- [ ] Landing platform at top
- [ ] Ladder fall arrest system (alternative to cage)
- [ ] Ladder material (galvanized, aluminum)
- [ ] Ladder-to-platform tab connections
- [ ] Ladder-to-handrail connections

---

### 24.31 Stairs (12 tasks)
- [ ] Stair angle (30-50° per OSHA)
- [ ] Tread depth (min 9.5")
- [ ] Riser height (max 9.5", uniform)
- [ ] Stair width (min 22" typical)
- [ ] Stair rail height (30-37" per OSHA)
- [ ] Handrail both sides (if >44" wide)
- [ ] Stair landing dimensions
- [ ] Slip-resistant treads
- [ ] Open riser vs closed riser
- [ ] Intermediate landings (every 12 ft vertical)
- [ ] Stair stringer material
- [ ] Stair attachment to structure

---

### 24.32 Structure & Support (25 tasks) ⭐ EXPANDED

#### Main Structure - Columns
- [ ] Column identification (COLUMN_1 through COLUMN_n)
- [ ] Column material and size (W-shape typical)
- [ ] Column base plate design
- [ ] Anchor bolt pattern and size
- [ ] Column spacing

#### Main Structure - Beams
- [ ] Floor beam identification (FLOOR_BEAM_1 through FLOOR_BEAM_n)
- [ ] Beam material and size
- [ ] Beam-to-column connections

#### Bracing System ⭐ EXPANDED
- [ ] **Knee braces** (KNEE_BRACE_1, KNEE_BRACE_2)
- [ ] **Knee brace gussets** ⭐ NEW
- [ ] **X-braces** (X_BRACE_1, X_BRACE_2) ⭐ NEW
- [ ] **Brace spacers** ⭐ NEW
- [ ] Cross bracing design and connections

#### Bundle Support
- [ ] Side frame material
- [ ] Side frame connection to structure
- [ ] Bundle guide rails
- [ ] Bundle slide-out clearance
- [ ] Bundle lifting provisions

#### Piperack Integration
- [ ] Piperack connection details
- [ ] Load transfer to piperack
- [ ] Expansion/contraction allowance
- [ ] Piperack elevation coordination

#### Surface Treatment
- [ ] Structure surface prep (SSPC-SP6, SP10)
- [ ] Painting system (primer, intermediate, topcoat)
- [ ] Hot-dip galvanizing option

---

### 24.33-24.34 Enclosures & Winterization (27 tasks)
Recirculation, rain hoods, noise enclosures, steam coils, auto-variable fans

---

### 24.35-24.43 AI Features & Integration (66 tasks)
Standards compliance, recommendations, reports, cost estimation, notifications, chat, mobile

---

## NEW SECTIONS ⭐

### 24.44 Fastener Analysis (15 tasks) ⭐ NEW

#### Structural Bolts
- [ ] **A325 bolt identification** (Type 1, HDG)
- [ ] Bolt diameter × length matrix extraction
- [ ] Bolt grade verification (A325 for structural)
- [ ] Hot-dip galvanized (HDG) verification
- [ ] Bolt torque requirements

#### Washers
- [ ] **F436 hardened washer** requirements
- [ ] **Bevel washer** identification (ASME B18.23.1) for sloped surfaces
- [ ] Flat washer quantity per connection (typically 2)
- [ ] Lock washer requirements

#### Specialty Fasteners
- [ ] **Carriage bolts** (CAR) applications
- [ ] Grating clips (B-CLIP) - type and quantity
- [ ] Self-tapping screws (if any)

#### Fastener Documentation
- [ ] Fastener count by size/type/grade
- [ ] Fastener weight calculation
- [ ] Fastener material certifications (MTR)
- [ ] Fastener procurement list generation

---

### 24.45 Connection Details (12 tasks) ⭐ NEW

#### Column Connections
- [ ] **Column splice connections** - bolt size/qty per drawing notes
- [ ] **Column-to-floor beam connections**
- [ ] **Column-to-knee brace connections**
- [ ] Column gusset-to-X brace connections

#### Brace Connections
- [ ] Knee brace gusset-to-knee brace
- [ ] Knee brace-to-plenum gusset
- [ ] Knee brace gusset-to-floor beam
- [ ] X-brace-to-X-brace + spacer

#### Platform & Walkway Connections
- [ ] **Platform-to-WW_support connections**
- [ ] **Handrail-to-platform connections**
- [ ] **Toe guard-to-handrail post connections**
- [ ] **Ladder-to-platform connections**

#### Connection Notes Extraction
- [ ] Parse drawing notes for fastener specs per connection type
- [ ] Generate connection schedule from drawing notes

---

### 24.46 Field Erection Support (8 tasks) ⭐ NEW

- [ ] Field erection sequence identification
- [ ] Shop assembly vs field erection split
- [ ] Shipping split identification
- [ ] Field bolt list generation
- [ ] Erection weight by lift
- [ ] Rigging requirements
- [ ] Field weld identification
- [ ] Touch-up paint requirements

---

## Complete ACHE Component Checklist

| Component Category | Sub-Components |
|-------------------|----------------|
| **Tube Bundle** | Tubes, fins, tube supports, tube keepers, side frames, tube sheets |
| **Header Box** | Plug sheet, cover plate, bonnet, pass partitions, gaskets, plugs |
| **Plenum** | Box plenum, slope-sided plenum, partitions, drains, access doors |
| **Fan System** | Fan blades, fan hub, fan ring, inlet bell, hub seal disc |
| **Mechanical Drive Support** | Motor support beam, drive mount, drive pedestal, fan bridge, machinery housing |
| **Fan Drive** | Motor, V-belt, HTD belt, gear drive, sheaves, belt guard |
| **Removal/Maintenance** | Lifting beams, monorail, trolley beam, davit crane, hoist |
| **Fan Control** | Variable pitch hub, VFD, pneumatic/electric actuator |
| **Louvers** | Inlet louvers, outlet louvers, blades, frame, torque tube, actuators |
| **Screens** | Hail guard, bug screen, lint screen |
| **Guards** | Fan guard, belt guard, transmission guard |
| **Walkways** | Header walkway, fan walkway, actuator walkway, catwalk |
| **Walkway Supports** | WW_SUPPORT, WW_SUPPORT_BRACE, WW_SUPPORT_BEAM ⭐ NEW |
| **Flooring** | Bar grating, checkered plate, toe plates, B-clips |
| **Handrails** | Top rail, mid rail, posts, corner assemblies |
| **Safety** | Toe boards, toe guard support angle, safety gates, kick plates |
| **Ladders** | Side rails, rungs, cage hoops, cage bars, rest platforms |
| **Stairs** | Stringers, treads, risers, handrails, landings |
| **Structure** | Columns, floor beams, knee braces, X-braces, gussets, spacers |
| **Enclosures** | Recirculation enclosure, rain hood, noise enclosure |
| **Winterization** | Steam coils, heaters, recirculation ducts, auto-variable fans |
| **Instrumentation** | Thermowells, pressure taps, TI, PI, TT, PT, vibration switch |
| **Nozzles** | Inlet, outlet, vent, drain, utility connections |
| **Fasteners** | A325 bolts, F436 washers, bevel washers, carriage bolts, B-clips ⭐ NEW |
| **Connections** | Splice, brace, platform, handrail, ladder connections ⭐ NEW |

---

## Standards Database Requirements

| Standard | Purpose | Key Sections |
|----------|---------|--------------| 
| **API 661** | Air-Cooled Heat Exchangers | Table 6 (tip clearance), para 4.2.3 (fan), drive assembly |
| **ASME VIII Div 1** | Pressure Vessel Design | UG-27, UG-32, UG-34, UG-37, UG-40 |
| **TEMA** | Shell & Tube HX Standards | Classes R/C/B, Section 6 (vibration) |
| **AWS D1.1** | Structural Welding (USA) | Weld sizes, joint types, WPS |
| **CSA W59** | Welded Steel Construction (Canada) ⭐ NEW | Canadian welding requirements |
| **CSA W47.1** | Certification of Welding (Canada) ⭐ NEW | Welder qualification |
| **CSA W48** | Filler Metals (Canada) ⭐ NEW | Welding consumables |
| **ASME B16.5** | Flanges | Dimensions, ratings |
| **ASTM A325** | Structural Bolts ⭐ NEW | Type 1, HDG, torque |
| **ASTM F436** | Hardened Washers ⭐ NEW | For A325/A490 bolts |
| **ASME B18.23.1** | Bevel Washers ⭐ NEW | Sloped surface connections |
| **AISC 360** | Steel Construction ⭐ NEW | Table J3.4 edge distances, connections |
| **AISC Steel Manual** | Design Tables ⭐ NEW | Channel, angle, plate properties |
| **OSHA 1910.25** | Stairways | Angle, tread, riser |
| **OSHA 1910.27** | Ladders | Width, rungs, cage |
| **OSHA 1910.28** | Fall Protection | 4 ft trigger |
| **OSHA 1910.29** | Guardrails | 42" top rail, 21" mid rail |
| **SSPC** | Surface Prep ⭐ NEW | SP6, SP10, SP-COM |
| **ANSI B46.1** | Surface Finish ⭐ NEW | Ra measurements |

---

## Example Drawing Component Mapping (M180-10AF)

| Drawing Item | Part Number Pattern | Task.md Section |
|--------------|---------------------|-----------------|
| COLUMN_1-6 | 25A-1 to 25A-6 | 24.32 Structure |
| FLOOR_BEAM_1-7 | 25A-7 to 25A-13 | 24.32 Structure |
| KNEE_BRACE_1-2 | 25A-14, 25A-15 | 24.32 Structure |
| KNEE_BRACE_GUSSET | 25A-16 | 24.32 Structure |
| X_BRACE_1-2 | 25A-17, 25A-18 | 24.32 Structure |
| SPACER | 25A-19 | 24.32 Structure |
| SHOP_ASSEMBLY | 10AS | 24.22-24.24 |
| WW_HANDRAIL_1-10 | 28A-1, 28A-2, etc. | 24.29 Handrails |
| WW_TOE_GUARD_1-8 | 28A-3, 28A-4, etc. | 24.29 Handrails |
| GRATING_1-18 | 28A-5 to 28A-47 | 24.28 Walkways |
| PLATFORM_1-5 | 28A-11 to 28A-37 | 24.28 Walkways |
| WW_SUPPORT_1-4 | 28A-30, 28A-31, etc. | 24.28 Walkways |
| WW_SUPPORT_BRACE_1-3 | 28A-32, 28A-33, 28A-51 | 24.28 Walkways |
| WW_SUPPORT_BEAM | 28A-50 | 24.28 Walkways |
| LADDER_1-2 | 28A10-10, 28A10-11 | 24.30 Ladders |
| GATE_SAFETY | 41495 (Intrepid UDG-27) | 24.29 Handrails |
| B-CLIP | 72585 | 24.44 Fasteners |
| A325 BOLTS | 15421-15440 | 24.44 Fasteners |
| F436 WASHERS | 16713, 16716 | 24.44 Fasteners |
| BEVEL WASHER | 16642 | 24.44 Fasteners |
| CARRIAGE BOLT | 58268 | 24.44 Fasteners |

---

## Drawing Checker Implementation Notes

### PDF Extraction Pipeline
```
1. PDF → PyMuPDF (text extraction)
2. Text → Dimension Parser (regex for fractions, decimals)
3. Dimensions → Coordinate System Mapping
4. Coordinates → Cross-Part Comparison
5. Comparison → Tolerance Check (±1/16" structural)
6. Results → Report Generation (Excel, HTML, PDF)
```

### Key Regex Patterns
```python
# Fractional dimensions: 1'-7 7/16", 4'-10 13/16"
FRACTION_DIM = r"(\d+)'[-\s]?(\d+)\s*(\d+)/(\d+)\""

# Decimal dimensions: 0.1345", 2.9375"
DECIMAL_DIM = r"(\d+\.?\d*)\""

# Hole callouts: Ø11/16", Ø3/4" (TYP)
HOLE_CALLOUT = r"[ØⰀ](\d+)/(\d+)\"?\s*\(?TYP\)?"

# Tolerance: +0.003/-0.000
TOLERANCE = r"\+(\d+\.?\d*)/[-–](\d+\.?\d*)"
```

### Standards Database Queries
```python
# Edge distance lookup
def get_min_edge_distance(hole_dia, bolt_dia):
    """Per AISC Table J3.4"""
    return AISC_EDGE_DISTANCE[bolt_dia]

# Hole spacing lookup  
def get_min_hole_spacing(hole_dia):
    """Per AISC - min 2.67d"""
    return 2.67 * hole_dia

# Bend radius lookup
def get_min_bend_radius(thickness, material):
    """1×t for mild steel, 2×t for high strength"""
    return thickness * BEND_FACTOR[material]
```

---

**Total Tasks**: 490 (340 ACHE + 150 Drawing Checker)
**Estimated Effort**: 490-580 hours (~12-15 weeks)
**Last Updated**: Dec 25, 2025
