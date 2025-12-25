/**
 * Validation Intent Parser
 * 
 * Parses natural language commands to detect validation requests.
 */

export interface ValidationIntent {
  action: "validate" | "check" | "analyze";
  type: "drawing" | "ache" | "gdt" | "welding" | "material" | "general";
  fileRef?: string; // "drawing ABC-123", "this drawing", etc.
  checks?: string[]; // Specific check types requested
  confidence: number; // 0-1
}

const VALIDATION_KEYWORDS = {
  actions: [
    "validate",
    "check",
    "verify",
    "inspect",
    "review",
    "analyze",
    "audit",
    "scan",
  ],
  types: {
    gdt: ["gd&t", "gdt", "geometric", "tolerance", "tolerances", "datum", "datums", "position"],
    welding: ["weld", "welds", "welding", "aws", "d1.1", "fillet", "groove"],
    material: ["material", "materials", "mtr", "astm", "spec", "composition", "chemical"],
    ache: ["ache", "comprehensive", "complete", "full", "all", "everything"],
    drawing: ["drawing", "dwg", "print", "blueprint", "sheet"],
  },
  fileRefs: [
    /drawing\s+([A-Z0-9-]+)/i,
    /dwg\s+([A-Z0-9-]+)/i,
    /part\s+([A-Z0-9-]+)/i,
    /([A-Z0-9]{3,}-[A-Z0-9]{2,})/i, // ABC-123 pattern
    /this\s+(drawing|dwg|part)/i,
    /current\s+(drawing|dwg|part)/i,
  ],
};

/**
 * Parse a user message to detect validation intent
 */
export function parseValidationIntent(message: string): ValidationIntent | null {
  const lowerMessage = message.toLowerCase();
  
  // Check if message contains validation action keywords
  const hasValidationAction = VALIDATION_KEYWORDS.actions.some(
    (keyword) => lowerMessage.includes(keyword)
  );
  
  if (!hasValidationAction) {
    return null;
  }
  
  // Determine validation type
  let type: ValidationIntent["type"] = "general";
  const checks: string[] = [];
  let typeScore = 0;
  
  // Check for GD&T
  if (VALIDATION_KEYWORDS.types.gdt.some((kw) => lowerMessage.includes(kw))) {
    checks.push("gdt");
    typeScore++;
  }
  
  // Check for welding
  if (VALIDATION_KEYWORDS.types.welding.some((kw) => lowerMessage.includes(kw))) {
    checks.push("welding");
    typeScore++;
  }
  
  // Check for material
  if (VALIDATION_KEYWORDS.types.material.some((kw) => lowerMessage.includes(kw))) {
    checks.push("material");
    typeScore++;
  }
  
  // Check for ACHE (comprehensive)
  if (VALIDATION_KEYWORDS.types.ache.some((kw) => lowerMessage.includes(kw))) {
    type = "ache";
    typeScore += 2; // Higher weight for ACHE
  }
  
  // Check for drawing reference
  if (VALIDATION_KEYWORDS.types.drawing.some((kw) => lowerMessage.includes(kw))) {
    type = checks.length > 0 ? "drawing" : type;
    typeScore++;
  }
  
  // Set type based on checks
  if (checks.length === 1) {
    type = checks[0] as any;
  } else if (checks.length > 1) {
    type = "drawing"; // Multi-check validation
  } else if (type === "general") {
    type = "ache"; // Default to comprehensive if no specific checks
  }
  
  // Extract file reference
  let fileRef: string | undefined;
  for (const pattern of VALIDATION_KEYWORDS.fileRefs) {
    const match = message.match(pattern);
    if (match) {
      fileRef = match[1] || match[0];
      break;
    }
  }
  
  // Calculate confidence
  let confidence = 0.5; // Base confidence
  
  if (hasValidationAction) confidence += 0.2;
  if (checks.length > 0) confidence += 0.15 * checks.length;
  if (fileRef) confidence += 0.15;
  if (type === "ache") confidence += 0.1;
  
  confidence = Math.min(confidence, 1.0);
  
  // Determine action
  let action: ValidationIntent["action"] = "validate";
  if (lowerMessage.includes("check")) action = "check";
  if (lowerMessage.includes("analyze")) action = "analyze";
  
  return {
    action,
    type,
    fileRef,
    checks: checks.length > 0 ? checks : undefined,
    confidence,
  };
}

/**
 * Generate validation response message
 */
export function formatValidationResponse(intent: ValidationIntent, hasFile: boolean): string {
  const { action, type, fileRef, checks } = intent;
  
  if (!hasFile && !fileRef) {
    return `I can ${action} your drawing! Please upload a PDF drawing file and I'll run the validation.`;
  }
  
  const checkList = checks?.join(", ") || "all checks";
  const target = fileRef || "the uploaded drawing";
  
  return `📊 Starting ${type} validation for ${target}...\n\nRunning ${checkList}...`;
}

/**
 * Example patterns that trigger validation:
 * 
 * - "Check drawing ABC-123 for GD&T errors"
 * - "Validate this drawing"
 * - "Run ACHE validation"
 * - "Inspect welds in drawing XYZ-456"
 * - "Verify material specs"
 * - "Check GD&T and welding on this print"
 * - "Analyze this drawing for all issues"
 */
