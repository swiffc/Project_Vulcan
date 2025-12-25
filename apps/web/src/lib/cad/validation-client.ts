/**
 * CAD Validation Client Library
 * 
 * Client-side functions for validating drawings.
 */

export interface ValidationRequest {
  type: "drawing" | "assembly" | "ache" | "custom";
  file?: File;
  fileId?: string;
  checks?: string[];
  severity?: "critical" | "all";
  userId?: string;
  projectId?: string;
}

export interface ValidationIssue {
  severity: "critical" | "error" | "warning" | "info";
  checkType: string;
  message: string;
  location?: string;
  suggestion?: string;
  standardReference?: string;
}

export interface GDTValidationResult {
  totalFeatures: number;
  validFeatures: number;
  invalidFeatures: number;
  issues: ValidationIssue[];
  datumsFound: string[];
  tolerancesParsed: number;
}

export interface WeldValidationResult {
  totalWelds: number;
  compliantWelds: number;
  nonCompliantWelds: number;
  issues: ValidationIssue[];
  awsD11Compliant: boolean;
  weldSymbolsFound: string[];
}

export interface MaterialValidationResult {
  materialsValidated: number;
  mtrsFound: number;
  compliantMaterials: number;
  issues: ValidationIssue[];
  astmSpecsChecked: string[];
  carbonEquivalentOk: boolean;
}

export interface ACHEValidationResult {
  totalChecks: number;
  passed: number;
  warnings: number;
  errors: number;
  criticalFailures: number;
  issues: ValidationIssue[];
  categoryScores: Record<string, number>;
}

export interface ValidationReport {
  id: string;
  requestId: string;
  timestamp: string;
  durationMs: number;
  status: "queued" | "running" | "complete" | "error";

  // Results by type
  gdtResults?: GDTValidationResult;
  weldingResults?: WeldValidationResult;
  materialResults?: MaterialValidationResult;
  acheResults?: ACHEValidationResult;

  // Phase 25 - Drawing Checker results
  phase25Results?: Phase25Results;

  // Summary
  totalChecks: number;
  passed: number;
  warnings: number;
  errors: number;
  criticalFailures: number;
  passRate: number;

  // All issues
  allIssues: ValidationIssue[];

  // Files
  inputFile: string;
  annotatedPdf?: string;
  reportPdf?: string;

  // Metadata
  metadata: Record<string, any>;
}

export interface ValidationResponse {
  requestId: string;
  status: string;
  report?: ValidationReport;
  durationMs: number;
  message: string;
}

export interface ValidationStatus {
  available: boolean;
  validators?: {
    gdtParser: boolean;
    weldingValidator: boolean;
    materialValidator: boolean;
    acheValidator: boolean;
    drawingParser: boolean;
    // Phase 25 validators
    aiscHoleValidator: boolean;
    structuralValidator: boolean;
    shaftValidator: boolean;
    handlingValidator: boolean;
    bomValidator: boolean;
    dimensionValidator: boolean;
    oshaValidator: boolean;
  };
  message: string;
  error?: string;
}

// Phase 25 - Drawing Checker types
export interface Phase25Results {
  holes?: HoleValidationResult;
  structural?: StructuralValidationResult;
  shaft?: ShaftValidationResult;
  handling?: HandlingValidationResult;
  bom?: BOMValidationResult;
  dimensions?: DimensionValidationResult;
  osha?: OSHAValidationResult;
}

export interface HoleValidationResult {
  totalChecks: number;
  passed: number;
  failed: number;
  warnings: number;
  criticalFailures: number;
  issues: ValidationIssue[];
}

export interface StructuralValidationResult {
  checks: any[];
  boltCapacityKips?: number;
  weldCapacityKips?: number;
  bearingCapacityKips?: number;
}

export interface ShaftValidationResult {
  checks: any[];
  missingCallouts: string[];
}

export interface HandlingValidationResult {
  totalChecks: number;
  passed: number;
  failed: number;
  warnings: number;
  criticalFailures: number;
  issues: ValidationIssue[];
  statistics: {
    weightLbs: number;
    requiresLiftingLugs: boolean;
    requiresCg: boolean;
    shippableStandard: boolean;
  };
}

export interface BOMValidationResult {
  totalChecks: number;
  passed: number;
  failed: number;
  warnings: number;
  issues: ValidationIssue[];
}

export interface DimensionValidationResult {
  totalChecks: number;
  passed: number;
  failed: number;
  warnings: number;
  issues: ValidationIssue[];
}

export interface OSHAValidationResult {
  totalChecks: number;
  passed: number;
  failed: number;
  warnings: number;
  issues: ValidationIssue[];
}

/**
 * Validate a CAD drawing
 */
export async function validateDrawing(
  request: ValidationRequest
): Promise<ValidationResponse> {
  const formData = new FormData();
  
  if (request.file) {
    formData.append("file", request.file);
  } else if (request.fileId) {
    formData.append("fileId", request.fileId);
  } else {
    throw new Error("Either file or fileId must be provided");
  }
  
  formData.append("checks", JSON.stringify(request.checks || ["all"]));
  formData.append("severity", request.severity || "all");
  formData.append("userId", request.userId || "anonymous");
  formData.append("type", request.type || "drawing");
  
  if (request.projectId) {
    formData.append("projectId", request.projectId);
  }
  
  const response = await fetch("/api/cad/validate", {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Validation failed");
  }
  
  return response.json();
}

/**
 * Run ACHE 130-point validation
 */
export async function validateACHE(
  file: File,
  userId?: string,
  projectId?: string
): Promise<ValidationResponse> {
  return validateDrawing({
    type: "ache",
    file,
    userId,
    projectId,
    checks: ["ache"],
  });
}

/**
 * Get validation system status
 */
export async function getValidationStatus(): Promise<ValidationStatus> {
  const response = await fetch("/api/cad/validate");
  
  if (!response.ok) {
    return {
      available: false,
      message: "Validation system unavailable",
      error: response.statusText,
    };
  }
  
  return response.json();
}

/**
 * Format validation report as markdown
 */
export function formatValidationReport(report: ValidationReport): string {
  const lines: string[] = [];
  
  lines.push("# Validation Report");
  lines.push("");
  lines.push(`**Status:** ${report.status}`);
  lines.push(`**Duration:** ${report.durationMs}ms`);
  lines.push(`**Pass Rate:** ${report.passRate.toFixed(1)}%`);
  lines.push("");
  
  lines.push("## Summary");
  lines.push("");
  lines.push(`- Total Checks: ${report.totalChecks}`);
  lines.push(`- Passed: ${report.passed} (${((report.passed / report.totalChecks) * 100).toFixed(1)}%)`);
  lines.push(`- Warnings: ${report.warnings}`);
  lines.push(`- Errors: ${report.errors}`);
  lines.push(`- Critical Failures: ${report.criticalFailures}`);
  lines.push("");
  
  if (report.criticalFailures > 0) {
    lines.push("## ❌ Critical Issues");
    lines.push("");
    
    const critical = report.allIssues.filter(i => i.severity === "critical");
    for (const issue of critical) {
      lines.push(`- **${issue.checkType}**: ${issue.message}`);
      if (issue.location) {
        lines.push(`  - Location: ${issue.location}`);
      }
      if (issue.suggestion) {
        lines.push(`  - Suggestion: ${issue.suggestion}`);
      }
    }
    lines.push("");
  }
  
  if (report.errors > 0) {
    lines.push("## ⚠️ Errors");
    lines.push("");
    
    const errors = report.allIssues.filter(i => i.severity === "error");
    for (const issue of errors) {
      lines.push(`- **${issue.checkType}**: ${issue.message}`);
    }
    lines.push("");
  }
  
  if (report.warnings > 0) {
    lines.push("## ⚠️ Warnings");
    lines.push("");
    
    const warnings = report.allIssues.filter(i => i.severity === "warning");
    for (const issue of warnings.slice(0, 10)) {  // Limit to 10
      lines.push(`- ${issue.message}`);
    }
    
    if (warnings.length > 10) {
      lines.push(`- ... and ${warnings.length - 10} more`);
    }
    lines.push("");
  }
  
  return lines.join("\n");
}

// ============================================================================
// Phase 25 - Drawing Checker API Functions
// ============================================================================

const DESKTOP_SERVER_URL = process.env.NEXT_PUBLIC_DESKTOP_SERVER_URL || "http://localhost:8765";

/**
 * Check hole edge distances and spacing (AISC)
 */
export async function checkHoles(holes: {
  diameter: number;
  edgeDistance?: number;
  spacing?: number;
  boltDiameter?: number;
  partId?: string;
}[]): Promise<HoleValidationResult> {
  const response = await fetch(`${DESKTOP_SERVER_URL}/phase25/check-holes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ holes }),
  });

  if (!response.ok) {
    throw new Error(`Hole check failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check structural capacity (bolts, welds)
 */
export async function checkStructural(data: {
  checkType: "bolt_shear" | "bolt_bearing" | "fillet_weld" | "net_section";
  bolt?: {
    diameter: number;
    grade?: string;
    threadsExcluded?: boolean;
    numBolts?: number;
    numShearPlanes?: number;
  };
  weld?: {
    legSize: number;
    length: number;
  };
  appliedLoadKips?: number;
  materialThickness?: number;
  materialGrade?: string;
}): Promise<StructuralValidationResult> {
  const response = await fetch(`${DESKTOP_SERVER_URL}/phase25/check-structural`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Structural check failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check shaft/machining requirements
 */
export async function checkShaft(data: {
  checkType: "shaft" | "keyway" | "retaining_ring" | "chamfer";
  shaft?: {
    diameter: number;
    tolerancePlus?: number;
    toleranceMinus?: number;
    surfaceFinishRa?: number;
    runoutTir?: number;
  };
  keyway?: {
    width: number;
    depth: number;
    angularLocation?: number;
  };
  shaftDiameter?: number;
  featureType?: string;
}): Promise<ShaftValidationResult> {
  const response = await fetch(`${DESKTOP_SERVER_URL}/phase25/check-shaft`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Shaft check failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check handling/lifting requirements
 */
export async function checkHandling(data: {
  totalWeightLbs: number;
  lengthIn?: number;
  widthIn?: number;
  heightIn?: number;
  hasLiftingLugs?: boolean;
  numLiftingLugs?: number;
  lugCapacityLbs?: number;
  cgMarked?: boolean;
  cgLocation?: string;
  hasRiggingDiagram?: boolean;
}): Promise<HandlingValidationResult> {
  const response = await fetch(`${DESKTOP_SERVER_URL}/phase25/check-handling`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Handling check failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check BOM completeness
 */
export async function checkBOM(bomItems: {
  itemNumber: string;
  partNumber?: string;
  description?: string;
  quantity?: number;
  material?: string;
}[]): Promise<BOMValidationResult> {
  const response = await fetch(`${DESKTOP_SERVER_URL}/phase25/check-bom`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ bom_items: bomItems }),
  });

  if (!response.ok) {
    throw new Error(`BOM check failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check dimension callouts
 */
export async function checkDimensions(dimensions: {
  value: number;
  tolerance?: number;
  tolerancePlus?: number;
  toleranceMinus?: number;
  unit?: string;
}[]): Promise<DimensionValidationResult> {
  const response = await fetch(`${DESKTOP_SERVER_URL}/phase25/check-dimensions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dimensions }),
  });

  if (!response.ok) {
    throw new Error(`Dimension check failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check OSHA safety requirements
 */
export async function checkOSHA(data: {
  guardrails?: {
    topRailHeight?: number;
    hasMidRail?: boolean;
    hasToeBoard?: boolean;
    toeboardHeight?: number;
    openingSize?: number;
  }[];
  ladders?: {
    width?: number;
    rungSpacing?: number;
    sideRailExtension?: number;
    height?: number;
    hasCage?: boolean;
  }[];
  platforms?: {
    width?: number;
    length?: number;
    height?: number;
  }[];
}): Promise<OSHAValidationResult> {
  const response = await fetch(`${DESKTOP_SERVER_URL}/phase25/check-osha`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`OSHA check failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Run all Phase 25 checks on a drawing
 */
export async function runAllPhase25Checks(request: ValidationRequest): Promise<ValidationResponse> {
  return validateDrawing({
    ...request,
    checks: ["holes", "structural", "shaft", "handling", "bom", "dimensions", "osha"],
  });
}
