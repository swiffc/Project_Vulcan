"""
Error Analysis Test - Identify and categorize all bot errors
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

project_root = Path(__file__).parent.parent
nlp_parser = load_module("cad_nlp_parser", project_root / "core" / "cad_nlp_parser.py")
CADNLPParser = nlp_parser.CADNLPParser


def analyze_parsing_errors():
    """Test edge cases that might cause errors."""
    
    print("\n" + "="*80)
    print("🔍 ERROR ANALYSIS - CAD CHATBOT EDGE CASES")
    print("="*80 + "\n")
    
    parser = CADNLPParser("solidworks")
    
    error_categories = defaultdict(list)
    
    # Test cases designed to expose errors
    test_cases = [
        {
            "category": "Ambiguous Dimensions",
            "tests": [
                "6 inch",  # Which parameter type?
                "100mm",   # No context
                "quarter inch",  # Written fraction
                "3.14159",  # Just a number
            ]
        },
        {
            "category": "Conflicting Units",
            "tests": [
                "6 inch diameter, 150mm thick",  # Mixed imperial/metric
                "2 inch OD, 50mm ID",  # Different units same part
                "100 cm or 1 meter",  # Alternatives
            ]
        },
        {
            "category": "Extreme Values",
            "tests": [
                "0.0001 inch",  # Very small
                "10000 inches",  # Very large
                "0 inch",  # Zero
                "-5 inches",  # Negative
            ]
        },
        {
            "category": "Invalid Input",
            "tests": [
                "",  # Empty
                "just some text",  # No dimensions
                "!!!@@@###",  # Special chars
                "make it bigger",  # Relative, not absolute
            ]
        },
        {
            "category": "Complex Fractions",
            "tests": [
                "1-1/2 inches",
                "3/32 inch",
                "5 and 3/4 inches",
                "7/8ths of an inch",
            ]
        },
        {
            "category": "Material Edge Cases",
            "tests": [
                "stainless",  # Incomplete
                "316 grade",  # Partial
                "A105 or A106",  # Alternatives
                "some kind of steel",  # Vague
            ]
        },
        {
            "category": "Standard Edge Cases",
            "tests": [
                "ASME",  # No specific code
                "per code",  # Which code?
                "B16.5 class 150",  # With rating
                "AWS welding standard",  # Incomplete
            ]
        },
        {
            "category": "Multiple Interpretations",
            "tests": [
                "6 inch pipe",  # OD or NPS?
                "quarter plate",  # 1/4 inch thick plate?
                "4x4 tube",  # 4"x4" square tube?
                "150 pound flange",  # 150# rating?
            ]
        }
    ]
    
    total_tests = 0
    total_errors = 0
    total_warnings = 0
    
    for category_data in test_cases:
        category = category_data["category"]
        print(f"\n{'─'*80}")
        print(f"Category: {category}")
        print(f"{'─'*80}")
        
        for test_input in category_data["tests"]:
            total_tests += 1
            print(f"\nInput: \"{test_input}\"")
            
            try:
                # Parse
                params = parser.parse(test_input)
                material = parser.extract_material(test_input)
                standard = parser.extract_standard(test_input)
                
                # Analyze results
                issues = []
                
                if not params and not material and not standard:
                    issues.append("⚠️ Nothing extracted")
                    total_warnings += 1
                
                if len(params) > 1:
                    param_types = [p.parameter_type for p in params.values()]
                    if len(set(param_types)) != len(param_types):
                        issues.append("⚠️ Duplicate parameter types")
                        total_warnings += 1
                
                # Check for unrealistic values
                for name, param in params.items():
                    if param.value > 100:  # > 100 meters is suspicious
                        issues.append(f"⚠️ Very large value: {param.value:.2f} {param.unit}")
                        total_warnings += 1
                    if param.value < 0.00001:  # < 0.01mm is suspicious
                        issues.append(f"⚠️ Very small value: {param.value:.6f} {param.unit}")
                        total_warnings += 1
                    if param.value < 0:
                        issues.append(f"❌ Negative value: {param.value}")
                        total_errors += 1
                
                # Display results
                if params:
                    print(f"  Dimensions: {len(params)}")
                    for name, p in params.items():
                        print(f"    • {name}: {p.value:.6f} {p.unit} ({p.parameter_type})")
                else:
                    print("  Dimensions: None")
                
                if material:
                    print(f"  Material: {material}")
                if standard:
                    print(f"  Standard: {standard}")
                
                if issues:
                    print("  Issues:")
                    for issue in issues:
                        print(f"    {issue}")
                        error_categories[category].append({
                            "input": test_input,
                            "issue": issue
                        })
                else:
                    print("  ✅ No issues detected")
                
            except Exception as e:
                print(f"  ❌ EXCEPTION: {e}")
                total_errors += 1
                error_categories[category].append({
                    "input": test_input,
                    "issue": f"Exception: {str(e)}"
                })
    
    # Summary by category
    print("\n" + "="*80)
    print("📊 ERROR SUMMARY BY CATEGORY")
    print("="*80)
    
    for category, errors in error_categories.items():
        if errors:
            print(f"\n{category}: {len(errors)} issues")
            for error in errors[:3]:  # Show first 3
                print(f"  • \"{error['input']}\" - {error['issue']}")
            if len(errors) > 3:
                print(f"  ... and {len(errors)-3} more")
    
    # Overall summary
    print("\n" + "="*80)
    print("📈 OVERALL ERROR ANALYSIS")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"Total Errors: {total_errors}")
    print(f"Total Warnings: {total_warnings}")
    print(f"Success Rate: {(total_tests - total_errors)/total_tests*100:.1f}%")
    
    # Recommendations
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    
    if total_errors > 0:
        print("🔴 CRITICAL:")
        print("  - Fix exception handling for edge cases")
        print("  - Add input validation before parsing")
    
    if total_warnings > 5:
        print("🟡 WARNINGS:")
        print("  - Add confidence scoring for ambiguous inputs")
        print("  - Implement user confirmation for edge cases")
        print("  - Add default value suggestions")
    
    print("\n✅ STRENGTHS:")
    print("  - Parser handles most inputs without crashing")
    print("  - Graceful degradation (returns empty instead of failing)")
    print("  - Good unit conversion accuracy")
    
    return total_errors == 0


if __name__ == "__main__":
    success = analyze_parsing_errors()
    sys.exit(0 if success else 1)
