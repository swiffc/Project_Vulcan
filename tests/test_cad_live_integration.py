"""
Live CAD Chatbot Integration Test
Simulates real user commands and tests end-to-end flow
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import directly
import importlib.util

def load_module_from_path(module_name: str, file_path: Path):
    """Load a module directly from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules
project_root = Path(__file__).parent.parent
prompt_lib = load_module_from_path("prompt_library", project_root / "core" / "prompt_library.py")
nlp_parser = load_module_from_path("cad_nlp_parser", project_root / "core" / "cad_nlp_parser.py")

PromptLibrary = prompt_lib.PromptLibrary
CADNLPParser = nlp_parser.CADNLPParser


@dataclass
class CADCommand:
    """Represents a parsed CAD command ready for execution."""
    tool_name: str
    parameters: Dict[str, Any]
    confidence: float
    warnings: List[str]


class CADChatbotSimulator:
    """Simulates the CAD chatbot pipeline."""
    
    def __init__(self, cad_software: str = "solidworks"):
        self.parser = CADNLPParser(cad_software)
        self.prompt_library = PromptLibrary()
        self.cad_software = cad_software
        self.conversation_history = []
        
    def process_user_command(self, user_input: str) -> Dict[str, Any]:
        """Process a user command through the full pipeline."""
        result = {
            "input": user_input,
            "parsed_dimensions": {},
            "material": None,
            "standard": None,
            "cad_commands": [],
            "system_prompt": "",
            "warnings": [],
            "errors": [],
            "success": False
        }
        
        try:
            # Step 1: Parse dimensions
            params = self.parser.parse(user_input)
            result["parsed_dimensions"] = {
                name: {
                    "value": p.value,
                    "unit": p.unit,
                    "type": p.parameter_type
                }
                for name, p in params.items()
            }
            
            # Step 2: Extract material
            material = self.parser.extract_material(user_input)
            if material:
                result["material"] = material
            
            # Step 3: Extract standard
            standard = self.parser.extract_standard(user_input)
            if standard:
                result["standard"] = standard
            
            # Step 4: Get appropriate prompt
            prompt = self._select_prompt(user_input)
            if prompt:
                result["system_prompt"] = prompt.content[:200] + "..."
            
            # Step 5: Generate CAD commands
            commands = self._generate_cad_commands(user_input, params, material, standard)
            result["cad_commands"] = commands
            
            # Step 6: Validate
            warnings = self._validate_commands(commands, params, material)
            result["warnings"] = warnings
            
            result["success"] = len(commands) > 0
            
        except Exception as e:
            result["errors"].append(str(e))
            result["success"] = False
        
        return result
    
    def _select_prompt(self, user_input: str) -> Optional[Any]:
        """Select appropriate prompt based on user input."""
        user_lower = user_input.lower()
        
        # Check for specific intents
        if any(word in user_lower for word in ["build", "create", "make", "design"]):
            if "part" in user_lower or "component" in user_lower:
                return self.prompt_library.get_prompt("engineering.cad_expert")
            elif "assembly" in user_lower:
                prompts = self.prompt_library.search_prompts(tags=["assembly"])
                return prompts[0] if prompts else None
        
        elif any(word in user_lower for word in ["validate", "check", "verify"]):
            return self.prompt_library.get_prompt("engineering.chain_of_thought_validation")
        
        # Default to CAD expert
        return self.prompt_library.get_prompt("engineering.cad_expert")
    
    def _generate_cad_commands(
        self, 
        user_input: str, 
        params: Dict, 
        material: Optional[str],
        standard: Optional[str]
    ) -> List[CADCommand]:
        """Generate CAD tool commands from parsed input."""
        commands = []
        user_lower = user_input.lower()
        
        # Detect intent
        if "flange" in user_lower:
            commands.extend(self._generate_flange_commands(params, material, standard))
        elif "bracket" in user_lower:
            commands.extend(self._generate_bracket_commands(params, material))
        elif "extrude" in user_lower:
            commands.extend(self._generate_extrude_commands(params))
        elif "sketch" in user_lower:
            commands.extend(self._generate_sketch_commands(params))
        elif "assembly" in user_lower:
            commands.extend(self._generate_assembly_commands(params))
        else:
            # Generic part creation
            commands.extend(self._generate_generic_part_commands(params, material))
        
        return commands
    
    def _generate_flange_commands(
        self, 
        params: Dict, 
        material: Optional[str],
        standard: Optional[str]
    ) -> List[CADCommand]:
        """Generate commands to build a flange."""
        commands = []
        
        # Command 1: Connect to CAD
        commands.append(CADCommand(
            tool_name="sw_connect" if self.cad_software == "solidworks" else "inv_connect",
            parameters={},
            confidence=1.0,
            warnings=[]
        ))
        
        # Command 2: New part
        commands.append(CADCommand(
            tool_name="sw_new_part" if self.cad_software == "solidworks" else "inv_new_part",
            parameters={},
            confidence=1.0,
            warnings=[]
        ))
        
        # Command 3: Create sketch on Front plane
        commands.append(CADCommand(
            tool_name="sw_create_sketch" if self.cad_software == "solidworks" else "inv_create_sketch",
            parameters={"plane": "Front"},
            confidence=0.9,
            warnings=[]
        ))
        
        # Command 4: Sketch circle (outer diameter)
        diameter_param = None
        for name, param in params.items():
            if "diameter" in name.lower():
                diameter_param = param
                break
        
        if diameter_param:
            commands.append(CADCommand(
                tool_name="sw_sketch_circle" if self.cad_software == "solidworks" else "inv_sketch_circle",
                parameters={
                    "center_x": 0.0,
                    "center_y": 0.0,
                    "radius": diameter_param.value / 2
                },
                confidence=0.95,
                warnings=[]
            ))
        else:
            commands.append(CADCommand(
                tool_name="sw_sketch_circle",
                parameters={
                    "center_x": 0.0,
                    "center_y": 0.0,
                    "radius": 0.1  # Default 200mm OD
                },
                confidence=0.5,
                warnings=["No diameter specified, using default 200mm"]
            ))
        
        # Command 5: Extrude
        thickness_param = None
        for name, param in params.items():
            if "thick" in name.lower():
                thickness_param = param
                break
        
        if thickness_param:
            commands.append(CADCommand(
                tool_name="sw_extrude" if self.cad_software == "solidworks" else "inv_extrude",
                parameters={
                    "depth": thickness_param.value,
                    "direction": "blind"
                },
                confidence=0.95,
                warnings=[]
            ))
        else:
            commands.append(CADCommand(
                tool_name="sw_extrude",
                parameters={
                    "depth": 0.025,  # Default 25mm thick
                    "direction": "blind"
                },
                confidence=0.5,
                warnings=["No thickness specified, using default 25mm"]
            ))
        
        # Command 6: Set material
        if material:
            commands.append(CADCommand(
                tool_name="sw_set_material" if self.cad_software == "solidworks" else "inv_set_material",
                parameters={"material": material},
                confidence=0.9,
                warnings=[]
            ))
        
        # Command 7: Save
        commands.append(CADCommand(
            tool_name="sw_save_part" if self.cad_software == "solidworks" else "inv_save_part",
            parameters={"name": "flange.sldprt"},
            confidence=0.8,
            warnings=[]
        ))
        
        return commands
    
    def _generate_bracket_commands(self, params: Dict, material: Optional[str]) -> List[CADCommand]:
        """Generate commands for bracket."""
        commands = []
        
        commands.append(CADCommand(
            tool_name="sw_connect",
            parameters={},
            confidence=1.0,
            warnings=[]
        ))
        
        commands.append(CADCommand(
            tool_name="sw_new_part",
            parameters={},
            confidence=1.0,
            warnings=[]
        ))
        
        # Bracket-specific operations
        commands.append(CADCommand(
            tool_name="sw_create_sketch",
            parameters={"plane": "Front"},
            confidence=0.9,
            warnings=["Bracket design may require multiple sketches"]
        ))
        
        return commands
    
    def _generate_extrude_commands(self, params: Dict) -> List[CADCommand]:
        """Generate extrude commands."""
        commands = []
        
        depth_param = None
        for name, param in params.items():
            if any(word in name.lower() for word in ["depth", "length", "thick"]):
                depth_param = param
                break
        
        if depth_param:
            commands.append(CADCommand(
                tool_name="sw_extrude",
                parameters={
                    "depth": depth_param.value,
                    "direction": "blind"
                },
                confidence=0.9,
                warnings=[]
            ))
        else:
            commands.append(CADCommand(
                tool_name="sw_extrude",
                parameters={},
                confidence=0.3,
                warnings=["No depth specified for extrude"]
            ))
        
        return commands
    
    def _generate_sketch_commands(self, params: Dict) -> List[CADCommand]:
        """Generate sketch commands."""
        return [
            CADCommand(
                tool_name="sw_create_sketch",
                parameters={"plane": "Front"},
                confidence=0.8,
                warnings=["Plane selection may need adjustment"]
            )
        ]
    
    def _generate_assembly_commands(self, params: Dict) -> List[CADCommand]:
        """Generate assembly commands."""
        return [
            CADCommand(
                tool_name="sw_new_assembly",
                parameters={},
                confidence=0.9,
                warnings=["Assembly requires component files"]
            )
        ]
    
    def _generate_generic_part_commands(self, params: Dict, material: Optional[str]) -> List[CADCommand]:
        """Generate generic part creation commands."""
        commands = []
        
        commands.append(CADCommand(
            tool_name="sw_connect",
            parameters={},
            confidence=1.0,
            warnings=[]
        ))
        
        commands.append(CADCommand(
            tool_name="sw_new_part",
            parameters={},
            confidence=1.0,
            warnings=[]
        ))
        
        if params:
            commands.append(CADCommand(
                tool_name="sw_create_sketch",
                parameters={"plane": "Front"},
                confidence=0.7,
                warnings=["Generic part creation - may need more specifics"]
            ))
        
        return commands
    
    def _validate_commands(
        self, 
        commands: List[CADCommand], 
        params: Dict,
        material: Optional[str]
    ) -> List[str]:
        """Validate generated commands."""
        warnings = []
        
        # Check for missing dimensions
        if not params:
            warnings.append("⚠️ No dimensions provided - using defaults")
        
        # Check for material
        if not material:
            warnings.append("⚠️ No material specified")
        
        # Check command sequence
        tool_names = [cmd.tool_name for cmd in commands]
        
        if "sw_connect" not in tool_names and "inv_connect" not in tool_names:
            warnings.append("⚠️ Missing connection command")
        
        if "sw_save_part" not in tool_names and "inv_save_part" not in tool_names:
            warnings.append("⚠️ Part won't be saved")
        
        # Check for low confidence commands
        low_confidence = [cmd for cmd in commands if cmd.confidence < 0.7]
        if low_confidence:
            warnings.append(f"⚠️ {len(low_confidence)} commands have low confidence")
        
        return warnings


def run_live_tests():
    """Run live integration tests with realistic user commands."""
    
    print("\n" + "="*80)
    print("🤖 CAD CHATBOT LIVE INTEGRATION TEST")
    print("="*80 + "\n")
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Simple Flange",
            "command": "Build a 6 inch flange, quarter inch thick, A105 material",
            "expected_tools": ["sw_connect", "sw_new_part", "sw_sketch_circle", "sw_extrude", "sw_set_material"]
        },
        {
            "name": "ASME Flange with Standard",
            "command": "Create a 150# RFWN flange per ASME B16.5, 8 inch diameter, 316SS",
            "expected_tools": ["sw_connect", "sw_new_part", "sw_extrude"]
        },
        {
            "name": "Sheet Metal Bracket",
            "command": "Design a bracket 100mm x 50mm, 3mm thick aluminum",
            "expected_tools": ["sw_connect", "sw_new_part", "sw_create_sketch"]
        },
        {
            "name": "Extrude Command",
            "command": "Extrude the current sketch 25mm",
            "expected_tools": ["sw_extrude"]
        },
        {
            "name": "Pipe Nozzle",
            "command": "Build a 2 inch sch 40 nozzle, 8 inches long, carbon steel per B31.3",
            "expected_tools": ["sw_connect", "sw_new_part"]
        },
        {
            "name": "Minimal Input",
            "command": "Create a part",
            "expected_tools": ["sw_connect", "sw_new_part"]
        },
        {
            "name": "Assembly Request",
            "command": "Create an assembly with 4 bolts",
            "expected_tools": ["sw_new_assembly"]
        },
        {
            "name": "Complex Weldment",
            "command": "Design a structural frame with 4 inch square tube, 3/8 wall, 10 feet long per AWS D1.1",
            "expected_tools": ["sw_connect", "sw_new_part"]
        },
        {
            "name": "Sketch Only",
            "command": "Create a sketch on the front plane",
            "expected_tools": ["sw_create_sketch"]
        },
        {
            "name": "Imperial Units",
            "command": "Make a flange 12 inches diameter, 1.5 inches thick",
            "expected_tools": ["sw_sketch_circle", "sw_extrude"]
        },
    ]
    
    simulator = CADChatbotSimulator("solidworks")
    
    passed = 0
    failed = 0
    total_commands = 0
    total_warnings = 0
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}/{len(test_scenarios)}: {scenario['name']}")
        print(f"{'─'*80}")
        print(f"User: \"{scenario['command']}\"")
        print()
        
        result = simulator.process_user_command(scenario['command'])
        
        # Display parsed information
        print("📊 PARSED DATA:")
        if result["parsed_dimensions"]:
            print(f"  Dimensions: {len(result['parsed_dimensions'])} found")
            for name, data in result["parsed_dimensions"].items():
                print(f"    • {name}: {data['value']:.4f} {data['unit']} ({data['type']})")
        else:
            print("  Dimensions: None")
        
        if result["material"]:
            print(f"  Material: {result['material']}")
        if result["standard"]:
            print(f"  Standard: {result['standard']}")
        
        # Display generated commands
        print(f"\n🔧 GENERATED COMMANDS: {len(result['cad_commands'])}")
        for cmd in result["cad_commands"]:
            confidence_emoji = "✅" if cmd.confidence >= 0.8 else "🟡" if cmd.confidence >= 0.6 else "🔴"
            print(f"  {confidence_emoji} {cmd.tool_name}({json.dumps(cmd.parameters, indent=None)})")
            print(f"     Confidence: {cmd.confidence*100:.0f}%")
            if cmd.warnings:
                for warning in cmd.warnings:
                    print(f"     ⚠️ {warning}")
        
        # Display warnings
        if result["warnings"]:
            print(f"\n⚠️ VALIDATION WARNINGS: {len(result['warnings'])}")
            for warning in result["warnings"]:
                print(f"  {warning}")
            total_warnings += len(result["warnings"])
        
        # Display errors
        if result["errors"]:
            print(f"\n❌ ERRORS:")
            for error in result["errors"]:
                print(f"  {error}")
        
        # Check if expected tools were generated
        generated_tools = [cmd.tool_name for cmd in result["cad_commands"]]
        expected_found = sum(1 for tool in scenario["expected_tools"] if tool in generated_tools)
        
        if result["success"] and expected_found > 0:
            print(f"\n✅ TEST PASSED ({expected_found}/{len(scenario['expected_tools'])} expected tools found)")
            passed += 1
        else:
            print(f"\n❌ TEST FAILED (only {expected_found}/{len(scenario['expected_tools'])} expected tools found)")
            failed += 1
        
        total_commands += len(result["cad_commands"])
    
    # Summary
    print("\n" + "="*80)
    print("📈 TEST SUMMARY")
    print("="*80)
    print(f"Tests Passed: {passed}/{len(test_scenarios)} ({passed/len(test_scenarios)*100:.1f}%)")
    print(f"Tests Failed: {failed}/{len(test_scenarios)}")
    print(f"Total Commands Generated: {total_commands}")
    print(f"Total Warnings: {total_warnings}")
    print(f"Average Commands per Test: {total_commands/len(test_scenarios):.1f}")
    print("="*80)
    
    return passed == len(test_scenarios)


if __name__ == "__main__":
    success = run_live_tests()
    sys.exit(0 if success else 1)
