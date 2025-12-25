"""
Example: Using the Comprehensive ACHE Validation System
=======================================================
Demonstrates all 130 ACHE checks + GD&T + Welding + Material validation.

Usage:
    python examples/ache_validation_example.py
"""

from agents.cad_agent.adapters import (
    ACHEValidator,
    ACHEDesignData,
    GDTParser,
    WeldingValidator,
    MaterialValidator,
    MTRData,
    ChemicalComposition,
    MechanicalProperties,
)


def example_gdt_validation():
    """Example: GD&T validation from drawing text."""
    print("\n" + "="*70)
    print("EXAMPLE 1: GD&T VALIDATION")
    print("="*70)
    
    parser = GDTParser()
    
    # Simulate OCR text from a drawing
    drawing_text = """
    POSITION Ø0.010 MMC DATUM A DATUM B DATUM C
    FLATNESS 0.005
    PERPENDICULARITY 0.015 DATUM A
    DATUM A
    DATUM B MMC
    DATUM C
    """
    
    result = parser.parse_drawing_text(drawing_text)
    
    print(f"\n✅ Frames found: {result.frames_found}")
    print(f"✅ Datums found: {', '.join(result.datums_found)}")
    print(f"✅ Is valid: {result.is_valid}")
    
    if result.errors:
        print("\n❌ Errors:")
        for error in result.errors:
            print(f"   - {error}")
    
    if result.warnings:
        print("\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   - {warning}")
    
    # Example bonus tolerance calculation
    print("\n--- Position Tolerance with MMC Bonus ---")
    analysis = parser.calculate_position_bonus(
        nominal_tolerance=0.010,
        feature_size_actual=0.505,  # Actual hole size
        feature_size_mmc=0.500,     # MMC (smallest) hole size
        is_hole=True
    )
    
    print(f"Nominal tolerance: {analysis.nominal_tolerance:.4f}\"")
    print(f"Bonus tolerance: {analysis.bonus_tolerance:.4f}\"")
    print(f"Total tolerance: {analysis.total_tolerance:.4f}\"")
    print(f"Virtual condition: {analysis.virtual_condition:.4f}\"")


def example_welding_validation():
    """Example: Welding validation."""
    print("\n" + "="*70)
    print("EXAMPLE 2: WELDING VALIDATION")
    print("="*70)
    
    validator = WeldingValidator()
    
    # Example weld callouts
    test_callouts = [
        ("1/4\" FILLET WELD BOTH SIDES", 0.375),  # 3/8" base metal
        ("3/16\" FILLET WELD ALL AROUND", 0.50),  # 1/2" base metal
        ("1/8\" FILLET WELD", 0.25),              # 1/4" base metal
    ]
    
    for callout, thickness in test_callouts:
        print(f"\n--- Testing: {callout} (Base metal: {thickness}\") ---")
        result = validator.validate_weld_callout(callout, thickness)
        
        if result.is_valid:
            print(f"✅ PASS - {result.message}")
        else:
            print(f"❌ FAIL")
            for error in result.errors:
                print(f"   Error: {error}")
        
        for info in result.info:
            print(f"   ℹ️  {info}")


def example_material_validation():
    """Example: Material MTR validation."""
    print("\n" + "="*70)
    print("EXAMPLE 3: MATERIAL MTR VALIDATION")
    print("="*70)
    
    validator = MaterialValidator()
    
    # Create sample MTR data for A516-70 plate
    mtr = MTRData(
        heat_number="H12345",
        material_spec="ASTM A516 Grade 70",
        chemistry=ChemicalComposition(
            carbon=0.25,
            manganese=1.10,
            phosphorus=0.020,
            sulfur=0.015,
            silicon=0.25,
        ),
        mechanical=MechanicalProperties(
            yield_strength=42,      # ksi
            tensile_strength=75,    # ksi
            elongation=22,          # %
            unit="ksi"
        ),
        manufacturer="ABC Steel Mill",
    )
    
    # Validate against specification
    result = validator.validate_mtr(mtr, design_spec="A516-70")
    
    print(f"\nMaterial: {mtr.material_spec}")
    print(f"Heat Number: {mtr.heat_number}")
    
    if result.is_valid:
        print("\n✅ MTR VALID - Meets specification")
    else:
        print("\n❌ MTR INVALID")
        for error in result.errors:
            print(f"   Error: {error}")
    
    print(f"\n--- Validation Results ---")
    print(f"Chemistry: {'✅ PASS' if result.chemistry_pass else '❌ FAIL'}")
    print(f"Mechanical: {'✅ PASS' if result.mechanical_pass else '❌ FAIL'}")
    print(f"Heat Treatment: {'✅ OK' if result.heat_treatment_ok else '⚠️  CHECK'}")
    
    for info in result.info:
        print(f"ℹ️  {info}")
    
    # Check NACE compliance
    print("\n--- NACE MR0175 Compliance ---")
    is_compliant, issues = validator.check_nace_compliance(
        mtr.chemistry,
        hardness=220  # HB
    )
    
    if is_compliant:
        print("✅ NACE compliant for sour service")
    else:
        print("❌ NACE issues:")
        for issue in issues:
            print(f"   - {issue}")


def example_ache_master_validation():
    """Example: Complete 130-point ACHE validation."""
    print("\n" + "="*70)
    print("EXAMPLE 4: MASTER ACHE VALIDATION (130 CHECKS)")
    print("="*70)
    
    validator = ACHEValidator()
    
    # Create ACHE design data
    design_data = ACHEDesignData(
        heat_duty_mmbtu_hr=45.2,
        design_pressure_psig=450,
        design_temp_f=650,
        lmtd_f=127.3,
        mtd_correction=0.92,
        tube_material="A179 Seamless",
        tube_od=1.0,
        tube_wall_bwg=14,
        fin_type="L-Fin Aluminum",
        fan_diameter_ft=10.0,
        num_fans=2,
        motor_hp=25,
        motor_enclosure="TEFC",
        hydro_test_pressure=675,  # 1.5× MAWP
    )
    
    # Run complete validation
    report = validator.validate_complete_ache(design_data)
    
    print(f"\nProject: {report.project_name}")
    print(f"Total Checks: {report.total_checks}")
    print(f"Overall Pass Rate: {report.overall_pass_rate:.1f}%")
    print(f"\n{'✅ ACCEPTABLE' if report.is_acceptable else '❌ NEEDS WORK'}")
    
    print(f"\n--- Summary by Phase ---")
    for phase, phase_result in report.phase_results.items():
        print(f"\n{phase.value.upper()}:")
        print(f"  Total: {phase_result.total_checks}")
        print(f"  Passed: {phase_result.passed} ({'✅' if phase_result.pass_rate >= 90 else '⚠️'})")
        print(f"  Failed: {phase_result.failed}")
        print(f"  Warnings: {phase_result.warnings}")
        print(f"  Pass Rate: {phase_result.pass_rate:.1f}%")
    
    if report.critical_failures:
        print(f"\n❌ CRITICAL FAILURES ({len(report.critical_failures)}):")
        for failure in report.critical_failures:
            print(f"   - {failure}")
    
    if report.recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report.recommendations:
            print(f"   - {rec}")
    
    # Show detailed checks for Design Basis phase
    design_basis = report.phase_results.get(list(report.phase_results.keys())[0])
    if design_basis:
        print(f"\n--- Design Basis Detailed Checks ---")
        for check in design_basis.checks[:5]:  # First 5 checks
            status_icon = {
                "pass": "✅",
                "fail": "❌",
                "warning": "⚠️",
                "not_applicable": "⊝",
                "not_checked": "○"
            }.get(check.status.value, "?")
            
            print(f"{status_icon} {check.check_id}: {check.description}")
            if check.message:
                print(f"      {check.message}")


def main():
    """Run all validation examples."""
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║  PROJECT VULCAN - COMPREHENSIVE ENGINEERING VALIDATION SYSTEM    ║")
    print("║  383+ Quality & Model Checks for CAD Design Verification         ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    example_gdt_validation()
    example_welding_validation()
    example_material_validation()
    example_ache_master_validation()
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETE!")
    print("="*70)
    print("\n📚 For more details, see:")
    print("   - docs/ache/COMPREHENSIVE_CHECK_RECOMMENDATIONS.md")
    print("   - docs/ache/ACHE_CHECKLIST.md (130 checks)")
    print("   - agents/cad_agent/adapters/gdt_parser.py")
    print("   - agents/cad_agent/adapters/welding_validator.py")
    print("   - agents/cad_agent/adapters/material_validator.py")
    print("   - agents/cad_agent/adapters/ache_validator.py")


if __name__ == "__main__":
    main()
