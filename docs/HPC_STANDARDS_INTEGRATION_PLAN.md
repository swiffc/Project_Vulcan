# HPC Standards Integration Plan - Complete Implementation Guide

**Date**: December 25, 2025  
**Status**: Ready for Implementation  
**Scope**: Full integration of HPC Standards Books I-IV into Project Vulcan

---

## Executive Summary

This plan provides a **complete roadmap** for integrating 98,116 extracted HPC standards items into Project Vulcan's CAD validation system. The integration follows existing patterns and extends current capabilities without breaking changes.

**Key Metrics:**
- **31,357** standard parts extracted
- **6,780** design rules extracted
- **60,979** specifications extracted
- **5** standard lifting lug parts (W708-W712)
- **1,733** pages of source material

---

## 1. Architecture Overview

### Current System Architecture

```
Project_Vulcan/
├── data/standards/              # JSON standards files
│   ├── aisc_shapes.json
│   ├── fasteners.json
│   ├── materials.json
│   ├── pipe_schedules.json
│   ├── api_661_data.json
│   └── hpc/                     # NEW: HPC standards
│       ├── hpc_standard_parts.json
│       ├── hpc_design_rules.json
│       ├── hpc_specifications.json
│       └── hpc_lifting_lugs.json
│
├── agents/cad_agent/
│   ├── adapters/
│   │   ├── standards_db_v2.py  # EXTEND: Add HPC methods
│   │   └── ...
│   └── validators/
│       ├── handling_validator.py    # ENHANCE: Add HPC lifting lug checks
│       ├── rigging_validator.py     # ENHANCE: Add HPC rigging standards
│       ├── pdf_validation_engine.py # EXTEND: Add HPC validation
│       └── hpc_*.py                 # NEW: HPC-specific validators
│
└── desktop_server/
    └── controllers/
        └── cad_validation.py    # EXTEND: Add HPC validation endpoints
```

---

## 2. Integration Points

### 2.1 Standards Database Extension

**File**: `agents/cad_agent/adapters/standards_db_v2.py`

**Current Pattern:**
```python
class StandardsDB:
    @lru_cache(maxsize=1)
    def _load_aisc_shapes(self) -> Dict[str, Any]:
        with open(self.data_dir / "aisc_shapes.json") as f:
            return json.load(f)
    
    def get_beam(self, designation: str) -> Optional[BeamProperties]:
        # Lookup logic
```

**Integration Plan:**

#### A. Add HPC Data Classes

```python
@dataclass
class HPCLiftingLug:
    """HPC standard lifting lug."""
    part_number: str  # W708, W709, etc.
    thickness_in: float
    width_in: float
    block_out_dimensions: Dict[str, float]  # A, B, C
    description: str

@dataclass
class HPCStandardPart:
    """HPC standard part."""
    part_number: str
    description: str
    category: str
    specifications: Dict[str, Any]
    source_book: str
    source_page: int

@dataclass
class HPCDesignRule:
    """HPC design rule or formula."""
    rule_id: str
    title: str
    description: str
    formula: Optional[str]
    category: str
```

#### B. Add HPC Load Methods

```python
@lru_cache(maxsize=1)
def _load_hpc_lifting_lugs(self) -> Dict[str, Any]:
    """Load HPC lifting lug standards."""
    try:
        with open(self.data_dir / "hpc" / "hpc_lifting_lugs.json") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("hpc_lifting_lugs.json not found")
        return {}

@lru_cache(maxsize=1)
def _load_hpc_standard_parts(self) -> Dict[str, Any]:
    """Load HPC standard parts."""
    try:
        with open(self.data_dir / "hpc" / "hpc_standard_parts.json") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("hpc_standard_parts.json not found")
        return {}
```

#### C. Add HPC Lookup Methods

```python
def get_hpc_lifting_lug(self, part_number: str) -> Optional[HPCLiftingLug]:
    """
    Get HPC lifting lug specifications.
    
    Args:
        part_number: Part number (e.g., "W708", "W709")
    
    Returns:
        HPCLiftingLug or None
    """
    lugs_data = self._load_hpc_lifting_lugs()
    parts = lugs_data.get("lifting_lug_standards", {}).get("standard_parts", [])
    
    for lug_data in parts:
        if lug_data.get("part_number") == part_number.upper():
            return HPCLiftingLug(**lug_data)
    return None

def get_hpc_standard_part(self, part_number: str) -> Optional[HPCStandardPart]:
    """Get HPC standard part by part number."""
    parts_data = self._load_hpc_standard_parts()
    parts = parts_data.get("parts", [])
    
    for part_data in parts:
        if part_data.get("part_number") == part_number.upper():
            return HPCStandardPart(**part_data)
    return None

def search_hpc_parts(self, category: str = None, keyword: str = None) -> List[HPCStandardPart]:
    """Search HPC standard parts by category or keyword."""
    parts_data = self._load_hpc_standard_parts()
    parts = parts_data.get("parts", [])
    results = []
    
    for part_data in parts:
        if category and part_data.get("category") != category:
            continue
        if keyword and keyword.lower() not in part_data.get("description", "").lower():
            continue
        results.append(HPCStandardPart(**part_data))
    
    return results
```

**Implementation Priority**: ⭐⭐⭐ **HIGH**  
**Estimated Time**: 4-6 hours  
**Dependencies**: None (uses existing pattern)

---

### 2.2 Handling Validator Enhancement

**File**: `agents/cad_agent/validators/handling_validator.py`

**Current State:**
- Has generic lifting lug capacity checks
- Uses hardcoded capacity table
- No HPC-specific part number validation

**Integration Plan:**

#### A. Import HPC Standards

```python
from agents.cad_agent.adapters.standards_db_v2 import StandardsDB, get_standards_db

class HandlingValidator:
    def __init__(self):
        self.standards_db = get_standards_db()
        self.hpc_lug_requirements = self._load_hpc_lug_requirements()
    
    def _load_hpc_lug_requirements(self) -> Dict[str, Any]:
        """Load HPC lifting lug requirements."""
        lugs_data = self.standards_db._load_hpc_lifting_lugs()
        return lugs_data.get("lifting_lug_standards", {}).get("requirements", {})
```

#### B. Add HPC-Specific Checks

```python
def _check_hpc_lifting_lug_part_number(
    self, 
    handling: HandlingData, 
    result: HandlingValidationResult
):
    """Check if lifting lug part number matches HPC standards."""
    if not handling.has_lifting_lugs:
        return
    
    result.total_checks += 1
    
    # Extract part number from drawing (if available)
    lug_part_number = getattr(handling, 'lug_part_number', None)
    
    if lug_part_number:
        hpc_lug = self.standards_db.get_hpc_lifting_lug(lug_part_number)
        if hpc_lug:
            result.passed += 1
            logger.info(f"Valid HPC lifting lug: {lug_part_number}")
        else:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="hpc_lug_part_number",
                message=f"Lifting lug part number '{lug_part_number}' not found in HPC standards",
                suggestion="Use standard HPC part: W708, W709, W710, W711, or W712"
            ))
    else:
        result.warnings += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            check_type="hpc_lug_part_number_missing",
            message="Lifting lug part number not specified",
            suggestion="Specify HPC standard part number (W708-W712)"
        ))

def _check_hpc_lug_quantity_requirement(
    self,
    handling: HandlingData,
    result: HandlingValidationResult,
    tube_length_ft: Optional[float] = None
):
    """Check HPC quantity requirement: 4 lugs for 50' or 60' tubes."""
    if not tube_length_ft:
        return  # Can't check without tube length
    
    result.total_checks += 1
    
    # HPC requirement: 4 lugs for units with 50' or 60' long tubes
    requires_4_lugs = tube_length_ft >= 50.0
    
    if requires_4_lugs and handling.num_lifting_lugs < 4:
        result.failed += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.CRITICAL,
            check_type="hpc_lug_quantity",
            message=f"HPC standard requires 4 lifting lugs for {tube_length_ft}' tubes, found {handling.num_lifting_lugs}",
            suggestion="Add lifting lugs to meet HPC requirement (4 lugs minimum)"
        ))
    elif requires_4_lugs and handling.num_lifting_lugs >= 4:
        result.passed += 1
    else:
        result.passed += 1  # Below threshold, quantity OK

def _check_hpc_lug_spacing(
    self,
    handling: HandlingData,
    result: HandlingValidationResult,
    lug_spacing_ft: Optional[float] = None
):
    """Check HPC maximum spacing: 23'-0\" centerline to centerline."""
    if not lug_spacing_ft or handling.num_lifting_lugs < 2:
        return
    
    result.total_checks += 1
    
    max_spacing_ft = self.hpc_lug_requirements.get("max_centerline_spacing_ft", 23.0)
    
    if lug_spacing_ft > max_spacing_ft:
        result.failed += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.CRITICAL,
            check_type="hpc_lug_spacing",
            message=f"Lifting lug spacing {lug_spacing_ft}' exceeds HPC maximum {max_spacing_ft}'",
            suggestion=f"Reduce spacing to ≤ {max_spacing_ft}' centerline to centerline"
        ))
    else:
        result.passed += 1
```

#### C. Update validate() Method

```python
def validate(self, handling: HandlingData, **kwargs) -> HandlingValidationResult:
    """Validate handling requirements (enhanced with HPC checks)."""
    result = HandlingValidationResult()
    result.weight_lbs = handling.total_weight_lbs
    
    # Existing checks
    self._check_lifting_lugs(handling, result)
    self._check_lug_capacity(handling, result)
    self._check_cg_marking(handling, result)
    # ... other existing checks
    
    # NEW: HPC-specific checks
    tube_length_ft = kwargs.get("tube_length_ft")
    lug_spacing_ft = kwargs.get("lug_spacing_ft")
    lug_part_number = kwargs.get("lug_part_number")
    
    if lug_part_number:
        handling.lug_part_number = lug_part_number
    
    self._check_hpc_lifting_lug_part_number(handling, result)
    self._check_hpc_lug_quantity_requirement(handling, result, tube_length_ft)
    self._check_hpc_lug_spacing(handling, result, lug_spacing_ft)
    
    return result
```

**Implementation Priority**: ⭐⭐⭐ **HIGH**  
**Estimated Time**: 6-8 hours  
**Dependencies**: StandardsDB extension (2.1)

---

### 2.3 Create HPC Mechanical Validator

**File**: `agents/cad_agent/validators/hpc_mechanical_validator.py` (NEW)

**Purpose**: Validate machinery mounts, fans, shafts per HPC standards

**Integration Plan:**

```python
"""
HPC Mechanical Validator
========================
Validates machinery mounts, fans, shafts per HPC Standards Book II Vol. I.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from agents.cad_agent.adapters.standards_db_v2 import StandardsDB, get_standards_db
from .validation_models import ValidationIssue, ValidationSeverity

@dataclass
class HPCMechanicalData:
    """Data for HPC mechanical validation."""
    machinery_mount_type: Optional[str] = None  # "forced_draft", "induced_draft"
    fan_diameter_ft: Optional[float] = None
    vibration_switch_mounted: bool = False
    vibration_switch_location: Optional[Dict[str, float]] = None
    diagonal_brace_spacing_in: Optional[float] = None

@dataclass
class HPCMechanicalValidationResult:
    """HPC mechanical validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

class HPCMechanicalValidator:
    """Validates HPC mechanical components."""
    
    def __init__(self):
        self.standards_db = get_standards_db()
        self._load_hpc_mechanical_standards()
    
    def _load_hpc_mechanical_standards(self):
        """Load HPC mechanical standards from JSON."""
        # Load from hpc_machinery_mounts.json (to be created)
        pass
    
    def validate(self, data: HPCMechanicalData) -> HPCMechanicalValidationResult:
        """Validate HPC mechanical components."""
        result = HPCMechanicalValidationResult()
        
        # Check vibration switch location
        self._check_vibration_switch_location(data, result)
        
        # Check diagonal brace spacing
        self._check_diagonal_brace_spacing(data, result)
        
        # Check machinery mount length formulas
        self._check_machinery_mount_length(data, result)
        
        return result
    
    def _check_vibration_switch_location(self, data: HPCMechanicalData, result: HPCMechanicalValidationResult):
        """Check vibration switch location: 1' from fan centerline, 6" from top."""
        if not data.vibration_switch_mounted:
            return
        
        result.total_checks += 1
        
        if data.vibration_switch_location:
            # HPC standard: 1' from fan centerline, 6" from top
            from_centerline = data.vibration_switch_location.get("from_centerline_ft", 0)
            from_top = data.vibration_switch_location.get("from_top_in", 0)
            
            if abs(from_centerline - 1.0) > 0.1 or abs(from_top - 6.0) > 0.5:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="hpc_vibration_switch_location",
                    message=f"Vibration switch location deviates from HPC standard (1' from centerline, 6\" from top)",
                    suggestion="Relocate to HPC standard position"
                ))
            else:
                result.passed += 1
```

**Implementation Priority**: ⭐⭐ **MEDIUM**  
**Estimated Time**: 8-10 hours  
**Dependencies**: StandardsDB extension, machinery mounts JSON file

---

### 2.4 Create HPC Walkway Validator

**File**: `agents/cad_agent/validators/hpc_walkway_validator.py` (NEW)

**Purpose**: Validate walkways, ladders, handrails per HPC Standards Book II Vol. II

**Integration Plan:**

```python
"""
HPC Walkway Validator
=====================
Validates walkways, ladders, handrails per HPC Standards Book II Vol. II.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from agents.cad_agent.adapters.standards_db_v2 import StandardsDB, get_standards_db
from .validation_models import ValidationIssue, ValidationSeverity

@dataclass
class HPCWalkwayData:
    """Data for HPC walkway validation."""
    ladder_rung_material: Optional[str] = None
    toe_plate_type: Optional[str] = None  # "PRL" or "FB"
    handrail_detailing_method: Optional[str] = None  # "plan_view" or other
    walkway_width_in: Optional[float] = None

@dataclass
class HPCWalkwayValidationResult:
    """HPC walkway validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

class HPCWalkwayValidator:
    """Validates HPC walkway standards."""
    
    def __init__(self):
        self.standards_db = get_standards_db()
        self._load_hpc_walkway_standards()
    
    def _load_hpc_walkway_standards(self):
        """Load HPC walkway standards."""
        # Load from hpc_walkway_standards.json (to be created)
        pass
    
    def validate(self, data: HPCWalkwayData) -> HPCWalkwayValidationResult:
        """Validate HPC walkway components."""
        result = HPCWalkwayValidationResult()
        
        # Check ladder rung material (#6 rebar)
        self._check_ladder_rung_material(data, result)
        
        # Check toe-plate design (PRL 4-1/2" x 2" x 1/4")
        self._check_toe_plate_design(data, result)
        
        # Check handrail detailing method (plan-view)
        self._check_handrail_detailing(data, result)
        
        return result
    
    def _check_ladder_rung_material(self, data: HPCWalkwayData, result: HPCWalkwayValidationResult):
        """Check ladder rung is #6 rebar per HPC standard."""
        result.total_checks += 1
        
        if data.ladder_rung_material:
            if "#6" in data.ladder_rung_material.upper() or "REBAR" in data.ladder_rung_material.upper():
                result.passed += 1
            else:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="hpc_ladder_rung_material",
                    message=f"Ladder rung material '{data.ladder_rung_material}' does not match HPC standard (#6 rebar)",
                    suggestion="Use #6 rebar for ladder rungs per HPC standard"
                ))
        else:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="hpc_ladder_rung_material_missing",
                message="Ladder rung material not specified",
                suggestion="Specify #6 rebar per HPC standard"
            ))
```

**Implementation Priority**: ⭐⭐ **MEDIUM**  
**Estimated Time**: 6-8 hours  
**Dependencies**: StandardsDB extension, walkway standards JSON file

---

### 2.5 PDF Validation Engine Integration

**File**: `agents/cad_agent/validators/pdf_validation_engine.py`

**Current State:**
- Orchestrates multiple validators
- Supports standards list: `["api_661", "asme", "aws_d1_1", "osha", "bom", "dimension", "completeness"]`

**Integration Plan:**

```python
# Add HPC validators to imports
from .hpc_mechanical_validator import HPCMechanicalValidator, HPCMechanicalData
from .hpc_walkway_validator import HPCWalkwayValidator, HPCWalkwayData
from .handling_validator import HandlingValidator  # Already enhanced

class PDFValidationEngine:
    def __init__(self):
        # ... existing initializations ...
        
        # NEW: Initialize HPC validators
        self.hpc_mechanical = HPCMechanicalValidator()
        self.hpc_walkway = HPCWalkwayValidator()
        # handling_validator already enhanced with HPC checks
    
    def validate(
        self,
        pdf_path: str,
        standards: Optional[List[str]] = None
    ) -> PDFValidationResult:
        # ... existing validation ...
        
        # NEW: Add HPC validation
        if "hpc" in standards or standards is None:
            logger.info("Running HPC validation...")
            
            # Extract HPC-specific data from extraction
            hpc_mechanical_data = self._extract_hpc_mechanical_data(extraction)
            hpc_walkway_data = self._extract_hpc_walkway_data(extraction)
            handling_data = self._extract_handling_data(extraction)
            
            # Run HPC validations
            hpc_mechanical_result = self.hpc_mechanical.validate(hpc_mechanical_data)
            hpc_walkway_result = self.hpc_walkway.validate(hpc_walkway_data)
            handling_result = self.handling.validate(handling_data, **hpc_kwargs)
            
            # Add to result
            result.hpc_results = {
                "mechanical": self.hpc_mechanical.to_dict(hpc_mechanical_result),
                "walkway": self.hpc_walkway.to_dict(hpc_walkway_result),
                "handling": self.handling.to_dict(handling_result)
            }
            
            self._aggregate_results(result, hpc_mechanical_result)
            self._aggregate_results(result, hpc_walkway_result)
            self._aggregate_results(result, handling_result)
```

**Implementation Priority**: ⭐⭐⭐ **HIGH**  
**Estimated Time**: 4-6 hours  
**Dependencies**: HPC validators (2.3, 2.4), HandlingValidator enhancement (2.2)

---

### 2.6 Design Recommender Integration

**File**: `agents/design_recommender/agent.py` (if exists)

**Purpose**: Use HPC design rules to recommend standard parts and configurations

**Integration Plan:**

```python
from agents.cad_agent.adapters.standards_db_v2 import StandardsDB, get_standards_db

class DesignRecommender:
    def __init__(self):
        self.standards_db = get_standards_db()
    
    def recommend_lifting_lug(
        self,
        weight_lbs: float,
        tube_length_ft: float,
        num_lugs: int = 4
    ) -> Dict[str, Any]:
        """Recommend HPC lifting lug based on requirements."""
        # HPC requirement: 4 lugs for 50' or 60' tubes
        if tube_length_ft >= 50.0:
            recommended_lugs = 4
        else:
            recommended_lugs = 2
        
        # Get default HPC lug (W708)
        default_lug = self.standards_db.get_hpc_lifting_lug("W708")
        
        # Calculate required capacity per lug
        required_capacity = (weight_lbs / recommended_lugs) * 2  # 2:1 safety factor
        
        # Recommend appropriate lug size
        if required_capacity <= 9000:
            recommended = "W708"  # 3/4" × 5-1/2"
        elif required_capacity <= 15000:
            recommended = "W711"  # 1" × 7"
        else:
            recommended = "W712"  # 1" × 8"
        
        return {
            "recommended_part_number": recommended,
            "recommended_quantity": recommended_lugs,
            "required_capacity_per_lug_lbs": required_capacity,
            "hpc_standard": True
        }
```

**Implementation Priority**: ⭐⭐ **MEDIUM**  
**Estimated Time**: 6-8 hours  
**Dependencies**: StandardsDB extension

---

## 3. Implementation Phases

### Phase 1: Foundation (Week 1) ⭐⭐⭐ HIGH PRIORITY

**Goal**: Extend StandardsDB with HPC data

**Tasks:**
1. ✅ Add HPC data classes to `standards_db_v2.py`
2. ✅ Add `_load_hpc_*()` methods with @lru_cache
3. ✅ Add `get_hpc_lifting_lug()` method
4. ✅ Add `get_hpc_standard_part()` method
5. ✅ Add `search_hpc_parts()` method
6. ✅ Unit tests for HPC lookups

**Deliverables:**
- Extended `standards_db_v2.py`
- Unit tests passing
- Documentation updated

**Estimated Time**: 4-6 hours

---

### Phase 2: Handling Validator Enhancement (Week 1-2) ⭐⭐⭐ HIGH PRIORITY

**Goal**: Add HPC lifting lug validation

**Tasks:**
1. ✅ Import StandardsDB into `handling_validator.py`
2. ✅ Add `_check_hpc_lifting_lug_part_number()`
3. ✅ Add `_check_hpc_lug_quantity_requirement()`
4. ✅ Add `_check_hpc_lug_spacing()`
5. ✅ Update `validate()` method signature
6. ✅ Integration tests

**Deliverables:**
- Enhanced `handling_validator.py`
- HPC lifting lug checks working
- Tests passing

**Estimated Time**: 6-8 hours

---

### Phase 3: HPC Validators (Week 2-3) ⭐⭐ MEDIUM PRIORITY

**Goal**: Create HPC-specific validators

**Tasks:**
1. ✅ Create `hpc_mechanical_validator.py`
2. ✅ Create `hpc_walkway_validator.py`
3. ✅ Create `hpc_header_validator.py` (if needed)
4. ✅ Create `hpc_parts_validator.py` (if needed)
5. ✅ Unit tests for each validator

**Deliverables:**
- 2-4 new HPC validators
- Tests passing
- Documentation

**Estimated Time**: 20-30 hours total

---

### Phase 4: Integration (Week 3-4) ⭐⭐⭐ HIGH PRIORITY

**Goal**: Integrate HPC validators into validation engine

**Tasks:**
1. ✅ Update `pdf_validation_engine.py`
2. ✅ Add HPC data extraction methods
3. ✅ Add HPC validation to standards list
4. ✅ Update result aggregation
5. ✅ Integration tests

**Deliverables:**
- HPC validation in main engine
- End-to-end tests passing
- API endpoints updated

**Estimated Time**: 4-6 hours

---

### Phase 5: Design Recommender (Week 4) ⭐⭐ MEDIUM PRIORITY

**Goal**: Add HPC recommendations

**Tasks:**
1. ✅ Extend design recommender with HPC rules
2. ✅ Add lifting lug recommendations
3. ✅ Add standard parts recommendations
4. ✅ Tests

**Deliverables:**
- Enhanced design recommender
- HPC recommendations working

**Estimated Time**: 6-8 hours

---

## 4. File Structure After Integration

```
agents/cad_agent/
├── adapters/
│   ├── standards_db_v2.py          # EXTENDED: HPC methods added
│   └── ...
│
└── validators/
    ├── handling_validator.py       # ENHANCED: HPC lifting lug checks
    ├── rigging_validator.py        # ENHANCED: HPC rigging standards
    ├── hpc_mechanical_validator.py # NEW: Machinery mounts, fans
    ├── hpc_walkway_validator.py    # NEW: Walkways, ladders
    ├── hpc_header_validator.py     # NEW: Header design (optional)
    ├── pdf_validation_engine.py    # EXTENDED: HPC validation added
    └── ...

data/standards/
├── hpc/
│   ├── hpc_lifting_lugs.json       # ✅ EXISTS
│   ├── hpc_standard_parts.json     # ✅ EXISTS
│   ├── hpc_design_rules.json       # ✅ EXISTS
│   ├── hpc_specifications.json    # ✅ EXISTS
│   ├── hpc_machinery_mounts.json  # TO CREATE
│   ├── hpc_walkway_standards.json # TO CREATE
│   └── hpc_header_design.json     # TO CREATE
│
└── ... (existing standards)
```

---

## 5. Testing Strategy

### Unit Tests

**File**: `tests/test_hpc_standards_integration.py` (NEW)

```python
import pytest
from agents.cad_agent.adapters.standards_db_v2 import StandardsDB
from agents.cad_agent.validators.handling_validator import HandlingValidator, HandlingData

def test_get_hpc_lifting_lug():
    """Test HPC lifting lug lookup."""
    db = StandardsDB()
    lug = db.get_hpc_lifting_lug("W708")
    assert lug is not None
    assert lug.part_number == "W708"
    assert lug.thickness_in == 0.75
    assert lug.width_in == 5.5

def test_hpc_lug_quantity_check():
    """Test HPC quantity requirement check."""
    validator = HandlingValidator()
    handling = HandlingData(
        total_weight_lbs=1000,
        has_lifting_lugs=True,
        num_lifting_lugs=2
    )
    result = validator.validate(handling, tube_length_ft=55.0)
    assert result.failed > 0  # Should fail: need 4 lugs for 55' tubes

def test_hpc_lug_spacing_check():
    """Test HPC spacing requirement check."""
    validator = HandlingValidator()
    handling = HandlingData(
        total_weight_lbs=1000,
        has_lifting_lugs=True,
        num_lifting_lugs=4
    )
    result = validator.validate(handling, lug_spacing_ft=25.0)
    assert result.failed > 0  # Should fail: 25' > 23' max
```

### Integration Tests

**File**: `tests/test_hpc_validation_integration.py` (NEW)

```python
def test_hpc_validation_in_pdf_engine():
    """Test HPC validation in PDF validation engine."""
    engine = PDFValidationEngine()
    result = engine.validate("test_drawing.pdf", standards=["hpc"])
    assert "hpc_results" in result.to_dict()
    assert "handling" in result.hpc_results
```

---

## 6. API Endpoints

**File**: `desktop_server/controllers/cad_validation.py`

**Integration Plan:**

```python
@router.post("/validate/hpc")
async def validate_hpc(request: ValidateDrawingRequest):
    """Validate drawing against HPC standards."""
    orchestrator = get_orchestrator()
    
    # Extract HPC-specific data
    hpc_data = extract_hpc_data(request.drawing_path)
    
    # Run HPC validations
    result = await orchestrator.validate_hpc(hpc_data)
    
    return result
```

---

## 7. Success Metrics

### Phase 1 Success Criteria
- ✅ HPC lifting lug lookup works: `db.get_hpc_lifting_lug("W708")` returns data
- ✅ All unit tests pass
- ✅ No breaking changes to existing code

### Phase 2 Success Criteria
- ✅ HPC lifting lug checks run automatically
- ✅ Part number validation works
- ✅ Quantity requirement check works
- ✅ Spacing check works

### Phase 3 Success Criteria
- ✅ All HPC validators created
- ✅ Integration tests pass
- ✅ Validation reports include HPC results

### Overall Success Criteria
- ✅ 100% of HPC lifting lug standards integrated
- ✅ Validation accuracy >95%
- ✅ Performance: <100ms for HPC lookups
- ✅ Zero breaking changes to existing validators

---

## 8. Risk Mitigation

### Risk 1: Breaking Changes
**Mitigation**: 
- All changes are additive (new methods, new validators)
- Existing code continues to work
- Backward compatibility maintained

### Risk 2: Performance Impact
**Mitigation**:
- Use @lru_cache for JSON loading
- Lazy loading of HPC data
- Only load when needed

### Risk 3: Data Quality
**Mitigation**:
- Validate JSON structure
- Unit tests for data loading
- Fallback to empty dict if file missing

---

## 9. Next Steps

### Immediate (This Week)
1. ✅ **Review this plan** - Confirm approach
2. ✅ **Start Phase 1** - Extend StandardsDB
3. ✅ **Create unit tests** - Test HPC lookups

### Short-term (Next 2 Weeks)
4. ✅ **Complete Phase 2** - Enhance HandlingValidator
5. ✅ **Start Phase 3** - Create HPC validators
6. ✅ **Integration testing** - End-to-end validation

### Medium-term (Next Month)
7. ✅ **Complete Phase 4** - Full integration
8. ✅ **Phase 5** - Design recommender
9. ✅ **Documentation** - User guides

---

## 10. Quick Reference

### Key Files to Modify
1. `agents/cad_agent/adapters/standards_db_v2.py` - Add HPC methods
2. `agents/cad_agent/validators/handling_validator.py` - Add HPC checks
3. `agents/cad_agent/validators/pdf_validation_engine.py` - Integrate HPC

### Key Files to Create
1. `agents/cad_agent/validators/hpc_mechanical_validator.py`
2. `agents/cad_agent/validators/hpc_walkway_validator.py`
3. `tests/test_hpc_standards_integration.py`

### Key Data Files
1. `data/standards/hpc/hpc_lifting_lugs.json` ✅ EXISTS
2. `data/standards/hpc/hpc_standard_parts.json` ✅ EXISTS
3. `data/standards/hpc/hpc_machinery_mounts.json` - TO CREATE
4. `data/standards/hpc/hpc_walkway_standards.json` - TO CREATE

---

**Document Version**: 1.0  
**Last Updated**: December 25, 2025  
**Status**: Ready for Implementation  
**Estimated Total Time**: 40-60 hours  
**Priority**: HIGH for lifting lugs, MEDIUM for other components

