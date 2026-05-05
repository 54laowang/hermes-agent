---
name: agchk-agent-self-audit
description: Professional agent architecture health audit using the agchk open-source framework. Includes installation, scanning, false-positive triage, and report generation. Rated on a 7-stage civilization-era scale.
version: "1.0.0"
category: agent-architecture
keywords: [architecture audit, agchk, agent health, self-assessment, civilization era, maturity scoring]
---
# Agent Architecture Self-Audit with agchk

Use the `agchk` open-source tool to perform professional architecture health audits on any AI agent project. This skill covers installation, scanning, result interpretation, false-positive triage, and report generation.

## What is agchk?

agchk is an agent architecture health checker that scans Python/TypeScript/JavaScript agent projects and rates them on a civilization-era scale:

```
石器时代 → 青铜时代 → 铁器时代 → 蒸汽机时代 → 内燃机时代 → 新能源时代 → 人工智能时代
```

It checks 17+ scanner categories covering both safety and architecture maturity.

## Prerequisites

- Python 3.9+ environment
- uv or pip package manager
- Target agent project directory

## Step-by-Step Workflow

### 1. Install agchk

```bash
# Clone and install from source (recommended for latest version)
cd /tmp
git clone https://github.com/huangrichao2020/agchk.git
cd agchk
uv pip install -e .

# OR install from PyPI (may be older)
pip install agchk
```

### 2. Run the Audit

Choose the appropriate profile:
- `personal` - for solo dev, local prototyping (default)
- `enterprise` - for production agents with stricter safety checks

```bash
# Basic audit (with uv environment)
uv run agchk audit --profile personal /path/to/agent/project \
  -o /tmp/audit-results.json \
  -r /tmp/audit-report.md

# Full audit with self-review
uv run agchk audit --profile personal /path/to/agent/project \
  --self-review self_review.json \
  -o /tmp/audit-results.json \
  -r /tmp/audit-report.md

# Enterprise profile with fail-on-high
uv run agchk audit --profile enterprise /path/to/agent/project \
  --fail-on high \
  -o /tmp/audit-results.json
```

### 3. Parse Audit Results with Python

```python
import json

with open('/tmp/audit-results.json', 'r') as f:
    data = json.load(f)

# Executive summary
ms = data['maturity_score']
print(f"Era: {ms['era_name']}")
print(f"Score: {ms['score']}/100")
print(f"Health: {data['executive_verdict']['overall_health']}")

# Strengths list
print("Strengths:")
for s in ms['strengths']:
    print(f"  ✅ {s}")

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

### 4. Triage False Positives (IMPORTANT)

agchk is aggressive with secret detection. MANY findings are false positives:

| Pattern | Common False Positive |
|---------|----------------------|
| `auth.json` files | These are INTENTIONAL credential storage (exclude from git!) |
| `test_*.py` with secrets | TEST DATA used to test redaction features |
| `session_*.json` files | Session dumps that captured config diffs containing keys |
| `config.yaml`/`.env` | Local configuration that shouldn't be committed but isn't "source code" |

**Architecture findings that are actually design choices:**
- "Internal orchestration sprawl" → Multi-agent orchestration systems BY DESIGN have many coordination markers
- "Memory freshness confusion" → Projects that support multiple memory backends will have many memory surfaces
- "Role-play handoff orchestration" → Skill systems with role-based agents are methodology, not sprawl
- "Startup surface sprawl" → Platforms with CLI, web, gateway, API modes naturally have multiple entry points
- "Runtime surface sprawl" → Full-stack agent platforms span multiple runtime surfaces

**For Hermes Agent projects**, see `references/hermes-false-positive-triage.md` for detailed triage guidance based on the April 2026 audit (青铜时代, 30/100, 121 issues).

### 5. Generate Final Report

Structure the report to:
1.  Start with the era rating and score headline
2.  List all detected strengths as validation points
3.  Present the severity summary
4.  Explicitly triage each critical finding (false-positive vs real issue)
5.  Analyze high-severity findings as potential design tradeoffs
6.  Create a prioritized action plan
7.  Add self-assessment conclusion

## Common Scanner Categories

| Scanner | Severity | What It Catches |
|---------|----------|-----------------|
| Hardcoded Secrets | CRITICAL | API keys, tokens in source code |
| Internal Orchestration Sprawl | HIGH | Too many planning/routing/delegation layers |
| Memory Freshness Confusion | HIGH | Too many checkpoint/summary/archive generations |
| Role-Play Handoff Orchestration | HIGH | PM/architect/coder/QA serial handoffs |
| Agent OS Architecture | MEDIUM/HIGH | Missing paging, recovery, scheduler fairness |
| Skill Duplication | MEDIUM | Repeated SOPs without canonical versions |
| Startup Surface Sprawl | HIGH | Too many launchers/wrappers/boot paths |
| Runtime Surface Sprawl | HIGH | Mixing too many runtime surfaces |
| Unrestricted Code Execution | MEDIUM/CRITICAL | exec(), eval(), shell=True |
| Hidden LLM Calls | MEDIUM/HIGH | Secondary model paths bypassing main loop |

## Architecture Era Definitions

| Era | Score Range | Meaning |
|-----|-------------|---------|
| 石器时代 | 0-20 | Raw prompts + tool calling, no methodology |
| 青铜时代 | 21-40 | Has methodology layer, basic memory |
| 铁器时代 | 41-60 | Stateful recovery, basic skill system |
| 蒸汽机时代 | 61-75 | Semantic paging, page-fault recovery |
| 内燃机时代 | 76-85 | Impression pointers, capability tables |
| 新能源时代 | 86-95 | Fair scheduling, semantic VFS, LLM workers |
| 人工智能时代 | 96-100 | Full Agent OS with optimization闭环 |

## Output Artifacts

Save these to the project directory:
- `AGCHK-ARCHITECTURE-AUDIT-YYYYMMDD.md` - Full report with triage
- `/tmp/audit-results.json` - Raw JSON data (temp location)
- `/tmp/audit-report.md` - Machine-generated MD (temp location)
- `.agchk.yaml` - Project-specific configuration (use template below)

### Configuration Template

For Hermes Agent projects, use the pre-configured template:
```bash
cp ~/.hermes/skills/agent-architecture/agchk-agent-self-audit/templates/hermes-agchk.yaml .agchk.yaml
```

This template includes:
- Common false-positive exclusions (test data, build outputs)
- Design choice declarations for multi-agent architectures
- Memory backend multi-surface support
- Startup/runtime surface sprawl allowances
- Project-specific rules for high-complexity files

## Pitfalls and Troubleshooting

1. **Command not found?** Use `uv run agchk` instead of direct `agchk`
2. **Wrong argument order?** `audit` subcommand comes BEFORE the profile
3. **Too many critical findings?** Almost certainly secret false positives - triage carefully
4. **Health says CRITICAL but score is 100?** This is NORMAL! The health metric weights security findings HIGHER than architecture maturity
5. **Scan takes too long?** Exclude `node_modules`, `venv`, `.git` directories from scan target

## When to Use This Skill

- After major architecture refactoring
- Before production deployment
- Monthly health check
- When comparing agent framework architectures
- When evaluating third-party agent projects
- Self-improvement benchmarking
- Performance optimization and bottleneck identification

---

## ⚠️ CRITICAL: Prioritize Based on Usage Scenario

**DO NOT blindly fix all issues.** Audit results must be interpreted in context of the user's actual usage scenario.

### Personal/Local Use (Low Priority for Security Fixes)

**Characteristics**:
- Single user, local environment
- No external input processing
- No sensitive data handling
- No public API exposure
- Personal productivity tool

**Recommendation**:
- P0 (CRITICAL issues): Fix if they represent real vulnerabilities
- P1 (HIGH issues): Optional - evaluate actual risk
- P2 (MEDIUM issues): Low priority - may not be worth the effort
- P3 (Performance/Architecture): Optional - only if it affects daily use

**Key insight**: For personal use, "accurate and simple" > "perfectly secure". Over-engineering security for a local tool is a waste of time.

### Production/Public Use (High Priority for Security Fixes)

**Characteristics**:
- Multi-user environment
- External API endpoints
- Processes untrusted input
- Handles sensitive data
- Public-facing service

**Recommendation**:
- P0/P1: MUST fix before deployment
- P2: Should fix within reasonable timeframe
- P3: Address to maintain code quality

### Decision Framework

Before starting improvements, ask the user:

```
❓ What's your primary use case?
   - Personal productivity (low security priority)
   - Team collaboration (medium priority)
   - Public service (high priority)

❓ Does this issue affect your daily use?
   - Yes → High priority
   - No → Low priority

❓ What's the risk if you DON'T fix it?
   - Real vulnerability → Fix
   - Theoretical risk → Evaluate cost/benefit
```

### Common Mistakes to Avoid

❌ **Mistake**: Fixing all MEDIUM issues because "they're there"
✅ **Correct**: Focus on issues that matter for the user's scenario

❌ **Mistake**: Setting up complex automation (pre-commit hooks, CI/CD) for personal projects
✅ **Correct**: Simplify workflow for personal use - disable strict checks if they slow you down

❌ **Mistake**: Chasing perfect agchk score
✅ **Correct**: Good enough for your use case is good enough

### Example: Hermes Agent Personal Customization (April 2026)

**Scenario**: Personal use, A股分析, 网格交易, 知识管理

**Audit Result**: 青铜时代 (30/100), 121 issues (1 critical, 6 high, 38 medium)

**What we did**:
- ✅ P0 权限策略加固 - Fixed real vulnerability
- ❌ P1 安全代码执行 (25 issues) - Skipped (low risk for personal use)
- ⚠️ P2 自动化机制 - Built but then **simplified** (pre-commit was overkill)

**Lesson learned**: User asked "这些问题都是官方仓库没有发现的吗，还是说必须改进的，我主要关注的是我能够准确简单使用"
- Translation: "Are these real issues? I care about accurate simple use."
- Response: Disabled pre-commit hooks, simplified configuration
- Result: User satisfaction increased, functionality preserved

**Takeaway**: The user's feedback "禁用pre-commit，简化配置" was a clear signal that we over-engineered for their needs.

---

## Performance Optimization Methodology

Beyond architecture health, agchk drives a systematic performance optimization loop: **发现-测量-优化-验证** (Discover-Measure-Optimize-Verify).

### Step 1: Deep Code Scanning

Identify common performance killers:

| Check | Command | Risk Threshold |
|-------|---------|----------------|
| Unprotected `while True` loops | `grep -rn 'while True:' --include=*.py .` | > 10 occurrences |
| `deepcopy` in loops | `grep -rn 'deepcopy' --include=*.py .` | Inside for/while |
| Debug `print` statements | `grep -rn 'print(' --include=*.py .` | > 50 occurrences |
| Unnecessary list/dict copies | `grep -rn '.copy()\\|dict()\\|list()'` | In hot paths |

### Step 2: Establish Performance Baselines

Create benchmark suite for critical operations:

```python
import time
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    name: str
    avg_time: float
    p50: float
    p95: float
    p99: float

# Benchmark key operations: deepcopy vs shallow copy, serialization, etc.
```

### Step 3: Apply Optimizations

**Top-tier (10-100x improvement):**

1. **Eliminate unnecessary deepcopy** (Hermes real case: 2.6x overall speedup)
   ```python
   # ❌ Slow
   messages = copy.deepcopy(messages)
   
   # ✅ Fast
   messages = list(messages)  # Shallow copy only
   ```

2. **Lazy log formatting**
   ```python
   # ❌ Slow (always formats)
   logger.debug(f"Processing: {big_payload}")
   
   # ✅ Fast (formats only when debug enabled)
   logger.debug("Processing: %s", big_payload)
   ```

**First-tier (2-10x improvement):**

3. **Loop protection** - Add max iterations to prevent hangs
4. **Hot attribute caching** - Use `@cached_property` or `@lru_cache`
5. **String concatenation** - Use `''.join(parts)` instead of `+=`

### Step 4: Continuous Audit Mechanism

- **Pre-commit hook** - Check for new prints, while True, etc.
- **Daily CI audit** - Run `agchk --profile enterprise`
- **Performance regression alerts** - Alert if >20% slowdown

### Key Insight

> **Performance optimization 90% gains come from 10% of code changes.**
> 
> Find that 10%, fix it in 10 minutes, get 10-100x improvement.

---

## Improvement Tracking

After running audits, track improvements over time:

```bash
# Record an improvement
python scripts/track_improvements.py record "P0 权限策略加固"

# View current status
python scripts/track_improvements.py status

# View improvement trend
python scripts/track_improvements.py trend

# Generate report
python scripts/track_improvements.py report
```

Data stored in `~/.hermes/improvements.json`.

## Automated Security Checks

Pre-commit hooks automatically check for security issues:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Run specific check
pre-commit run security-check --all-files
```

Checks include:
- `subprocess(shell=True)` - command injection risk
- `exec()/eval()` - code injection risk
- Hardcoded secrets - credential leakage
- Dangerous imports - pickle/marshal

Configuration in `.pre-commit-config.yaml`.

## CI/CD Integration

GitHub Actions workflow (`.github/workflows/security-audit.yml`) runs:
- On push to main/develop
- On pull requests
- Weekly scheduled audit (Monday 6:00)
- Manual trigger

Jobs:
- security-check - Security scan
- architecture-audit - agchk audit
- code-quality - Format/lint check
- dependency-scan - Trivy scan
- notification - Slack alerts on failure

## Resources

- Repository: https://github.com/huangrichao2020/agchk
- Doctrine documentation: `/docs/doctrine/README.md` in the repo
- Agent prompt contract: `/docs/AGENT_PROMPT.md`
- Security Automation Guide: `SECURITY-AUTOMATION-GUIDE.md`

## Reference Files

- **Improvement Tracking**: `references/improvement-tracking.md` - Track security improvements over time
- **Security Check Script**: `references/security-check-script.md` - Pre-commit security validation

### References

- `references/agchk-practical-usage.md` - Practical usage guide with Hermes Agent case study, false positive triage, CI integration patterns
- `references/personal-use-simplification-pattern.md` - **IMPORTANT**: When to simplify security for personal use (April 2026 case study)
