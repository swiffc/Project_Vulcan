# Vision Analysis Tools Research for CAD Screenshot Feature

## 📋 Executive Summary

Based on research of existing codebase and industry best practices, here are **15+ additional tools** that can enhance the vision-based CAD analysis feature.

---

## ✅ Currently Available Tools

1. ✅ **Full Screen Screenshot** - `/screen/screenshot`
2. ✅ **Region Screenshot** - `/screen/region`
3. ✅ **OCR on Region** - `/screen/ocr`
4. ✅ **Image Template Matching** - `/screen/find`
5. ✅ **Window Management** - `/window/*` (find, focus, resize)
6. ✅ **Vision Analysis** - Claude Vision API integration (just added)

---

## 🔴 HIGH PRIORITY - Add These First

### 1. **Window-Specific Screenshot** 🔴
**Tool**: `sw_screenshot_window`
**Endpoint**: `/screen/window/{window_title}`
**Description**: Capture only the SolidWorks window (not full screen)
**Use Case**: Cleaner screenshots without desktop clutter
**Implementation**:
```python
@router.post("/window/{window_title}")
async def screenshot_window(window_title: str):
    """Capture screenshot of specific window."""
    hwnd = find_window_by_title(window_title)
    if not hwnd:
        raise HTTPException(404, "Window not found")
    
    rect = win32gui.GetWindowRect(hwnd)
    return await screenshot_region(RegionRequest(
        x=rect[0], y=rect[1],
        width=rect[2]-rect[0],
        height=rect[3]-rect[1]
    ))
```

### 2. **Viewport-Only Screenshot** 🔴
**Tool**: `sw_screenshot_viewport`
**Description**: Capture only the 3D viewport area (exclude toolbars, feature tree)
**Use Case**: Focused analysis of geometry only
**Implementation**: Use window coordinates + known SolidWorks UI layout

### 3. **Multi-View Capture** 🔴
**Tool**: `sw_screenshot_views`
**Description**: Capture multiple standard views (Front, Top, Right, Isometric) in one call
**Use Case**: Comprehensive part analysis from all angles
**Returns**: Array of 4 screenshots with view labels

### 4. **Drawing-Specific OCR** 🔴
**Tool**: `sw_ocr_drawing`
**Description**: OCR optimized for engineering drawings (title block, dimensions, notes)
**Use Case**: Extract part numbers, revisions, dimensions from drawing screenshots
**Enhancement**: Use existing `DimensionExtractor` class on screenshot

### 5. **Dimension Extraction from Screenshot** 🔴
**Tool**: `sw_extract_dimensions_screenshot`
**Description**: Extract dimensions visible in screenshot using OCR + pattern matching
**Use Case**: "What dimensions are shown?" queries
**Implementation**: Combine `/screen/ocr` with `DimensionExtractor` class

---

## 🟡 MEDIUM PRIORITY - High Value Additions

### 6. **Feature Tree Screenshot** 🟡
**Tool**: `sw_screenshot_feature_tree`
**Description**: Capture the feature tree panel
**Use Case**: Analyze part structure, feature sequence
**Vision Analysis**: "List all features in order"

### 7. **Property Manager Screenshot** 🟡
**Tool**: `sw_screenshot_property_manager`
**Description**: Capture the property manager panel
**Use Case**: Extract current feature parameters, dimensions
**Vision Analysis**: "What are the current extrude settings?"

### 8. **GD&T Symbol Detection** 🟡
**Tool**: `sw_detect_gdt_symbols`
**Description**: Detect and identify GD&T symbols in drawing screenshots
**Use Case**: Compliance checking, symbol recognition
**Implementation**: Pattern matching + vision analysis for symbols (⏥ ⊥ ∥ ⊕ ○ ⌭ ⌓ ↗)

### 9. **Annotation Detection** 🟡
**Tool**: `sw_detect_annotations`
**Description**: Detect and extract all annotations (notes, balloons, dimensions)
**Use Case**: Drawing completeness check
**Vision Analysis**: "How many annotations are visible?"

### 10. **BOM Extraction from Drawing** 🟡
**Tool**: `sw_extract_bom_screenshot`
**Description**: Extract BOM table from drawing screenshot
**Use Case**: Quick BOM review without opening file
**Implementation**: OCR + table parsing

### 11. **Before/After Comparison** 🟡
**Tool**: `sw_compare_screenshots`
**Description**: Compare two screenshots and highlight differences
**Use Case**: Verify changes, track modifications
**Implementation**: Use existing `VisualVerifier` class

---

## 🟢 NICE TO HAVE - Advanced Features

### 12. **Feature Recognition** 🟢
**Tool**: `sw_recognize_features`
**Description**: Identify CAD features from screenshot (extrude, fillet, hole, etc.)
**Use Case**: "What type of feature is this?"
**Vision Analysis**: Train on feature patterns

### 13. **Material Detection** 🟢
**Tool**: `sw_detect_material`
**Description**: Detect material from appearance/color in viewport
**Use Case**: Quick material identification
**Note**: Less reliable, but useful for common materials

### 14. **Assembly Component Count** 🟢
**Tool**: `sw_count_components_screenshot`
**Description**: Count visible components in assembly screenshot
**Use Case**: Quick assembly complexity check
**Vision Analysis**: "How many parts are visible?"

### 15. **Drawing Sheet Analysis** 🟢
**Tool**: `sw_analyze_drawing_sheet`
**Description**: Analyze entire drawing sheet (views, title block, BOM, notes)
**Use Case**: Comprehensive drawing review
**Returns**: Structured analysis of all drawing elements

### 16. **View Orientation Detection** 🟢
**Tool**: `sw_detect_view_orientation`
**Description**: Detect current view orientation (Front, Top, Isometric, etc.)
**Use Case**: Context-aware analysis
**Vision Analysis**: "What view is this?"

### 17. **Sketch Recognition** 🟢
**Tool**: `sw_recognize_sketch`
**Description**: Identify sketch elements (lines, arcs, circles) from screenshot
**Use Case**: Sketch analysis and validation
**Vision Analysis**: "What geometry is in this sketch?"

---

## 🔧 Implementation Recommendations

### Phase 1: Quick Wins (1-2 days)
1. Window-specific screenshot
2. Viewport-only screenshot
3. Drawing-specific OCR enhancement

### Phase 2: High Value (3-5 days)
4. Multi-view capture
5. Dimension extraction from screenshot
6. Feature tree screenshot
7. Property manager screenshot

### Phase 3: Advanced (1-2 weeks)
8. GD&T symbol detection
9. Annotation detection
10. BOM extraction
11. Before/after comparison

### Phase 4: Experimental (2+ weeks)
12-17. Advanced recognition features

---

## 📚 Existing Code to Leverage

1. **Window Controller** (`desktop_server/controllers/window.py`)
   - Already has window finding logic
   - Can extend for window-specific screenshots

2. **Dimension Extractor** (`agents/cad_agent/adapters/dimension_extractor.py`)
   - Already extracts dimensions from images
   - Can be used on screenshots

3. **Drawing Analyzer** (`agents/cad_agent/adapters/drawing_analyzer.py`)
   - OCR and text extraction
   - Can be adapted for screenshots

4. **Visual Verifier** (`desktop_server/controllers/verifier.py`)
   - Image comparison logic
   - Can be used for before/after

5. **Screen Controller** (`desktop_server/controllers/screen.py`)
   - Base screenshot functionality
   - OCR capabilities

---

## 🎯 Integration with Vision Analysis

All new tools should:
1. **Capture screenshot** using existing screen controller
2. **Send to Claude Vision API** for analysis
3. **Combine with OCR** for text extraction
4. **Return structured data** for chatbot context

**Example Flow**:
```
User: "What dimensions are visible?"
→ sw_extract_dimensions_screenshot()
→ Capture viewport
→ OCR + Vision Analysis
→ Extract dimensions
→ Return: [{value: 50, unit: "mm", location: "top view"}, ...]
```

---

## 📊 Priority Matrix

| Tool | Impact | Effort | Priority |
|------|--------|--------|----------|
| Window Screenshot | High | Low | 🔴 P0 |
| Viewport Screenshot | High | Low | 🔴 P0 |
| Multi-View Capture | High | Medium | 🔴 P1 |
| Drawing OCR | High | Medium | 🔴 P1 |
| Dimension Extraction | High | Medium | 🟡 P2 |
| Feature Tree | Medium | Low | 🟡 P2 |
| GD&T Detection | Medium | High | 🟡 P3 |
| Annotation Detection | Medium | Medium | 🟡 P3 |
| BOM Extraction | Medium | Medium | 🟢 P4 |
| Feature Recognition | Low | High | 🟢 P5 |

---

## 🚀 Next Steps

1. **Implement P0 tools** (Window & Viewport screenshots)
2. **Add to CAD tools** (`apps/web/src/lib/cad-tools.ts`)
3. **Update CAD chat route** to use new tools
4. **Test with real SolidWorks screenshots**
5. **Iterate based on user feedback**

---

## 📝 Notes

- All tools should handle errors gracefully (window not found, OCR fails, etc.)
- Consider caching screenshots to avoid redundant captures
- Vision API calls are expensive - batch when possible
- OCR accuracy depends on screenshot quality - ensure high DPI captures

