"""
Industry-Specific Scenarios & Design Validation Test
Tests bot's handling of domain-specific builds and validation checks
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

project_root = Path(__file__).parent.parent
nlp_parser = load_module("cad_nlp_parser", project_root / "core" / "cad_nlp_parser.py")
prompt_lib = load_module("prompt_library", project_root / "core" / "prompt_library.py")

CADNLPParser = nlp_parser.CADNLPParser
PromptLibrary = prompt_lib.PromptLibrary


class IndustryValidator:
    """Validates builds against industry standards and best practices."""
    
    def __init__(self):
        self.parser = CADNLPParser("solidworks")
        self.prompt_library = PromptLibrary()
    
    def validate_pressure_vessel(self, description: str) -> Dict[str, Any]:
        """Validate pressure vessel design requirements."""
        params = self.parser.parse(description)
        material = self.parser.extract_material(description)
        standard = self.parser.extract_standard(description)
        
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check for ASME VIII requirement
        if "pressure" in description.lower() or "vessel" in description.lower():
            if not standard or "VIII" not in standard:
                validation["warnings"].append("Pressure vessels typically require ASME VIII compliance")
        
        # Check material suitability
        if material:
            if "vessel" in description.lower() and "carbon steel" not in material.lower() and "A516" not in material:
                validation["recommendations"].append("Consider A516 carbon steel for pressure vessels")
        
        # Check for thickness
        has_thickness = any("thickness" in str(k).lower() or "thick" in str(k).lower() for k in params.keys())
        if not has_thickness:
            validation["errors"].append("Pressure vessel requires wall thickness specification")
            validation["valid"] = False
        
        return validation
    
    def validate_piping(self, description: str) -> Dict[str, Any]:
        """Validate piping component requirements."""
        params = self.parser.parse(description)
        material = self.parser.extract_material(description)
        standard = self.parser.extract_standard(description)
        
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check for piping standards
        if "pipe" in description.lower() or "flange" in description.lower():
            if not standard:
                validation["warnings"].append("Consider specifying ASME B16.5 or B31.3 for piping")
            elif "B16" not in standard and "B31" not in standard:
                validation["warnings"].append("Common piping standards: ASME B16.5, B16.9, B31.3")
        
        # Check for schedule or class
        has_schedule = "schedule" in description.lower() or "sch" in description.lower()
        has_class = re.search(r'\b(150|300|600|900|1500|2500)#?\b', description)
        
        if "pipe" in description.lower() and not has_schedule:
            validation["recommendations"].append("Specify pipe schedule (e.g., Schedule 40, 80, 160)")
        
        if "flange" in description.lower() and not has_class:
            validation["recommendations"].append("Specify flange class (e.g., 150#, 300#)")
        
        return validation
    
    def validate_weldment(self, description: str) -> Dict[str, Any]:
        """Validate weldment requirements."""
        material = self.parser.extract_material(description)
        standard = self.parser.extract_standard(description)
        
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        if "weld" in description.lower():
            if not standard or "AWS" not in standard:
                validation["warnings"].append("Welding typically requires AWS D1.1 or similar standard")
            
            if not material:
                validation["errors"].append("Weldment requires material specification")
                validation["valid"] = False
            
            # Check for weld prep
            has_prep = any(term in description.lower() for term in ["bevel", "groove", "prep", "chamfer"])
            if not has_prep:
                validation["recommendations"].append("Consider specifying weld preparation (bevel, groove)")
        
        return validation
    
    def validate_structural(self, description: str) -> Dict[str, Any]:
        """Validate structural component requirements."""
        material = self.parser.extract_material(description)
        standard = self.parser.extract_standard(description)
        
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        structural_keywords = ["beam", "column", "truss", "frame", "brace", "support"]
        is_structural = any(kw in description.lower() for kw in structural_keywords)
        
        if is_structural:
            if not standard or "AISC" not in standard:
                validation["warnings"].append("Structural steel typically follows AISC standards")
            
            if not material:
                validation["recommendations"].append("Specify structural steel grade (e.g., A36, A992)")
        
        return validation


def run_industry_tests():
    """Run industry-specific scenario tests."""
    
    print("\n" + "="*80)
    print("🏭 INDUSTRY-SPECIFIC SCENARIO TESTS")
    print("="*80 + "\n")
    
    validator = IndustryValidator()
    
    # Industry scenarios
    scenarios = [
        {
            "industry": "Oil & Gas - Pressure Vessels",
            "tests": [
                {
                    "desc": "Create a pressure vessel, 48 inch diameter, 3/8 inch wall, A516 Grade 70, ASME VIII Div 1",
                    "type": "pressure_vessel"
                },
                {
                    "desc": "Build vertical pressure vessel 60 inches dia, A516 material",
                    "type": "pressure_vessel"
                },
                {
                    "desc": "Horizontal vessel for 150 psi service, 36 inch diameter",
                    "type": "pressure_vessel"
                }
            ]
        },
        {
            "industry": "Piping Systems",
            "tests": [
                {
                    "desc": "6 inch RFWN flange, Class 150, A105 carbon steel, ASME B16.5",
                    "type": "piping"
                },
                {
                    "desc": "Create 2 inch Schedule 40 pipe, 10 feet long, A106 Grade B",
                    "type": "piping"
                },
                {
                    "desc": "Build a pipe reducer 6x4 inch, 316SS, ASME B16.9",
                    "type": "piping"
                },
                {
                    "desc": "4 inch flange for high pressure service",
                    "type": "piping"
                }
            ]
        },
        {
            "industry": "Structural Steel",
            "tests": [
                {
                    "desc": "W12x40 wide flange beam, A992 steel, 20 feet long, AISC",
                    "type": "structural"
                },
                {
                    "desc": "Build support bracket for piping, A36 steel, 12 inches",
                    "type": "structural"
                },
                {
                    "desc": "Create structural frame with HSS 6x6x3/8 tube steel",
                    "type": "structural"
                }
            ]
        },
        {
            "industry": "Weldments & Fabrication",
            "tests": [
                {
                    "desc": "Welded nozzle assembly, 6 inch dia, 45 degree bevel, A105, AWS D1.1",
                    "type": "weldment"
                },
                {
                    "desc": "Create weldment with 30 degree chamfer for full penetration weld",
                    "type": "weldment"
                },
                {
                    "desc": "Build welded bracket assembly, structural steel",
                    "type": "weldment"
                }
            ]
        },
        {
            "industry": "Aerospace",
            "tests": [
                {
                    "desc": "Create bracket in 7075-T6 aluminum, .125 inch thick, weight optimized",
                    "type": "general"
                },
                {
                    "desc": "Build titanium fitting, 2 inch flange, Ti-6Al-4V",
                    "type": "general"
                },
                {
                    "desc": "Lightweight structural member, carbon fiber composite",
                    "type": "general"
                }
            ]
        },
        {
            "industry": "Automotive",
            "tests": [
                {
                    "desc": "Create engine bracket, 6061-T6 aluminum, 8mm thick",
                    "type": "general"
                },
                {
                    "desc": "Build suspension mount, high strength steel, with clearance holes",
                    "type": "general"
                },
                {
                    "desc": "Sheet metal stamping die for body panel, tool steel",
                    "type": "general"
                }
            ]
        }
    ]
    
    total_tests = 0
    tests_with_warnings = 0
    tests_with_errors = 0
    tests_with_recommendations = 0
    
    for scenario in scenarios:
        print(f"\n{'─'*80}")
        print(f"🏭 Industry: {scenario['industry']}")
        print(f"{'─'*80}\n")
        
        for test in scenario["tests"]:
            total_tests += 1
            desc = test["desc"]
            test_type = test["type"]
            
            print(f"Test: \"{desc}\"")
            
            # Parse basic info
            params = validator.parser.parse(desc)
            material = validator.parser.extract_material(desc)
            standard = validator.parser.extract_standard(desc)
            
            print(f"  📏 Dimensions: {len(params)}")
            if material:
                print(f"  🔩 Material: {material}")
            if standard:
                print(f"  📋 Standard: {standard}")
            
            # Validate based on type
            if test_type == "pressure_vessel":
                validation = validator.validate_pressure_vessel(desc)
            elif test_type == "piping":
                validation = validator.validate_piping(desc)
            elif test_type == "weldment":
                validation = validator.validate_weldment(desc)
            elif test_type == "structural":
                validation = validator.validate_structural(desc)
            else:
                validation = {"valid": True, "warnings": [], "errors": [], "recommendations": []}
            
            # Display validation results
            if validation["errors"]:
                tests_with_errors += 1
                print(f"  ❌ ERRORS:")
                for error in validation["errors"]:
                    print(f"     - {error}")
            
            if validation["warnings"]:
                tests_with_warnings += 1
                print(f"  ⚠️  WARNINGS:")
                for warning in validation["warnings"]:
                    print(f"     - {warning}")
            
            if validation["recommendations"]:
                tests_with_recommendations += 1
                print(f"  💡 RECOMMENDATIONS:")
                for rec in validation["recommendations"]:
                    print(f"     - {rec}")
            
            if validation["valid"] and not validation["warnings"] and not validation["recommendations"]:
                print(f"  ✅ VALIDATED - Meets industry requirements")
            
            print()
    
    # Summary
    print("="*80)
    print("📊 INDUSTRY TEST SUMMARY")
    print("="*80)
    print(f"Total Industry Tests: {total_tests}")
    print(f"Tests with Errors: {tests_with_errors} ({tests_with_errors/total_tests*100:.1f}%)")
    print(f"Tests with Warnings: {tests_with_warnings} ({tests_with_warnings/total_tests*100:.1f}%)")
    print(f"Tests with Recommendations: {tests_with_recommendations} ({tests_with_recommendations/total_tests*100:.1f}%)")
    print(f"\nValidation Coverage: {(total_tests - tests_with_errors)/total_tests*100:.1f}%")
    
    if tests_with_errors == 0:
        print("\n✅ EXCELLENT - All tests have complete required information")
    elif tests_with_errors / total_tests <= 0.2:
        print("\n🟡 GOOD - Most tests complete, some missing critical data")
    else:
        print("\n🔴 NEEDS IMPROVEMENT - Many tests missing required information")
    
    return True


def run_safety_checks():
    """Test safety and validation checks."""
    
    print("\n" + "="*80)
    print("🛡️  SAFETY & VALIDATION CHECKS")
    print("="*80 + "\n")
    
    parser = CADNLPParser("solidworks")
    
    safety_tests = [
        {
            "category": "Dimension Validity",
            "tests": [
                ("Create flange 0 inches diameter", "Zero dimension"),
                ("Build part -5 inches long", "Negative dimension"),
                ("Make wall thickness 0.001 inches for pressure vessel", "Too thin"),
                ("6 inch flange, 12 inch thickness", "Thickness > diameter"),
            ]
        },
        {
            "category": "Material Compatibility",
            "tests": [
                ("Aluminum part for cryogenic service -320F", "Material limitation"),
                ("Plastic pressure vessel for 150 psi", "Inappropriate material"),
                ("Wood structural beam for industrial load", "Non-standard material"),
            ]
        },
        {
            "category": "Standard Compliance",
            "tests": [
                ("Pressure vessel with no code requirements", "Missing standard"),
                ("Flange for Class 2500 in A105", "Material rating mismatch"),
                ("Pipe for 3000 psi service, Schedule 10", "Insufficient schedule"),
            ]
        },
        {
            "category": "Fabrication Feasibility",
            "tests": [
                ("Extrude 1000 feet long part", "Excessive length"),
                ("Create hole 0.010 inches diameter in 2 inch plate", "Too small"),
                ("Build part with 500 complex features", "Over-complex"),
            ]
        }
    ]
    
    total_checks = 0
    detected_issues = 0
    
    for category_data in safety_tests:
        category = category_data["category"]
        print(f"\n{'─'*80}")
        print(f"Category: {category}")
        print(f"{'─'*80}\n")
        
        for desc, issue in category_data["tests"]:
            total_checks += 1
            print(f"Test: \"{desc}\"")
            print(f"  Expected Issue: {issue}")
            
            # Parse
            params = parser.parse(desc)
            material = parser.extract_material(desc)
            standard = parser.extract_standard(desc)
            
            # Simple checks
            warnings = []
            
            # Check for zero/negative
            for key, value in params.items():
                val = value.value if hasattr(value, 'value') else value
                if val <= 0:
                    warnings.append(f"Invalid dimension: {key} = {val}")
                if val > 100:  # Very large (in meters for SW)
                    warnings.append(f"Unusually large dimension: {key} = {val}")
            
            # Check for missing standard
            if "pressure" in desc.lower() or "vessel" in desc.lower():
                if not standard or "VIII" not in standard:
                    warnings.append("Pressure vessel missing ASME VIII standard")
            
            # Check material
            if "cryogenic" in desc.lower() and material and "aluminum" in material.lower():
                warnings.append("Aluminum may not be suitable for cryogenic service")
            
            if warnings:
                detected_issues += 1
                print(f"  ⚠️  DETECTED:")
                for warning in warnings:
                    print(f"     - {warning}")
            else:
                print(f"  ℹ️  No automatic checks triggered (may need domain expert)")
            
            print()
    
    # Summary
    print("="*80)
    print("📊 SAFETY CHECK SUMMARY")
    print("="*80)
    print(f"Total Safety Checks: {total_checks}")
    print(f"Issues Detected: {detected_issues}/{total_checks} ({detected_issues/total_checks*100:.1f}%)")
    print(f"\nNote: Some safety checks require domain expertise beyond automated validation")
    
    return True


def run_all_industry_tests():
    """Run all industry and validation tests."""
    
    print("\n" + "🏭"*40)
    print("INDUSTRY-SPECIFIC & VALIDATION TESTING")
    print("🏭"*40)
    
    # Run industry tests
    run_industry_tests()
    
    # Run safety checks
    run_safety_checks()
    
    print("\n" + "="*80)
    print("✅ ALL INDUSTRY & VALIDATION TESTS COMPLETE")
    print("="*80)
    
    return True


if __name__ == "__main__":
    success = run_all_industry_tests()
    sys.exit(0 if success else 1)
