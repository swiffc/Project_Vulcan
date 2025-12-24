# Pre-Task Checklist (COMPREHENSIVE)

**Claude: Read RULES.md and this checklist BEFORE starting any task.**

---

## Step 0: ALWAYS Do This First

- [ ] Scan RULES.md (all 8 sections)
- [ ] State: "Checked RULES.md - relevant sections: [list them]"
- [ ] If CAD task: Create PLAN file, show to user, wait for approval

---

## Complete Rule Coverage

### Section 1: Project Overview
- [ ] Understand the architecture (cloud + local PC)
- [ ] Know which agent handles this task (Trading, CAD, Work, General)
- [ ] Understand the data flow (Web -> Orchestrator -> VPN -> Desktop Server)

### Section 2: Remote Repository References
- [ ] Check if external GitHub repos have solutions
- [ ] Don't clone repos - reference them via raw URLs
- [ ] Use existing implementations before writing new

### Section 3: Tech Stack
- [ ] Frontend: Next.js 14, TypeScript, Tailwind, shadcn/ui
- [ ] Backend: FastAPI (Python), PostgreSQL
- [ ] Desktop: pyautogui, win32com, playwright
- [ ] Use correct technologies per the stack

### Section 4: Coding Conventions
- [ ] Follow naming patterns (kebab-case files, PascalCase components)
- [ ] Use existing code patterns in the codebase
- [ ] Error handling follows project patterns

### Section 5: File & Folder Structure
- [ ] Put files in correct directories
- [ ] Follow naming conventions
- [ ] Check if similar files exist before creating new

### Section 6: Safety & Security
- [ ] Never expose secrets
- [ ] Use environment variables for sensitive data
- [ ] Follow CORS and authentication patterns
- [ ] Test locally before production

### Section 7: Mechanical Engineering (CAD) - CRITICAL
- [ ] **Rule 25**: Think like a mechanical engineer, not shape drawer
- [ ] **Rule 26**: Standard parts first (buy before make)
- [ ] **Rule 27**: Manufacturing awareness (how is it made?)
- [ ] **Rule 28**: What to ask before building
- [ ] **Rule 29**: CAD strategy file format
- [ ] **Rule 30**: Checklist before starting
- [ ] **CLASSIFY**: Assembly vs Part?
- [ ] **IDENTIFY**: What standards apply?
- [ ] **DECOMPOSE**: What are the components?
- [ ] **CREATE PLAN**: output/PLAN_{name}.md
- [ ] **WAIT FOR APPROVAL** before building

### Section 8: External Repositories
- [ ] pySolidWorks, pySldWrap, pySW for SolidWorks
- [ ] CodeStack for API examples
- [ ] Check these before writing COM code

---

## Task-Specific Additions

### CAD Tasks
- Create `output/PLAN_{part_name}.md` with:
  - Phase 1: Identify (what is it?)
  - Phase 2: Classify (assembly or part?)
  - Phase 3: Decompose (what components?)
  - Phase 4: Plan (build strategy)
  - Phase 5: API sequence
  - BOM if applicable

### API/Backend Tasks
- Check `docs/API.md` for existing endpoints
- Follow FastAPI patterns in `orchestrator/` or `desktop_server/`
- Test with curl/Postman locally

### Frontend Tasks
- Check `apps/web/components/` for existing components
- Use shadcn/ui components
- Follow Tailwind patterns

### Trading Tasks
- Reference `agents/trading_agent/knowledge/`
- Follow trading plan templates

---

## Acknowledgment Format

When starting ANY task, Claude should state:

```
Checked RULES.md:
- Section 1: [relevant? yes/no]
- Section 2: [relevant? yes/no]
- Section 3: [relevant? yes/no]
- Section 4: [relevant? yes/no]
- Section 5: [relevant? yes/no]
- Section 6: [relevant? yes/no]
- Section 7: [relevant? yes/no] <- REQUIRED for CAD
- Section 8: [relevant? yes/no]

Plan: [creating plan / not needed for simple task]
```

---

## If Claude Skips This

User should say: **"Did you read RULES.md and CHECKLIST.md?"**
