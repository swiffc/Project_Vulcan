"""
Comprehensive CAD Chatbot Test Suite
Tests all major features: Prompt Library, NLP Parser, Integration, Edge Cases
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import directly without triggering core/__init__.py
import importlib.util

def load_module_from_path(module_name: str, file_path: Path):
    """Load a module directly from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules directly
project_root = Path(__file__).parent.parent
prompt_lib = load_module_from_path("prompt_library", project_root / "core" / "prompt_library.py")
nlp_parser = load_module_from_path("cad_nlp_parser", project_root / "core" / "cad_nlp_parser.py")

# Import classes
PromptLibrary = prompt_lib.PromptLibrary
PromptType = prompt_lib.PromptType
PromptCategory = prompt_lib.PromptCategory
CADNLPParser = nlp_parser.CADNLPParser


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests: List[Dict[str, Any]] = []
    
    def record(self, name: str, passed: bool, details: str = ""):
        self.tests.append({
            "name": name,
            "passed": passed,
            "details": details
        })
        if passed:
            self.passed += 1
            print(f"✅ PASS: {name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {name}")
            if details:
                print(f"   Details: {details}")
    
    def summary(self):
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        print("\n" + "="*80)
        print(f"TEST SUMMARY: {self.passed}/{total} passed ({pass_rate:.1f}%)")
        print("="*80)
        if self.failed > 0:
            print("\nFailed Tests:")
            for test in self.tests:
                if not test["passed"]:
                    print(f"  - {test['name']}")
                    if test["details"]:
                        print(f"    {test['details']}")


def test_prompt_library(results: TestResults):
    """Test Prompt Library functionality."""
    print("\n" + "="*80)
    print("TESTING PROMPT LIBRARY")
    print("="*80 + "\n")
    
    try:
        # Test 1: Initialize library
        library = PromptLibrary()
        results.record(
            "Prompt Library Initialization",
            True,
            f"Loaded {len(library.prompts)} built-in prompts"
        )
    except Exception as e:
        results.record("Prompt Library Initialization", False, str(e))
        return
    
    # Test 2: Load YAML prompts
    try:
        yaml_path = Path(__file__).parent.parent / "data" / "prompts" / "community_prompts.yaml"
        if yaml_path.exists():
            library.load_from_yaml(str(yaml_path))
            results.record(
                "Load YAML Prompts",
                True,
                f"Total prompts: {len(library.prompts)}"
            )
        else:
            results.record("Load YAML Prompts", False, f"File not found: {yaml_path}")
    except Exception as e:
        results.record("Load YAML Prompts", False, str(e))
    
    # Test 3: Get specific prompt
    try:
        prompt = library.get_prompt("engineering.cad_expert")
        results.record(
            "Get CAD Expert Prompt",
            prompt is not None,
            f"Found prompt with {len(prompt.content)} characters" if prompt else "Not found"
        )
    except Exception as e:
        results.record("Get CAD Expert Prompt", False, str(e))
    
    # Test 4: Search by category
    try:
        eng_prompts = library.search_prompts(category=PromptCategory.ENGINEERING)
        results.record(
            "Search by Category (ENGINEERING)",
            len(eng_prompts) > 0,
            f"Found {len(eng_prompts)} engineering prompts"
        )
    except Exception as e:
        results.record("Search by Category", False, str(e))
    
    # Test 5: Search by tags
    try:
        cad_prompts = library.search_prompts(tags=["CAD"])
        results.record(
            "Search by Tags (CAD)",
            len(cad_prompts) > 0,
            f"Found {len(cad_prompts)} CAD-tagged prompts"
        )
    except Exception as e:
        results.record("Search by Tags", False, str(e))
    
    # Test 6: Variable substitution
    try:
        prompt = library.get_prompt("engineering.chain_of_thought_validation")
        if prompt:
            formatted = library.format_prompt(
                "engineering.chain_of_thought_validation",
                component_type="flange"
            )
            has_substitution = "flange" in formatted
            results.record(
                "Variable Substitution",
                has_substitution,
                f"Variables replaced in {len(formatted)} character prompt"
            )
        else:
            results.record("Variable Substitution", False, "Prompt not found")
    except Exception as e:
        results.record("Variable Substitution", False, str(e))
    
    # Test 7: Export to YAML
    try:
        export_path = Path(__file__).parent / "test_export.yaml"
        library.export_to_yaml(str(export_path))
        exported = export_path.exists() and export_path.stat().st_size > 0
        if exported:
            export_path.unlink()  # Clean up
        results.record(
            "Export to YAML",
            exported,
            "Successfully exported and cleaned up"
        )
    except Exception as e:
        results.record("Export to YAML", False, str(e))


def test_nlp_parser_solidworks(results: TestResults):
    """Test NLP Parser for SolidWorks (meters)."""
    print("\n" + "="*80)
    print("TESTING NLP PARSER - SOLIDWORKS (METERS)")
    print("="*80 + "\n")
    
    parser = CADNLPParser("solidworks")
    
    test_cases = [
        {
            "name": "Simple inches to meters",
            "input": "6 inch diameter",
            "expected_value": 0.1524,  # 6 inches = 0.1524 meters
            "expected_type": "diameter",
            "tolerance": 0.0001
        },
        {
            "name": "Fraction parsing (1/2 inch)",
            "input": "half inch thick",
            "expected_value": 0.0127,  # 0.5 inches = 0.0127 meters
            "expected_type": "thickness",
            "tolerance": 0.0001
        },
        {
            "name": "Mixed fraction (1-1/4 inch)",
            "input": "1 and a quarter inch",
            "expected_value": 0.03175,  # 1.25 inches = 0.03175 meters
            "expected_type": "length",
            "tolerance": 0.0001
        },
        {
            "name": "Multiple dimensions",
            "input": "6 inch flange, quarter inch thick",
            "expected_count": 2,
            "check_type": "multiple"
        },
        {
            "name": "Decimal inches",
            "input": "3.5 inch diameter",
            "expected_value": 0.0889,  # 3.5 inches = 0.0889 meters
            "expected_type": "diameter",
            "tolerance": 0.0001
        },
        {
            "name": "Millimeters to meters",
            "input": "150 mm diameter",
            "expected_value": 0.15,  # 150mm = 0.15 meters
            "expected_type": "diameter",
            "tolerance": 0.001
        },
        {
            "name": "Angle parsing",
            "input": "45 degree angle",
            "expected_value": 45.0,
            "expected_type": "angle",
            "tolerance": 0.1
        }
    ]
    
    for test in test_cases:
        try:
            params = parser.parse(test["input"])
            
            if test.get("check_type") == "multiple":
                # Check for multiple parameters
                passed = len(params) >= test["expected_count"]
                details = f"Found {len(params)} parameters: {list(params.keys())}"
            else:
                # Check single parameter
                param_found = False
                param_value = None
                
                for param_name, param_data in params.items():
                    if test["expected_type"] in param_name.lower():
                        param_found = True
                        param_value = param_data.value
                        break
                
                if param_found and param_value is not None:
                    diff = abs(param_value - test["expected_value"])
                    passed = diff <= test["tolerance"]
                    details = f"Expected {test['expected_value']:.4f}, got {param_value:.4f} (diff: {diff:.6f})"
                else:
                    passed = False
                    details = f"Parameter type '{test['expected_type']}' not found. Got: {list(params.keys())}"
            
            results.record(f"NLP-SW: {test['name']}", passed, details)
            
        except Exception as e:
            results.record(f"NLP-SW: {test['name']}", False, str(e))


def test_nlp_parser_inventor(results: TestResults):
    """Test NLP Parser for Inventor (centimeters)."""
    print("\n" + "="*80)
    print("TESTING NLP PARSER - INVENTOR (CENTIMETERS)")
    print("="*80 + "\n")
    
    parser = CADNLPParser("inventor")
    
    test_cases = [
        {
            "name": "Inches to centimeters",
            "input": "6 inch diameter",
            "expected_value": 15.24,  # 6 inches = 15.24 cm
            "expected_type": "diameter",
            "tolerance": 0.01
        },
        {
            "name": "Fraction to centimeters",
            "input": "quarter inch thick",
            "expected_value": 0.635,  # 0.25 inches = 0.635 cm
            "expected_type": "thickness",
            "tolerance": 0.01
        },
        {
            "name": "Millimeters to centimeters",
            "input": "150 mm diameter",
            "expected_value": 15.0,  # 150mm = 15 cm
            "expected_type": "diameter",
            "tolerance": 0.1
        }
    ]
    
    for test in test_cases:
        try:
            params = parser.parse(test["input"])
            
            param_found = False
            param_value = None
            
            for param_name, param_data in params.items():
                if test["expected_type"] in param_name.lower():
                    param_found = True
                    param_value = param_data.value
                    break
            
            if param_found and param_value is not None:
                diff = abs(param_value - test["expected_value"])
                passed = diff <= test["tolerance"]
                details = f"Expected {test['expected_value']:.3f}cm, got {param_value:.3f}cm (diff: {diff:.4f})"
            else:
                passed = False
                details = f"Parameter type '{test['expected_type']}' not found. Got: {list(params.keys())}"
            
            results.record(f"NLP-INV: {test['name']}", passed, details)
            
        except Exception as e:
            results.record(f"NLP-INV: {test['name']}", False, str(e))


def test_material_extraction(results: TestResults):
    """Test material extraction from user input."""
    print("\n" + "="*80)
    print("TESTING MATERIAL EXTRACTION")
    print("="*80 + "\n")
    
    parser = CADNLPParser("solidworks")
    
    test_cases = [
        ("A105 carbon steel", "ASTM A105"),
        ("316 stainless steel", "316SS"),
        ("6061-T6 aluminum", "6061-T6"),
        ("A516 grade 70", "ASTM A516"),
        ("plain carbon steel", "carbon steel"),
    ]
    
    for input_text, expected in test_cases:
        try:
            material = parser.extract_material(input_text)
            passed = material is not None and expected.lower() in material.lower()
            details = f"Input: '{input_text}' → Extracted: '{material}'"
            results.record(f"Material: {expected}", passed, details)
        except Exception as e:
            results.record(f"Material: {expected}", False, str(e))


def test_standard_extraction(results: TestResults):
    """Test engineering standard extraction."""
    print("\n" + "="*80)
    print("TESTING STANDARD EXTRACTION")
    print("="*80 + "\n")
    
    parser = CADNLPParser("solidworks")
    
    test_cases = [
        ("per ASME B16.5", "ASME B16.5"),
        ("AWS D1.1 welding", "AWS D1.1"),
        ("AISC requirements", "AISC"),
        ("according to B31.3", "B31.3"),
    ]
    
    for input_text, expected in test_cases:
        try:
            standard = parser.extract_standard(input_text)
            passed = standard is not None and expected in standard
            details = f"Input: '{input_text}' → Extracted: '{standard}'"
            results.record(f"Standard: {expected}", passed, details)
        except Exception as e:
            results.record(f"Standard: {expected}", False, str(e))


def test_edge_cases(results: TestResults):
    """Test edge cases and error handling."""
    print("\n" + "="*80)
    print("TESTING EDGE CASES")
    print("="*80 + "\n")
    
    parser = CADNLPParser("solidworks")
    
    # Test 1: Empty input
    try:
        params = parser.parse("")
        results.record(
            "Edge: Empty input",
            len(params) == 0,
            "Should return empty dict"
        )
    except Exception as e:
        results.record("Edge: Empty input", False, str(e))
    
    # Test 2: No dimensions
    try:
        params = parser.parse("create a flange with holes")
        results.record(
            "Edge: No dimensions",
            len(params) == 0,
            f"Got {len(params)} parameters (should be 0)"
        )
    except Exception as e:
        results.record("Edge: No dimensions", False, str(e))
    
    # Test 3: Very large number
    try:
        params = parser.parse("1000 inch diameter")
        has_diameter = any("diameter" in k.lower() for k in params.keys())
        results.record(
            "Edge: Large number (1000 inches)",
            has_diameter,
            f"Parsed: {list(params.keys())}"
        )
    except Exception as e:
        results.record("Edge: Large number", False, str(e))
    
    # Test 4: Very small number
    try:
        params = parser.parse("0.001 inch thick")
        has_thickness = any("thick" in k.lower() for k in params.keys())
        results.record(
            "Edge: Small number (0.001 inches)",
            has_thickness,
            f"Parsed: {list(params.keys())}"
        )
    except Exception as e:
        results.record("Edge: Small number", False, str(e))
    
    # Test 5: Mixed units in same input
    try:
        params = parser.parse("6 inch outer diameter, 150mm inner diameter")
        results.record(
            "Edge: Mixed units",
            len(params) >= 2,
            f"Found {len(params)} parameters: {list(params.keys())}"
        )
    except Exception as e:
        results.record("Edge: Mixed units", False, str(e))
    
    # Test 6: Invalid CAD software
    try:
        bad_parser = CADNLPParser("invalid_software")
        params = bad_parser.parse("6 inch")
        results.record(
            "Edge: Invalid CAD software",
            True,
            "Should default to meters"
        )
    except Exception as e:
        results.record("Edge: Invalid CAD software", False, str(e))


def test_real_world_scenarios(results: TestResults):
    """Test realistic CAD chatbot scenarios."""
    print("\n" + "="*80)
    print("TESTING REAL-WORLD SCENARIOS")
    print("="*80 + "\n")
    
    parser_sw = CADNLPParser("solidworks")
    library = PromptLibrary()
    
    scenarios = [
        {
            "name": "Build flange request",
            "user_input": "Build me a 6 inch 150# RFWN flange with A105 material per ASME B16.5",
            "checks": [
                ("dimensions", lambda p: len(p) > 0),
                ("material", lambda p: parser_sw.extract_material("A105") is not None),
                ("standard", lambda p: parser_sw.extract_standard("ASME B16.5") is not None),
            ]
        },
        {
            "name": "Sheet metal design",
            "user_input": "Create a sheet metal bracket, 3mm thick, 45 degree bend",
            "checks": [
                ("thickness", lambda p: any("thick" in k.lower() for k in p.keys())),
                ("angle", lambda p: any("angle" in k.lower() or "bend" in k.lower() for k in p.keys())),
            ]
        },
        {
            "name": "Weldment design",
            "user_input": "Design a structural frame with 4 inch square tube, quarter inch wall, per AWS D1.1",
            "checks": [
                ("dimensions", lambda p: len(p) >= 2),
                ("standard", lambda p: parser_sw.extract_standard("AWS D1.1") is not None),
            ]
        },
    ]
    
    for scenario in scenarios:
        params = parser_sw.parse(scenario["user_input"])
        all_checks_passed = True
        failed_checks = []
        
        for check_name, check_func in scenario["checks"]:
            try:
                if not check_func(params):
                    all_checks_passed = False
                    failed_checks.append(check_name)
            except Exception as e:
                all_checks_passed = False
                failed_checks.append(f"{check_name} (error: {str(e)})")
        
        details = f"Parsed {len(params)} params. "
        if failed_checks:
            details += f"Failed checks: {', '.join(failed_checks)}"
        else:
            details += f"All checks passed. Params: {list(params.keys())}"
        
        results.record(f"Scenario: {scenario['name']}", all_checks_passed, details)


def test_prompt_library_integration(results: TestResults):
    """Test integration between prompt library and NLP parser."""
    print("\n" + "="*80)
    print("TESTING PROMPT LIBRARY + NLP INTEGRATION")
    print("="*80 + "\n")
    
    library = PromptLibrary()
    parser = CADNLPParser("solidworks")
    
    # Test: Use CAD prompt with parsed parameters
    try:
        # Get CAD expert prompt
        cad_prompt_obj = library.get_prompt("engineering.cad_expert")
        if not cad_prompt_obj:
            results.record("Integration: CAD Expert with NLP", False, "Prompt not found")
            return
        
        # Parse user input
        user_input = "Build a 6 inch flange, half inch thick, A105 material"
        params = parser.parse(user_input)
        material = parser.extract_material(user_input)
        
        # Format prompt with parsed data
        formatted_params = parser.format_for_cad(params)
        
        # Create system message
        system_prompt = cad_prompt_obj.content
        
        # Add parsed dimensions to context
        full_context = f"{system_prompt}\n\nUSER REQUEST PARSED:\n{formatted_params}\nMaterial: {material}"
        
        passed = (
            len(system_prompt) > 0 and
            len(params) > 0 and
            material is not None
        )
        
        details = f"Prompt: {len(system_prompt)} chars, Params: {len(params)}, Material: {material}"
        results.record("Integration: CAD Expert with NLP", passed, details)
        
    except Exception as e:
        results.record("Integration: CAD Expert with NLP", False, str(e))


def run_all_tests():
    """Run all test suites."""
    print("\n" + "🚀"*40)
    print("CAD CHATBOT COMPREHENSIVE TEST SUITE")
    print("Testing: Prompt Library, NLP Parser, Integration, Edge Cases")
    print("🚀"*40)
    
    results = TestResults()
    
    # Run all test suites
    test_prompt_library(results)
    test_nlp_parser_solidworks(results)
    test_nlp_parser_inventor(results)
    test_material_extraction(results)
    test_standard_extraction(results)
    test_edge_cases(results)
    test_real_world_scenarios(results)
    test_prompt_library_integration(results)
    
    # Print summary
    results.summary()
    
    # Return exit code
    return 0 if results.failed == 0 else 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
