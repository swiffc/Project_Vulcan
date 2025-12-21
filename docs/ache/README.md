# ACHE Standards Checker Documentation

This folder contains the complete documentation for the ACHE (Air-Cooled Heat Exchanger) Standards Checker Agent.

## Files

| File | Description |
|------|-------------|
| TASK_LIST.md | Complete 27-task implementation plan |
| ACHE_CHECKLIST.md | 51-point automatic verification checklist |
| HOLE_PATTERN_DIMS.md | Hole alignment and dimension requirements |
| MULTI_DRAWING.md | Assembly structure and mating parts |
| REPOS_VISUALS.md | GitHub repos and visual examples |
| REQUIREMENTS_V2.md | Verification requirements |

## Key Standards

- **API 661** - Air-Cooled Heat Exchangers
- **OSHA 1910** - Platforms, ladders, handrails
- **AMCA 204** - Fan balance grades
- **AISC** - Structural steel
- **AWS D1.1** - Structural welding

## ACHE Structure

```
                    TUBE BUNDLE (Finned Tubes)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    PLENUM CHAMBER                           │
│              ┌──────────┐    ┌──────────┐                   │
│              │ FAN RING │    │ FAN RING │                   │
│              └──────────┘    └──────────┘                   │
│     Floor panels, stiffeners, wall panels, corner angles    │
└─────────────────────────────────────────────────────────────┘
                           ↓
              STRUCTURAL SUPPORT FRAME
                           ↓
              PLATFORMS, LADDERS, WALKWAYS
```

## Development Timeline

Estimated: 22-28 days

Created: December 21, 2025