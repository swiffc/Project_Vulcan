# PROJECT VULCAN - COMPLETE VERIFICATION REQUIREMENTS
## AI Engineering Drawing Analysis System
## Version 2.0
## Referenced in: task.md (Phase 15: CAD Drawing Review Bot)

---

# TABLE OF CONTENTS

1. [Mandatory Verification Checks](#part-1-mandatory-verification-checks)
2. [Speed Optimization Strategies](#part-2-speed-optimization-strategies)
3. [Standards Database Schema](#part-3-standards-database-schema)
4. [Suggested Workflow](#part-4-suggested-workflow)

---

# PART 1: MANDATORY VERIFICATION CHECKS

## 1.1 VISUAL VERIFICATION (CRITICAL)

**ALL drawings must be verified visually - NEVER rely on text extraction alone**

```
WORKFLOW:
1. Extract PDF → Images
2. Analyze EACH page visually
3. Cross-reference text data with visual
4. Record verified data
5. DELETE temp images after verification
```

---

## 1.2 WEIGHT VERIFICATION

### Check Part Weight Against:

| Material | Density | Formula |
|----------|---------|---------|
| Steel | 0.284 lb/in³ | Volume × 0.284 |
| Aluminum | 0.098 lb/in³ | Volume × 0.098 |
| Stainless | 0.289 lb/in³ | Volume × 0.289 |

### Standard Beam Weights (AISC):

| Shape | Weight/ft | Check |
|-------|-----------|-------|
| W8×31 | 31 lb/ft | Length × 31 |
| W8×18 | 18 lb/ft | Length × 18 |
| W6×15 | 15 lb/ft | Length × 15 |
| L3×3×3/16 | 3.71 lb/ft | Length × 3.71 |
| L3×3×1/4 | 4.9 lb/ft | Length × 4.9 |

### Example Weight Check:

```
5A-B MIDBEAM: W8×31, Length = 6'-8 3/16" = 6.682 ft
CALCULATED: 6.682 × 31 = 207.1 lb
DRAWING SHOWS: 214.31 lb
DIFFERENCE: 7.2 lb (3.5%) - ACCEPTABLE (includes end plate)
```

### Weight Tolerance:

- ±5% for simple parts
- ±10% for assemblies with welds
- FLAG if >10% difference

---

## 1.3 BEAM SIZE VERIFICATION

### Verify Description Matches Actual Dimensions:

| Description | Actual d | Actual bf | Actual tw | Actual tf |
|-------------|----------|-----------|-----------|-----------|
| W8×31 | 8.00" | 7.995" | 0.285" | 0.435" |
| W8×18 | 8.14" | 5.250" | 0.230" | 0.330" |
| W6×15 | 5.99" | 5.990" | 0.230" | 0.260" |

### Check From Drawing:

```
IF drawing shows (8") depth AND (8") flange width
THEN W8×31 is CORRECT

IF description says "W8×31" but dims show 6" flange
THEN FLAG: "DESCRIPTION MISMATCH - Verify beam size"
```

---

## 1.4 DESCRIPTION vs ACTUAL DIMENSIONS CHECK

### Verify Material Description Matches Part:

| Description | Expected Thickness | Tolerance |
|-------------|-------------------|-----------|
| PLATE_1/4" | 0.250" | ±0.010" |
| PLATE_3/8" | 0.375" | ±0.010" |
| PLATE_1/2" | 0.500" | ±0.015" |
| SHEET_10GA | 0.1345" | ±0.007" |
| SHEET_12GA | 0.1046" | ±0.005" |
| SHEET_14GA | 0.0747" | ±0.004" |

### FLAG IF:

- Description says 1/4" but drawing shows 3/8"
- Description says 10GA but drawing shows 0.1875"
- Any mismatch >1 gauge or >1/16" plate

---

## 1.5 SHEET METAL BEND VERIFICATION

### Minimum Bend Radius by Material Thickness:

| Thickness | Min Inside Radius (Mild Steel) | Min IR (A572-50) |
|-----------|-------------------------------|------------------|
| 10GA (0.134") | 0.134" (1T) | 0.201" (1.5T) |
| 1/8" (0.125") | 0.125" (1T) | 0.188" (1.5T) |
| 3/16" (0.188") | 0.188" (1T) | 0.281" (1.5T) |
| 1/4" (0.250") | 0.250" (1T) | 0.375" (1.5T) |
| 3/8" (0.375") | 0.375" (1T) | 0.563" (1.5T) |

### K-Factor for Bend Allowance:

- Soft materials (1010 steel): K = 0.33
- Medium (A36, A572): K = 0.40-0.45
- Hard (spring steel): K = 0.50

### FLAG IF:

- Bend radius < 1T (will crack)
- Bend radius < 1.5T for high-strength steel
- No bend radius specified

---

## 1.6 HOLE EDGE DISTANCE VERIFICATION

### Minimum Edge Distance (AISC Table J3.4):

| Bolt Dia | Hole Dia | Min Edge (Sheared) | Min Edge (Rolled/Cut) |
|----------|----------|-------------------|----------------------|
| 1/2" | 9/16" | 7/8" | 3/4" |
| 5/8" | 11/16" | 1-1/8" | 7/8" |
| 3/4" | 13/16" | 1-1/4" | 1" |
| 7/8" | 15/16" | 1-1/2" | 1-1/8" |
| 1" | 1-1/16" | 1-3/4" | 1-1/4" |

### Minimum End Distance:

- General: 1.5 × bolt diameter minimum
- Preferred: 2.0 × bolt diameter

### FLAG IF:

- Edge distance < minimum from AISC table
- End distance < 1.5 × bolt diameter
- Hole within 1" of bend line

---

## 1.7 FUNCTIONAL PURPOSE ANALYSIS

### Understand Part Function Before Review:

| Part Type | Primary Function | Critical Checks |
|-----------|-----------------|-----------------|
| LIFTING LUG | Rigging/handling | Edge distance, thickness, shackle fit |
| BACKING PLATE | Connection stiffening | Bolt pattern, contact area |
| KNEE BRACE | Lateral support | Bend angle, hole alignment |
| FAN RING | Air seal | Radius accuracy, pinch spacing |
| FLOOR PANEL | Walk surface | Deflection, slip resistance |
| STIFFENER | Panel support | Spacing, weld access |
| BEAM | Structural support | Deflection, connection capacity |

---

# PART 2: SPEED OPTIMIZATION STRATEGIES

## 2.1 PRE-LOADED STANDARDS DATABASE (CRITICAL)

**Build database of standard values for instant lookup:**

```python
# File: agents/cad_agent/adapters/standards_db.py

STANDARDS_DB = {
    "beams": {
        "W8x31": {"d": 8.00, "bf": 7.995, "tw": 0.285, "tf": 0.435, "wt_per_ft": 31},
        "W8x18": {"d": 8.14, "bf": 5.250, "tw": 0.230, "tf": 0.330, "wt_per_ft": 18},
        "W6x15": {"d": 5.99, "bf": 5.990, "tw": 0.230, "tf": 0.260, "wt_per_ft": 15},
        # ... all AISC shapes
    },
    "angles": {
        "L3x3x3/16": {"leg": 3.0, "t": 0.1875, "wt_per_ft": 3.71},
        "L3x3x1/4": {"leg": 3.0, "t": 0.250, "wt_per_ft": 4.9},
        # ... all angles
    },
    "plates": {
        "10GA": {"t": 0.1345, "wt_per_sqft": 5.625},
        "12GA": {"t": 0.1046, "wt_per_sqft": 4.375},
        "14GA": {"t": 0.0747, "wt_per_sqft": 3.125},
        "1/4": {"t": 0.250, "wt_per_sqft": 10.2},
        "3/8": {"t": 0.375, "wt_per_sqft": 15.3},
        "1/2": {"t": 0.500, "wt_per_sqft": 20.4},
        # ... all gauges/thicknesses
    },
    "edge_distances": {
        "1/2_bolt": {"hole": 0.5625, "min_sheared": 0.875, "min_rolled": 0.75},
        "5/8_bolt": {"hole": 0.6875, "min_sheared": 1.125, "min_rolled": 0.875},
        "3/4_bolt": {"hole": 0.8125, "min_sheared": 1.25, "min_rolled": 1.00},
        "7/8_bolt": {"hole": 0.9375, "min_sheared": 1.50, "min_rolled": 1.125},
        "1_bolt": {"hole": 1.0625, "min_sheared": 1.75, "min_rolled": 1.25},
    },
    "bend_radii": {
        "A572-50": {"factor": 1.5},  # 1.5T minimum
        "A36": {"factor": 1.0},      # 1T minimum
        "1010": {"factor": 0.5},     # 0.5T minimum (soft)
        "SS304": {"factor": 1.5},    # 1.5T minimum
    },
    "densities": {
        "steel": 0.284,      # lb/in³
        "aluminum": 0.098,   # lb/in³
        "stainless": 0.289,  # lb/in³
        "brass": 0.307,      # lb/in³
    }
}
```

**SPEED GAIN: Instant validation instead of manual lookup = 50% faster**

---

## 2.2 OCR + TEMPLATE MATCHING FOR TITLE BLOCKS

**Train OCR to recognize standard title block formats:**

```python
TITLE_BLOCK_PATTERNS = {
    "part_number": r"[A-Z0-9]+-[A-Z0-9]+(-[A-Z0-9]+)?",
    "material": r"(PLATE|BEAM|ANGLE|SHEET|TUBE|PIPE|HSS)_[\w_]+",
    "weight": r"WT:?\s*([\d.]+)\s*LBS?",
    "thickness": r"(\d+GA|\d+/\d+\"|\d+\.\d+\")",
    "finish": r"(GALV|PAINTED|BARE|HDG|MECH\s*GALV)",
}
```

**SPEED GAIN: 80% of metadata captured automatically = 30% faster**

---

## 2.3 PARALLEL PAGE PROCESSING

**Process multiple pages simultaneously:**

```python
from concurrent.futures import ThreadPoolExecutor

def analyze_page(page_num: int, pdf_path: str) -> dict:
    """Analyze a single page and return results."""
    # Extract image
    # Run checks
    # Return results
    pass

def analyze_pdf_parallel(pdf_path: str, max_workers: int = 8) -> list:
    """Process all pages in parallel."""
    page_count = get_page_count(pdf_path)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(analyze_page, i, pdf_path)
            for i in range(page_count)
        ]
        results = [f.result() for f in futures]

    return results
```

**SPEED GAIN: 8× faster for large drawing packages**

---

## 2.4 SMART PART GROUPING

**Group similar parts for batch verification:**

```python
PART_GROUPS = {
    "plates": ["5A-A", "5A-AA", "5A-D", "5A-AD", "5A-E", "5A-F", "5A-G"],
    "beams": ["5A-B", "5A-C", "5A-Z"],
    "sheets": ["5A-H", "5A-J", "5A-Q", "5A-U"],
    "angles": ["5A-P", "5A-N"],
}

# Checks by group
GROUP_CHECKS = {
    "plates": ["edge_distance", "bend_radius", "thickness", "weight"],
    "beams": ["weight_per_ft", "section_properties", "hole_gauge"],
    "sheets": ["gauge_verify", "bend_radius", "deflection"],
    "angles": ["leg_size", "thickness", "hole_pattern"],
}
```

**SPEED GAIN: 25% faster on grouped parts**

---

## 2.5 AUTOMATED RED FLAG DETECTION

**Pre-scan for obvious issues before detailed review:**

```python
def red_flag_scan(part: Part) -> list[str]:
    """Quick scan for obvious issues."""
    flags = []

    # Edge distance too small
    if part.edge_dist < get_min_edge(part.bolt_size, "rolled"):
        flags.append(f"EDGE_DIST: {part.edge_dist}\" < min {get_min_edge(part.bolt_size, 'rolled')}\"")

    # Bend radius too tight
    min_radius = part.thickness * get_bend_factor(part.material)
    if part.bend_radius < min_radius:
        flags.append(f"BEND_RADIUS: R{part.bend_radius}\" < min R{min_radius}\"")

    # Non-standard hole size
    std_holes = [0.5625, 0.6875, 0.8125, 0.9375, 1.0625]
    if part.hole_dia not in std_holes:
        flags.append(f"NON_STD_HOLE: Ø{part.hole_dia}\" not standard")

    # Weight mismatch >10%
    calc_weight = calculate_weight(part)
    if abs(calc_weight - part.stated_weight) / part.stated_weight > 0.10:
        flags.append(f"WEIGHT_MISMATCH: Calc {calc_weight:.1f} vs Stated {part.stated_weight:.1f} lb")

    # Description mismatch
    if not verify_description(part.description, part.dimensions):
        flags.append(f"DESC_MISMATCH: {part.description} doesn't match dims")

    return flags
```

**SPEED GAIN: Focus review time on problem areas = 40% faster**

---

## 2.6 INCREMENTAL VERIFICATION CACHING

**Cache verified parts for similar future drawings:**

```python
import json
from datetime import datetime

CACHE_FILE = "verified_cache.json"

def load_cache() -> dict:
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cache(cache: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_cached_verification(shape: str) -> dict | None:
    cache = load_cache()
    if shape in cache:
        return cache[shape]
    return None

def cache_verification(shape: str, data: dict):
    cache = load_cache()
    cache[shape] = {
        **data,
        "verified": True,
        "date": datetime.now().isoformat()
    }
    save_cache(cache)
```

**SPEED GAIN: Skip re-verifying standard shapes = 20% faster on repeat jobs**

---

## 2.7 PROGRESSIVE DETAIL LEVELS

**Three-tier verification approach:**

```python
class VerificationTier:
    QUICK = 1      # 2 min - BOM count, title blocks, obvious errors
    STANDARD = 2   # 15 min - Weight, description, dimensions, holes
    DEEP = 3       # 30+ min - Edge dist, bend radius, structural, interference

def get_verification_tier(part: Part, flags: list) -> int:
    """Determine required verification depth."""
    if flags:
        return VerificationTier.DEEP
    if part.is_critical or part.is_structural:
        return VerificationTier.STANDARD
    return VerificationTier.QUICK
```

**Use Tier 1 for initial screening, Tier 3 only for flagged items**

---

## 2.8 ESTIMATED SPEED IMPROVEMENTS

| Optimization | Time Saved |
|--------------|------------|
| Pre-loaded standards DB | 50% |
| Parallel processing | 40% |
| Auto title block OCR | 30% |
| Smart grouping | 25% |
| Red flag pre-scan | 40% |
| Caching | 20% |
| **COMBINED** | **~70-80% faster** |

---

# PART 3: STANDARDS DATABASE SCHEMA

## 3.1 AISC SHAPES (W-Sections)

```python
# File: agents/cad_agent/data/aisc_w_shapes.py

W_SHAPES = {
    # Shape: {d, bf, tw, tf, wt_per_ft, A, Ix, Sx, Zx, Iy, Sy, Zy}
    "W4x13": {"d": 4.16, "bf": 4.060, "tw": 0.280, "tf": 0.345, "wt": 13},
    "W5x16": {"d": 5.01, "bf": 5.000, "tw": 0.240, "tf": 0.360, "wt": 16},
    "W5x19": {"d": 5.15, "bf": 5.030, "tw": 0.270, "tf": 0.430, "wt": 19},
    "W6x9": {"d": 5.90, "bf": 3.940, "tw": 0.170, "tf": 0.215, "wt": 9},
    "W6x12": {"d": 6.03, "bf": 4.000, "tw": 0.230, "tf": 0.280, "wt": 12},
    "W6x15": {"d": 5.99, "bf": 5.990, "tw": 0.230, "tf": 0.260, "wt": 15},
    "W6x16": {"d": 6.28, "bf": 4.030, "tw": 0.260, "tf": 0.405, "wt": 16},
    "W6x20": {"d": 6.20, "bf": 6.020, "tw": 0.260, "tf": 0.365, "wt": 20},
    "W6x25": {"d": 6.38, "bf": 6.080, "tw": 0.320, "tf": 0.455, "wt": 25},
    "W8x10": {"d": 7.89, "bf": 3.940, "tw": 0.170, "tf": 0.205, "wt": 10},
    "W8x13": {"d": 7.99, "bf": 4.000, "tw": 0.230, "tf": 0.255, "wt": 13},
    "W8x15": {"d": 8.11, "bf": 4.015, "tw": 0.245, "tf": 0.315, "wt": 15},
    "W8x18": {"d": 8.14, "bf": 5.250, "tw": 0.230, "tf": 0.330, "wt": 18},
    "W8x21": {"d": 8.28, "bf": 5.270, "tw": 0.250, "tf": 0.400, "wt": 21},
    "W8x24": {"d": 7.93, "bf": 6.495, "tw": 0.245, "tf": 0.400, "wt": 24},
    "W8x28": {"d": 8.06, "bf": 6.535, "tw": 0.285, "tf": 0.465, "wt": 28},
    "W8x31": {"d": 8.00, "bf": 7.995, "tw": 0.285, "tf": 0.435, "wt": 31},
    "W8x35": {"d": 8.12, "bf": 8.020, "tw": 0.310, "tf": 0.495, "wt": 35},
    "W8x40": {"d": 8.25, "bf": 8.070, "tw": 0.360, "tf": 0.560, "wt": 40},
    "W8x48": {"d": 8.50, "bf": 8.110, "tw": 0.400, "tf": 0.685, "wt": 48},
    "W8x58": {"d": 8.75, "bf": 8.220, "tw": 0.510, "tf": 0.810, "wt": 58},
    "W8x67": {"d": 9.00, "bf": 8.280, "tw": 0.570, "tf": 0.935, "wt": 67},
    "W10x12": {"d": 9.87, "bf": 3.960, "tw": 0.190, "tf": 0.210, "wt": 12},
    "W10x15": {"d": 9.99, "bf": 4.000, "tw": 0.230, "tf": 0.270, "wt": 15},
    "W10x17": {"d": 10.11, "bf": 4.010, "tw": 0.240, "tf": 0.330, "wt": 17},
    "W10x19": {"d": 10.24, "bf": 4.020, "tw": 0.250, "tf": 0.395, "wt": 19},
    "W10x22": {"d": 10.17, "bf": 5.750, "tw": 0.240, "tf": 0.360, "wt": 22},
    "W10x26": {"d": 10.33, "bf": 5.770, "tw": 0.260, "tf": 0.440, "wt": 26},
    "W10x30": {"d": 10.47, "bf": 5.810, "tw": 0.300, "tf": 0.510, "wt": 30},
    "W10x33": {"d": 9.73, "bf": 7.960, "tw": 0.290, "tf": 0.435, "wt": 33},
    "W10x39": {"d": 9.92, "bf": 7.985, "tw": 0.315, "tf": 0.530, "wt": 39},
    "W10x45": {"d": 10.10, "bf": 8.020, "tw": 0.350, "tf": 0.620, "wt": 45},
    "W12x14": {"d": 11.91, "bf": 3.970, "tw": 0.200, "tf": 0.225, "wt": 14},
    "W12x16": {"d": 11.99, "bf": 3.990, "tw": 0.220, "tf": 0.265, "wt": 16},
    "W12x19": {"d": 12.16, "bf": 4.005, "tw": 0.235, "tf": 0.350, "wt": 19},
    "W12x22": {"d": 12.31, "bf": 4.030, "tw": 0.260, "tf": 0.425, "wt": 22},
    "W12x26": {"d": 12.22, "bf": 6.490, "tw": 0.230, "tf": 0.380, "wt": 26},
    "W12x30": {"d": 12.34, "bf": 6.520, "tw": 0.260, "tf": 0.440, "wt": 30},
    "W12x35": {"d": 12.50, "bf": 6.560, "tw": 0.300, "tf": 0.520, "wt": 35},
    "W12x40": {"d": 11.94, "bf": 8.005, "tw": 0.295, "tf": 0.515, "wt": 40},
    "W12x45": {"d": 12.06, "bf": 8.045, "tw": 0.335, "tf": 0.575, "wt": 45},
    "W12x50": {"d": 12.19, "bf": 8.080, "tw": 0.370, "tf": 0.640, "wt": 50},
    "W12x53": {"d": 12.06, "bf": 9.995, "tw": 0.345, "tf": 0.575, "wt": 53},
    "W12x58": {"d": 12.19, "bf": 10.010, "tw": 0.360, "tf": 0.640, "wt": 58},
    "W12x65": {"d": 12.12, "bf": 12.000, "tw": 0.390, "tf": 0.605, "wt": 65},
}
```

## 3.2 ANGLES (L-Shapes)

```python
# File: agents/cad_agent/data/aisc_angles.py

ANGLES = {
    # Equal leg angles: L{leg}x{leg}x{t}
    "L2x2x1/8": {"leg": 2.0, "t": 0.125, "wt": 0.98},
    "L2x2x3/16": {"leg": 2.0, "t": 0.1875, "wt": 1.44},
    "L2x2x1/4": {"leg": 2.0, "t": 0.250, "wt": 1.88},
    "L2-1/2x2-1/2x3/16": {"leg": 2.5, "t": 0.1875, "wt": 1.83},
    "L2-1/2x2-1/2x1/4": {"leg": 2.5, "t": 0.250, "wt": 2.38},
    "L3x3x3/16": {"leg": 3.0, "t": 0.1875, "wt": 3.71},
    "L3x3x1/4": {"leg": 3.0, "t": 0.250, "wt": 4.90},
    "L3x3x5/16": {"leg": 3.0, "t": 0.3125, "wt": 6.10},
    "L3x3x3/8": {"leg": 3.0, "t": 0.375, "wt": 7.20},
    "L3-1/2x3-1/2x1/4": {"leg": 3.5, "t": 0.250, "wt": 5.80},
    "L3-1/2x3-1/2x5/16": {"leg": 3.5, "t": 0.3125, "wt": 7.20},
    "L3-1/2x3-1/2x3/8": {"leg": 3.5, "t": 0.375, "wt": 8.50},
    "L4x4x1/4": {"leg": 4.0, "t": 0.250, "wt": 6.60},
    "L4x4x5/16": {"leg": 4.0, "t": 0.3125, "wt": 8.20},
    "L4x4x3/8": {"leg": 4.0, "t": 0.375, "wt": 9.80},
    "L4x4x1/2": {"leg": 4.0, "t": 0.500, "wt": 12.80},
    "L5x5x5/16": {"leg": 5.0, "t": 0.3125, "wt": 10.30},
    "L5x5x3/8": {"leg": 5.0, "t": 0.375, "wt": 12.30},
    "L5x5x1/2": {"leg": 5.0, "t": 0.500, "wt": 16.20},
    "L6x6x3/8": {"leg": 6.0, "t": 0.375, "wt": 14.90},
    "L6x6x1/2": {"leg": 6.0, "t": 0.500, "wt": 19.60},
    "L6x6x5/8": {"leg": 6.0, "t": 0.625, "wt": 24.20},
}
```

## 3.3 SHEET METAL GAUGES

```python
# File: agents/cad_agent/data/sheet_gauges.py

SHEET_GAUGES = {
    # Gauge: {thickness_in, wt_per_sqft_steel}
    "7GA": {"t": 0.1793, "wt_sqft": 7.5},
    "8GA": {"t": 0.1644, "wt_sqft": 6.875},
    "9GA": {"t": 0.1495, "wt_sqft": 6.25},
    "10GA": {"t": 0.1345, "wt_sqft": 5.625},
    "11GA": {"t": 0.1196, "wt_sqft": 5.0},
    "12GA": {"t": 0.1046, "wt_sqft": 4.375},
    "13GA": {"t": 0.0897, "wt_sqft": 3.75},
    "14GA": {"t": 0.0747, "wt_sqft": 3.125},
    "15GA": {"t": 0.0673, "wt_sqft": 2.8125},
    "16GA": {"t": 0.0598, "wt_sqft": 2.5},
    "17GA": {"t": 0.0538, "wt_sqft": 2.25},
    "18GA": {"t": 0.0478, "wt_sqft": 2.0},
    "19GA": {"t": 0.0418, "wt_sqft": 1.75},
    "20GA": {"t": 0.0359, "wt_sqft": 1.5},
    "22GA": {"t": 0.0299, "wt_sqft": 1.25},
    "24GA": {"t": 0.0239, "wt_sqft": 1.0},
    "26GA": {"t": 0.0179, "wt_sqft": 0.75},
}

PLATE_THICKNESSES = {
    # Fraction: {thickness_in, wt_per_sqft_steel}
    "1/16": {"t": 0.0625, "wt_sqft": 2.55},
    "3/32": {"t": 0.09375, "wt_sqft": 3.83},
    "1/8": {"t": 0.125, "wt_sqft": 5.10},
    "3/16": {"t": 0.1875, "wt_sqft": 7.65},
    "1/4": {"t": 0.250, "wt_sqft": 10.20},
    "5/16": {"t": 0.3125, "wt_sqft": 12.75},
    "3/8": {"t": 0.375, "wt_sqft": 15.30},
    "7/16": {"t": 0.4375, "wt_sqft": 17.85},
    "1/2": {"t": 0.500, "wt_sqft": 20.40},
    "9/16": {"t": 0.5625, "wt_sqft": 22.95},
    "5/8": {"t": 0.625, "wt_sqft": 25.50},
    "3/4": {"t": 0.750, "wt_sqft": 30.60},
    "7/8": {"t": 0.875, "wt_sqft": 35.70},
    "1": {"t": 1.000, "wt_sqft": 40.80},
}
```

---

# PART 4: SUGGESTED WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: UPLOAD PDF                                         │
│  → Auto-extract all pages to images                         │
│  → OCR title blocks for metadata                            │
│  → Build part list from BOM                                 │
│  → Load standards database                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: AUTOMATED PRE-SCAN (Red Flags)                     │
│  → Check weights against calculated                         │
│  → Verify descriptions match dims                           │
│  → Flag non-standard hole sizes                             │
│  → Check bend radii against material                        │
│  → Identify edge distance concerns                          │
│  → Group by verification tier                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: PARALLEL PROCESSING                                │
│  → Process 8 pages simultaneously                           │
│  → Apply group-specific checks                              │
│  → Use cached verifications where available                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: VISUAL VERIFICATION (FLAGGED ITEMS ONLY)           │
│  → Show image + extracted data side-by-side                 │
│  → User confirms or corrects                                │
│  → AI learns from corrections                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: CROSS-CHECK MATING PARTS                           │
│  → Verify hole patterns align (±1/16")                      │
│  → Check BOM completeness                                   │
│  → Validate assembly fit                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: FUNCTIONAL ANALYSIS                                │
│  → Understand assembly purpose                              │
│  → Check part function vs design                            │
│  → Verify fits, clearances, tolerances                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: OUTPUT & CLEANUP                                   │
│  → Generate verification report                             │
│  → Export JSON/Excel data                                   │
│  → Cache verified shapes for future                         │
│  → DELETE temp images                                       │
│  → Save only final outputs                                  │
└─────────────────────────────────────────────────────────────┘
```

---

**END OF VERIFICATION REQUIREMENTS DOCUMENT**

*Document Version: 2.0*
*Last Updated: 2025-12-21*
*Project: Vulcan AI Engineering Drawing Analysis*
*Referenced in: task.md Phase 15*
