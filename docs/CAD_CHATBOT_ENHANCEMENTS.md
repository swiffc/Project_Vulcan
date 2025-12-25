# CAD Chatbot Enhancement Requirements

## 🎯 Executive Summary

Current CAD chatbot has **strong foundation** (200+ tools, prompts, validation) but needs **10 critical enhancements** for professional-grade operation.

**Priority Scale**: 🔴 Critical | 🟡 Important | 🟢 Nice-to-have

---

## ✅ Current Strengths (Already Implemented)

1. ✅ **Tool Execution** - 200+ CAD operations (SolidWorks, Inventor)
2. ✅ **Screenshot Feedback** - Visual confirmation (sw_screenshot, inv_screenshot)
3. ✅ **Error Handling** - Basic try/catch in executeCADTool
4. ✅ **Prompt Library** - 10 CAD-specific expert prompts
5. ✅ **Dimension Extraction** - Advanced OCR with DimensionExtractor
6. ✅ **Standards Database** - ASME, AWS, ASTM, AISC specs
7. ✅ **Validation System** - 130+ ACHE validators, GD&T checks
8. ✅ **RULES.md Integration** - Engineering mindset, Plan-Build-Verify
9. ✅ **Unit Helpers** - Manual conversion (parseToMeters)
10. ✅ **File Upload** - PDF drawing upload capability

---

## 🔴 CRITICAL MISSING FEATURES (Implement First)

### 1. **Natural Language Dimension Parser** 🔴
**Status**: ✅ **JUST CREATED** → `core/cad_nlp_parser.py`

**What It Does**:
```python
# User says: "6 inch flange, quarter inch thick"
parser = CADNLPParser("solidworks")
params = parser.parse("6 inch flange, quarter inch thick")

# Auto-converts to SolidWorks units (METERS):
params["nominal_size"].value  # 0.1524 meters (6 inches)
params["thickness"].value     # 0.00635 meters (1/4 inch)
```

**Features**:
- Fractions ("1/2 inch", "3-1/4") ✅
- Written numbers ("quarter inch", "six inches") ✅
- Pipe sizes ("2 inch sch 40") ✅
- Angles ("45 degrees", "90°") ✅
- Material extraction ("A105", "316SS") ✅
- Standard extraction ("ASME B16.5") ✅
- Auto-converts to target CAD units (meters/cm) ✅

**Integration Point**: Inject into CAD chat route BEFORE tool execution

---

### 2. **Context Awareness System** 🔴
**Status**: ⚠️ **PARTIAL** (fetches status but no state tracking)

**Problem**: Bot doesn't remember what's currently open in CAD

**What's Needed**:

```typescript
// apps/web/src/lib/cad-context.ts

interface CADContext {
  software: "solidworks" | "inventor";
  connected: boolean;
  current_document: {
    name: string;
    type: "part" | "assembly" | "drawing";
    path: string;
    unsaved_changes: boolean;
  };
  active_sketch: string | null;
  selected_features: string[];
  last_operation: {
    tool: string;
    timestamp: Date;
    success: boolean;
  };
  session_history: Operation[];  // All operations this session
}

// Track state across messages
class CADSessionManager {
  getContext(): CADContext;
  updateContext(operation: Operation): void;
  getRelevantHistory(query: string): Operation[];
}
```

**Integration**:
- Store in Redis or in-memory cache
- Update after each CAD tool execution
- Inject into system prompt: "CURRENT CONTEXT: Part 'flange.sldprt' open, sketch active on Front plane"

---

### 3. **Intelligent Error Recovery** 🔴
**Status**: ⚠️ **BASIC** (logs errors but doesn't retry)

**Current Code** (cad-tools.ts):
```typescript
catch (error) {
  const errorMessage = error instanceof Error ? error.message : String(error);
  console.error(`[CAD Tool] Error executing ${toolName}:`, errorMessage);
  return { success: false, error: errorMessage };  // ❌ Just fails
}
```

**What's Needed**:

```typescript
// apps/web/src/lib/cad-error-recovery.ts

interface RetryStrategy {
  maxRetries: number;
  backoffMs: number;
  shouldRetry: (error: string) => boolean;
}

class CADErrorRecovery {
  async executeWithRetry(
    toolName: string,
    toolInput: Record<string, unknown>,
    strategy: RetryStrategy = DEFAULT_STRATEGY
  ): Promise<ToolResult> {
    for (let attempt = 1; attempt <= strategy.maxRetries; attempt++) {
      const result = await executeCADTool(toolName, toolInput);
      
      if (result.success) {
        return result;
      }
      
      // Check if retryable
      if (!strategy.shouldRetry(result.error || "")) {
        return result;  // Permanent failure
      }
      
      // Auto-fix common errors
      if (result.error?.includes("sketch not closed")) {
        await executeCADTool("sw_close_sketch", {});
        continue;  // Retry original operation
      }
      
      if (result.error?.includes("document not open")) {
        await executeCADTool("sw_new_part", {});
        continue;
      }
      
      if (result.error?.includes("feature failed")) {
        // Reduce extrude depth and retry
        if (toolInput.depth && typeof toolInput.depth === "number") {
          toolInput.depth *= 0.9;  // Reduce by 10%
          continue;
        }
      }
      
      // Wait before retry
      await new Promise(r => setTimeout(r, strategy.backoffMs * attempt));
    }
    
    return { success: false, error: "Max retries exceeded" };
  }
  
  getRecoverySuggestion(error: string): string {
    // Provide human-readable recovery steps
  }
}
```

**Common Errors to Handle**:
- "Sketch not closed" → Auto-call sw_close_sketch
- "Document not open" → Create new document
- "Feature failed" → Adjust parameters (reduce depth, increase radius)
- "Timeout" → Retry with exponential backoff
- "COM disconnected" → Reconnect to CAD app

---

### 4. **Vision Integration (Screenshot Analysis)** 🔴
**Status**: ⚠️ **SCREENSHOT EXISTS** but no Claude vision analysis

**Current**: Takes screenshot, returns base64 string, but bot doesn't SEE it

**What's Needed**:

```typescript
// apps/web/src/app/api/chat/cad/route.ts

// After creating CAD geometry:
const screenshotResult = await executeCADTool("sw_screenshot", {});

if (screenshotResult.success && screenshotResult.result?.image) {
  // ADD VISION ANALYSIS
  const visionResponse = await client.messages.create({
    model: "claude-sonnet-4",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: {
              type: "base64",
              media_type: "image/png",
              data: screenshotResult.result.image,
            },
          },
          {
            type: "text",
            text: "Analyze this CAD model. Does it match the user's request for a '6 inch flange'? Check dimensions, geometry, and overall appearance."
          }
        ],
      },
    ],
  });
  
  // Use vision analysis to verify build success
  const analysis = visionResponse.content[0].text;
  
  // If doesn't match, auto-correct
  if (analysis.includes("incorrect") || analysis.includes("wrong")) {
    // Retry with adjustments
  }
}
```

**Use Cases**:
- Verify built geometry matches intent
- Catch modeling errors (wrong plane, missing features)
- Quality check before saving
- Generate automatic documentation ("Screenshot shows 6\" OD flange with bolt holes")

---

### 5. **Multi-Step Workflow Orchestration** 🔴
**Status**: ⚠️ **SEQUENTIAL ONLY** (no parallelization or dependencies)

**Problem**: Bot executes tools one-by-one, can't handle complex workflows

**What's Needed**:

```python
# core/cad_workflow_engine.py

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowStep:
    id: str
    tool_name: str
    tool_input: Dict[str, Any]
    depends_on: List[str] = []  # IDs of prerequisite steps
    retry_on_failure: bool = True
    max_retries: int = 3
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None

class CADWorkflowEngine:
    """Execute complex multi-step CAD workflows with dependencies."""
    
    def __init__(self):
        self.steps: Dict[str, WorkflowStep] = {}
        self.execution_order: List[str] = []
    
    def add_step(self, step: WorkflowStep):
        """Add a step to the workflow."""
        self.steps[step.id] = step
    
    def build_execution_plan(self) -> List[List[str]]:
        """
        Build execution plan with parallelization.
        
        Returns:
            List of lists - each sublist can execute in parallel
            
        Example:
            [
                ["connect", "load_material_db"],  # Parallel
                ["new_part"],                      # Sequential
                ["sketch_base", "sketch_holes"],  # Parallel
                ["extrude_base"],
                ["pattern_holes"],
                ["save"]
            ]
        """
        # Topological sort with parallel grouping
        pass
    
    async def execute(self) -> Dict[str, Any]:
        """Execute workflow with optimal parallelization."""
        plan = self.build_execution_plan()
        
        for parallel_group in plan:
            # Execute steps in parallel
            results = await asyncio.gather(*[
                self._execute_step(step_id)
                for step_id in parallel_group
            ])
            
            # Check for failures
            if any(not r.success for r in results):
                return {"success": False, "failed_step": ...}
        
        return {"success": True, "results": ...}
    
    async def _execute_step(self, step_id: str):
        """Execute a single step with retry logic."""
        step = self.steps[step_id]
        
        # Check dependencies
        for dep_id in step.depends_on:
            if self.steps[dep_id].status != StepStatus.COMPLETE:
                step.status = StepStatus.SKIPPED
                return
        
        step.status = StepStatus.RUNNING
        
        # Execute with retries
        for attempt in range(step.max_retries):
            result = await executeCADTool(step.tool_name, step.tool_input)
            
            if result.success:
                step.status = StepStatus.COMPLETE
                step.result = result
                return result
            
            if not step.retry_on_failure:
                break
        
        step.status = StepStatus.FAILED
        step.error = result.error
        return result

# Example Usage:
# Build a flange (7 steps)
workflow = CADWorkflowEngine()
workflow.add_step(WorkflowStep(
    id="connect",
    tool_name="sw_connect",
    tool_input={}
))
workflow.add_step(WorkflowStep(
    id="new_part",
    tool_name="sw_new_part",
    tool_input={},
    depends_on=["connect"]
))
workflow.add_step(WorkflowStep(
    id="sketch_base",
    tool_name="sw_create_sketch",
    tool_input={"plane": "Front"},
    depends_on=["new_part"]
))
# ... etc
result = await workflow.execute()
```

---

## 🟡 IMPORTANT FEATURES (Next Priority)

### 6. **Design History & Undo** 🟡
**Status**: ❌ **MISSING**

**What's Needed**:
- Track all CAD operations in session
- Allow "undo last 3 operations"
- Checkpoint/restore state
- Feature tree navigation ("go back to before the fillet")

```python
class CADHistory:
    operations: List[CADOperation] = []
    
    def undo(self, steps: int = 1):
        """Undo last N operations."""
        # Call sw_undo or recreate file from checkpoint
        
    def checkpoint(self, name: str):
        """Save current state for later restore."""
        
    def restore(self, checkpoint_name: str):
        """Restore to a saved state."""
```

---

### 7. **Standards Database Integration** 🟡
**Status**: ⚠️ **EXISTS** but not auto-queried during builds

**What's Needed**:
- Auto-lookup standard parts during design
- Suggest correct bolt sizes for flange class
- Validate material against code requirements
- Propose standard pipe schedules

```python
# Integration point: Before building
user_request = "Build a 6 inch 150# flange"
parsed = nlp_parser.parse(user_request)

# Auto-query standards
from agents.cad_agent.adapters.standards_db import standards_db
flange_data = standards_db.get_flange_spec(
    size=6,
    rating=150,
    type="RFWN"
)

# Use standard dimensions
bolt_circle_diameter = flange_data["bolt_circle"]
bolt_count = flange_data["bolt_count"]
bolt_size = flange_data["bolt_size"]  # "3/4-10 UNC"
```

---

### 8. **Real-Time Validation During Build** 🟡
**Status**: ⚠️ **POST-BUILD ONLY**

**What's Needed**:
- Check clearances WHILE building
- Validate against standards DURING design
- Warn about manufacturability issues BEFORE saving

```typescript
// After each feature creation:
const validationResult = await executeCADTool("sw_validate_part", {
  checks: ["interference", "clearance", "wall_thickness"]
});

if (!validationResult.success || validationResult.result?.issues.length > 0) {
  // Warn user immediately
  // Suggest fixes
  // Allow auto-correction
}
```

---

### 9. **Cost & Fabrication Estimation** 🟡
**Status**: ❌ **MISSING**

**What's Needed**:
```python
class FabricationEstimator:
    def estimate_cost(self, cad_file: str) -> Dict:
        """
        Estimate fabrication cost.
        
        Returns:
            {
                "material_cost": 125.50,
                "machining_hours": 2.5,
                "machining_cost": 187.50,
                "total_cost": 313.00,
                "lead_time_days": 5,
                "processes": ["CNC turning", "drilling", "tapping"]
            }
        """
        pass
```

---

### 10. **Voice Commands** 🟢 (Nice-to-have)
**Status**: ❌ **MISSING**

**What's Needed**:
- Hands-free CAD operation
- "Create a 6 inch flange"
- "Rotate view 90 degrees"
- "Zoom to fit"

```typescript
// Web Speech API integration
const recognition = new webkitSpeechRecognition();
recognition.onresult = (event) => {
  const command = event.results[0][0].transcript;
  handleSendMessage(command);  // Existing chat handler
};
```

---

## 📊 Implementation Priority Matrix

| Feature | Priority | Effort | Impact | Status |
|---------|----------|--------|--------|--------|
| **1. NLP Dimension Parser** | 🔴 Critical | Medium | High | ✅ **DONE** |
| **2. Context Awareness** | 🔴 Critical | High | High | ⚠️ Partial |
| **3. Error Recovery** | 🔴 Critical | Medium | High | ⚠️ Basic |
| **4. Vision Analysis** | 🔴 Critical | Low | High | ⚠️ Screenshot only |
| **5. Workflow Engine** | 🔴 Critical | High | High | ❌ Missing |
| **6. Design History** | 🟡 Important | Medium | Medium | ❌ Missing |
| **7. Standards Integration** | 🟡 Important | Low | Medium | ⚠️ Exists |
| **8. Real-Time Validation** | 🟡 Important | Medium | Medium | ⚠️ Post-build |
| **9. Cost Estimation** | 🟡 Important | High | Low | ❌ Missing |
| **10. Voice Commands** | 🟢 Nice-to-have | Low | Low | ❌ Missing |

---

## 🚀 Recommended Implementation Order

### **Phase 1: Foundation (Week 1-2)**
1. ✅ **NLP Dimension Parser** → DONE
2. **Context Awareness System** → Track CAD state
3. **Error Recovery** → Auto-retry with smart fixes

### **Phase 2: Intelligence (Week 3-4)**
4. **Vision Integration** → Claude sees screenshots
5. **Workflow Engine** → Complex multi-step builds

### **Phase 3: Polish (Week 5-6)**
6. **Design History** → Undo/checkpoint
7. **Standards Integration** → Auto-lookup during build
8. **Real-Time Validation** → Check while building

### **Phase 4: Advanced (Week 7+)**
9. **Cost Estimation** → Fab cost calculator
10. **Voice Commands** → Hands-free operation

---

## 💡 Quick Wins (Implement Today)

### **Quick Win #1: Add NLP Parser to CAD Chat** (10 minutes)
```typescript
// apps/web/src/app/api/chat/cad/route.ts

import { CADNLPParser } from "@/core/cad_nlp_parser";

// BEFORE tool execution loop:
const parser = new CADNLPParser("solidworks");
const lastMessage = anthropicMessages[anthropicMessages.length - 1].content;
const parsedParams = parser.parse(lastMessage);

// Inject into system prompt
systemPrompt += `\n\nPARSED USER DIMENSIONS:\n${parser.format_for_cad(parsedParams)}`;
```

### **Quick Win #2: Enable Vision on Screenshots** (15 minutes)
```typescript
// After sw_screenshot:
if (screenshotResult.result?.image) {
  // Send to Claude vision
  const visionMsg = await client.messages.create({
    model: "claude-sonnet-4",
    max_tokens: 512,
    messages: [{
      role: "user",
      content: [
        { type: "image", source: { type: "base64", media_type: "image/png", data: screenshotResult.result.image } },
        { type: "text", text: "Does this CAD model look correct? Briefly describe what you see." }
      ]
    }]
  });
  
  // Add vision feedback to response
  assistantMessage += `\n\n**Visual Check**: ${visionMsg.content[0].text}`;
}
```

### **Quick Win #3: Add Basic Retry Logic** (20 minutes)
```typescript
// Wrap executeCADTool:
async function executeWithRetry(toolName, toolInput, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    const result = await executeCADTool(toolName, toolInput);
    if (result.success) return result;
    
    // Auto-fix sketch not closed
    if (result.error?.includes("sketch not closed")) {
      await executeCADTool("sw_close_sketch", {});
      continue;
    }
    
    // Retry after delay
    await new Promise(r => setTimeout(r, 1000 * (i + 1)));
  }
  return { success: false, error: "Max retries exceeded" };
}
```

---

## 📚 Additional Resources

### **Libraries to Install**
```bash
# For NLP Parser (already created)
pip install fractions  # Built-in

# For voice commands
npm install react-speech-recognition

# For cost estimation
pip install numpy scipy  # For calculations
```

### **API Documentation**
- SolidWorks API: https://help.solidworks.com/api
- Inventor API: https://help.autodesk.com/view/INVNTOR/
- Claude Vision: https://docs.anthropic.com/claude/docs/vision

---

## ✅ Summary

**Your CAD chatbot is 70% complete**. The critical gaps are:

1. ✅ **NLP Dimension Parser** → DONE (just created)
2. ⚠️ **Context Awareness** → Need state tracking
3. ⚠️ **Error Recovery** → Need smart retry logic
4. ⚠️ **Vision Integration** → Have screenshots, need Claude analysis
5. ❌ **Workflow Engine** → Need multi-step orchestration

**Implement the 3 Quick Wins above TODAY** for immediate impact, then tackle the Phase 1 features (Context + Error Recovery) this week.
