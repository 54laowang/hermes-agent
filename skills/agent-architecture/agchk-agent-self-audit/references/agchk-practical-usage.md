# agchk Practical Usage Guide - Hermes Agent Case Study

**Date**: 2026-04-30
**Context**: Hermes Agent architecture audit and security hardening

---

## Installation

```bash
# From PyPI
pip install agchk

# Verify
agchk --version
# Output: agchk 1.2.6
```

---

## Execution

### Basic Audit

```bash
cd ~/.hermes/hermes-agent
source .venv/bin/activate

agchk audit --profile personal . \
  -o /tmp/hermes-audit-results.json \
  -r /tmp/hermes-audit-report.md
```

**Output**:
```
🔍 Agent Architecture Audit
   Target: .
   Started: 2026-04-30 09:46:07
   Profile: Personal Development

  Scanning: Internal Orchestration Sprawl...
  Scanning: Completion Closure Gap...
  [... 27 scanners ...]
  
──────────────────────────────────────────────────
✅ Audit complete. Found 121 issues in 123.6s:
   CRITICAL: 1
   HIGH: 6
   MEDIUM: 38
   LOW: 76
   Overall: critical
   Era: 青铜时代 (30/100)
```

### Enterprise Profile

```bash
agchk audit --profile enterprise . \
  --fail-on high \
  -o /tmp/audit-results.json
```

---

## Result Parsing

### Python Parsing

```python
import json

with open('/tmp/hermes-audit-results.json', 'r') as f:
    data = json.load(f)

# Executive summary
ms = data['maturity_score']
print(f"Era: {ms['era_name']}")           # 青铜时代
print(f"Score: {ms['score']}/100")        # 30/100
print(f"Health: {data['executive_verdict']['overall_health']}")  # critical

# Severity breakdown
for sev, count in data['severity_summary'].items():
    print(f"{sev}: {count}")

# Findings by severity
critical = [f for f in data['findings'] if f['severity'] == 'critical']
high = [f for f in data['findings'] if f['severity'] == 'high']

# Ordered fix plan
for step in data['ordered_fix_plan']:
    print(f"{step['order']}. {step['goal']}")
```

---

## False Positive Triage

### Common False Positives

| Pattern | Reason | Action |
|---------|--------|--------|
| `test_redact.py` with secrets | Test data for redaction | Exclude in `.agchk.yaml` |
| `auth.json` files | Intentional credential storage | Add to gitignore |
| `session_*.json` with keys | Session dumps | Exclude pattern |
| `config.yaml` with API keys | Local configuration | Document as expected |

### Example: Test Data False Positive

**Finding**:
```json
{
  "severity": "critical",
  "title": "Hardcoded secret or API key detected",
  "symptom": "Secret pattern found at test_redact.py:70: text = 'MY_SECRET_TOKEN=\"supe...\"'",
  "evidence_refs": ["tests/agent/test_redact.py:70"]
}
```

**Triage**:
- File: `tests/agent/test_redact.py`
- Purpose: Testing sensitive info redaction
- Content: Test data with intentional secrets
- Verdict: **False positive** - exclude from audit

---

## Configuration

### `.agchk.yaml` Template

```yaml
# agchk configuration
# Documentation: https://github.com/huangrichao2020/agchk

# Exclude patterns
exclude_patterns:
  # Test files
  - "tests/**/test_redact.py"
  - "tests/fixtures/**"
  
  # Build outputs
  - "build/**"
  - "dist/**"
  - "*.egg-info/**"
  
  # Dependencies
  - "node_modules/**"
  - ".venv/**"
  - "venv/**"

# False positive markers
false_positive_markers:
  - "# TEST DATA"
  - "# pragma: no cover"
  - "# noqa"

# Design choices (non-issues)
design_choices:
  internal_orchestration:
    rationale: "Multi-agent orchestration system by design"
    
  memory_surfaces:
    rationale: "Multiple memory backends by design"
    
  startup_surfaces:
    rationale: "Multi-platform support requires multiple entry points"
    
  runtime_surfaces:
    rationale: "Full-stack platform spans multiple runtimes"
```

---

## Scanner Categories

agchk runs 27+ scanners across security and architecture:

| Scanner | Severity | What It Catches |
|---------|----------|-----------------|
| Hardcoded Secrets | CRITICAL | API keys, tokens in source code |
| Internal Orchestration Sprawl | HIGH | Too many coordination layers |
| Memory Freshness Confusion | HIGH | Too many memory surfaces |
| Role-Play Handoff Orchestration | HIGH | Serial role handoffs |
| Permission Policy | HIGH | Incomplete permission enforcement |
| Startup Surface Sprawl | HIGH | Too many launch paths |
| Runtime Surface Sprawl | HIGH | Mixed runtime surfaces |
| Unrestricted Code Execution | MEDIUM | exec(), eval(), shell=True |
| Hidden LLM Calls | MEDIUM | Secondary model paths |
| Skill Duplication | MEDIUM | Repeated SOPs |
| Memory Growth | MEDIUM | Unbounded memory |

---

## Civilization Era Scale

| Era | Score | Characteristics |
|-----|-------|----------------|
| 石器时代 | 0-20 | Raw prompts + tool calling |
| 青铜时代 | 21-40 | Methodology layer, basic memory |
| 铁器时代 | 41-60 | Stateful recovery, skill system |
| 蒸汽机时代 | 61-75 | Semantic paging, page-fault recovery |
| 内燃机时代 | 76-85 | Impression pointers, capability tables |
| 新能源时代 | 86-95 | Fair scheduling, semantic VFS |
| 人工智能时代 | 96-100 | Full Agent OS with optimization |

**Hermes Agent**: 青铜时代 (30/100)

---

## Practical Tips

### 1. Run in Virtual Environment

```bash
source .venv/bin/activate
agchk audit --profile personal .
```

Avoids dependency conflicts.

### 2. Use GIT_EDITOR=true for Rebase

If audit triggers git operations:
```bash
GIT_EDITOR=true git pull --rebase origin main
```

### 3. Parse JSON for Automation

Don't parse markdown report - use JSON for:
- CI integration
- Automated triage
- Trend tracking

### 4. Document Design Choices

Many HIGH findings are architectural decisions:
- Document in `.agchk.yaml`
- Add rationale for future audits
- Distinguish from actual issues

### 5. Prioritize by Severity

- CRITICAL: Fix immediately (or triage as false positive)
- HIGH: Fix within 24 hours (or document as design choice)
- MEDIUM: Fix within 1 week
- LOW: Backlog

---

## Integration Patterns

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
agchk audit --profile enterprise . --fail-on high || exit 1
```

### CI/CD Pipeline

```yaml
# .github/workflows/security-audit.yml
name: Security Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install agchk
        run: pip install agchk
      - name: Run audit
        run: agchk audit --profile enterprise .
```

### Scheduled Audit

```bash
# crontab -e
0 2 * * 0 cd ~/.hermes/hermes-agent && agchk audit --profile personal . -o /tmp/audit-$(date +\%Y\%m\%d).json
```

---

## Output Files

| File | Purpose |
|------|---------|
| `audit-results.json` | Machine-readable, for automation |
| `audit-report.md` | Human-readable, for review |
| `.agchk.yaml` | Configuration, exclude patterns |
| `SECURITY-IMPROVEMENT-*.md` | Improvement documentation |

---

## Lessons from Hermes Audit

1. **False positives common**: agchk aggressive on secrets, triage carefully
2. **Design vs bugs**: Many HIGH findings are architectural choices
3. **Parse JSON**: Markdown report for humans, JSON for automation
4. **Document exclusions**: Future audits need context for exclusions
5. **Track progress**: Save audit results for trend analysis

---

**Reference**: Hermes Agent audit 2026-04-30
**Next**: Schedule monthly audits for trend tracking
