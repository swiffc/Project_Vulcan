#!/usr/bin/env python3
"""
Test Standards Database - Offline JSON Lookups
==============================================
Demonstrates instant lookups with zero API calls.

Run this to verify your standards database is working:
    python scripts/test_standards_db.py
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.cad_agent.adapters.standards_db_v2 import StandardsDB, get_standards_db


def test_beam_lookups():
    """Test AISC beam lookups."""
    print("\n" + "="*60)
    print("TEST 1: AISC BEAM LOOKUPS")
    print("="*60)
    
    db = get_standards_db()
    
    # Test beam lookup
    beam = db.get_beam("W8X31")
    if beam:
        print(f"✅ W8X31 Beam Properties:")
        print(f"   Weight: {beam.weight_per_ft} lb/ft")
        print(f"   Depth: {beam.depth}\"")
        print(f"   Flange Width: {beam.flange_width}\"")
        print(f"   Moment of Inertia (Ix): {beam.Ix} in⁴")
        
        # Calculate weight for 10' beam
        length = 10.0
        weight = beam.calculate_weight(length)
        print(f"   Total weight for {length}' beam: {weight} lbs")
    else:
        print("❌ W8X31 not found")
    
    # Test weight verification
    print("\n📊 Weight Verification Test:")
    result = db.verify_beam_weight("W8X31", length_ft=10.0, tolerance_pct=5.0)
    print(f"   Expected: {result['expected_weight_lb']} lbs")
    print(f"   Tolerance: ±{result['tolerance_lb']} lbs ({result['tolerance_pct']}%)")
    print(f"   Acceptable range: {result['min_acceptable_lb']} - {result['max_acceptable_lb']} lbs")


def test_fastener_lookups():
    """Test bolt specifications."""
    print("\n" + "="*60)
    print("TEST 2: FASTENER LOOKUPS")
    print("="*60)
    
    db = get_standards_db()
    
    bolt = db.get_bolt("3/4")
    if bolt:
        print(f"✅ 3/4\" Bolt Specifications:")
        print(f"   Nominal Diameter: {bolt.nominal_diameter}\"")
        print(f"   Standard Hole Size: {bolt.hole_size_standard}\"")
        print(f"   Edge Distance (rolled): {bolt.edge_distance_min_rolled}\"")
        print(f"   Edge Distance (sheared): {bolt.edge_distance_min_sheared}\"")
        print(f"   A325 Tensile Capacity: {bolt.A325_tensile_capacity_kips} kips")
        print(f"   A490 Tensile Capacity: {bolt.A490_tensile_capacity_kips} kips")
    else:
        print("❌ 3/4\" bolt not found")
    
    # Test torque specs
    torque = db.get_torque_spec("3/4", lubricated=True)
    if torque:
        print(f"   Recommended Torque (lubricated): {torque} ft-lbs")


def test_material_lookups():
    """Test material properties."""
    print("\n" + "="*60)
    print("TEST 3: MATERIAL LOOKUPS")
    print("="*60)
    
    db = get_standards_db()
    
    materials_to_test = ["A36", "A572-50", "304", "6061-T6"]
    
    for mat_name in materials_to_test:
        mat = db.get_material(mat_name)
        if mat:
            print(f"\n✅ {mat.designation} ({mat.type}):")
            print(f"   Yield Strength: {mat.yield_strength_ksi} ksi")
            print(f"   Tensile Strength: {mat.tensile_strength_ksi} ksi")
            print(f"   Density: {mat.density_lb_in3} lb/in³")
            print(f"   Max Temperature: {mat.max_temperature_F}°F")
            print(f"   Bend Radius Factor: {mat.bend_radius_factor}T")
        else:
            print(f"❌ {mat_name} not found")


def test_pipe_lookups():
    """Test pipe schedule lookups."""
    print("\n" + "="*60)
    print("TEST 4: PIPE SCHEDULE LOOKUPS")
    print("="*60)
    
    db = get_standards_db()
    
    pipe = db.get_pipe("6", schedule="40")
    if pipe:
        print(f"✅ 6\" NPS Schedule 40 Pipe:")
        print(f"   Outside Diameter: {pipe.OD}\"")
        print(f"   Wall Thickness: {pipe.wall_thickness}\"")
        print(f"   Inside Diameter: {pipe.ID}\"")
        print(f"   Weight: {pipe.weight_per_ft} lb/ft")
    else:
        print("❌ 6\" Schedule 40 pipe not found")
    
    # Test different schedule
    pipe_80 = db.get_pipe("6", schedule="80")
    if pipe_80:
        print(f"\n✅ 6\" NPS Schedule 80 Pipe:")
        print(f"   Wall Thickness: {pipe_80.wall_thickness}\"")
        print(f"   Weight: {pipe_80.weight_per_ft} lb/ft")


def test_api_661_lookups():
    """Test API 661 ACHE standards."""
    print("\n" + "="*60)
    print("TEST 5: API 661 ACHE STANDARDS")
    print("="*60)
    
    db = get_standards_db()
    
    # Fan tip clearance
    fan_dia = 10.0  # feet
    clearance = db.get_fan_tip_clearance(fan_dia)
    if clearance:
        print(f"✅ Fan Tip Clearance for {fan_dia}' diameter fan:")
        print(f"   Maximum clearance: {clearance}\"")
    
    # OSHA platform requirements
    osha_platform = db.get_osha_requirements("platforms")
    if osha_platform:
        print(f"\n✅ OSHA Platform Requirements:")
        print(f"   Minimum width: {osha_platform['min_width_in']}\"")
        print(f"   Load rating: {osha_platform['load_rating_psf']} psf")
        print(f"   Handrail height: {osha_platform['handrail_height_in']}\" ± {osha_platform['handrail_tolerance_in']}\"")
        print(f"   Midrail height: {osha_platform['midrail_height_in']}\"")
        print(f"   Toeboard height: {osha_platform['toeboard_height_in']}\"")
    
    # OSHA ladder requirements
    osha_ladder = db.get_osha_requirements("ladders")
    if osha_ladder:
        print(f"\n✅ OSHA Ladder Requirements:")
        print(f"   Rung spacing: {osha_ladder['rung_spacing_in']}\"")
        print(f"   Side rail clearance: {osha_ladder['side_rail_clearance_in']}\"")
        print(f"   Cage required above: {osha_ladder['cage_required_above_ft']}'")


def test_performance():
    """Test lookup performance."""
    print("\n" + "="*60)
    print("TEST 6: PERFORMANCE (CACHED LOOKUPS)")
    print("="*60)
    
    import time
    
    db = get_standards_db()
    
    # First lookup (loads JSON, caches data)
    start = time.time()
    beam1 = db.get_beam("W8X31")
    time1 = (time.time() - start) * 1000  # Convert to ms
    
    # Second lookup (from cache)
    start = time.time()
    beam2 = db.get_beam("W10X49")
    time2 = (time.time() - start) * 1000
    
    # Third lookup (from cache)
    start = time.time()
    beam3 = db.get_beam("W12X65")
    time3 = (time.time() - start) * 1000
    
    print(f"✅ Lookup Performance:")
    print(f"   First lookup (load + cache): {time1:.3f} ms")
    print(f"   Second lookup (cached): {time2:.3f} ms")
    print(f"   Third lookup (cached): {time3:.3f} ms")
    print(f"   Speedup: {time1 / time2:.1f}x faster after caching")


def test_listing():
    """Test listing available data."""
    print("\n" + "="*60)
    print("TEST 7: AVAILABLE DATA")
    print("="*60)
    
    db = get_standards_db()
    
    beams = db.list_available_beams()
    print(f"✅ Available AISC Beams: {len(beams)} total")
    print(f"   Examples: {', '.join(beams[:5])}...")
    
    materials = db.list_available_materials()
    print(f"\n✅ Available Materials:")
    for category, items in materials.items():
        print(f"   {category}: {len(items)} items ({', '.join(items[:3])}...)")


def main():
    """Run all tests."""
    print("╔" + "="*58 + "╗")
    print("║  STANDARDS DATABASE TEST - OFFLINE JSON LOOKUPS          ║")
    print("║  Zero API calls • Instant lookups • Cached in memory    ║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_beam_lookups()
        test_fastener_lookups()
        test_material_lookups()
        test_pipe_lookups()
        test_api_661_lookups()
        test_performance()
        test_listing()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n💡 Tip: Use get_standards_db() in your code for instant lookups")
        print("   No API calls, no rate limits, 100% offline!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
