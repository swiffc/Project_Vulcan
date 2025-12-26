# HPC Lifting Lug Standards

**Source**: Standards Book II Vol. I  
**Extracted**: December 25, 2025

---

## Standard Lifting Lug Parts

### Part Numbers and Dimensions

| Part Number | Size (Thickness × Width) | Block Out Dimensions |
|-------------|-------------------------|---------------------|
| **W708** | 3/4" × 5-1/2" | A: 2-7/8", B: 2-7/8", C: 1" |
| **W709** | 3/4" × 7" | A: 3-5/8", B: 2-7/8", C: 1" |
| **W710** | 3/4" × 8" | A: 4-1/8", B: 2-7/8", C: 1" |
| **W711** | 1" × 7" | A: 3-5/8", B: 2-7/8", C: 1-1/4" |
| **W712** | 1" × 8" | A: 4-1/8", B: 2-7/8", C: 1-1/4" |

**Block Out Dimensions:**
- **A**: Horizontal dimension
- **B**: Vertical dimension  
- **C**: Thickness/clearance dimension

**Reference**: Lifting lug center line location

---

## Lifting Lug Requirements

### Quantity Requirements

1. **Standard Units**:
   - Units with **50' long tubes or greater**: **4 lifting lugs**
   - Units with **60' long tubes or greater**: **4 lifting lugs**

2. **Shop Lifting Arrangement**:
   - Only units with 60' long tubes or greater have 4 lifting lugs

### Location Requirements

1. **Standard Locations**:
   - Lifting lug locations have been updated in Hood Program
   - Default program setup uses **W708 lifting lug**
   - Non-standard lifting lug locations must be checked

2. **Air Seal Block Outs**:
   - Need to check lifting lug size for air seal block outs
   - Program defaults to W708, but other sizes may be required:
     - W708 (3/4" × 5-1/2")
     - W709 (3/4" × 7")
     - W710 (3/4" × 8")
     - W711 (1" × 7")
     - W712 (1" × 8")

### Maximum Distance

- **Maximum distance centerline to centerline of lifting lugs**: **23'-0"**

---

## Lifting Arrangement Drawings

### Standard Drawings Referenced

- **F 7REF5**: STD LIFTING LUG (MS Excel)
- **F 7REF6**: LIFT LUG LOC.ND (MS Excel) - Induced Draft
- **F 7REF7**: LIFT LUG LOC.FD (MS Excel) - Forced Draft
- **F 7REF8**: 1 FAN ND SUP & LUG LOC. (MS Excel)
- **F 7REF9**: 2 FAN ND SUP/LUG (MS Excel)
- **F 7REF10**: 3 FAN ND SUP/LUG (MS Excel)
- **F 7REF11**: 1 FAN FD SUP/LUG LOC. (MS Excel)
- **F 7REF13**: 3 FAN FD SUP/LUG (MS Excel)

### Suggested Lifting Arrangement

- Drawings show "SUGGESTED LIFTING ARRANGEMENT"
- Lifting beam with components shown in hidden line format
- Call-out indicates who will provide lifting equipment
- Dimensions shown on suggested lifting arrangement drawings

---

## Integration Notes

### Hood Program Integration

1. **Program Defaults**:
   - Hood Program runs on Macintosh only
   - Default lifting lug: **W708**
   - Lifting lug locations updated in program

2. **Things to Check After Running Hood Program**:
   - ✅ Bolts are not counted for fan guards (when required)
   - ⚠️ Some problems with 3 fan common center panel hoods
   - ⚠️ **Need to check lifting lug size for air seal block outs**
   - ⚠️ Check code 5 & 11 dimensions for vertical stiffener requirements
   - ⚠️ **Non-standard lifting lug locations**

### Material Considerations

- Lifting lugs may be made from header material
- Standard parts available in HPC parts library

---

## Related Standards

### From Standards Book I
- Part numbering system references: OW708, OW709, OW710, OW711, OW712

### From Standards Book II Vol. I
- General Arrangement procedures
- Machinery mount standards
- Fan order forms

---

## Validation Requirements

When validating CAD drawings, check:

1. ✅ **Quantity**: 4 lifting lugs for units ≥50' or ≥60' long tubes
2. ✅ **Part Number**: Standard part (W708-W712) specified
3. ✅ **Location**: Standard locations per drawing references
4. ✅ **Block Out Dimensions**: Correct dimensions for selected lug size
5. ✅ **Maximum Spacing**: Centerline to centerline ≤ 23'-0"
6. ✅ **Air Seal Clearance**: Block out dimensions accommodate air seals
7. ✅ **Lifting Arrangement**: Suggested lifting arrangement drawing included

---

## Data Structure

```json
{
  "lifting_lug_standards": {
    "standard_parts": [
      {
        "part_number": "W708",
        "thickness_in": 0.75,
        "width_in": 5.5,
        "block_out_dimensions": {
          "A_in": 2.875,
          "B_in": 2.875,
          "C_in": 1.0
        }
      },
      {
        "part_number": "W709",
        "thickness_in": 0.75,
        "width_in": 7.0,
        "block_out_dimensions": {
          "A_in": 3.625,
          "B_in": 2.875,
          "C_in": 1.0
        }
      },
      {
        "part_number": "W710",
        "thickness_in": 0.75,
        "width_in": 8.0,
        "block_out_dimensions": {
          "A_in": 4.125,
          "B_in": 2.875,
          "C_in": 1.0
        }
      },
      {
        "part_number": "W711",
        "thickness_in": 1.0,
        "width_in": 7.0,
        "block_out_dimensions": {
          "A_in": 3.625,
          "B_in": 2.875,
          "C_in": 1.25
        }
      },
      {
        "part_number": "W712",
        "thickness_in": 1.0,
        "width_in": 8.0,
        "block_out_dimensions": {
          "A_in": 4.125,
          "B_in": 2.875,
          "C_in": 1.25
        }
      }
    ],
    "requirements": {
      "quantity_rule": "4 lifting lugs for units with 50' or 60' long tubes or greater",
      "max_centerline_spacing_ft": 23.0,
      "default_part": "W708",
      "drawing_references": [
        "F 7REF5", "F 7REF6", "F 7REF7", "F 7REF8",
        "F 7REF9", "F 7REF10", "F 7REF11", "F 7REF13"
      ]
    }
  }
}
```

---

**Last Updated**: December 25, 2025  
**Source Pages**: Standards Book II Vol. I, Page ~197  
**Status**: Extracted and structured

