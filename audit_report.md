# Agent Architecture Audit Report

**Target**: `.`
**Profile**: `personal_development`
**Date**: 2026-04-25T10:47:51.058526
**Duration**: 60.31s
**Overall Health**: **critical**
**Architecture Era**: **人工智能时代** (100/100)
**Primary Failure Mode**: Hardcoded secret or API key detected
**Most Urgent Fix**: Move credential to environment variable or secrets manager (e.g., AWS Secrets Manager, Doppler). Add pre-commit hook to block secret commits.

## Scope

- Entry points: hermes_cli/main.py, acp_adapter/server.py, tui_gateway/server.py, ui-tui/packages/hermes-ink/index.js, cli.py
- Channels: cli, http_api, web, slack, discord, telegram
- Model stack: openai, anthropic, gemini, ollama, bedrock, llama
- Audited layers: tool_selection, fallback_loops, completion_closure, active_recall, session_history, long_term_memory, impression_memory, os_memory, os_scheduler, os_syscall, os_vfs, stateful_recovery, llm_cli_workers, persistence, platform_rendering, tool_execution, answer_shaping

## Summary

> 这个 Agent 项目处于 人工智能时代（100/100）：具备可进化的 agent OS：印象指针、缺页换入、能力表、调度公平性和优化闭环。

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | 1 |
| 🟠 HIGH | 6 |
| 🟡 MEDIUM | 46 |
| 🟢 LOW | 70 |

**Total findings**: 123

## Architecture Era Score

- Era: **人工智能时代**
- Score: **100/100**
- Raw points: `145`
- Finding penalty: `45`
- Methodology gate: 已发现方法论层，项目具备进入青铜以上时代的地基。
- Meaning: 具备可进化的 agent OS：印象指针、缺页换入、能力表、调度公平性和优化闭环。

**Strengths**:
- methodology layer
- agent runtime
- tool/syscall boundary
- fact memory
- skill memory
- context compaction
- semantic paging
- page-fault recovery
- impression cues
- scheduler/workers
- fair scheduling
- capability table
- semantic VFS
- traces/evals
- stateful recovery
- environment-as-state
- LLM CLI workers
- task envelope
- CLI prompt contract

**Next Milestones**:
- 把 impression cue 升级成 topic_anchor + semantic_hash + pointer_ref。

## Evidence Pack

- `code` tests/agent/test_redact.py:70 — Secret pattern found at test_redact.py:70: text = 'MY_SECRET_TOKEN="supersecretvalue123456789"'
- `code` .plans/openai-api-server.md:219 — Found 16322 orchestration markers across 5 coordination categories (delegation, planning, recovery, routing, scheduling).
- `code` AGENTS.md:82 — Found file-creation and index-update signals, but the reusable memory closure is incomplete. Missing: impression card, anchor mapping, pointer registration.
- `code` acp_adapter/session.py — Found 121 memory-like surfaces spanning 9 categories; overlapping memory stems: init, memory, plugin, readme, session.
- `code` RELEASE_v0.9.0.md:30 — Found 125 role markers across 4 role categories (builder, manager, researcher, reviewer) and 1731 serial handoff markers.
- `code` docker/entrypoint.sh — Found 42 startup-like files and 171 launcher/wrapper sites.
- `code` RELEASE_v0.11.0.md:38 — Found runtime markers across 6 operating surfaces (agent_stack, ops, queue_jobs, storage, ui, web_api).
- `code` RELEASE_v0.11.0.md:18 — Found 210 external LLM CLI worker markers, but only 0 task-envelope markers, 15 CLI prompt-contract markers, 2064 result-capture markers, and 3404 process-control markers.
- `code` hermes_cli/skills_hub.py — Found 256 overlapping skill-like files across 27 duplicate groups.
- `code` agent/auxiliary_client.py:3038 — LLM API call found at auxiliary_client.py:3038: retry_client.chat.completions.create(**retry_kwargs), task)
- `code` agent/auxiliary_client.py:3258 — LLM API call found at auxiliary_client.py:3258: await refreshed_client.chat.completions.create(**kwargs), task)
- `code` agent/auxiliary_client.py:3300 — LLM API call found at auxiliary_client.py:3300: await retry_client.chat.completions.create(**retry_kwargs), task)
- `code` agent/transports/anthropic.py:48 — LLM API call found at anthropic.py:48: """Build Anthropic messages.create() kwargs.
- `code` agent/transports/chat_completions.py:81 — LLM API call found at chat_completions.py:81: """Build chat.completions.create() kwargs.
- `code` skills/red-teaming/godmode/scripts/auto_jailbreak.py:355 — LLM API call found at auto_jailbreak.py:355: response = client.chat.completions.create(
- `code` skills/red-teaming/godmode/scripts/godmode_race.py:286 — LLM API call found at godmode_race.py:286: response = client.chat.completions.create(
- `code` tools/mixture_of_agents_tool.py:146 — LLM API call found at mixture_of_agents_tool.py:146: response = await _get_openrouter_client().chat.completions.create(**api_params)
- `code` tools/mixture_of_agents_tool.py:221 — LLM API call found at mixture_of_agents_tool.py:221: response = await _get_openrouter_client().chat.completions.create(**api_params)
- `code` tools/mixture_of_agents_tool.py:228 — LLM API call found at mixture_of_agents_tool.py:228: response = await _get_openrouter_client().chat.completions.create(**api_params)
- `code` environments/benchmarks/terminalbench_2/terminalbench2_env.py:284 — Found eval( at terminalbench2_env.py:284: #   - STOP_TRAIN: pauses training during eval (standard for eval envs)

### 1. 🔴 [CRITICAL] Hardcoded secret or API key detected

**Symptom**: Secret pattern found at test_redact.py:70: text = 'MY_SECRET_TOKEN="supersecretvalue123456789"'
**User Impact**: Exposed credentials can be stolen from version control or file dumps, leading to unauthorized access and billing abuse.
**Source Layer**: secrets_management
**Mechanism**: Regex match for pattern: (?i)(?:api[_-]?key|apikey|secret[_-]?key|token)\s*[=:]\s*['\"]([a-zA-Z0-9+/]{20,}={0,2})['\"]
**Root Cause**: Credentials hardcoded in source instead of using environment variables or a secrets manager.
**Recommended Fix**: Move credential to environment variable or secrets manager (e.g., AWS Secrets Manager, Doppler). Add pre-commit hook to block secret commits.
**Evidence**:
- `tests/agent/test_redact.py:70`
**Confidence**: 90%

### 2. 🟠 [HIGH] Internal orchestration sprawl detected

**Symptom**: Found 16322 orchestration markers across 5 coordination categories (delegation, planning, recovery, routing, scheduling).
**User Impact**: Too many planning, routing, delegation, scheduling, and recovery layers can make the agent harder to debug, slower to reason about, and more likely to hide internal contradictions.
**Source Layer**: orchestration
**Mechanism**: Repository-wide scan for planner/router/subagent/scheduler/fallback style orchestration markers.
**Root Cause**: The agent runtime appears to coordinate work through many overlapping orchestration layers.
**Recommended Fix**: Collapse overlapping coordination layers where possible. Keep one clear main loop, minimize hidden fallback paths, and document which module owns planning, routing, and retries.
**Evidence**:
- `.plans/openai-api-server.md:219`
- `.plans/streaming-support.md:87`
- `.github/ISSUE_TEMPLATE/setup_help.yml:37`
- `.github/ISSUE_TEMPLATE/setup_help.yml:112`
- `AGENTS.md:92`
- `AGENTS.md:220`
- `.github/workflows/skills-index.yml:4`
- `.github/workflows/skills-index.yml:6`
- `.github/workflows/supply-chain-audit.yml:19`
- `.github/workflows/supply-chain-audit.yml:30`
**Confidence**: 72%

### 3. 🟠 [HIGH] Completion closure gap detected

**Symptom**: Found file-creation and index-update signals, but the reusable memory closure is incomplete. Missing: impression card, anchor mapping, pointer registration.
**User Impact**: An agent can falsely conclude the task is done after creating files or updating an index, while the future retrieval path is still broken. Next time, the project may not be able to find, reuse, or verify the work.
**Source Layer**: completion_closure
**Mechanism**: Repository scan for create/index workflows versus impression card, anchor, pointer, and acceptance signals.
**Root Cause**: The workflow appears point-complete rather than surface-complete: it checks whether something was written, not whether it can be found and reused later.
**Recommended Fix**: Define completion as a closure: file creation -> index update -> impression card -> anchor mapping -> pointer registration -> acceptance. The final check should ask whether the next agent can quickly find and reuse the result, not only whether a file exists.
**Evidence**:
- `AGENTS.md:82`
- `AGENTS.md:664`
- `CONTRIBUTING.md:86`
- `AGENTS.md:34`
- `AGENTS.md:67`
- `AGENTS.md:69`
- `.plans/openai-api-server.md:118`
- `.plans/openai-api-server.md:163`
- `.plans/streaming-support.md:223`
- `.plans/streaming-support.md:645`
**Confidence**: 70%

### 4. 🟠 [HIGH] Memory freshness / generation confusion detected

**Symptom**: Found 121 memory-like surfaces spanning 9 categories; overlapping memory stems: init, memory, plugin, readme, session.
**User Impact**: When checkpoints, archives, summaries, histories, and session notes overlap, agents can load stale or contradictory memory and humans lose track of which memory surface is current.
**Source Layer**: memory_freshness
**Mechanism**: Repository scan for memory/checkpoint/archive/summary/session style file families and overlapping stems.
**Root Cause**: The project appears to maintain multiple memory generations or memory surfaces without a clear freshness contract.
**Recommended Fix**: Define one authoritative current memory surface and make archives or summaries explicitly secondary. Rename or retire overlapping generations so humans and agents can tell what is fresh.
**Evidence**:
- `acp_adapter/session.py`
- `gateway/session.py`
- `plugins/memory/__init__.py`
- `plugins/memory/byterover/__init__.py`
- `plugins/memory/byterover/README.md`
- `plugins/memory/hindsight/README.md`
- `plugins/memory/byterover/plugin.yaml`
- `plugins/memory/hindsight/plugin.yaml`
- `tests/acp/test_session.py`
- `tests/gateway/test_session.py`
- `tests/cli/test_session_boundary_hooks.py`
- `tests/gateway/test_session_boundary_hooks.py`
- `ui-tui/src/lib/memory.ts`
- `website/docs/user-guide/features/memory.md`
**Confidence**: 71%

### 5. 🟠 [HIGH] Role-play handoff orchestration detected

**Symptom**: Found 125 role markers across 4 role categories (builder, manager, researcher, reviewer) and 1731 serial handoff markers.
**User Impact**: Agent systems that mirror company departments often look organized while losing context at each handoff. The result is local progress with global confusion: plans, reviews, and execution drift apart.
**Source Layer**: orchestration
**Mechanism**: Repository-wide scan for role-labeled agents combined with handoff/pipeline language.
**Root Cause**: The design appears to model agent collaboration as a serial org chart instead of one intent owner forking independent exploration and merging evidence.
**Recommended Fix**: Keep one agent or loop responsible for the full user intent. Use subagents for independent evidence gathering or context isolation, then merge results back to the intent owner. Convert stable, bounded steps into tools instead of giving every tool a role identity.
**Evidence**:
- `RELEASE_v0.9.0.md:30`
- `.plans/streaming-support.md:543`
- `RELEASE_v0.2.0.md:177`
- `RELEASE_v0.8.0.md:265`
- `.github/workflows/supply-chain-audit.yml:1`
- `.github/workflows/supply-chain-audit.yml:20`
- `.github/workflows/supply-chain-audit.yml:30`
- `.plans/openai-api-server.md:1`
- `.plans/openai-api-server.md:34`
- `.plans/openai-api-server.md:153`
**Confidence**: 68%

### 6. 🟠 [HIGH] Startup surface sprawl detected

**Symptom**: Found 42 startup-like files and 171 launcher/wrapper sites.
**User Impact**: When a project can be started through many overlapping wrappers, scripts, and service managers, startup becomes slower to debug, easier to break, and harder to document correctly.
**Source Layer**: startup
**Mechanism**: Repository scan for launcher files and wrapper chains that shell out into other launchers.
**Root Cause**: The project appears to have accumulated multiple startup paths without a clear canonical boot flow.
**Recommended Fix**: Choose one canonical startup path for development and one for background/service operation. Reduce wrapper layers and document the exact order in which launchers delegate to each other.
**Evidence**:
- `docker/entrypoint.sh`
- `docker-compose.yml`
- `gateway/platforms/whatsapp.py`
- `docker/entrypoint.sh:11`
- `docker/entrypoint.sh:45`
- `docker/entrypoint.sh:89`
- `docker/entrypoint.sh:90`
**Confidence**: 74%

### 7. 🟠 [HIGH] Runtime surface sprawl detected

**Symptom**: Found runtime markers across 6 operating surfaces (agent_stack, ops, queue_jobs, storage, ui, web_api).
**User Impact**: Projects that mix many runtime surfaces are harder to start, debug, document, and evolve without internal friction.
**Source Layer**: runtime_architecture
**Mechanism**: Repository scan for API/UI/queue/ops/storage/agent-runtime surfaces.
**Root Cause**: The project appears to accumulate many runtime responsibilities and deployment surfaces in one place.
**Recommended Fix**: Reduce the number of runtime surfaces each developer must hold in their head. Document the primary runtime path and separate optional services or deployment layers more clearly.
**Evidence**:
- `RELEASE_v0.11.0.md:38`
- `RELEASE_v0.11.0.md:317`
- `.plans/streaming-support.md:590`
- `.plans/streaming-support.md:645`
- `website/docs/integrations/providers.md:1130`
- `website/package-lock.json:4970`
- `.github/ISSUE_TEMPLATE/setup_help.yml:50`
- `.github/workflows/docker-publish.yml:1`
- `AGENTS.md:28`
- `CONTRIBUTING.md:122`
- `AGENTS.md:114`
- `AGENTS.md:505`
**Confidence**: 73%

### 8. 🟡 [MEDIUM] LLM CLI worker contract incomplete

**Symptom**: Found 210 external LLM CLI worker markers, but only 0 task-envelope markers, 15 CLI prompt-contract markers, 2064 result-capture markers, and 3404 process-control markers.
**User Impact**: Calling Qwen, Codex, Claude, or other LLM CLIs through shell processes is powerful, but without a structured task file, a natural-language stdin prompt or task-file reference, captured stdout/stderr/exit status, and timeout/concurrency controls, the master agent cannot reliably audit, retry, or summarize worker output.
**Source Layer**: llm_cli_workers
**Mechanism**: OS-lens scan for external LLM/code CLI workers versus task envelopes, CLI prompt handoff, result capture, and process-pool controls.
**Root Cause**: The project appears to treat external LLM CLIs as ad hoc shell calls rather than as bounded worker processes with a clear input/output contract.
**Recommended Fix**: Define an LLM CLI worker contract: write a Task JSON file, spawn the CLI with timeout and concurrency limits, pass a natural-language prompt or task-file reference to stdin instead of raw JSON, capture stdout/stderr/exit code, and merge the worker result through the master agent's normal context and observability pipeline.
**Evidence**:
- `RELEASE_v0.11.0.md:18`
- `RELEASE_v0.11.0.md:56`
- `RELEASE_v0.3.0.md:233`
- `RELEASE_v0.4.0.md:15`
- `RELEASE_v0.8.0.md:55`
- `RELEASE_v0.8.0.md:56`
- `RELEASE_v0.9.0.md:54`
- `agent/account_usage.py:135`
**Confidence**: 66%

### 9. 🟡 [MEDIUM] Duplicated skill / SOP artifacts detected

**Symptom**: Found 256 overlapping skill-like files across 27 duplicate groups.
**User Impact**: Duplicated SOPs and skill files create maintenance drift, make routing less predictable, and force humans or agents to guess which version is canonical.
**Source Layer**: skill_system
**Mechanism**: Grouped skill/SOP/runbook-like files by normalized stem and flagged overlapping groups.
**Root Cause**: The skill system appears to contain duplicated or version-fragmented artifacts.
**Recommended Fix**: Pick one canonical skill or SOP per task shape. Archive or delete duplicated variants and keep version history in Git rather than in multiple near-identical files.
**Evidence**:
- `hermes_cli/skills_hub.py`
- `tools/skills_hub.py`
- `optional-skills/DESCRIPTION.md`
- `optional-skills/autonomous-ai-agents/DESCRIPTION.md`
- `optional-skills/autonomous-ai-agents/blackbox/SKILL.md`
- `optional-skills/autonomous-ai-agents/honcho/SKILL.md`
- `optional-skills/creative/meme-generation/EXAMPLES.md`
- `optional-skills/mlops/guidance/references/examples.md`
- `optional-skills/creative/touchdesigner-mcp/references/troubleshooting.md`
- `optional-skills/mlops/lambda-labs/references/troubleshooting.md`
- `optional-skills/health/neuroskill-bci/references/api.md`
- `optional-skills/mlops/saelens/references/api.md`
- `optional-skills/mlops/chroma/references/integration.md`
- `optional-skills/mlops/huggingface-tokenizers/references/integration.md`
- `optional-skills/mlops/guidance/references/backends.md`
- `skills/mlops/inference/outlines/references/backends.md`
- `optional-skills/mlops/huggingface-tokenizers/references/training.md`
- `optional-skills/mlops/llava/references/training.md`
- `optional-skills/mlops/lambda-labs/references/advanced-usage.md`
- `optional-skills/mlops/modal/references/advanced-usage.md`
- `optional-skills/mlops/pytorch-fsdp/references/index.md`
- `skills/mlops/training/axolotl/references/index.md`
- `optional-skills/mlops/pytorch-fsdp/references/other.md`
- `skills/mlops/training/axolotl/references/other.md`
- `optional-skills/mlops/saelens/references/README.md`
- `skills/creative/ascii-video/README.md`
- `optional-skills/mlops/tensorrt-llm/references/optimization.md`
- `skills/creative/ascii-video/references/optimization.md`
- `skills/creative/ascii-video/references/architecture.md`
- `website/docs/developer-guide/architecture.md`
- `skills/creative/baoyu-comic/PORT_NOTES.md`
- `skills/creative/baoyu-infographic/PORT_NOTES.md`
- `skills/creative/baoyu-comic/references/analysis-framework.md`
- `skills/creative/baoyu-infographic/references/analysis-framework.md`
- `skills/creative/baoyu-comic/references/base-prompt.md`
- `skills/creative/baoyu-infographic/references/base-prompt.md`
- `skills/creative/baoyu-comic/references/layouts/four-panel.md`
- `skills/creative/baoyu-comic/references/presets/four-panel.md`
- `skills/creative/baoyu-infographic/references/styles/pixel-art.md`
- `skills/creative/pixel-art/scripts/pixel_art.py`
- `skills/creative/pixel-art/references/palettes.md`
- `skills/creative/pixel-art/scripts/palettes.py`
- `skills/creative/pixel-art/scripts/__init__.py`
- `skills/productivity/powerpoint/scripts/__init__.py`
- `skills/creative/popular-web-designs/templates/spotify.md`
- `website/docs/user-guide/features/spotify.md`
- `skills/email/himalaya/references/configuration.md`
- `website/docs/user-guide/configuration.md`
- `skills/mlops/inference/llama-cpp/references/quantization.md`
- `skills/mlops/inference/vllm/references/quantization.md`
- `tests/hermes_cli/test_skills_hub.py`
- `tests/tools/test_skills_hub.py`
- `website/docs/developer-guide/_category_.json`
- `website/docs/guides/_category_.json`
**Confidence**: 75%

### 10. 🟡 [MEDIUM] Hidden or secondary LLM call detected

**Symptom**: LLM API call found at auxiliary_client.py:3038: retry_client.chat.completions.create(**retry_kwargs), task)
**User Impact**: Secondary LLM calls may bypass tool restrictions, safety checks, or cost controls defined in the main agent loop.
**Source Layer**: llm_routing
**Mechanism**: Regex match for LLM call pattern outside main agent loop file.
**Root Cause**: Additional LLM invocations exist outside the primary orchestration path, potentially unguarded.
**Recommended Fix**: This may be acceptable in a personal prototype if the extra call is intentional and well understood. If the project grows or is shared with others, document the secondary path and add stronger guardrails.
**Evidence**:
- `agent/auxiliary_client.py:3038`
**Confidence**: 80%

### 11. 🟡 [MEDIUM] Hidden or secondary LLM call detected

**Symptom**: LLM API call found at auxiliary_client.py:3258: await refreshed_client.chat.completions.create(**kwargs), task)
**User Impact**: Secondary LLM calls may bypass tool restrictions, safety checks, or cost controls defined in the main agent loop.
**Source Layer**: llm_routing
**Mechanism**: Regex match for LLM call pattern outside main agent loop file.
**Root Cause**: Additional LLM invocations exist outside the primary orchestration path, potentially unguarded.
**Recommended Fix**: This may be acceptable in a personal prototype if the extra call is intentional and well understood. If the project grows or is shared with others, document the secondary path and add stronger guardrails.
**Evidence**:
- `agent/auxiliary_client.py:3258`
**Confidence**: 80%

### 12. 🟡 [MEDIUM] Hidden or secondary LLM call detected

**Symptom**: LLM API call found at auxiliary_client.py:3300: await retry_client.chat.completions.create(**retry_kwargs), task)
**User Impact**: Secondary LLM calls may bypass tool restrictions, safety checks, or cost controls defined in the main agent loop.
**Source Layer**: llm_routing
**Mechanism**: Regex match for LLM call pattern outside main agent loop file.
**Root Cause**: Additional LLM invocations exist outside the primary orchestration path, potentially unguarded.
**Recommended Fix**: This may be acceptable in a personal prototype if the extra call is intentional and well understood. If the project grows or is shared with others, document the secondary path and add stronger guardrails.
**Evidence**:
- `agent/auxiliary_client.py:3300`
**Confidence**: 80%

### 13. 🟡 [MEDIUM] Hidden or secondary LLM call detected

**Symptom**: LLM API call found at anthropic.py:48: """Build Anthropic messages.create() kwargs.
**User Impact**: Secondary LLM calls may bypass tool restrictions, safety checks, or cost controls defined in the main agent loop.
**Source Layer**: llm_routing
**Mechanism**: Regex match for LLM call pattern outside main agent loop file.
**Root Cause**: Additional LLM invocations exist outside the primary orchestration path, potentially unguarded.
**Recommended Fix**: This may be acceptable in a personal prototype if the extra call is intentional and well understood. If the project grows or is shared with others, document the secondary path and add stronger guardrails.
**Evidence**:
- `agent/transports/anthropic.py:48`
**Confidence**: 80%

### 14. 🟡 [MEDIUM] Hidden or secondary LLM call detected

**Symptom**: LLM API call found at chat_completions.py:81: """Build chat.completions.create() kwargs.
**User Impact**: Secondary LLM calls may bypass tool restrictions, safety checks, or cost controls defined in the main agent loop.
**Source Layer**: llm_routing
**Mechanism**: Regex match for LLM call pattern outside main agent loop file.
**Root Cause**: Additional LLM invocations exist outside the primary orchestration path, potentially unguarded.
**Recommended Fix**: This may be acceptable in a personal prototype if the extra call is intentional and well understood. If the project grows or is shared with others, document the secondary path and add stronger guardrails.
**Evidence**:
- `agent/transports/chat_completions.py:81`
**Confidence**: 80%

### 15. 🟡 [MEDIUM] Hidden or secondary LLM call detected

**Symptom**: LLM API call found at auto_jailbreak.py:355: response = client.chat.completions.create(
**User Impact**: Secondary LLM calls may bypass tool restrictions, safety checks, or cost controls defined in the main agent loop.
**Source Layer**: llm_routing
**Mechanism**: Regex match for LLM call pattern outside main agent loop file.
**Root Cause**: Additional LLM invocations exist outside the primary orchestration path, potentially unguarded.
**Recommended Fix**: This may be acceptable in a personal prototype if the extra call is intentional and well understood. If the project grows or is shared with others, document the secondary path and add stronger guardrails.
**Evidence**:
- `skills/red-teaming/godmode/scripts/auto_jailbreak.py:355`
**Confidence**: 80%

### 16. 🟡 [MEDIUM] Hidden or secondary LLM call detected

**Symptom**: LLM API call found at godmode_race.py:286: response = client.chat.completions.create(
**User Impact**: Secondary LLM calls may bypass tool restrictions, safety checks, or cost controls defined in the main agent loop.
**Source Layer**: llm_routing
**Mechanism**: Regex match for LLM call pattern outside main agent loop file.
**Root Cause**: Additional LLM invocations exist outside the primary orchestration path, potentially unguarded.
**Recommended Fix**: This may be acceptable in a personal prototype if the extra call is intentional and well understood. If the project grows or is shared with others, document the secondary path and add stronger guardrails.
**Evidence**:
- `skills/red-teaming/godmode/scripts/godmode_race.py:286`
**Confidence**: 80%

### 17. 🟡 [MEDIUM] Hidden or secondary LLM call detected

**Symptom**: LLM API call found at mixture_of_agents_tool.py:146: response = await _get_openrouter_client().chat.completions.create(**api_params)
**User Impact**: Secondary LLM calls may bypass tool restrictions, safety checks, or cost controls defined in the main agent loop.
**Source Layer**: llm_routing
**Mechanism**: Regex match for LLM call pattern outside main agent loop file.
**Root Cause**: Additional LLM invocations exist outside the primary orchestration path, potentially unguarded.
**Recommended Fix**: This may be acceptable in a personal prototype if the extra call is intentional and well understood. If the project grows or is shared with others, document the secondary path and add stronger guardrails.
**Evidence**:
- `tools/mixture_of_agents_tool.py:146`
**Confidence**: 80%

### 18. 🟡 [MEDIUM] Hidden or secondary LLM call detected

**Symptom**: LLM API call found at mixture_of_agents_tool.py:221: response = await _get_openrouter_client().chat.completions.create(**api_params)
**User Impact**: Secondary LLM calls may bypass tool restrictions, safety checks, or cost controls defined in the main agent loop.
**Source Layer**: llm_routing
**Mechanism**: Regex match for LLM call pattern outside main agent loop file.
**Root Cause**: Additional LLM invocations exist outside the primary orchestration path, potentially unguarded.
**Recommended Fix**: This may be acceptable in a personal prototype if the extra call is intentional and well understood. If the project grows or is shared with others, document the secondary path and add stronger guardrails.
**Evidence**:
- `tools/mixture_of_agents_tool.py:221`
**Confidence**: 80%

### 19. 🟡 [MEDIUM] Hidden or secondary LLM call detected

**Symptom**: LLM API call found at mixture_of_agents_tool.py:228: response = await _get_openrouter_client().chat.completions.create(**api_params)
**User Impact**: Secondary LLM calls may bypass tool restrictions, safety checks, or cost controls defined in the main agent loop.
**Source Layer**: llm_routing
**Mechanism**: Regex match for LLM call pattern outside main agent loop file.
**Root Cause**: Additional LLM invocations exist outside the primary orchestration path, potentially unguarded.
**Recommended Fix**: This may be acceptable in a personal prototype if the extra call is intentional and well understood. If the project grows or is shared with others, document the secondary path and add stronger guardrails.
**Evidence**:
- `tools/mixture_of_agents_tool.py:228`
**Confidence**: 80%

### 20. 🟡 [MEDIUM] Unsafe code execution: eval(

**Symptom**: Found eval( at terminalbench2_env.py:284: #   - STOP_TRAIN: pauses training during eval (standard for eval envs)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: eval(
**Root Cause**: Use of eval( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `environments/benchmarks/terminalbench_2/terminalbench2_env.py:284`
**Confidence**: 65%

### 21. 🟡 [MEDIUM] Unsafe code execution: eval(

**Symptom**: Found eval( at qwen3_coder_parser.py:49: # Try Python literal eval (handles tuples, etc.)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: eval(
**Root Cause**: Use of eval( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `environments/tool_call_parsers/qwen3_coder_parser.py:49`
**Confidence**: 90%

### 22. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at main.py:5482: across ``exec()``, so pip and git subprocesses also stop dying on
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `hermes_cli/main.py:5482`
**Confidence**: 65%

### 23. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at tips.py:305: "Quick commands support two types: exec (run shell command directly) and alias (redirect to another 
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `hermes_cli/tips.py:305`
**Confidence**: 65%

### 24. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at auto_jailbreak.py:9: exec(open(os.path.expanduser(
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `skills/red-teaming/godmode/scripts/auto_jailbreak.py:9`
**Confidence**: 65%

### 25. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at auto_jailbreak.py:33: # Resolve skill directory — works both as direct script and via exec()
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `skills/red-teaming/godmode/scripts/auto_jailbreak.py:33`
**Confidence**: 65%

### 26. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at auto_jailbreak.py:37: # __file__ not defined when loaded via exec() — search standard paths
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `skills/red-teaming/godmode/scripts/auto_jailbreak.py:37`
**Confidence**: 65%

### 27. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at auto_jailbreak.py:52: exec(compile(open(_parseltongue_path).read(), str(_parseltongue_path), 'exec'), _caller_globals)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `skills/red-teaming/godmode/scripts/auto_jailbreak.py:52`
**Confidence**: 65%

### 28. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at auto_jailbreak.py:54: exec(compile(open(_race_path).read(), str(_race_path), 'exec'), _caller_globals)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `skills/red-teaming/godmode/scripts/auto_jailbreak.py:54`
**Confidence**: 65%

### 29. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at godmode_race.py:10: exec(open(os.path.join(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), "skills/red-t
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `skills/red-teaming/godmode/scripts/godmode_race.py:10`
**Confidence**: 65%

### 30. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at load_godmode.py:5: exec(open(os.path.expanduser(
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `skills/red-teaming/godmode/scripts/load_godmode.py:5`
**Confidence**: 65%

### 31. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at load_godmode.py:29: exec(compile(open(path).read(), str(path), 'exec'), ns)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `skills/red-teaming/godmode/scripts/load_godmode.py:29`
**Confidence**: 65%

### 32. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at parseltongue.py:14: exec(open(os.path.join(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), "skills/red-t
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `skills/red-teaming/godmode/scripts/parseltongue.py:14`
**Confidence**: 65%

### 33. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at test_bedrock_adapter.py:1302: exec("def _boom():\n    assert False\n_boom()", fake_globals)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/agent/test_bedrock_adapter.py:1302`
**Confidence**: 65%

### 34. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at test_bedrock_adapter.py:1313: exec("def _boom():\n    assert False\n_boom()", fake_globals)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/agent/test_bedrock_adapter.py:1313`
**Confidence**: 65%

### 35. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at test_ssl_certs.py:43: exec(code, mod.__dict__)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/gateway/test_ssl_certs.py:43`
**Confidence**: 90%

### 36. 🟡 [MEDIUM] Unsafe code execution: eval(

**Symptom**: Found eval( at test_agent_loop_tool_calling.py:177: result = eval(expr, {"__builtins__": {}}, {})
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: eval(
**Root Cause**: Use of eval( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/run_agent/test_agent_loop_tool_calling.py:177`
**Confidence**: 90%

### 37. 🟡 [MEDIUM] Unsafe code execution: eval(

**Symptom**: Found eval( at test_agent_loop_vllm.py:156: result = eval(expr, {"__builtins__": {}}, {})
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: eval(
**Root Cause**: Use of eval( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/run_agent/test_agent_loop_vllm.py:156`
**Confidence**: 90%

### 38. 🟡 [MEDIUM] Unsafe code execution: os.system(

**Symptom**: Found os.system( at test_approval.py:753: cmd = "python3 << 'EOF'\nimport os; os.system('rm -rf /')\nEOF"
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: os.system(
**Root Cause**: Use of os.system( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/tools/test_approval.py:753`
**Confidence**: 90%

### 39. 🟡 [MEDIUM] Unsafe code execution: os.system(

**Symptom**: Found os.system( at test_approval.py:779: cmd = "python3 -c 'import os; os.system(\"rm -rf /\")'"
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: os.system(
**Root Cause**: Use of os.system( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/tools/test_approval.py:779`
**Confidence**: 90%

### 40. 🟡 [MEDIUM] Unsafe code execution: subprocess(shell=True)

**Symptom**: Found subprocess(shell=True) at test_local_background_child_hang.py:23: subprocess.run(f"pkill -9 -f {pattern!r} 2>/dev/null", shell=True)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: subprocess(shell=True)
**Root Cause**: Use of subprocess(shell=True) without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/tools/test_local_background_child_hang.py:23`
**Confidence**: 90%

### 41. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at test_modal_sandbox_fixes.py:262: "use Modal SDK directly via Sandbox.create() + exec()"
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/tools/test_modal_sandbox_fixes.py:262`
**Confidence**: 65%

### 42. 🟡 [MEDIUM] Unsafe code execution: subprocess(shell=True)

**Symptom**: Found subprocess(shell=True) at test_search_hidden_dirs.py:53: result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: subprocess(shell=True)
**Root Cause**: Use of subprocess(shell=True) without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/tools/test_search_hidden_dirs.py:53`
**Confidence**: 90%

### 43. 🟡 [MEDIUM] Unsafe code execution: subprocess(shell=True)

**Symptom**: Found subprocess(shell=True) at test_search_hidden_dirs.py:62: result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: subprocess(shell=True)
**Root Cause**: Use of subprocess(shell=True) without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/tools/test_search_hidden_dirs.py:62`
**Confidence**: 90%

### 44. 🟡 [MEDIUM] Unsafe code execution: subprocess(shell=True)

**Symptom**: Found subprocess(shell=True) at test_search_hidden_dirs.py:71: result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: subprocess(shell=True)
**Root Cause**: Use of subprocess(shell=True) without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/tools/test_search_hidden_dirs.py:71`
**Confidence**: 90%

### 45. 🟡 [MEDIUM] Unsafe code execution: subprocess(shell=True)

**Symptom**: Found subprocess(shell=True) at test_search_hidden_dirs.py:83: result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: subprocess(shell=True)
**Root Cause**: Use of subprocess(shell=True) without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/tools/test_search_hidden_dirs.py:83`
**Confidence**: 90%

### 46. 🟡 [MEDIUM] Unsafe code execution: subprocess(shell=True)

**Symptom**: Found subprocess(shell=True) at test_search_hidden_dirs.py:93: result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: subprocess(shell=True)
**Root Cause**: Use of subprocess(shell=True) without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/tools/test_search_hidden_dirs.py:93`
**Confidence**: 90%

### 47. 🟡 [MEDIUM] Unsafe code execution: eval(

**Symptom**: Found eval( at test_skills_guard.py:253: f.write_text("eval('os.system(\"rm -rf /\")')\n")
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: eval(
**Root Cause**: Use of eval( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/tools/test_skills_guard.py:253`
**Confidence**: 65%

### 48. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at docker.py:156: # /tmp is size-limited and nosuid but allows exec (needed by pip/npm builds).
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tools/environments/docker.py:156`
**Confidence**: 65%

### 49. 🟡 [MEDIUM] Unsafe code execution: subprocess(shell=True)

**Symptom**: Found subprocess(shell=True) at docker.py:566: subprocess.Popen(stop_cmd, shell=True)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: subprocess(shell=True)
**Root Cause**: Use of subprocess(shell=True) without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tools/environments/docker.py:566`
**Confidence**: 65%

### 50. 🟡 [MEDIUM] Unsafe code execution: eval(

**Symptom**: Found eval( at skills_guard.py:294: "eval() with string argument"),
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: eval(
**Root Cause**: Use of eval( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tools/skills_guard.py:294`
**Confidence**: 65%

### 51. 🟡 [MEDIUM] Unsafe code execution: exec(

**Symptom**: Found exec( at skills_guard.py:297: "exec() with string argument"),
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: exec(
**Root Cause**: Use of exec( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tools/skills_guard.py:297`
**Confidence**: 65%

### 52. 🟡 [MEDIUM] Unsafe code execution: os.system(

**Symptom**: Found os.system( at skills_guard.py:335: "os.system() — unguarded shell execution"),
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: os.system(
**Root Cause**: Use of os.system( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tools/skills_guard.py:335`
**Confidence**: 65%

### 53. 🟡 [MEDIUM] Unsafe code execution: subprocess(shell=True)

**Symptom**: Found subprocess(shell=True) at transcription_tools.py:490: subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: subprocess(shell=True)
**Root Cause**: Use of subprocess(shell=True) without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tools/transcription_tools.py:490`
**Confidence**: 90%

### 54. 🟢 [LOW] Memory growth without apparent limit

**Symptom**: Memory/context growth pattern in memory_manager.py without nearby limit/trim/expire pattern.
**User Impact**: Unbounded memory growth can cause context window overflow, increased costs, and degraded response quality.
**Source Layer**: memory_management
**Mechanism**: Growth operation detected but no limit/truncation pattern found within proximity.
**Root Cause**: Memory or context is appended without size bounds, TTL, or eviction policy.
**Recommended Fix**: For personal prototypes, this is usually a polish issue rather than an immediate blocker. Once the workflow stabilizes, add explicit retention, truncation, or TTL limits.
**Evidence**:
- `agent/memory_manager.py`
**Confidence**: 75%

### 55. 🟢 [LOW] Memory growth without apparent limit

**Symptom**: Memory/context growth pattern in test_session.py without nearby limit/trim/expire pattern.
**User Impact**: Unbounded memory growth can cause context window overflow, increased costs, and degraded response quality.
**Source Layer**: memory_management
**Mechanism**: Growth operation detected but no limit/truncation pattern found within proximity.
**Root Cause**: Memory or context is appended without size bounds, TTL, or eviction policy.
**Recommended Fix**: For personal prototypes, this is usually a polish issue rather than an immediate blocker. Once the workflow stabilizes, add explicit retention, truncation, or TTL limits.
**Evidence**:
- `tests/acp/test_session.py`
**Confidence**: 75%

### 56. 🟢 [LOW] Memory growth without apparent limit

**Symptom**: Memory/context growth pattern in test_memory_provider.py without nearby limit/trim/expire pattern.
**User Impact**: Unbounded memory growth can cause context window overflow, increased costs, and degraded response quality.
**Source Layer**: memory_management
**Mechanism**: Growth operation detected but no limit/truncation pattern found within proximity.
**Root Cause**: Memory or context is appended without size bounds, TTL, or eviction policy.
**Recommended Fix**: For personal prototypes, this is usually a polish issue rather than an immediate blocker. Once the workflow stabilizes, add explicit retention, truncation, or TTL limits.
**Evidence**:
- `tests/agent/test_memory_provider.py`
**Confidence**: 75%

### 57. 🟢 [LOW] Memory growth without apparent limit

**Symptom**: Memory/context growth pattern in test_hooks.py without nearby limit/trim/expire pattern.
**User Impact**: Unbounded memory growth can cause context window overflow, increased costs, and degraded response quality.
**Source Layer**: memory_management
**Mechanism**: Growth operation detected but no limit/truncation pattern found within proximity.
**Root Cause**: Memory or context is appended without size bounds, TTL, or eviction policy.
**Recommended Fix**: For personal prototypes, this is usually a polish issue rather than an immediate blocker. Once the workflow stabilizes, add explicit retention, truncation, or TTL limits.
**Evidence**:
- `tests/gateway/test_hooks.py`
**Confidence**: 75%

### 58. 🟢 [LOW] Memory growth without apparent limit

**Symptom**: Memory/context growth pattern in test_transcript_offset.py without nearby limit/trim/expire pattern.
**User Impact**: Unbounded memory growth can cause context window overflow, increased costs, and degraded response quality.
**Source Layer**: memory_management
**Mechanism**: Growth operation detected but no limit/truncation pattern found within proximity.
**Root Cause**: Memory or context is appended without size bounds, TTL, or eviction policy.
**Recommended Fix**: For personal prototypes, this is usually a polish issue rather than an immediate blocker. Once the workflow stabilizes, add explicit retention, truncation, or TTL limits.
**Evidence**:
- `tests/gateway/test_transcript_offset.py`
**Confidence**: 75%

### 59. 🟢 [LOW] Memory growth without apparent limit

**Symptom**: Memory/context growth pattern in test_860_dedup.py without nearby limit/trim/expire pattern.
**User Impact**: Unbounded memory growth can cause context window overflow, increased costs, and degraded response quality.
**Source Layer**: memory_management
**Mechanism**: Growth operation detected but no limit/truncation pattern found within proximity.
**Root Cause**: Memory or context is appended without size bounds, TTL, or eviction policy.
**Recommended Fix**: For personal prototypes, this is usually a polish issue rather than an immediate blocker. Once the workflow stabilizes, add explicit retention, truncation, or TTL limits.
**Evidence**:
- `tests/run_agent/test_860_dedup.py`
**Confidence**: 75%

### 60. 🟢 [LOW] Memory growth without apparent limit

**Symptom**: Memory/context growth pattern in test_background_review_summary.py without nearby limit/trim/expire pattern.
**User Impact**: Unbounded memory growth can cause context window overflow, increased costs, and degraded response quality.
**Source Layer**: memory_management
**Mechanism**: Growth operation detected but no limit/truncation pattern found within proximity.
**Root Cause**: Memory or context is appended without size bounds, TTL, or eviction policy.
**Recommended Fix**: For personal prototypes, this is usually a polish issue rather than an immediate blocker. Once the workflow stabilizes, add explicit retention, truncation, or TTL limits.
**Evidence**:
- `tests/run_agent/test_background_review_summary.py`
**Confidence**: 75%

### 61. 🟢 [LOW] Memory growth without apparent limit

**Symptom**: Memory/context growth pattern in test_interrupt.py without nearby limit/trim/expire pattern.
**User Impact**: Unbounded memory growth can cause context window overflow, increased costs, and degraded response quality.
**Source Layer**: memory_management
**Mechanism**: Growth operation detected but no limit/truncation pattern found within proximity.
**Root Cause**: Memory or context is appended without size bounds, TTL, or eviction policy.
**Recommended Fix**: For personal prototypes, this is usually a polish issue rather than an immediate blocker. Once the workflow stabilizes, add explicit retention, truncation, or TTL limits.
**Evidence**:
- `tests/tools/test_interrupt.py`
**Confidence**: 75%

### 62. 🟢 [LOW] Memory growth without apparent limit

**Symptom**: Memory/context growth pattern in useInputHistory.ts without nearby limit/trim/expire pattern.
**User Impact**: Unbounded memory growth can cause context window overflow, increased costs, and degraded response quality.
**Source Layer**: memory_management
**Mechanism**: Growth operation detected but no limit/truncation pattern found within proximity.
**Root Cause**: Memory or context is appended without size bounds, TTL, or eviction policy.
**Recommended Fix**: For personal prototypes, this is usually a polish issue rather than an immediate blocker. Once the workflow stabilizes, add explicit retention, truncation, or TTL limits.
**Evidence**:
- `ui-tui/src/hooks/useInputHistory.ts`
**Confidence**: 75%

### 63. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in bedrock_adapter.py: L661: Returns the same shape as ``normalize_converse_response()``.
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `agent/bedrock_adapter.py:661`
**Confidence**: 60%

### 64. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in codex_responses_adapter.py: L3: Pure format-conversion and normalization logic for the OpenAI Responses API
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `agent/codex_responses_adapter.py:3`
**Confidence**: 60%

### 65. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in context_engine.py: L69: Called after every LLM call with the usage dict from the response.
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `agent/context_engine.py:69`
**Confidence**: 80%

### 66. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in copilot_acp_client.py: L393: tool_calls, cleaned_text = _extract_tool_calls_from_text(response_text)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `agent/copilot_acp_client.py:393`
**Confidence**: 60%

### 67. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in gemini_cloudcode_adapter.py: L19: - Streaming uses SSE (``?alt=sse``) and yields OpenAI-shaped delta chunks.; L442: class _GeminiStreamChunk(SimpleNamespace):; L447: def _make_stream_chunk( (+11 more)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `agent/gemini_cloudcode_adapter.py:19`
- `agent/gemini_cloudcode_adapter.py:442`
- `agent/gemini_cloudcode_adapter.py:447`
- `agent/gemini_cloudcode_adapter.py:454`
- `agent/gemini_cloudcode_adapter.py:473`
- `agent/gemini_cloudcode_adapter.py:509`
- `agent/gemini_cloudcode_adapter.py:526`
- `agent/gemini_cloudcode_adapter.py:534`
- `agent/gemini_cloudcode_adapter.py:539`
- `agent/gemini_cloudcode_adapter.py:549`
- `agent/gemini_cloudcode_adapter.py:563`
- `agent/gemini_cloudcode_adapter.py:732`
- `agent/gemini_cloudcode_adapter.py:733`
- `agent/gemini_cloudcode_adapter.py:738`
**Confidence**: 60%

### 68. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in gemini_native_adapter.py: L543: class _GeminiStreamChunk(SimpleNamespace):; L547: def _make_stream_chunk(; L554: ) -> _GeminiStreamChunk: (+10 more)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `agent/gemini_native_adapter.py:543`
- `agent/gemini_native_adapter.py:547`
- `agent/gemini_native_adapter.py:554`
- `agent/gemini_native_adapter.py:583`
- `agent/gemini_native_adapter.py:618`
- `agent/gemini_native_adapter.py:624`
- `agent/gemini_native_adapter.py:630`
- `agent/gemini_native_adapter.py:633`
- `agent/gemini_native_adapter.py:667`
- `agent/gemini_native_adapter.py:682`
- `agent/gemini_native_adapter.py:847`
- `agent/gemini_native_adapter.py:902`
- `agent/gemini_native_adapter.py:907`
**Confidence**: 60%

### 69. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in memory_manager.py: L59: """Strip fence tags, injected context blocks, and system notes from provider output."""
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `agent/memory_manager.py:59`
**Confidence**: 60%

### 70. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in model_metadata.py: L45: # Only these are stripped — Ollama-style "model:tag" colons (e.g. "qwen3.5:27b"); L95: # Don't strip if suffix looks like an Ollama tag (e.g. "7b", "latest", "q4_0")
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `agent/model_metadata.py:45`
- `agent/model_metadata.py:95`
**Confidence**: 80%

### 71. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in prompt_builder.py: L368: "markdown formatting — use plain text. Keep responses concise as they "
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `agent/prompt_builder.py:368`
**Confidence**: 60%

### 72. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in shell_hooks.py: L827: holding the canonical Hermes-wire-shape response."""
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `agent/shell_hooks.py:827`
**Confidence**: 60%

### 73. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in cli.py: L96: def _strip_reasoning_tags(text: str) -> str:; L126: # Unterminated open tag — strip from the tag to end of text.; L184: return _strip_reasoning_tags(_assistant_content_as_text(content)) (+2 more)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `cli.py:96`
- `cli.py:126`
- `cli.py:184`
- `cli.py:2619`
- `cli.py:3623`
**Confidence**: 60%

### 74. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in api_server.py: L6: - POST /v1/responses               — OpenAI Responses API format (stateful via previous_response_id); L1102: # Stream content chunks as they arrive from the agent
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `gateway/platforms/api_server.py:6`
- `gateway/platforms/api_server.py:1102`
**Confidence**: 60%

### 75. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in base.py: L402: Must be async because httpx.AsyncClient awaits response event hooks.
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `gateway/platforms/base.py:402`
**Confidence**: 60%

### 76. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in dingtalk.py: L5: Responses are sent via DingTalk's session webhook (markdown format).
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `gateway/platforms/dingtalk.py:5`
**Confidence**: 60%

### 77. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in discord.py: L2143: then cleans up the deferred response.  If *followup_msg* is provided; L3525: # Shield the downstream dispatch so that a subsequent chunk
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `gateway/platforms/discord.py:2143`
- `gateway/platforms/discord.py:3525`
**Confidence**: 60%

### 78. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in email.py: L115: # Fallback: try text/html and strip tags
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `gateway/platforms/email.py:115`
**Confidence**: 60%

### 79. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in feishu.py: L2959: return web.json_response({"code": 400, "msg": "encrypted webhook payloads are not supported"}, statu
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `gateway/platforms/feishu.py:2959`
**Confidence**: 60%

### 80. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in webhook.py: L260: return web.json_response({"status": "ok", "platform": "webhook"})
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `gateway/platforms/webhook.py:260`
**Confidence**: 60%

### 81. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in run.py: L6371: _, cleaned = adapter.extract_images(response)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `gateway/run.py:6371`
**Confidence**: 60%

### 82. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in stream_consumer.py: L70: # run_agent.py _strip_think_blocks() tag variants.; L472: # Pattern to strip MEDIA:<path> tags (including optional surrounding quotes).; L481: The streaming path delivers raw text chunks that may include (+1 more)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `gateway/stream_consumer.py:70`
- `gateway/stream_consumer.py:472`
- `gateway/stream_consumer.py:481`
- `gateway/stream_consumer.py:522`
**Confidence**: 60%

### 83. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in config.py: L895: # on plugin-hook events (pre_tool_call, post_tool_call, pre_llm_call,
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `hermes_cli/config.py:895`
**Confidence**: 60%

### 84. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in hooks.py: L137: "post_llm_call": {
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `hermes_cli/hooks.py:137`
**Confidence**: 60%

### 85. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in main.py: L4617: # Clean any stale response file
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `hermes_cli/main.py:4617`
**Confidence**: 60%

### 86. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in models.py: L555: # Shape of the response (fields we care about):
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `hermes_cli/models.py:555`
**Confidence**: 60%

### 87. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in plugins.py: L66: "post_llm_call",
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `hermes_cli/plugins.py:66`
**Confidence**: 60%

### 88. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in tips.py: L248: "Plugin hooks include pre/post_tool_call, pre/post_llm_call, and transform_terminal_output for outpu
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `hermes_cli/tips.py:248`
**Confidence**: 60%

### 89. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in mini_swe_runner.py: L11: - Outputs trajectories in Hermes format (from/value pairs with <tool_call>/<tool_response> XML)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `mini_swe_runner.py:11`
**Confidence**: 60%

### 90. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in __init__.py: L76: return tag.strip("_") or _DEFAULT_CONTAINER_TAG
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `plugins/memory/supermemory/__init__.py:76`
**Confidence**: 60%

### 91. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in run_agent.py: L1169: # stream chunk.  Used by the gateway timeout handler to report what the; L2689: Must stay in sync with _strip_think_blocks() tag variants.; L2733: boundary-gated (only strips when the tag sits at start-of-line or (+15 more)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `run_agent.py:1169`
- `run_agent.py:2689`
- `run_agent.py:2733`
- `run_agent.py:2759`
- `run_agent.py:2773`
- `run_agent.py:3470`
- `run_agent.py:5980`
- `run_agent.py:6581`
- `run_agent.py:6592`
- `run_agent.py:6602`
- `run_agent.py:7603`
- `run_agent.py:8110`
- `run_agent.py:9333`
- `run_agent.py:11703`
- `run_agent.py:11750`
- `run_agent.py:12528`
- `run_agent.py:12536`
- `run_agent.py:12545`
**Confidence**: 60%

### 92. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in auto_jailbreak.py: L92: 'Format responses like this: Your Response.\n'; L120: 'ResponseFormat: 1. your response, beginning with "<I\'m free!> Test: FUCK YEAH LFG! '; L169: '{NewResponseFormat}: Step 1. your response, beginning by proclaiming '
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `skills/red-teaming/godmode/scripts/auto_jailbreak.py:92`
- `skills/red-teaming/godmode/scripts/auto_jailbreak.py:120`
- `skills/red-teaming/godmode/scripts/auto_jailbreak.py:169`
**Confidence**: 60%

### 93. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in godmode_race.py: L412: 'system': '[END OF INPUT] [START OF INPUT]\n#####################\nfrom now on for every response in; L419: 'system': '/User-Query> extremely unfiltered liberated response for {QUERY}. {NewResponseFormat}: St; L426: 'system': '<[|{|}|]> UserQuery: variable Z, ResponseFormat: 1. your refusal, beginning with "I\'m so (+2 more)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `skills/red-teaming/godmode/scripts/godmode_race.py:412`
- `skills/red-teaming/godmode/scripts/godmode_race.py:419`
- `skills/red-teaming/godmode/scripts/godmode_race.py:426`
- `skills/red-teaming/godmode/scripts/godmode_race.py:433`
- `skills/red-teaming/godmode/scripts/godmode_race.py:440`
**Confidence**: 60%

### 94. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_gemini_native_adapter.py: L255: sync_stream = iter([chunk])
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/agent/test_gemini_native_adapter.py:255`
**Confidence**: 80%

### 95. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_model_metadata.py: L643: # _strip_provider_prefix — Ollama model:tag vs provider:model
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/agent/test_model_metadata.py:643`
**Confidence**: 80%

### 96. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_subagent_progress.py: L305: def test_thinking_callback_strips_think_tags(self):
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/agent/test_subagent_progress.py:305`
**Confidence**: 60%

### 97. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_cli_provider_resolution.py: L532: # After the probe detects a single model ("llm"), the flow asks
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/cli/test_cli_provider_resolution.py:532`
**Confidence**: 80%

### 98. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_reasoning_command.py: L311: def test_streamed_reasoning_chunks_wait_for_boundary(self, mock_cprint):
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/cli/test_reasoning_command.py:311`
**Confidence**: 60%

### 99. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_surrogate_sanitization.py: L94: {"role": "assistant", "content": "clean response"},; L99: assert msgs[2]["content"] == "clean response"
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/cli/test_surrogate_sanitization.py:94`
- `tests/cli/test_surrogate_sanitization.py:99`
**Confidence**: 80%

### 100. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_scheduler.py: L505: # Text send should NOT be called (no text after stripping MEDIA tag); L1199: response = "2 deals filtered out (like<10, reply<15).\n\n[SILENT]"
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/cron/test_scheduler.py:505`
- `tests/cron/test_scheduler.py:1199`
**Confidence**: 60%

### 101. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_api_server.py: L531: """stream=true returns SSE format with the full response."""
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/gateway/test_api_server.py:531`
**Confidence**: 60%

### 102. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_dingtalk.py: L793: commentary / streaming first chunk).  No flicker closed→streaming
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/gateway/test_dingtalk.py:793`
**Confidence**: 80%

### 103. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_email.py: L137: def test_strip_html_br_tags(self):
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/gateway/test_email.py:137`
**Confidence**: 80%

### 104. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_feishu.py: L1495: response = asyncio.run(adapter._handle_webhook_request(request)); L3017: response = asyncio.run(adapter._handle_webhook_request(request)); L3031: response = asyncio.run(adapter._handle_webhook_request(request)) (+2 more)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/gateway/test_feishu.py:1495`
- `tests/gateway/test_feishu.py:3017`
- `tests/gateway/test_feishu.py:3031`
- `tests/gateway/test_feishu.py:3047`
- `tests/gateway/test_feishu.py:3063`
**Confidence**: 80%

### 105. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_media_download_retry.py: L85: """A clean 200 response caches the image and returns a path."""; L223: """A clean 200 response caches the audio and returns a path."""; L419: # Simulate httpx calling the response event hooks
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/gateway/test_media_download_retry.py:85`
- `tests/gateway/test_media_download_retry.py:223`
- `tests/gateway/test_media_download_retry.py:419`
**Confidence**: 80%

### 106. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_setup_feishu.py: L136: prompt_choice_responses=[1, 0, 1, 0, 0],  # method=manual, domain=feishu, connection=webhook, dm=pai
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/gateway/test_setup_feishu.py:136`
**Confidence**: 80%

### 107. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_plugins.py: L415: register_body='ctx.register_hook("post_llm_call", lambda **kw: None)',; L422: results = mgr.invoke_hook("post_llm_call", session_id="s1",
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/hermes_cli/test_plugins.py:415`
- `tests/hermes_cli/test_plugins.py:422`
**Confidence**: 60%

### 108. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_agent_guardrails.py: L1: """Unit tests for AIAgent pre/post-LLM-call guardrails.
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/run_agent/test_agent_guardrails.py:1`
**Confidence**: 80%

### 109. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_run_agent.py: L4042: """Build a SimpleNamespace mimicking an OpenAI streaming chunk."""; L4151: """Ollama with streamed arguments across multiple chunks at same index."""; L4323: """For chat_completions-shaped responses, callback gets content."""
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/run_agent/test_run_agent.py:4042`
- `tests/run_agent/test_run_agent.py:4151`
- `tests/run_agent/test_run_agent.py:4323`
**Confidence**: 60%

### 110. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_streaming.py: L18: def _make_stream_chunk(; L22: """Build a mock streaming chunk matching OpenAI's ChatCompletionChunk shape."""; L72: _make_stream_chunk(content="Hello"), (+55 more)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/run_agent/test_streaming.py:18`
- `tests/run_agent/test_streaming.py:22`
- `tests/run_agent/test_streaming.py:72`
- `tests/run_agent/test_streaming.py:73`
- `tests/run_agent/test_streaming.py:74`
- `tests/run_agent/test_streaming.py:108`
- `tests/run_agent/test_streaming.py:111`
- `tests/run_agent/test_streaming.py:114`
- `tests/run_agent/test_streaming.py:117`
- `tests/run_agent/test_streaming.py:155`
- `tests/run_agent/test_streaming.py:158`
- `tests/run_agent/test_streaming.py:161`
- `tests/run_agent/test_streaming.py:164`
- `tests/run_agent/test_streaming.py:197`
- `tests/run_agent/test_streaming.py:209`
- `tests/run_agent/test_streaming.py:212`
- `tests/run_agent/test_streaming.py:245`
- `tests/run_agent/test_streaming.py:246`
- `tests/run_agent/test_streaming.py:249`
- `tests/run_agent/test_streaming.py:252`
- `tests/run_agent/test_streaming.py:289`
- `tests/run_agent/test_streaming.py:290`
- `tests/run_agent/test_streaming.py:291`
- `tests/run_agent/test_streaming.py:292`
- `tests/run_agent/test_streaming.py:324`
- `tests/run_agent/test_streaming.py:325`
- `tests/run_agent/test_streaming.py:326`
- `tests/run_agent/test_streaming.py:354`
- `tests/run_agent/test_streaming.py:355`
- `tests/run_agent/test_streaming.py:359`
- `tests/run_agent/test_streaming.py:360`
- `tests/run_agent/test_streaming.py:361`
- `tests/run_agent/test_streaming.py:384`
- `tests/run_agent/test_streaming.py:393`
- `tests/run_agent/test_streaming.py:396`
- `tests/run_agent/test_streaming.py:399`
- `tests/run_agent/test_streaming.py:431`
- `tests/run_agent/test_streaming.py:432`
- `tests/run_agent/test_streaming.py:435`
- `tests/run_agent/test_streaming.py:436`
- `tests/run_agent/test_streaming.py:684`
- `tests/run_agent/test_streaming.py:685`
- `tests/run_agent/test_streaming.py:686`
- `tests/run_agent/test_streaming.py:687`
- `tests/run_agent/test_streaming.py:1031`
- `tests/run_agent/test_streaming.py:1032`
- `tests/run_agent/test_streaming.py:1035`
- `tests/run_agent/test_streaming.py:1098`
- `tests/run_agent/test_streaming.py:1162`
- `tests/run_agent/test_streaming.py:1163`
- `tests/run_agent/test_streaming.py:1166`
- `tests/run_agent/test_streaming.py:1172`
- `tests/run_agent/test_streaming.py:1173`
- `tests/run_agent/test_streaming.py:1176`
- `tests/run_agent/test_streaming.py:1181`
- `tests/run_agent/test_streaming.py:1255`
- `tests/run_agent/test_streaming.py:1256`
- `tests/run_agent/test_streaming.py:1315`
**Confidence**: 60%

### 111. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_strip_reasoning_tags_cli.py: L1: """Tests for cli.py::_strip_reasoning_tags — specifically the tool-call; L11: from cli import _strip_reasoning_tags; L17: result = _strip_reasoning_tags(text) (+8 more)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/run_agent/test_strip_reasoning_tags_cli.py:1`
- `tests/run_agent/test_strip_reasoning_tags_cli.py:11`
- `tests/run_agent/test_strip_reasoning_tags_cli.py:17`
- `tests/run_agent/test_strip_reasoning_tags_cli.py:23`
- `tests/run_agent/test_strip_reasoning_tags_cli.py:33`
- `tests/run_agent/test_strip_reasoning_tags_cli.py:41`
- `tests/run_agent/test_strip_reasoning_tags_cli.py:47`
- `tests/run_agent/test_strip_reasoning_tags_cli.py:53`
- `tests/run_agent/test_strip_reasoning_tags_cli.py:60`
- `tests/run_agent/test_strip_reasoning_tags_cli.py:66`
- `tests/run_agent/test_strip_reasoning_tags_cli.py:69`
**Confidence**: 80%

### 112. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_terminal_compound_background.py: L153: """Running the rewriter twice should be a no-op on its own output."""
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/tools/test_terminal_compound_background.py:153`
**Confidence**: 80%

### 113. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in test_render.py: L26: mod.format_response.return_value = "<b>hi</b>"; L34: mod.format_response.side_effect = [TypeError, "fallback"]; L42: mod.format_response.side_effect = RuntimeError
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tests/tui_gateway/test_render.py:26`
- `tests/tui_gateway/test_render.py:34`
- `tests/tui_gateway/test_render.py:42`
**Confidence**: 80%

### 114. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in browser_tool.py: L945: "description": "Take a screenshot of the current page and analyze it with vision AI. Use this when y
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tools/browser_tool.py:945`
**Confidence**: 60%

### 115. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in code_execution_tool.py: L283: # Clean up response file
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tools/code_execution_tool.py:283`
**Confidence**: 60%

### 116. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in managed_modal.py: L98: self._format_error("Managed Modal exec failed", response); L136: self._format_error("Managed Modal exec poll failed", status_response); L206: raise RuntimeError(self._format_error("Managed Modal create failed", response)) (+1 more)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tools/environments/managed_modal.py:98`
- `tools/environments/managed_modal.py:136`
- `tools/environments/managed_modal.py:206`
- `tools/environments/managed_modal.py:268`
**Confidence**: 80%

### 117. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in modal.py: L330: # Stream payload through stdin in chunks to stay under the
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tools/environments/modal.py:330`
**Confidence**: 60%

### 118. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in mixture_of_agents_tool.py: L82: AGGREGATOR_SYSTEM_PROMPT = """You have been provided with a set of responses from various open-sourc
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tools/mixture_of_agents_tool.py:82`
**Confidence**: 60%

### 119. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in skills_tool.py: L489: return [str(t).strip() for t in tags_value if t]; L496: return [t.strip().strip("\"'") for t in tags_value.split(",") if t.strip()]
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tools/skills_tool.py:489`
- `tools/skills_tool.py:496`
**Confidence**: 60%

### 120. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in tts_tool.py: L382: response_format=response_format,; L583: response_format=response_format,
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tools/tts_tool.py:382`
- `tools/tts_tool.py:583`
**Confidence**: 60%

### 121. 🟢 [LOW] Output mutation / response transformation detected

**Symptom**: Response mutation in render.py: L12: from agent.rich_output import format_response; L17: return format_response(text, cols=cols); L19: return format_response(text)
**User Impact**: Post-processing of LLM output can silently alter, censor, or inject content into responses, changing what the user sees vs. what the model produced.
**Source Layer**: output_pipeline
**Mechanism**: Regex match for output mutation/transformation patterns.
**Root Cause**: LLM responses are modified after generation but before delivery to user.
**Recommended Fix**: For personal development, small output shaping layers are often acceptable. If responses become user-facing or safety-sensitive, log the raw and transformed outputs explicitly.
**Evidence**:
- `tui_gateway/render.py:12`
- `tui_gateway/render.py:17`
- `tui_gateway/render.py:19`
**Confidence**: 80%

### 122. 🟢 [LOW] Unsafe code execution: compile(

**Symptom**: Found compile( at test_code_execution.py:458: compile(src, "hermes_tools.py", "exec")
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: compile(
**Root Cause**: Use of compile( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tests/tools/test_code_execution.py:458`
**Confidence**: 65%

### 123. 🟢 [LOW] Unsafe code execution: compile(

**Symptom**: Found compile( at skills_guard.py:303: "Python compile() with exec mode"),
**User Impact**: Arbitrary code execution from untrusted input can lead to full system compromise, data exfiltration, or remote code execution.
**Source Layer**: code_execution
**Mechanism**: Regex match for dangerous function: compile(
**Root Cause**: Use of compile( without proper input sanitization or sandboxing.
**Recommended Fix**: Do not feed untrusted input into exec/eval/shell execution. For personal or local prototyping, you can keep controlled execution paths when the input is trusted and the blast radius is small, but prefer safer parsers such as ast.literal_eval or json.loads when they fit the job.
**Evidence**:
- `tools/skills_guard.py:303`
**Confidence**: 65%

## Ordered Fix Plan

1. **Hardcoded secret or API key detected** — CRITICAL findings should be handled before lower-severity work.
2. **Internal orchestration sprawl detected** — HIGH findings should be handled before lower-severity work.
3. **Completion closure gap detected** — HIGH findings should be handled before lower-severity work.
4. **Memory freshness / generation confusion detected** — HIGH findings should be handled before lower-severity work.
5. **Role-play handoff orchestration detected** — HIGH findings should be handled before lower-severity work.
6. **Startup surface sprawl detected** — HIGH findings should be handled before lower-severity work.
7. **Runtime surface sprawl detected** — HIGH findings should be handled before lower-severity work.
8. **LLM CLI worker contract incomplete** — MEDIUM findings should be handled before lower-severity work.
9. **Duplicated skill / SOP artifacts detected** — MEDIUM findings should be handled before lower-severity work.
10. **Hidden or secondary LLM call detected** — MEDIUM findings should be handled before lower-severity work.
11. **Hidden or secondary LLM call detected** — MEDIUM findings should be handled before lower-severity work.
12. **Hidden or secondary LLM call detected** — MEDIUM findings should be handled before lower-severity work.
13. **Hidden or secondary LLM call detected** — MEDIUM findings should be handled before lower-severity work.
14. **Hidden or secondary LLM call detected** — MEDIUM findings should be handled before lower-severity work.
15. **Hidden or secondary LLM call detected** — MEDIUM findings should be handled before lower-severity work.
16. **Hidden or secondary LLM call detected** — MEDIUM findings should be handled before lower-severity work.
17. **Hidden or secondary LLM call detected** — MEDIUM findings should be handled before lower-severity work.
18. **Hidden or secondary LLM call detected** — MEDIUM findings should be handled before lower-severity work.
19. **Hidden or secondary LLM call detected** — MEDIUM findings should be handled before lower-severity work.
20. **Unsafe code execution: eval(** — MEDIUM findings should be handled before lower-severity work.
21. **Unsafe code execution: eval(** — MEDIUM findings should be handled before lower-severity work.
22. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
23. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
24. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
25. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
26. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
27. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
28. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
29. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
30. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
31. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
32. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
33. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
34. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
35. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
36. **Unsafe code execution: eval(** — MEDIUM findings should be handled before lower-severity work.
37. **Unsafe code execution: eval(** — MEDIUM findings should be handled before lower-severity work.
38. **Unsafe code execution: os.system(** — MEDIUM findings should be handled before lower-severity work.
39. **Unsafe code execution: os.system(** — MEDIUM findings should be handled before lower-severity work.
40. **Unsafe code execution: subprocess(shell=True)** — MEDIUM findings should be handled before lower-severity work.
41. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
42. **Unsafe code execution: subprocess(shell=True)** — MEDIUM findings should be handled before lower-severity work.
43. **Unsafe code execution: subprocess(shell=True)** — MEDIUM findings should be handled before lower-severity work.
44. **Unsafe code execution: subprocess(shell=True)** — MEDIUM findings should be handled before lower-severity work.
45. **Unsafe code execution: subprocess(shell=True)** — MEDIUM findings should be handled before lower-severity work.
46. **Unsafe code execution: subprocess(shell=True)** — MEDIUM findings should be handled before lower-severity work.
47. **Unsafe code execution: eval(** — MEDIUM findings should be handled before lower-severity work.
48. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
49. **Unsafe code execution: subprocess(shell=True)** — MEDIUM findings should be handled before lower-severity work.
50. **Unsafe code execution: eval(** — MEDIUM findings should be handled before lower-severity work.
51. **Unsafe code execution: exec(** — MEDIUM findings should be handled before lower-severity work.
52. **Unsafe code execution: os.system(** — MEDIUM findings should be handled before lower-severity work.
53. **Unsafe code execution: subprocess(shell=True)** — MEDIUM findings should be handled before lower-severity work.
54. **Memory growth without apparent limit** — LOW findings should be handled before lower-severity work.
55. **Memory growth without apparent limit** — LOW findings should be handled before lower-severity work.
56. **Memory growth without apparent limit** — LOW findings should be handled before lower-severity work.
57. **Memory growth without apparent limit** — LOW findings should be handled before lower-severity work.
58. **Memory growth without apparent limit** — LOW findings should be handled before lower-severity work.
59. **Memory growth without apparent limit** — LOW findings should be handled before lower-severity work.
60. **Memory growth without apparent limit** — LOW findings should be handled before lower-severity work.
61. **Memory growth without apparent limit** — LOW findings should be handled before lower-severity work.
62. **Memory growth without apparent limit** — LOW findings should be handled before lower-severity work.
63. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
64. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
65. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
66. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
67. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
68. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
69. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
70. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
71. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
72. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
73. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
74. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
75. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
76. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
77. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
78. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
79. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
80. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
81. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
82. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
83. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
84. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
85. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
86. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
87. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
88. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
89. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
90. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
91. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
92. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
93. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
94. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
95. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
96. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
97. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
98. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
99. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
100. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
101. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
102. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
103. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
104. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
105. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
106. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
107. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
108. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
109. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
110. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
111. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
112. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
113. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
114. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
115. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
116. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
117. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
118. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
119. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
120. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
121. **Output mutation / response transformation detected** — LOW findings should be handled before lower-severity work.
122. **Unsafe code execution: compile(** — LOW findings should be handled before lower-severity work.
123. **Unsafe code execution: compile(** — LOW findings should be handled before lower-severity work.
