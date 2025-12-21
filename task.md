# Project Vulcan: Master Task List

**Status**: Phase 14 + 15 + 16 IN PROGRESS - Trading, CAD & ACHE Standards Checker
**Last Updated**: Dec 21, 2025 - ACHE Standards Checker Agent Added
**Goal**: Unified AI Operating System (Trading, CAD, General)
**Pattern**: Adapter + Bridge (lightweight, no cloning)

---

## 🎯 Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Chat response | < 5 sec | ✅ |
| Core files | < 85 | ✅ (~81) |
| Adapter size | < 250 lines | ✅ |
| Agent size | < 500 lines | ✅ |
| System Manager uptime | > 7 days | 🟡 Testing |
| CAD reconstruction | > 90% accuracy | 🟡 Testing |
| Docker deployment | Working | ✅ |
| Circuit breaker | Protecting | ✅ |
| API cost reduction | > 50% | ✅ **90-95%!** |
| Trading module redesign | Complete | 🔄 In Progress |
| CAD module redesign | Complete | 🔲 Planned |
| **ACHE Standards Checker** | Complete | 🔄 In Progress |

---

## 📚 Key References

- `REFERENCES.md` - All external packages
- `config/mcp-servers.json` - MCP registry
- `RULES.md` - Architecture rules (Section 6 = Elite Patterns)
- `CLAUDE.md` - AI instructions
- `docker-compose.yml` - Deployment config
- `TRADING_APP_REDESIGN_PLAN.md` - Full trading module design spec
- `CAD_APP_REDESIGN_PLAN.md` - Full CAD module design spec
- [Anthropic Prompt Caching Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Trading-Guide Repo](https://github.com/swiffc/Trading-Guide) - BTMM content source

### ACHE Standards Checker References (NEW):
- `docs/ache/TASK_LIST.md` - Full 27-task implementation plan
- `docs/ache/ACHE_CHECKLIST.md` - 51-point automatic verification
- `docs/ache/HOLE_PATTERN_DIMS.md` - Hole alignment & dimensions
- `docs/ache/MULTI_DRAWING.md` - Assembly structure & mating parts
- `docs/ache/REPOS_VISUALS.md` - GitHub repos & visual examples
- `docs/ache/REQUIREMENTS_V2.md` - Verification requirements

---

## 🔧 Phase 15: CAD Module Redesign - PLANNED

See `CAD_APP_REDESIGN_PLAN.md` for full details.

### Quick Summary
- **27 new routes** for `/cad/*`
- **60+ new components** (dashboard, projects, drawings, assemblies, parts, ECN, jobs, exports, performance)
- **Full TypeScript types** for CAD entities (Part, Assembly, Drawing, ECN, Job, Project)
- **7-week implementation** checklist
- **Integrates with existing adapters** (SolidWrap, Flatter Files, Performance Manager)

### Key Features
- PLM-style dashboard with job queue and performance monitoring
- Hierarchical BOM visualization with export to Excel/CSV
- ECN workflow management with approval tracking
- Flatter Files integration for drawing search
- Real-time RAM/GPU monitoring with tier indicators
- Part/Assembly/Drawing CRUD with revision history

---

## 🔧 Phase 16: ACHE Standards Checker Agent - IN PROGRESS

See `docs/ache/` folder for full documentation.

### What is ACHE?
Air-Cooled Heat Exchanger (Fin Fan) - NOT shell & tube!
S25139-5A is a PLENUM ASSEMBLY for an ACHE.

```
ACHE STRUCTURE:
                    TUBE BUNDLE (Finned Tubes)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    PLENUM CHAMBER  ← S25139-5A              │
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

### Key Standards
- **API 661** - Air-Cooled Heat Exchangers (primary)
- **OSHA 1910** - Platforms, ladders, handrails
- **AMCA 204** - Fan balance grades
- **AISC** - Structural steel
- **AWS D1.1** - Structural welding

### 27 Tasks to Implement

| Priority | Task | Category |
|----------|------|----------|
| 1 | Standards Database (API 661, OSHA, AISC) | Foundation |
| 2 | Visual Verification Pipeline | Core |
| 3 | ACHE Component Recognition | ACHE |
| 4 | Mating Part Hole Checker | Critical |
| 5 | Fan Ring & Coverage Checker | ACHE/API 661 |
| 6 | Plenum Panel Checker | ACHE |
| 7 | Platform Checker | OSHA |
| 8 | Ladder/Stair/Handrail Checker | OSHA |
| 9 | Edge Distance Checker | Structural |
| 10 | Weight Verification | QC |
| 11 | Louver Checker | ACHE |
| 12 | Weather Protection Checker | ACHE |
| 13 | Winterization Checker | ACHE |
| 14 | Bend Radius Checker | Manufacturing |
| 15 | Description Matcher | Common errors |

### 51 Automatic Checks

| Category | Checks |
|----------|--------|
| Tube Bundle | 8 |
| Plenum | 7 |
| Fan & Drive | 7 |
| Louvers | 5 |
| Weather Protection | 5 |
| Platforms & Access | 9 |
| Structural | 5 |
| Cross-Checks | 5 |
| **TOTAL** | **51** |

### OSHA Requirements (Critical)

| Component | Requirement |
|-----------|-------------|
| Platform width | 30" min (header), 36" min (motor) |
| Handrail height | 42" ± 3" |
| Midrail height | 21" |
| Toe board | 4" min |
| Ladder rung spacing | 12" on center |
| Cage required | > 20' unbroken climb |
| Landing | Every 30' max |

### API 661 Tip Clearances

| Fan Diameter | Max Clearance |
|--------------|---------------|
| 4'-5' | 3/8" |
| 6'-8' | 1/2" |
| 9'-12' | 5/8" |
| 13'-18' | 3/4" |
| 19'-28' | 1" |
| >28' | 1-1/4" |

### Estimated Development Time
**22-28 days total**

| Component | Days |
|-----------|------|
| Standards Database | 3-4 |
| Vision Pipeline | 3-5 |
| ACHE Component Recognition | 2 |
| Mating Part Hole Checker | 2-3 |
| Fan/Plenum/Platform Checkers | 4-5 |
| Integration & Testing | 4-5 |

### GitHub Repos for Implementation

| Repo | Purpose |
|------|---------|
| eDOCr | Engineering drawing OCR |
| Image2CAD | Drawing to DXF |
| steelpy | AISC shape properties |
| python-hvac | Fin-tube HX models |
| OpenCV | Circle/hole detection |

### Industry References

| Source | Content |
|--------|---------|
| Chart Industries | Hudson Products, Tuf-Lite fans |
| API 661 | Air-Cooled Heat Exchangers |
| AMCA 204 | Fan balance grades |
| OSHA 1910 | Access structure requirements |
