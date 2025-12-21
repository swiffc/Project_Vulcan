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
5. OUTPUT -> Report, DELETE temp images