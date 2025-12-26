# Recommended Python Packages for Standards Extraction

## Current Status

**Already Installed:**
- ✅ `pdfplumber` - Table extraction (used in scripts)
- ✅ `pdf2image` - PDF to image conversion
- ✅ `Pillow` - Image processing
- ✅ `pytesseract` - OCR
- ✅ `PyPDF2` - PDF text extraction
- ✅ `pydantic` - Data validation
- ✅ `reportlab` - PDF generation
- ✅ `numpy` - Numerical operations

---

## High Priority Packages (Essential for Visual Validation)

### 1. **Table Extraction & Processing**

| Package | Purpose | Priority | Install |
|---------|---------|----------|---------|
| `tabula-py` | Advanced table extraction from PDFs (Java-based, very accurate) | ⭐⭐⭐ | `pip install tabula-py` |
| `camelot-py` | PDF table extraction with better accuracy than pdfplumber | ⭐⭐⭐ | `pip install camelot-py[cv]` |
| `pandas` | Data manipulation for extracted tables | ⭐⭐⭐ | `pip install pandas` |
| `openpyxl` | Export tables to Excel for review | ⭐⭐ | `pip install openpyxl` |

**Why:**
- `pdfplumber` is good but `tabula-py` and `camelot-py` often extract complex tables more accurately
- `pandas` is essential for cleaning and structuring table data
- `openpyxl` allows exporting to Excel for manual review/validation

---

### 2. **Image Processing & Computer Vision**

| Package | Purpose | Priority | Install |
|---------|---------|----------|---------|
| `opencv-python` | Advanced image processing, table detection, edge detection | ⭐⭐⭐ | `pip install opencv-python` |
| `scikit-image` | Image processing algorithms, feature detection | ⭐⭐ | `pip install scikit-image` |
| `matplotlib` | Visualization, comparison plots, validation charts | ⭐⭐⭐ | `pip install matplotlib` |
| `seaborn` | Statistical visualizations for validation reports | ⭐⭐ | `pip install seaborn` |

**Why:**
- `opencv-python` can detect table boundaries automatically
- Useful for creating visual comparison reports
- Can identify regions of interest on pages

---

### 3. **Advanced OCR & Text Extraction**

| Package | Purpose | Priority | Install |
|---------|---------|----------|---------|
| `easyocr` | Alternative OCR engine (better for scanned documents) | ⭐⭐ | `pip install easyocr` |
| `pdfminer.six` | Low-level PDF parsing, better text positioning | ⭐⭐ | `pip install pdfminer.six` |
| `unstructured` | Intelligent document parsing (tables, text, metadata) | ⭐⭐⭐ | `pip install unstructured[pdf]` |

**Why:**
- `easyocr` handles scanned PDFs better than pytesseract
- `pdfminer.six` provides better text positioning for validation
- `unstructured` is excellent for intelligent document parsing

---

### 4. **Data Validation & Schema**

| Package | Purpose | Priority | Install |
|---------|---------|----------|---------|
| `jsonschema` | JSON schema validation for extracted data | ⭐⭐⭐ | `pip install jsonschema` |
| `cerberus` | Data validation library (alternative to pydantic) | ⭐⭐ | `pip install cerberus` |
| `marshmallow` | Schema validation and serialization | ⭐⭐ | `pip install marshmallow` |

**Why:**
- Validate extracted JSON data against schemas
- Ensure data quality before integration
- `pydantic` is already installed, but `jsonschema` is useful for JSON file validation

---

### 5. **Visualization & Reporting**

| Package | Purpose | Priority | Install |
|---------|---------|----------|---------|
| `weasyprint` | HTML to PDF for validation reports | ⭐⭐ | `pip install weasyprint` |
| `plotly` | Interactive visualizations for validation dashboards | ⭐⭐ | `pip install plotly` |
| `jinja2` | Template engine for generating reports | ⭐⭐ | `pip install jinja2` |

**Why:**
- Create professional validation reports
- Interactive dashboards for reviewing extraction quality
- Template-based report generation

---

### 6. **PDF Processing (Advanced)**

| Package | Purpose | Priority | Install |
|---------|---------|----------|---------|
| `pymupdf` (fitz) | Fast PDF rendering and text extraction | ⭐⭐⭐ | `pip install pymupdf` |
| `pdfquery` | PDF scraping with XPath-like queries | ⭐⭐ | `pip install pdfquery` |
| `pdfrw` | PDF reading/writing with form support | ⭐ | `pip install pdfrw` |

**Why:**
- `pymupdf` is faster than pdf2image for rendering
- Better for extracting text with positioning
- Useful for complex PDF structures

---

## Medium Priority Packages (Nice to Have)

### 7. **Machine Learning / AI (Optional)**

| Package | Purpose | Priority | Install |
|---------|---------|----------|---------|
| `transformers` | NLP models for intelligent text extraction | ⭐ | `pip install transformers` |
| `torch` | PyTorch (if using ML models) | ⭐ | `pip install torch` |
| `layoutparser` | Document layout analysis with ML | ⭐ | `pip install layoutparser` |

**Why:**
- Could use ML models to identify document sections
- Intelligent table detection
- Only needed if you want AI-powered extraction

---

### 8. **Utilities**

| Package | Purpose | Priority | Install |
|---------|---------|----------|---------|
| `tqdm` | Progress bars for long-running extractions | ⭐⭐ | `pip install tqdm` |
| `rich` | Beautiful terminal output and progress | ⭐⭐ | `pip install rich` |
| `click` | Better CLI for extraction scripts | ⭐ | `pip install click` |
| `python-multipart` | File upload handling | ⭐ | `pip install python-multipart` |

**Why:**
- Better user experience during extraction
- Progress tracking for 1,733 pages
- Professional CLI interfaces

---

## Installation Commands

### Essential Packages (High Priority)
```bash
pip install tabula-py camelot-py[cv] pandas openpyxl opencv-python matplotlib jsonschema pymupdf unstructured[pdf] tqdm rich
```

### Full Installation (All Recommended)
```bash
pip install \
  tabula-py \
  camelot-py[cv] \
  pandas \
  openpyxl \
  opencv-python \
  scikit-image \
  matplotlib \
  seaborn \
  easyocr \
  pdfminer.six \
  unstructured[pdf] \
  jsonschema \
  weasyprint \
  plotly \
  jinja2 \
  pymupdf \
  tqdm \
  rich \
  click
```

### Optional (ML/AI)
```bash
pip install transformers torch layoutparser
```

---

## Package-Specific Notes

### tabula-py
- **Requires Java**: Install Java JDK first
- **Best for**: Complex tables with merged cells
- **Usage**: `import tabula; tables = tabula.read_pdf("file.pdf", pages="all")`

### camelot-py
- **Requires Ghostscript**: Install Ghostscript separately
- **Best for**: Tables with clear borders
- **Usage**: `import camelot; tables = camelot.read_pdf("file.pdf")`

### opencv-python
- **Large package**: ~100MB download
- **Best for**: Image processing, table detection, edge detection
- **Usage**: `import cv2; img = cv2.imread("page.png")`

### unstructured
- **Best for**: Intelligent document parsing
- **Handles**: Tables, text, metadata automatically
- **Usage**: `from unstructured.partition.pdf import partition_pdf; elements = partition_pdf("file.pdf")`

### pymupdf (fitz)
- **Very fast**: Faster than pdf2image
- **Best for**: Rendering PDFs to images quickly
- **Usage**: `import fitz; doc = fitz.open("file.pdf"); page = doc[0]; pix = page.get_pixmap()`

---

## Recommended Installation Order

1. **Phase 1 (Immediate)**: Essential for visual validation
   ```bash
   pip install tabula-py pandas opencv-python matplotlib jsonschema tqdm rich
   ```

2. **Phase 2 (Table Extraction)**: Better table extraction
   ```bash
   pip install camelot-py[cv] openpyxl
   ```

3. **Phase 3 (Advanced)**: Enhanced capabilities
   ```bash
   pip install unstructured[pdf] pymupdf easyocr scikit-image
   ```

4. **Phase 4 (Reporting)**: Professional reports
   ```bash
   pip install weasyprint plotly jinja2 seaborn
   ```

---

## System Dependencies

Some packages require system-level dependencies:

### Windows
- **Java JDK** (for tabula-py): Download from Oracle or use OpenJDK
- **Ghostscript** (for camelot-py): Download installer from ghostscript.com
- **Tesseract OCR** (for pytesseract): Already mentioned in project docs

### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt-get install default-jdk ghostscript tesseract-ocr

# macOS
brew install openjdk ghostscript tesseract
```

---

## Testing Recommendations

After installation, test each package:

```python
# Test tabula-py
import tabula
tables = tabula.read_pdf("test.pdf", pages=1)
print(f"Extracted {len(tables)} tables")

# Test camelot-py
import camelot
tables = camelot.read_pdf("test.pdf")
print(f"Extracted {len(tables)} tables")

# Test opencv
import cv2
img = cv2.imread("test.png")
print(f"Image shape: {img.shape}")

# Test unstructured
from unstructured.partition.pdf import partition_pdf
elements = partition_pdf("test.pdf")
print(f"Extracted {len(elements)} elements")
```

---

## Cost/Benefit Analysis

| Package | Install Complexity | Performance Gain | Priority |
|---------|-------------------|------------------|----------|
| `tabula-py` | Medium (needs Java) | High (better tables) | ⭐⭐⭐ |
| `camelot-py` | Medium (needs Ghostscript) | High (better tables) | ⭐⭐⭐ |
| `pandas` | Low | High (data processing) | ⭐⭐⭐ |
| `opencv-python` | Low | Medium (image processing) | ⭐⭐⭐ |
| `unstructured` | Low | High (intelligent parsing) | ⭐⭐⭐ |
| `pymupdf` | Low | High (faster rendering) | ⭐⭐⭐ |
| `easyocr` | Low | Medium (better OCR) | ⭐⭐ |
| `matplotlib` | Low | Medium (visualization) | ⭐⭐⭐ |

---

**Last Updated**: December 25, 2025  
**For**: Standards Books Visual Validation Extraction

---

## Full Scope Document

For complete scope including:
- Data storage & persistence
- Performance & scalability
- Integration with existing systems
- Workflow automation
- Testing & QA

See: `docs/STANDARDS_EXTRACTION_FULL_SCOPE.md`

