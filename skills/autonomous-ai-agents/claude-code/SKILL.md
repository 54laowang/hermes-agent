---
name: claude-code
description: |
  将编码任务委派给 Claude Code（Anthropic 的 CLI 代理）。用于构建功能、重构、PR 审查和迭代编码。需要安装 claude CLI。
  
  Use when: claude code, 编码任务, coding task, 代码审查, code review, 重构, refactoring, PR审查, Claude CLI.
  
  Do NOT use for:
  - Hermes 配置问题（用 hermes-agent skill）
  - Codex/OpenCode 任务（用 codex/opencode skills）
  - 非编码任务（用相应 skills）
  - 批量文件操作（用 file/terminal 工具）
version: 2.3.0
author: Hermes Agent + Teknium
license: MIT
keywords:
  - claude code
  - 编码任务
  - coding task
  - 代码审查
  - code review
  - 重构
  - refactoring
  - Claude CLI
triggers:
  - claude code
  - 编码任务
  - coding task
  - 代码审查
  - code review
  - 重构
  - refactoring
  - PR审查
metadata:
  hermes:
    tags: [Coding-Agent, Claude, Anthropic, Code-Review, Refactoring, PTY, Automation]
    related_skills: [codex, hermes-agent, opencode]
---

# Claude Code — Hermes Orchestration Guide

Delegate coding tasks to [Claude Code](https://code.claude.com/docs/en/cli-reference) (Anthropic's autonomous coding agent CLI) via the Hermes terminal. Claude Code v2.x can read files, write code, run shell commands, spawn subagents, and manage git workflows autonomously.

## Prerequisites

- **Install:** `npm install -g @anthropic-ai/claude-code`
- **Auth:** run `claude` once to log in (browser OAuth for Pro/Max, or set `ANTHROPIC_API_KEY`)
- **Console auth:** `claude auth login --console` for API key billing
- **SSO auth:** `claude auth login --sso` for Enterprise
- **Check status:** `claude auth status` (JSON) or `claude auth status --text` (human-readable)
- **Health check:** `claude doctor` — checks auto-updater and installation health
- **Version check:** `claude --version` (requires v2.x+)
- **Update:** `claude update` or `claude upgrade`

## Two Orchestration Modes

Hermes interacts with Claude Code in two fundamentally different ways. Choose based on the task.

### Mode 1: Print Mode (`-p`) — Non-Interactive (PREFERRED for most tasks)

Print mode runs a one-shot task, returns the result, and exits. No PTY needed. No interactive prompts. This is the cleanest integration path.

```
terminal(command="claude -p 'Add error handling to all API calls in src/' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)
```

**When to use print mode:**
- One-shot coding tasks (fix a bug, add a feature, refactor)
- CI/CD automation and scripting
- Structured data extraction with `--json-schema`
- Piped input processing (`cat file | claude -p "analyze this"`)
- Any task where you don't need multi-turn conversation

**Print mode skips ALL interactive dialogs** — no workspace trust prompt, no permission confirmations. This makes it ideal for automation.

### Mode 2: Interactive PTY via tmux — Multi-Turn Sessions

Interactive mode gives you a full conversational REPL where you can send follow-up prompts, use slash commands, and watch Claude work in real time. **Requires tmux orchestration.**

```
# Start a tmux session
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")

# Launch Claude Code inside it
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")

# Wait for startup, then send your task
# (after ~3-5 seconds for the welcome screen)
terminal(command="sleep 5 && tmux send-keys -t claude-work 'Refactor the auth module to use JWT tokens' Enter")

# Monitor progress by capturing the pane
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")

# Send follow-up tasks
terminal(command="tmux send-keys -t claude-work 'Now add unit tests for the new JWT code' Enter")

# Exit when done
terminal(command="tmux send-keys -t claude-work '/exit' Enter")
```

**When to use interactive mode:**
- Multi-turn iterative work (refactor → review → fix → test cycle)
- Tasks requiring human-in-the-loop decisions
- Exploratory coding sessions
- When you need to use Claude's slash commands (`/compact`, `/review`, `/model`)

## PTY Dialog Handling (CRITICAL for Interactive Mode)

Claude Code presents up to two confirmation dialogs on first launch. You MUST handle these via tmux send-keys:

### Dialog 1: Workspace Trust (first visit to a directory)
```
❯ 1. Yes, I trust this folder    ← DEFAULT (just press Enter)
  2. No, exit
```
**Handling:** `tmux send-keys -t <session> Enter` — default selection is correct.

### Dialog 2: Bypass Permissions Warning (only with --dangerously-skip-permissions)
```
❯ 1. No, exit                    ← DEFAULT (WRONG choice!)
  2. Yes, I accept
```
**Handling:** Must navigate DOWN first, then Enter:
```
tmux send-keys -t <session> Down && sleep 0.3 && tmux send-keys -t <session> Enter
```

### Robust Dialog Handling Pattern
```
# Launch with permissions bypass
terminal(command="tmux send-keys -t claude-work 'claude --dangerously-skip-permissions \"your task\"' Enter")

# Handle trust dialog (Enter for default "Yes")
terminal(command="sleep 4 && tmux send-keys -t claude-work Enter")

# Handle permissions dialog (Down then Enter for "Yes, I accept")
terminal(command="sleep 3 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter")

# Now wait for Claude to work
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -60")
```

**Note:** After the first trust acceptance for a directory, the trust dialog won't appear again. Only the permissions dialog recurs each time you use `--dangerously-skip-permissions`.

## CLI Subcommands

| Subcommand | Purpose |
|------------|---------|
| `claude` | Start interactive REPL |
| `claude "query"` | Start REPL with initial prompt |
| `claude -p "query"` | Print mode (non-interactive, exits when done) |
| `cat file \| claude -p "query"` | Pipe content as stdin context |
| `claude -c` | Continue the most recent conversation in this directory |
| `claude -r "id"` | Resume a specific session by ID or name |
| `claude auth login` | Sign in (add `--console` for API billing, `--sso` for Enterprise) |
| `claude auth status` | Check login status (returns JSON; `--text` for human-readable) |
| `claude mcp add <name> -- <cmd>` | Add an MCP server |
| `claude mcp list` | List configured MCP servers |
| `claude mcp remove <name>` | Remove an MCP server |
| `claude agents` | List configured agents |
| `claude doctor` | Run health checks on installation and auto-updater |
| `claude update` / `claude upgrade` | Update Claude Code to latest version |
| `claude remote-control` | Start server to control Claude from claude.ai or mobile app |
| `claude install [target]` | Install native build (stable, latest, or specific version) |
| `claude setup-token` | Set up long-lived auth token (requires subscription) |
| `claude plugin` / `claude plugins` | Manage Claude Code plugins |
| `claude auto-mode` | Inspect auto mode classifier configuration |

## Print Mode Deep Dive

### Structured JSON Output
```
terminal(command="claude -p 'Analyze auth.py for security issues' --output-format json --max-turns 5", workdir="/project", timeout=120)
```

Returns a JSON object with:
```json
{
  "type": "result",
  "subtype": "success",
  "result": "The analysis text...",
  "session_id": "75e2167f-...",
  "num_turns": 3,
  "total_cost_usd": 0.0787,
  "duration_ms": 10276,
  "stop_reason": "end_turn",
  "terminal_reason": "completed",
  "usage": { "input_tokens": 5, "output_tokens": 603, ... },
  "modelUsage": { "claude-sonnet-4-6": { "costUSD": 0.078, "contextWindow": 200000 } }
}
```

**Key fields:** `session_id` for resumption, `num_turns` for agentic loop count, `total_cost_usd` for spend tracking, `subtype` for success/error detection (`success`, `error_max_turns`, `error_budget`).

### Streaming JSON Output
For real-time token streaming, use `stream-json` with `--verbose`:
```
terminal(command="claude -p 'Write a summary' --output-format stream-json --verbose --include-partial-messages", timeout=60)
```

Returns newline-delimited JSON events. Filter with jq for live text:
```
claude -p "Explain X" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

Stream events include `system/api_retry` with `attempt`, `max_retries`, and `error` fields (e.g., `rate_limit`, `billing_error`).

### Bidirectional Streaming
For real-time input AND output streaming:
```
claude -p "task" --input-format stream-json --output-format stream-json --replay-user-messages
```
`--replay-user-messages` re-emits user messages on stdout for acknowledgment.

### Piped Input
```
# Pipe a file for analysis
terminal(command="cat src/auth.py | claude -p 'Review this code for bugs' --max-turns 1", timeout=60)

# Pipe multiple files
terminal(command="cat src/*.py | claude -p 'Find all TODO comments' --max-turns 1", timeout=60)

# Pipe command output
terminal(command="git diff HEAD~3 | claude -p 'Summarize these changes' --max-turns 1", timeout=60)
```

### JSON Schema for Structured Extraction
```
terminal(command="claude -p 'List all functions in src/' --output-format json --json-schema '{\"type\":\"object\",\"properties\":{\"functions\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}}},\"required\":[\"functions\"]}' --max-turns 5", workdir="/project", timeout=90)
```

Parse `structured_output` from the JSON result. Claude validates output against the schema before returning.

### Session Continuation
```
# Start a task
terminal(command="claude -p 'Start refactoring the database layer' --output-format json --max-turns 10 > /tmp/session.json", workdir="/project", timeout=180)

# Resume with session ID
terminal(command="claude -p 'Continue and add connection pooling' --resume $(cat /tmp/session.json | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"session_id\"])') --max-turns 5", workdir="/project", timeout=120)

# Or resume the most recent session in the same directory
terminal(command="claude -p 'What did you do last time?' --continue --max-turns 1", workdir="/project", timeout=30)

# Fork a session (new ID, keeps history)
terminal(command="claude -p 'Try a different approach' --resume <id> --fork-session --max-turns 10", workdir="/project", timeout=120)
```

### Bare Mode for CI/Scripting
```
terminal(command="claude --bare -p 'Run all tests and report failures' --allowedTools 'Read,Bash' --max-turns 10", workdir="/project", timeout=180)
```

`--bare` skips hooks, plugins, MCP discovery, and CLAUDE.md loading. Fastest startup. Requires `ANTHROPIC_API_KEY` (skips OAuth).

To selectively load context in bare mode:
| To load | Flag |
|---------|------|
| System prompt additions | `--append-system-prompt "text"` or `--append-system-prompt-file path` |
| Settings | `--settings <file-or-json>` |
| MCP servers | `--mcp-config <file-or-json>` |
| Custom agents | `--agents '<json>'` |

### Fallback Model for Overload
```
terminal(command="claude -p 'task' --fallback-model haiku --max-turns 5", timeout=90)
```
Automatically falls back to the specified model when the default is overloaded (print mode only).

## Complete CLI Flags Reference

### Session & Environment
| Flag | Effect |
|------|--------|
| `-p, --print` | Non-interactive one-shot mode (exits when done) |
| `-c, --continue` | Resume most recent conversation in current directory |
| `-r, --resume <id>` | Resume specific session by ID or name (interactive picker if no ID) |
| `--fork-session` | When resuming, create new session ID instead of reusing original |
| `--session-id <uuid>` | Use a specific UUID for the conversation |
| `--no-session-persistence` | Don't save session to disk (print mode only) |
| `--add-dir <paths...>` | Grant Claude access to additional working directories |
| `-w, --worktree [name]` | Run in an isolated git worktree at `.claude/worktrees/<name>` |
| `--tmux` | Create a tmux session for the worktree (requires `--worktree`) |
| `--ide` | Auto-connect to a valid IDE on startup |
| `--chrome` / `--no-chrome` | Enable/disable Chrome browser integration for web testing |
| `--from-pr [number]` | Resume session linked to a specific GitHub PR |
| `--file <specs...>` | File resources to download at startup (format: `file_id:relative_path`) |

### Model & Performance
| Flag | Effect |
|------|--------|
| `--model <alias>` | Model selection: `sonnet`, `opus`, `haiku`, or full name like `claude-sonnet-4-6` |
| `--effort <level>` | Reasoning depth: `low`, `medium`, `high`, `max`, `auto` | Both |
| `--max-turns <n>` | Limit agentic loops (print mode only; prevents runaway) |
| `--max-budget-usd <n>` | Cap API spend in dollars (print mode only) |
| `--fallback-model <model>` | Auto-fallback when default model is overloaded (print mode only) |
| `--betas <betas...>` | Beta headers to include in API requests (API key users only) |

### Permission & Safety
| Flag | Effect |
|------|--------|
| `--dangerously-skip-permissions` | Auto-approve ALL tool use (file writes, bash, network, etc.) |
| `--allow-dangerously-skip-permissions` | Enable bypass as an *option* without enabling it by default |
| `--permission-mode <mode>` | `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` |
| `--allowedTools <tools...>` | Whitelist specific tools (comma or space-separated) |
| `--disallowedTools <tools...>` | Blacklist specific tools |
| `--tools <tools...>` | Override built-in tool set (`""` = none, `"default"` = all, or tool names) |

### Output & Input Format
| Flag | Effect |
|------|--------|
| `--output-format <fmt>` | `text` (default), `json` (single result object), `stream-json` (newline-delimited) |
| `--input-format <fmt>` | `text` (default) or `stream-json` (real-time streaming input) |
| `--json-schema <schema>` | Force structured JSON output matching a schema |
| `--verbose` | Full turn-by-turn output |
| `--include-partial-messages` | Include partial message chunks as they arrive (stream-json + print) |
| `--replay-user-messages` | Re-emit user messages on stdout (stream-json bidirectional) |

### System Prompt & Context
| Flag | Effect |
|------|--------|
| `--append-system-prompt <text>` | **Add** to the default system prompt (preserves built-in capabilities) |
| `--append-system-prompt-file <path>` | **Add** file contents to the default system prompt |
| `--system-prompt <text>` | **Replace** the entire system prompt (use --append instead usually) |
| `--system-prompt-file <path>` | **Replace** the system prompt with file contents |
| `--bare` | Skip hooks, plugins, MCP discovery, CLAUDE.md, OAuth (fastest startup) |
| `--agents '<json>'` | Define custom subagents dynamically as JSON |
| `--mcp-config <path>` | Load MCP servers from JSON file (repeatable) |
| `--strict-mcp-config` | Only use MCP servers from `--mcp-config`, ignoring all other MCP configs |
| `--settings <file-or-json>` | Load additional settings from a JSON file or inline JSON |
| `--setting-sources <sources>` | Comma-separated sources to load: `user`, `project`, `local` |
| `--plugin-dir <paths...>` | Load plugins from directories for this session only |
| `--disable-slash-commands` | Disable all skills/slash commands |

### Debugging
| Flag | Effect |
|------|--------|
| `-d, --debug [filter]` | Enable debug logging with optional category filter (e.g., `"api,hooks"`, `"!1p,!file"`) |
| `--debug-file <path>` | Write debug logs to file (implicitly enables debug mode) |

### Agent Teams
| Flag | Effect |
|------|--------|
| `--teammate-mode <mode>` | How agent teams display: `auto`, `in-process`, or `tmux` |
| `--brief` | Enable `SendUserMessage` tool for agent-to-user communication |

### Tool Name Syntax for --allowedTools / --disallowedTools
```
Read                    # All file reading
Edit                    # File editing (existing files)
Write                   # File creation (new files)
Bash                    # All shell commands
Bash(git *)             # Only git commands
Bash(git commit *)      # Only git commit commands
Bash(npm run lint:*)    # Pattern matching with wildcards
WebSearch               # Web search capability
WebFetch                # Web page fetching
mcp__<server>__<tool>   # Specific MCP tool
```

## Settings & Configuration

### Settings Hierarchy (highest to lowest priority)
1. **CLI flags** — override everything
2. **Local project:** `.claude/settings.local.json` (personal, gitignored)
3. **Project:** `.claude/settings.json` (shared, git-tracked)
4. **User:** `~/.claude/settings.json` (global)

### Permissions in Settings
```json
{
  "permissions": {
    "allow": ["Bash(npm run lint:*)", "WebSearch", "Read"],
    "ask": ["Write(*.ts)", "Bash(git push*)"],
    "deny": ["Read(.env)", "Bash(rm -rf *)"]
  }
}
```

### Memory Files (CLAUDE.md) Hierarchy
1. **Global:** `~/.claude/CLAUDE.md` — applies to all projects
2. **Project:** `./CLAUDE.md` — project-specific context (git-tracked)
3. **Local:** `.claude/CLAUDE.local.md` — personal project overrides (gitignored)

Use the `#` prefix in interactive mode to quickly add to memory: `# Always use 2-space indentation`.

## Interactive Session: Slash Commands

### Session & Context
| Command | Purpose |
|---------|---------|
| `/help` | Show all commands (including custom and MCP commands) |
| `/compact [focus]` | Compress context to save tokens; CLAUDE.md survives compaction. E.g., `/compact focus on auth logic` |
| `/clear` | Wipe conversation history for a fresh start |
| `/context` | Visualize context usage as a colored grid with optimization tips |
| `/cost` | View token usage with per-model and cache-hit breakdowns |
| `/resume` | Switch to or resume a different session |
| `/rewind` | Revert to a previous checkpoint in conversation or code |
| `/btw <question>` | Ask a side question without adding to context cost |
| `/status` | Show version, connectivity, and session info |
| `/todos` | List tracked action items from the conversation |
| `/exit` or `Ctrl+D` | End session |

### Development & Review
| Command | Purpose |
|---------|---------|
| `/review` | Request code review of current changes |
| `/security-review` | Perform security analysis of current changes |
| `/plan [description]` | Enter Plan mode with auto-start for task planning |
| `/loop [interval]` | Schedule recurring tasks within the session |
| `/batch` | Auto-create worktrees for large parallel changes (5-30 worktrees) |

### Configuration & Tools
| Command | Purpose |
|---------|---------|
| `/model [model]` | Switch models mid-session (use arrow keys to adjust effort) |
| `/effort [level]` | Set reasoning effort: `low`, `medium`, `high`, `max`, or `auto` |
| `/init` | Create a CLAUDE.md file for project memory |
| `/memory` | Open CLAUDE.md for editing |
| `/config` | Open interactive settings configuration |
| `/permissions` | View/update tool permissions |
| `/agents` | Manage specialized subagents |
| `/mcp` | Interactive UI to manage MCP servers |
| `/add-dir` | Add additional working directories (useful for monorepos) |
| `/usage` | Show plan limits and rate limit status |
| `/voice` | Enable push-to-talk voice mode (20 languages; hold Space to record, release to send) |
| `/release-notes` | Interactive picker for version release notes |

### Custom Slash Commands
Create `.claude/commands/<name>.md` (project-shared) or `~/.claude/commands/<name>.md` (personal):

```markdown
# .claude/commands/deploy.md
Run the deploy pipeline:
1. Run all tests
2. Build the Docker image
3. Push to registry
4. Update the $ARGUMENTS environment (default: staging)
```

Usage: `/deploy production` — `$ARGUMENTS` is replaced with the user's input.

### Skills (Natural Language Invocation)
Unlike slash commands (manually invoked), skills in `.claude/skills/` are markdown guides that Claude invokes automatically via natural language when the task matches:

```markdown
# .claude/skills/database-migration.md
When asked to create or modify database migrations:
1. Use Alembic for migration generation
2. Always create a rollback function
3. Test migrations against a local database copy
```

## Interactive Session: Keyboard Shortcuts

### General Controls
| Key | Action |
|-----|--------|
| `Ctrl+C` | Cancel current input or generation |
| `Ctrl+D` | Exit session |
| `Ctrl+R` | Reverse search command history |
| `Ctrl+B` | Background a running task |
| `Ctrl+V` | Paste image into conversation |
| `Ctrl+O` | Transcript mode — see Claude's thinking process |
| `Ctrl+G` or `Ctrl+X Ctrl+E` | Open prompt in external editor |
| `Esc Esc` | Rewind conversation or code state / summarize |

### Mode Toggles
| Key | Action |
|-----|--------|
| `Shift+Tab` | Cycle permission modes (Normal → Auto-Accept → Plan) |
| `Alt+P` | Switch model |
| `Alt+T` | Toggle thinking mode |
| `Alt+O` | Toggle Fast Mode |

### Multiline Input
| Key | Action |
|-----|--------|
| `\` + `Enter` | Quick newline |
| `Shift+Enter` | Newline (alternative) |
| `Ctrl+J` | Newline (alternative) |

### Input Prefixes
| Prefix | Action |
|--------|--------|
| `!` | Execute bash directly, bypassing AI (e.g., `!npm test`). Use `!` alone to toggle shell mode. |
| `@` | Reference files/directories with autocomplete (e.g., `@./src/api/`) |
| `#` | Quick add to CLAUDE.md memory (e.g., `# Use 2-space indentation`) |
| `/` | Slash commands |

### Pro Tip: "ultrathink"
Use the keyword "ultrathink" in your prompt for maximum reasoning effort on a specific turn. This triggers the deepest thinking mode regardless of the current `/effort` setting.

## PR Review Pattern

### Quick Review (Print Mode)
```
terminal(command="cd /path/to/repo && git diff main...feature-branch | claude -p 'Review this diff for bugs, security issues, and style problems. Be thorough.' --max-turns 1", timeout=60)
```

### Deep Review (Interactive + Worktree)
```
terminal(command="tmux new-session -d -s review -x 140 -y 40")
terminal(command="tmux send-keys -t review 'cd /path/to/repo && claude -w pr-review' Enter")
terminal(command="sleep 5 && tmux send-keys -t review Enter")  # Trust dialog
terminal(command="sleep 2 && tmux send-keys -t review 'Review all changes vs main. Check for bugs, security issues, race conditions, and missing tests.' Enter")
terminal(command="sleep 30 && tmux capture-pane -t review -p -S -60")
```

### PR Review from Number
```
terminal(command="claude -p 'Review this PR thoroughly' --from-pr 42 --max-turns 10", workdir="/path/to/repo", timeout=120)
```

### Claude Worktree with tmux
```
terminal(command="claude -w feature-x --tmux", workdir="/path/to/repo")
```
Creates an isolated git worktree at `.claude/worktrees/feature-x` AND a tmux session for it. Uses iTerm2 native panes when available; add `--tmux=classic` for traditional tmux.

## Parallel Claude Instances

Run multiple independent Claude tasks simultaneously:

```
# Task 1: Fix backend
terminal(command="tmux new-session -d -s task1 -x 140 -y 40 && tmux send-keys -t task1 'cd ~/project && claude -p \"Fix the auth bug in src/auth.py\" --allowedTools \"Read,Edit\" --max-turns 10' Enter")

# Task 2: Write tests
terminal(command="tmux new-session -d -s task2 -x 140 -y 40 && tmux send-keys -t task2 'cd ~/project && claude -p \"Write integration tests for the API endpoints\" --allowedTools \"Read,Write,Bash\" --max-turns 15' Enter")

# Task 3: Update docs
terminal(command="tmux new-session -d -s task3 -x 140 -y 40 && tmux send-keys -t task3 'cd ~/project && claude -p \"Update README.md with the new API endpoints\" --allowedTools \"Read,Edit\" --max-turns 5' Enter")

# Monitor all
terminal(command="sleep 30 && for s in task1 task2 task3; do echo '=== '$s' ==='; tmux capture-pane -t $s -p -S -5 2>/dev/null; done")
```

## CLAUDE.md — Project Context File

Claude Code auto-loads `CLAUDE.md` from the project root. Use it to persist project context:

```markdown
# Project: My API

## Architecture
- FastAPI backend with SQLAlchemy ORM
- PostgreSQL database, Redis cache
- pytest for testing with 90% coverage target

## Key Commands
- `make test` — run full test suite
- `make lint` — ruff + mypy
- `make dev` — start dev server on :8000

## Code Standards
- Type hints on all public functions
- Docstrings in Google style
- 2-space indentation for YAML, 4-space for Python
- No wildcard imports
```

**Be specific.** Instead of "Write good code", use "Use 2-space indentation for JS" or "Name test files with `.test.ts` suffix." Specific instructions save correction cycles.

### Rules Directory (Modular CLAUDE.md)
For projects with many rules, use the rules directory instead of one massive CLAUDE.md:
- **Project rules:** `.claude/rules/*.md` — team-shared, git-tracked
- **User rules:** `~/.claude/rules/*.md` — personal, global

Each `.md` file in the rules directory is loaded as additional context. This is cleaner than cramming everything into a single CLAUDE.md.

### Auto-Memory
Claude automatically stores learned project context in `~/.claude/projects/<project>/memory/`.
- **Limit:** 25KB or 200 lines per project
- This is separate from CLAUDE.md — it's Claude's own notes about the project, accumulated across sessions

## Custom Subagents

Define specialized agents in `.claude/agents/` (project), `~/.claude/agents/` (personal), or via `--agents` CLI flag (session):

### Agent Location Priority
1. `.claude/agents/` — project-level, team-shared
2. `--agents` CLI flag — session-specific, dynamic
3. `~/.claude/agents/` — user-level, personal

### Creating an Agent
```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Security-focused code review
model: opus
tools: [Read, Bash]
---
You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication/authorization flaws
- Secrets in code
- Unsafe deserialization
```

Invoke via: `@security-reviewer review the auth module`

### Dynamic Agents via CLI
```
terminal(command="claude --agents '{\"reviewer\": {\"description\": \"Reviews code\", \"prompt\": \"You are a code reviewer focused on performance\"}}' -p 'Use @reviewer to check auth.py'", timeout=120)
```

Claude can orchestrate multiple agents: "Use @db-expert to optimize queries, then @security to audit the changes."

## Hooks — Automation on Events

Configure in `.claude/settings.json` (project) or `~/.claude/settings.json` (global):

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write(*.py)",
      "hooks": [{"type": "command", "command": "ruff check --fix $CLAUDE_FILE_PATHS"}]
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -q 'rm -rf'; then echo 'Blocked!' && exit 2; fi"}]
    }],
    "Stop": [{
      "hooks": [{"type": "command", "command": "echo 'Claude finished a response' >> /tmp/claude-activity.log"}]
    }]
  }
}
```

### All 8 Hook Types
| Hook | When it fires | Common use |
|------|--------------|------------|
| `UserPromptSubmit` | Before Claude processes a user prompt | Input validation, logging |
| `PreToolUse` | Before tool execution | Security gates, block dangerous commands (exit 2 = block) |
| `PostToolUse` | After a tool finishes | Auto-format code, run linters |
| `Notification` | On permission requests or input waits | Desktop notifications, alerts |
| `Stop` | When Claude finishes a response | Completion logging, status updates |
| `SubagentStop` | When a subagent completes | Agent orchestration |
| `PreCompact` | Before context memory is cleared | Backup session transcripts |
| `SessionStart` | When a session begins | Load dev context (e.g., `git status`) |

### Hook Environment Variables
| Variable | Content |
|----------|---------|
| `CLAUDE_PROJECT_DIR` | Current project path |
| `CLAUDE_FILE_PATHS` | Files being modified |
| `CLAUDE_TOOL_INPUT` | Tool parameters as JSON |

### Security Hook Examples
```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf|git push.*--force|:(){ :|:& };:'; then echo 'Dangerous command blocked!' && exit 2; fi"}]
  }]
}
```

## MCP Integration

Add external tool servers for databases, APIs, and services:

```
# GitHub integration
terminal(command="claude mcp add -s user github -- npx @modelcontextprotocol/server-github", timeout=30)

# PostgreSQL queries
terminal(command="claude mcp add -s local postgres -- npx @anthropic-ai/server-postgres --connection-string postgresql://localhost/mydb", timeout=30)

# Puppeteer for web testing
terminal(command="claude mcp add puppeteer -- npx @anthropic-ai/server-puppeteer", timeout=30)
```

### MCP Scopes
| Flag | Scope | Storage |
|------|-------|---------|
| `-s user` | Global (all projects) | `~/.claude.json` |
| `-s local` | This project (personal) | `.claude/settings.local.json` (gitignored) |
| `-s project` | This project (team-shared) | `.claude/settings.json` (git-tracked) |

### MCP in Print/CI Mode
```
terminal(command="claude --bare -p 'Query database' --mcp-config mcp-servers.json --strict-mcp-config", timeout=60)
```
`--strict-mcp-config` ignores all MCP servers except those from `--mcp-config`.

Reference MCP resources in chat: `@github:issue://123`

### MCP Limits & Tuning
- **Tool descriptions:** 2KB cap per server for tool descriptions and server instructions
- **Result size:** Default capped; use `maxResultSizeChars` annotation to allow up to **500K** characters for large outputs
- **Output tokens:** `export MAX_MCP_OUTPUT_TOKENS=50000` — cap output from MCP servers to prevent context flooding
- **Transports:** `stdio` (local process), `http` (remote), `sse` (server-sent events)

## Monitoring Interactive Sessions

### Reading the TUI Status
```
# Periodic capture to check if Claude is still working or waiting for input
terminal(command="tmux capture-pane -t dev -p -S -10")
```

Look for these indicators:
- `❯` at bottom = waiting for your input (Claude is done or asking a question)
- `●` lines = Claude is actively using tools (reading, writing, running commands)
- `⏵⏵ bypass permissions on` = status bar showing permissions mode
- `◐ medium · /effort` = current effort level in status bar
- `ctrl+o to expand` = tool output was truncated (can be expanded interactively)

### Context Window Health
Use `/context` in interactive mode to see a colored grid of context usage. Key thresholds:
- **< 70%** — Normal operation, full precision
- **70-85%** — Precision starts dropping, consider `/compact`
- **> 85%** — Hallucination risk spikes significantly, use `/compact` or `/clear`

## Environment Variables

| Variable | Effect |
|----------|--------|
| `ANTHROPIC_API_KEY` | API key for authentication (alternative to OAuth) |
| `CLAUDE_CODE_EFFORT_LEVEL` | Default effort: `low`, `medium`, `high`, `max`, or `auto` |
| `MAX_THINKING_TOKENS` | Cap thinking tokens (set to `0` to disable thinking entirely) |
| `MAX_MCP_OUTPUT_TOKENS` | Cap output from MCP servers (default varies; set e.g., `50000`) |
| `CLAUDE_CODE_NO_FLICKER=1` | Enable alt-screen rendering to eliminate terminal flicker |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | Strip credentials from sub-processes for security |

## Cost & Performance Tips

1. **Use `--max-turns`** in print mode to prevent runaway loops. Start with 5-10 for most tasks.
2. **Use `--max-budget-usd`** for cost caps. Note: minimum ~$0.05 for system prompt cache creation.
3. **Use `--effort low`** for simple tasks (faster, cheaper). `high` or `max` for complex reasoning.
4. **Use `--bare`** for CI/scripting to skip plugin/hook discovery overhead.
5. **Use `--allowedTools`** to restrict to only what's needed (e.g., `Read` only for reviews).
6. **Use `/compact`** in interactive sessions when context gets large.
7. **Pipe input** instead of having Claude read files when you just need analysis of known content.
8. **Use `--model haiku`** for simple tasks (cheaper) and `--model opus` for complex multi-step work.
9. **Use `--fallback-model haiku`** in print mode to gracefully handle model overload.
10. **Start new sessions for distinct tasks** — sessions last 5 hours; fresh context is more efficient.
11. **Use `--no-session-persistence`** in CI to avoid accumulating saved sessions on disk.

## 设计哲学：98.4%是工程，不是AI

> **核心理念**：模型能力再强，如果没有好的"Harness"（鞍具），也无法在具体项目中发挥价值。详见 `references/architecture-design-philosophy.md`。

### Harness隐喻

> 「一匹马可以跑得很快很有力，但它自己不知道往哪儿走：整套挽具决定了它的方向。」

- **方向盘**：指引方向（CLAUDE.md、Skills）
- **刹车**：安全保障（Hooks、权限系统）
- **导航**：上下文理解（上下文管理、文档）

### 能力占比真相

| 维度 | 传统认知 | 实际真相 |
|------|----------|----------|
| AI能力占比 | 认为是核心 | 仅占1.6% |
| 工程架构占比 | 被忽视 | **占98.4%** |

### 今天就能做的3件事

1. **建立CLAUDE.md**：10分钟写完架构规则、命名约定、踩过的坑。AI犯错时先问：CLAUDE.md里缺了什么？
2. **把重复做事变成Skill**：Code review、commit message、发布说明——不该每天手敲提示词
3. **在踩坑地方加Hook**：最有杠杆的部分，用确定性代码做强制检查，不依赖AI变聪明

### 关键洞察

- **Hook的核心不在写代码，而在写规则**
- **不换模型，优化Harness也能显著提升效果**（LangChain案例：52.8→66.5）
- **工程师价值从"我能写多少行代码"转向"我能为AI设计多严格的工作环境"**

---

## Pitfalls & Gotchas

1. **Interactive mode REQUIRES tmux** — Claude Code is a full TUI app. Using `pty=true` alone in Hermes terminal works but tmux gives you `capture-pane` for monitoring and `send-keys` for input, which is essential for orchestration.
2. **`--dangerously-skip-permissions` dialog defaults to "No, exit"** — you must send Down then Enter to accept. Print mode (`-p`) skips this entirely.
3. **`--max-budget-usd` minimum is ~$0.05** — system prompt cache creation alone costs this much. Setting lower will error immediately.
4. **`--max-turns` is print-mode only** — ignored in interactive sessions.
5. **Claude may use `python` instead of `python3`** — on systems without a `python` symlink, Claude's bash commands will fail on first try but it self-corrects.
6. **Session resumption requires same directory** — `--continue` finds the most recent session for the current working directory.
7. **`--json-schema` needs enough `--max-turns`** — Claude must read files before producing structured output, which takes multiple turns.
8. **Trust dialog only appears once per directory** — first-time only, then cached.
9. **Background tmux sessions persist** — always clean up with `tmux kill-session -t <name>` when done.
10. **Slash commands (like `/commit`) only work in interactive mode** — in `-p` mode, describe the task in natural language instead.
11. **`--bare` skips OAuth** — requires `ANTHROPIC_API_KEY` env var or an `apiKeyHelper` in settings.
12. **Context degradation is real** — AI output quality measurably degrades above 70% context window usage. Monitor with `/context` and proactively `/compact`.

## Rules for Hermes Agents

1. **Prefer print mode (`-p`) for single tasks** — cleaner, no dialog handling, structured output
2. **Use tmux for multi-turn interactive work** — the only reliable way to orchestrate the TUI
3. **Always set `workdir`** — keep Claude focused on the right project directory
4. **Set `--max-turns` in print mode** — prevents infinite loops and runaway costs
5. **Monitor tmux sessions** — use `tmux capture-pane -t <session> -p -S -50` to check progress
6. **Look for the `❯` prompt** — indicates Claude is waiting for input (done or asking a question)
7. **Clean up tmux sessions** — kill them when done to avoid resource leaks
8. **Report results to user** — after completion, summarize what Claude did and what changed
9. **Don't kill slow sessions** — Claude may be doing multi-step work; check progress instead
10. **Use `--allowedTools`** — restrict capabilities to what the task actually needs

---

## 📋 检查点设计

### 检查点 1：环境准备验证

**【前置检查】执行任务前必须验证**：

```bash
# 检查Claude Code是否安装
which claude && claude --version

# 检查认证状态
claude auth status --text

# 检查工作目录
test -d "/path/to/project" && echo "✓ 目录存在" || echo "✗ 目录不存在"
```

**验证清单**：
- [ ] Claude Code已安装（v2.x+）
- [ ] 认证状态有效（Pro/Max或API Key）
- [ ] 工作目录存在且可访问
- [ ] tmux已安装（如需交互模式）

---

### 检查点 2：Print Mode执行验证

**【执行中监控】Print Mode关键指标**：

```bash
# 执行并捕获退出码
claude -p "任务描述" --max-turns 10 --allowedTools "Read,Edit"
exit_code=$?

# 检查退出码
if [ $exit_code -eq 0 ]; then
    echo "✓ 任务成功完成"
else
    echo "✗ 任务失败，退出码: $exit_code"
fi
```

**验证清单**：
- [ ] 命令退出码为0（成功）
- [ ] 输出内容符合预期
- [ ] 文件修改已生效（如有）
- [ ] 未超过max-turns限制

---

### 检查点 3：Interactive Mode会话验证

**【会话管理】Interactive Mode关键节点**：

```bash
# 1. 启动tmux会话
tmux new-session -d -s claude-work -x 140 -y 40
echo "✓ tmux会话已创建"

# 2. 启动Claude并等待初始化
tmux send-keys -t claude-work 'cd /project && claude' Enter
sleep 5  # 等待初始化

# 3. 处理信任对话框
tmux send-keys -t claude-work Enter
sleep 3

# 4. 验证Claude已就绪（检查提示符）
tmux capture-pane -t claude-work -p -S -5 | grep "❯" && echo "✓ Claude已就绪"
```

**验证清单**：
- [ ] tmux会话创建成功
- [ ] Claude初始化完成
- [ ] 信任对话框已处理
- [ ] Claude提示符可见（❯）

---

### 检查点 4：任务完成验证

**【结果验证】任务完成后必须检查**：

```bash
# Print Mode结果验证
claude -p "任务描述" --output-format json 2>&1 | jq -r '.status'
# 期望输出: "success" 或 "completed"

# Interactive Mode进度检查
tmux capture-pane -t claude-work -p -S -50 | grep -E "(完成|finished|done|❯)"
# 期望看到完成标志或新的提示符

# 文件修改验证
git status --short  # 检查是否有预期的文件变更
git diff --stat     # 检查修改范围
```

**验证清单**：
- [ ] 任务状态为success/completed
- [ ] 文件修改符合预期
- [ ] 无错误或警告信息
- [ ] 代码可编译/运行（如适用）

---

## ⚠️ 异常处理

### 异常类型1：认证失败

**症状**：
```
Error: Not authenticated. Run 'claude auth login' first.
```

**恢复流程**：
```bash
# 1. 检查认证状态
claude auth status

# 2. 重新认证
claude auth login  # 浏览器OAuth
# 或
claude auth login --console  # API Key

# 3. 验证认证成功
claude auth status --text | grep "Logged in"
```

---

### 异常类型2：工作目录不存在

**症状**：
```
Error: Directory '/path/to/project' does not exist
```

**恢复流程**：
```bash
# 1. 验证目录路径
pwd
ls -la /path/to/project

# 2. 创建目录（如需要）
mkdir -p /path/to/project

# 3. 重新执行任务
cd /path/to/project && claude -p "任务描述"
```

---

### 异常类型3：超时或卡死

**症状**：
- Print Mode长时间无输出（>5分钟）
- Interactive Mode无响应（>10分钟）

**恢复流程**：
```bash
# Print Mode
# 1. 中断当前命令（Ctrl+C）
# 2. 降低max-turns
claude -p "任务描述" --max-turns 5

# Interactive Mode
# 1. 检查会话状态
tmux capture-pane -t claude-work -p -S -50

# 2. 强制退出并重启
tmux kill-session -t claude-work
tmux new-session -d -s claude-work
```

---

### 异常类型4：权限被拒绝

**症状**：
```
Error: Permission denied: /path/to/file
```

**恢复流程**：
```bash
# 1. 检查文件权限
ls -la /path/to/file

# 2. 修改权限（如需要）
chmod 644 /path/to/file  # 文件
chmod 755 /path/to/dir   # 目录

# 3. 重新执行任务
claude -p "任务描述"
```

---

### 异常类型5：模型过载

**症状**：
```
Error: Model overloaded. Please retry.
```

**恢复流程**：
```bash
# 1. 使用fallback模型
claude -p "任务描述" --fallback-model haiku

# 2. 或直接使用Haiku
claude -p "任务描述" --model haiku

# 3. 等待后重试
sleep 60 && claude -p "任务描述"
```

---

### 异常类型6：上下文窗口溢出

**症状**：
```
Error: Context window exceeded. Use /compact or reduce input size.
```

**恢复流程**：
```bash
# Interactive Mode
tmux send-keys -t claude-work '/compact' Enter
sleep 5

# Print Mode
# 1. 减少输入文件数量
claude -p "分析单个文件" --allowedTools "Read"

# 2. 或使用更短的提示词
claude -p "简要分析 auth.py"
```

---

### 异常类型7：tmux会话冲突

**症状**：
```
duplicate session
```

**恢复流程**：
```bash
# 1. 列出现有会话
tmux list-sessions

# 2. 杀死旧会话
tmux kill-session -t claude-work

# 3. 创建新会话
tmux new-session -d -s claude-work
```

---

### 异常类型8：预算超限

**症状**：
```
Error: Budget exceeded ($X.XX used, limit was $Y.YY)
```

**恢复流程**：
```bash
# 1. 提高预算限制
claude -p "任务描述" --max-budget-usd 1.00

# 2. 或使用更便宜的模型
claude -p "任务描述" --model haiku

# 3. 减少max-turns
claude -p "任务描述" --max-turns 3
```

---

## 🎯 边界条件

### 资源边界

| 资源 | 最小值 | 最大值 | 推荐值 | 说明 |
|------|--------|--------|--------|------|
| **max-turns** | 1 | 100 | 5-20 | Print Mode专用 |
| **max-budget-usd** | $0.05 | 无限制 | $0.10-1.00 | 最低$0.05用于缓存 |
| **上下文窗口** | - | 200K tokens | <70% | 超过70%质量下降 |
| **会话时长** | - | 5小时 | 1-2小时 | 之后需新会话 |

### 并发边界

| 场景 | 限制 | 说明 |
|------|------|------|
| **Print Mode并发** | 建议≤3个 | 避免API限流 |
| **Interactive Mode会话** | 建议≤2个 | tmux资源消耗 |
| **文件操作** | 单次≤100文件 | 避免上下文溢出 |

### 性能边界

| 指标 | 目标值 | 告警阈值 | 说明 |
|------|--------|----------|------|
| **Print Mode响应时间** | <30秒 | >60秒 | 简单任务 |
| **Interactive Mode首次响应** | <10秒 | >20秒 | 复杂任务可能更长 |
| **文件读取速度** | <1秒/文件 | >3秒/文件 | 大文件例外 |

### 使用场景边界

**适用场景** ✅：
- 代码重构和优化
- Bug修复和调试
- 代码审查和改进
- 文档生成
- 测试编写
- API集成

**不适用场景** ❌：
- 实时性要求高的任务（<5秒响应）
- 大规模文件批量处理（>100文件）
- 需要图形界面的操作
- 系统级配置修改
- 敏感数据处理（无审计）

---

## 📊 成功指标

| 指标 | 目标 | 测量方法 |
|------|------|---------|
| **任务成功率** | >95% | exit_code=0的比例 |
| **代码质量** | 无阻塞性问题 | 人工审查或CI检查 |
| **响应速度** | <60秒 | 简单任务完成时间 |
| **成本控制** | <$1.00/任务 | max-budget-usd监控 |

---

## 🔄 恢复策略总结

| 异常类型 | 自动恢复 | 人工介入 | 预防措施 |
|---------|---------|---------|---------|
| 认证失败 | ❌ | ✅ 重登录 | 定期检查认证状态 |
| 目录不存在 | ✅ 自动创建 | ❌ | 前置检查 |
| 超时卡死 | ✅ 重启任务 | ❌ | 设置合理max-turns |
| 权限拒绝 | ✅ 修改权限 | ❌ | 预先检查权限 |
| 模型过载 | ✅ fallback模型 | ❌ | 使用Haiku备用 |
| 上下文溢出 | ✅ /compact | ❌ | 监控上下文使用率 |
| tmux冲突 | ✅ 杀旧会话 | ❌ | 用后清理 |
| 预算超限 | ✅ 提高预算 | ❌ | 设置合理上限 |

---

## ⚠️ Known Gotchas

### 认证和权限问题

- **认证过期**: Claude Code 会话失效
  ```bash
  # 检查认证状态
  claude auth status
  
  # 重新认证
  claude auth login
  
  # 或使用 API Key
  export ANTHROPIC_API_KEY="sk-ant-..."
  claude auth login --console
  ```

- **权限不足**: 无法访问项目目录
  ```bash
  # 检查目录权限
  ls -la /path/to/project
  
  # 修复权限
  chmod -R u+rw /path/to/project
  
  # 或切换到有权限的用户
  sudo -u owner claude -p "task"
  ```

- **工作区信任失败**: Print 模式跳过信任提示
  ```bash
  # Print 模式自动信任
  # ❌ 不推荐在不受信任的代码库使用
  claude -p "analyze code"
  
  # ✅ 正确: 先手动信任工作区
  claude trust /path/to/project
  claude -p "task"
  ```

### Print 模式陷阱

- **超时未设置**: 默认 60 秒不够
  ```python
  # ❌ 错误: 未设置超时
  terminal("claude -p 'complex task'")
  
  # ✅ 正确: 设置足够超时
  terminal(
      "claude -p 'complex task' --max-turns 20",
      timeout=300  # 5 分钟
  )
  ```

- **JSON Schema 解析失败**: 输出格式不符合预期
  ```bash
  # 使用 --json-schema 严格约束
  claude -p "extract APIs" \
    --json-schema '{"type": "array", "items": {"type": "string"}}'
  ```

- **allowedTools 过宽**: 给予过多权限
  ```bash
  # ❌ 错误: 允许所有工具
  claude -p "task" --allowedTools "*"
  
  # ✅ 正确: 仅允许必要工具
  claude -p "task" --allowedTools "Read,Edit,Write"
  ```

### PTY/tmux 模式问题

- **tmux 会话残留**: 未正确清理
  ```bash
  # 检查残留会话
  tmux list-sessions
  
  # 清理所有 Claude 会话
  tmux kill-session -t claude-* 2>/dev/null
  
  # 或强制清理
  tmux kill-server
  ```

- **PTY 响应超时**: 交互式提示卡住
  ```python
  # 设置合理的读取超时
  process = terminal(
      "claude",
      background=True,
      pty=True,
      timeout=300
  )
  
  # 等待响应
  time.sleep(2)
  output = process.poll()
  ```

- **多轮对话丢失上下文**: 会话重启后失忆
  ```python
  # 保存会话状态
  session_id = save_session()
  
  # 恢复会话
  claude resume <session_id>
  ```

### 工具调用问题

- **Edit 工具失败**: 文件内容不匹配
  ```python
  # Claude Code 使用字符串匹配编辑
  # ❌ 错误: 空格/缩进不匹配
  # ✅ 正确: 精确匹配原文件内容
  
  # 先 Read 查看原始内容
  # 再 Edit 精确替换
  ```

- **Bash 工具被禁**: 安全策略限制
  ```bash
  # 检查工具权限
  claude -p "list tools" --allowedTools "Read"
  
  # 启用必要工具
  claude -p "task" --allowedTools "Read,Edit,Bash"
  ```

- **文件路径错误**: 相对路径解析失败
  ```python
  # ❌ 错误: 相对路径
  claude -p "edit src/main.py"
  
  # ✅ 正确: 使用 workdir
  terminal(
      "claude -p 'edit src/main.py'",
      workdir="/absolute/path/to/project"
  )
  ```

### 成本控制问题

- **预算超支**: 未设置 max-budget
  ```bash
  # 设置预算上限
  claude -p "task" --max-budget-usd 1.00
  
  # 监控成本
  # 每次 API 调用都会累计
  # 超过预算自动停止
  ```

- **Token 浪费**: 重复读取大文件
  ```python
  # 避免重复读取
  # ❌ 错误: 多次读取同一文件
  for file in files:
      claude -p f"read {file}"
  
  # ✅ 正确: 一次性读取多个文件
  claude -p f"read {' '.join(files)}"
  ```

- **模型选择错误**: Sonnet/Opus 不匹配任务
  ```bash
  # 简单任务用 Haiku（便宜）
  claude -p "fix typo" --model claude-3-haiku
  
  # 复杂任务用 Sonnet（平衡）
  claude -p "refactor module" --model claude-3-sonnet
  
  # 困难任务用 Opus（强大）
  claude -p "architectural redesign" --model claude-3-opus
  ```

### 并发和冲突

- **多个 Claude 实例冲突**: 同时修改同一文件
  ```python
  # 使用锁机制
  import fcntl
  
  with open("/tmp/claude.lock", "w") as lock:
      fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
      terminal("claude -p 'task'")
      fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
  ```

- **Git 冲突**: Claude 提交与本地冲突
  ```bash
  # 提交前先拉取
  claude -p "git pull && make changes && git commit"
  
  # 或使用分支隔离
  claude -p "git checkout -b feature/ai-gen && make changes"
  ```

- **IDE 文件监控**: 文件变化触发重载
  ```bash
  # 临时禁用 IDE 监控
  # VSCode: 设置 "files.watcherExclude"
  # JetBrains: Settings → Appearance → Disable auto-reload
  ```

### 性能问题

- **启动慢**: 首次运行需要初始化
  ```bash
  # 预热 Claude Code
  claude --version
  claude doctor
  ```

- **大文件处理慢**: 文件超过 1MB
  ```python
  # 分段处理大文件
  chunks = split_large_file(file, max_size=500000)
  for chunk in chunks:
      result = claude -p f"process: {chunk}"
  ```

- **网络延迟**: API 调用慢
  ```python
  # 使用缓存
  # 相同请求会复用结果
  
  # 或切换到更近的 API endpoint
  export ANTHROPIC_API_BASE="https://api.anthropic.com"
  ```

### 输出质量

- **代码风格不一致**: 与项目规范冲突
  ```bash
  # 提供 CLAUDE.md 或 .cursorrules
  # Claude Code 会自动读取项目规范
  
  # 或显式指定
  claude -p "follow PEP 8, max line length 88"
  ```

- **生成代码有 Bug**: 未经过测试
  ```python
  # 要求 Claude 生成测试
  claude -p "implement feature X and write tests"
  
  # 或使用 TDD
  claude -p "write tests first, then implement"
  ```

- **理解偏差**: 任务描述不清晰
  ```python
  # ❌ 错误: 模糊描述
  claude -p "optimize code"
  
  # ✅ 正确: 明确目标
  claude -p "optimize performance: reduce time complexity from O(n²) to O(n log n)"
  ```

### 兼容性问题

- **Node.js 版本不兼容**: 需要 Node 18+
  ```bash
  # 检查 Node 版本
  node --version
  
  # 升级 Node
  nvm install 18
  nvm use 18
  ```

- **操作系统限制**: Windows/WSL 路径问题
  ```bash
  # Windows: 使用 WSL
  wsl claude -p "task"
  
  # 或使用 Git Bash
  # 注意路径转换: C:\path → /c/path
  ```

- **环境变量缺失**: ANTHROPIC_API_KEY 未设置
  ```bash
  # 检查环境变量
  echo $ANTHROPIC_API_KEY
  
  # 添加到 ~/.bashrc
  echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
  source ~/.bashrc
  ```
