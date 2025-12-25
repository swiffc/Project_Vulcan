# Missing Helpful APIs - Gap Analysis

**Status:** 174 APIs implemented, ~30 high-value APIs missing  
**Date:** December 25, 2025

---

## 🎯 Summary

While the bot has **174 API endpoints** covering core CAD operations, there are **30 high-value APIs** that would significantly improve automation capabilities.

---

## 🔴 PRIORITY 1: High Impact, Commonly Needed (12 APIs)

### 1. Measurement APIs (4 missing)
**Gap:** Can get mass properties but cannot measure specific dimensions

| API | Use Case | Example |
|-----|----------|---------|
| `measure_distance` | Distance between faces/edges/points | "What's the distance between these two holes?" |
| `measure_angle` | Angle measurement | "Measure the angle of this bend" |
| `get_bounding_box` | Overall part dimensions | "Get the bounding box dimensions" |
| `check_clearance` | Minimum clearance checking | "What's the clearance between these parts?" |

**Impact:** HIGH - Users frequently need measurements for validation and documentation

---

### 2. Configuration APIs (3 missing)
**Gap:** No configuration management at all

| API | Use Case | Example |
|-----|----------|---------|
| `list_configurations` | View available configs | "List all configurations" |
| `activate_configuration` | Switch between configs | "Switch to the steel configuration" |
| `create_configuration` | Create size families | "Create configs for 2-inch, 4-inch, 6-inch sizes" |

**Impact:** HIGH - Configurations are fundamental for design variations

---

### 3. Custom Properties APIs (2 missing)
**Gap:** Can SET properties but cannot LIST or GET them

| API | Use Case | Example |
|-----|----------|---------|
| `list_custom_properties` | View all properties | "List all custom properties" |
| `get_custom_property` | Read specific property | "Get the material property" |

**Impact:** HIGH - Essential for BOM, PLM, and drawing automation

---

### 4. Feature Control APIs (3 missing)
**Gap:** Can suppress components but not individual features

| API | Use Case | Example |
|-----|----------|---------|
| `suppress_feature` | Simplify parts | "Suppress all cosmetic features" |
| `unsuppress_feature` | Restore features | "Unsuppress feature XYZ" |
| `list_suppressed_features` | Check suppression state | "Show all suppressed features" |

**Impact:** HIGH - Critical for simplified versions and performance

---

## 🟡 PRIORITY 2: Useful for Automation (12 APIs)

### 5. Equations/Linking APIs (3 missing)
**Gap:** No parametric equation support

| API | Use Case | Example |
|-----|----------|---------|
| `create_equation` | Parametric design | "Set diameter = length * 2" |
| `set_dimension_value` | Update dimensions | "Change diameter to 4 inches" |
| `set_global_variable` | Global parameters | "Create global variable for wall thickness" |

**Impact:** MEDIUM - Important for parametric automation

---

### 6. Batch Processing APIs (3 missing)
**Gap:** No multi-file operations

| API | Use Case | Example |
|-----|----------|---------|
| `batch_export` | Export multiple files | "Export all parts to STEP" |
| `process_folder` | Folder-level operations | "Process all files in this folder" |
| `batch_apply_material` | Apply to multiple parts | "Apply aluminum to all sheet metal parts" |

**Impact:** MEDIUM - Saves significant time on repetitive tasks

---

### 7. View Control APIs (3 missing)
**Gap:** Limited view manipulation

| API | Use Case | Example |
|-----|----------|---------|
| `capture_screenshot` | Documentation | "Take a screenshot of this view" |
| `set_view_orientation` | Standard views | "Set to front view" |
| `zoom_to_selection` | Focus on selected | "Zoom to this feature" |

**Impact:** MEDIUM - Useful for documentation automation

---

### 8. Selection APIs (3 missing)
**Gap:** Very limited selection capability

| API | Use Case | Example |
|-----|----------|---------|
| `select_edge` | Edge selection | "Select this edge" |
| `select_feature` | Feature selection | "Select the extrude feature" |
| `get_selection` | Query selection | "What's currently selected?" |

**Impact:** MEDIUM - Foundation for interactive operations

---

## 🟢 PRIORITY 3: Advanced Features (6 APIs)

### 9. Reference Geometry APIs (3 missing)
**Gap:** Limited reference geometry creation

| API | Use Case |
|-----|----------|
| `create_reference_plane` | Construction planes (SolidWorks) |
| `create_reference_axis` | Construction axes |
| `create_coordinate_system` | Custom coordinate systems |

**Impact:** LOW - Advanced users only

---

### 10. Validation APIs (3 missing)
**Gap:** Limited design validation

| API | Use Case |
|-----|----------|
| `validate_dimensions` | Check dimension compliance |
| `check_manufacturability` | DFM validation |
| `check_minimum_thickness` | Thickness checks |

**Impact:** LOW - Nice to have for quality checks

---

## 📊 Gap Statistics

| Category | Total Possible | Implemented | Missing | Coverage |
|----------|----------------|-------------|---------|----------|
| Measurement | 8 | 1 | 7 | 12.5% |
| Configuration | 8 | 0 | 8 | 0% ❌ |
| Equations/Linking | 8 | 0 | 8 | 0% ❌ |
| Batch Processing | 7 | 0 | 7 | 0% ❌ |
| Custom Properties | 7 | 1 | 6 | 14.3% |
| Feature Control | 7 | 1 | 6 | 14.3% |
| View Control | 9 | 2 | 7 | 22.2% |
| Selection | 9 | 1 | 8 | 11.1% |
| Reference Geometry | 6 | 1 | 5 | 16.7% |
| Validation | 8 | 2 | 6 | 25.0% |
| **TOTAL** | **77** | **9** | **68** | **11.7%** |

---

## 💡 Recommendations

### Immediate Priority (Next Implementation):
1. **Configuration APIs** (3 APIs) - Zero coverage, high demand
   - `list_configurations`
   - `activate_configuration`
   - `create_configuration`

2. **Measurement APIs** (4 APIs) - Frequently requested
   - `measure_distance`
   - `measure_angle`
   - `get_bounding_box`
   - `check_clearance`

3. **Custom Properties** (2 APIs) - Complete the partial implementation
   - `list_custom_properties`
   - `get_custom_property`

### Implementation Impact:
- Adding **9 APIs** (3 config + 4 measurement + 2 properties) would:
  - Close 75% of Priority 1 gaps
  - Enable powerful new automation scenarios
  - Complement existing 174 endpoints

### Estimated Effort:
- **Configuration APIs:** ~200 lines (similar complexity to feature_reader)
- **Measurement APIs:** ~300 lines (COM calls + calculations)
- **Custom Properties:** ~100 lines (simple wrappers)
- **Total:** ~600 lines for 9 high-impact APIs

---

## 🎯 What Users CANNOT Currently Do

### Common Scenarios That Fail:

❌ **"What's the distance between these two holes?"**
- No measurement API exists

❌ **"Switch to the 6-inch configuration"**
- No configuration management

❌ **"List all custom properties"**
- Can set but not read properties

❌ **"Suppress all cosmetic features"**
- Can only suppress components, not individual features

❌ **"Export all parts in this folder to STEP"**
- No batch processing

❌ **"Set diameter = length * 2"**
- No equation support

---

## ✅ What the Bot CAN Do (174 APIs)

The bot excels at:
- ✅ Creating parts from text (95% coverage)
- ✅ Analyzing assemblies (100% after assembly_component_analyzer)
- ✅ Generating BOMs and drawings
- ✅ Checking interference
- ✅ Estimating costs
- ✅ Standards validation
- ✅ Basic feature analysis

---

## 📈 Coverage Improvement Plan

### Phase 1: Priority 1 (12 APIs) - Target 30 days
- Configuration management (3 APIs)
- Measurement tools (4 APIs)
- Custom properties (2 APIs)
- Feature suppression (3 APIs)

### Phase 2: Priority 2 (12 APIs) - Target 60 days
- Equations/linking (3 APIs)
- Batch processing (3 APIs)
- View control (3 APIs)
- Selection tools (3 APIs)

### Phase 3: Priority 3 (6 APIs) - Target 90 days
- Reference geometry (3 APIs)
- Advanced validation (3 APIs)

---

## 🔗 Related Documents

- [CAD_BOT_LIMITATIONS.md](CAD_BOT_LIMITATIONS.md) - Comprehensive limitations list
- [ASSEMBLY_COMPONENT_ANALYZER_COMPLETE.md](ASSEMBLY_COMPONENT_ANALYZER_COMPLETE.md) - Recent implementation
- [FEATURE_ANALYSIS_COMPLETE.md](FEATURE_ANALYSIS_COMPLETE.md) - Feature reader implementation

---

**Bottom Line:**  
The bot has excellent core CAD capabilities (174 APIs) but is missing **30 high-value helper APIs** that would significantly improve user experience. Focus on **Priority 1** (12 APIs) for maximum impact.

**Most Critical Gap:** Configuration management (0% coverage, high user demand)
