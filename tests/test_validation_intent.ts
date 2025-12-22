/**
 * Validation Intent Parser Tests
 * 
 * Tests natural language command parsing for validation.
 */

import { parseValidationIntent } from "../apps/web/src/lib/cad/validation-intent";

function test_validation_intent_parser() {
  console.log("=" * 60);
  console.log("TEST: Validation Intent Parser");
  console.log("=" * 60);

  const testCases = [
    {
      input: "Check drawing ABC-123 for GD&T errors",
      expected: { action: "check", type: "gdt", hasFileRef: true, confidence: ">0.7" },
    },
    {
      input: "Validate this drawing",
      expected: { action: "validate", type: "ache", hasFileRef: true, confidence: ">0.6" },
    },
    {
      input: "Run ACHE validation",
      expected: { action: "validate", type: "ache", hasFileRef: false, confidence: ">0.7" },
    },
    {
      input: "Inspect welds in drawing XYZ-456",
      expected: { action: "validate", type: "welding", hasFileRef: true, confidence: ">0.7" },
    },
    {
      input: "Verify material specs on part DEF-789",
      expected: { action: "validate", type: "material", hasFileRef: true, confidence: ">0.7" },
    },
    {
      input: "Check GD&T and welding on this print",
      expected: { action: "check", type: "drawing", hasFileRef: true, confidence: ">0.7" },
    },
    {
      input: "Analyze this drawing for all issues",
      expected: { action: "analyze", type: "ache", hasFileRef: true, confidence: ">0.7" },
    },
    {
      input: "How's the weather today?",
      expected: null,
    },
  ];

  let passed = 0;
  let failed = 0;

  for (const testCase of testCases) {
    const result = parseValidationIntent(testCase.input);
    
    console.log(`\nInput: "${testCase.input}"`);
    
    if (testCase.expected === null) {
      if (result === null) {
        console.log("✓ Correctly identified as non-validation");
        passed++;
      } else {
        console.log(`✗ False positive: ${JSON.stringify(result)}`);
        failed++;
      }
    } else {
      if (result === null) {
        console.log("✗ Failed to detect validation intent");
        failed++;
      } else {
        const checks = [];
        
        // Check action
        if (result.action === testCase.expected.action) {
          checks.push("action ✓");
        } else {
          checks.push(`action ✗ (expected ${testCase.expected.action}, got ${result.action})`);
        }
        
        // Check type
        if (result.type === testCase.expected.type) {
          checks.push("type ✓");
        } else {
          checks.push(`type ✗ (expected ${testCase.expected.type}, got ${result.type})`);
        }
        
        // Check file ref
        const hasFileRef = !!result.fileRef;
        if (hasFileRef === testCase.expected.hasFileRef) {
          checks.push("fileRef ✓");
        } else {
          checks.push(`fileRef ✗ (expected ${testCase.expected.hasFileRef}, got ${hasFileRef})`);
        }
        
        // Check confidence
        const confidenceThreshold = parseFloat(testCase.expected.confidence.replace(">", ""));
        if (result.confidence > confidenceThreshold) {
          checks.push(`confidence ✓ (${result.confidence.toFixed(2)})`);
        } else {
          checks.push(`confidence ✗ (${result.confidence.toFixed(2)} <= ${confidenceThreshold})`);
        }
        
        const allPassed = checks.every((c) => c.includes("✓"));
        if (allPassed) {
          console.log(`✓ ${checks.join(", ")}`);
          passed++;
        } else {
          console.log(`✗ ${checks.join(", ")}`);
          failed++;
        }
        
        console.log(`  Result: ${JSON.stringify(result)}`);
      }
    }
  }

  console.log("\n" + "=" * 60);
  console.log(`Results: ${passed} passed, ${failed} failed`);
  console.log("=" * 60);

  return failed === 0;
}

// Run tests
console.log("\n" + "=".repeat(70));
console.log(" ".repeat(15) + "VALIDATION INTENT TESTS");
console.log("=".repeat(70));

const success = test_validation_intent_parser();

if (success) {
  console.log("\n✓ ALL TESTS PASSED");
  process.exit(0);
} else {
  console.log("\n✗ SOME TESTS FAILED");
  process.exit(1);
}
