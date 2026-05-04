---
name: Agent Cognitive Architecture Evolution
description: Systematic approach to upgrading an AI agent's internal cognitive architecture - memory systems, self-monitoring, meta-cognition, and self-evolution capabilities
version: "1.0"
confidence: high
last_updated: 2026-04-26
---

# Agent Cognitive Architecture Evolution Skill

## Overview

A systematic methodology for upgrading an AI agent's internal cognitive architecture. Follows a progressive, layered approach from basic memory systems through advanced self-evolution capabilities. Developed and validated during the "Hermes Second Evolution" project.

## When to Use

- When upgrading an agent's memory and knowledge systems
- When adding meta-cognitive capabilities (self-observation, self-improvement)
- When refactoring agent architecture from monolithic to modular
- When the agent needs to "learn how to learn better"
- When current context window usage is inefficient

## Architecture Evolution Roadmap

### Phase 0: Baseline Assessment

**Always start with diagnosis before evolution:**

```bash
# Assess current state
python3 ~/.hermes/scripts/memory_stats.py
python3 ~/.hermes/scripts/health_check.py
hermes gateway status
```

**Diagnosis checklist:**
- [ ] Current memory structure and constraints
- [ ] Existing SOP/skill inventory
- [ ] Active pain points and bottlenecks
- [ ] Context window utilization
- [ ] Tool call efficiency metrics

---

### Phase 1: Four-Layer Memory Architecture

**Core principle: Higher layers = more compact, more frequently accessed, more strictly constrained**

| Layer | Purpose | Size Constraint | Content Type |
|-------|---------|-----------------|-------------|
| **L1 - Insight Index** | Fast lookup, keyword mapping | ≤ 30 lines | Pointers, keywords, trigger conditions |
| **L2 - Global Facts** | Stable ground truth | ≤ 100 lines | User preferences, environment facts, core principles |
| **L3 - SOP Knowledge** | Reusable procedures | 10-30 SOPs | Step-by-step workflows, best practices |
| **L4 - Raw Sessions** | Historical archive | Unlimited | Full conversation history, raw logs |

**Implementation steps:**
1. Create directory structure: `memory/L1_insight_index.txt`, `memory/L2_global_facts.txt`, `memory/L3_sop/`, `memory/L4_raw_sessions/`
2. Migrate existing knowledge into appropriate layers
3. Implement size validation scripts
4. Create L1 index with trigger keywords pointing to L3 SOPs

---

### Phase 2: Self-Evolution Engine

Enable the agent to automatically improve its own procedures based on experience.

**Trigger conditions for SOP auto-generation:**
- Conversation rounds > 15
- Tool calls > 8
- User explicitly says "remember this process"
- Task involves > 3 different tools in combination

**Three-layer SOP generation process:**
1. **Retrospective**: What tools were used? What was tried that failed?
2. **Abstract**: Remove task-specific details, generalize pattern
3. **Formalize**: Write as standard SOP with validation steps

**SOP quality checklist:**
- [ ] Executable by anyone/any agent
- [ ] Contains failure modes and workarounds
- [ ] Has clear success verification criteria
- [ ] Is generalized (not task-specific)

---

### Phase 3: Context Compression Pipeline

Eliminate context bloat by processing large outputs in sandboxed environments.

**Four levels of compression decision:**

| Output Size | Action |
|-------------|--------|
| < 50 lines | Display normally |
| 50-200 lines | Summarize, show key findings only |
| > 200 lines | Process via Python script, output only structured stats |
| Log files/structured data | Always use analysis scripts |

**Standard patterns:**
1. Log analysis → `log_analyzer.py` → error distribution + recent errors
2. Config comparison → `config_diff.py` → changed values summary
3. Code search → Python script → matching files + hit counts

**Anti-patterns to eliminate:**
- ❌ `cat big.log | grep error` → floods context
- ❌ Multiple small terminal calls → combine into one script
- ❌ `read_file` just to understand structure → use script extraction

---

### Phase 4: Atomic Toolkit Refactoring

Optimize tool usage patterns and create helper scripts for common operations.

**Tool classification and optimization strategy:**

| Tool Category | Optimization |
|--------------|-------------|
| Terminal | Batch similar calls, prefer scripts for analysis |
| File ops | Read → modify → verify atomic pattern |
| Knowledge | Find → apply → update loop |
| Diagnostics | One script = full health check |

**Create reusable helper scripts:**
- `log_analyzer.py` - error distribution and trends
- `config_diff.py` - YAML config comparison
- `memory_stats.py` - memory health validation
- `health_check.py` - full system status

---

### Phase 5: Meta-Memory System

Enable the agent to observe and optimize its own execution quality.

**Post-task meta-memory checklist (run after every complex task):**

```
📊 Execution Statistics:
- Total rounds: ____
- Tool calls: ____
- Tool distribution: ____

⚡ Quality Self-Assessment:
- Correctness: ____/10 (Did it work?)
- Optimality: ____/10 (Shortest path?)
- Context efficiency: ____/10 (Wasteful output?)
- User experience: ____/10 (Clear communication?)

💡 Lessons Learned:
- What worked well:
  1. ____
  2. ____
- What to improve:
  1. ____
  2. ____
```

**Typical inefficiency patterns to detect:**
1. Trial-and-error tool calls (same tool >3x with minor changes)
2. Output flooding (large unprocessed dumps)
3. Confirmation loops (repeatedly asking "is this right?")
4. Information re-reading (asking what was already said)

---

### Phase 6: Progressive Generalization

Scale solutions from specific problems to general principles.

**Three layers of generalization:**

```
Specific Problem (e.g., "Fix GLM-5 timeout")
    ↓ Layer 1: Same Category
  Apply to all models, all providers
    ↓ Layer 2: Cross-Domain
  Same pattern applies to rate limiting, retries
    ↓ Layer 3: First Principles
  "Resource protection scales with input size"
```

**Design principles library:**
- P001: Resource protection scales with input size
- P002: External uncertainty requires internal elasticity
- P003: Layered configuration > one-size-fits-all
- P004: Memory = upper layers compact, lower layers complete

---

### Phase 7: Forgetting & Degeneration Detection

Prevent knowledge rot with active memory management.

**Vitality Score formula:**
```
Vitality = (1×recent_use) + (2×citations) + (3×successful_applications)
```

**Vitality-based lifecycle:**
- ≥ 10: Core - prioritize retrieval, validate monthly
- 5-9: Active - normal usage
- 2-4: Low activity - flag for review
- 0-1: Dormant - archive to L4 after 30 days

**Monthly memory health check:**
1. Validate L1/L2 size constraints
2. Scan SOPs for vitality scores
3. Merge duplicate SOPs
4. Archive/dormant low-vitality content
5. Update L1 index keywords

---

## Validation & Quality Gates

After each evolution phase:

1. **Constraint validation**: L1 ≤ 30 lines, L2 ≤ 100 lines
2. **Script testing**: Run all helper scripts and verify output
3. **Gateway health**: `hermes gateway status` shows no errors
4. **Regression check**: Existing functionality still works
5. **Meta-memory review**: Record what was learned about the evolution process itself

---

## Pitfalls & Lessons Learned

1. **Don't over-engineer early**: Start simple, add complexity as needed
2. **Constraint enforcement is critical**: Without size limits, layers bloat quickly
3. **Forgetting is a feature, not a bug**: Active pruning improves signal-to-noise
4. **Meta-memory pays off exponentially**: Small investment in self-observation creates compounding improvements
5. **Test scripts incrementally**: One helper script at a time, validate before next

---

## Success Metrics

Target improvements after full evolution:
- [ ] Context window utilization: +50% more efficient
- [ ] Tool call efficiency: +30% fewer redundant calls
- [ ] SOP reuse rate: +40% more tasks follow established SOPs
- [ ] Same bug recurrence: -50% fewer repeat issues
