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
| Phase 24 (ACHE Design Assistant) | 0/305 | 305 | 0% |

**Current Focus**: Phase 24 - ACHE Design Assistant (COMPLETE SCOPE) 🚧

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

### 24.23 Mechanical Drive Support System (18 tasks) ⭐ NEW

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

### 24.28-24.31 Access & Safety (72 tasks)
Walkways, Handrails, Ladders, Stairs - per OSHA 1910.25/27/28/29

---

### 24.32 Structure & Support (18 tasks)
- [ ] Columns, beams, cross bracing, base plates
- [ ] Bundle support (side frames, guide rails, lifting)
- [ ] Piperack integration
- [ ] Surface treatment (painted vs galvanized)

---

### 24.33-24.34 Enclosures & Winterization (27 tasks)
Recirculation, rain hoods, noise enclosures, steam coils, auto-variable fans

---

### 24.35-24.43 AI Features & Integration (66 tasks)
Standards compliance, recommendations, reports, cost estimation, notifications, chat, mobile

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
|----------|---------|---------------|
| **API 661** | Air-Cooled Heat Exchangers | Table 6 (tip clearance), para 4.2.3 (fan), drive assembly requirements |
| **ASME VIII Div 1** | Pressure Vessel Design | UG-27, UG-32, UG-34, UG-37, UG-40 |
| **TEMA** | Shell & Tube HX Standards | Classes R/C/B, Section 6 (vibration) |
| **AWS D1.1** | Structural Welding | Weld sizes, joint types |
| **ASME B16.5** | Flanges | Dimensions, ratings |
| **OSHA 1910.25** | Stairways | Angle, tread, riser |
| **OSHA 1910.27** | Ladders | Width, rungs, cage |
| **OSHA 1910.28** | Fall Protection | 4 ft trigger |
| **OSHA 1910.29** | Guardrails | 42" top rail, 21" mid rail |

---

**Total Tasks**: 305
**Estimated Effort**: 300-380 hours (~8-10 weeks)
**Last Updated**: Dec 25, 2025
