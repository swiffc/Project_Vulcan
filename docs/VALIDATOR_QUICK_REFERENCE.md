# Validator Suite - Quick Reference

## 🚀 Quick Start

### 1. StandardsDB - Offline Engineering Data
```python
from agents.cad_agent.adapters.standards_db_v2 import StandardsDB

db = StandardsDB()

# AISC beams
beam = db.get_beam('W8X31')
print(f"Depth: {beam.depth}\", Weight: {beam.weight_per_ft} lb/ft")

# Bolts
bolt = db.get_bolt('3/4')
print(f"Hole: {bolt.hole_size_standard}\", Capacity: {bolt.A325_tensile_capacity_kips} kips")

# Materials
material = db.get_material('A36')
print(f"Fy: {material.yield_strength_ksi} ksi, Fu: {material.tensile_strength_ksi} ksi")

# Pipes
pipe = db.get_pipe('6', schedule='40')
print(f"OD: {pipe.OD}\", Wall: {pipe.wall_thickness}\"")
```

### 2. GDTParser - Geometric Tolerances
```python
from agents.cad_agent.adapters.gdt_parser import GDTParser

parser = GDTParser()
result = parser.parse_drawing_text("⌖ 0.005 A B C")

print(f"Frames: {result.frames_found}, Datums: {result.datums_found}")
print(f"Valid: {result.is_valid}")
```

### 3. WeldingValidator - AWS D1.1
```python
from agents.cad_agent.adapters.welding_validator import WeldingValidator

validator = WeldingValidator()
result = validator.validate_weld_callout(
    '1/4" FILLET WELD BOTH SIDES',
    base_metal_thickness=0.375
)

print(f"Valid: {result.is_valid}")
print(f"Info: {result.info}")
```

### 4. MaterialValidator - MTR Checking
```python
from agents.cad_agent.adapters.material_validator import (
    MaterialValidator, ChemicalComposition, MechanicalProperties,
    MTRData, HeatTreatment
)

chemistry = ChemicalComposition(carbon=0.24, manganese=1.00)
mechanical = MechanicalProperties(yield_strength=42.0, tensile_strength=75.0)

mtr = MTRData(
    heat_number="H12345",
    material_spec="ASTM A516 Grade 70",
    chemistry=chemistry,
    mechanical=mechanical,
    heat_treatment=HeatTreatment.NORMALIZED
)

validator = MaterialValidator()
result = validator.validate_mtr(mtr, design_spec="A516-70")

print(f"Valid: {result.is_valid}")
print(f"CE: {chemistry.carbon_equivalent:.3f}")
```

### 5. ACHEValidator - 130-Point Checklist
```python
from agents.cad_agent.adapters.ache_validator import ACHEValidator, ACHEDesignData

design_data = ACHEDesignData(
    heat_duty_mmbtu_hr=10.5,
    design_pressure_psig=150,
    design_temp_f=350,
    lmtd_f=50.0,
    tube_material='A106-B'
)

validator = ACHEValidator()
report = validator.validate_complete_ache(design_data)

print(f"Pass Rate: {report.overall_pass_rate:.1f}%")
print(f"Acceptable: {report.is_acceptable}")
```

---

## 📊 Data Coverage

| Category | Count | File |
|----------|-------|------|
| AISC Shapes | 234 | `data/standards/aisc_shapes.json` |
| Fasteners | 21 | `data/standards/fasteners.json` |
| Pipe Fittings | 383 | `data/standards/pipe_schedules.json` |
| Materials | 20 | `data/standards/materials.json` |

---

## 🔍 Common Lookups

### AISC Beams
```python
db.get_beam('W8X31')   # Wide flange
db.get_beam('C10X30')  # Channel
db.get_beam('L4X4X1/2') # Angle
```

### Bolts
```python
db.get_bolt('1/2')  # 1/2" bolt
db.get_bolt('3/4')  # 3/4" bolt
db.get_bolt('1')    # 1" bolt
```

### Materials
```python
db.get_material('A36')      # Carbon steel
db.get_material('A516-70')  # Pressure vessel
db.get_material('304')      # Stainless
db.get_material('316')      # Stainless (Mo)
```

### Pipes
```python
db.get_pipe('6', schedule='40')   # NPS 6 Sch 40
db.get_pipe('8', schedule='80')   # NPS 8 Sch 80
db.get_pipe('10', schedule='160') # NPS 10 Sch 160
```

---

## 🧪 Testing

### Run All Tests
```bash
cd /workspaces/Project_Vulcan
PYTHONPATH=/workspaces/Project_Vulcan python scripts/test_validators.py
```

### Expected Output
```
✅ StandardsDB: ALL TESTS PASSED
✅ GDTParser: TESTS PASSED
✅ WeldingValidator: ALL TESTS PASSED
✅ MaterialValidator: ALL TESTS PASSED
✅ ACHEValidator: ALL TESTS PASSED

🎉 ALL VALIDATOR TESTS PASSED!
```

---

## 🔄 External Standards Refresh

### Install Optional Dependencies
```bash
pip install -r scripts/requirements.txt
```

### Pull Fresh Data
```bash
python scripts/pull_from_repos.py
```

This attempts to fetch from 40+ GitHub repos, falls back to local data if unavailable.

---

## 📚 Standards Reference

### GD&T Symbols (ASME Y14.5)
- ⏥ Flatness
- ⊥ Perpendicularity
- ∥ Parallelism
- ⌖ Position
- ○ Circularity
- ∠ Angularity

### AWS D1.1 Minimum Weld Sizes
| Base Metal | Min Fillet |
|-----------|------------|
| ≤ 1/4" | 1/8" |
| 1/4" - 1/2" | 3/16" |
| 1/2" - 3/4" | 1/4" |
| > 3/4" | 5/16" |

### Material Specs
- **A36**: Fy=36 ksi, Fu=58 ksi
- **A516-70**: Fy=38 ksi, Fu=70 ksi (normalized)
- **A572-50**: Fy=50 ksi, Fu=65 ksi
- **304**: 18-20% Cr, 8-10.5% Ni
- **316**: 16-18% Cr, 10-14% Ni, 2-3% Mo

---

## 🚨 Error Handling

### Import Errors
All validators have graceful fallbacks:
```python
try:
    from .standards_db_v2 import StandardsDB
    _db = StandardsDB()
except ImportError:
    _db = None
    logging.warning("Using fallback data")
```

### Missing Data
Returns `None` instead of raising exceptions:
```python
beam = db.get_beam('INVALID')
if beam is None:
    print("Beam not found")
```

---

## 📈 Performance

- **Lookup Time**: <1ms (with @lru_cache)
- **Startup**: Instant (lazy loading)
- **Memory**: ~15 MB for all standards
- **Network**: Zero dependencies

**100-1000x faster than API calls!**

---

## 🔗 See Also

- [PHASE_17_COMPLETION_SUMMARY.md](./PHASE_17_COMPLETION_SUMMARY.md) - Full documentation
- [OFFLINE_STANDARDS_DB_README.md](./OFFLINE_STANDARDS_DB_README.md) - Database guide
- [COMPREHENSIVE_CHECK_RECOMMENDATIONS.md](./ache/COMPREHENSIVE_CHECK_RECOMMENDATIONS.md) - 383 checks
- [ACHE_CHECKLIST.md](./ache/ACHE_CHECKLIST.md) - 130-point master list

---

Last Updated: December 22, 2025
