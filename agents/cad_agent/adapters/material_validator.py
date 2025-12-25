"""
Material MTR (Mill Test Report) Validator
=========================================
Validates material certifications and traceability per ASME, ASTM standards.

Features:
- Chemical composition verification
- Mechanical properties validation
- Heat treatment verification
- Material traceability (heat numbers)
- NACE MR0175 compliance for sour service

References:
- ASME II Part A: Ferrous Material Specifications
- ASME II Part D: Properties (Customary)
- ASTM A20: General Requirements for Steel Plates
- NACE MR0175/ISO 15156: Sour Service

Usage:
    from agents.cad_agent.adapters.material_validator import MaterialValidator
    
    validator = MaterialValidator()
    result = validator.validate_mtr(mtr_data, design_spec="A516-70")
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import logging

# Import from standards_db_v2 for enhanced material lookups
try:
    from .standards_db_v2 import StandardsDB
    _db = StandardsDB()
except ImportError:
    _db = None
    logging.warning("standards_db_v2 not available, using fallback data")

logger = logging.getLogger("cad_agent.material-validator")


# =============================================================================
# MATERIAL SPECIFICATIONS
# =============================================================================

class MaterialGrade(Enum):
    """Common carbon and alloy steel grades."""
    # Carbon steels
    A36 = "a36"
    A53_B = "a53_b"
    A106_B = "a106_b"
    A516_70 = "a516_70"
    A572_50 = "a572_50"
    
    # Stainless steels
    SS304 = "304"
    SS316 = "316"
    SS321 = "321"
    
    # Alloy steels
    A335_P11 = "a335_p11"
    A335_P22 = "a335_p22"
    A213_T11 = "a213_t11"
    A213_T22 = "a213_t22"


class HeatTreatment(Enum):
    """Heat treatment conditions."""
    AS_ROLLED = "as_rolled"
    NORMALIZED = "normalized"
    NORMALIZED_TEMPERED = "normalized_tempered"
    QUENCHED_TEMPERED = "quenched_tempered"
    ANNEALED = "annealed"
    SOLUTION_ANNEALED = "solution_annealed"
    STRESS_RELIEVED = "stress_relieved"


@dataclass
class ChemicalComposition:
    """Chemical composition from MTR (weight %)."""
    carbon: Optional[float] = None       # C
    manganese: Optional[float] = None    # Mn
    phosphorus: Optional[float] = None   # P
    sulfur: Optional[float] = None       # S
    silicon: Optional[float] = None      # Si
    chromium: Optional[float] = None     # Cr
    nickel: Optional[float] = None       # Ni
    molybdenum: Optional[float] = None   # Mo
    copper: Optional[float] = None       # Cu
    vanadium: Optional[float] = None     # V
    niobium: Optional[float] = None      # Nb (Columbium)
    titanium: Optional[float] = None     # Ti
    aluminum: Optional[float] = None     # Al
    nitrogen: Optional[float] = None     # N
    
    @property
    def carbon_equivalent(self) -> Optional[float]:
        """
        Calculate carbon equivalent (CE) per IIW formula.
        CE = C + Mn/6 + (Cr+Mo+V)/5 + (Ni+Cu)/15
        """
        if self.carbon is None:
            return None
        
        ce = self.carbon
        if self.manganese:
            ce += self.manganese / 6
        if self.chromium or self.molybdenum or self.vanadium:
            ce += (self.chromium or 0 + self.molybdenum or 0 + self.vanadium or 0) / 5
        if self.nickel or self.copper:
            ce += (self.nickel or 0 + self.copper or 0) / 15
        
        return ce


@dataclass
class MechanicalProperties:
    """Mechanical properties from MTR."""
    yield_strength: Optional[float] = None     # ksi or MPa
    tensile_strength: Optional[float] = None   # ksi or MPa
    elongation: Optional[float] = None         # %
    reduction_of_area: Optional[float] = None  # %
    hardness: Optional[float] = None           # Brinell or Rockwell
    charpy_impact: Optional[float] = None      # ft-lbf or Joules
    charpy_temp: Optional[float] = None        # °F or °C
    unit: str = "ksi"  # "ksi" or "MPa"


@dataclass
class MTRData:
    """Mill Test Report data."""
    heat_number: str
    material_spec: str  # e.g., "ASTM A516 Grade 70"
    chemistry: ChemicalComposition
    mechanical: MechanicalProperties
    heat_treatment: Optional[HeatTreatment] = None
    thickness: Optional[float] = None  # inches or mm
    manufacturer: str = ""
    test_date: str = ""
    certificate_number: str = ""


@dataclass
class MaterialSpec:
    """Material specification limits per ASTM."""
    spec_name: str  # e.g., "A516-70"
    
    # Chemical composition limits (weight %)
    carbon_max: Optional[float] = None
    carbon_min: Optional[float] = None
    manganese_max: Optional[float] = None
    manganese_min: Optional[float] = None
    phosphorus_max: float = 0.035  # Typical max
    sulfur_max: float = 0.035      # Typical max
    silicon_max: Optional[float] = None
    silicon_min: Optional[float] = None
    chromium_max: Optional[float] = None
    chromium_min: Optional[float] = None
    nickel_max: Optional[float] = None
    nickel_min: Optional[float] = None
    molybdenum_max: Optional[float] = None
    molybdenum_min: Optional[float] = None
    
    # Mechanical property minimums
    yield_min_ksi: Optional[float] = None
    tensile_min_ksi: Optional[float] = None
    tensile_max_ksi: Optional[float] = None
    elongation_min: Optional[float] = None  # % in 2"
    
    # Impact requirements
    charpy_min_ftlbf: Optional[float] = None
    charpy_temp_f: Optional[float] = None
    
    # Heat treatment
    required_heat_treatment: Optional[HeatTreatment] = None


# =============================================================================
# MATERIAL SPECIFICATIONS DATABASE
# =============================================================================

MATERIAL_SPECS: dict[str, MaterialSpec] = {
    "A36": MaterialSpec(
        spec_name="ASTM A36 Carbon Structural Steel",
        carbon_max=0.26,  # For plates >3/4"
        manganese_min=0.80,  # For Mn steel
        manganese_max=1.20,
        phosphorus_max=0.04,
        sulfur_max=0.05,
        silicon_min=0.15,
        silicon_max=0.40,
        yield_min_ksi=36,
        tensile_min_ksi=58,
        tensile_max_ksi=80,
        elongation_min=20,  # % in 2"
    ),
    
    "A516-70": MaterialSpec(
        spec_name="ASTM A516 Grade 70 Pressure Vessel Plate",
        carbon_max=0.27,  # For ≤2" thick
        manganese_min=0.79,
        manganese_max=1.30,
        phosphorus_max=0.035,
        sulfur_max=0.035,
        silicon_min=0.15,
        silicon_max=0.40,
        yield_min_ksi=38,
        tensile_min_ksi=70,
        tensile_max_ksi=90,
        elongation_min=17,  # % in 2"
        required_heat_treatment=HeatTreatment.NORMALIZED,
    ),
    
    "A572-50": MaterialSpec(
        spec_name="ASTM A572 Grade 50 HSLA Structural Steel",
        carbon_max=0.23,
        manganese_max=1.35,
        phosphorus_max=0.04,
        sulfur_max=0.05,
        silicon_max=0.40,
        yield_min_ksi=50,
        tensile_min_ksi=65,
        elongation_min=18,
    ),
    
    "304": MaterialSpec(
        spec_name="ASTM A240 Type 304 Stainless Steel",
        carbon_max=0.08,
        manganese_max=2.00,
        phosphorus_max=0.045,
        sulfur_max=0.030,
        silicon_max=1.00,
        chromium_min=18.0,
        chromium_max=20.0,
        nickel_min=8.0,
        nickel_max=10.5,
        yield_min_ksi=30,
        tensile_min_ksi=75,
        elongation_min=40,
        required_heat_treatment=HeatTreatment.SOLUTION_ANNEALED,
    ),
    
    "316": MaterialSpec(
        spec_name="ASTM A240 Type 316 Stainless Steel",
        carbon_max=0.08,
        manganese_max=2.00,
        phosphorus_max=0.045,
        sulfur_max=0.030,
        silicon_max=1.00,
        chromium_min=16.0,
        chromium_max=18.0,
        nickel_min=10.0,
        nickel_max=14.0,
        molybdenum_min=2.0,
        molybdenum_max=3.0,
        yield_min_ksi=30,
        tensile_min_ksi=75,
        elongation_min=40,
        required_heat_treatment=HeatTreatment.SOLUTION_ANNEALED,
    ),
}


@dataclass
class MaterialValidationResult:
    """Result of material validation."""
    is_valid: bool
    spec_matched: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)
    chemistry_pass: bool = True
    mechanical_pass: bool = True
    heat_treatment_ok: bool = True


# =============================================================================
# MATERIAL VALIDATOR
# =============================================================================

class MaterialValidator:
    """
    Validate material certifications (MTRs) against specifications.
    
    Features:
    - Chemical composition verification
    - Mechanical properties verification
    - Heat treatment validation
    - Carbon equivalent calculation
    - NACE compliance checking
    """
    
    def __init__(self):
        self.mtrs: list[MTRData] = []
    
    def validate_mtr(self, mtr: MTRData, design_spec: str) -> MaterialValidationResult:
        """
        Validate MTR against design specification.
        
        Args:
            mtr: Mill Test Report data
            design_spec: Required specification (e.g., "A516-70")
        
        Returns:
            MaterialValidationResult
        """
        result = MaterialValidationResult(is_valid=True, spec_matched=False)
        
        # Get specification limits
        spec = MATERIAL_SPECS.get(design_spec.upper().replace(" ", "").replace("ASTM", ""))
        if not spec:
            result.warnings.append(f"Specification {design_spec} not in database")
            return result
        
        result.spec_matched = True
        result.info.append(f"Validating against {spec.spec_name}")
        
        # Validate chemistry
        chem_errors = self._validate_chemistry(mtr.chemistry, spec)
        result.errors.extend(chem_errors)
        result.chemistry_pass = len(chem_errors) == 0
        
        # Validate mechanical properties
        mech_errors = self._validate_mechanical(mtr.mechanical, spec)
        result.errors.extend(mech_errors)
        result.mechanical_pass = len(mech_errors) == 0
        
        # Validate heat treatment
        if spec.required_heat_treatment:
            if mtr.heat_treatment != spec.required_heat_treatment:
                result.warnings.append(
                    f"Heat treatment mismatch: MTR shows {mtr.heat_treatment}, "
                    f"spec requires {spec.required_heat_treatment}"
                )
                result.heat_treatment_ok = False
        
        # Check carbon equivalent for weldability
        if mtr.chemistry.carbon_equivalent:
            ce = mtr.chemistry.carbon_equivalent
            result.info.append(f"Carbon Equivalent (CE): {ce:.3f}")
            
            if ce > 0.45:
                result.warnings.append(
                    f"High carbon equivalent ({ce:.3f}) may require preheat for welding"
                )
            elif ce > 0.40:
                result.info.append("Moderate CE - verify preheat requirements")
        
        # Check traceability
        if not mtr.heat_number:
            result.errors.append("Heat number missing from MTR")
        
        result.is_valid = len(result.errors) == 0
        
        return result
    
    def _validate_chemistry(self, chemistry: ChemicalComposition, spec: MaterialSpec) -> list[str]:
        """Validate chemical composition against spec limits."""
        errors = []
        
        # Carbon
        if chemistry.carbon is not None and spec.carbon_max is not None:
            if chemistry.carbon > spec.carbon_max:
                errors.append(
                    f"Carbon {chemistry.carbon:.3f}% exceeds max {spec.carbon_max:.3f}%"
                )
            if spec.carbon_min and chemistry.carbon < spec.carbon_min:
                errors.append(
                    f"Carbon {chemistry.carbon:.3f}% below min {spec.carbon_min:.3f}%"
                )
        
        # Manganese
        if chemistry.manganese is not None:
            if spec.manganese_max and chemistry.manganese > spec.manganese_max:
                errors.append(
                    f"Manganese {chemistry.manganese:.3f}% exceeds max {spec.manganese_max:.3f}%"
                )
            if spec.manganese_min and chemistry.manganese < spec.manganese_min:
                errors.append(
                    f"Manganese {chemistry.manganese:.3f}% below min {spec.manganese_min:.3f}%"
                )
        
        # Phosphorus (impurity limit)
        if chemistry.phosphorus is not None and chemistry.phosphorus > spec.phosphorus_max:
            errors.append(
                f"Phosphorus {chemistry.phosphorus:.4f}% exceeds max {spec.phosphorus_max:.4f}%"
            )
        
        # Sulfur (impurity limit)
        if chemistry.sulfur is not None and chemistry.sulfur > spec.sulfur_max:
            errors.append(
                f"Sulfur {chemistry.sulfur:.4f}% exceeds max {spec.sulfur_max:.4f}%"
            )
        
        # Silicon
        if chemistry.silicon is not None:
            if spec.silicon_max and chemistry.silicon > spec.silicon_max:
                errors.append(
                    f"Silicon {chemistry.silicon:.3f}% exceeds max {spec.silicon_max:.3f}%"
                )
            if spec.silicon_min and chemistry.silicon < spec.silicon_min:
                errors.append(
                    f"Silicon {chemistry.silicon:.3f}% below min {spec.silicon_min:.3f}%"
                )
        
        # For stainless steel - check Cr, Ni, Mo
        if spec.spec_name and "304" in spec.spec_name:
            if chemistry.chromium and (chemistry.chromium < 18.0 or chemistry.chromium > 20.0):
                errors.append(f"Chromium {chemistry.chromium:.2f}% out of range 18.0-20.0%")
            if chemistry.nickel and (chemistry.nickel < 8.0 or chemistry.nickel > 10.5):
                errors.append(f"Nickel {chemistry.nickel:.2f}% out of range 8.0-10.5%")
        
        return errors
    
    def _validate_mechanical(self, mechanical: MechanicalProperties, spec: MaterialSpec) -> list[str]:
        """Validate mechanical properties against spec limits."""
        errors = []
        
        # Convert units if needed
        ys = mechanical.yield_strength
        ts = mechanical.tensile_strength
        
        if mechanical.unit == "MPa" and spec.yield_min_ksi:
            # Convert MPa to ksi (1 ksi = 6.895 MPa)
            ys = ys / 6.895 if ys else None
            ts = ts / 6.895 if ts else None
        
        # Yield strength
        if ys is not None and spec.yield_min_ksi is not None:
            if ys < spec.yield_min_ksi:
                errors.append(
                    f"Yield strength {ys:.0f} ksi below minimum {spec.yield_min_ksi:.0f} ksi"
                )
        
        # Tensile strength
        if ts is not None:
            if spec.tensile_min_ksi and ts < spec.tensile_min_ksi:
                errors.append(
                    f"Tensile strength {ts:.0f} ksi below minimum {spec.tensile_min_ksi:.0f} ksi"
                )
            if spec.tensile_max_ksi and ts > spec.tensile_max_ksi:
                errors.append(
                    f"Tensile strength {ts:.0f} ksi exceeds maximum {spec.tensile_max_ksi:.0f} ksi"
                )
        
        # Elongation
        if mechanical.elongation is not None and spec.elongation_min is not None:
            if mechanical.elongation < spec.elongation_min:
                errors.append(
                    f"Elongation {mechanical.elongation:.1f}% below minimum {spec.elongation_min:.1f}%"
                )
        
        # Charpy impact (if required)
        if spec.charpy_min_ftlbf:
            if mechanical.charpy_impact is None:
                errors.append(f"Charpy impact test required but not provided")
            elif mechanical.charpy_impact < spec.charpy_min_ftlbf:
                errors.append(
                    f"Charpy impact {mechanical.charpy_impact:.0f} ft-lbf below "
                    f"minimum {spec.charpy_min_ftlbf:.0f} ft-lbf"
                )
        
        return errors
    
    def check_nace_compliance(self, chemistry: ChemicalComposition, hardness: Optional[float]) -> tuple[bool, list[str]]:
        """
        Check NACE MR0175/ISO 15156 compliance for sour service.
        
        Args:
            chemistry: Chemical composition
            hardness: Brinell hardness (HB) or Rockwell C (HRC)
        
        Returns:
            (is_compliant, issues)
        """
        issues = []
        
        # NACE MR0175 hardness limit: 22 HRC (237 HB)
        if hardness:
            if hardness > 237:  # Assuming Brinell
                issues.append(
                    f"Hardness {hardness:.0f} HB exceeds NACE MR0175 limit of 237 HB (22 HRC)"
                )
            elif hardness > 22:  # If Rockwell C
                issues.append(
                    f"Hardness {hardness:.0f} HRC exceeds NACE MR0175 limit of 22 HRC"
                )
        
        # Carbon equivalent limit for NACE
        if chemistry.carbon_equivalent:
            ce = chemistry.carbon_equivalent
            if ce > 0.43:
                issues.append(
                    f"Carbon equivalent {ce:.3f} may not meet NACE requirements (typical max 0.43)"
                )
        
        return len(issues) == 0, issues


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_allowable_stress(material_spec: str, temp_f: float) -> Optional[float]:
    """
    Get allowable stress for material at temperature per ASME II Part D.
    
    Args:
        material_spec: Material specification (e.g., "A516-70")
        temp_f: Design temperature (°F)
    
    Returns:
        Allowable stress (ksi) or None if not found
    """
    # Simplified - real implementation would have full ASME II Part D tables
    
    allowable_stresses_20f = {
        "A36": 14.4,       # 0.4 × YS at 100°F
        "A516-70": 17.1,   # at 100°F
        "A572-50": 20.0,   # at 100°F
        "304": 16.7,       # at 100°F
        "316": 16.7,       # at 100°F
    }
    
    base_stress = allowable_stresses_20f.get(material_spec.upper().replace(" ", ""))
    
    # Temperature reduction factor (simplified)
    if temp_f > 650:
        factor = 0.8  # Significant reduction at elevated temp
    elif temp_f > 400:
        factor = 0.9
    else:
        factor = 1.0
    
    return base_stress * factor if base_stress else None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MaterialValidator",
    "MTRData",
    "ChemicalComposition",
    "MechanicalProperties",
    "MaterialSpec",
    "MaterialGrade",
    "HeatTreatment",
    "MaterialValidationResult",
    "MATERIAL_SPECS",
    "get_allowable_stress",
]
