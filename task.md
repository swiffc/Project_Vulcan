# Project Vulcan: Active Task List

**Status**: Phase 24 - ACHE Design Assistant
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
| Phase 24 (ACHE Design Assistant) | 0/42 | 42 | 0% |

**Current Focus**: Phase 24 - ACHE Design Assistant 🚧

---

## Phase 24: ACHE Design Assistant 🚧

**Goal**: Auto-launch chatbot when SolidWorks opens with comprehensive model overview, checks, and AI-powered design recommendations.

### 24.1 Auto-Launch System
- [ ] SolidWorks process watcher (`desktop_server/watchers/solidworks_watcher.py`)
- [ ] Auto-open chatbot URL when SW detected
- [ ] Document change detection (Part/Assembly/Drawing switch)
- [ ] WebSocket real-time updates to web UI
- [ ] Tailscale connection handling

### 24.2 Model Overview Tab
- [ ] Visual Preview (screenshots: isometric, front, side, top)
- [ ] Quick Stats (parts count, weight, dimensions, fasteners)
- [ ] Structure Diagram (ACHE bundle visualization)
- [ ] Warnings Summary (quick view of issues)
- [ ] Linked Documents list

### 24.3 Properties Extraction (All Properties)
- [ ] Standard Properties (filename, path, config, dates, SW version)
- [ ] Mass Properties (mass, volume, surface area, COG, moments of inertia)
- [ ] Custom Properties - Job Info (job#, customer, PO, tag#, service)
- [ ] Custom Properties - Design Data (pressure, temp, MDMT, corrosion allowance)
- [ ] Custom Properties - Tube Bundle (tubes, pitch, fins, passes)
- [ ] Custom Properties - Header Box (type, material, thickness, plugs)
- [ ] Custom Properties - Structural (tube sheet, side frames, supports)
- [ ] Custom Properties - Drawing Info (DWG#, rev, drawn by, checked by)
- [ ] Custom Properties - Paint & Coating (system, prep, primer, topcoat)
- [ ] Configuration-specific properties
- [ ] ECN History tracking

### 24.4 Component Analysis
- [ ] BOM extraction with quantities
- [ ] Weight Breakdown (visual bar chart by component type)
- [ ] Fastener Summary (bolts, nuts, plugs by size/material)
- [ ] Material Summary (by spec, weight, components)
- [ ] Revision Comparison (Rev A vs Rev B changes)

### 24.5 Checks Tab
- [ ] Mate & Constraint Status (satisfied, over-defined, broken)
- [ ] Broken mate identification and fix suggestions
- [ ] Interference Detection (run check, show results)
- [ ] Interference volume and location details

### 24.6 Sheet Metal & Bend Radius Checks
- [ ] Bend Radius Analyzer (`desktop_server/analyzers/bend_radius_analyzer.py`)
- [ ] Material-based minimum bend radius lookup
- [ ] K-Factor and Bend Allowance display
- [ ] Grain Direction warnings
- [ ] Flat Pattern accuracy verification
- [ ] Auto-fix radius suggestions

### 24.7 Hole Location Analysis
- [ ] Hole Pattern Extractor (`desktop_server/extractors/holes.py`)
- [ ] Tube Sheet hole pattern verification
- [ ] Edge Distance checks (min 1.5D)
- [ ] Ligament checks (min per TEMA)
- [ ] Mating Hole Alignment checker (header ↔ tube sheet)
- [ ] Bolt Circle verification (per ASME B16.5)
- [ ] Hole schedule export

### 24.8 Calculations & Verification
- [ ] Tube Sheet thickness calc (ASME UG-34)
- [ ] Header Box thickness calc (ASME UG-32)
- [ ] Nozzle Reinforcement area calc
- [ ] Tube Vibration analysis (natural vs exciting frequency)
- [ ] Display margin percentages

### 24.9 Manufacturing & Logistics
- [ ] Welding Notes extraction (WPS requirements)
- [ ] Machining Notes (surface finish, tolerances)
- [ ] Assembly Notes (tube insertion, bolt torque)
- [ ] Testing Requirements (hydro, leak, NDE)
- [ ] Shipping Dimensions and weight
- [ ] Lifting Points and CG location
- [ ] Preservation requirements

### 24.10 Design Recommendations Tab (AI-Powered)
- [ ] Design Recommender Agent (`agents/design_recommender/`)
- [ ] Critical Issues identification (must fix)
- [ ] Warnings identification (should review)
- [ ] Suggestions (nice to have)
- [ ] Weight Optimization recommendations
- [ ] Cost Reduction opportunities
- [ ] Manufacturability (DFM) analysis
- [ ] One-Click Fix buttons (apply changes to SW)
- [ ] Summary dashboard (savings potential)

### 24.11 Standards Compliance Tab
- [ ] API 661 compliance checks (ACHE specific)
- [ ] ASME VIII Div 1 checks
- [ ] TEMA Class C checks
- [ ] AWS D1.1 weld checks
- [ ] OSHA 1910 (platforms, ladders) checks
- [ ] Drawing Checklist (title block, dims, welds, BOM, notes)

### 24.12 Real-Time Notifications
- [ ] Interference detected alerts
- [ ] Mate broken alerts
- [ ] Model rebuild status
- [ ] Save/revision notifications
- [ ] Notification settings

### 24.13 Contextual AI Chat
- [ ] Quick action buttons ("Summarize", "Check compliance", "Generate report")
- [ ] Context-aware prompts (knows current model data)
- [ ] Ask questions about the specific model

---

## Phase 24 File Structure

```
Project_Vulcan/
├── apps/web/src/
│   ├── components/
│   │   ├── overview/
│   │   │   ├── ModelOverview.tsx
│   │   │   ├── QuickStats.tsx
│   │   │   ├── StructureDiagram.tsx
│   │   │   └── VisualPreview.tsx
│   │   ├── properties/
│   │   │   ├── PropertiesTab.tsx
│   │   │   ├── StandardProperties.tsx
│   │   │   ├── MassProperties.tsx
│   │   │   ├── CustomProperties.tsx
│   │   │   ├── BOMTable.tsx
│   │   │   └── MaterialSummary.tsx
│   │   ├── checks/
│   │   │   ├── ChecksTab.tsx
│   │   │   ├── MateStatus.tsx
│   │   │   ├── InterferenceCheck.tsx
│   │   │   ├── BendRadiusCheck.tsx
│   │   │   ├── HoleLocationCheck.tsx
│   │   │   └── CalculationsVerify.tsx
│   │   ├── recommendations/
│   │   │   ├── RecommendationsTab.tsx
│   │   │   ├── CriticalIssues.tsx
│   │   │   ├── Warnings.tsx
│   │   │   ├── Suggestions.tsx
│   │   │   └── OneClickFix.tsx
│   │   └── standards/
│   │       ├── StandardsTab.tsx
│   │       ├── API661Check.tsx
│   │       └── ASMECheck.tsx
│   └── app/api/
│       ├── model-update/route.ts
│       └── ws/route.ts
│
├── desktop_server/
│   ├── watchers/
│   │   └── solidworks_watcher.py
│   ├── extractors/
│   │   ├── properties.py
│   │   ├── mass_properties.py
│   │   ├── bom.py
│   │   ├── mates.py
│   │   ├── dimensions.py
│   │   ├── sheet_metal.py
│   │   ├── holes.py
│   │   └── screenshots.py
│   └── analyzers/
│       ├── bend_radius_analyzer.py
│       ├── hole_alignment_analyzer.py
│       └── manufacturability.py
│
├── agents/
│   └── design_recommender/
│       ├── agent.py
│       └── analyzers/
│           ├── weight_optimizer.py
│           ├── cost_optimizer.py
│           └── dfm_analyzer.py
│
└── data/standards/
    └── bend_radius_tables.json
```

---

## Phase 24 Implementation Plan

| Sub-Phase | Tasks | Effort | Priority |
|-----------|-------|--------|----------|
| 24.1 Auto-Launch | 5 tasks | 4-6 hrs | HIGH |
| 24.2 Overview Tab | 5 tasks | 6-8 hrs | HIGH |
| 24.3 Properties | 11 tasks | 8-10 hrs | HIGH |
| 24.4 Components | 5 tasks | 4-6 hrs | MEDIUM |
| 24.5 Checks Tab | 4 tasks | 4-6 hrs | HIGH |
| 24.6 Bend Radius | 6 tasks | 6-8 hrs | HIGH |
| 24.7 Hole Analysis | 7 tasks | 8-10 hrs | HIGH |
| 24.8 Calculations | 5 tasks | 6-8 hrs | MEDIUM |
| 24.9 Manufacturing | 7 tasks | 4-6 hrs | MEDIUM |
| 24.10 Recommendations | 9 tasks | 10-12 hrs | HIGH |
| 24.11 Standards | 6 tasks | 8-10 hrs | MEDIUM |
| 24.12 Notifications | 5 tasks | 4-6 hrs | LOW |
| 24.13 AI Chat | 3 tasks | 4-6 hrs | MEDIUM |

**Total Estimated Effort**: 77-102 hours (~2-3 weeks focused work)

---

## Previous Phases (Completed)

### Phase 22: Active CAD Event Listening ✅
- [x] Implement COM Event Listener (`desktop_server/com/events.py`)
- [x] Create Event Stream Endpoint (`/api/solidworks/events`)
- [x] Connect Orchestrator to Desktop Events

### Phase 23: Render.com Production Deployment ✅
**Completed**: Dec 25, 2025

#### Issues Fixed
- [x] Web frontend 404 error (build commands corrected)
- [x] Duplicate render.yaml files (consolidated to config/render.yaml)
- [x] Desktop server unreachable (Tailscale setup documented)
- [x] Missing deployment documentation (1,575+ lines created)
- [x] Next.js build configuration (Sentry made optional)
- [x] Environment variable template (complete with Tailscale)

#### Documentation Created
- [x] RENDER_DEPLOYMENT_GUIDE.md (650+ lines)
- [x] .env.render.example (185 lines)
- [x] RENDER_STATUS.md (350+ lines)
- [x] RENDER_FIXES_SUMMARY.md (390+ lines)
- [x] scripts/render-fixes.sh (90 lines)

---

## Blocked Task

### Flatter Files Integration
**Status**: BLOCKED - Awaiting API credentials
**Priority**: Low
**Decision**: Skip - offline standards database (658 entries) covers 95% of use cases

---

## Explicitly SKIPPING (Not Needed for Personal Use)

- Multi-user accounts (40-50 hours)
- OAuth/SSO (10-15 hours)
- Team collaboration (20-30 hours)
- Enterprise compliance (10-15 hours)

**Total time saved**: ~100-150 hours by focusing on personal use

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR WINDOWS PC                                            │
│                                                             │
│  SolidWorks ←→ Desktop Server (Python FastAPI)             │
│                     │                                       │
│  • Watchers (detect SW open/changes)                       │
│  • Extractors (properties, BOM, mates, holes)              │
│  • Analyzers (bend radius, hole alignment, DFM)            │
│  • COM API (SolidWorks automation)                         │
│                                                             │
└─────────────────────┬───────────────────────────────────────┘
                      │ Tailscale VPN
┌─────────────────────┴───────────────────────────────────────┐
│  RENDER.COM (Cloud)                                         │
│                                                             │
│  Web App (Next.js) ←→ Agents                               │
│                                                             │
│  TABS:                                                      │
│  • Chat (contextual AI)                                    │
│  • Overview (stats, preview, structure)                    │
│  • Properties (all custom/standard props)                  │
│  • Checks (mates, bends, holes, interferences)            │
│  • Recommendations (AI-powered suggestions)                │
│  • Standards (API 661, ASME, TEMA)                        │
│                                                             │
│  AGENTS:                                                    │
│  • CAD Agent (extract, analyze, build)                     │
│  • ACHE Checker (standards compliance)                     │
│  • Design Recommender (AI suggestions)                     │
│  • Inspector Bot (auditing)                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Maintenance Notes

- **Autonomous Learning Loop**: Running weekly (Sunday 00:00 UTC)
- **Monthly maintenance**: Update standards DB + retrain memory
- **Phase 24 focus**: ACHE Design Assistant with full model overview

---

**Last Updated**: Dec 25, 2025
**Next Review**: Weekly (automated via feedback loop)
