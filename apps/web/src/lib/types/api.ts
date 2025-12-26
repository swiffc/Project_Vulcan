/**
 * Shared API Types
 * Common types used across the application for API responses
 */

// Health Check Response
export interface HealthResponse {
  status: "healthy" | "unhealthy" | "degraded";
  version?: string;
  uptime?: number;
  services?: ServiceHealth[];
}

export interface ServiceHealth {
  name: string;
  status: "online" | "offline" | "degraded";
  latency_ms?: number;
  last_check?: string;
}

// Validation Types
export interface ValidationResult {
  id: string;
  file_path: string;
  file_name: string;
  timestamp: string;
  duration_ms: number;
  drawing_type: string;
  extraction: ExtractionResult;
  summary: ValidationSummary;
  severity_counts: SeverityCounts;
  results_by_standard: ResultsByStandard;
  all_issues: ValidationIssue[];
}

export interface ExtractionResult {
  success: boolean;
  errors: string[];
  page_count: number;
  part_number: string;
  revision: string;
}

export interface ValidationSummary {
  total_checks: number;
  passed: number;
  failed: number;
  warnings: number;
  critical_failures: number;
  pass_rate: number;
}

export interface SeverityCounts {
  critical: number;
  error: number;
  warning: number;
  info: number;
}

export interface ResultsByStandard {
  api_661?: StandardResult;
  asme?: StandardResult;
  aws_d1_1?: StandardResult;
  osha?: StandardResult;
  bom?: StandardResult;
  dimension?: StandardResult;
  completeness?: StandardResult;
  hpc_mechanical?: StandardResult;
  hpc_walkway?: StandardResult;
  hpc_header?: StandardResult;
}

export interface StandardResult {
  total_checks: number;
  passed: number;
  failed: number;
  warnings: number;
  critical_failures: number;
  issues: ValidationIssue[];
}

export interface ValidationIssue {
  severity: "critical" | "error" | "warning" | "info";
  check_type: string;
  message: string;
  location?: string;
  suggestion?: string;
  standard_reference?: string;
}

// CAD Types
export interface CADModelInfo {
  file_name: string;
  file_path: string;
  model_type: "part" | "assembly" | "drawing";
  configuration?: string;
  mass_kg?: number;
  volume_m3?: number;
  surface_area_m2?: number;
  material?: string;
  part_count?: number;
}

export interface BOMItem {
  item_number: number;
  part_number: string;
  description: string;
  quantity: number;
  material?: string;
  weight_kg?: number;
  unit?: string;
}

// ACHE Types
export interface ACHECalculationResult {
  success: boolean;
  result?: Record<string, unknown>;
  error?: string;
  calculation_type: string;
  timestamp: string;
}

// Desktop Server Types
export interface DesktopStatus {
  connected: boolean;
  solidworks_running: boolean;
  active_document?: string;
  api_version?: string;
  last_ping?: string;
}

// API Response Wrapper
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

// Paginated Response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_prev: boolean;
}
