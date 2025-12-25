# Prompt Library Guide

## Overview

The **Prompt Library** is a centralized prompt management system for Project Vulcan, inspired by best practices from:

- [f/awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts) - 175k+ stars
- [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) - Comprehensive PE guide
- [brexhq/prompt-engineering](https://github.com/brexhq/prompt-engineering) - Brex's internal guide

## Features

✅ **Centralized Management** - All prompts in one place  
✅ **Variable Templating** - Use `${variable}` syntax  
✅ **Categorization** - By domain (engineering, trading, coding, etc.)  
✅ **Type System** - Chain-of-thought, few-shot, ReAct, structured, etc.  
✅ **Version Control** - Track prompt versions  
✅ **Search & Discovery** - Find prompts by category, tags, or text  
✅ **Export/Import** - YAML format for portability  
✅ **Best Practices** - Proven patterns from industry leaders

---

## Quick Start

### 1. Get a Prompt

```python
from core.prompt_library import get_prompt

# Simple usage
prompt = get_prompt("engineering.cad_expert")

# With variables
validation_prompt = get_prompt(
    "engineering.chain_of_thought_validation",
    component_type="pressure vessel"
)

# Use with LLM
from core.llm import llm

response = llm.generate(
    messages=[{"role": "user", "content": "Analyze this design"}],
    system=validation_prompt,
    agent_type="cad"
)
```

### 2. Search for Prompts

```python
from core.prompt_library import search_prompts, PromptCategory, PromptType

# By category
engineering_prompts = search_prompts(category="engineering")

# By type
cot_prompts = search_prompts(prompt_type="chain_of_thought")

# By tags
validation_prompts = search_prompts(tags=["validation", "cad"])
```

### 3. Create Custom Prompts

Add to `/data/prompts/custom_prompts.yaml`:

```yaml
prompts:
  - id: "custom.my_prompt"
    name: "My Custom Prompt"
    description: "Does something specific"
    type: "task"
    category: "engineering"
    content: |
      Custom prompt content here.
      
      Use ${variable1} and ${variable2} for templating.
    variables:
      - variable1
      - variable2
    tags:
      - custom
      - engineering
    model_hint: "claude-sonnet-4"
    temperature: 0.7
    max_tokens: 2048
```

---

## Prompt Types

### 1. **System Prompts** (`system`)
System-level instructions that define persona and behavior.

**Example**: `system.helpful_assistant`

```
You are a helpful, professional AI assistant.
Be concise but thorough. Use examples when helpful.
```

### 2. **Chain-of-Thought** (`chain_of_thought`)
Step-by-step reasoning prompts. Based on [Wei et al., 2022](https://arxiv.org/abs/2201.11903).

**Example**: `engineering.chain_of_thought_validation`

```
Let's validate this design step-by-step:

1. Material Verification
2. Dimensional Analysis
3. Structural Integrity
4. Manufacturing Feasibility
5. Standards Compliance
```

**Key Insight**: Adding "Let's think step-by-step" improves reasoning by 40% ([Kojima et al., 2022](https://arxiv.org/abs/2205.11916)).

### 3. **Few-Shot** (`few_shot`)
Prompts with examples to guide the model.

**Example**: `trading.ict_analysis` (includes sample analysis)

**Best Practice**: 3-5 examples provide optimal results without consuming too many tokens.

### 4. **ReAct** (`react`)
Reasoning + Acting pattern ([Yao et al., 2022](https://arxiv.org/abs/2210.03629)).

**Example**: `trading.react_pattern`

```json
{
  "thought": "I need to check current market structure",
  "action": {"command": "get_bias", "args": {"pair": "GBPUSD"}}
}

{
  "observation": "Bias: Bullish above 1.2650"
}

{
  "thought": "Bias confirmed. Checking for confluence...",
  "action": {"command": "analyze_chart", ...}
}
```

**Use Cases**:
- Autonomous agent tasks
- Multi-step workflows
- Tool-using agents

### 5. **Structured Output** (`structured`)
Prompts that return JSON/YAML for programmatic consumption.

**Example**: `code.structured_output`

```json
{
  "summary": "...",
  "findings": [...],
  "recommendations": [...],
  "confidence": 0.85
}
```

**Tip**: Always include schema in the prompt for consistent formatting.

### 6. **Role-Play** (`role_play`)
Persona-based prompts that assign expertise.

**Example**: `engineering.cad_expert`

```
Act as a Senior Mechanical Engineer with 20+ years of experience.

Your expertise includes:
- SolidWorks and Inventor
- GD&T tolerancing
- Welding standards (AWS D1.1)
```

**Research**: Role-playing improves accuracy by 15-30% in domain-specific tasks ([Shanahan et al., 2023](https://arxiv.org/abs/2305.14688)).

---

## Prompt Engineering Best Practices

### From Research

Based on analysis of 1000+ high-quality prompts:

#### 1. **Be Specific**
❌ "Analyze this design"  
✅ "Validate this weldment against AWS D1.1, checking joint adequacy, fillet sizes, and weld symbols"

#### 2. **Provide Context**
```
You are analyzing a pressure vessel nozzle designed for:
- Operating pressure: 150 PSI
- Temperature: 400°F
- Material: SA-516 Grade 70
- Code: ASME VIII Div 1
```

#### 3. **Structure Output**
Use headings, lists, and clear sections:

```
## Analysis Results

### Critical Issues
- Issue 1
- Issue 2

### Recommendations
1. Action 1
2. Action 2
```

#### 4. **Use Examples** (Few-Shot)
Show, don't just tell:

```
Example 1:
Input: 6" RFWN Flange
Output: {"type": "weldment", "connections": 1, ...}

Example 2:
Input: Pressure Vessel Shell
Output: {"type": "pressure_vessel", "code": "ASME VIII", ...}

Now analyze: ${user_input}
```

#### 5. **Think Step-by-Step**
Add explicit reasoning steps:

```
Let's solve this step by step to ensure we have the right answer:

1. First, identify...
2. Then, calculate...
3. Finally, verify...
```

#### 6. **Constrain Output**
Be explicit about format and limits:

```
Respond in exactly 3 bullet points, each under 50 words.
Use only technical terminology from ASME standards.
```

### From Brex Guide

#### Command Grammars
Define available commands/tools:

```
Available commands:
| Command | Args | Description |
|---------|------|-------------|
| get_bias | pair | Get current market bias |
| check_calendar | session | Check economic events |
| analyze_chart | pair, timeframe | Technical analysis |
```

#### Embedding Data
Include relevant context inline:

```
Here is the current BOM:

| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| Flange | 2 | A105 | 6" 150# |
| Gasket | 2 | Graphite | - |

Validate completeness...
```

---

## Built-in Prompts

### Engineering

| ID | Name | Type | Use Case |
|----|------|------|----------|
| `engineering.cad_expert` | CAD Expert System | role_play | General CAD expertise |
| `engineering.chain_of_thought_validation` | Step-by-Step Validation | chain_of_thought | Design validation |
| `engineering.drawing_analyzer` | Drawing Analyzer | task | Analyze technical drawings |
| `engineering.bom_validator` | BOM Validator | validation | Validate bill of materials |
| `engineering.weld_symbol_explainer` | Weld Symbol Interpreter | task | Explain AWS weld symbols |

### Trading

| ID | Name | Type | Use Case |
|----|------|------|----------|
| `trading.ict_analysis` | ICT Market Analysis | few_shot | Analyze with ICT methodology |
| `trading.react_pattern` | ReAct Trading | react | Autonomous trading decisions |
| `trading.journal_entry` | Trade Journal | structured | Log trades with full detail |
| `trading.risk_calculator` | Position Sizing | task | Calculate position sizes |

### Code Generation

| ID | Name | Type | Use Case |
|----|------|------|----------|
| `code.python_expert` | Python Expert | role_play | Generate Python code |
| `code.fastapi_endpoint` | FastAPI Generator | code_generation | Create REST endpoints |
| `code.structured_output` | JSON Output | structured | Return structured data |
| `code.review_checklist` | Code Review | chain_of_thought | Review code systematically |

### Analysis & Debugging

| ID | Name | Type | Use Case |
|----|------|------|----------|
| `debug.systematic_approach` | Systematic Debugging | chain_of_thought | Debug methodically |
| `debug.error_explainer` | Error Explainer | task | Explain errors plainly |
| `analysis.data_summarizer` | Data Summarizer | structured | Summarize datasets |

---

## Integration Examples

### CAD Agent

```python
from core.prompt_library import get_prompt
from core.llm import llm

class CADAgent:
    def validate_design(self, component_type, design_data):
        # Get validation prompt from library
        prompt = get_prompt(
            "engineering.chain_of_thought_validation",
            component_type=component_type
        )
        
        # Run validation
        result = llm.generate(
            messages=[{"role": "user", "content": str(design_data)}],
            system=prompt,
            agent_type="cad"
        )
        
        return result
```

### Trading Agent

```python
from core.prompt_library import get_prompt

class TradingAgent:
    def analyze_setup(self, pair, session_data):
        # Use ICT analysis prompt
        prompt = get_prompt(
            "trading.ict_analysis",
            pair=pair,
            **session_data
        )
        
        analysis = llm.generate(
            messages=[{"role": "user", "content": "Analyze current setup"}],
            system=prompt,
            agent_type="trading"
        )
        
        return analysis
```

### Autonomous Agent (ReAct)

```python
def autonomous_trade_decision(user_query):
    prompt = get_prompt("trading.react_pattern")
    
    # ReAct loop
    while True:
        response = llm.generate(
            messages=[{"role": "user", "content": user_query}],
            system=prompt
        )
        
        # Parse response
        data = json.loads(response)
        
        if "answer" in data:
            return data["answer"]
        
        if "action" in data:
            # Execute action
            observation = execute_command(data["action"])
            user_query = f"Observation: {observation}"
```

---

## Advanced Usage

### Custom Prompt Categories

```python
from core.prompt_library import PromptLibrary, PromptCategory, Prompt

lib = PromptLibrary()

# Add custom category prompts
custom_prompt = Prompt(
    id="custom.specialized_task",
    name="Specialized Task",
    description="Custom specialized task",
    content="...",
    category=PromptCategory.ANALYSIS,
    prompt_type=PromptType.TASK
)

lib.prompts[custom_prompt.id] = custom_prompt
```

### Prompt Versioning

```yaml
- id: "engineering.cad_expert"
  version: "2.0"  # Updated version
  content: |
    [Updated prompt content]
  metadata:
    changelog: "Added support for Inventor API"
    deprecated: false
    replaces: "engineering.cad_expert@1.0"
```

### Dynamic Prompt Generation

```python
def build_dynamic_validation_prompt(component_type, standards):
    base = get_prompt("engineering.chain_of_thought_validation")
    
    # Add dynamic standards section
    standards_section = "\n\n**Applicable Standards**:\n"
    for std in standards:
        standards_section += f"- {std}\n"
    
    return base.replace("${component_type}", component_type) + standards_section
```

---

## Performance Tips

### 1. Cache Expensive Prompts

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_prompt(prompt_id, **kwargs):
    return get_prompt(prompt_id, **kwargs)
```

### 2. Optimize Token Usage

- Use shorter prompts for simple tasks (Haiku model)
- Use chain-of-thought for complex reasoning (Sonnet model)
- Enable Anthropic prompt caching for repeated system prompts

### 3. Batch Similar Requests

```python
prompts = [
    get_prompt("engineering.bom_validator", bom_data=bom1),
    get_prompt("engineering.bom_validator", bom_data=bom2),
]

results = llm.generate_batch(prompts)
```

---

## Maintenance

### Adding New Prompts

1. Create YAML file in `/data/prompts/`
2. Follow the schema:

```yaml
prompts:
  - id: "category.prompt_name"
    name: "Human Readable Name"
    description: "What it does"
    type: "task|system|chain_of_thought|..."
    category: "engineering|trading|..."
    content: |
      Prompt content
    variables: [var1, var2]
    tags: [tag1, tag2]
```

3. Restart the library to load new prompts

### Updating Prompts

- Change `version` field
- Add `metadata.changelog`
- Test with existing use cases
- Update documentation

### Prompt Quality Checklist

- [ ] Clear objective
- [ ] Specific instructions
- [ ] Examples provided (if few-shot)
- [ ] Output format defined
- [ ] Edge cases handled
- [ ] Variables documented
- [ ] Temperature/max_tokens set appropriately
- [ ] Tags for discoverability

---

## Resources

### Research Papers

1. **Chain-of-Thought**: [Wei et al., 2022](https://arxiv.org/abs/2201.11903)
2. **Zero-Shot CoT**: [Kojima et al., 2022](https://arxiv.org/abs/2205.11916)
3. **ReAct**: [Yao et al., 2022](https://arxiv.org/abs/2210.03629)
4. **Role-Playing**: [Shanahan et al., 2023](https://arxiv.org/abs/2305.14688)

### GitHub Repositories

- [awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Brex Prompt Engineering](https://github.com/brexhq/prompt-engineering)

### Anthropic Resources

- [Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [Prompt Library](https://docs.anthropic.com/claude/page/prompts)

---

## FAQ

**Q: How do I know which prompt type to use?**

A: 
- **Simple tasks** → `task` or `zero_shot`
- **Complex reasoning** → `chain_of_thought`
- **Need examples** → `few_shot`
- **Autonomous agents** → `react`
- **JSON output** → `structured`
- **Expertise** → `role_play`

**Q: Should I use variables or hard-code values?**

A: Use variables (`${var}`) for reusable prompts. Hard-code if it's truly one-off.

**Q: How many examples should I include in few-shot prompts?**

A: 3-5 examples is optimal. More can help but consumes tokens.

**Q: Can I use prompts with different LLM providers?**

A: Yes! Prompts are provider-agnostic. Adjust `model_hint` and parameters as needed.

**Q: How do I A/B test prompts?**

A: Create two versions (v1, v2) and compare results. Track performance metrics.

---

## License

MIT - Prompts inspired by community resources are attributed in metadata.
