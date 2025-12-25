# CAD Build Plan: 6" RFWN Nozzle Assembly (CORRECTED v2)

**Created**: 2025-12-23
**Revised**: 2025-12-23 (Corrected per ASME B16.5 actual values)
**Status**: CORRECTED
**Standard References**: ASME B16.5-2020, ASME B36.10M, ASME B16.25

---

## PHASE 1: IDENTIFY - What Is This Thing?

| Question | Answer |
|----------|--------|
| What is it called? | 6" Raised Face Weld Neck (RFWN) Nozzle |
| What does it do? | Provides connection point from vessel/pipe to process piping |
| What is it used for? | Pressure vessel connections, pipe branches, equipment connections |
| What industry standards apply? | ASME B16.5 (flanges), ASME B36.10 (pipe), ASME B16.25 (weld ends), ASME VIII (vessels) |

---

## PHASE 2: CLASSIFY - Assembly or Part?

| Question | Answer |
|----------|--------|
| Is this ONE manufactured piece? | NO |
| Is this MULTIPLE pieces joined? | YES - Flange + Pipe welded together |
| Are there purchased components? | YES - WN Flange is a standard purchased part |
| What type of joints? | Full-penetration butt weld between flange hub and pipe |

**CLASSIFICATION: ASSEMBLY**

---

## PHASE 3: DECOMPOSE - What Components?

### Component Breakdown

| Component | Type | Standard | Source |
|-----------|------|----------|--------|
| 1. Weld Neck Flange | PURCHASED | ASME B16.5, 6" 150# WN RF | Standard part library |
| 2. Pipe Section | FABRICATED | ASME B36.10, 6" Sch 40 | Model from standard dims |

### Component 1: 6" 150# Weld Neck Flange (ASME B16.5) - CORRECTED

| Dimension | Symbol | Value | Tolerance | Notes |
|-----------|--------|-------|-----------|-------|
| Nominal Pipe Size | NPS | 6" | - | |
| Pressure Class | - | 150 | - | Class 150 |
| Flange Outside Diameter | O | 11.00" (279.4 mm) | ±0.06" | |
| Bolt Circle Diameter | BC | 9.50" (241.3 mm) | ±0.03" | |
| Bolt Holes | - | 8 x 0.875" (22.2 mm) | - | Equally spaced |
| **Hub OD at Flange Base** | **X** | **7.56"** (192.0 mm) | +0.15"/-0.03" | **CORRECTED from 8.50"** |
| Hub OD at Weld End | A | 6.625" (168.28 mm) | ±0.03" | Matches pipe OD |
| Bore ID | B | 6.065" (154.05 mm) | +0.03"/-0.00" | Sch 40 bore |
| Flange Thickness | C | 0.94"-1.00" (24-25.4 mm) | Min 0.94" | |
| **Length Through Hub** | **Y** | **3.44"** (87.4 mm) | ±0.06" | **CORRECTED from 3.75"** |
| Raised Face Height | - | 0.0625" (1.6 mm) | ±0.03" | 1/16" RF standard |
| Raised Face OD | - | 8.50" (215.9 mm) | - | |
| **Straight Section at Weld** | - | **0.25"** (6.4 mm) | Min | For pipe alignment |
| Weight (approx) | - | 23-25 lbs | - | Carbon steel |

### Hub Taper Geometry (CRITICAL)

```
                    ┌─────────────────┐
                    │   RAISED FACE   │ 0.0625" height
                    │    OD 8.50"     │
    ┌───────────────┼─────────────────┼───────────────┐
    │               │                 │               │
    │   FLANGE      │      BORE       │    FLANGE     │ Thickness C = 0.94-1.00"
    │   BODY        │    ID 6.065"    │    BODY       │
    │               │                 │               │
    └───────┬───────┴─────────────────┴───────┬───────┘
            │                                 │
            │         TAPERED HUB             │
            │    X = 7.56" at base            │
            │         ↓                       │
            │    Taper angle ~7-10°           │
            │         ↓                       │
            │    A = 6.625" at weld end       │
            │                                 │
            │    ┌───────────────────────┐    │ ← 0.25" straight section
            └────┤   WELD END FACE       ├────┘
                 │   37.5° bevel prep    │
                 └───────────────────────┘
                          ↑
                 Length Y = 3.44"
```

### Weld End Preparation (ASME B16.25)

| Feature | Value | Notes |
|---------|-------|-------|
| Bevel Angle | 37.5° ±2.5° | Standard V-groove |
| Root Face | 0.0625" (1/16") | Land thickness |
| Root Gap | 0.0625"-0.125" | Per WPS |
| Straight Section | 0.25" min | Before bevel starts |

### Component 2: 6" Sch 40 Pipe (ASME B36.10)

| Dimension | Value | Tolerance | Notes |
|-----------|-------|-----------|-------|
| Nominal Pipe Size | 6" | - | NPS 6 |
| Schedule | 40 | - | Standard weight |
| Outside Diameter | 6.625" (168.28 mm) | ±0.5% | |
| Wall Thickness | 0.280" (7.11 mm) | +12.5%/-0.0% | |
| Inside Diameter | 6.065" (154.05 mm) | Calculated | |
| Length | 6.00" (152.4 mm) | ±0.125" | Parametric (6-12" typical) |
| Bevel Angle | 37.5° ±2.5° | - | Match flange weld prep |
| Weight (6" length) | ~10-12 lbs | - | Carbon steel |

---

## PHASE 4: PLAN - Build Strategy

### What Joins Them?
- Full-penetration butt weld between flange hub neck and pipe section
- Weld per ASME Section IX / B31.3
- V-groove prep with 37.5° bevel on both sides

### Critical Dimensions/Tolerances

| Check | Tolerance | Method |
|-------|-----------|--------|
| Concentricity (bore to pipe ID) | ≤0.010" | Measure at weld interface |
| Weld gap at interface | 0.0625"-0.125" | Feeler gauge |
| Hub-to-pipe OD match | 6.625" ±0.03" | Both must match |
| Axial alignment | ≤0.5° | Visual/measurement |

### Hub Geometry Calculation

```
Taper Angle = arctan((X - A) / (2 * Y_taper))
            = arctan((7.56 - 6.625) / (2 * 3.19))  # Y_taper = Y - straight - flange
            = arctan(0.935 / 6.38)
            = ~8.3° per side
```

### Assembly Sequence

```
Step 1: Create/Load Components
   └── Load 6in_150_wn_flange.SLDPRT (with correct hub geometry)
   └── Load 6in_sch40_pipe_section.SLDPRT (with weld prep)

Step 2: Create Assembly
   └── New Assembly document
   └── Insert flange GROUNDED at origin (weld end facing +Z)

Step 3: Insert Pipe
   └── Insert pipe section
   └── Initial position: offset in Z to avoid overlap

Step 4: Add Mates (SPECIFIC)
   └── CONCENTRIC: Pipe ID cylindrical face ↔ Flange hub neck OD (6.625")
   └── COINCIDENT: Pipe end face (flat) ↔ Flange hub weld end face (flat)
   └── Verify: 0.000" gap at weld interface (or 0.0625" if modeling root gap)

Step 5: Validate
   └── Run interference detection (expect 0 interferences)
   └── Check concentricity: measure bore alignment ≤0.010"
   └── Verify OD match at weld: both = 6.625"
   └── Measure overall length

Step 6: Save
   └── Save as 6in_rfwn_nozzle_assembly.SLDASM
```

---

## PHASE 5: API Endpoint Sequence

| Step | Endpoint | Body | Validation |
|------|----------|------|------------|
| 1 | `POST /com/solidworks/new_assembly` | `{}` | status=ok |
| 2 | `POST /com/solidworks/insert_component` | `{"filepath": "output/6in_150_wn_flange.SLDPRT", "x": 0, "y": 0, "z": 0}` | component_count=1 |
| 3 | `POST /com/solidworks/insert_component` | `{"filepath": "output/6in_sch40_pipe_section.SLDPRT", "x": 0, "y": 0, "z": 0.1}` | component_count=2 |
| 4 | `POST /com/solidworks/add_mate` | `{"mate_type": "concentric", "entity1": "pipe@ID_face", "entity2": "flange@hub_neck_OD"}` | mate created |
| 5 | `POST /com/solidworks/add_mate` | `{"mate_type": "coincident", "entity1": "pipe@end_face", "entity2": "flange@hub_weld_face", "offset": 0}` | mate created |
| 6 | `POST /com/solidworks/interference_check` | `{}` | interferences=0 |
| 7 | `POST /com/solidworks/save` | `{"filepath": "output/6in_rfwn_nozzle_assembly.SLDASM"}` | status=ok |

---

## PHASE 6: VALIDATION CHECKLIST

### Pre-Build Validation
- [ ] ASME B16.5 dimensions verified against table (Class 150, NPS 6)
- [ ] Hub length Y = 3.44" (NOT 3.75")
- [ ] Hub base X = 7.56" (NOT 8.50")
- [ ] Taper angle calculated (~8.3°)
- [ ] Straight section at weld end = 0.25" min
- [ ] Weld prep = 37.5° bevel per B16.25

### Post-Build Validation
- [ ] Interference check: 0 interferences
- [ ] Concentricity: bore alignment ≤0.010"
- [ ] OD match at weld: both = 6.625" ±0.03"
- [ ] Weld gap: 0.0625"-0.125" (if modeled)
- [ ] GD&T on bolt holes: position ±0.03", 8x equally spaced on 9.50" BC
- [ ] Total weight: ~33-37 lbs (flange + 6" pipe)

---

## BOM (Bill of Materials)

| Item | Qty | Part Number | Description | Standard | Weight |
|------|-----|-------------|-------------|----------|--------|
| 1 | 1 | WNF-6-150-RF-CS | 6" 150# WN Flange, RF, Carbon Steel | ASME B16.5 | 23-25 lbs |
| 2 | 1 | PIPE-6-S40-6L-CS | 6" Sch 40 Pipe, 6" long, Carbon Steel | ASME B36.10 | 10-12 lbs |
| - | - | - | **TOTAL ASSEMBLY** | - | **33-37 lbs** |

---

## ERRORS IN PREVIOUS VERSION (v1)

| Error | v1 Value | Correct Value | Source |
|-------|----------|---------------|--------|
| Hub Length (Y) | 3.75" | 3.44" | ASME B16.5 Table |
| Hub OD at Base (X) | 8.50" | 7.56" | ASME B16.5 Table |
| Taper Angle | Not specified | ~8.3° | Calculated |
| Weld Prep | Not specified | 37.5° bevel | ASME B16.25 |
| Straight Section | Not specified | 0.25" min | ASME B16.5 |
| Tolerances | None | Per ASME | ASME B16.5 |
| Mate Specification | Ambiguous | Pipe ID ↔ Hub Neck OD | Engineering practice |
| Weights | None | 23-25 + 10-12 lbs | Standard tables |

---

## Notes

- Weld prep (37.5° bevel) should be modeled on both flange hub and pipe end
- Gasket surface finish: 125-250 Ra for spiral wound gaskets
- This is a PREFAB SUB-ASSEMBLY that would mate to vessel/pipe in parent assembly
- For parametric design: pipe length should be equation-driven (6-12" typical)
- Cosmetic weld bead can be added for visualization (optional)
