# PROJECT VULCAN - MASTER TASK LIST & BOT ARCHITECTURE
## Standards Checker Agent - Structural Engineer & Designer Capabilities
## Version 1.0 | Created: 2025-12-21

---

# SECTION 1: TASK LIST - WHAT WE LEARNED & NEED TO IMPLEMENT

## ✅ COMPLETED TASKS

| Task | Status | Notes |
|------|--------|-------|
| Visual verification requirement | ✅ DONE | Never trust text extraction alone |
| Delete temp images after analysis | ✅ DONE | Save space requirement |
| Basic dimension extraction | ✅ DONE | JSON + Excel output |
| BOM extraction | ✅ DONE | Part list with quantities |

---

## 🔲 NEW TASKS TO IMPLEMENT

### TASK 1: Weight Verification System
**Priority: HIGH**
```
[ ] Build material density database
    - Steel: 0.284 lb/in³
    - Aluminum: 0.098 lb/in³
    - Stainless: 0.289 lb/in³
    
[ ] Build standard shape weight tables (AISC)
    - All W-shapes (W4×13 through W44×335)
    - All angles (L2×2×1/8 through L8×8×1)
    - All channels, tubes, pipes
    
[ ] Create weight calculator
    - Input: dimensions + material
    - Output: calculated weight
    - Compare to stated weight
    - Flag if >10% difference
```

### TASK 2: Description vs Dimensions Matcher
**Priority: HIGH**
```
[ ] Parse material descriptions
    - "PLATE_1/4"_A572_50" → thickness=0.250", material=A572-50
    - "BEAM_W_8X31_A992" → d=8.00", bf=7.995", wt=31 lb/ft
    - "SHEET_10GA_A1011-33" → thickness=0.1345"
    
[ ] Extract actual dimensions from drawing
    - Look for (parentheses) = reference dims
    - Look for thickness callouts
    - Look for section views
    
[ ] Compare and flag mismatches
    - Description says 1/4" but drawing shows 3/8" = FLAG
    - Description says W8×31 but drawing shows 6" flange = FLAG
```

### TASK 3: Bend Radius Checker (Sheet Metal)
**Priority: HIGH**
```
[ ] Build minimum bend radius table
    Material Type | Min Bend Radius
    -------------|----------------
    A36          | 1.0T (1× thickness)
    A572-50      | 1.5T
    Stainless    | 2.0T
    Aluminum     | 0.5T to 2.0T (varies by alloy)
    
[ ] Extract bend info from drawings
    - Bend angle (30°, 45°, 90°, etc.)
    - Inside radius (R1/2", R1", etc.)
    - Material thickness
    
[ ] Validate bends
    - IF radius < minimum THEN FLAG "BEND TOO TIGHT - WILL CRACK"
    - IF no radius specified THEN FLAG "MISSING BEND RADIUS"
```

### TASK 4: Edge Distance Checker
**Priority: HIGH**
```
[ ] Build AISC edge distance table (Table J3.4)
    Bolt Dia | Hole Dia | Min Edge (Sheared) | Min Edge (Rolled)
    ---------|----------|-------------------|------------------
    1/2"     | 9/16"    | 7/8"              | 3/4"
    5/8"     | 11/16"   | 1-1/8"            | 7/8"
    3/4"     | 13/16"   | 1-1/4"            | 1"
    7/8"     | 15/16"   | 1-1/2"            | 1-1/8"
    1"       | 1-1/16"  | 1-3/4"            | 1-1/4"
    
[ ] Calculate edge distances from drawings
    - Part width - hole centerline = edge distance
    - Hole to edge of cutout
    - Hole to bend line (should be >2× thickness)
    
[ ] Flag violations
    - "EDGE DISTANCE 0.72" < 1.00" MIN FOR 3/4" BOLT"
    - "HOLE TOO CLOSE TO BEND LINE"
```

### TASK 5-17: See full document for remaining tasks...

---

# SECTION 9: ACHE (AIR-COOLED HEAT EXCHANGER) SPECIFIC TASKS

## IMPORTANT: S25139-5A is an ACHE Plenum Assembly - NOT a Shell & Tube!

```
ACHE STRUCTURE:
                    TUBE BUNDLE (Finned Tubes)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    PLENUM CHAMBER  ← THIS IS S25139-5A!     │
│              ┌──────────┐    ┌──────────┐                   │
│              │ FAN RING │    │ FAN RING │                   │
│              └──────────┘    └──────────┘                   │
│     Floor panels, stiffeners, wall panels, corner angles    │
└─────────────────────────────────────────────────────────────┘
                           ↓
              STRUCTURAL SUPPORT FRAME
                           ↓
              PLATFORMS, LADDERS, WALKWAYS
```

## TASK 18: ACHE Component Recognition
**Priority: CRITICAL**

## TASK 19: Plenum Panel Checker
**Priority: HIGH**

## TASK 20: Fan Ring & Coverage Checker
**Priority: HIGH**

## TASK 21: Louver & Damper Checker
**Priority: MEDIUM**

## TASK 22: Weather Protection Checker
**Priority: MEDIUM**

## TASK 23: Winterization Checker
**Priority: MEDIUM**

---

# SECTION 10: ACCESS STRUCTURE TASKS (OSHA COMPLIANCE)

## TASK 24: Platform Checker - OSHA
## TASK 25: Ladder Checker - OSHA 1910.23
## TASK 26: Stair Checker - OSHA 1910.25
## TASK 27: Handrail & Guardrail Checker - OSHA 1910.29

---

# SECTION 11: COMPLETE 51-POINT ACHE CHECKLIST

See ACHE_CHECKLIST.md for complete details.

---

# SECTION 12: PRIORITY ORDER

| Priority | Task | Category |
|----------|------|----------|
| 1 | Standards Database | Foundation |
| 2 | Visual Verification | Core |
| 3 | ACHE Component Recognition | ACHE |
| 4 | Mating Part Hole Checker | Critical |
| 5 | Fan Ring & Coverage | ACHE |
| 6 | Plenum Panel Checker | ACHE |
| 7 | Platform Checker | OSHA |
| 8 | Ladder/Stair/Handrail | OSHA |
| 9-15 | Remaining tasks | Various |

---

# SECTION 14: ESTIMATED DEVELOPMENT TIME

**TOTAL: 22-28 days**

---

**Full 985-line document available - this is summary for GitHub.**