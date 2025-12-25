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
| Phase 24 (ACHE Design Assistant) | 217/287 | 70 | 76% |

**Current Focus**: Phase 24.15-24.21 - Instrumentation, Nozzles, Welds, Drawings 🚧

---

## Phase 24: ACHE Design Assistant (COMPLETE SCOPE) 🚧

**Goal**: Auto-launch chatbot when SolidWorks opens with comprehensive model overview, checks, and AI-powered design recommendations for Air-Cooled Heat Exchangers - covering EVERY component.

---

### 24.1 Auto-Launch System (5 tasks) ✅
- [x] SolidWorks process watcher (`desktop_server/watchers/solidworks_watcher.py`)
- [x] Auto-open chatbot URL when SW detected
- [x] Document change detection (Part/Assembly/Drawing switch)
- [x] WebSocket real-time updates to web UI
- [x] Tailscale connection handling

---

### 24.2 Model Overview Tab (8 tasks) ✅
- [x] Visual Preview (screenshots: isometric, front, side, top views)
- [x] Quick Stats dashboard (parts count, weight, dimensions, fasteners)
- [x] ACHE Bundle Structure Diagram visualization
- [x] Warnings Summary (quick view of issues)
- [x] Linked Documents list
- [x] Configuration selector
- [x] Real-time refresh indicator
- [x] Export overview as PDF

---

### 24.3 Properties Extraction - Standard Properties (8 tasks) ✅
- [x] File Name, Path, Extension
- [x] Configuration name (active and all available)
- [x] Created Date, Last Modified Date
- [x] Last Saved By (author)
- [x] SolidWorks Version
- [x] Total Edit Time
- [x] File Size
- [x] Rebuild Status (up to date, needs rebuild)

---

### 24.4 Properties Extraction - Mass Properties (10 tasks) ✅
- [x] Mass (kg/lbs)
- [x] Volume (m³/in³)
- [x] Surface Area (m²/in²)
- [x] Density (average)
- [x] Center of Mass (X, Y, Z coordinates)
- [x] Moments of Inertia (Ixx, Iyy, Izz)
- [x] Products of Inertia (Ixy, Ixz, Iyz)
- [x] Principal Axes of Inertia
- [x] Bounding Box dimensions (L × W × H)
- [x] Mass properties by configuration

---

### 24.5 Properties Extraction - Custom Properties (15 tasks) ✅

#### Job Information
- [x] Job Number
- [x] Customer Name
- [x] Project Name
- [x] PO Number
- [x] Item/Tag Number
- [x] Service Description
- [x] Unit/Area

#### Design Data
- [x] Design Code (ASME VIII Div 1, etc.)
- [x] Design Pressure
- [x] Design Temperature
- [x] Operating Pressure
- [x] Operating Temperature
- [x] Test Pressure (Hydro)
- [x] MDMT (Minimum Design Metal Temperature)
- [x] Corrosion Allowance

---

### 24.6 Properties Extraction - ACHE-Specific Properties (20 tasks) ✅

#### Tube Bundle Data
- [x] Number of Tubes
- [x] Tube OD
- [x] Tube BWG (wall thickness)
- [x] Tube Length
- [x] Tube Material (spec &amp; grade)
- [x] Tube Pitch
- [x] Pitch Pattern (triangular/square)
- [x] Number of Rows
- [x] Number of Passes
- [x] Tubes Per Row

#### Fin Data
- [x] Fin Type (L-foot, embedded, extruded, wrap-on)
- [x] Fin Height
- [x] Fin Thickness
- [x] Fin Density (fins per inch)
- [x] Fin Material (aluminum, steel)

#### Header Box Data
- [x] Header Type (plug, cover plate, bonnet)
- [x] Header Material
- [x] Header Thickness
- [x] Plug Type (shoulder, taper)
- [x] Plug Material

---

### 24.7 Properties Extraction - Additional Properties (12 tasks) ✅

#### Structural Data
- [x] Tube Sheet Material
- [x] Tube Sheet Thickness
- [x] Tube-to-Tubesheet Joint Type (rolled, welded, strength welded)
- [x] Side Frame Material
- [x] Tube Support Material
- [x] Tube Support Quantity
- [x] Tube Support Spacing (max 1.83m per API 661)

#### Drawing Information
- [x] Drawing Number
- [x] Revision
- [x] Revision Date
- [x] Revision Description
- [x] Drawn By / Checked By / Approved By

---

### 24.8 Component Analysis (10 tasks) ✅
- [x] BOM extraction with quantities (auto-aggregate)
- [x] Weight Breakdown by component type (visual bar chart)
- [x] Fastener Summary (bolts, nuts, plugs by size/material/qty)
- [x] Material Summary (by spec, total weight, components list)
- [x] Revision Comparison (Rev A vs Rev B changes)
- [x] Component count by type (plates, tubes, fasteners, etc.)
- [x] Duplicate part detection
- [x] Missing part number detection
- [x] Orphan component detection (not in BOM)
- [x] Configuration-specific BOM comparison

---

### 24.9 Mates &amp; Constraints Analysis (6 tasks) ✅
- [x] Mate Status summary (satisfied, over-defined, broken)
- [x] Broken mate identification with component names
- [x] Over-defined mate detection
- [x] Fix suggestions for broken mates
- [x] Mate count by type (coincident, concentric, distance, etc.)
- [x] Redundant mate detection

---

### 24.10 Interference Detection (6 tasks) ✅
- [x] Run interference check on demand
- [x] Display interference results (component pairs)
- [x] Interference volume calculation
- [x] Interference location visualization
- [x] Coincident face detection
- [x] Clearance analysis (minimum gaps)

---

### 24.11 Sheet Metal &amp; Bend Radius Analysis (10 tasks) ✅
- [x] Bend Radius Analyzer
- [x] Material-based minimum bend radius lookup table
- [x] K-Factor display and validation
- [x] Bend Allowance calculation
- [x] Bend Deduction calculation
- [x] Grain Direction warnings (bend parallel vs perpendicular)
- [x] Flat Pattern accuracy verification
- [x] Auto-fix radius suggestions
- [x] Bend sequence recommendation
- [x] Springback compensation notes

---

### 24.12 Hole Location Analysis (12 tasks) ✅
- [x] Hole Pattern Extractor
- [x] Tube Sheet hole pattern verification (pitch, rows, count)
- [x] Edge Distance checks (minimum 1.5× diameter per TEMA)
- [x] Ligament checks (minimum per TEMA)
- [x] Mating Hole Alignment checker (header ↔ tube sheet)
- [x] Bolt Circle verification (per ASME B16.5)
- [x] Hole schedule export
- [x] Hole tolerance verification (+0.003/-0.000 typical)
- [x] Countersink/counterbore detection
- [x] Threaded hole identification (NPT, UNC, etc.)
- [x] Hole centerline alignment verification
- [x] Pattern symmetry check

---

### 24.13 Calculations &amp; Verification (12 tasks) ✅
- [x] Tube Sheet thickness calc (ASME UG-34)
- [x] Header Box thickness calc (ASME UG-32)
- [x] Nozzle Reinforcement area calc (ASME UG-37/UG-40)
- [x] Nozzle Reinforcement limits verification (UG-40)
- [x] Tube Vibration - Natural Frequency calc
- [x] Tube Vibration - Vortex Shedding check
- [x] Tube Vibration - Fluidelastic Instability check
- [x] Tube Vibration - Acoustic Resonance check
- [x] Margin percentage display (actual vs required)
- [x] MAWP (Maximum Allowable Working Pressure) calc
- [x] Hydrostatic Test Pressure calc
- [x] Minimum Required Thickness calc

---

### 24.14 Thermal &amp; Pressure Analysis (10 tasks) ✅
- [x] Thermal expansion calculation
- [x] Thermal growth at design temperature
- [x] Thermal stress analysis summary
- [x] Sliding support requirements
- [x] Bundle expansion allowance verification (min 6mm per API 661)
- [x] Header box thermal stress
- [x] Pressure drop estimation
- [x] Operating vs Design pressure comparison
- [x] Temperature classification verification
- [x] PWHT (Post-Weld Heat Treatment) requirements check

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

### 24.22 Plenum Chamber Analysis (15 tasks) ✅
- [x] Plenum type identification (box type, slope-sided)
- [x] Plenum depth verification (min 915mm / 36" per API 661)
- [x] Plenum material verification (carbon steel typical)
- [x] Plenum thickness check
- [x] Plenum volume calculation
- [x] Air distribution uniformity analysis
- [x] Plenum drain locations
- [x] Plenum access door locations
- [x] Plenum seal/gasket verification
- [x] Plenum-to-bundle connection verification
- [x] Plenum structural bracing
- [x] Plenum coating/galvanizing verification
- [x] Plenum lifting lugs
- [x] Plenum partition plates (multi-service)
- [x] Plenum rain hood integration

---

### 24.23 Fan System Analysis (20 tasks) ✅

#### Fan Assembly
- [x] Fan diameter verification
- [x] Fan blade material (aluminum, FRP, steel)
- [x] Number of blades
- [x] Fan blade pitch (fixed vs adjustable)
- [x] Fan blade tip clearance (per API 661 Table 6)
- [x] Fan ring/shroud diameter
- [x] Fan ring material and thickness
- [x] Fan coverage ratio (min 40% per API 661)
- [x] Fan dispersion angle (max 45°)
- [x] Fan hub seal disc verification
- [x] Inlet bell/rounded fan ring (optional)

#### Fan Drive
- [x] Motor type and size (HP/kW)
- [x] Motor enclosure (TEFC, explosion-proof)
- [x] Motor voltage and frequency
- [x] V-belt drive verification
- [x] HTD (timing belt) drive verification
- [x] Right-angle gear drive verification
- [x] Belt guard verification
- [x] Sheave/pulley sizing
- [x] Service factor verification (min 1.4 per API 661)

---

### 24.24 Fan Control Systems (15 tasks) ✅

#### Variable Pitch Fan
- [x] Auto-variable pitch hub identification
- [x] Pneumatic actuator verification
- [x] Electric actuator verification
- [x] Hydraulic actuator verification
- [x] Pitch range (positive and negative)
- [x] Actuator temperature rating
- [x] Control signal type (4-20mA, pneumatic)

#### VFD (Variable Frequency Drive)
- [x] VFD compatibility verification
- [x] Motor nameplate rating match
- [x] VFD enclosure rating (NEMA 3R, 4X)
- [x] VFD bypass capability

#### Fixed Speed Control
- [x] Two-speed motor option
- [x] On/off sequencing (multi-fan)
- [x] Fan shutdown interlocks
- [x] Vibration switch verification

---

### 24.25 Louver System Analysis (20 tasks) ✅

#### Inlet Louvers (Below Bundle - Forced Draft)
- [x] Louver frame material (aluminum, galvanized steel)
- [x] Louver blade material (extruded aluminum typical)
- [x] Louver blade type (parallel action, opposed action)
- [x] Louver blade width and spacing
- [x] Louver frame dimensions
- [x] TFE/Teflon bushing verification
- [x] Torque tube diameter (2" typical)

#### Outlet Louvers (Above Bundle - Induced Draft)
- [x] Outlet louver location
- [x] Outlet louver sizing
- [x] Weather protection design

#### Louver Actuators
- [x] Manual operator (spring-loaded)
- [x] Pneumatic actuator (diaphragm type)
- [x] Electric actuator (rotary)
- [x] Actuator linkage verification
- [x] Bolted connection (blade horn to actuator rod)
- [x] Clamp connection (linkage to torque tube)
- [x] Fail-safe position (open/closed)
- [x] Control signal (4-20mA, on/off, pneumatic)
- [x] Actuator enclosure rating (IP67, IP69K)
- [x] Position feedback verification

---

### 24.26 Screens &amp; Guards Analysis (18 tasks) ✅

#### Hail Guards
- [x] Hail guard material (galvanized steel, aluminum)
- [x] Hail guard mesh size/opening
- [x] Hail guard frame construction
- [x] Hail guard mounting method
- [x] Hail guard pressure drop allowance
- [x] Hail guard location (above bundle - induced draft)

#### Bug/Insect Screens
- [x] Bug screen material (stainless steel, aluminum mesh)
- [x] Bug screen mesh size (typically 16-20 mesh)
- [x] Bug screen frame construction
- [x] Bug screen mounting (removable for cleaning)
- [x] Bug screen pressure drop allowance (2× clean per API 661)

#### Lint/Cottonwood Screens
- [x] Lint screen material
- [x] Lint screen mesh size
- [x] Lint screen cleaning access
- [x] Lint screen pressure drop allowance

#### Fan Guards
- [x] Fan guard material (aluminum, steel)
- [x] Fan guard design (OSHA compliant)
- [x] Fan guard opening size (personnel protection)
- [x] Fan guard mounting

---

### 24.27 Walkways &amp; Platforms (25 tasks) ✅

#### Header Walkway (Piperack End)
- [x] Walkway width (min 18" clear per OSHA)
- [x] Walkway length
- [x] Walkway elevation
- [x] Walkway structural support

#### Fan Maintenance Walkway/Catwalk
- [x] Catwalk width (min 18" per OSHA)
- [x] Catwalk load rating (50 psf minimum)
- [x] Catwalk material (steel grating, checkered plate)
- [x] Catwalk structural support

#### Ballroom Walkway (Full Width Access)
- [x] Ballroom dimensions (length × width)
- [x] Ballroom load rating
- [x] Ballroom material
- [x] Ballroom access points

#### Flooring
- [x] Grating type (welded bar, press-lock)
- [x] Grating bar size and spacing
- [x] Grating bearing bar direction
- [x] Grating load rating
- [x] Grating material (galvanized, painted, aluminum)
- [x] Grating clips and fasteners
- [x] Checkered plate locations (solid flooring areas)
- [x] Slip-resistant surface verification
- [x] Floor openings protection

---

### 24.28 Handrails &amp; Safety (20 tasks) ✅

#### Top Rail
- [x] Top rail height (42" ± 3" per OSHA 1910.29)
- [x] Top rail material (pipe, tube, angle)
- [x] Top rail diameter (1.25" - 2" graspable)
- [x] Top rail smooth surface (no snag hazards)

#### Mid Rail
- [x] Mid rail height (21" typical - midway)
- [x] Mid rail material
- [x] Mid rail spacing verification

#### Toe Board/Kick Plate
- [x] Toe board height (min 3.5" per OSHA)
- [x] Toe board material
- [x] Toe board gap to floor (max 0.25")

#### Safety Gates
- [x] Self-closing gate at ladder access
- [x] Gate swing direction (away from opening)
- [x] Gate latch mechanism
- [x] Gate top rail and mid rail

#### Corner Posts &amp; Supports
- [x] Post spacing (max 8 ft typical)
- [x] Post material and size
- [x] Post base plate mounting
- [x] Post splice connections

---

### 24.29 Ladders (15 tasks) ✅

#### Vertical Ladders
- [x] Ladder width (min 16" clear)
- [x] Rung spacing (max 12" uniform)
- [x] Rung diameter (0.75" - 1.125")
- [x] Side rail extension (42" above landing)
- [x] Ladder offset from wall (7" min)

#### Ladder Cage
- [x] Cage required (>20 ft unbroken length)
- [x] Cage start height (7-8 ft from base)
- [x] Cage hoop spacing (max 4 ft)
- [x] Cage vertical bar spacing (max 9.5")
- [x] Rest platform spacing (max 35 ft vertical)

#### Ladder Safety
- [x] Ladder angle (75-90° from horizontal)
- [x] Landing platform at top
- [x] Ladder fall arrest system (alternative to cage)
- [x] Ladder material (galvanized, aluminum)
- [x] Ladder attachment method

---

### 24.30 Stairs (12 tasks) ✅
- [x] Stair angle (30-50° per OSHA)
- [x] Tread depth (min 9.5")
- [x] Riser height (max 9.5", uniform)
- [x] Stair width (min 22" typical)
- [x] Stair rail height (30-37" per OSHA)
- [x] Handrail both sides (if >44" wide)
- [x] Stair landing dimensions
- [x] Slip-resistant treads
- [x] Open riser vs closed riser
- [x] Intermediate landings (every 12 ft vertical)
- [x] Stair stringer material
- [x] Stair attachment to structure

---

### 24.31 Structure &amp; Support (18 tasks) ✅

#### Main Structure
- [x] Column material and size (W-shape typical)
- [x] Column base plate design
- [x] Anchor bolt pattern and size
- [x] Beam material and size
- [x] Cross bracing design
- [x] Structure height verification
- [x] Column spacing

#### Bundle Support
- [x] Side frame material
- [x] Side frame connection to structure
- [x] Bundle guide rails
- [x] Bundle slide-out clearance
- [x] Bundle lifting provisions

#### Piperack Integration
- [x] Piperack connection details
- [x] Load transfer to piperack
- [x] Expansion/contraction allowance
- [x] Piperack elevation coordination

#### Surface Treatment
- [x] Structure surface prep (SSPC-SP6, SP10)
- [x] Painting system (primer, intermediate, topcoat)
- [x] Hot-dip galvanizing option
- [x] Paint vs galvanizing comparison

---

### 24.32 Enclosures &amp; Hoods (15 tasks) ✅

#### Recirculation Enclosure (Winterization)
- [x] Enclosure type (internal vs external recirculation)
- [x] Enclosure material (galvanized sheet, insulated panel)
- [x] Recirculation duct sizing
- [x] Recirculation duct location (over-side, over-end)
- [x] Mixing chamber design
- [x] Enclosure access doors
- [x] Enclosure sealing/weatherproofing

#### Rain Hood/Weather Protection
- [x] Rain hood material
- [x] Rain hood dimensions
- [x] Rain hood drainage
- [x] Rain hood support structure

#### Noise Enclosure (Optional)
- [x] Acoustic enclosure material
- [x] Sound attenuation rating (dBA reduction)
- [x] Ventilation provisions
- [x] Access panels

#### Hot Air Discharge Hood
- [x] Discharge hood height
- [x] Discharge velocity calculation
- [x] Recirculation prevention

---

### 24.33 Winterization Systems (12 tasks) ✅
- [x] Steam coil location and sizing
- [x] Steam coil tube pitch (max 2× bundle pitch per API 661)
- [x] Steam coil slope (min 10mm/m toward outlet)
- [x] Glycol/electric heater (Ruffneck style)
- [x] Internal recirculation louvers
- [x] External recirculation ducts
- [x] Positive/negative pitch fan combination
- [x] Auto-variable fan control
- [x] Air tempering verification
- [x] Freeze protection temperature setpoint
- [x] Steam trap and condensate return
- [x] Heating coil control valve

---

### 24.34 Standards Compliance Checks (20 tasks) ✅

#### API 661 Compliance
- [x] Tube bundle lateral movement (min 6mm each direction)
- [x] Tube support spacing (max 1.83m / 6ft)
- [x] Header type for pressure rating (plug >435 psi)
- [x] Plug hardness verification (HRB 68 max CS, HRB 82 max SS)
- [x] Fin material verification
- [x] Motor specifications compliance
- [x] Fan tip clearance per Table 6
- [x] Plenum depth minimum
- [x] Fan coverage ratio minimum
- [x] Screen pressure drop allowance

#### ASME VIII Div 1 Compliance
- [x] Pressure rating verification
- [x] Material allowable stress check
- [x] Joint efficiency verification
- [x] Minimum thickness requirements
- [x] Nozzle reinforcement compliance

#### TEMA Compliance
- [x] TEMA class verification (R, C, B)
- [x] Tubesheet thickness (TEMA vs ASME)
- [x] Tube-to-tubesheet joint requirements
- [x] Baffle/support spacing requirements

#### OSHA 1910 Compliance
- [x] Handrail height (42" ± 3")
- [x] Mid-rail requirement
- [x] Toe board height (3.5" min)
- [x] Ladder requirements
- [x] Safety gate requirements

---

### 24.35 Design Recommendations Tab (AI-Powered) (12 tasks) ✅
- [x] Design Recommender Agent
- [x] Critical Issues identification (must fix) with severity ranking
- [x] Warnings identification (should review)
- [x] Suggestions (nice to have)
- [x] Weight Optimization recommendations with savings estimate
- [x] Cost Reduction opportunities with $ estimate
- [x] Manufacturability (DFM) analysis
- [x] One-Click Fix buttons (apply changes to SW via COM)
- [x] Summary dashboard (total savings potential)
- [x] Before/After comparison visualization
- [x] Recommendation history tracking
- [x] User acceptance/rejection logging

---

### 24.36 Reports &amp; Documentation (10 tasks) ✅
- [x] PDF report generation (full model summary)
- [x] Excel export (BOM, properties, checks)
- [x] Customer submittal package generator
- [x] As-built documentation generator
- [x] Fabrication traveler generator
- [x] Inspection checklist generator
- [x] Weight report generator
- [x] Nozzle schedule report
- [x] Weld map generator
- [x] Drawing checklist report

---

### 24.37 Version Control &amp; History (6 tasks) ✅
- [x] Model version comparison (visual diff)
- [x] Property change tracking
- [x] ECN (Engineering Change Notice) history
- [x] Who changed what, when log
- [x] Rollback suggestions
- [x] Revision timeline visualization

---

### 24.38 Cost Estimation (6 tasks) ✅
- [x] Material cost calculator (by weight × $/lb per spec)
- [x] Labor hour estimation
- [x] Machining time estimates
- [x] Welding time estimates (by weld volume)
- [x] Paint/coating cost estimation
- [x] Total estimated cost summary

---

### 24.39 Real-Time Notifications (6 tasks) ✅
- [x] Interference detected alerts
- [x] Mate broken alerts
- [x] Model rebuild status notifications
- [x] Save/revision notifications
- [x] Standards violation alerts
- [x] Notification settings (enable/disable, priority)

---

### 24.40 Contextual AI Chat (6 tasks) ✅
- [x] Quick action buttons ("Summarize", "Check compliance", "Generate report")
- [x] Context-aware prompts (knows current model data)
- [x] Ask questions about the specific model
- [x] Natural language commands ("Find all undersized welds")
- [x] Conversation history per model
- [x] Export chat as documentation

---

### 24.41 Integrations (6 tasks) ✅
- [x] PDM integration (SolidWorks PDM check-in/out status)
- [x] ERP system connection concept (job costing)
- [x] Email notification capability
- [x] Slack/Teams alert integration
- [x] Google Drive backup of reports
- [x] Export to customer portal

---

### 24.42 Mobile/Tablet Support (4 tasks) ✅
- [x] Responsive UI for shop floor tablets
- [x] QR code generation (link to model data)
- [x] Offline mode for shop floor (cached data)
- [x] Touch-friendly interface

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
