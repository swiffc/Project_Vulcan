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
| **Standards Database** | **91/117** | **26** | **78%** |

---

## Completed Validators (91/117 checks)

| Validator | Checks | Status |
|-----------|--------|--------|
| `aisc_hole_validator.py` | 16 | ✅ Complete |
| `aws_d1_1_validator.py` | 14 | ✅ Complete |
| `api661_bundle_validator.py` | 32 | ✅ Complete |
| `osha_validator.py` | 12 | ✅ Complete |
| `nema_motor_validator.py` | 5 | ✅ Complete |
| `sspc_coating_validator.py` | 6 | ✅ Complete |
| `structural_capacity_validator.py` | - | ✅ Complete |
| `shaft_validator.py` | - | ✅ Complete |
| `handling_validator.py` | - | ✅ Complete |
| `bom_validator.py` | - | ✅ Complete |
| `dimension_validator.py` | - | ✅ Complete |

---

## Remaining Tasks (26 standards checks)

### ASME VIII Pressure Vessel (8 checks) - NOT STARTED

| # | Check | Reference | Priority |
|---|-------|-----------|----------|
| 1 | Minimum wall thickness calculation | UG-27 | High |
| 2 | Nozzle reinforcement | UG-37 | High |
| 3 | Flange rating verification | Appendix 2 | High |
| 4 | Weld joint efficiency | UW-12 | Medium |
| 5 | Hydrostatic test pressure | UG-99 | Medium |
| 6 | MAWP calculation | UG-98 | Medium |
| 7 | Corrosion allowance | UG-25 | Low |
| 8 | Material traceability | UG-93 | Low |

### TEMA Heat Exchanger (6 checks) - NOT STARTED

| # | Check | Reference | Priority |
|---|-------|-----------|----------|
| 1 | Tubesheet thickness | RCB-7 | High |
| 2 | Tube-to-tubesheet joint | RCB-7.4 | High |
| 3 | Baffle spacing | RCB-4.5 | Medium |
| 4 | Tube pitch | RCB-2.2 | Medium |
| 5 | Shell-side velocity | - | Low |
| 6 | Tube-side velocity | - | Low |

### Other Gaps (12 checks)

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

## Quick Reference Tables (Keep)

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

---

**Next Priority**: Create ASME VIII and TEMA validators to reach 100% standards coverage

**Last Updated**: Dec 25, 2025
