---
name: install-oh-my-claudecode-macos
description: Complete step-by-step installation guide for oh-my-claudecode (Sisyphus) on macOS, solving common npm/optional dependency issues
author: Hermes
tags: [claude-code, oh-my-claudecode, installation, macos, multi-agent]
---

# Install oh-my-claudecode on macOS

Complete step-by-step installation guide for oh-my-claudecode (Sisyphus) on macOS, solving common npm/optional dependency issues.

## Trigger
Need to install oh-my-claudecode (oh-my-claude-sisyphus) for Claude Code multi-agent orchestration on macOS.

## Prerequisites
- macOS (Apple Silicon/Intel supported)
- Node.js + npm (via nvm or manual)
- Homebrew installed

## Step-by-step Installation

### 1. Uninstall any broken existing Claude Code
```bash
# Uninstall npm global version
npm uninstall -g @anthropic-ai/claude-code

# If installed via brew and want to switch
brew uninstall claude
```

### 2. Install Claude Code via Homebrew (RECOMMENDED)
This avoids the `--omit=optional` npm issue completely:
```bash
# Add Anthropic tap
brew tap anthropic-ai/claude

# Install Claude Code
brew install claude
```

### 3. Verify Claude Code installation
```bash
# Should output version like "2.1.74 (Claude Code)"
claude --version
```

### 4. Install oh-my-claude-sisyphus (oh-my-claudecode)
```bash
npm install -g oh-my-claude-sisyphus
```

### 5. Initialize configuration
```bash
omc init
```

### 6. Activate in Claude Code
1. Start Claude Code:
```bash
claude
```
2. Inside Claude Code, run:
```
/plugin install Yeachan-Heo/oh-my-claudecode
```

### 7. Restart Claude Code and start
After plugin installation completes, exit and restart Claude Code, then:
```
/start
```

## Common Issues & Solutions

### Issue 1: "claude native binary not installed" after npm install
**Cause:** npm defaults to `--omit=optional` which skips the native binary dependency.
**Solution:** Use the Homebrew installation method above.

### Issue 2: omc says "claude CLI not found"
**Cause:** Claude not installed or not in PATH.
**Solution:**
```bash
# Check if claude is found
which claude
# If empty, fix brew installation
brew unlink claude && brew link claude
```

### Issue 3: Multiple Claude versions, want NVM version to take priority
**Cause:** Old Homebrew version installed and takes precedence in PATH.
**Solution:** Add to the **TOP** of `~/.zshrc` (or `~/.bashrc`):
```bash
# Replace <version> with your nvm node version (e.g. v23.11.1)
export PATH="/Users/$USER/.nvm/versions/node/<version>/bin:$PATH"
```
Then restart shell.

### Issue 4: Deadly loop between cli-wrapper.cjs and cli-wrapper.sh
**Cause:** Installation script bug creates mutual recursion.
**Solution:** Edit `cli-wrapper.cjs` to directly call the native binary without going through the shell wrapper. Find the binary path:
- Homebrew: `/opt/homebrew/bin/claude`
- NVM: `/Users/$USER/.nvm/versions/node/<version>/lib/node_modules/@anthropic-ai/claude-code/bin/claude`

### Issue 5: Network/SSL failure downloading binary
**Cause:** Proxy/network issues prevent GitHub release downloads.
**Solution:** Copy working binary from existing installation:
```bash
# If you have a working Homebrew copy:
cp /opt/homebrew/bin/claude /Users/$USER/.nvm/versions/node/<version>/lib/node_modules/@anthropic-ai/claude-code/bin/claude
```

### Issue 6: NVM installation corrupted - npm missing after node install
**Cause:** NVM installation interrupted, leaving `npm` symlinks but actual `npm` directory missing.
**Solution:** Reinstall node version completely:
```bash
source $HOME/.nvm/nvm.sh
nvm use <current-working-version>
nvm uninstall <target-broken-version>
nvm install <target-broken-version>
```

### Issue 7: `@anthropic-ai/claude-code-darwin-arm64` installed but missing actual `claude` binary
**Cause:** npm packages for platform-specific binaries are just **empty placeholders** (316 bytes total). The real binary is downloaded dynamically during postinstall from Anthropic CDN. When network download fails, you get an empty package and `ENOENT` error when running `claude`.

**Solution - Manual download from Anthropic CDN:**
```bash
# Replace VERSION with your installed version (e.g. 2.1.114)
VERSION=2.1.114
cd /tmp
# Download with curl (use proxy if needed)
curl -fSL --proxy http://127.0.0.1:7890 https://downloads.claude.ai/claude-code-releases/$VERSION/darwin-arm64/claude -o claude
chmod +x /tmp/claude
# Place in the correct location
cp /tmp/claude /Users/$USER/.nvm/versions/node/<node-version>/lib/node_modules/@anthropic-ai/claude-code-darwin-arm64/claude
# Re-run postinstall to link
cd /Users/$USER/.nvm/versions/node/<node-version>/lib/node_modules/@anthropic-ai/claude-code
node install.cjs
```

**Download URL pattern:**
- `https://downloads.claude.ai/claude-code-releases/{VERSION}/{PLATFORM}/claude`
- Platform options: `darwin-arm64`, `darwin-x64`, `linux-x64`, `linux-arm64`

### Issue 8: NVM node installation corrupted - npm command not found after install
**Cause:** Installation interrupted, leaves symlinks but `../lib/node_modules/npm` directory is actually missing. NVM `ls` shows the version exists but `nvm use` says "not installed".

**Solution - Full reinstall:**
```bash
source $HOME/.nvm/nvm.sh
nvm use <existing-working-version>  # e.g. nvm use v23.11.1
nvm uninstall <target-broken-version>  # e.g. nvm uninstall v25.9.0
nvm install <target-broken-version>
```
After reinstall, npm is restored. Then reinstall the global packages:
```bash
nvm use v25.9.0
npm install -g @anthropic-ai/claude-code
npm install -g oh-my-claude-sisyphus
```

**This also fixes:**
- `bash: npm: command not found` after nvm installation
- NVM shows version in `nvm ls` but `nvm use` reports "not yet installed"

### Issue 9: After npm install, optionalDependencies (platform package) not installed
**Cause:** npm in global mode sometimes skips optionalDependencies. The platform package is required but missing.

**Solution - Install explicitly:**
```bash
# For Apple Silicon macOS:
npm install -g @anthropic-ai/claude-code-darwin-arm64
# For Intel macOS:
# npm install -g @anthropic-ai/claude-code-darwin-x64
```

### Issue 10: How to install oh-my-claudecode plugin when plugin marketpace doesn't install it
**Cause:** You're using npm global installation instead of Claude Code built-in plugin installer.

**Solution - Manual plugin install:**
```bash
# Copy the plugin from npm package to Claude plugins directory
mkdir -p ~/.claude/plugins/oh-my-claudecode
cp -r /Users/$USER/.nvm/versions/node/<node-version>/lib/node_modules/oh-my-claude-sisyphus/.claude-plugin/* ~/.claude/plugins/oh-my-claudecode/
```
Then restart Claude Code and run `/omc-setup` inside Claude.

## Verification
After installation, inside Claude Code you should see:
- `/start` command available
- `/team <task>` works
- Plugin shows in `/plugin list`

## Notes
- oh-my-claudecode is the official successor to Claude-Code-Game-Studios
- It's a general-purpose multi-agent orchestration framework, not limited to game development
- Active development, 29.7k+ GitHub stars as of April 2026
