---
name: hermes-agent
description: Hermes Agent 完整使用和扩展指南 — CLI 用法、设置、配置、生成额外代理、网关平台、skills、语音、工具、配置文件和贡献者参考。帮助用户配置 Hermes、排查问题、生成代理实例或进行代码贡献时加载此 skill。
version: 2.1.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic** — swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

## 参考资料

- 官方文档: https://hermes-agent.nousresearch.com/docs
- GitHub: https://github.com/nousresearch/hermes-agent
- `references/desktop-pet-implementation.md` - 桌面宠物系统实现笔记（线程安全、单例模式、PIL动画生成）
- `references/hook-conflict-resolution.md` - Hook 冲突解决实录（时间感知合并、Token 优化、优先级配置）
- `references/skill-authoring-best-practices.md` - 14 个 Skill 编写模式实践要点（触发检查、Token 经济、指令校准）
## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes login [--provider P] OAuth login (nous, openai-codex)
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks. Open WebUI connects via the API Server adapter.

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### Sessions

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

### Cron Jobs

```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### Credential Pools

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

## Slash Commands (In-Session)

Type these during an interactive chat session.

### Session Control
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/resume [name]       Resume a named session
```

### Configuration
```
/config              Show config (CLI)
/model [name]        Show or change model
/provider            Show provider info
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### Tools & Skills
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/cron                Manage cron jobs (CLI)
/reload-mcp          Reload MCP servers
/plugins             List plugins (CLI)
```

### Gateway
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes to latest (gateway)
/platforms (/gateway) Show platform connection status (gateway)
```

### Utility
```
/branch (/fork)      Branch the current session
/btw                 Ephemeral side question (doesn't interrupt main task)
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
```

### Info
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/status              Session info (gateway)
/profile             Active profile info
```

### Exit
```
/quit (/exit, /q)    Exit CLI
```

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
~/.hermes/skills/           Installed skills
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout.

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `smart_model_routing` | `enabled`, `cheap_model` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes login --provider nous` |
| OpenAI Codex | OAuth | `hermes login --provider openai-codex` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` in config.yaml |
| GitHub Copilot ACP | External | `COPILOT_CLI_PATH` or Copilot CLI |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `search` | Web search only (subset of `web`) |
| `todo` | In-session task planning and tracking |
| `rl` | Reinforcement learning tools (off by default) |
| `moa` | Mixture of Agents (off by default) |
| `homeassistant` | Smart home control (off by default) |

Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed.

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — set `MISTRAL_API_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

Voice commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry

---

## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes login` — re-authenticate OAuth providers
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows HTTP 400 "No models provided"**: Config file encoding issue (BOM). Ensure `config.yaml` is saved as UTF-8 without BOM.
- **WeChat/Weixin not connecting**: Check `enabled: true` in platform config and verify `WEIXIN_HOME_CHANNEL` has no `@im.wechat` suffix.
- **Cron job running at wrong time**: A股交易时间需排除午休时段 `11:30-13:00`。使用 `*/5 9-11,13-15 * * 1-5` 而非 `*/5 9-15 * * 1-5`。

### Monitoring script pitfalls

**Token 监控脚本误判导致 Gateway 重启**

**问题**：火山引擎等 API 返回 400 状态码时，监控脚本误判为 Token 失效，触发 Gateway 重启，导致服务中断。

**根因**：监控脚本只区分 200 和非 200，没有区分：
- **400 Bad Request**：请求参数问题（非 Token 问题）
- **401/403 Unauthorized**：真正的认证/权限问题

**正确逻辑**：
```python
if response.status_code == 200:
    return True, "Token 有效"
elif response.status_code in [401, 403]:
    return False, "Token 失效"
elif response.status_code == 400:
    # 400 通常是请求参数问题，检查响应内容
    try:
        resp_json = response.json()
        error_msg = resp_json.get('error', {}).get('message', '')
        if 'auth' in error_msg.lower() or 'token' in error_msg.lower():
            return False, f"认证问题: {error_msg}"
    except:
        pass
    # 400 但不是认证问题，Token 仍然有效
    return True, "Token 有效 (状态码 400 可能是请求参数问题)"
else:
    # 其他状态码不触发重启
    return True, f"状态码 {response.status_code} (不触发重启)"
```

**错误日志过滤**：
- ❌ 不要因为飞书权限问题、连接超时等非关键错误触发重启
- ✅ 只关注真正的认证错误：`InvalidToken`、`401`、`403`、`PermissionDenied`
- 忽略模式：`Failed to get chat info`、`RemoteProtocolError`、`TimedOut`

**推荐监控脚本**：
- Token 监控：`~/.hermes/scripts/monitor-token-status.py`（每天凌晨 3:25）
- Gateway 进程守护：`~/.hermes/scripts/gateway-watchdog.py`（每 5 分钟）

**Crontab 配置示例**：
```bash
# Gateway 进程守护 - 每 5 分钟检查
*/5 * * * * ~/.hermes/hermes-agent/venv/bin/python3 ~/.hermes/scripts/gateway-watchdog.py >> ~/.hermes/logs/gateway-watchdog.log 2>&1

# Token 监控 - 每天凌晨 3:25
25 3 * * * ~/.hermes/hermes-agent/venv/bin/python3 ~/.hermes/scripts/monitor-token-status.py >> ~/.hermes/logs/token-monitor.log 2>&1
```

### Common config warnings

#### "unknown config keys ignored"
```
WARNING hermes_cli.config
providers.openrouter: unknown config keys ignored: extra, priority, slug, type
```

**Cause**: Provider configuration contains fields no longer supported in current Hermes version.

**Supported fields** (check `_KNOWN_KEYS` in `hermes_cli/config.py`):
- `name`, `api`, `url`, `base_url`, `api_key`, `key_env`
- `api_mode`, `transport`, `model`, `default_model`, `models`
- `context_length`, `rate_limit_delay`

**Unsupported fields** (remove these):
- `extra` — timeout/retry settings moved to top-level config
- `priority` — no longer used
- `slug` — redundant with `name`
- `type` — auto-detected from `base_url`
- `available_models` — renamed to `models`

**Fix**:
```yaml
# ❌ Before (old format)
providers:
  openrouter:
    api_key: ${OPENROUTER_API_KEY}
    base_url: https://openrouter.ai/api/v1
    default_model: openrouter/free
    extra:
      max_retries: 3
      timeout: 600
    name: openrouter
    priority: 10
    slug: openrouter
    type: openai

# ✅ After (current format)
providers:
  openrouter:
    api_key: ${OPENROUTER_API_KEY}
    base_url: https://openrouter.ai/api/v1
    default_model: openrouter/free
    name: openrouter
```

#### API Server "No API key configured" warning
```
WARNING gateway.platforms.api_server
[Api_Server] ⚠️ No API key configured (API_SERVER_KEY / platforms.api_server.key).
```

**Cause**: API key configured at wrong nesting level.

**Wrong** (key at top level):
```yaml
platforms:
  api_server:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8642
    key: "your-api-key"  # ❌ Wrong location
```

**Correct** (key inside extra):
```yaml
platforms:
  api_server:
    enabled: true
    extra:
      host: 127.0.0.1
      key: "your-api-key"  # ✅ Correct location
      port: 8642
```

**Verification**:
```bash
# Without auth - should fail
curl http://127.0.0.1:8642/v1/models
# {"error": {"message": "Invalid API key"}}

# With auth - should succeed
curl -H "Authorization: Bearer your-api-key" http://127.0.0.1:8642/v1/models
# {"object": "list", "data": [...]}
```

**Root cause**: API server reads key from `extra.get("key", ...)` (line 575 in `gateway/platforms/api_server.py`), not from top-level `platforms.api_server.key`.

#### Platform not connecting or missing enabled flag

**Symptom**: Platform shows in `send_message list` but doesn't actually connect, or push notifications fail.

**Cause**: Missing `enabled: true` in platform configuration.

**Example** (WeChat):
```yaml
# ❌ Before - missing enabled flag
platforms:
  weixin:
    extra:
      send_chunk_delay_seconds: "0.8"
      send_chunk_retries: "3"

# ✅ After - explicitly enabled
platforms:
  weixin:
    enabled: true  # ← Add this
    extra:
      send_chunk_delay_seconds: "0.8"
      send_chunk_retries: "3"
```

**Check platform connection**:
```bash
tail -100 ~/.hermes/logs/gateway.log | grep -i "weixin\|wecom\|telegram"
```

#### HOME_CHANNEL format errors

**Symptom**: "No home channel set" error even though config has `WEIXIN_HOME_CHANNEL` set.

**Cause**: Channel ID includes platform-specific suffix.

**Wrong**:
```yaml
WEIXIN_HOME_CHANNEL: o9cq80znDxnUb_ojFoc-8kBCdqdE@im.wechat  # ❌ Has suffix
```

**Correct**:
```yaml
WEIXIN_HOME_CHANNEL: o9cq80znDxnUb_ojFoc-8kBCdqdE  # ✅ User ID only
```

The `@im.wechat` suffix is added internally by the platform adapter — don't include it in the config.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

---

## Where to Find Things

| Looking for... | Location |
|----------------|----------|
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session or [Slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` or [CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Session files | `~/.hermes/sessions/` or `hermes sessions browse` |
| Source code | `~/.hermes/hermes-agent/` |

---

## Contributor Quick Reference

For occasional contributors and PR authors. Full developer docs: https://hermes-agent.nousresearch.com/docs/developer-guide/

### Project Layout

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

Config: `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys).

### Adding a Tool (3 files)

**1. Create `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. Add import** in `model_tools.py` → `_discover_tools()` list.

**3. Add to `toolsets.py`** → `_HERMES_CORE_TOOLS` list.

All handlers must return JSON strings. Use `get_hermes_home()` for paths, never hardcode `~/.hermes`.

### Adding a Slash Command

1. Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`
2. Add handler in `cli.py` → `process_command()`
3. (Optional) Add gateway handler in `gateway/run.py`

All consumers (help text, autocomplete, Telegram menu, Slack mapping) derive from the central registry automatically.

### Agent Loop (High Level)

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### Testing

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- Tests auto-redirect `HERMES_HOME` to temp dirs — never touch real `~/.hermes/`
- Run full suite before pushing any change
- Use `-o 'addopts='` to clear any baked-in pytest flags

### Commit Conventions

```
type: concise subject line

Optional body.
```

Types: `fix:`, `feat:`, `refactor:`, `docs:`, `chore:`

### Key Rules

- **Never break prompt caching** — don't change context, tools, or system prompt mid-conversation
- **Message role alternation** — never two assistant or two user messages in a row
- Use `get_hermes_home()` from `hermes_constants` for all paths (profile-safe)
- Config values go in `config.yaml`, secrets go in `.env`
- New tools need a `check_fn` so they only appear when requirements are met

---

## Safety & Security Checklist

### Dangerous Operations (Require Confirmation)

These operations trigger approval prompts unless `--yolo` is set:

| Operation | Risk Level | Impact |
|-----------|------------|--------|
| `rm -rf` / `rmdir` | 🔴 Critical | Irreversible file deletion |
| `git push --force` | 🔴 Critical | History rewrite, data loss |
| `DROP TABLE` / `TRUNCATE` | 🔴 Critical | Database data loss |
| `sudo` commands | 🟠 High | System-level changes |
| `chmod 777` | 🟠 High | Security exposure |
| `curl | bash` | 🟠 High | Arbitrary code execution |
| `pip install` from git | 🟡 Medium | Unverified code |
| Environment variable changes | 🟡 Medium | May break auth |

### Pre-Operation Verification Checklist

Before executing potentially destructive operations:

```
□ Verify current working directory (avoid accidental deletion)
□ Check git status (uncommitted changes warning)
□ Confirm target paths exist
□ Validate user intent with explicit confirmation
□ Create checkpoint if filesystem changes expected (/rollback available)
```

### Security Best Practices

1. **Never hardcode API keys** in code or skills — use `.env` or `hermes auth add`
2. **Use credential pools** for API key rotation — `hermes auth list` to check status
3. **Review webhook endpoints** before exposing — `hermes webhook list`
4. **Audit cron jobs** regularly — `hermes cron list` to check for suspicious tasks
5. **Check gateway pairing** — `hermes pairing list` to see authorized DM sources

---

## Checkpoints & Rollback

### Creating Checkpoints

```bash
# Enable checkpoints globally
hermes config set checkpoints.enabled true

# Or per-session (CLI)
/hermes chat --checkpoints

# Checkpoint triggers automatically before:
# - File modifications via patch tool
# - Git operations (commit, push, merge)
# - Package installations
```

### Rollback Procedure

```
1. /rollback           # List available checkpoints
2. /rollback 2         # Rollback to checkpoint 2 (most recent is 1)
3. Verify changes: git status, file comparison
4. If wrong: /rollback 1 to undo the rollback
```

### Checkpoint Limits

- Default: 50 snapshots (`checkpoints.max_snapshots`)
- Older checkpoints auto-purged
- Each checkpoint ~1-5MB depending on changes
- Location: `~/.hermes/checkpoints/`

---

## Boundary Conditions & Limits

### Token Limits

| Scenario | Limit | Behavior |
|----------|-------|----------|
| Context window | Model-specific (4K-200K) | Auto-compression at 50% threshold |
| Single response | Provider-specific | Truncation or error |
| Tool output | ~10K chars per result | Truncated with warning |
| Session history | Configurable | Old messages compressed |

### Rate Limits

```yaml
# In config.yaml - rate limit handling
model:
  rate_limit_delay: 1.0  # Seconds between requests
  max_retries: 3         # Retry attempts on 429
```

### Concurrency Limits

| Resource | Limit | Configuration |
|----------|-------|---------------|
| Background processes | 10 per session | Hard limit |
| Parallel tool calls | 5 per turn | Provider-specific |
| MCP connections | 20 | Hard limit |
| Gateway platforms | 15 active | Recommended max |

### Recovery from Limit Errors

```
1. Token limit hit → Context compression triggers automatically
2. Rate limit (429) → Auto-retry with exponential backoff
3. Connection timeout → Check network, increase timeout in config
4. Memory exhausted → Restart gateway, check for memory leaks
```

---

## Exception Handling Guide

### Common Exceptions & Recovery

| Exception | Cause | Recovery |
|-----------|-------|----------|
| `ContextLengthExceeded` | Token limit | `/compress` or `/reset` |
| `AuthenticationError` | Invalid/expired key | `hermes login` or check `.env` |
| `RateLimitError` | Too many requests | Wait or use credential pool |
| `ToolExecutionError` | Tool precondition failed | Check requirements, fix params |
| `SessionNotFoundError` | Session ID invalid | `hermes sessions list` to find valid ID |
| `ProviderUnavailable` | Provider down | Switch provider: `/model` |
| `GatewayDisconnected` | Platform connection lost | `/restart` gateway |
| `CheckpointCorrupted` | Disk issue | Delete corrupted checkpoint, recreate |

### Error Code Reference

```
E001: API key missing or invalid
E002: Model not available in current provider
E003: Tool not enabled for platform
E004: Session store corrupted
E005: Gateway authentication failed
E006: File permission denied
E007: Network timeout
E008: Context length exceeded
E009: Invalid configuration
E010: MCP server connection failed
```

### Graceful Degradation

When primary features fail, fallback options:

| Primary | Fallback | Action |
|---------|----------|--------|
| Primary provider | Secondary in pool | Auto-switch |
| Memory backend | Built-in SQLite | Auto-fallback |
| Browser automation | Simple HTTP fetch | Manual switch |
| TTS service | Text-only response | Auto-silent |
| STT service | Text input only | Manual type |

---

## Debugging & Observability

### Debug Mode

```bash
# Enable verbose logging
hermes chat -v                          # CLI verbose mode
hermes config set display.verbose true  # Persistent

# Check logs
tail -f ~/.hermes/logs/gateway.log      # Gateway activity
tail -f ~/.hermes/logs/error.log        # Errors only

# Log levels: DEBUG, INFO, WARNING, ERROR
hermes config set logging.level DEBUG
```

### Health Check Commands

```bash
hermes doctor                    # Full diagnostic
hermes status --all              # All components
hermes gateway status            # Gateway health
hermes mcp list                  # MCP server status
hermes tools list                # Tool availability
hermes auth list                 # Credential status
```

### Performance Monitoring

```bash
hermes insights --days 7         # Usage analytics
/usage                           # Token usage in session
hermes sessions stats            # Session storage stats
```

### Debug Checklist

When something doesn't work:

```
□ hermes doctor --fix           # Auto-fix common issues
□ Check logs: ~/.hermes/logs/
□ Verify config: hermes config check
□ Test provider: hermes model → test connection
□ Check toolset: hermes tools list
□ Try /reset or restart gateway
□ Search issues: github.com/NousResearch/hermes-agent/issues
```

---

## Version Compatibility

### Breaking Changes by Version

| Version | Breaking Change | Migration |
|---------|-----------------|-----------|
| 2.0.0 | Provider config structure changed | `hermes config migrate` |
| 2.0.0 | Session store format updated | Auto-migration on first run |
| 1.5.0 | Tool names standardized | Update custom skills |

### Compatibility Matrix

| Feature | Min Version | Recommended |
|---------|-------------|-------------|
| MCP servers | 1.8.0 | 2.0.0+ |
| Credential pools | 1.9.0 | 2.0.0+ |
| Checkpoints | 1.10.0 | 2.0.0+ |
| Delegation tool | 2.0.0 | 2.0.0+ |

### Update Procedure

```bash
hermes update                   # Update to latest
hermes config migrate           # Migrate config if needed
hermes doctor --fix             # Fix any issues
hermes skills update            # Update installed skills
```

---

## Operation Verification Checkpoints

### Post-Setup Verification

After `hermes setup`:

```
□ hermes doctor passes
□ hermes config check shows no warnings
□ Test chat: hermes chat -q "Hello"
□ Tools available: hermes tools list
```

### Post-Gateway Start Verification

After `hermes gateway start`:

```
□ hermes gateway status shows "running"
□ Check logs: tail -20 ~/.hermes/logs/gateway.log
□ Test from platform: send a message
□ /platforms in gateway shows connected
```

### Post-Skill-Install Verification

After `hermes skills install <id>`:

```
□ hermes skills list shows new skill
□ /skill <name> loads successfully
□ Skill content visible in session
□ No import errors in logs
```

### Post-Config-Change Verification

After editing config.yaml:

```
□ hermes config check passes
□ No "unknown config keys" warnings
□ Restart CLI/gateway to apply
□ Test affected feature works
```

---

## ✅ Done When 完成判据

> **核心思想**：从"我猜我做完了"变成"我能确认我做完了"

### 四大支柱

| 支柱 | 说明 | 本 Skill 对应 |
|------|------|--------------|
| **Goal** | 任务目标 | 成功配置/使用 Hermes Agent 并验证功能正常 |
| **Context** | 上下文来源 | 用户需求 + 当前环境状态 |
| **Constraints** | 约束条件 | 配置文件结构、API 密钥、系统依赖 |
| **Done When** | 完成判据 | 下方必检项 |

### 必检项（全部满足才算完成）

#### 【任务：Hermes 安装与配置】

- [ ] **安装成功验证**
  - `hermes --version` 返回版本号
  - `hermes doctor` 通过所有检查
  - 配置文件已创建（`~/.hermes/config.yaml`）
  - **验证方法**：`hermes doctor` 无错误输出

- [ ] **模型配置正确**
  - Provider 已配置（`hermes model` 显示）
  - API 密钥已设置（`.env` 文件或 `hermes auth`）
  - 测试连接成功（发送测试消息）
  - **验证方法**：`hermes chat -q "Hello"` 返回正常响应

- [ ] **工具集启用正确**
  - 必要工具已启用（`hermes tools list`）
  - 工具依赖已满足（如 browser 需要 browserbase token）
  - **验证方法**：`hermes tools` 显示工具状态为 enabled

#### 【任务：Gateway 平台配置】

- [ ] **Gateway 启动成功**
  - `hermes gateway status` 显示 running
  - 日志无错误（`tail -20 ~/.hermes/logs/gateway.log`）
  - 进程持久化（systemd/launchd）
  - **验证方法**：`hermes gateway status` 返回 "running"

- [ ] **平台连接成功**
  - 平台配置正确（`~/.hermes/config.yaml` 的 platforms 部分）
  - `enabled: true` 已设置
  - Home channel 已设置（如需要）
  - `/platforms` 显示已连接
  - **验证方法**：从平台发送测试消息，Hermes 正常响应

- [ ] **Webhook/配对已配置**
  - Webhook 路由已创建（`hermes webhook list`）
  - DM 配对已授权（`hermes pairing list`）
  - **验证方法**：测试 webhook 或 DM 消息到达

#### 【任务：Skill 安装与使用】

- [ ] **Skill 安装成功**
  - `hermes skills list` 显示新 Skill
  - Skill 文件已下载到 `~/.hermes/skills/`
  - 无导入错误（日志检查）
  - **验证方法**：`hermes skills list` 包含目标 Skill

- [ ] **Skill 可加载**
  - `/skill <name>` 成功加载
  - Skill 内容在会话中可见
  - 功能可用（如有特定功能）
  - **验证方法**：`/skill <name>` 无错误输出

#### 【任务：Cron Job 配置】

- [ ] **Cron Job 创建成功**
  - `hermes cron list` 显示新 Job
  - Schedule 格式正确（cron 表达式或简写）
  - Prompt 已设置
  - Delivery 目标已配置
  - **验证方法**：`hermes cron list` 显示目标 Job

- [ ] **Cron Job 运行正常**
  - 等待触发时间到达
  - 检查执行日志（`~/.hermes/logs/cron.log`）
  - 结果已送达目标平台
  - **验证方法**：目标平台收到消息

#### 【任务：问题排查】

- [ ] **问题已诊断**
  - `hermes doctor` 已运行
  - 日志已检查（`~/.hermes/logs/`）
  - 配置已验证（`hermes config check`）
  - 根因已识别
  - **验证方法**：输出包含问题诊断结果

- [ ] **修复已验证**
  - 修复措施已执行
  - `hermes doctor --fix` 通过
  - 功能恢复正常
  - **验证方法**：原问题不再出现

### 可选项（加分项）

- [ ] **性能优化完成**
  - Token 使用优化（`hermes insights`）
  - 响应时间优化
  - 内存使用优化
  - **验证方法**：`hermes insights --days 7` 显示改善

- [ ] **多 Provider 配置完成**
  - Credential pool 已配置（`hermes auth list`）
  - Fallback provider 已设置
  - 自动切换测试通过
  - **验证方法**：禁用主 provider，自动切换到备选

- [ ] **Profile 配置完成**
  - 多个 Profile 已创建（`hermes profile list`）
  - 独立配置已隔离
  - Profile 切换正常
  - **验证方法**：`hermes profile use <name>` 切换成功

### 失败处理

| 失败场景 | 处理路径 | 用户提示 |
|---------|---------|---------|
| 安装失败 | 检查依赖 + 重试 | ❌ 安装失败，请检查依赖：Python 3.8+, pip |
| API 密钥无效 | 重新配置 | ⚠️ API 密钥无效，请运行 `hermes login` 或检查 `.env` |
| Gateway 启动失败 | 检查日志 + 端口冲突 | ⚠️ Gateway 启动失败，检查日志：`tail -20 ~/.hermes/logs/gateway.log` |
| 平台连接失败 | 检查配置 + 重新授权 | ⚠️ 平台连接失败，请检查 `platforms` 配置或重新授权 |
| Skill 加载失败 | 检查依赖 + 重新安装 | ⚠️ Skill 加载失败，请检查依赖或重新安装 |

### 自检代码示例

```python
def verify_done_when(task_type):
    """验证 Done When 是否满足"""
    
    if task_type == 'setup':
        # 检查安装
        assert subprocess.run(['hermes', '--version']).returncode == 0
        
        # 检查 doctor
        result = subprocess.run(['hermes', 'doctor'], capture_output=True)
        assert result.returncode == 0
        
        # 检查配置文件
        assert os.path.exists(os.path.expanduser('~/.hermes/config.yaml'))
    
    elif task_type == 'gateway':
        # 检查 gateway 状态
        result = subprocess.run(['hermes', 'gateway', 'status'], capture_output=True)
        assert 'running' in result.stdout.decode()
        
        # 检查日志无错误
        log_file = os.path.expanduser('~/.hermes/logs/gateway.log')
        with open(log_file, 'r') as f:
            recent_logs = f.readlines()[-50:]
            assert not any('ERROR' in line for line in recent_logs)
    
    elif task_type == 'skill':
        # 检查 skill 列表
        result = subprocess.run(['hermes', 'skills', 'list'], capture_output=True)
        assert skill_name in result.stdout.decode()
        
        # 检查 skill 文件
        skill_path = os.path.expanduser(f'~/.hermes/skills/{skill_name}/SKILL.md')
        assert os.path.exists(skill_path)
    
    elif task_type == 'cron':
        # 检查 cron 列表
        result = subprocess.run(['hermes', 'cron', 'list'], capture_output=True)
        assert job_id in result.stdout.decode()
        
        # 检查下次运行时间
        assert 'next run' in result.stdout.decode().lower()
    
    return True  # 所有检查通过
```
