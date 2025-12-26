# PRD-024: ACHE Design Assistant

**Status**: Draft
**Created**: 2025-12-26
**Owner**: CAD Agent Team
**Priority**: P1 - Next Major Feature

---

## 1. Overview

### 1.1 What is ACHE?
**Air Cooled Heat Exchangers (ACHE)** are industrial equipment used to cool process fluids using ambient air. They are governed by **API 661 / ISO 13706** standards and are critical components in oil & gas, petrochemical, and power generation facilities.

### 1.2 Problem Statement
Current CAD workflow for ACHE design requires:
- Manual property extraction from SolidWorks models
- Manual cross-referencing with API 661 requirements
- Manual structural calculations per AISC/AWS
- No integrated design assistance for accessories (walkways, ladders, platforms)
- No automated field erection documentation

### 1.3 Solution
Build an **ACHE Design Assistant** that:
- Auto-launches when ACHE-related models are opened
- Provides real-time property extraction and validation
- Automates structural component design per standards
- Generates field erection packages
- Integrates AI for design recommendations

---

## 2. User Stories

### Primary Users
- **Mechanical Engineers**: Design ACHE units per API 661
- **Structural Engineers**: Design supporting structures per AISC
- **Field Engineers**: Need erection/installation packages

### Stories

1. **As a mechanical engineer**, I want the assistant to automatically detect when I open an ACHE model and show me relevant properties and validation status.

2. **As a designer**, I want to see a Model Overview Tab showing all critical dimensions, materials, and design parameters extracted from the SolidWorks model.

3. **As a structural engineer**, I want automated structural calculations for platforms, walkways, and handrails per OSHA 1910.

4. **As a field engineer**, I want erection sequence documentation with lifting lug calculations and rigging diagrams.

5. **As a project engineer**, I want AI-powered design recommendations based on similar past projects.

---

## 3. Feature Breakdown (8 Major Areas)

### 3.1 Auto-Launch System (Phase 24.1)
**Goal**: Detect ACHE models and launch assistant automatically

| Task | Description | Priority |
|------|-------------|----------|
| 24.1.1 | SolidWorks event listener for model open | P1 |
| 24.1.2 | ACHE model detection (by custom property or filename pattern) | P1 |
| 24.1.3 | Assistant panel auto-launch | P1 |
| 24.1.4 | User preference for auto-launch on/off | P2 |
| 24.1.5 | Integration with existing desktop server | P1 |

**Estimated Tasks**: 8

---

### 3.2 Model Overview Tab (Phase 24.2)
**Goal**: Display comprehensive model information

| Task | Description | Priority |
|------|-------------|----------|
| 24.2.1 | Custom property extraction (Part Number, Revision, Material) | P1 |
| 24.2.2 | Mass properties display (weight, CG, moments) | P1 |
| 24.2.3 | Bounding box dimensions | P1 |
| 24.2.4 | Configuration management display | P2 |
| 24.2.5 | Reference document links | P2 |
| 24.2.6 | Real-time property refresh | P1 |
| 24.2.7 | Property editing capability | P2 |
| 24.2.8 | Export to Excel/PDF | P2 |

**Estimated Tasks**: 15

---

### 3.3 Properties Extraction (Phase 24.3)
**Goal**: Deep extraction of ACHE-specific properties

| Task | Description | Priority |
|------|-------------|----------|
| 24.3.1 | Header box dimensions extraction | P1 |
| 24.3.2 | Tube bundle parameters (rows, tubes/row, pitch) | P1 |
| 24.3.3 | Fan system parameters (diameter, blade count) | P1 |
| 24.3.4 | Structural frame dimensions | P1 |
| 24.3.5 | Nozzle schedule extraction | P1 |
| 24.3.6 | Material takeoff (MTO) generation | P1 |
| 24.3.7 | Weight summary by component type | P1 |
| 24.3.8 | Assembly hierarchy extraction | P1 |

**Estimated Tasks**: 20

---

### 3.4 Analysis & Calculations (Phase 24.4)
**Goal**: Automated engineering calculations

| Task | Description | Priority |
|------|-------------|----------|
| 24.4.1 | Thermal performance calculator (API 661 Section 6) | P1 |
| 24.4.2 | Pressure drop calculations | P1 |
| 24.4.3 | Tube bundle weight calculation | P1 |
| 24.4.4 | Header stress analysis interface | P2 |
| 24.4.5 | Fan power consumption calculator | P1 |
| 24.4.6 | Noise level estimation | P2 |
| 24.4.7 | Integration with existing Phase 25 validators | P1 |
| 24.4.8 | Calculation report generation | P1 |

**Estimated Tasks**: 25

---

### 3.5 Structural Components (Phase 24.5)
**Goal**: Design and validate structural elements

| Task | Description | Priority |
|------|-------------|----------|
| 24.5.1 | Column design per AISC | P1 |
| 24.5.2 | Beam design per AISC | P1 |
| 24.5.3 | Bracing system design | P1 |
| 24.5.4 | Base plate design | P1 |
| 24.5.5 | Anchor bolt layout | P1 |
| 24.5.6 | Wind load analysis interface | P1 |
| 24.5.7 | Seismic load analysis interface | P1 |
| 24.5.8 | Connection design (bolted/welded) | P1 |
| 24.5.9 | Unity check calculations | P1 |
| 24.5.10 | Structural report generation | P1 |

**Estimated Tasks**: 40

---

### 3.6 Walkways, Handrails, Ladders (Phase 24.6)
**Goal**: Design accessories per OSHA 1910

| Task | Description | Priority |
|------|-------------|----------|
| 24.6.1 | Platform grating design | P1 |
| 24.6.2 | Handrail design per OSHA 1910.29 | P1 |
| 24.6.3 | Ladder design per OSHA 1910.23 | P1 |
| 24.6.4 | Cage/safety climb requirements | P1 |
| 24.6.5 | Toe board requirements | P1 |
| 24.6.6 | Self-closing gate design | P2 |
| 24.6.7 | Access platform layout optimizer | P2 |
| 24.6.8 | Maintenance access verification | P1 |
| 24.6.9 | Load rating verification | P1 |
| 24.6.10 | Integration with rigging validator | P1 |

**Estimated Tasks**: 35

---

### 3.7 AI Features & Integration (Phase 24.7)
**Goal**: Intelligent design assistance

| Task | Description | Priority |
|------|-------------|----------|
| 24.7.1 | Natural language query for ACHE parameters | P1 |
| 24.7.2 | Design recommendation engine | P2 |
| 24.7.3 | Similar project lookup (RAG) | P2 |
| 24.7.4 | Anomaly detection in designs | P2 |
| 24.7.5 | Auto-dimensioning suggestions | P2 |
| 24.7.6 | Chat integration for design questions | P1 |
| 24.7.7 | Voice command support | P3 |
| 24.7.8 | Learning from validated designs | P3 |

**Estimated Tasks**: 30

---

### 3.8 Field Erection Support (Phase 24.8)
**Goal**: Support on-site installation

| Task | Description | Priority |
|------|-------------|----------|
| 24.8.1 | Erection sequence generator | P1 |
| 24.8.2 | Lifting lug design per AISC DG 29 | P1 |
| 24.8.3 | Rigging diagram generator | P1 |
| 24.8.4 | Shipping split recommendations | P1 |
| 24.8.5 | Field weld map generation | P1 |
| 24.8.6 | Torque sequence documentation | P1 |
| 24.8.7 | Alignment/leveling procedures | P2 |
| 24.8.8 | QC checkpoint definition | P1 |
| 24.8.9 | Punch list template generation | P2 |
| 24.8.10 | As-built documentation support | P2 |

**Estimated Tasks**: 40

---

## 4. Technical Architecture

### 4.1 Component Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACHE Design Assistant                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Auto-Launch  │  │ Model        │  │ Properties   │          │
│  │ System       │──│ Overview Tab │──│ Extraction   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                │                  │                   │
│         ▼                ▼                  ▼                   │
│  ┌──────────────────────────────────────────────────┐          │
│  │              Desktop Server (FastAPI)             │          │
│  │  - SolidWorks COM Interface                       │          │
│  │  - Event Listeners                                │          │
│  │  - Property Extractors                            │          │
│  └──────────────────────────────────────────────────┘          │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────┐          │
│  │           Phase 25 Validators (213 checks)        │          │
│  │  - API 661 Full Scope (82 checks)                 │          │
│  │  - GD&T (14 checks)                               │          │
│  │  - Structural (AISC/AWS)                          │          │
│  │  - OSHA (Platform/Ladder)                         │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 New Endpoints Required

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ache/detect` | GET | Check if current model is ACHE |
| `/ache/overview` | GET | Get model overview data |
| `/ache/properties` | GET | Extract ACHE-specific properties |
| `/ache/calculations` | POST | Run engineering calculations |
| `/ache/structural` | POST | Run structural analysis |
| `/ache/accessories` | POST | Design walkways/ladders |
| `/ache/erection` | POST | Generate erection package |
| `/ache/assistant` | POST | AI chat for design questions |

### 4.3 New Files/Modules

```
agents/cad_agent/
├── ache_assistant/
│   ├── __init__.py
│   ├── detector.py          # Model detection
│   ├── extractor.py         # Property extraction
│   ├── calculator.py        # Engineering calculations
│   ├── structural.py        # Structural design
│   ├── accessories.py       # Walkways/ladders
│   ├── erection.py          # Field erection support
│   └── ai_assistant.py      # AI integration
│
desktop_server/
├── ache/
│   ├── __init__.py
│   ├── event_listener.py    # SW event hooks
│   ├── property_reader.py   # COM property extraction
│   └── model_analyzer.py    # Model analysis
```

---

## 5. Implementation Plan

### Phase 24.1: Foundation (Week 1-2)
- [ ] Auto-launch system
- [ ] Event listener setup
- [ ] Basic model detection

### Phase 24.2: Core Features (Week 3-4)
- [ ] Model Overview Tab
- [ ] Properties Extraction
- [ ] Integration with existing validators

### Phase 24.3: Analysis (Week 5-6)
- [ ] Engineering calculations
- [ ] Structural design tools
- [ ] Report generation

### Phase 24.4: Accessories (Week 7-8)
- [ ] Walkways/platforms
- [ ] Handrails/ladders
- [ ] OSHA compliance checks

### Phase 24.5: Advanced (Week 9-10)
- [ ] AI integration
- [ ] Field erection support
- [ ] Final testing

---

## 6. Success Criteria

- [ ] Auto-launch works for 95%+ of ACHE models
- [ ] Property extraction accuracy > 99%
- [ ] All calculations match manual verification
- [ ] Structural designs pass unity checks
- [ ] OSHA compliance 100%
- [ ] Erection packages reviewed by field team

---

## 7. Dependencies

- Phase 25 validators (COMPLETE - 213 checks)
- SolidWorks COM interface (COMPLETE)
- Desktop server (COMPLETE)
- API 661 standards database (COMPLETE)

---

## 8. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SolidWorks event API limitations | Medium | High | Polling fallback |
| Complex assembly performance | Medium | Medium | Lazy loading |
| Structural calculation accuracy | Low | High | Third-party validation |
| AI hallucination in recommendations | Medium | Medium | Human-in-loop approval |

---

## 9. Task Summary

| Phase | Tasks | Priority |
|-------|-------|----------|
| 24.1 Auto-Launch | 8 | P1 |
| 24.2 Model Overview | 15 | P1 |
| 24.3 Properties | 20 | P1 |
| 24.4 Calculations | 25 | P1 |
| 24.5 Structural | 40 | P1 |
| 24.6 Accessories | 35 | P1 |
| 24.7 AI Features | 30 | P2 |
| 24.8 Field Erection | 40 | P1 |
| **TOTAL** | **213** | - |

*Note: Original estimate was 340 tasks. After detailed analysis, scope is 213 tasks. Additional 127 tasks may be added for testing, documentation, and edge cases.*

---

**Approval Required**: User must approve this PRD before implementation begins.
