# Project Vulcan: Active Task List

**Status**: Phase 25 - Drawing Checker System (IN PROGRESS)
**Last Updated**: Dec 25, 2025
**Overall Health**: 9.9/10 (Production Deployment Ready)

---

## Progress Summary

| Category | Complete | Remaining | % Done |
|----------|----------|-----------|--------|
| Phase 19-23 (Foundation) | 57/58 | 1 (blocked) | 98% |
| Phase 24 (ACHE Design Assistant) | 0/340 | 340 | 0% |
| Phase 25 (Drawing Checker) | 68/150 | 82 | 45% |
| **Standards Database** | **105/117** | **12** | **90%** |

---

## Completed Validators (105/117 checks)

| Validator | Checks | Status |
|-----------|--------|--------|
| `aisc_hole_validator.py` | 16 | ✅ Complete |
| `aws_d1_1_validator.py` | 14 | ✅ Complete |
| `api661_bundle_validator.py` | 32 | ✅ Complete |
| `osha_validator.py` | 12 | ✅ Complete |
| `nema_motor_validator.py` | 5 | ✅ Complete |
| `sspc_coating_validator.py` | 6 | ✅ Complete |
| `asme_viii_validator.py` | 8 | ✅ Complete |
| `tema_validator.py` | 6 | ✅ Complete |
| `structural_capacity_validator.py` | - | ✅ Complete |
| `shaft_validator.py` | - | ✅ Complete |
| `handling_validator.py` | - | ✅ Complete |
| `bom_validator.py` | - | ✅ Complete |
| `dimension_validator.py` | - | ✅ Complete |

---

## Remaining Standards Gaps (12 checks)

| Category | Missing Checks |
|----------|----------------|
| Profile/Cutout | 4 (corner radii, cope dims, notch stress, web openings) |
| Tolerances | 3 (flatness, squareness, parallelism) |
| Sheet Metal | 3 (bend allowance, grain direction, springback) |
| Structural | 2 (member capacity, deflection limits) |

---

## Phase 25 Remaining Tasks (82 tasks)

### 25.1 Geometry (11 remaining)
- [ ] Slot length-to-width ratio
- [ ] Inside corner radii (plasma/laser min)
- [ ] Cope dimensions for weld access
- [ ] Notch stress concentration
- [ ] Web openings for tooling
- [ ] Flatness requirements
- [ ] Squareness requirements
- [ ] Parallelism requirements
- [ ] Bend allowance/K-factor
- [ ] Grain direction
- [ ] Springback consideration

### 25.2 Structural (4 remaining)
- [ ] Member capacity (channels, angles)
- [ ] Connection capacity
- [ ] Deflection limits specified
- [ ] Fatigue consideration

### 25.3-25.13 (67 remaining)
- 25.3 Fabrication Feasibility (~8 tasks)
- 25.4 Welding (~6 tasks)
- 25.5 Machining/Shaft (~3 tasks)
- 25.6 Materials & Finishing (~8 tasks)
- 25.7 Hardware & Fasteners (~6 tasks)
- 25.8 Handling & Erection (~2 tasks)
- 25.9 Inspection & QC (~10 tasks)
- 25.10 Documentation (~8 tasks)
- 25.11 Safety & Code (~6 tasks)
- 25.12 Cross-Part Reference (~5 tasks)
- 25.13 Report Generation (~5 tasks)

---

## Phase 24: ACHE Design Assistant (340 tasks) - NOT STARTED

Major feature areas:
- Auto-Launch System
- Model Overview Tab
- Properties Extraction
- Analysis & Calculations
- Structural Components
- Walkways, Handrails, Ladders
- AI Features & Integration
- Field Erection Support

---

## Quick Reference Tables

### AISC J3.3 - Hole Dimensions
| Bolt | Std | Oversized | Short-Slot | Long-Slot |
|------|-----|-----------|------------|-----------|
| 3/4" | 13/16" | 15/16" | 13/16"×1" | 13/16"×1-7/8" |
| 7/8" | 15/16" | 1-1/16" | 15/16"×1-1/8" | 15/16"×2-3/16" |
| 1" | 1-1/8" | 1-1/4" | 1-1/8"×1-5/16" | 1-1/8"×2-1/2" |

### AWS D1.1 - Min Fillet Size
| Thickness | Min Fillet |
|-----------|------------|
| ≤1/4" | 1/8" |
| 1/4"-1/2" | 3/16" |
| 1/2"-3/4" | 1/4" |
| >3/4" | 5/16" |

### OSHA Ladder (2018 Final Rule)
| Parameter | Requirement |
|-----------|-------------|
| Fall protection trigger | >24 ft (not 20 ft) |
| New installs after 11/19/2018 | PFAS or LAD only (no cages) |
| All ladders by 11/18/2036 | Must have PFAS/LAD |

### API 661 Fan Tip Clearance
| Fan Dia | Min | Max |
|---------|-----|-----|
| ≤10 ft | 1/4" | 1/2" |
| 10-11.5 ft | 1/4" | 5/8" |
| >11.5 ft | 1/4" | 3/4" |

### ASME VIII - Wall Thickness (UG-27)
| Material | Max Allowable Stress (psi) at 650°F |
|----------|-------------------------------------|
| SA-516-70 | 17,500 |
| SA-516-60 | 15,000 |
| SA-240-304 | 15,600 |
| SA-240-316 | 16,300 |

### TEMA Tubesheet Thickness Factor
| Class | Factor × Tube OD |
|-------|------------------|
| R (Petroleum) | 0.75 |
| C (Commercial) | 0.625 |
| B (Chemical) | 0.50 |

---

**Next Priority**: Complete remaining 12 geometry/tolerance validators to reach 100% standards coverage

**Last Updated**: Dec 25, 2025
