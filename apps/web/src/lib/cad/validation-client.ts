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
  };
  message: string;
  error?: string;
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
