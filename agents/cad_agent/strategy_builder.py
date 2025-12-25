"""
Strategy Builder Service - Phase 20 Task 18

LLM-powered service to CREATE new strategies from user prompts.
Uses Claude/GPT-4 with product schema as context.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger("cad_agent.strategy_builder")


class StrategyBuilder:
    """
    LLM-powered strategy creation service.

    Takes user prompts like:
    - "Design a weldment for a 10-ton overhead crane support beam"
    - "Create a sheet metal enclosure 400x300x200mm"
    - "Build a machined adapter plate for 6-inch flange"

    Returns a complete strategy JSON matching the product schema.
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy load Anthropic client."""
        if self._client is None:
            try:
                import anthropic

                self._client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
            except ImportError:
                logger.error("anthropic package not installed")
                raise
        return self._client

    def _get_schema_context(self) -> str:
        """Get product schema documentation for LLM context."""
        return """
## Product Schema Reference

### ProductType (Enum)
- weldment: Structural steel, tube frames, I-beams
- sheet_metal: Bent sheet metal parts, enclosures, brackets
- machining: CNC milled/turned parts, adapters, plates
- assembly: Multi-component assemblies with mates
- solid: General solid parts

### Core Objects

#### MaterialSpec
```json
{
  "name": "ASTM A36",     // Standard name
  "grade": "Structural",  // specific grade
  "density": 7850,        // kg/m^3
  "yield_strength": 250,  // MPa
  "tensile_strength": 400 // MPa
}
```

#### Dimension
```json
{
  "value": 10.0,
  "unit": "mm",  // or "in"
  "tolerance_plus": 0.1,
  "tolerance_minus": 0.1
}
```

### Required Fields
- name: Descriptive part name (string)
- product_type: One of the ProductType values
- description: clear functional description
- material: MaterialSpec object

### WeldmentStrategy Fields
- structural_members: List of objects:
  - profile: "ISO 20x20x2" (string)
  - length: Dimension object
  - orientation: {x,y,z} vector
- weld_joints: List of objects:
  - type: "fillet" | "butt"
  - size: Dimension object
  - standard: "AWS D1.1"
- cut_list: List of cut instructions

### SheetMetalStrategy Fields
- thickness: Dimension object
- bend_radius: Dimension object
- k_factor: float (default 0.44)
- bends: List of objects:
  - angle: float (degrees)
  - radius: Dimension object
  - direction: "up" | "down"

### MachiningStrategy Fields
- stock_size: {x: float, y: float, z: float} (mm)
- operations: List of strings e.g. ["face", "drill_m6", "contour"]
- tooling: List of tool names
- setup_count: int

### Common Fields
- features: List of feature objects (extrude, cut, hole)
- constraints: List of design constraints
"""

    def _get_system_prompt(self) -> str:
        """Build system prompt for strategy generation."""
        # Try to get from prompt library first
        library_prompt = get_prompt("engineering.cad_expert")
        if library_prompt:
            base_prompt = library_prompt
        else:
            base_prompt = "You are a Senior Mechanical Engineer with 20+ years of CAD experience."
        
        return f"""{base_prompt}
        
Your task is to create detailed, manufacturable CAD strategies from user descriptions.

{self._get_schema_context()}

## Rules
1. Output ONLY valid JSON matching the schema - no markdown, no explanation
2. Use realistic engineering values (dimensions, tolerances, materials)
3. Include all required fields
4. Add appropriate constraints with standards references (ASME, AWS, AISC)
5. Include cut lists for weldments, flat patterns for sheet metal
6. Estimate machining times based on typical CNC operations
7. Use standard materials (ASTM A36 for steel, 6061-T6 for aluminum, etc.)
8. Set is_experimental: true for new untested strategies

## Example Output Format
{{
  "name": "Part Name",
  "product_type": "weldment",
  "description": "...",
  "material": {{"name": "ASTM A36", "density": 7850, ...}},
  ...
}}
"""

    async def create_from_description(
        self,
        user_prompt: str,
        product_type: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Generate a strategy from a user description.

        Args:
            user_prompt: Natural language description of the part
            product_type: Optional hint for product type
            context: Optional additional context (standards, constraints)

        Returns:
            Complete strategy JSON matching product schema
        """
        client = self._get_client()

        # Build the prompt
        prompt_parts = [user_prompt]

        if product_type:
            prompt_parts.append(f"\nProduct type: {product_type}")

        if context:
            if "standards" in context:
                prompt_parts.append(
                    f"\nApplicable standards: {', '.join(context['standards'])}"
                )
            if "constraints" in context:
                prompt_parts.append(
                    f"\nConstraints: {json.dumps(context['constraints'])}"
                )
            if "material" in context:
                prompt_parts.append(f"\nPreferred material: {context['material']}")

        full_prompt = "\n".join(prompt_parts)

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self._get_system_prompt(),
                messages=[{"role": "user", "content": full_prompt}],
            )

            # Extract JSON from response
            content = response.content[0].text.strip()

            # Clean up if wrapped in markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            strategy = json.loads(content)

            # Add metadata
            strategy["created_at"] = datetime.utcnow().isoformat()
            strategy["created_by"] = "strategy_builder"
            strategy["is_experimental"] = True  # New strategies are experimental

            logger.info(f"Created strategy: {strategy.get('name', 'unnamed')}")
            return strategy

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise ValueError(f"Invalid strategy JSON: {e}")
        except Exception as e:
            logger.error(f"Strategy creation failed: {e}")
            raise

    async def create_from_example(
        self, existing_part: Dict[str, Any], modifications: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new strategy based on an existing part.

        Args:
            existing_part: Existing strategy/part to use as template
            modifications: Description of changes to make

        Returns:
            New strategy based on the example
        """
        client = self._get_client()

        prompt = f"""Based on this existing part:
```json
{json.dumps(existing_part, indent=2)}
```

{"Create a modified version with: " + modifications if modifications else "Create a similar but distinct variant."}

Output the complete new strategy as JSON.
"""

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self._get_system_prompt(),
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            strategy = json.loads(content)
            strategy["created_at"] = datetime.utcnow().isoformat()
            strategy["created_by"] = "strategy_builder"
            strategy["is_experimental"] = True

            return strategy

        except Exception as e:
            logger.error(f"Failed to create strategy from example: {e}")
            raise

    def validate_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a strategy against the schema.

        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str]
            }
        """
        errors = []
        warnings = []

        # Required fields
        required = ["name", "product_type"]
        for field in required:
            if field not in strategy:
                errors.append(f"Missing required field: {field}")

        # Product type validation
        valid_types = [
            "weldment",
            "sheet_metal",
            "machining",
            "assembly",
            "solid",
            "casting",
        ]
        if strategy.get("product_type") not in valid_types:
            errors.append(f"Invalid product_type: {strategy.get('product_type')}")

        # Material validation
        if "material" not in strategy:
            warnings.append("No material specified")
        elif not isinstance(strategy["material"], dict):
            errors.append("Material must be an object")
        elif "name" not in strategy["material"]:
            warnings.append("Material name not specified")

        # Type-specific validation
        ptype = strategy.get("product_type")

        if ptype == "weldment":
            if not strategy.get("structural_members"):
                warnings.append("Weldment has no structural members defined")
            if not strategy.get("weld_joints"):
                warnings.append("Weldment has no weld joints defined")

        elif ptype == "sheet_metal":
            if not strategy.get("thickness"):
                errors.append("Sheet metal must have thickness defined")
            if not strategy.get("bends"):
                warnings.append("Sheet metal has no bends defined")

        elif ptype == "machining":
            if not strategy.get("stock_size"):
                warnings.append("Machining has no stock size defined")
            if not strategy.get("operations"):
                warnings.append("Machining has no operations defined")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    async def suggest_improvements(
        self, strategy: Dict[str, Any], performance_data: Optional[List[Dict]] = None
    ) -> List[str]:
        """
        Suggest improvements for a strategy based on performance data.

        Args:
            strategy: Current strategy
            performance_data: Historical performance records

        Returns:
            List of improvement suggestions
        """
        client = self._get_client()

        prompt_parts = [
            f"Analyze this CAD strategy and suggest improvements:",
            f"```json\n{json.dumps(strategy, indent=2)}\n```",
        ]

        if performance_data:
            # Summarize performance issues
            failures = [p for p in performance_data if not p.get("validation_passed")]
            if failures:
                error_summary = {}
                for f in failures:
                    for err in f.get("errors_json") or []:
                        err_type = err.get("type", "unknown")
                        error_summary[err_type] = error_summary.get(err_type, 0) + 1

                prompt_parts.append(f"\nPerformance Issues:")
                for err_type, count in error_summary.items():
                    prompt_parts.append(f"- {err_type}: {count} failures")

        prompt_parts.append(
            "\nProvide 3-5 specific, actionable improvements as a JSON array of strings."
        )

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": "\n".join(prompt_parts)}],
            )

            content = response.content[0].text.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            return json.loads(content)

        except Exception as e:
            logger.error(f"Failed to generate improvements: {e}")
            return [f"Error generating suggestions: {e}"]


# Singleton instance
_builder: Optional[StrategyBuilder] = None


def get_strategy_builder() -> StrategyBuilder:
    """Get or create strategy builder singleton."""
    global _builder
    if _builder is None:
        _builder = StrategyBuilder()
    return _builder


# Convenience functions
async def create_strategy(prompt: str, product_type: str = None) -> Dict[str, Any]:
    """Create a new strategy from a description."""
    builder = get_strategy_builder()
    return await builder.create_from_description(prompt, product_type)


def validate_strategy(strategy: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a strategy against the schema."""
    builder = get_strategy_builder()
    return builder.validate_strategy(strategy)
