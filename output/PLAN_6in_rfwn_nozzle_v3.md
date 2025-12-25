# CAD Build Plan: 6" RFWN Nozzle Assembly (v3 - VERIFIED)

**Created**: 2025-12-23
**Status**: AWAITING APPROVAL
**Standard References**: ASME B16.5-2020, ASME B36.10M, ASME B16.25
**Data Sources**:
- pipe_schedules.json (verified)
- Verified ASME B16.5 tables (wermac.org, piping-designer.com, ferrobend.com)

---

## PHASE 1: IDENTIFY

| Question | Answer |
|----------|--------|
| What is it? | 6" Raised Face Weld Neck (RFWN) Nozzle |
| Function | Vessel/tank connection point for process piping |
| Standards | ASME B16.5 (flanges), ASME B36.10 (pipe), ASME B16.25 (weld ends) |

---

## PHASE 2: CLASSIFY

**CLASSIFICATION: ASSEMBLY** (NOT single part)

- Weld Neck Flange = PURCHASED standard part (forged per ASME B16.5)
- Pipe Section = FABRICATED from stock (per ASME B36.10)
- Joint = Full penetration butt weld

---

## PHASE 3: DECOMPOSE

### Component 1: 6" 150# Weld Neck Flange (VERIFIED ASME B16.5)

| Dimension | Symbol | Value | Source |
|-----------|--------|-------|--------|
| Outside Diameter | O | 11.00" | ASME B16.5 |
| Raised Face Diameter | R | 8.50" | ASME B16.5 |
| Raised Face Height | - | 0.0625" | ASME B16.5 Class 150 |
| Flange Thickness | T | 1.00" | ASME B16.5 (min) |
| Bolt Circle Diameter | - | 9.50" | ASME B16.5 |
| Bolt Holes | - | 8 x 0.875" | ASME B16.5 |
| **Hub Diameter at Base** | **X** | **7.56"** | ASME B16.5 |
| **Hub Diameter at Weld** | **A** | **6.625"** | ASME B16.5 (matches pipe OD) |
| **Length Through Hub** | **Y** | **3.44"** | ASME B16.5 |
| **Straight Section at Weld** | - | **0.236"** (6 mm) | ASME B16.5 |
| Bore ID | B | 6.065" | Sch 40 bore |
| Tolerances (Hub at Weld) | - | +0.15" / -0.03" | ASME B16.5 (NPS ≥6) |
| Weld Prep Bevel | - | 37.5° | ASME B16.25 |

### Hub Taper Calculation

```
Taper Length = Y - Straight - Flange contribution
             = 3.44" - 0.236" - ~0.25" = ~2.95"

Taper per side = (X - A) / 2 = (7.56 - 6.625) / 2 = 0.4675"

Taper Angle = arctan(0.4675 / 2.95) = ~9° per side
```

### Component 2: 6" Sch 40 Pipe (FROM pipe_schedules.json)

| Dimension | Value | Source |
|-----------|-------|--------|
| NPS | 6" | pipe_schedules.json |
| Schedule | 40 | pipe_schedules.json |
| Outside Diameter | 6.625" | pipe_schedules.json |
| Wall Thickness | 0.280" | pipe_schedules.json |
| Inside Diameter | 6.065" | pipe_schedules.json |
| Weight | 18.97 lb/ft | pipe_schedules.json |
| Length | 6.00" | User-defined (parametric) |
| Weld Prep Bevel | 37.5° | ASME B16.25 |

---

## PHASE 4: BUILD STRATEGY

### Flange Part Sketch Profile (Revolve)

```
Point sequence (Right half, revolve about centerline):

1. Start at bore ID, bottom of flange
   (X=3.0325", Y=0)  ← Bore radius = 6.065/2

2. Move up to raised face height
   (X=3.0325", Y=1.0625")  ← Flange thickness + RF height

3. Move out to RF OD
   (X=4.25", Y=1.0625")  ← RF radius = 8.50/2

4. Move down RF height
   (X=4.25", Y=1.00")

5. Move out to flange OD
   (X=5.50", Y=1.00")  ← Flange OD radius = 11.00/2

6. Move down to bottom of flange
   (X=5.50", Y=0)

7. Move in to hub base OD
   (X=3.78", Y=0)  ← Hub base radius = 7.56/2

8. Taper down to weld point
   (X=3.3125", Y=-2.954")  ← Hub weld radius = 6.625/2, taper length

9. Straight section down
   (X=3.3125", Y=-3.19")  ← Add 0.236" straight

10. Move to bore ID at hub end
    (X=3.0325", Y=-3.19")

11. Close back to start
    (X=3.0325", Y=0)
```

### Assembly Mates (SPECIFIC)

| Mate | Type | Entity 1 | Entity 2 | Notes |
|------|------|----------|----------|-------|
| 1 | CONCENTRIC | Pipe OD cylinder | Flange hub weld OD (6.625") | Align centerlines |
| 2 | COINCIDENT | Pipe end face | Flange hub weld end face | 0 offset (butt weld) |

### Validation Checks

| Check | Expected | Method |
|-------|----------|--------|
| Concentricity | ≤0.010" | Measure at weld interface |
| OD match at weld | 6.625" ±0.03" | Both components |
| Interference | 0 | Run interference detection |
| Hub length | 3.44" | Measure from flange bottom |

---

## PHASE 5: API SEQUENCE

| Step | Endpoint | Validation |
|------|----------|------------|
| 1 | Create flange part with verified dims | Saved to output/ |
| 2 | Create pipe part from pipe_schedules.json | Saved to output/ |
| 3 | POST /com/solidworks/new_assembly | status=ok |
| 4 | POST /com/solidworks/insert_component (flange) | count=1 |
| 5 | POST /com/solidworks/insert_component (pipe) | count=2 |
| 6 | Add mates (concentric + coincident) | mates created |
| 7 | Run interference check | 0 interferences |
| 8 | POST /com/solidworks/save | status=ok |

---

## BOM

| Item | Part Number | Description | Qty | Material | Weight |
|------|-------------|-------------|-----|----------|--------|
| 1 | WNF-6-150-RF | 6" 150# WN Flange RF | 1 | A105 | ~25 lbs |
| 2 | PIPE-6-S40-6L | 6" Sch 40 Pipe x 6" | 1 | A106 Gr.B | ~9.5 lbs |
| | | **TOTAL** | | | **~34.5 lbs** |

---

## DATA SOURCES VERIFIED

- [x] pipe_schedules.json: NPS 6 Sch 40 → OD 6.625", Wall 0.280", ID 6.065"
- [x] ASME B16.5 verified tables: Y=3.44", X=7.56", A=6.625"
- [x] ASME B16.25: 37.5° weld prep bevel
- [ ] engineering_standards.json: Needs correction (has wrong values)

---

## APPROVAL REQUIRED

This plan uses ONLY verified dimensions from:
1. pipe_schedules.json (confirmed correct)
2. External ASME B16.5 tables (user-provided verified values)

**Awaiting user approval before proceeding with build.**
