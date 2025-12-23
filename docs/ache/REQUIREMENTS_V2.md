# PROJECT VULCAN - VERIFICATION REQUIREMENTS V2

---

# MANDATORY CHECKS

## 1. VISUAL VERIFICATION (CRITICAL)
ALL drawings must be verified visually - NEVER rely on text extraction alone

## 2. WEIGHT VERIFICATION
| Material | Density |
|----------|---------|
| Steel | 0.284 lb/in3 |
| Aluminum | 0.098 lb/in3 |
| Stainless | 0.289 lb/in3 |

Tolerance: +/-5% simple, +/-10% assemblies

## 3. DESCRIPTION MATCH
| Description | Expected |
|-------------|----------|
| PLATE_1/4" | 0.250" |
| SHEET_10GA | 0.1345" |

## 4. BEND RADIUS
| Material | Min Radius |
|----------|------------|
| A36 | 1.0T |
| A572-50 | 1.5T |
| Stainless | 2.0T |

## 5. EDGE DISTANCE (AISC J3.4)
| Bolt | Min Edge (Rolled) |
|------|-------------------|
| 1/2" | 3/4" |
| 5/8" | 7/8" |
| 3/4" | 1" |
| 7/8" | 1-1/8" |
| 1" | 1-1/4" |

---

# SPEED OPTIMIZATIONS

1. Pre-loaded standards DB -> 50% faster
2. Parallel processing -> 40% faster  
3. Auto title block OCR -> 30% faster
4. Red flag pre-scan -> 40% faster
5. Caching -> 20% faster

**COMBINED: ~70-80% faster**

---

# WORKFLOW

1. UPLOAD PDF -> Extract images, OCR title blocks
2. AUTO PRE-SCAN -> Check weights, descriptions, holes
3. VISUAL VERIFY -> Flagged items only
4. FUNCTIONAL ANALYSIS -> Assembly purpose
---

# 6. API 661 SPECIFIC REQUIREMENTS

### Tube Bundle Design
| Parameter | API 661 Requirement |
|-----------|---------------------|
| Tube OD | 1" or 1-1/4" typical |
| Fin type | Embedded, extruded, or welded |
| Fin density | 8-11 fins/inch typical |
| Tube pitch | 2.0" - 2.5" typical |
| Header plate thickness | Per API 661 Table 1 |

### Fan Requirements (API 661 Section 6.3)
| Fan Diameter | Max Tip Clearance |
|--------------|-------------------|
| 4'-5' | 3/8" |
| 6'-8' | 1/2" |
| 9'-12' | 5/8" |
| 13'-18' | 3/4" |
| 19'-28' | 1" |
| >28' | 1-1/4" |

### Air-Side Pressure Drop
- Maximum: 0.5" H2O (typical)
- Calculation: ΔP = (V²/2g) × K
  - V = face velocity (ft/s)
  - K = resistance coefficient
  - g = 32.2 ft/s²

### Performance Testing (API 661 Section 7)
- [ ] Heat duty within ±5% of rated
- [ ] Air flow within ±10% of design
- [ ] Process outlet temperature within ±5°F
- [ ] Mechanical run test: 4 hours minimum
- [ ] Vibration limits: 0.2" peak-to-peak displacement

---

# 7. THERMAL RATING FORMULAS

### Log Mean Temperature Difference (LMTD)
```
LMTD = (ΔT1 - ΔT2) / ln(ΔT1 / ΔT2)
```
*Note: Apply F-factor for cross-flow correction.*

### Heat Duty (Q)
```
Q = U * A * MTD
```
- U = Overall heat transfer coefficient
- A = Total surface area
- MTD = Corrected Mean Temperature Difference

### Overall Heat Transfer Coefficient (U)
```
1/Uc = 1/ha + 1/hp + Rf
```
- ha = Air-side coefficient
- hp = Process-side coefficient
- Rf = Fouling factor
