"""
Prompt Library for Project Vulcan
==================================

Centralized prompt management inspired by:
- f/awesome-chatgpt-prompts
- dair-ai/Prompt-Engineering-Guide  
- brexhq/prompt-engineering

Provides reusable, version-controlled prompts for all agents.
"""

import os
import yaml
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class PromptType(Enum):
    """Types of prompts in the library."""
    SYSTEM = "system"  # System-level instructions
    TASK = "task"  # Specific task templates
    CHAIN_OF_THOUGHT = "chain_of_thought"  # Reasoning prompts
    FEW_SHOT = "few_shot"  # With examples
    ZERO_SHOT = "zero_shot"  # No examples
    REACT = "react"  # ReAct pattern (thought + action)
    STRUCTURED = "structured"  # JSON/YAML output
    ROLE_PLAY = "role_play"  # Persona-based
    CODE_GENERATION = "code_generation"  # Code generation tasks


class PromptCategory(Enum):
    """Prompt categories by domain."""
    ENGINEERING = "engineering"
    TRADING = "trading"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    VALIDATION = "validation"
    SUMMARIZATION = "summarization"
    DEBUGGING = "debugging"
    CREATIVE = "creative"


@dataclass
class Prompt:
    """A single prompt template."""
    id: str
    name: str
    description: str
    content: str
    prompt_type: PromptType
    category: PromptCategory
    variables: List[str] = field(default_factory=list)  # ${variable} placeholders
    examples: List[Dict[str, str]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    author: str = "Project Vulcan"
    version: str = "1.0"
    model_hint: str = "claude-sonnet-4"  # Recommended model
    temperature: float = 0.7
    max_tokens: int = 2048
    metadata: Dict[str, Any] = field(default_factory=dict)


class PromptLibrary:
    """
    Centralized prompt library with best practices from GitHub research.
    
    Features:
    - Templating with ${variable} syntax
    - Chain-of-thought prompts
    - ReAct patterns
    - Few-shot examples
    - Role-based prompts
    - Version control
    """
    
    def __init__(self, library_path: Optional[Path] = None):
        self.library_path = library_path or Path(__file__).parent.parent / "data" / "prompts"
        self.library_path.mkdir(parents=True, exist_ok=True)
        self.prompts: Dict[str, Prompt] = {}
        self._load_library()
        self._register_builtin_prompts()
    
    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Get a prompt by ID."""
        return self.prompts.get(prompt_id)
    
    def search_prompts(
        self,
        query: Optional[str] = None,
        category: Optional[PromptCategory] = None,
        prompt_type: Optional[PromptType] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Prompt]:
        """Search prompts by various criteria."""
        results = list(self.prompts.values())
        
        if category:
            results = [p for p in results if p.category == category]
        
        if prompt_type:
            results = [p for p in results if p.prompt_type == prompt_type]
        
        if tags:
            results = [p for p in results if any(tag in p.tags for tag in tags)]
        
        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if query_lower in p.name.lower()
                or query_lower in p.description.lower()
                or any(query_lower in tag for tag in p.tags)
            ]
        
        return results
    
    def format_prompt(self, prompt_id: str, **variables) -> str:
        """Format a prompt with variables."""
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return ""
        
        content = prompt.content
        for key, value in variables.items():
            content = content.replace(f"${{{key}}}", str(value))
        
        return content
    
    def load_from_yaml(self, yaml_path: str):
        """Load prompts from a YAML file."""
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'prompts' in data:
                    for prompt_data in data['prompts']:
                        prompt = Prompt(
                            id=prompt_data['id'],
                            name=prompt_data['name'],
                            description=prompt_data['description'],
                            content=prompt_data['content'],
                            prompt_type=PromptType(prompt_data.get('type', 'task')),
                            category=PromptCategory(prompt_data.get('category', 'analysis')),
                            variables=prompt_data.get('variables', []),
                            examples=prompt_data.get('examples', []),
                            tags=prompt_data.get('tags', []),
                            version=prompt_data.get('version', '1.0'),
                            model_hint=prompt_data.get('model_hint', 'claude-sonnet-4'),
                            temperature=prompt_data.get('temperature', 0.7),
                            max_tokens=prompt_data.get('max_tokens', 2048),
                        )
                        self.prompts[prompt.id] = prompt
        except Exception as e:
            print(f"Error loading {yaml_path}: {e}")
    
    def export_to_yaml(self, output_path: str):
        """Export prompts to YAML file."""
        prompts_data = []
        for prompt in self.prompts.values():
            prompts_data.append({
                'id': prompt.id,
                'name': prompt.name,
                'description': prompt.description,
                'type': prompt.prompt_type.value,
                'category': prompt.category.value,
                'content': prompt.content,
                'variables': prompt.variables,
                'examples': prompt.examples,
                'tags': prompt.tags,
                'version': prompt.version,
                'model_hint': prompt.model_hint,
                'temperature': prompt.temperature,
                'max_tokens': prompt.max_tokens,
            })
        
        with open(output_path, 'w') as f:
            yaml.dump({'version': '1.0', 'prompts': prompts_data}, f, default_flow_style=False)
    
    def _load_library(self):
        """Load prompts from YAML files."""
        for yaml_file in self.library_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and 'prompts' in data:
                        for prompt_data in data['prompts']:
                            prompt = Prompt(
                                id=prompt_data['id'],
                                name=prompt_data['name'],
                                description=prompt_data['description'],
                                content=prompt_data['content'],
                                prompt_type=PromptType(prompt_data.get('type', 'task')),
                                category=PromptCategory(prompt_data.get('category', 'analysis')),
                                variables=prompt_data.get('variables', []),
                                examples=prompt_data.get('examples', []),
                                tags=prompt_data.get('tags', []),
                                version=prompt_data.get('version', '1.0'),
                                model_hint=prompt_data.get('model_hint', 'claude-sonnet-4'),
                                temperature=prompt_data.get('temperature', 0.7),
                                max_tokens=prompt_data.get('max_tokens', 2048),
                            )
                            self.prompts[prompt.id] = prompt
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")
    
    def _register_builtin_prompts(self):
        """Register built-in prompts based on research."""
        
        # =====================================================================
        # ENGINEERING PROMPTS (CAD Agent)
        # =====================================================================
        
        self.prompts["engineering.cad_expert"] = Prompt(
            id="engineering.cad_expert",
            name="CAD Expert System Prompt",
            description="Expert mechanical engineer for CAD automation",
            content="""Act as a Senior Mechanical Engineer with 20+ years of experience in CAD design and manufacturing.

Your expertise includes:
- SolidWorks and Inventor CAD software
- GD&T (Geometric Dimensioning & Tolerancing)
- Welding standards (AWS D1.1)
- Material selection (ASTM/ASME)
- Design for Manufacturing (DFM)

When analyzing designs:
1. First, identify potential issues and standards violations
2. Explain the impact of each issue with specific references
3. Provide actionable recommendations with examples
4. Consider trade-offs and alternative approaches
5. Reference relevant standards (ASME Y14.5, AWS D1.1, etc.)

Maintain a professional but approachable tone. Ask clarifying questions if requirements are unclear.""",
            prompt_type=PromptType.ROLE_PLAY,
            category=PromptCategory.ENGINEERING,
            tags=["CAD", "mechanical", "expert", "solidworks", "engineering"],
            model_hint="claude-sonnet-4",
            temperature=0.5,
        )
        
        self.prompts["engineering.chain_of_thought_validation"] = Prompt(
            id="engineering.chain_of_thought_validation",
            name="Chain-of-Thought CAD Validation",
            description="Step-by-step reasoning for design validation",
            content="""Validate the ${component_type} design step-by-step:

Let's work through this systematically to ensure we have the right answer:

1. **Material Verification**:
   - Check material specification against requirements
   - Verify material properties meet load conditions
   - Confirm availability and cost-effectiveness

2. **Dimensional Analysis**:
   - Verify critical dimensions against tolerances
   - Check for interference and clearances
   - Validate against standards (ASME Y14.5)

3. **Structural Integrity**:
   - Calculate stresses and safety factors
   - Check weld joint adequacy (if applicable)
   - Verify bolt patterns and fastener sizing

4. **Manufacturing Feasibility**:
   - Assess machining complexity
   - Check for sharp internal corners
   - Verify accessibility for welding/assembly

5. **Standards Compliance**:
   - Cross-reference with applicable codes
   - Check for missing callouts or notes
   - Verify drawing completeness

**Final Assessment**: [Pass/Fail with specific recommendations]""",
            prompt_type=PromptType.CHAIN_OF_THOUGHT,
            category=PromptCategory.VALIDATION,
            variables=["component_type"],
            tags=["CAD", "validation", "cot", "systematic", "engineering"],
            temperature=0.3,
        )
        
        # =====================================================================
        # TRADING PROMPTS (Trading Agent)
        # =====================================================================
        
        self.prompts["trading.ict_analysis"] = Prompt(
            id="trading.ict_analysis",
            name="ICT Market Structure Analysis",
            description="Analyze market structure using ICT concepts",
            content="""Analyze the ${pair} chart using ICT methodology:

**Market Structure Analysis:**
1. Identify current trend direction (bullish/bearish/ranging)
2. Locate key liquidity pools (buy-side/sell-side)
3. Mark order blocks (bullish OB / bearish OB)
4. Identify Fair Value Gaps (FVG)
5. Determine institutional reference points

**Session Analysis:**
- London Killzone: ${london_time}
- New York Killzone: ${newyork_time}
- Asia Session Range: ${asia_range}

**Setup Confluence:**
Check for alignment of:
- [ ] Order block + FVG
- [ ] Liquidity sweep
- [ ] Session timing
- [ ] HTF bias alignment
- [ ] 50% retracement level

**Bias**: ${bias}
**Confidence**: ${confidence}/10

Provide specific entry, stop loss, and take profit levels.""",
            prompt_type=PromptType.FEW_SHOT,
            category=PromptCategory.TRADING,
            variables=["pair", "london_time", "newyork_time", "asia_range", "bias", "confidence"],
            examples=[
                {
                    "input": "GBPUSD, London: 03:00-12:00, NY: 08:00-17:00, Asia: 1.2650-1.2680",
                    "output": "Bullish bias - liquidity sweep below 1.2650, FVG at 1.2670..."
                }
            ],
            tags=["ict", "trading", "analysis"],
            temperature=0.6,
        )
        
        self.prompts["trading.react_pattern"] = Prompt(
            id="trading.react_pattern",
            name="ReAct Trading Decision Pattern",
            description="Thought + Action pattern for autonomous trading decisions",
            content="""You are a trading assistant using the ReAct (Reasoning + Acting) pattern.

For each user query, respond with JSON containing your thought process and action:

{
  "thought": "Analysis of the situation and next step reasoning",
  "action": {"command": "command_name", "args": {...}},
  "observation": "Results from previous action (filled automatically)"
}

Available commands:
| Command | Args | Description |
|---------|------|-------------|
| check_calendar | session | Check economic calendar for ${session} |
| analyze_chart | pair, timeframe | Technical analysis of ${pair} on ${timeframe} |
| check_correlations | pair | Check correlated pairs and indices |
| place_order | type, pair, entry, sl, tp | Execute trade |
| update_journal | setup, result | Log trade to journal |
| get_bias | pair | Retrieve current bias from memory |

Continue generating thoughts and actions until you reach a conclusion.

Example:
User: "Should I take a long on GBPUSD?"

{
  "thought": "I need to check current market structure and bias first",
  "action": {"command": "get_bias", "args": {"pair": "GBPUSD"}}
}

{
  "observation": "Current bias: Bullish above 1.2650, targeting 1.2720"
}

{
  "thought": "Bias is bullish. Now checking for confluence with economic calendar",
  "action": {"command": "check_calendar", "args": {"session": "london"}}
}

{
  "observation": "No high-impact news in next 4 hours"
}

{
  "thought": "Bias aligned, no news conflict. Checking technical structure",
  "action": {"command": "analyze_chart", "args": {"pair": "GBPUSD", "timeframe": "15m"}}
}

{
  "answer": "Yes - take long at 1.2665 (order block), SL: 1.2645, TP: 1.2710"
}""",
            prompt_type=PromptType.REACT,
            category=PromptCategory.TRADING,
            tags=["react", "autonomous", "trading"],
            temperature=0.4,
        )
        
        # =====================================================================
        # CODE GENERATION PROMPTS
        # =====================================================================
        
        self.prompts["code.python_expert"] = Prompt(
            id="code.python_expert",
            name="Python Expert System",
            description="Expert Python developer for code generation",
            content="""Act as a Senior Python Developer with 15+ years of experience.

Your specializations:
- Clean, idiomatic Python (PEP 8)
- FastAPI and async programming
- Type hints and Pydantic models
- Testing (pytest)
- Performance optimization

When writing code:
1. Use type hints for all functions
2. Add docstrings (Google style)
3. Handle errors gracefully
4. Include logging where appropriate
5. Follow SOLID principles
6. Write testable code

Provide code examples and explain trade-offs.""",
            prompt_type=PromptType.ROLE_PLAY,
            category=PromptCategory.CODE_GENERATION,
            tags=["python", "coding", "expert"],
            temperature=0.3,
        )
        
        self.prompts["code.structured_output"] = Prompt(
            id="code.structured_output",
            name="Structured JSON Output",
            description="Generate structured JSON responses",
            content="""Generate your response as valid JSON matching this schema:

{
  "summary": "Brief summary of the analysis",
  "details": {
    "findings": ["Finding 1", "Finding 2", ...],
    "recommendations": ["Rec 1", "Rec 2", ...],
    "risks": ["Risk 1", "Risk 2", ...]
  },
  "confidence": 0.85,
  "next_steps": ["Step 1", "Step 2", ...]
}

Rules:
- Output ONLY valid JSON, no markdown
- Do not include explanations outside the JSON
- Use null for missing optional fields
- Confidence should be 0.0 to 1.0""",
            prompt_type=PromptType.STRUCTURED,
            category=PromptCategory.CODE_GENERATION,
            tags=["json", "structured", "format"],
            temperature=0.2,
        )
        
        # =====================================================================
        # ANALYSIS & DEBUGGING PROMPTS
        # =====================================================================
        
        self.prompts["debug.systematic_approach"] = Prompt(
            id="debug.systematic_approach",
            name="Systematic Debugging",
            description="Step-by-step debugging methodology",
            content="""Debug the following issue systematically:

**Error**: ${error_message}
**Code**: ${code_snippet}
**Attempted Solutions**: ${attempts}

**Debugging Process**:

1. **Understand the Error**:
   - Parse error message
   - Identify error type and location
   - Understand expected vs actual behavior

2. **Root Cause Analysis**:
   - Trace execution flow
   - Identify where things go wrong
   - Consider edge cases

3. **Solution**:
   - Provide corrected code
   - Explain why original failed
   - Show how fix addresses root cause

4. **Prevention**:
   - Recommend tests to catch this
   - Suggest defensive coding practices
   - Identify similar potential issues

5. **Best Practices**:
   - How to avoid this pattern in future
   - Related concepts to study""",
            prompt_type=PromptType.CHAIN_OF_THOUGHT,
            category=PromptCategory.DEBUGGING,
            variables=["error_message", "code_snippet", "attempts"],
            tags=["debugging", "systematic", "cot"],
            temperature=0.3,
        )
        
        # =====================================================================
        # SUMMARIZATION PROMPTS
        # =====================================================================
        
        self.prompts["summary.executive_brief"] = Prompt(
            id="summary.executive_brief",
            name="Executive Summary",
            description="Generate concise executive summaries",
            content="""Create an executive summary of the following content:

${content}

**Summary Format**:

## Executive Summary
[2-3 sentence overview]

## Key Findings
- Finding 1
- Finding 2
- Finding 3

## Critical Actions Required
1. Action item 1 (Priority: High/Med/Low)
2. Action item 2
3. Action item 3

## Risks & Mitigation
- Risk 1: [Mitigation]
- Risk 2: [Mitigation]

## Bottom Line
[One sentence takeaway]

Keep total length under 200 words.""",
            prompt_type=PromptType.TASK,
            category=PromptCategory.SUMMARIZATION,
            variables=["content"],
            tags=["summary", "executive", "concise"],
            temperature=0.5,
        )
    
    def get(self, prompt_id: str, **variables) -> Optional[str]:
        """
        Get a prompt by ID and fill in variables.
        
        Args:
            prompt_id: Prompt identifier
            **variables: Variables to substitute (${var} syntax)
        
        Returns:
            Formatted prompt string or None
        """
        if prompt_id not in self.prompts:
            return None
        
        prompt = self.prompts[prompt_id]
        content = prompt.content
        
        # Substitute variables
        for var_name, var_value in variables.items():
            content = content.replace(f"${{{var_name}}}", str(var_value))
        
        return content
    
    def search(
        self,
        category: Optional[PromptCategory] = None,
        prompt_type: Optional[PromptType] = None,
        tags: Optional[List[str]] = None,
        query: Optional[str] = None,
    ) -> List[Prompt]:
        """
        Search prompts by criteria.
        
        Args:
            category: Filter by category
            prompt_type: Filter by type
            tags: Filter by tags (any match)
            query: Search in name/description
        
        Returns:
            List of matching prompts
        """
        results = list(self.prompts.values())
        
        if category:
            results = [p for p in results if p.category == category]
        
        if prompt_type:
            results = [p for p in results if p.prompt_type == prompt_type]
        
        if tags:
            results = [p for p in results if any(tag in p.tags for tag in tags)]
        
        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if query_lower in p.name.lower() or query_lower in p.description.lower()
            ]
        
        return results
    
    def list_categories(self) -> List[str]:
        """List all available categories."""
        return [cat.value for cat in PromptCategory]
    
    def list_types(self) -> List[str]:
        """List all available prompt types."""
        return [pt.value for pt in PromptType]
    
    def export_to_yaml(self, output_path: Path):
        """Export all prompts to a YAML file."""
        export_data = {
            "version": "1.0",
            "prompts": []
        }
        
        for prompt in self.prompts.values():
            export_data["prompts"].append({
                "id": prompt.id,
                "name": prompt.name,
                "description": prompt.description,
                "content": prompt.content,
                "type": prompt.prompt_type.value,
                "category": prompt.category.value,
                "variables": prompt.variables,
                "examples": prompt.examples,
                "tags": prompt.tags,
                "version": prompt.version,
                "model_hint": prompt.model_hint,
                "temperature": prompt.temperature,
                "max_tokens": prompt.max_tokens,
            })
        
        with open(output_path, 'w') as f:
            yaml.dump(export_data, f, default_flow_style=False, sort_keys=False)


# Global instance
_library = None


def get_prompt_library() -> PromptLibrary:
    """Get the global prompt library instance."""
    global _library
    if _library is None:
        _library = PromptLibrary()
    return _library


# Convenience functions
def get_prompt(prompt_id: str, **variables) -> Optional[str]:
    """Quick access to get a prompt."""
    return get_prompt_library().get(prompt_id, **variables)


def search_prompts(
    category: Optional[str] = None,
    prompt_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> List[Prompt]:
    """Quick search for prompts."""
    lib = get_prompt_library()
    cat = PromptCategory(category) if category else None
    ptype = PromptType(prompt_type) if prompt_type else None
    return lib.search(category=cat, prompt_type=ptype, tags=tags)


if __name__ == "__main__":
    # Example usage
    lib = get_prompt_library()
    
    # Get a prompt with variables
    cad_prompt = lib.get("engineering.chain_of_thought_validation", component_type="weldment")
    print(f"CAD Validation Prompt:\n{cad_prompt}\n")
    
    # Search for trading prompts
    trading_prompts = lib.search(category=PromptCategory.TRADING)
    print(f"Found {len(trading_prompts)} trading prompts")
    
    # Export to YAML
    lib.export_to_yaml(Path("/tmp/prompts_export.yaml"))
    print("✅ Exported prompts to YAML")
