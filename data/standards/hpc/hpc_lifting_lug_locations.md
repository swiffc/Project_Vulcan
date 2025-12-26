# HPC Lifting Lug Location Standards

**Source**: Standards Book II Vol. I  
**Extracted**: December 25, 2025

---

## Location Drawing References

### Standard Location Drawings

The specific lifting lug location coordinates are defined in **Excel drawing files**:

| Drawing Reference | Description | Contains |
|------------------|-------------|----------|
| **F 7REF6** | LIFT LUG LOC.ND | Induced Draft location coordinates |
| **F 7REF7** | LIFT LUG LOC.FD | Forced Draft location coordinates |
| **F 7REF8** | 1 FAN ND SUP & LUG LOC. | 1 Fan Induced Draft locations |
| **F 7REF9** | 2 FAN ND SUP/LUG | 2 Fan Induced Draft locations |
| **F 7REF10** | 3 FAN ND SUP/LUG | 3 Fan Induced Draft locations |
| **F 7REF11** | 1 FAN FD SUP/LUG LOC. | 1 Fan Forced Draft locations |
| **F 7REF13** | 3 FAN FD SUP/LUG | 3 Fan Forced Draft locations |

**Note**: These are MS Excel files that contain the specific coordinate locations for each configuration.

---

## Location Requirements

### General Requirements

1. **Location Source**:
   - Lifting lug locations are defined in **Hood Program** (Macintosh-based)
   - Locations have been **updated** in the Hood Program
   - Standard locations are provided in Excel reference drawings

2. **Location Validation**:
   - **Non-standard lifting lug locations must be verified**
   - Default program setup uses W708 lifting lug
   - Locations must accommodate air seal block outs

3. **Spacing Requirements**:
   - **Maximum spacing**: 23'-0" centerline to centerline
   - Lifting lug center line location is **critical**

### Configuration-Specific Locations

Locations vary by:
- **Draft Type**: Induced Draft (ND) vs Forced Draft (FD)
- **Fan Count**: 1, 2, or 3 fans
- **Unit Configuration**: Specific to each unit design

---

## Hood Program Integration

### Location Updates

The Hood Program (Macintosh-based) contains:
- Updated lifting lug locations
- Standard location coordinates for all configurations
- Default W708 lifting lug locations

### Program Output

After running Hood Program, check:
1. ✅ Lifting lug locations match standard drawings
2. ⚠️ **Non-standard lifting lug locations** (must verify)
3. ⚠️ Lifting lug size for air seal block outs

---

## Location Data Structure

```json
{
  "lifting_lug_locations": {
    "source": "Hood Program and Excel reference drawings (F 7REF6, F 7REF7, etc.)",
    "location_files": {
      "induced_draft": "F 7REF6 - LIFT LUG LOC.ND",
      "forced_draft": "F 7REF7 - LIFT LUG LOC.FD",
      "1_fan_nd": "F 7REF8 - 1 FAN ND SUP & LUG LOC.",
      "2_fan_nd": "F 7REF9 - 2 FAN ND SUP/LUG",
      "3_fan_nd": "F 7REF10 - 3 FAN ND SUP/LUG",
      "1_fan_fd": "F 7REF11 - 1 FAN FD SUP/LUG LOC.",
      "3_fan_fd": "F 7REF13 - 3 FAN FD SUP/LUG"
    },
    "requirements": {
      "max_spacing_centerline_to_centerline_ft": 23.0,
      "location_updated_in_program": true,
      "non_standard_locations_require_verification": true,
      "center_line_critical": true
    },
    "notes": [
      "Specific coordinates are in Excel files, not PDF",
      "Hood Program contains updated locations",
      "Locations vary by draft type and fan count",
      "Must verify non-standard locations"
    ]
  }
}
```

---

## Integration Notes

### For CAD Validation

When validating lifting lug locations:

1. **Check Drawing Reference**:
   - Verify correct drawing reference is used (F 7REF6, F 7REF7, etc.)
   - Match configuration (ND/FD, fan count)

2. **Verify Spacing**:
   - Check centerline to centerline ≤ 23'-0"
   - Verify center line location is correct

3. **Check for Non-Standard Locations**:
   - Flag any locations not matching standard drawings
   - Require verification/approval for non-standard locations

4. **Air Seal Clearance**:
   - Verify block out dimensions accommodate air seals
   - Check lug size matches air seal requirements

### For Design Recommender

When recommending lifting lug locations:

1. **Use Hood Program Output** (if available)
2. **Reference Standard Drawings** (F 7REF6, F 7REF7, etc.)
3. **Verify Spacing** meets 23'-0" maximum
4. **Flag Non-Standard** locations for review

---

## Missing Data

**Note**: The specific coordinate locations are **not in the PDF text** - they are in:
- Excel files (F 7REF6, F 7REF7, etc.) - **Need to extract separately**
- Hood Program output - **Macintosh-based program**

**Action Required**: 
- Extract location coordinates from Excel reference drawings
- Or integrate with Hood Program output
- Or manually document standard locations from drawings

---

**Last Updated**: December 25, 2025  
**Status**: Location references documented, coordinates need extraction from Excel files

