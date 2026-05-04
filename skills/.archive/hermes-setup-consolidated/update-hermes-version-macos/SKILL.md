---
name: update-hermes-version-macos
description: 在 macOS 上更新 Hermes Agent 到最新版本，处理本地修改和依赖问题
author: Hermes
---

# 更新 Hermes Agent 版本（macOS）

在 macOS 上更新已安装的 Hermes Agent 到最新版本的标准流程。

## 推荐方法（官方内置命令）

### 1. 检查当前版本和更新状态

```bash
hermes --version
```

该命令会显示：
- 当前安装的版本号
- 是否有更新可用（落后多少个 commits）
- Python 和 OpenAI SDK 版本

### 2. 检查本地修改

```bash
git -C ~/.hermes/hermes-agent status --short
```

如果有本地修改（显示 M 标记的文件），需要先备份：

```bash
git -C ~/.hermes/hermes-agent stash
```

### 3. 执行官方更新命令

```bash
hermes update
```

该命令会自动完成以下操作：
- ✅ Fetch 和 Pull 最新代码
- ✅ 更新 Python 依赖
- ✅ 更新 Node.js 依赖（repo root + ui-tui）
- ✅ 重新构建 Web UI
- ✅ 同步内置技能（保留用户修改的 62 个技能）
- ✅ 检查配置更新
- ✅ 重启网关服务（ai.hermes.gateway）

### 4. 恢复本地修改

```bash
git -C ~/.hermes/hermes-agent stash pop
```

### 5. 验证更新成功

```bash
hermes --version
```

显示 "Up to date" 表示已更新到最新版本。

---

## 查看更新内容

### 查看提交历史

```bash
# 查看最近 N 个提交
git -C ~/.hermes/hermes-agent log --oneline -10

# 查看两个版本之间的差异
git -C ~/.hermes/hermes-agent log --oneline <old-commit>..HEAD --no-merges
```

### 检查特定组件的更新

```bash
# Web UI 更新
git -C ~/.hermes/hermes-agent diff <old-commit>..HEAD --name-only -- web/

# TUI (终端 UI) 更新
git -C ~/.hermes/hermes-agent diff <old-commit>..HEAD --name-only -- ui-tui/

# 按类别查看变更
git -C ~/.hermes/hermes-agent diff <old-commit>..HEAD --stat
```

---

## 手动更新方法（备用）

如果 `hermes update` 命令失败，可以手动执行：

```bash
cd ~/.hermes/hermes-agent
git stash  # 备份本地修改
git pull
git stash pop  # 恢复本地修改
```

手动安装依赖：
```bash
uv pip install -e . --no-deps
.venv/bin/python -m ensurepip
.venv/bin/python -m pip install pyyaml aiohttp rich prompt_toolkit anthropic openai pydantic python-dotenv requests jinja2 httpx tenacity
```

---

## 关键要点

1. **"X commits behind" 说明**: `hermes --version` 显示的落后 commits 数量是预估值，实际执行 `hermes update` 后会拉取真正的最新提交

2. **本地修改保留**: 通过 `git stash` + `git stash pop` 可以保留用户对 `cli.py`、`ModelPickerDialog.tsx` 等文件的自定义修改

3. **相关组件版本检查**:
   ```bash
   # 检查 oh-my-claudecode 版本
   omc --version

   # 检查 AutoCLI 版本
   autocli --version
   ```

4. **更新后的验证清单**:
   - ✅ `hermes --version` 显示 "Up to date"
   - ✅ `git status` 显示分支与 origin/main 同步
   - ✅ Web UI 可以正常访问
   - ✅ 网关服务已重启（如果在运行）
