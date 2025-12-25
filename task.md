# Project Vulcan: Active Task List

**Status**: Phase 24 - ACHE Design Assistant (Full Scope)
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
| Phase 24 (ACHE Design Assistant) | 0/156 | 156 | 0% |

**Current Focus**: Phase 24 - ACHE Design Assistant (Full Scope) 🚧

---

## Phase 24: ACHE Design Assistant (Full Scope) 🚧

**Goal**: Auto-launch chatbot when SolidWorks opens with comprehensive model overview, checks, and AI-powered design recommendations for Air-Cooled Heat Exchangers.

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
- [ ] Tube Material (spec & grade)
- [ ] Tube Pitch
- [ ] Pitch Pattern (triangular/square)
- [ ] Number of Rows
- [ ] Number of Passes
- [ ] Tubes Per Row

#### Fin Data
- [ ] Fin Type (L-foot, embedded, etc.)
- [ ] Fin Height
- [ ] Fin Thickness
- [ ] Fin Density (fins per inch)
- [ ] Fin Material

#### Header Box Data
- [ ] Header Type (plug, cover plate, bonnet)
- [ ] Header Material
- [ ] Header Thickness
- [ ] Plug Type
- [ ] Plug Material

---

### 24.7 Properties Extraction - Additional Properties (12 tasks)

#### Structural Data
- [ ] Tube Sheet Material
- [ ] Tube Sheet Thickness
- [ ] Tube-to-Tubesheet Joint Type
- [ ] Side Frame Material
- [ ] Tube Support Material
- [ ] Tube Support Quantity
- [ ] Tube Support Spacing

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

### 24.9 Mates & Constraints Analysis (6 tasks)
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

### 24.11 Sheet Metal & Bend Radius Analysis (10 tasks)
- [ ] Bend Radius Analyzer (`desktop_server/analyzers/bend_radius_analyzer.py`)
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
- [ ] Hole Pattern Extractor (`desktop_server/extractors/holes.py`)
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

### 24.13 Calculations & Verification (12 tasks)
- [ ] Tube Sheet thickness calc (ASME UG-34)
- [ ] Header Box thickness calc (ASME UG-32)
- [ ] Nozzle Reinforcement area calc (ASME UG-37/UG-40)
- [ ] Nozzle Reinforcement limits verification (UG-40)
- [ ] Tube Vibration analysis - Natural Frequency calc
- [ ] Tube Vibration analysis - Vortex Shedding check
- [ ] Tube Vibration analysis - Fluidelastic Instability check
- [ ] Tube Vibration analysis - Acoustic Resonance check
- [ ] Margin percentage display (actual vs required)
- [ ] MAWP (Maximum Allowable Working Pressure) calc
- [ ] Hydrostatic Test Pressure calc
- [ ] Minimum Required Thickness calc

---

### 24.14 Thermal & Pressure Analysis (10 tasks)
- [ ] Thermal expansion calculation
- [ ] Thermal growth at design temperature
- [ ] Thermal stress analysis summary
- [ ] Sliding support requirements
- [ ] Bundle expansion allowance verification
- [ ] Header box thermal stress
- [ ] Pressure drop estimation
- [ ] Operating vs Design pressure comparison
- [ ] Temperature classification verification
- [ ] PWHT (Post-Weld Heat Treatment) requirements check

---

### 24.15 Instrumentation & Connections (12 tasks)

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

#### Vents, Drains & Utilities
- [ ] Vent connection locations and sizes
- [ ] Drain connection locations and sizes
- [ ] Utility connection locations (cleaning, purging)

---

### 24.16 Nozzle & Flange Analysis (10 tasks)
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
- [ ] GD&T parsing and verification
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

### 24.19 Manufacturing & Fabrication Notes (10 tasks)
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

### 24.20 Shipping & Handling (8 tasks)
- [ ] Shipping Dimensions (L × W × H)
- [ ] Shipping Weight (with crating/skid)
- [ ] Over-dimensional flag
- [ ] Lifting Points and capacity
- [ ] Center of Gravity location
- [ ] Spreader bar requirements
- [ ] Preservation requirements
- [ ] Shipping orientation requirements

---

### 24.21 Quality & Inspection (8 tasks)
- [ ] NDE requirements summary (RT, UT, MT, PT)
- [ ] Inspection hold points list
- [ ] MTR (Material Test Report) requirements
- [ ] Hydrostatic test requirements
- [ ] Pneumatic/leak test requirements
- [ ] Witness points identification
- [ ] Third-party inspection requirements
- [ ] Code stamping requirements (U stamp, etc.)

---

### 24.22 Fan & Plenum Analysis (ACHE-Specific) (8 tasks)
- [ ] Fan ring dimensions verification
- [ ] Plenum chamber volume calculation
- [ ] Air flow path verification
- [ ] Fan blade clearance check
- [ ] Vibration isolator locations
- [ ] Fan motor mounting verification
- [ ] V-belt drive verification (if applicable)
- [ ] Fan guard requirements

---

### 24.23 Platforms & Access (OSHA 1910) (8 tasks)
- [ ] Platform dimensions verification
- [ ] Handrail height verification (42" min)
- [ ] Mid-rail requirements (21" typical)
- [ ] Toe board requirements (4" min)
- [ ] Ladder spacing and width verification
- [ ] Ladder cage requirements (>20 ft)
- [ ] Access to maintenance points verification
- [ ] Floor opening protection

---

### 24.24 Standards Compliance Checks (15 tasks)

#### API 661 Compliance
- [ ] Tube bundle lateral movement (min 6mm each direction)
- [ ] Tube support spacing (max 1.83m / 6ft)
- [ ] Header type for pressure rating
- [ ] Plug hardness verification
- [ ] Fin material verification
- [ ] Motor specifications compliance

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

---

### 24.25 Design Recommendations Tab (AI-Powered) (12 tasks)
- [ ] Design Recommender Agent (`agents/design_recommender/`)
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

### 24.26 Reports & Documentation (10 tasks)
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

### 24.27 Version Control & History (6 tasks)
- [ ] Model version comparison (visual diff)
- [ ] Property change tracking
- [ ] ECN (Engineering Change Notice) history
- [ ] Who changed what, when log
- [ ] Rollback suggestions
- [ ] Revision timeline visualization

---

### 24.28 Cost Estimation (6 tasks)
- [ ] Material cost calculator (by weight × $/lb per spec)
- [ ] Labor hour estimation
- [ ] Machining time estimates
- [ ] Welding time estimates (by weld volume)
- [ ] Paint/coating cost estimation
- [ ] Total estimated cost summary

---

### 24.29 Real-Time Notifications (6 tasks)
- [ ] Interference detected alerts
- [ ] Mate broken alerts
- [ ] Model rebuild status notifications
- [ ] Save/revision notifications
- [ ] Standards violation alerts
- [ ] Notification settings (enable/disable, priority)

---

### 24.30 Contextual AI Chat (6 tasks)
- [ ] Quick action buttons ("Summarize", "Check compliance", "Generate report")
- [ ] Context-aware prompts (knows current model data)
- [ ] Ask questions about the specific model
- [ ] Natural language commands ("Find all undersized welds")
- [ ] Conversation history per model
- [ ] Export chat as documentation

---

### 24.31 Integrations (6 tasks)
- [ ] PDM integration (SolidWorks PDM check-in/out status)
- [ ] ERP system connection concept (job costing)
- [ ] Email notification capability
- [ ] Slack/Teams alert integration
- [ ] Google Drive backup of reports
- [ ] Export to customer portal

---

### 24.32 Mobile/Tablet Support (4 tasks)
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
| 24.22-24.23 Fan/Platforms | 16 | 8-10 hrs | MEDIUM |
| 24.24 Standards | 15 | 12-15 hrs | HIGH |
| 24.25 Recommendations | 12 | 15-20 hrs | HIGH |
| 24.26 Reports | 10 | 10-12 hrs | MEDIUM |
| 24.27-24.28 History/Cost | 12 | 8-10 hrs | LOW |
| 24.29-24.30 Notifications/Chat | 12 | 8-10 hrs | MEDIUM |
| 24.31-24.32 Integrations/Mobile | 10 | 10-12 hrs | LOW |

**Total Tasks**: 156
**Total Estimated Effort**: 180-230 hours (~5-6 weeks focused work)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  YOUR WINDOWS PC                                                            │
│                                                                             │
│  SolidWorks ←→ Desktop Server (Python FastAPI)                             │
│                     │                                                       │
│  WATCHERS:                                                                  │
│  • Process watcher (detect SW open/close)                                  │
│  • Document watcher (detect file changes)                                  │
│                                                                             │
│  EXTRACTORS:                                                                │
│  • Properties (standard, custom, mass, config)                             │
│  • BOM & Components                                                        │
│  • Mates & Constraints                                                     │
│  • Dimensions & Tolerances                                                 │
│  • Holes & Patterns                                                        │
│  • Welds & Symbols                                                         │
│  • Instrumentation connections                                             │
│                                                                             │
│  ANALYZERS:                                                                 │
│  • Bend radius analyzer                                                    │
│  • Hole alignment analyzer                                                 │
│  • Interference analyzer                                                   │
│  • Vibration analyzer                                                      │
│  • Thermal expansion analyzer                                              │
│  • DFM (manufacturability) analyzer                                        │
│                                                                             │
│  COM API:                                                                   │
│  • SolidWorks automation                                                   │
│  • One-click fix implementation                                            │
│                                                                             │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │ Tailscale VPN
┌─────────────────────┴───────────────────────────────────────────────────────┐
│  RENDER.COM (Cloud)                                                         │
│                                                                             │
│  Web App (Next.js) ←→ Agents                                               │
│                                                                             │
│  TABS:                                                                      │
│  ├── 💬 Chat (contextual AI)                                               │
│  ├── 📊 Overview (stats, preview, structure)                               │
│  ├── 📝 Properties (all custom/standard props)                             │
│  ├── ✅ Checks (mates, bends, holes, interferences)                        │
│  ├── 🌡️ Thermal (expansion, pressure, temp connections)                    │
│  ├── 🔩 Nozzles (schedule, reinforcement, flanges)                         │
│  ├── ⚙️ Welds (symbols, sizing, NDE)                                       │
│  ├── 💡 Recommendations (AI-powered suggestions)                           │
│  ├── 📋 Standards (API 661, ASME, TEMA, AWS)                               │
│  └── 📄 Reports (PDF, Excel, submittals)                                   │
│                                                                             │
│  AGENTS:                                                                    │
│  • CAD Agent (extract, analyze, build)                                     │
│  • ACHE Checker (standards compliance)                                     │
│  • Design Recommender (AI suggestions)                                     │
│  • Inspector Bot (auditing)                                                │
│  • Report Generator                                                        │
│                                                                             │
│  KNOWLEDGE BASE:                                                            │
│  • Standards database (API 661, ASME, TEMA, AWS)                           │
│  • Material properties database                                            │
│  • Bend radius tables by material                                          │
│  • Flange dimensions (ASME B16.5)                                          │
│  • Customer preferences                                                    │
│  • Lessons learned                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Standards Database Requirements

| Standard | Purpose | Key Sections |
|----------|---------|--------------|
| **API 661** | Air-Cooled Heat Exchangers | Tube support spacing, header types, fin specs |
| **ASME VIII Div 1** | Pressure Vessel Design | UG-27, UG-32, UG-34, UG-37, UG-40 |
| **TEMA** | Shell & Tube HX Standards | Classes R/C/B, vibration, tubesheet |
| **AWS D1.1** | Structural Welding | Weld sizes, joint types, NDE |
| **ASME B16.5** | Flanges | Dimensions, ratings, bolt patterns |
| **OSHA 1910** | Platforms & Ladders | Handrails, toe boards, access |
| **WRC 107/297** | Nozzle Loads | Local stresses at nozzle junctions |

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
- **Phase 24 focus**: ACHE Design Assistant with full model overview

---

**Last Updated**: Dec 25, 2025
**Next Review**: Weekly (automated via feedback loop)
