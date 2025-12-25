# Project Vulcan: Active Task List

**Status**: Phase 24 - ACHE Design Assistant (COMPLETE SCOPE)
**Last Updated**: Dec 25, 2025
**Overall Health**: 9.9/10 (Production Deployment Ready)

**Use Case**: Personal AI assistant for engineering projects at work
- CAD model validation and design checking (130+ validators active)
- Trading analysis and journal keeping
- Work automation and productivity
- Learning loop to improve over time (LIVE)
- **NEW**: Auto-launch chatbot when SolidWorks opens with full model overview

---

## Progress Summary

| Category | Tasks Complete | Tasks Remaining | % Done |
|----------|----------------|-----------------|--------|
| Phase 19 (Foundation) | 24/25 | 1 (blocked) | 96% |
| Phase 20 (Strategy System) | 12/12 | 0 | 100% |
| Phase 21 (Enhancements) | 12/12 | 0 | 100% |
| Phase 22 (CAD Events) | 3/3 | 0 | 100% |
| Phase 23 (Render Deploy) | 6/6 | 0 | 100% |
| Phase 24 (ACHE Design Assistant) | 0/287 | 287 | 0% |

**Current Focus**: Phase 24 - ACHE Design Assistant (COMPLETE SCOPE) 🚧

---

## Phase 24: ACHE Design Assistant (COMPLETE SCOPE) 🚧

**Goal**: Auto-launch chatbot when SolidWorks opens with comprehensive model overview, checks, and AI-powered design recommendations for Air-Cooled Heat Exchangers - covering EVERY component.

---

### 24.1 Auto-Launch System (5 tasks)
- [ ] SolidWorks process watcher (`desktop_server/watchers/solidworks_watcher.py`)
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

### 24.3 Properties Extraction - Standard Properties (8 tasks)
- [ ] File Name, Path, Extension
- [ ] Configuration name (active and all available)
- [ ] Created Date, Last Modified Date
- [ ] Last Saved By (author)
- [ ] SolidWorks Version
- [ ] Total Edit Time
- [ ] File Size
- [ ] Rebuild Status (up to date, needs rebuild)

---

### 24.4 Properties Extraction - Mass Properties (10 tasks)
- [ ] Mass (kg/lbs)
- [ ] Volume (m³/in³)
- [ ] Surface Area (m²/in²)
- [ ] Density (average)
- [ ] Center of Mass (X, Y, Z coordinates)
- [ ] Moments of Inertia (Ixx, Iyy, Izz)
- [ ] Products of Inertia (Ixy, Ixz, Iyz)
- [ ] Principal Axes of Inertia
- [ ] Bounding Box dimensions (L × W × H)
- [ ] Mass properties by configuration

---

### 24.5 Properties Extraction - Custom Properties (15 tasks)

#### Job Information
- [ ] Job Number
- [ ] Customer Name
- [ ] Project Name
- [ ] PO Number
- [ ] Item/Tag Number
- [ ] Service Description
- [ ] Unit/Area

#### Design Data
- [ ] Design Code (ASME VIII Div 1, etc.)
- [ ] Design Pressure
- [ ] Design Temperature
- [ ] Operating Pressure
- [ ] Operating Temperature
- [ ] Test Pressure (Hydro)
- [ ] MDMT (Minimum Design Metal Temperature)
- [ ] Corrosion Allowance

---

### 24.6 Properties Extraction - ACHE-Specific Properties (20 tasks)

#### Tube Bundle Data
- [ ] Number of Tubes
- [ ] Tube OD
- [ ] Tube BWG (wall thickness)
- [ ] Tube Length
- [ ] Tube Material (spec &amp; grade)
- [ ] Tube Pitch
- [ ] Pitch Pattern (triangular/square)
- [ ] Number of Rows
- [ ] Number of Passes
- [ ] Tubes Per Row

#### Fin Data
- [ ] Fin Type (L-foot, embedded, extruded, wrap-on)
- [ ] Fin Height
- [ ] Fin Thickness
- [ ] Fin Density (fins per inch)
- [ ] Fin Material (aluminum, steel)

#### Header Box Data
- [ ] Header Type (plug, cover plate, bonnet)
- [ ] Header Material
- [ ] Header Thickness
- [ ] Plug Type (shoulder, taper)
- [ ] Plug Material

---

### 24.7 Properties Extraction - Additional Properties (12 tasks)

#### Structural Data
- [ ] Tube Sheet Material
- [ ] Tube Sheet Thickness
- [ ] Tube-to-Tubesheet Joint Type (rolled, welded, strength welded)
- [ ] Side Frame Material
- [ ] Tube Support Material
- [ ] Tube Support Quantity
- [ ] Tube Support Spacing (max 1.83m per API 661)

#### Drawing Information
- [ ] Drawing Number
- [ ] Revision
- [ ] Revision Date
- [ ] Revision Description
- [ ] Drawn By / Checked By / Approved By

---

### 24.8 Component Analysis (10 tasks)
- [ ] BOM extraction with quantities (auto-aggregate)
- [ ] Weight Breakdown by component type (visual bar chart)
- [ ] Fastener Summary (bolts, nuts, plugs by size/material/qty)
- [ ] Material Summary (by spec, total weight, components list)
- [ ] Revision Comparison (Rev A vs Rev B changes)
- [ ] Component count by type (plates, tubes, fasteners, etc.)
- [ ] Duplicate part detection
- [ ] Missing part number detection
- [ ] Orphan component detection (not in BOM)
- [ ] Configuration-specific BOM comparison

---

### 24.9 Mates &amp; Constraints Analysis (6 tasks)
- [ ] Mate Status summary (satisfied, over-defined, broken)
- [ ] Broken mate identification with component names
- [ ] Over-defined mate detection
- [ ] Fix suggestions for broken mates
- [ ] Mate count by type (coincident, concentric, distance, etc.)
- [ ] Redundant mate detection

---

### 24.10 Interference Detection (6 tasks)
- [ ] Run interference check on demand
- [ ] Display interference results (component pairs)
- [ ] Interference volume calculation
- [ ] Interference location visualization
- [ ] Coincident face detection
- [ ] Clearance analysis (minimum gaps)

---

### 24.11 Sheet Metal &amp; Bend Radius Analysis (10 tasks)
- [ ] Bend Radius Analyzer
- [ ] Material-based minimum bend radius lookup table
- [ ] K-Factor display and validation
- [ ] Bend Allowance calculation
- [ ] Bend Deduction calculation
- [ ] Grain Direction warnings (bend parallel vs perpendicular)
- [ ] Flat Pattern accuracy verification
- [ ] Auto-fix radius suggestions
- [ ] Bend sequence recommendation
- [ ] Springback compensation notes

---

### 24.12 Hole Location Analysis (12 tasks)
- [ ] Hole Pattern Extractor
- [ ] Tube Sheet hole pattern verification (pitch, rows, count)
- [ ] Edge Distance checks (minimum 1.5× diameter per TEMA)
- [ ] Ligament checks (minimum per TEMA)
- [ ] Mating Hole Alignment checker (header ↔ tube sheet)
- [ ] Bolt Circle verification (per ASME B16.5)
- [ ] Hole schedule export
- [ ] Hole tolerance verification (+0.003/-0.000 typical)
- [ ] Countersink/counterbore detection
- [ ] Threaded hole identification (NPT, UNC, etc.)
- [ ] Hole centerline alignment verification
- [ ] Pattern symmetry check

---

### 24.13 Calculations &amp; Verification (12 tasks)
- [ ] Tube Sheet thickness calc (ASME UG-34)
- [ ] Header Box thickness calc (ASME UG-32)
- [ ] Nozzle Reinforcement area calc (ASME UG-37/UG-40)
- [ ] Nozzle Reinforcement limits verification (UG-40)
- [ ] Tube Vibration - Natural Frequency calc
- [ ] Tube Vibration - Vortex Shedding check
- [ ] Tube Vibration - Fluidelastic Instability check
- [ ] Tube Vibration - Acoustic Resonance check
- [ ] Margin percentage display (actual vs required)
- [ ] MAWP (Maximum Allowable Working Pressure) calc
- [ ] Hydrostatic Test Pressure calc
- [ ] Minimum Required Thickness calc

---

### 24.14 Thermal &amp; Pressure Analysis (10 tasks)
- [ ] Thermal expansion calculation
- [ ] Thermal growth at design temperature
- [ ] Thermal stress analysis summary
- [ ] Sliding support requirements
- [ ] Bundle expansion allowance verification (min 6mm per API 661)
- [ ] Header box thermal stress
- [ ] Pressure drop estimation
- [ ] Operating vs Design pressure comparison
- [ ] Temperature classification verification
- [ ] PWHT (Post-Weld Heat Treatment) requirements check

---

### 24.15 Instrumentation &amp; Connections (12 tasks)

#### Temperature Connections
- [ ] Thermowell locations identification
- [ ] Thermowell insertion length verification
- [ ] Temperature indicator (TI) locations
- [ ] Temperature transmitter (TT) connections
- [ ] Skin temperature sensor locations

#### Pressure Connections
- [ ] Pressure tap locations
- [ ] Pressure indicator (PI) locations
- [ ] Pressure transmitter (PT) connections
- [ ] Test connection locations

#### Vents, Drains &amp; Utilities
- [ ] Vent connection locations and sizes
- [ ] Drain connection locations and sizes
- [ ] Utility connection locations (cleaning, purging)

---

### 24.16 Nozzle &amp; Flange Analysis (10 tasks)
- [ ] Nozzle schedule extraction
- [ ] Nozzle size verification
- [ ] Flange rating verification (150#, 300#, etc.)
- [ ] Nozzle projection verification
- [ ] Nozzle reinforcement pad sizing
- [ ] Nozzle orientation verification (clock position)
- [ ] Nozzle load verification (WRC 107/297)
- [ ] Gasket selection verification
- [ ] Flange facing type verification (RF, RTJ, FF)
- [ ] Bolt sizing verification per flange rating

---

### 24.17 Weld Analysis (10 tasks)
- [ ] Weld symbol extraction from drawings
- [ ] Weld size verification (per AWS D1.1)
- [ ] Weld length calculations
- [ ] Weld volume/weight estimation
- [ ] Joint type identification (butt, fillet, groove, etc.)
- [ ] WPS mapping (which WPS for which weld)
- [ ] Weld efficiency factor verification
- [ ] Full penetration vs partial penetration identification
- [ ] Weld NDE requirements mapping (RT, UT, MT, PT)
- [ ] Maximum weld hardness verification (per API 661)

---

### 24.18 Drawing-Specific Analysis (12 tasks)
- [ ] Dimension extraction from drawings (key dims)
- [ ] GD&amp;T parsing and verification
- [ ] View alignment verification
- [ ] Scale verification per sheet
- [ ] Balloon/BOM cross-reference check
- [ ] Section view validation
- [ ] Detail view completeness check
- [ ] Title block completeness verification
- [ ] Revision block accuracy
- [ ] General notes completeness
- [ ] Bill of Materials completeness
- [ ] Reference document list verification

---

### 24.19 Manufacturing &amp; Fabrication Notes (10 tasks)
- [ ] Welding Notes extraction (WPS requirements)
- [ ] Machining Notes (surface finish, tolerances)
- [ ] Assembly Notes (tube insertion method, bolt torque)
- [ ] Testing Requirements (hydro, leak, NDE)
- [ ] Surface Preparation requirements (SSPC spec)
- [ ] Painting/Coating requirements
- [ ] PWHT requirements
- [ ] Forming requirements
- [ ] Fit-up tolerances
- [ ] Inspection hold points

---

### 24.20 Shipping &amp; Handling (8 tasks)
- [ ] Shipping Dimensions (L × W × H)
- [ ] Shipping Weight (with crating/skid)
- [ ] Over-dimensional flag
- [ ] Lifting Points and capacity
- [ ] Center of Gravity location
- [ ] Spreader bar requirements
- [ ] Preservation requirements
- [ ] Shipping orientation requirements

---

### 24.21 Quality &amp; Inspection (8 tasks)
- [ ] NDE requirements summary (RT, UT, MT, PT)
- [ ] Inspection hold points list
- [ ] MTR (Material Test Report) requirements
- [ ] Hydrostatic test requirements
- [ ] Pneumatic/leak test requirements
- [ ] Witness points identification
- [ ] Third-party inspection requirements
- [ ] Code stamping requirements (U stamp, etc.)

---

## STRUCTURAL COMPONENTS (NEW - COMPLETE)

### 24.22 Plenum Chamber Analysis (15 tasks)
- [ ] Plenum type identification (box type, slope-sided)
- [ ] Plenum depth verification (min 915mm / 36" per API 661)
- [ ] Plenum material verification (carbon steel typical)
- [ ] Plenum thickness check
- [ ] Plenum volume calculation
- [ ] Air distribution uniformity analysis
- [ ] Plenum drain locations
- [ ] Plenum access door locations
- [ ] Plenum seal/gasket verification
- [ ] Plenum-to-bundle connection verification
- [ ] Plenum structural bracing
- [ ] Plenum coating/galvanizing verification
- [ ] Plenum lifting lugs
- [ ] Plenum partition plates (multi-service)
- [ ] Plenum rain hood integration

---

### 24.23 Fan System Analysis (20 tasks)

#### Fan Assembly
- [ ] Fan diameter verification
- [ ] Fan blade material (aluminum, FRP, steel)
- [ ] Number of blades
- [ ] Fan blade pitch (fixed vs adjustable)
- [ ] Fan blade tip clearance (per API 661 Table 6)
- [ ] Fan ring/shroud diameter
- [ ] Fan ring material and thickness
- [ ] Fan coverage ratio (min 40% per API 661)
- [ ] Fan dispersion angle (max 45°)
- [ ] Fan hub seal disc verification
- [ ] Inlet bell/rounded fan ring (optional)

#### Fan Drive
- [ ] Motor type and size (HP/kW)
- [ ] Motor enclosure (TEFC, explosion-proof)
- [ ] Motor voltage and frequency
- [ ] V-belt drive verification
- [ ] HTD (timing belt) drive verification
- [ ] Right-angle gear drive verification
- [ ] Belt guard verification
- [ ] Sheave/pulley sizing
- [ ] Service factor verification (min 1.4 per API 661)

---

### 24.24 Fan Control Systems (15 tasks)

#### Variable Pitch Fan
- [ ] Auto-variable pitch hub identification
- [ ] Pneumatic actuator verification
- [ ] Electric actuator verification
- [ ] Hydraulic actuator verification
- [ ] Pitch range (positive and negative)
- [ ] Actuator temperature rating
- [ ] Control signal type (4-20mA, pneumatic)

#### VFD (Variable Frequency Drive)
- [ ] VFD compatibility verification
- [ ] Motor nameplate rating match
- [ ] VFD enclosure rating (NEMA 3R, 4X)
- [ ] VFD bypass capability

#### Fixed Speed Control
- [ ] Two-speed motor option
- [ ] On/off sequencing (multi-fan)
- [ ] Fan shutdown interlocks
- [ ] Vibration switch verification

---

### 24.25 Louver System Analysis (20 tasks)

#### Inlet Louvers (Below Bundle - Forced Draft)
- [ ] Louver frame material (aluminum, galvanized steel)
- [ ] Louver blade material (extruded aluminum typical)
- [ ] Louver blade type (parallel action, opposed action)
- [ ] Louver blade width and spacing
- [ ] Louver frame dimensions
- [ ] TFE/Teflon bushing verification
- [ ] Torque tube diameter (2" typical)

#### Outlet Louvers (Above Bundle - Induced Draft)
- [ ] Outlet louver location
- [ ] Outlet louver sizing
- [ ] Weather protection design

#### Louver Actuators
- [ ] Manual operator (spring-loaded)
- [ ] Pneumatic actuator (diaphragm type)
- [ ] Electric actuator (rotary)
- [ ] Actuator linkage verification
- [ ] Bolted connection (blade horn to actuator rod)
- [ ] Clamp connection (linkage to torque tube)
- [ ] Fail-safe position (open/closed)
- [ ] Control signal (4-20mA, on/off, pneumatic)
- [ ] Actuator enclosure rating (IP67, IP69K)
- [ ] Position feedback verification

---

### 24.26 Screens &amp; Guards Analysis (18 tasks)

#### Hail Guards
- [ ] Hail guard material (galvanized steel, aluminum)
- [ ] Hail guard mesh size/opening
- [ ] Hail guard frame construction
- [ ] Hail guard mounting method
- [ ] Hail guard pressure drop allowance
- [ ] Hail guard location (above bundle - induced draft)

#### Bug/Insect Screens
- [ ] Bug screen material (stainless steel, aluminum mesh)
- [ ] Bug screen mesh size (typically 16-20 mesh)
- [ ] Bug screen frame construction
- [ ] Bug screen mounting (removable for cleaning)
- [ ] Bug screen pressure drop allowance (2× clean per API 661)

#### Lint/Cottonwood Screens
- [ ] Lint screen material
- [ ] Lint screen mesh size
- [ ] Lint screen cleaning access
- [ ] Lint screen pressure drop allowance

#### Fan Guards
- [ ] Fan guard material (aluminum, steel)
- [ ] Fan guard design (OSHA compliant)
- [ ] Fan guard opening size (personnel protection)
- [ ] Fan guard mounting

---

### 24.27 Walkways &amp; Platforms (25 tasks)

#### Header Walkway (Piperack End)
- [ ] Walkway width (min 18" clear per OSHA)
- [ ] Walkway length
- [ ] Walkway elevation
- [ ] Walkway structural support

#### Fan Maintenance Walkway/Catwalk
- [ ] Catwalk width (min 18" per OSHA)
- [ ] Catwalk load rating (50 psf minimum)
- [ ] Catwalk material (steel grating, checkered plate)
- [ ] Catwalk structural support

#### Ballroom Walkway (Full Width Access)
- [ ] Ballroom dimensions (length × width)
- [ ] Ballroom load rating
- [ ] Ballroom material
- [ ] Ballroom access points

#### Flooring
- [ ] Grating type (welded bar, press-lock)
- [ ] Grating bar size and spacing
- [ ] Grating bearing bar direction
- [ ] Grating load rating
- [ ] Grating material (galvanized, painted, aluminum)
- [ ] Grating clips and fasteners
- [ ] Checkered plate locations (solid flooring areas)
- [ ] Slip-resistant surface verification
- [ ] Floor openings protection

---

### 24.28 Handrails &amp; Safety (20 tasks)

#### Top Rail
- [ ] Top rail height (42" ± 3" per OSHA 1910.29)
- [ ] Top rail material (pipe, tube, angle)
- [ ] Top rail diameter (1.25" - 2" graspable)
- [ ] Top rail smooth surface (no snag hazards)

#### Mid Rail
- [ ] Mid rail height (21" typical - midway)
- [ ] Mid rail material
- [ ] Mid rail spacing verification

#### Toe Board/Kick Plate
- [ ] Toe board height (min 3.5" per OSHA)
- [ ] Toe board material
- [ ] Toe board gap to floor (max 0.25")

#### Safety Gates
- [ ] Self-closing gate at ladder access
- [ ] Gate swing direction (away from opening)
- [ ] Gate latch mechanism
- [ ] Gate top rail and mid rail

#### Corner Posts &amp; Supports
- [ ] Post spacing (max 8 ft typical)
- [ ] Post material and size
- [ ] Post base plate mounting
- [ ] Post splice connections

---

### 24.29 Ladders (15 tasks)

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

#### Ladder Safety
- [ ] Ladder angle (75-90° from horizontal)
- [ ] Landing platform at top
- [ ] Ladder fall arrest system (alternative to cage)
- [ ] Ladder material (galvanized, aluminum)
- [ ] Ladder attachment method

---

### 24.30 Stairs (12 tasks)
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

### 24.31 Structure &amp; Support (18 tasks)

#### Main Structure
- [ ] Column material and size (W-shape typical)
- [ ] Column base plate design
- [ ] Anchor bolt pattern and size
- [ ] Beam material and size
- [ ] Cross bracing design
- [ ] Structure height verification
- [ ] Column spacing

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
- [ ] Paint vs galvanizing comparison

---

### 24.32 Enclosures &amp; Hoods (15 tasks)

#### Recirculation Enclosure (Winterization)
- [ ] Enclosure type (internal vs external recirculation)
- [ ] Enclosure material (galvanized sheet, insulated panel)
- [ ] Recirculation duct sizing
- [ ] Recirculation duct location (over-side, over-end)
- [ ] Mixing chamber design
- [ ] Enclosure access doors
- [ ] Enclosure sealing/weatherproofing

#### Rain Hood/Weather Protection
- [ ] Rain hood material
- [ ] Rain hood dimensions
- [ ] Rain hood drainage
- [ ] Rain hood support structure

#### Noise Enclosure (Optional)
- [ ] Acoustic enclosure material
- [ ] Sound attenuation rating (dBA reduction)
- [ ] Ventilation provisions
- [ ] Access panels

#### Hot Air Discharge Hood
- [ ] Discharge hood height
- [ ] Discharge velocity calculation
- [ ] Recirculation prevention

---

### 24.33 Winterization Systems (12 tasks)
- [ ] Steam coil location and sizing
- [ ] Steam coil tube pitch (max 2× bundle pitch per API 661)
- [ ] Steam coil slope (min 10mm/m toward outlet)
- [ ] Glycol/electric heater (Ruffneck style)
- [ ] Internal recirculation louvers
- [ ] External recirculation ducts
- [ ] Positive/negative pitch fan combination
- [ ] Auto-variable fan control
- [ ] Air tempering verification
- [ ] Freeze protection temperature setpoint
- [ ] Steam trap and condensate return
- [ ] Heating coil control valve

---

### 24.34 Standards Compliance Checks (20 tasks)

#### API 661 Compliance
- [ ] Tube bundle lateral movement (min 6mm each direction)
- [ ] Tube support spacing (max 1.83m / 6ft)
- [ ] Header type for pressure rating (plug >435 psi)
- [ ] Plug hardness verification (HRB 68 max CS, HRB 82 max SS)
- [ ] Fin material verification
- [ ] Motor specifications compliance
- [ ] Fan tip clearance per Table 6
- [ ] Plenum depth minimum
- [ ] Fan coverage ratio minimum
- [ ] Screen pressure drop allowance

#### ASME VIII Div 1 Compliance
- [ ] Pressure rating verification
- [ ] Material allowable stress check
- [ ] Joint efficiency verification
- [ ] Minimum thickness requirements
- [ ] Nozzle reinforcement compliance

#### TEMA Compliance
- [ ] TEMA class verification (R, C, B)
- [ ] Tubesheet thickness (TEMA vs ASME)
- [ ] Tube-to-tubesheet joint requirements
- [ ] Baffle/support spacing requirements

#### OSHA 1910 Compliance
- [ ] Handrail height (42" ± 3")
- [ ] Mid-rail requirement
- [ ] Toe board height (3.5" min)
- [ ] Ladder requirements
- [ ] Safety gate requirements

---

### 24.35 Design Recommendations Tab (AI-Powered) (12 tasks)
- [ ] Design Recommender Agent
- [ ] Critical Issues identification (must fix) with severity ranking
- [ ] Warnings identification (should review)
- [ ] Suggestions (nice to have)
- [ ] Weight Optimization recommendations with savings estimate
- [ ] Cost Reduction opportunities with $ estimate
- [ ] Manufacturability (DFM) analysis
- [ ] One-Click Fix buttons (apply changes to SW via COM)
- [ ] Summary dashboard (total savings potential)
- [ ] Before/After comparison visualization
- [ ] Recommendation history tracking
- [ ] User acceptance/rejection logging

---

### 24.36 Reports &amp; Documentation (10 tasks)
- [ ] PDF report generation (full model summary)
- [ ] Excel export (BOM, properties, checks)
- [ ] Customer submittal package generator
- [ ] As-built documentation generator
- [ ] Fabrication traveler generator
- [ ] Inspection checklist generator
- [ ] Weight report generator
- [ ] Nozzle schedule report
- [ ] Weld map generator
- [ ] Drawing checklist report

---

### 24.37 Version Control &amp; History (6 tasks)
- [ ] Model version comparison (visual diff)
- [ ] Property change tracking
- [ ] ECN (Engineering Change Notice) history
- [ ] Who changed what, when log
- [ ] Rollback suggestions
- [ ] Revision timeline visualization

---

### 24.38 Cost Estimation (6 tasks)
- [ ] Material cost calculator (by weight × $/lb per spec)
- [ ] Labor hour estimation
- [ ] Machining time estimates
- [ ] Welding time estimates (by weld volume)
- [ ] Paint/coating cost estimation
- [ ] Total estimated cost summary

---

### 24.39 Real-Time Notifications (6 tasks)
- [ ] Interference detected alerts
- [ ] Mate broken alerts
- [ ] Model rebuild status notifications
- [ ] Save/revision notifications
- [ ] Standards violation alerts
- [ ] Notification settings (enable/disable, priority)

---

### 24.40 Contextual AI Chat (6 tasks)
- [ ] Quick action buttons ("Summarize", "Check compliance", "Generate report")
- [ ] Context-aware prompts (knows current model data)
- [ ] Ask questions about the specific model
- [ ] Natural language commands ("Find all undersized welds")
- [ ] Conversation history per model
- [ ] Export chat as documentation

---

### 24.41 Integrations (6 tasks)
- [ ] PDM integration (SolidWorks PDM check-in/out status)
- [ ] ERP system connection concept (job costing)
- [ ] Email notification capability
- [ ] Slack/Teams alert integration
- [ ] Google Drive backup of reports
- [ ] Export to customer portal

---

### 24.42 Mobile/Tablet Support (4 tasks)
- [ ] Responsive UI for shop floor tablets
- [ ] QR code generation (link to model data)
- [ ] Offline mode for shop floor (cached data)
- [ ] Touch-friendly interface

---

## Phase 24 Implementation Plan

| Sub-Phase | Tasks | Effort | Priority |
|-----------|-------|--------|----------|
| 24.1 Auto-Launch | 5 | 4-6 hrs | HIGH |
| 24.2 Overview Tab | 8 | 8-10 hrs | HIGH |
| 24.3-24.7 Properties | 65 | 20-25 hrs | HIGH |
| 24.8 Components | 10 | 6-8 hrs | HIGH |
| 24.9-24.10 Mates/Interference | 12 | 8-10 hrs | HIGH |
| 24.11 Sheet Metal | 10 | 8-10 hrs | HIGH |
| 24.12 Hole Analysis | 12 | 10-12 hrs | HIGH |
| 24.13-24.14 Calculations | 22 | 15-20 hrs | HIGH |
| 24.15-24.16 Instrumentation/Nozzles | 22 | 12-15 hrs | MEDIUM |
| 24.17-24.18 Welds/Drawings | 22 | 15-18 hrs | HIGH |
| 24.19-24.21 Manufacturing/QC | 26 | 12-15 hrs | MEDIUM |
| 24.22 Plenum | 15 | 6-8 hrs | HIGH |
| 24.23-24.24 Fans/Controls | 35 | 15-20 hrs | HIGH |
| 24.25 Louvers | 20 | 10-12 hrs | MEDIUM |
| 24.26 Screens/Guards | 18 | 8-10 hrs | MEDIUM |
| 24.27-24.30 Walkways/Rails/Ladders/Stairs | 72 | 25-30 hrs | HIGH |
| 24.31 Structure | 18 | 10-12 hrs | HIGH |
| 24.32-24.33 Enclosures/Winterization | 27 | 12-15 hrs | MEDIUM |
| 24.34 Standards | 20 | 12-15 hrs | HIGH |
| 24.35 Recommendations | 12 | 15-20 hrs | HIGH |
| 24.36-24.38 Reports/History/Cost | 22 | 15-18 hrs | MEDIUM |
| 24.39-24.42 Notifications/Chat/Mobile | 22 | 15-18 hrs | LOW |

**Total Tasks**: 287
**Total Estimated Effort**: 280-350 hours (~7-9 weeks focused work)

---

## Complete ACHE Component Checklist

| Component Category | Sub-Components |
|-------------------|----------------|
| **Tube Bundle** | Tubes, fins, tube supports, tube keepers, side frames, tube sheets |
| **Header Box** | Plug sheet, cover plate, bonnet, pass partitions, gaskets, plugs |
| **Plenum** | Box plenum, slope-sided plenum, partitions, drains, access doors |
| **Fan System** | Fan blades, fan hub, fan ring, inlet bell, hub seal disc |
| **Fan Drive** | Motor, V-belt, HTD belt, gear drive, sheaves, belt guard |
| **Fan Control** | Variable pitch hub, VFD, pneumatic actuator, electric actuator |
| **Louvers** | Inlet louvers, outlet louvers, blades, frame, torque tube, actuators |
| **Screens** | Hail guard, bug screen, lint screen, cottonwood screen |
| **Guards** | Fan guard, belt guard |
| **Walkways** | Header walkway, fan walkway, ballroom, catwalk |
| **Flooring** | Bar grating, checkered plate, toe plates |
| **Handrails** | Top rail, mid rail, posts, corner assemblies |
| **Safety** | Toe boards, safety gates, kick plates |
| **Ladders** | Side rails, rungs, cage hoops, cage bars, rest platforms |
| **Stairs** | Stringers, treads, risers, handrails, landings |
| **Structure** | Columns, beams, braces, base plates, anchor bolts |
| **Enclosures** | Recirculation enclosure, rain hood, noise enclosure |
| **Winterization** | Steam coils, heaters, recirculation ducts, auto-variable fans |
| **Instrumentation** | Thermowells, pressure taps, TI, PI, TT, PT, vibration switch |
| **Nozzles** | Inlet, outlet, vent, drain, utility connections |

---

## Standards Database Requirements

| Standard | Purpose | Key Sections |
|----------|---------|-----------------|
| **API 661** | Air-Cooled Heat Exchangers | Table 6 (tip clearance), para 4.2.3 (fan), Annex C (winterization) |
| **ASME VIII Div 1** | Pressure Vessel Design | UG-27, UG-32, UG-34, UG-37, UG-40 |
| **TEMA** | Shell &amp; Tube HX Standards | Classes R/C/B, Section 6 (vibration), tubesheet |
| **AWS D1.1** | Structural Welding | Weld sizes, joint types, NDE |
| **ASME B16.5** | Flanges | Dimensions, ratings, bolt patterns |
| **OSHA 1910.25** | Stairways | Angle, tread, riser, handrails |
| **OSHA 1910.27** | Ladders | Width, rungs, cage, rest platforms |
| **OSHA 1910.28** | Fall Protection | 4 ft trigger height |
| **OSHA 1910.29** | Guardrails | 42" top rail, 21" mid rail, 3.5" toe board |
| **WRC 107/297** | Nozzle Loads | Local stresses at nozzle junctions |
| **SSPC** | Surface Prep | SP6 (commercial), SP10 (near-white) |

---

## Previous Phases (Completed)

### Phase 22: Active CAD Event Listening ✅
- [x] Implement COM Event Listener
- [x] Create Event Stream Endpoint
- [x] Connect Orchestrator to Desktop Events

### Phase 23: Render.com Production Deployment ✅
- [x] Web frontend 404 fix
- [x] Docker configuration
- [x] Tailscale setup documentation
- [x] Environment variables template

---

## Blocked Task

### Flatter Files Integration
**Status**: BLOCKED - Awaiting API credentials
**Priority**: Low
**Decision**: Skip - offline standards database covers 95% of use cases

---

## Explicitly SKIPPING (Not Needed for Personal Use)

- Multi-user accounts (40-50 hours)
- OAuth/SSO (10-15 hours)
- Team collaboration (20-30 hours)
- Enterprise compliance (10-15 hours)

**Total time saved**: ~100-150 hours by focusing on personal use

---

## Maintenance Notes

- **Autonomous Learning Loop**: Running weekly (Sunday 00:00 UTC)
- **Monthly maintenance**: Update standards DB + retrain memory
- **Phase 24 focus**: ACHE Design Assistant with COMPLETE structural coverage

---

**Last Updated**: Dec 25, 2025
**Next Review**: Weekly (automated via feedback loop)
