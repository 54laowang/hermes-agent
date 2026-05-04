# Dashboard 启动指南

Hermes Agent 内置 Web Dashboard，提供可视化配置管理、会话浏览和内嵌 Chat 功能。

## 快速启动

```bash
# 进入项目目录
cd ~/.hermes/hermes-agent
source .venv/bin/activate

# 启动 Dashboard（带 TUI Chat）
python -m hermes_cli.main dashboard --no-open --tui

# 访问地址
# http://127.0.0.1:9119/
```

## 启动参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--port PORT` | 监听端口 | 9119 |
| `--host HOST` | 监听地址 | 127.0.0.1 |
| `--no-open` | 不自动打开浏览器 | False |
| `--insecure` | 允许非 localhost 绑定（危险） | False |
| `--tui` | 启用内嵌 Chat 功能 | False |
| `--stop` | 停止所有运行的 Dashboard 进程 | - |
| `--status` | 查看运行中的进程 | - |

## 常见问题

### 1. 启动失败：Web UI build failed

**现象**：
```
→ Building web UI...
  ✗ Web UI build failed
  Run manually:  cd web && npm install && npm run build
```

**解决**：
```bash
cd ~/.hermes/hermes-agent/web
npm install
npm run build
```

### 2. 构建失败：TypeScript 错误

**现象**：
```
src/components/ModelPickerDialog.tsx(126,4): error TS1005: ')' expected.
```

**原因**：保守式更新后冲突残留或本地修改不兼容

**解决**：
```bash
# 恢复上游版本
git checkout origin/main -- web/src/components/ModelPickerDialog.tsx

# 如果有自定义组件报错，移除它们
rm -f web/src/components/ToolRouterStatus.tsx

# 重新构建
cd web && npm run build
```

### 3. Chat unavailable: ptyprocess missing

**现象**：
```
Chat unavailable: The `ptyprocess` package is missing.
```

**解决**：
```bash
cd ~/.hermes/hermes-agent
source .venv/bin/activate
python -m pip install ptyprocess

# 重启 Dashboard
python -m hermes_cli.main dashboard --no-open --tui
```

### 4. 版本检查提示 "XX commits behind"

**现象**：Dashboard 显示 "⚠ 121 commits behind — run hermes update to update"

**原因**：Dashboard 检查的是官方仓库版本，而非你的 Fork 版本

**解决**：禁用版本检查提示
```bash
# 创建永久缓存（behind=0 表示"最新"）
echo '{"ts": 9999999999, "behind": 0, "rev": null}' > ~/.hermes/.update_check
```

**说明**：
- 这是 Fork 用户的正常现象，本地版本可能已是最新
- 设置后 Dashboard 不再显示"落后"提示
- 缓存文件：`~/.hermes/.update_check`

## 功能特性

| 功能 | 说明 |
|------|------|
| **Config** | 可视化编辑 `config.yaml` |
| **API Keys** | 管理 provider 密钥 |
| **Sessions** | 浏览和管理会话 |
| **Plugins** | 启用/禁用插件 |
| **Chat** | 内嵌 TUI 聊天界面（需 `--tui` 参数） |

## 后台运行

使用 `terminal(background=true)` 启动后台进程：

```python
from hermes_tools import terminal

# 启动后台进程
terminal(
    command="cd ~/.hermes/hermes-agent && source .venv/bin/activate && python -m hermes_cli.main dashboard --no-open --tui",
    background=True,
    notify_on_complete=False
)

# 验证启动
terminal("sleep 5 && curl -s http://127.0.0.1:9119/ | head -5")
```

## 停止服务

```bash
# 方法 1：使用内置命令
hermes dashboard --stop

# 方法 2：手动查找并杀进程
lsof -i :9119 | grep LISTEN | awk '{print $2}' | xargs kill

# 方法 3：通过 Hermes 进程管理
# 使用 process action=kill session_id=<session_id>
```

## 最佳实践

1. **保守式更新后验证**：
   - 更新后立即运行 `npm run build` 验证前端
   - 如果有 TypeScript 错误，优先恢复上游版本

2. **Chat 功能**：
   - 需要 `ptyprocess` 依赖
   - 使用 `--tui` 参数启用

3. **版本检查**：
   - Fork 用户建议禁用提示（避免误导）
   - 本地版本以 `git log` 为准

4. **安全性**：
   - 默认绑定 127.0.0.1（仅本机访问）
   - `--insecure` 参数允许网络访问，但会暴露 API keys

## 相关文件

| 文件 | 说明 |
|------|------|
| `hermes_cli/web_server.py` | 后端服务（FastAPI） |
| `web/` | 前端源码（Vite + React） |
| `hermes_cli/web_dist/` | 前端构建产物 |
| `~/.hermes/.update_check` | 版本检查缓存 |

## 参考链接

- 官方文档：https://hermes-agent.nousresearch.com/docs/
- Dashboard 功能：https://hermes-agent.nousresearch.com/docs/dashboard
