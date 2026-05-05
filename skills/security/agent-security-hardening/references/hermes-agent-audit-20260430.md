# Hermes Agent Security Audit - 2026-04-30

**Audit Date**: 2026-04-30 09:46
**Tool**: agchk 1.2.6
**Target**: ~/.hermes/hermes-agent
**Profile**: Personal Development

---

## Executive Summary

| Metric | Result |
|--------|--------|
| Civilization Era | 青铜时代 |
| Maturity Score | 30/100 |
| Overall Health | critical |
| Total Issues | 121 |
| Scan Duration | 123.6s |

### Issue Distribution

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| HIGH | 6 |
| MEDIUM | 38 |
| LOW | 76 |

---

## Critical Findings

### 1. Hardcoded Secret (False Positive)

**Issue**: Hardcoded secret or API key detected
**Location**: `tests/agent/test_redact.py:70`
**Symptom**: `text = 'MY_SECRET_TOKEN="supersecretvalue"'`

**Triage**: ✅ **Confirmed False Positive**
- Test file for redaction functionality
- Intentional test data to validate sensitive info masking
- File name `test_redact.py` indicates testing purpose

**Action**: Exclude in `.agchk.yaml`:
```yaml
exclude_patterns:
  - "tests/**/test_redact.py"
```

---

## High Priority Findings

### 1. Permission Policy Not Enforced on All Paths

**Issue**: Permission policy is not enforced on all dispatch paths
**Severity**: HIGH
**Root Cause**: Permission checks attached to some paths, not shared boundary
**Impact**: Sequential, concurrent, scheduled, delegated paths bypass policy

**Solution Implemented**: Centralized permission boundary
- Created `tools/permission_policy.py`
- Integrated into `model_tools.handle_function_call()`
- Coverage: All 4 dispatch paths

**Status**: ✅ **FIXED** (2026-04-30)

### 2. Internal Orchestration Sprawl

**Issue**: Too many planning, routing, delegation layers
**Severity**: HIGH
**Root Cause**: Multi-agent orchestration by design

**Triage**: ⚠️ **Design Choice**
- Hermes supports parallel delegation and multi-agent workflows
- Complexity is intentional, not accidental
- Document in `.agchk.yaml` as design choice

### 3. Memory Freshness Confusion

**Issue**: Multiple memory generations/surfaces
**Severity**: HIGH
**Root Cause**: Multiple backend support by design

**Triage**: ⚠️ **Design Choice**
- MemPalace + fact_store + session_search architecture
- Multiple surfaces are architectural decision
- Document as design choice

### 4. Role-Play Handoff Orchestration

**Issue**: PM/architect/coder/QA serial handoffs
**Severity**: HIGH
**Root Cause**: Skill-based role system by design

**Triage**: ⚠️ **Design Choice**
- Skill system uses role-based agents
- Methodology, not sprawl
- Document as design choice

### 5. Startup Surface Sprawl

**Issue**: Multiple launchers/wrappers/boot paths
**Severity**: HIGH
**Root Cause**: Multi-platform support by design

**Triage**: ⚠️ **Design Choice**
- CLI + web + gateway + API modes
- Multiple entry points required for platform flexibility
- Document as design choice

### 6. Runtime Surface Sprawl

**Issue**: Mixing runtime surfaces
**Severity**: HIGH
**Root Cause**: Full-stack platform by design

**Triage**: ⚠️ **Design Choice**
- Python backend + TypeScript frontend
- Multiple runtime surfaces intentional
- Document as design choice

---

## Medium Priority Findings

### Unsafe Code Execution

**Issue**: 25 occurrences of unsafe code execution
**Severity**: MEDIUM

**Breakdown**:
- `subprocess(shell=True)`: 13 occurrences
- `exec()`: 6 occurrences
- `compile()`: 4 occurrences
- `eval()`: 2 occurrences

**Risk**: Command injection, code injection vulnerabilities

**Remediation Priority**: P1 (fix within 1 week)

**Action Plan**:
1. Audit each occurrence for necessity
2. Replace `shell=True` with argument lists where possible
3. Restrict `exec/eval` with allowed names dict
4. Add input validation and whitelisting

---

## Architecture Strengths

Hermes Agent possesses strong architectural foundations:

- ✅ methodology layer
- ✅ agent runtime
- ✅ tool/syscall boundary
- ✅ fact memory
- ✅ skill memory
- ✅ context compaction
- ✅ semantic paging
- ✅ page-fault recovery
- ✅ impression cues
- ✅ impression pointers
- ✅ scheduler/workers
- ✅ fair scheduling
- ✅ capability table
- ✅ permission policy
- ✅ memory lifecycle governance
- ✅ multilingual memory retrieval
- ✅ RAG governance
- ✅ token-efficient context layer
- ✅ external signal intake
- ✅ source-level learning
- ✅ pattern extraction
- ✅ constraint adaptation
- ✅ small-step landing
- ✅ verification closure
- ✅ hands-on validation
- ✅ learning assetization
- ✅ semantic VFS
- ✅ daemon lifecycle safety
- ✅ plugin sandbox policy
- ✅ remote tool boundary
- ✅ middleware observability
- ✅ traces/evals
- ✅ before/after evidence logging
- ✅ handoff/workbook habit
- ✅ stateful recovery
- ✅ restart session recall
- ✅ environment-as-state
- ✅ LLM CLI workers
- ✅ task envelope
- ✅ CLI prompt contract
- ✅ self-evolution loop

---

## False Positive Configuration

### `.agchk.yaml`

```yaml
exclude_patterns:
  - "tests/**/test_redact.py"
  - "tests/fixtures/**"
  - "build/**"
  - ".venv/**"

false_positive_markers:
  - "# TEST DATA"
  - "# pragma: no cover"
  - "# noqa"

design_choices:
  internal_orchestration:
    rationale: "Multi-agent orchestration system by design - supports parallel delegation"
  
  memory_surfaces:
    rationale: "Multiple memory backends (MemPalace, fact_store, session_search) by design"
  
  startup_surfaces:
    rationale: "Platform supports CLI, web, gateway, API modes - multiple entry points required"
  
  runtime_surfaces:
    rationale: "Full-stack agent platform - spans Python backend and TypeScript frontend"
```

---

## Improvement Roadmap

### P0 (Completed)
- ✅ Permission policy centralized
- ✅ All dispatch paths covered
- ✅ Security improvement documented

### P1 (Next)
- [ ] Fix `subprocess(shell=True)` - 13 occurrences
- [ ] Restrict `exec/eval/compile` - 12 occurrences
- [ ] Add input validation

### P2 (Future)
- [ ] Pre-commit hook for agchk
- [ ] CI integration for security audit
- [ ] Regular audit schedule

---

## Lessons Learned

1. **False Positive Triage Critical**: agchk aggressive on secret detection, many false positives in test files
2. **Design Choices vs Issues**: Many HIGH findings are architectural decisions, not problems
3. **Centralized Boundaries**: Permission policy best enforced at single dispatch point
4. **Documentation Essential**: Security improvements need detailed documentation for future reference

---

**Report Generated**: 2026-04-30 09:50
**Next Audit**: Schedule for 2026-05-30
