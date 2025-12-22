# PRD-018: CAD Chatbot Integration & Validation UI

**Status**: Draft  
**Phase**: 18  
**Priority**: High  
**Depends On**: Phase 17 (Advanced Validators)  
**Date**: December 22, 2025  

---

## 1. Overview

Integrate the complete validator suite (Phase 17) into the CAD chatbot interface, enabling users to validate drawings and designs through natural language commands with real-time feedback.

---

## 2. Goals

### Primary Goals
- ✅ Natural language validation commands ("Check this drawing for GD&T errors")
- ✅ Real-time validation feedback with inline results
- ✅ Visual proof (screenshots + annotated PDFs)
- ✅ Validation report generation
- ✅ Integration with existing CAD dashboard

### Secondary Goals
- ⚠️ Batch validation (multiple drawings)
- ⚠️ Validation history tracking
- ⚠️ Custom checklist templates
- ⚠️ PDF annotation with red flags

---

## 3. User Stories

### As a Design Engineer:
- **Story 1**: "I want to ask 'Check drawing 12345 for welding compliance' and get an AWS D1.1 validation report in < 10 seconds"
- **Story 2**: "I want to upload a PDF drawing and see GD&T errors highlighted inline"
- **Story 3**: "I want to run a complete 130-point ACHE validation and export the report"

### As a Quality Inspector:
- **Story 4**: "I want to validate 10 drawings against our standards checklist before releasing to fabrication"
- **Story 5**: "I want to see which drawings have critical failures vs warnings"

### As a Project Manager:
- **Story 6**: "I want a dashboard showing validation pass rates across all active projects"

---

## 4. Technical Architecture

### 4.1 Chatbot Commands

```typescript
// Natural language → structured validation
interface ValidationRequest {
  type: "drawing" | "assembly" | "ache" | "custom";
  file?: File;
  fileId?: string;  // From Flatter Files
  checks: string[]; // ["gdt", "welding", "material", "ache_complete"]
  severity?: "critical" | "all";
}

interface ValidationResponse {
  requestId: string;
  status: "queued" | "running" | "complete" | "error";
  results?: ValidationReport;
  duration_ms: number;
  screenshot?: string;  // Base64 annotated image
  pdf?: string;         // Download URL
}
```

### 4.2 Backend Integration

```python
# agents/cad_agent/validators/orchestrator.py

class ValidationOrchestrator:
    """Orchestrates all validation checks."""
    
    def __init__(self):
        self.gdt_parser = GDTParser()
        self.welding_validator = WeldingValidator()
        self.material_validator = MaterialValidator()
        self.ache_validator = ACHEValidator()
        self.drawing_analyzer = DrawingAnalyzer()
    
    async def validate_drawing(
        self,
        file_path: str,
        checks: list[str] = ["all"]
    ) -> ValidationReport:
        """Run all requested validation checks."""
        # Extract drawing content
        analysis = self.drawing_analyzer.analyze_pdf(file_path)
        
        results = {}
        
        if "gdt" in checks or "all" in checks:
            results["gdt"] = self.gdt_parser.parse_drawing_text(
                analysis.extracted_text
            )
        
        if "welding" in checks or "all" in checks:
            results["welding"] = self.welding_validator.validate_drawing(
                analysis.weld_callouts
            )
        
        if "material" in checks or "all" in checks:
            results["material"] = self.material_validator.validate_drawing(
                analysis.material_callouts
            )
        
        return ValidationReport(**results)
```

### 4.3 Frontend Integration

```typescript
// apps/web/src/lib/cad/validation-client.ts

export async function validateDrawing(
  request: ValidationRequest
): Promise<ValidationResponse> {
  const formData = new FormData();
  
  if (request.file) {
    formData.append("file", request.file);
  } else if (request.fileId) {
    formData.append("fileId", request.fileId);
  }
  
  formData.append("checks", JSON.stringify(request.checks));
  formData.append("type", request.type);
  
  const response = await fetch("/api/cad/validate", {
    method: "POST",
    body: formData,
  });
  
  return response.json();
}
```

### 4.4 Dashboard Widget

```typescript
// apps/web/src/components/cad/dashboard/ValidationWidget.tsx

export function ValidationWidget() {
  const [recentValidations, setRecentValidations] = useState([]);
  
  return (
    <Card>
      <CardHeader 
        title="Recent Validations"
        icon={<CheckCircle />}
      />
      <CardContent>
        {recentValidations.map((validation) => (
          <ValidationItem 
            key={validation.id}
            validation={validation}
            onClick={() => viewReport(validation.id)}
          />
        ))}
      </CardContent>
    </Card>
  );
}
```

---

## 5. API Endpoints

### 5.1 Desktop Server (Python)

```
POST /cad/validate/drawing
  - Upload PDF/DXF drawing
  - Returns validation report

POST /cad/validate/ache
  - Full 130-point ACHE validation
  - Returns comprehensive report

GET /cad/validate/history
  - Get validation history
  - Filter by project/date/status

GET /cad/validate/report/{id}
  - Get detailed report
  - Download PDF with annotations
```

### 5.2 Next.js API Routes

```
POST /api/cad/validate
  - Proxy to desktop server
  - Handle file uploads
  - Stream progress updates

GET /api/cad/validations
  - List user's validations
  - Paginated results

GET /api/cad/validations/[id]
  - Get single validation
  - Include full results
```

---

## 6. UI/UX Flow

### 6.1 Chatbot Validation Flow

```
User: "Check drawing ABC-123 for GD&T errors"
  ↓
Bot: "📊 Analyzing drawing ABC-123..."
  ↓
Bot: [Progress: Extracting text... 30%]
  ↓
Bot: [Progress: Parsing GD&T symbols... 60%]
  ↓
Bot: [Progress: Validating tolerances... 90%]
  ↓
Bot: "✅ Validation Complete!"

     📋 GD&T Analysis Report
     ━━━━━━━━━━━━━━━━━━━━━━
     Total Checks:     28
     Passed:          25 (89%)
     Warnings:         2
     Errors:           1
     
     ❌ Critical Issues:
     • Feature control frame missing datum C reference
     
     ⚠️  Warnings:
     • Position tolerance may be too tight for manufacturing
     • Datum A flatness not specified
     
     [View Full Report] [Download PDF]
```

### 6.2 Validation Dashboard

```
┌─────────────────────────────────────────────────┐
│  Validation Dashboard                           │
├─────────────────────────────────────────────────┤
│                                                 │
│  📊 This Week                                   │
│  ┌──────────────────────────────────────┐      │
│  │  Total Validations:     47           │      │
│  │  Pass Rate:            91.5%         │      │
│  │  Critical Failures:      4           │      │
│  └──────────────────────────────────────┘      │
│                                                 │
│  Recent Validations                             │
│  ┌──────────────────────────────────────┐      │
│  │ ✅ Drawing-456  GD&T    100%  2m ago │      │
│  │ ⚠️  Assy-789   ACHE     85%   1h ago │      │
│  │ ❌ Part-123    Welding   67%   3h ago │      │
│  └──────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
```

---

## 7. Data Models

### 7.1 Validation Request

```python
class ValidationRequest(BaseModel):
    """User validation request."""
    type: Literal["drawing", "assembly", "ache", "custom"]
    file_path: Optional[str] = None
    file_id: Optional[str] = None  # Flatter Files ID
    checks: List[str] = ["all"]
    severity: Literal["critical", "all"] = "all"
    user_id: str
    project_id: Optional[str] = None
```

### 7.2 Validation Report

```python
class ValidationReport(BaseModel):
    """Complete validation results."""
    id: str
    request_id: str
    timestamp: datetime
    duration_ms: int
    
    # Results by check type
    gdt_results: Optional[GDTValidationResult] = None
    welding_results: Optional[WeldValidationResult] = None
    material_results: Optional[MaterialValidationResult] = None
    ache_results: Optional[ACHEValidationReport] = None
    
    # Summary
    total_checks: int
    passed: int
    warnings: int
    errors: int
    pass_rate: float
    
    # Files
    input_file: str
    annotated_pdf: Optional[str] = None
    report_pdf: Optional[str] = None
```

---

## 8. Implementation Plan

### Phase 18.1: Backend Integration (Week 1)
- [x] Create `ValidationOrchestrator` class
- [ ] Add Desktop Server validation endpoints
- [ ] Integrate with existing validators
- [ ] Add PDF annotation capabilities
- [ ] Create validation report generator

### Phase 18.2: API Layer (Week 1)
- [ ] Create Next.js `/api/cad/validate` route
- [ ] Add file upload handling
- [ ] Implement progress streaming (SSE)
- [ ] Add validation history storage

### Phase 18.3: Chatbot Integration (Week 2)
- [ ] Parse validation commands from natural language
- [ ] Add validation intent recognition
- [ ] Stream validation progress to chat
- [ ] Format results with markdown tables

### Phase 18.4: Dashboard Widgets (Week 2)
- [ ] Create `ValidationWidget` component
- [ ] Add validation history list
- [ ] Create validation detail modal
- [ ] Add pass rate charts

### Phase 18.5: Testing & Polish (Week 3)
- [ ] E2E validation flow tests
- [ ] Load testing (100 concurrent validations)
- [ ] Error handling & edge cases
- [ ] Documentation & examples

---

## 9. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Validation Time | < 10 sec | P95 latency |
| Accuracy | > 95% | vs manual review |
| User Satisfaction | > 4.5/5 | Survey rating |
| Daily Usage | > 50 validations | Analytics |
| Error Rate | < 2% | Failed validations |

---

## 10. Risks & Mitigations

### Risk 1: Slow PDF Processing
- **Mitigation**: Cache extracted text, use GPU for OCR
- **Fallback**: Queue system for batch validations

### Risk 2: False Positives
- **Mitigation**: Tunable confidence thresholds
- **Fallback**: Manual review override

### Risk 3: Large File Uploads
- **Mitigation**: 10MB file size limit, chunked uploads
- **Fallback**: Direct file path for local files

---

## 11. Future Enhancements (Phase 19+)

- **AI-Suggested Fixes**: "This GD&T error can be fixed by adding datum C"
- **Real-Time Validation**: Validate as you draw (SolidWorks plugin)
- **Custom Checklists**: Company-specific validation rules
- **Collaboration**: Multi-user review workflows
- **Mobile App**: Validate from phone/tablet

---

## 12. Dependencies

### External
- ✅ pytesseract (OCR) - Already installed
- ✅ pdf2image (PDF processing) - Already installed
- ✅ Pillow (Image manipulation) - Already installed
- ⚠️ reportlab (PDF generation) - Need to add

### Internal
- ✅ Phase 17 validators (gdt_parser, welding_validator, etc.)
- ✅ standards_db_v2 (offline lookups)
- ✅ drawing_analyzer (PDF extraction)
- ⚠️ PDF annotator (need to create)

---

## 13. Acceptance Criteria

- ✅ User can validate drawing via chat: "Check drawing X for GD&T errors"
- ✅ Validation completes in < 10 seconds for typical drawing
- ✅ Results show pass/warning/error breakdown
- ✅ Validation report is downloadable as PDF
- ✅ Dashboard shows recent validations with pass rates
- ✅ All Phase 17 validators are accessible via chat
- ✅ Progress is streamed to user in real-time
- ✅ Annotated PDF highlights errors on drawing

---

**Ready to Implement**: December 22, 2025  
**Target Completion**: January 12, 2026 (3 weeks)
