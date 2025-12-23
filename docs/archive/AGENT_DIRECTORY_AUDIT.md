# Agent Directory Naming Audit - Phase 19.1.2
**Date:** Dec 22, 2025 @ 12:45 PM  
**Status:** 🔴 CRITICAL - Multiple duplicate directories found

---

## 🔍 FINDINGS

### 1. Inspector Agent - DUPLICATE DIRECTORIES

**Directory 1:** `agents/inspector_bot/` (Python convention - underscore)
```
Contents:
- __init__.py
- adapters/
Used in code: Yes (tests/test_e2e_trading.py imports from this)
```

**Directory 2:** `agents/inspector-bot/` (kebab-case)
```
Contents:
- run_judge.bat
- run_review.bat
- SCHEDULE_REVIEW.bat
- src/
- templates/
Used in code: No imports found
```

**Recommendation:** ✅ **KEEP** `inspector_bot`, **MERGE** content from `inspector-bot`

---

### 2. System Manager - DUPLICATE DIRECTORIES

**Directory 1:** `agents/system_manager/` (Python convention - underscore)
```
Contents:
- __init__.py
- adapter.py (3.3KB)
Used in code: Likely (Python import style)
```

**Directory 2:** `agents/system-manager/` (kebab-case)
```
Contents:
- requirements.txt
- src/
Used in code: Unknown
```

**Recommendation:** ✅ **KEEP** `system_manager`, **MERGE** content from `system-manager`

---

### 3. Trading Agent - DUPLICATE DIRECTORIES

**Directory 1:** `agents/trading_agent/` (Python convention - underscore)
```
Contents:
- __init__.py
- adapters/
- knowledge/
- src/
- templates/
Size: LARGER, more complete
```

**Directory 2:** `agents/trading-bot/` (kebab-case)
```
Contents:
- knowledge/
- src/
- templates/
Size: SMALLER, subset of trading_agent
```

**Recommendation:** ✅ **KEEP** `trading_agent`, **DELETE** `trading-bot` (redundant)

---

### 4. CAD Agent - EXPERIMENTAL TYPESCRIPT VERSION

**Directory 1:** `agents/cad_agent/` (Python - MAIN)
```
Contents:
- __init__.py
- __pycache__/
- adapters/
- cad_orchestrator.py (12KB)
- knowledge/
- src/
- validators/
Status: ACTIVE, fully implemented
```

**Directory 2:** `agents/cad-agent-ai/` (TypeScript - EXPERIMENTAL)
```
Contents:
- src/ (appears empty or minimal)
Status: OBSOLETE/EXPERIMENTAL
Language: TypeScript (conflicts with Python-first architecture)
```

**Recommendation:** 🔴 **DELETE** `cad-agent-ai` (obsolete TypeScript experiment)

---

## 📊 SUMMARY

| Agent | Keep | Merge From | Delete | Action |
|-------|------|------------|--------|--------|
| Inspector | inspector_bot/ | inspector-bot/ | - | Merge .bat files |
| System Manager | system_manager/ | system-manager/ | - | Merge src/ & requirements |
| Trading | trading_agent/ | - | trading-bot/ | Delete duplicate |
| CAD | cad_agent/ | - | cad-agent-ai/ | Delete obsolete TS |

**Total Cleanup:** Remove 2 directories, merge 2 pairs

---

## 🎯 RECOMMENDED ACTIONS

### Priority 1: DELETE Obsolete Directories
```bash
# Safe to delete (after backing up any unique content):
rm -rf agents/trading-bot/
rm -rf agents/cad-agent-ai/
```

### Priority 2: MERGE Inspector Directories
```bash
# Move unique files from inspector-bot to inspector_bot:
mv agents/inspector-bot/*.bat agents/inspector_bot/
mv agents/inspector-bot/templates/* agents/inspector_bot/templates/
mv agents/inspector-bot/src/* agents/inspector_bot/src/
rm -rf agents/inspector-bot/
```

### Priority 3: MERGE System Manager Directories
```bash
# Move unique files from system-manager to system_manager:
mv agents/system-manager/requirements.txt agents/system_manager/
mv agents/system-manager/src/* agents/system_manager/src/
rm -rf agents/system-manager/
```

---

## 🚨 IMPACT ANALYSIS

### Code Imports
- ✅ Current imports use underscore style (`inspector_bot`)
- ✅ No code changes needed if we keep underscore versions
- ❌ Dash versions not referenced in imports

### Architecture Consistency
- ✅ Python PEP 8 recommends underscore for package names
- ✅ Keeping underscore aligns with RULES.md standards
- ✅ Eliminates confusion for developers

### Risk Level
- 🟢 **LOW RISK** - Dash versions appear to be legacy/experimental
- 🟢 No active imports to dash-named directories
- 🟢 Can safely consolidate to underscore naming

---

## ✅ SUCCESS CRITERIA

**Cleanup is complete when:**
- [ ] Only underscore directories remain (inspector_bot, system_manager, trading_agent, cad_agent)
- [ ] All unique content from dash directories merged
- [ ] No broken imports in codebase
- [ ] Git commit with consolidation changes
- [ ] Update RULES.md with naming convention enforcement

**Estimated Time:** 30 minutes  
**Risk:** Low (after backup verification)

---

**Next Steps:** Proceed with merge if you approve this audit.
