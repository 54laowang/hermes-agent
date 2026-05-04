---
name: fix-nvm-repeated-install
title: 修复 NVM 反复重新安装问题
description: 解决因版本冲突导致 npm 全局包反复重新安装的问题
---

# 修复 NVM 反复重新安装问题

## 问题现象

- NVM 安装的 Node.js 版本来回切换
- 每次打开新终端都需要重新安装全局 npm 包
- Claude Code 等工具提示找不到命令，需要重新安装

## 根本原因

错误地在 NVM 加载**之前**硬编码了特定版本的 PATH：
```bash
# ❌ 错误做法
export PATH="/Users/me/.nvm/versions/node/v25.9.0/bin:$PATH"
```

这导致：
1. NVM 本身还没加载，硬编码就先加入了路径
2. NVM 加载后会将默认版本再次加入 PATH
3. 不同环境下版本顺序不同，一会儿 v23.11.1，一会儿 v25.9.0
4. 版本切换后全局包位置变化，需要重新安装

## 修复步骤

### 1. 设置默认版本

让 NVM 统一管理默认版本：
```bash
nvm alias default v25.9.0  # 替换为你想要的版本
```

### 2. 修复 .zshrc 配置

移除开头的硬编码 PATH，改为在 NVM 加载完成后自动激活：

找到 `.zshrc` 中 NVM 加载块，在末尾添加：
```bash
# Load NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# ✅ 添加这一行：NVM 加载完成后自动使用默认版本
[[ -n "$NVM_DIR" ]] && nvm use default &>/dev/null
```

### 3. 移除硬编码

删除文件开头的 `export PATH="/Users/me/.nvm/versions/node/..."` 硬编码行，让 NVM 动态管理 PATH。

## 验证修复

打开新终端，检查：
```bash
node -v      # 应该一直显示默认版本，不会变化
which node   # 应该指向 NVM 目录下的对应版本
```

## 适用场景

- 需要优先使用 NVM 安装的 Claude Code，而不是 Homebrew 版本
- oh-my-claudecode 安装在 NVM Node.js 全局环境
- 避免每次新版本发布后都需要重新调整 PATH

## 注意事项

- 默认版本改变后，只需要更新 `nvm alias default <new-version>`
- 如果有多个 Node 版本需要切换，仍然可以使用 `nvm use <version>` 临时切换
- 永久改变默认版本只需要重新设置 alias 即可
