---
name: update-oh-my-claudecode-macos
title: macOS 更新 oh-my-claudecode 和 Claude Code 完整流程
description: 在 macOS 上更新 oh-my-claudecode、修复 NVM 环境、解决 Claude Code 更新问题、PATH 多版本冲突、CC Switch 配置管理
---

# macOS 更新 oh-my-claudecode 和 Claude Code 完整流程

## 问题场景

- 需要更新 Claude Code 到最新版本
- 旧版本在 `/opt/homebrew/bin/claude`，权限问题无法删除
- NVM 安装损坏，npm 缺失
- 需要优先使用 NVM 版本
- **多版本 PATH 冲突** — Homebrew、.local 原生、npm 三个安装位置互相干扰
- **CC Switch 配置管理** — 快速切换多个 API 提供商配置

## 完整更新步骤

### 0. 检测现有安装和版本冲突

首先检查是否有多个 Claude Code 安装：
```bash
# 列出所有位置的 claude
which -a claude

# 检查每个位置的版本
/opt/homebrew/bin/claude --version      # Homebrew 版本（通常较旧）
/Users/me/.local/bin/claude --version    # 官方原生版本（推荐）
$(npm bin -g)/claude --version           # npm 全局版本（可能冲突）
```

典型的多版本情况：
- `/opt/homebrew/bin/claude` → 2.1.74 (旧版)
- `/Users/me/.local/bin/claude` → 2.1.114 (官方原生)
- `~/.nvm/versions/node/v25.9.0/bin/claude` → npm 安装

### 1. 官方推荐：使用内置更新（优先方法）

**原生安装（.local）是官方推荐方式**，有内置更新机制：
```bash
# 使用官方原生安装的更新命令
/Users/me/.local/bin/claude --update
```

这个命令会：
- 自动检测最新版本
- 更新原生安装
- 修复配置文件
- 发出多版本冲突警告（如果有）

### 2. 解决 PATH 优先级问题

如果 `.local/bin` 在 PATH 中排在 `/opt/homebrew/bin` 后面，会导致旧版本优先被调用。

**修复方法**：在 `~/.zshrc` **开头**添加：
```bash
# Make .local/bin priority for Claude Code (官方原生安装优先)
export PATH=$HOME/.local/bin:$PATH
```

然后刷新 shell：
```bash
source ~/.zshrc
hash -r  # 清除命令缓存
```

验证：
```bash
which claude      # 应该显示 /Users/me/.local/bin/claude
claude --version  # 应该显示最新版本
```

### 3. 清理重复安装

建议只保留**官方原生安装**，卸载其他版本避免混淆：
```bash
# 卸载 npm 全局版本
npm -g uninstall @anthropic-ai/claude-code

# Homebrew 版本可以保留，但 PATH 优先级会让它不被调用
# 如果确实不需要：brew uninstall claude-code
```

### 4. 修复 NVM 环境

如果 NVM 未加载：
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

设置默认 Node.js 版本（解决反复安装问题）：
```bash
nvm alias default v25.9.0  # 使用最新稳定版
```

### 2. 更新 oh-my-claudecode

```bash
npm install -g oh-my-claude-sisyphus
```

### 3. 修复 npm 安装后的死循环问题

npm 安装后会生成 `cli-wrapper.cjs` 调用 `cli-wrapper.sh` 再调用自己，导致死循环。修复：

找到安装目录：
```bash
CLAUDE_PATH=$(dirname $(which claude))
cd $CLAUDE_PATH/../lib/node_modules/@anthropic-ai/claude-code
```

修改 `bin/cli-wrapper.cjs`，直接调用原生二进制：
```javascript
// 注释掉原有调用 cli-wrapper.sh 的代码
// const { spawn } = require('child_process');
// const path = require('path');
// const wrapperPath = path.join(__dirname, 'cli-wrapper.sh');
// spawn('sh', [wrapperPath], { stdio: 'inherit' }).on('close', (code) => process.exit(code));

// 直接调用原生二进制
const { spawn } = require('child_process');
const path = require('path');
const binaryPath = path.join(__dirname, '../claude-code-darwin-arm64/claude');
spawn(binaryPath, process.argv.slice(2), { stdio: 'inherit' }).on('close', (code) => process.exit(code));
```

### 4. 确保原生二进制存在

如果 postinstall 下载失败（网络问题），手动从已更新位置复制：
```bash
cp /Users/me/.local/bin/claude $CLAUDE_PATH/../lib/node_modules/@anthropic-ai/claude-code/claude-code-darwin-arm64/claude
chmod +x $CLAUDE_PATH/../lib/node_modules/@anthropic-ai/claude-code/claude-code-darwin-arm64/claude
```

重新运行 postinstall：
```bash
npm run postinstall
```

### 5. 配置 .zshrc PATH 优先级（解决 Homebrew 旧版本无法删除问题）

确保在 `.zshrc` 中：

```bash
# Load NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# 自动使用默认版本，解决版本反复切换问题
[[ -n "$NVM_DIR" ]] && nvm use default &>/dev/null
```

> **重要**：不要在文件开头硬编码 PATH，NVM 会自动管理。这会解决 NVM 反复重新安装问题。

### 6. 安装 tmux（支持 omc launch）

```bash
brew install tmux
```

## 配置管理工具：CC Switch

### 什么是 CC Switch

**CC Switch** (`@songhe/cc-switch`) 是 Claude Code 配置切换器，可以轻松管理和切换多个 API 提供商配置（Anthropic、火山引擎、OpenRouter 等）。

### 安装 CC Switch

```bash
npm install -g @songhe/cc-switch
```

验证安装：
```bash
ccs --version  # 应显示 1.1.2 或更高
```

### 常用命令

| 命令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `ccs add <name> <url> <token>` | `a` | 添加新配置 | `ccs add glm https://ark.cn-beijing.volces.com/api/v3 YOUR_API_KEY` |
| `ccs list` | `ls` | 列出所有配置 | `ccs list` |
| `ccs switch <name>` | `sw` | 切换到指定配置 | `ccs switch glm` |
| `ccs current` | | 显示当前使用的配置 | `ccs current` |
| `ccs remove <name>` | `rm` | 删除配置 | `ccs remove old-config` |
| `ccs backup` | | 备份所有配置 | `ccs backup` |

### 使用场景

1. **工作/个人环境切换**：快速在公司 API 和个人 API 之间切换
2. **多模型提供商切换**：在 Anthropic、火山引擎 GLM、OpenRouter 之间一键切换
3. **配置备份恢复**：迁移机器时备份恢复所有配置

### 导入现有配置

从当前 Claude Code 配置导入：
```bash
# 查看当前 Claude Code 配置
cat ~/.claude/settings.json

# 提取 API URL 和 Token 后添加到 CC Switch
ccs add my-config "https://api.example.com/v1" "your-api-token"
```

## 验证

```bash
# 检查 Node.js 版本
node -v  # 应该显示默认版本

# 检查 Claude Code 版本
claude --version  # 应该显示最新版本，比如 2.1.114

# 检查 oh-my-claudecode
omc --version  # 应该显示版本，比如 4.13.0

# 启动编排环境（在真正的终端中运行）
omc launch
```

## 常见问题

### Q: 运行 `claude --update` 报错 "Multiple versions found"？
A: 说明有多个 Claude Code 安装。先检查 `which -a claude`，让官方原生安装 PATH 优先（见步骤 2），或卸载 npm 版本。

### Q: 更新后 `claude --version` 还是显示旧版本？
A:
1. 检查 PATH 顺序：`echo $PATH | tr ':' '\n' | head -5`
2. 确保 `~/.local/bin` 在 `/opt/homebrew/bin` 前面
3. 清除命令缓存：`hash -r` 或重启终端

### Q: 我应该保留哪个安装版本？
A: **优先保留官方原生安装（~/.local/bin/claude）**，它有内置更新机制且更新最快。npm 和 Homebrew 版本可以卸载。

### Q: 为什么 NVM 会反复重新安装？
A: 因为在 NVM 加载前硬编码 PATH，导致版本冲突。修复方法见上面配置，使用 `nvm alias default` + 自动激活。

### Q: Claude Code 启动时报错 "command not found"？
A: 检查原生二进制是否存在且有可执行权限：`chmod +x <path-to-claude-binary>`

### Q: omc launch 报错 "claude not found"？
A: 确保 claude 在 NVM 当前版本的 PATH 中，重新运行 `npm install -g oh-my-claude-sisyphus` 在正确版本下安装。

### Q: CC Switch 和 CC Swap 有什么区别？
A:
- **`ccs` (CC Switch)**：`@songhe/cc-switch` npm 包，完整的配置管理 CLI
- **`cc swap`**：Claude Code 内置命令，只管理单个文件中的配置，可能冲突

推荐使用独立的 `ccs` 工具，更稳定、功能更完整。

### Q: 如何从内置配置迁移到 CC Switch？
A:
```bash
# 1. 查看当前配置
cat ~/.claude/settings.json

# 2. 提取 base_url 和 api_key 添加到 CC Switch
ccs add my-config "<base_url>" "<api_key>"

# 3. 切换到新配置
ccs switch my-config
```

## 参考

相关技能：
- `fix-nvm-repeated-install` 解决版本冲突问题
- `install-oh-my-claudecode-macos` 全新安装指南
