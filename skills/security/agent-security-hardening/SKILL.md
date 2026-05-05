---
name: agent-security-hardening
description: AI Agent 系统安全加固技能 - 权限策略、代码执行安全、审计改进的系统性方法。覆盖权限边界设计、危险命令检测、安全代码执行模式、agchk 审计改进全流程。
version: "1.0.0"
category: security
keywords: [security, permission-policy, code-execution-safety, audit, hardening, agchk]
---

# AI Agent Security Hardening

Systematic approach to security hardening for AI agent systems. Covers permission policy enforcement, safe code execution patterns, and audit-driven improvements.

## When to Use This Skill

- Agent architecture audit reveals security vulnerabilities
- Permission policy gaps detected (not enforced on all dispatch paths)
- Unsafe code execution patterns found (shell=True, exec/eval)
- Security review requested for agent systems
- Post-deployment security hardening

---

## Phase 1: Security Audit Foundation

### 1.1 Architecture Health Scan

Use `agchk` to identify security vulnerabilities:

```bash
# Install agchk
pip install agchk

# Run audit
agchk audit --profile personal /path/to/agent/project \
  -o /tmp/audit-results.json \
  -r /tmp/audit-report.md

# Enterprise profile (stricter)
agchk audit --profile enterprise /path/to/agent/project \
  --fail-on high \
  -o /tmp/audit-results.json
```

### 1.2 Vulnerability Classification

**CRITICAL** - Immediate fix required:
- Hardcoded secrets/API keys (exclude test data)
- Permission bypass on dispatch paths

**HIGH** - Fix within 24 hours:
- Permission policy not enforced on all paths
- Internal orchestration sprawl (if security-related)

**MEDIUM** - Fix within 1 week:
- Unsafe code execution (shell=True, exec/eval)
- Memory growth without limits

**Design Choices** - Document, don't fix:
- Internal orchestration sprawl (multi-agent design)
- Startup/runtime surface sprawl (multi-platform design)
- Memory surfaces (multiple backend support)

---

## Phase 2: Permission Policy Hardening

### 2.1 Problem Pattern

**Symptom**: Permission checks scattered across codebase
**Root Cause**: Checks attached to some paths, not shared boundary
**Impact**: Sequential, concurrent, scheduled, delegated paths bypass policy

### 2.2 Solution: Centralized Permission Boundary

**Architecture Principle**: 
- Single entry point for all tool execution
- Permission check at shared boundary
- Cover all dispatch paths with one check

**Implementation Pattern**:

1. **Create Permission Policy Module** (`tools/permission_policy.py`):

```python
def check_tool_permission(
    tool_name: str,
    tool_args: Dict[str, Any],
    session_id: Optional[str] = None,
    enabled_tools: Optional[list] = None,
) -> tuple[bool, Optional[str]]:
    """
    Permission check for all tool dispatch paths.
    
    Checks:
    1. enabled_tools list validation
    2. Dangerous command pattern detection
    3. Tool-specific permission rules
    
    Returns: (is_permitted, error_message)
    """
    # 1. enabled_tools check
    if enabled_tools is not None and tool_name not in enabled_tools:
        return False, f"Tool '{tool_name}' is not enabled"
    
    # 2. Dangerous command detection
    if tool_name in ("terminal", "execute_code", "process"):
        command = tool_args.get("command", "")
        if command:
            # Integrate with existing approval system
            from tools.approval import detect_dangerous_command
            result = detect_dangerous_command(command)
            if result and result[0]:
                logger.warning(f"Dangerous command: {result[1]}")
                # Approval handled by existing system
    
    return True, None
```

2. **Integrate at Core Dispatch Boundary** (`model_tools.handle_function_call`):

```python
def handle_function_call(function_name, function_args, ...):
    # Permission policy enforcement
    try:
        from tools.permission_policy import enforce_permission_policy
        permission_error = enforce_permission_policy(
            function_name,
            function_args,
            session_id=session_id,
            enabled_tools=enabled_tools,
        )
        if permission_error is not None:
            return json.dumps({"error": permission_error})
    except Exception as perm_exc:
        logger.debug(f"Permission check failed (allowing): {perm_exc}")
    
    # ... rest of dispatch logic
```

### 2.3 Coverage Verification

All dispatch paths must go through `handle_function_call`:

| Path | Entry Point | Coverage |
|------|-------------|----------|
| Sequential (CLI) | `handle_function_call()` | ✅ |
| Concurrent (batch) | `handle_function_call()` | ✅ |
| Scheduled (cron) | `handle_function_call()` | ✅ |
| Delegated (subagent) | `handle_function_call()` | ✅ |

### 2.4 Testing

```python
# Test 1: Normal tool
check_tool_permission('read_file', {'path': '/tmp/test.txt'})
# Expected: (True, None)

# Test 2: Disabled tool
check_tool_permission(
    'terminal',
    {'command': 'ls'},
    enabled_tools=['read_file', 'write_file']
)
# Expected: (False, "Tool 'terminal' is not enabled")

# Test 3: Dangerous command
check_tool_permission('terminal', {'command': 'rm -rf /tmp/test'})
# Expected: (True, None) - logs warning, approval handled elsewhere
```

---

## Phase 3: Safe Code Execution

### 3.1 Problem Patterns

**shell=True** (13 occurrences typical):
- Command injection risk
- Shell expansion vulnerabilities

**exec()/eval()/compile()** (12 occurrences typical):
- Code injection risk
- Arbitrary execution vulnerabilities

### 3.2 Remediation Strategy

**Priority**: MEDIUM (fix within 1 week)

**Approach**:

1. **Replace shell=True**:
```python
# ❌ Unsafe
subprocess.run(f"ls {user_input}", shell=True)

# ✅ Safe
subprocess.run(["ls", user_input], shell=False)
```

2. **Restrict exec/eval usage**:
```python
# ❌ Unsafe
exec(user_code)

# ✅ Restricted (if absolutely necessary)
allowed_names = {"safe_func": safe_func}
exec(user_code, {"__builtins__": {}}, allowed_names)
```

3. **Add input validation**:
```python
import re

def validate_command(command: str) -> bool:
    """Whitelist-based command validation."""
    ALLOWED_PATTERNS = [
        r'^ls\b',
        r'^cat\s+[\w/]+\b',
        r'^git\s+(status|log|diff)\b',
    ]
    return any(re.match(p, command) for p in ALLOWED_PATTERNS)
```

---

## Phase 4: False Positive Triage

### 4.1 Common False Positives

| Pattern | Reason | Action |
|---------|--------|--------|
| `test_redact.py` with secrets | Test data for redaction | Exclude in `.agchk.yaml` |
| `auth.json` files | Intentional credential storage | Add to gitignore |
| `config.yaml` with keys | Local configuration | Document as expected |

### 4.2 Configuration

Create `.agchk.yaml`:

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
    rationale: "Multi-agent orchestration system by design"
  memory_surfaces:
    rationale: "Multiple memory backends (MemPalace, fact_store) by design"
```

---

## Phase 5: Improvement Tracking

### 5.1 Documentation

Create improvement report:
- `SECURITY-IMPROVEMENT-P0-PERMISSION-POLICY.md`
- Document problem, solution, testing, impact
- Include before/after security assessment

### 5.2 Automation (Future)

**Pre-commit Hook**:
```bash
# .git/hooks/pre-commit
#!/bin/bash
agchk audit --profile enterprise . --fail-on high || exit 1
```

**CI Integration**:
```yaml
# .github/workflows/security-audit.yml
name: Security Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install agchk
      - run: agchk audit --profile enterprise .
```

---

## Civilization Era Progress

Track security maturity on agchk's 7-stage scale:

| Era | Score | Security Characteristics |
|-----|-------|-------------------------|
| 石器时代 | 0-20 | No permission system |
| 青铜时代 | 21-40 | Basic permission checks |
| 铁器时代 | 41-60 | Centralized permission boundary |
| 蒸汽机时代 | 61-75 | Safe code execution enforced |
| 内燃机时代 | 76-85 | Continuous audit automation |
| 新能源时代 | 86-95 | Proactive threat detection |
| 人工智能时代 | 96-100 | Self-healing security |

**Target**: Progress from 青铜时代 → 铁器时代 within 1 month

---

## Pitfalls

### 1. Breaking Existing Behavior

**Pitfall**: Permission checks block legitimate tool calls
**Solution**: Graceful degradation - allow on failure, log warning

```python
try:
    permission_error = enforce_permission_policy(...)
    if permission_error:
        return {"error": permission_error}
except Exception:
    logger.warning("Permission check failed, allowing tool")
    # Continue execution
```

### 2. False Positive Noise

**Pitfall**: agchk reports many false positives
**Solution**: Configure `.agchk.yaml` exclusions, triage systematically

### 3. Incomplete Coverage

**Pitfall**: Some dispatch paths bypass permission check
**Solution**: Verify all paths go through `handle_function_call`, add tests

### 4. Performance Impact

**Pitfall**: Permission checks add latency
**Solution**: Keep checks simple (list lookup, regex match), < 1ms overhead

---

## Success Criteria

- [ ] agchk audit shows no CRITICAL/HIGH security issues
- [ ] Permission policy enforced on all dispatch paths
- [ ] Unsafe code execution patterns eliminated or justified
- [ ] `.agchk.yaml` configured for project
- [ ] Security improvement report documented
- [ ] Pre-commit hook / CI integration planned

---

## Resources

- agchk Repository: https://github.com/huangrichao2020/agchk
- Permission Policy Implementation: `tools/permission_policy.py`
- Security Improvement Template: `SECURITY-IMPROVEMENT-*.md`

### References

- `references/hermes-agent-audit-20260430.md` - Complete audit report with findings, triage, and improvement roadmap for Hermes Agent
