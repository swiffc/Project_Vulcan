# Project Vulcan: Master Task List

**Status**: Phase 14 + 15 IN PROGRESS - Trading & CAD Module Redesign
**Last Updated**: Dec 2025 - Trading & CAD Strategic Redesign
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
