"""
Prompt Library Integration Examples
====================================

Shows how to use the new prompt library in existing Project Vulcan agents.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.prompt_library import (
    get_prompt_library,
    get_prompt,
    search_prompts,
    PromptCategory,
    PromptType,
)
from core.llm import llm


def example_cad_validation():
    """Example: Use chain-of-thought validation prompt for CAD."""
    
    # Get the prompt with variables filled in
    validation_prompt = get_prompt(
        "engineering.chain_of_thought_validation",
        component_type="pressure vessel nozzle weldment"
    )
    
    # Use with LLM
    response = llm.generate(
        messages=[{"role": "user", "content": "Validate the attached design"}],
        system=validation_prompt,
        agent_type="cad"
    )
    
    print(f"CAD Validation:\n{response}\n")


def example_trading_analysis():
    """Example: Use ICT analysis prompt for trading."""
    
    # Get trading prompt with session times
    analysis_prompt = get_prompt(
        "trading.ict_analysis",
        pair="GBPUSD",
        london_time="03:00-12:00 EST",
        newyork_time="08:00-17:00 EST",
        asia_range="1.2650-1.2680",
        bias="Bullish",
        confidence="8"
    )
    
    # Use with LLM
    response = llm.generate(
        messages=[{"role": "user", "content": "Analyze current market structure"}],
        system=analysis_prompt,
        agent_type="trading"
    )
    
    print(f"Trading Analysis:\n{response}\n")


def example_react_pattern():
    """Example: Use ReAct pattern for autonomous trading decisions."""
    
    # Get ReAct prompt
    react_prompt = get_prompt("trading.react_pattern")
    
    # Simulate ReAct loop
    user_query = "Should I take a long on EURUSD right now?"
    
    # First thought/action
    response = llm.generate(
        messages=[{"role": "user", "content": user_query}],
        system=react_prompt,
        agent_type="trading"
    )
    
    print(f"ReAct Decision Process:\n{response}\n")


def example_code_generation():
    """Example: Generate FastAPI endpoint using prompt library."""
    
    # Get code generation prompt
    endpoint_prompt = get_prompt(
        "code.fastapi_endpoint",
        endpoint_description="Create a new CAD validation task",
        path="/api/validations",
        method="POST",
        request_model="ValidationRequest",
        response_model="ValidationResponse",
        auth_required="Yes (API key)"
    )
    
    response = llm.generate(
        messages=[{"role": "user", "content": "Generate the endpoint code"}],
        system=endpoint_prompt,
        model="claude-sonnet-4",
        temperature=0.3,
    )
    
    print(f"Generated Code:\n{response}\n")


def example_search_prompts():
    """Example: Search for prompts by category."""
    
    lib = get_prompt_library()
    
    # Find all engineering prompts
    engineering_prompts = lib.search(category=PromptCategory.ENGINEERING)
    print(f"\nEngineering Prompts ({len(engineering_prompts)}):")
    for p in engineering_prompts:
        print(f"  - {p.id}: {p.name}")
    
    # Find all chain-of-thought prompts
    cot_prompts = lib.search(prompt_type=PromptType.CHAIN_OF_THOUGHT)
    print(f"\nChain-of-Thought Prompts ({len(cot_prompts)}):")
    for p in cot_prompts:
        print(f"  - {p.id}: {p.name}")
    
    # Find prompts by tag
    validation_prompts = lib.search(tags=["validation"])
    print(f"\nValidation Prompts ({len(validation_prompts)}):")
    for p in validation_prompts:
        print(f"  - {p.id}: {p.name}")


def example_custom_agent_integration():
    """Example: Integrate prompt library into a custom agent."""
    
    class CustomCADAgent:
        def __init__(self):
            self.library = get_prompt_library()
        
        def validate_design(self, component_type: str, design_data: dict):
            \"\"\"Validate a design using library prompts.\"\"\"
            
            # Get appropriate validation prompt
            validation_prompt = self.library.get(
                "engineering.chain_of_thought_validation",
                component_type=component_type
            )
            
            # Build context
            context = f\"\"\"
            Component: {component_type}
            
            Design Data:
            {design_data}
            \"\"\"
            
            # Run validation
            result = llm.generate(
                messages=[{"role": "user", "content": context}],
                system=validation_prompt,
                agent_type="cad",
                temperature=0.3,
            )
            
            return result
        
        def analyze_drawing(self, drawing_type: str, requirements: str):
            \"\"\"Analyze a technical drawing.\"\"\"
            
            prompt = self.library.get(
                "engineering.drawing_analyzer",
                drawing_type=drawing_type,
                specific_requirements=requirements
            )
            
            result = llm.generate(
                messages=[{"role": "user", "content": "Analyze the attached drawing"}],
                system=prompt,
                agent_type="cad"
            )
            
            return result
    
    # Use the agent
    agent = CustomCADAgent()
    
    validation_result = agent.validate_design(
        component_type="weldment",
        design_data={"material": "A36", "thickness": "0.5in", "welds": "fillet 1/4\""}
    )
    
    print(f"Custom Agent Validation:\n{validation_result}\n")


def example_export_prompts():
    """Example: Export all prompts to YAML for backup."""
    
    lib = get_prompt_library()
    output_path = Path(__file__).parent.parent / "data" / "prompts" / "exported_prompts.yaml"
    
    lib.export_to_yaml(output_path)
    print(f"✅ Exported all prompts to: {output_path}")


if __name__ == "__main__":
    print("=" * 70)
    print("PROMPT LIBRARY INTEGRATION EXAMPLES")
    print("=" * 70)
    
    # Run examples (commented out to avoid API calls during demo)
    # Uncomment to test
    
    # print("\n1. CAD Validation Example:")
    # example_cad_validation()
    
    # print("\n2. Trading Analysis Example:")
    # example_trading_analysis()
    
    # print("\n3. ReAct Pattern Example:")
    # example_react_pattern()
    
    # print("\n4. Code Generation Example:")
    # example_code_generation()
    
    print("\n5. Search Prompts Example:")
    example_search_prompts()
    
    # print("\n6. Custom Agent Integration Example:")
    # example_custom_agent_integration()
    
    print("\n7. Export Prompts Example:")
    example_export_prompts()
    
    print("\n" + "=" * 70)
    print("✅ Examples completed!")
    print("=" * 70)
