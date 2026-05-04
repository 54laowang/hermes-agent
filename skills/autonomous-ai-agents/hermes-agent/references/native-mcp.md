---
name: native-mcp
description: |
  内置 MCP (Model Context Protocol) 客户端，连接外部 MCP 服务器，发现其工具并注册为原生 Hermes Agent 工具。支持 stdio 和 HTTP 传输，带自动重连、安全过滤和零配置工具注入。
  
  Use when: MCP, Model Context Protocol, MCP服务器, MCP client, 插件系统, 工具集成, MCP配置.
  
  Do NOT use for:
  - 创建 MCP 服务器（用 MCP SDK）
  - HTTP API 调用（用 web tools）
  - 其他协议（如 gRPC、REST）
  - 临时 MCP 调用（用 mcporter）
version: 1.2.0
author: Hermes Agent
license: MIT
keywords:
  - MCP
  - Model Context Protocol
  - MCP服务器
  - MCP client
  - 插件系统
  - 工具集成
triggers:
  - MCP
  - Model Context Protocol
  - MCP服务器
  - MCP client
  - 插件系统
  - 工具集成
metadata:
  hermes:
    tags: [MCP, Tools, Integrations]
    related_skills: [mcporter]
  changelog:
    - version: 1.1.0
      date: 2026-05-02
      changes:
        - 新增：版本兼容性矩阵
        - 新增：边界条件与限制说明
        - 新增：生产环境部署清单
        - 新增：自动诊断脚本
        - 新增：故障排查决策树
        - 增强：异常处理场景覆盖
        - 增强：性能调优建议
        - 增强：安全审计清单
---

# Native MCP Client

Hermes Agent has a built-in MCP client that connects to MCP servers at startup, discovers their tools, and makes them available as first-class tools the agent can call directly. No bridge CLI needed -- tools from MCP servers appear alongside built-in tools like `terminal`, `read_file`, etc.

## When to Use

Use this whenever you want to:
- Connect to MCP servers and use their tools from within Hermes Agent
- Add external capabilities (filesystem access, GitHub, databases, APIs) via MCP
- Run local stdio-based MCP servers (npx, uvx, or any command)
- Connect to remote HTTP/StreamableHTTP MCP servers
- Have MCP tools auto-discovered and available in every conversation

For ad-hoc, one-off MCP tool calls from the terminal without configuring anything, see the `mcporter` skill instead.

---

## ⚡ Quick Start

```bash
# 1. 安装依赖
pip install mcp

# 2. 配置服务器
cat >> ~/.hermes/config.yaml << 'EOF'
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
EOF

# 3. 重启 Hermes
hermes restart

# 4. 验证连接
hermes mcp status
```

---

## 📋 Prerequisites

### Required Dependencies

| 依赖 | 版本要求 | 用途 | 安装命令 |
|------|---------|------|---------|
| **Python** | ≥ 3.8 | 运行时环境 | 系统包管理器 |
| **mcp** | ≥ 1.0.0 | MCP SDK | `pip install mcp` |
| **Node.js** | ≥ 16.0.0 | npx 服务器 | `brew install node` / `apt install nodejs` |
| **uv** | ≥ 0.1.0 | uvx 服务器 | `pip install uv` / `brew install uv` |

### Version Compatibility Matrix

| mcp SDK | Python | HTTP Support | Sampling | Notes |
|---------|--------|--------------|----------|-------|
| 1.0.x | 3.8+ | ❌ | ❌ | 基础功能 |
| 1.1.x | 3.8+ | ✅ | ❌ | 支持 HTTP 传输 |
| 1.2.x | 3.9+ | ✅ | ✅ | 完整功能 |
| 1.3.x | 3.9+ | ✅ | ✅ | 推荐版本 |

### Check Your Environment

```bash
# 一键检查脚本
cat << 'SCRIPT' | bash
#!/bin/bash
echo "=== MCP 环境检查 ==="
echo -n "Python: " && python3 --version 2>/dev/null || echo "❌ 未安装"
echo -n "mcp SDK: " && python3 -c "import mcp; print(mcp.__version__)" 2>/dev/null || echo "❌ 未安装"
echo -n "Node.js: " && node --version 2>/dev/null || echo "❌ 未安装 (可选)"
echo -n "uv: " && uv --version 2>/dev/null || echo "❌ 未安装 (可选)"
echo -n "Hermes config: " && test -f ~/.hermes/config.yaml && echo "✅ 存在" || echo "❌ 不存在"
echo -n "MCP servers: " && grep -q "mcp_servers:" ~/.hermes/config.yaml 2>/dev/null && echo "✅ 已配置" || echo "❌ 未配置"
SCRIPT
```

---

## 📖 Configuration Reference

### Stdio Transport (command + args)

```yaml
mcp_servers:
  server_name:
    command: "npx"             # (required) executable to run
    args: ["-y", "pkg-name"]   # (optional) command arguments, default: []
    env:                       # (optional) environment variables for the subprocess
      SOME_API_KEY: "value"
    timeout: 120               # (optional) per-tool-call timeout in seconds, default: 120
    connect_timeout: 60        # (optional) initial connection timeout in seconds, default: 60
    sampling:                  # (optional) sampling config
      enabled: true            # default: true
      model: "gemini-3-flash"  # model override
      max_tokens_cap: 4096     # max tokens per request
```

### HTTP Transport (url)

```yaml
mcp_servers:
  server_name:
    url: "https://my-server.example.com/mcp"   # (required) server URL
    headers:                                     # (optional) HTTP headers
      Authorization: "Bearer sk-..."
    timeout: 180               # (optional) per-tool-call timeout in seconds, default: 120
    connect_timeout: 60        # (optional) initial connection timeout in seconds, default: 60
```

### All Config Options

| Option            | Type   | Default | Description                                       |
|-------------------|--------|---------|---------------------------------------------------|
| `command`         | string | --      | Executable to run (stdio transport, required)     |
| `args`            | list   | `[]`    | Arguments passed to the command                   |
| `env`             | dict   | `{}`    | Extra environment variables for the subprocess    |
| `url`             | string | --      | Server URL (HTTP transport, required)             |
| `headers`         | dict   | `{}`    | HTTP headers sent with every request              |
| `timeout`         | int    | `120`   | Per-tool-call timeout in seconds                  |
| `connect_timeout` | int    | `60`    | Timeout for initial connection and discovery      |
| `sampling.enabled`| bool   | `true`  | Enable sampling capability                        |
| `sampling.model`  | string | --      | Override model for sampling requests              |
| `sampling.max_tokens_cap` | int | `4096` | Max tokens per sampling request          |

**⚠️ Constraint**: A server config must have either `command` (stdio) or `url` (HTTP), not both.

---

## 🚧 Boundary Conditions & Limits

### Connection Limits

| 资源 | 限制 | 说明 |
|------|------|------|
| **最大服务器数** | 无硬限制 | 受系统资源约束（建议 ≤ 20） |
| **每服务器最大工具数** | 无硬限制 | 受内存约束（建议 ≤ 100） |
| **并发工具调用** | 受限于事件循环 | 默认单线程处理 |
| **连接重试次数** | 5 次 | 指数退避（1s → 60s cap） |
| **请求超时范围** | 1-3600s | `timeout` 配置 |

### Resource Limits

| 资源 | 限制 | 处理方式 |
|------|------|---------|
| **工具参数大小** | ~10MB | 超过会被截断或拒绝 |
| **响应体大小** | ~100MB | 流式读取，超过会记录警告 |
| **子进程内存** | 继承系统限制 | 可通过 `env` 设置 `PYTHONHASHSEED` 等 |
| **日志文件大小** | 10MB/文件 | 自动轮转，最多保留 5 个 |

### Timeout Behaviors

```yaml
# 超时配置决策树
timeout: <seconds>
  ├─ 1-30s: 快速操作（读取小文件、简单查询）
  ├─ 30-120s: 常规操作（默认值，适合大多数场景）
  ├─ 120-300s: 长时间操作（批量处理、复杂分析）
  └─ 300-3600s: 超长操作（大数据集处理，谨慎使用）
```

---

## 🔧 How It Works

### Startup Discovery

When Hermes Agent starts, `discover_mcp_tools()` is called during tool initialization:

1. Reads `mcp_servers` from `~/.hermes/config.yaml`
2. For each server, spawns a connection in a dedicated background event loop
3. Initializes the MCP session and calls `list_tools()` to discover available tools
4. Registers each tool in the Hermes tool registry

### Tool Naming Convention

MCP tools are registered with the naming pattern:

```
mcp_{server_name}_{tool_name}
```

Hyphens and dots in names are replaced with underscores for LLM API compatibility.

**Examples**:
- Server `filesystem`, tool `read_file` → `mcp_filesystem_read_file`
- Server `github`, tool `list-issues` → `mcp_github_list_issues`
- Server `my-api`, tool `fetch.data` → `mcp_my_api_fetch_data`

### Auto-Injection

After discovery, MCP tools are automatically injected into all `hermes-*` platform toolsets (CLI, Discord, Telegram, etc.). This means MCP tools are available in every conversation without any additional configuration.

### Connection Lifecycle

- Each server runs as a long-lived asyncio Task in a background daemon thread
- Connections persist for the lifetime of the agent process
- **Automatic Reconnection**: Exponential backoff (1s, 2s, 4s, 8s, 16s, capped at 60s)
- **Max Retries**: 5 attempts before giving up
- On agent shutdown, all connections are gracefully closed

### Idempotency

`discover_mcp_tools()` is idempotent -- calling it multiple times only connects to servers that aren't already connected. Failed servers are retried on subsequent calls.

---

## 🔄 Transport Types

### Decision Tree: stdio vs HTTP

```
选择传输类型:
├─ 服务器在本地？
│  ├─ 是 → stdio (性能更好，无网络开销)
│  └─ 否 → HTTP (远程服务器)
├─ 需要隔离环境？
│  ├─ 是 → stdio (独立子进程)
│  └─ 否 → HTTP (共享进程)
├─ 需要持久连接？
│  ├─ 是 → stdio (长期运行)
│  └─ 否 → HTTP (按需连接)
└─ 安全要求高？
   ├─ 是 → HTTP + TLS + 认证
   └─ 否 → stdio (本地信任)
```

### Stdio Transport

The most common transport. Hermes launches the MCP server as a subprocess and communicates over stdin/stdout.

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

**Process Inheritance**: The subprocess inherits a **filtered** environment (see Security section below) plus any variables you specify in `env`.

### HTTP / StreamableHTTP Transport

For remote or shared MCP servers. Requires the `mcp` package to include HTTP client support (`mcp.client.streamable_http`).

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer sk-..."
```

**Compatibility Check**: If HTTP support is not available in your installed `mcp` version, the server will fail with an ImportError and other servers will continue normally.

---

## 🛡️ Security

### Environment Variable Filtering

For stdio servers, Hermes does NOT pass your full shell environment to MCP subprocesses. Only safe baseline variables are inherited:

**✅ Safe Baseline Variables**:
- `PATH`, `HOME`, `USER`, `LANG`, `LC_ALL`, `TERM`, `SHELL`, `TMPDIR`
- Any `XDG_*` variables

**❌ Excluded Variables** (unless explicitly added):
- API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.)
- Tokens (`GITHUB_TOKEN`, `GITLAB_TOKEN`, etc.)
- Secrets (`AWS_SECRET_ACCESS_KEY`, `DATABASE_URL`, etc.)
- Any custom credentials

**Example**:
```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      # Only this token is passed to the subprocess
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."
```

### Credential Stripping in Error Messages

If an MCP tool call fails, any credential-like patterns in the error message are automatically redacted before being shown to the LLM. This covers:

- GitHub PATs (`ghp_...`, `gho_...`, `ghu_...`, `ghs_...`, `ghr_...`)
- OpenAI-style keys (`sk-...`)
- Bearer tokens (`Bearer ...`)
- Generic patterns: `token=***`, `key=***`, `API_KEY=***`, `password=***`, `secret=***`

### Security Audit Checklist

Run this before deploying to production:

```bash
#!/bin/bash
# MCP 安全审计脚本

echo "=== MCP 安全审计 ==="

# 1. 检查配置文件权限
if [ -f ~/.hermes/config.yaml ]; then
    perms=$(stat -f "%Lp" ~/.hermes/config.yaml 2>/dev/null || stat -c "%a" ~/.hermes/config.yaml)
    if [ "$perms" -gt 600 ]; then
        echo "❌ 配置文件权限过于宽松: $perms (应为 600)"
        echo "   修复: chmod 600 ~/.hermes/config.yaml"
    else
        echo "✅ 配置文件权限正确: $perms"
    fi
fi

# 2. 检查敏感信息
if grep -E "(password|secret|token|key).*:" ~/.hermes/config.yaml 2>/dev/null | grep -v "GITHUB_PERSONAL_ACCESS_TOKEN" | grep -v "#" | head -5; then
    echo "⚠️  发现可能的明文敏感信息，建议使用环境变量"
fi

# 3. 检查 HTTP 服务器
if grep -q "url:" ~/.hermes/config.yaml 2>/dev/null; then
    if grep "url:" ~/.hermes/config.yaml | grep -qv "https://"; then
        echo "⚠️  发现 HTTP (非 HTTPS) 服务器，数据传输未加密"
    else
        echo "✅ 所有 HTTP 服务器使用 HTTPS"
    fi
fi

# 4. 检查环境变量泄露
if grep -q "env:" ~/.hermes/config.yaml 2>/dev/null; then
    env_count=$(grep -A 10 "env:" ~/.hermes/config.yaml | grep -c "  [A-Z_]*:")
    echo "ℹ️  已配置 $env_count 个环境变量传递给 MCP 服务器"
fi

echo "=== 审计完成 ==="
```

---

## 🔍 Troubleshooting

### Diagnostic Decision Tree

```
问题: MCP 工具不可用
├─ 步骤1: 检查 mcp 包
│  ├─ python3 -c "import mcp" 失败？
│  │  └─ 解决: pip install mcp
│  └─ 成功 → 步骤2
│
├─ 步骤2: 检查配置
│  ├─ grep "mcp_servers:" ~/.hermes/config.yaml 失败？
│  │  └─ 解决: 添加 mcp_servers 配置
│  └─ 存在 → 步骤3
│
├─ 步骤3: 检查服务器命令
│  ├─ which npx 失败？ → 解决: brew install node
│  ├─ which uvx 失败？ → 解决: pip install uv
│  └─ 存在 → 步骤4
│
├─ 步骤4: 检查启动日志
│  ├─ hermes logs | grep -i mcp
│  └─ 发现错误 → 查看下方错误代码表
│
└─ 步骤5: 运行诊断脚本
   └─ hermes mcp diagnose
```

### Error Code Reference

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `MCP SDK not available` | `mcp` 包未安装 | `pip install mcp` |
| `No MCP servers configured` | 配置文件无 `mcp_servers` 键 | 添加服务器配置 |
| `Failed to connect to MCP server 'X'` | 连接失败 | 见下方详细排查 |
| `Command not found: npx` | Node.js 未安装 | `brew install node` (macOS) / `apt install nodejs` (Linux) |
| `Command not found: uvx` | uv 未安装 | `pip install uv` |
| `HTTP transport not available` | mcp 版本过旧 | `pip install --upgrade mcp` |
| `Connection timeout` | 服务器启动慢 | 增加 `connect_timeout` |
| `Tool call timeout` | 工具执行慢 | 增加 `timeout` |
| `Permission denied` | 权限不足 | `chmod +x <command>` 或检查文件权限 |
| `Address already in use` | 端口冲突 | 修改服务器配置或关闭冲突进程 |
| `TLS/SSL error` | 证书问题 | 检查系统证书或更新 CA 证书 |
| `Out of memory` | 内存不足 | 关闭其他进程或增加 swap |

### Detailed Troubleshooting

#### "Failed to connect to MCP server 'X'"

**Common Causes**:

1. **Command not found**
   ```bash
   # 检查命令是否存在
   which npx || echo "npx 未安装"
   which uvx || echo "uvx 未安装"
   
   # 解决方案
   brew install node  # macOS
   apt install nodejs # Linux
   pip install uv     # Python uv
   ```

2. **Package not found** (npx servers)
   ```yaml
   # 错误示例
   args: ["@modelcontextprotocol/server-github"]  # 缺少 -y
   
   # 正确示例
   args: ["-y", "@modelcontextprotocol/server-github"]  # -y 自动安装
   ```

3. **Timeout**
   ```yaml
   # 增加超时时间
   connect_timeout: 120  # 默认 60s
   timeout: 300          # 默认 120s
   ```

4. **Port conflict** (HTTP servers)
   ```bash
   # 检查端口占用
   lsof -i :8080         # macOS/Linux
   netstat -tunlp | grep 8080  # Linux
   
   # 解决方案：修改服务器配置或关闭冲突进程
   ```

#### "MCP server 'X' requires HTTP transport but mcp.client.streamable_http is not available"

**Cause**: Your `mcp` package version doesn't include HTTP client support.

**Solution**:
```bash
pip install --upgrade mcp
# 验证
python3 -c "from mcp.client.streamable_http import streamablehttpclient; print('✅ HTTP 支持')"
```

#### "Tools not appearing"

**Diagnostic Steps**:

1. **Check configuration key**
   ```bash
   grep "mcp_servers:" ~/.hermes/config.yaml
   # ❌ 错误: mcp:, servers:, mcp-servers:
   # ✅ 正确: mcp_servers:
   ```

2. **Check YAML indentation**
   ```bash
   # 验证 YAML 语法
   python3 -c "import yaml; yaml.safe_load(open('$HOME/.hermes/config.yaml'))"
   ```

3. **Check startup logs**
   ```bash
   hermes logs | grep -i "mcp\|server"
   ```

4. **Verify tool names**
   ```bash
   # 工具命名格式: mcp_{server}_{tool}
   hermes tools list | grep "mcp_"
   ```

#### "Connection keeps dropping"

**Analysis**: The client retries up to 5 times with exponential backoff (1s, 2s, 4s, 8s, 16s, capped at 60s). If the server is fundamentally unreachable, it gives up after 5 attempts.

**Diagnostic Steps**:

1. **Check server process**
   ```bash
   ps aux | grep <server-command>
   ```

2. **Check network connectivity** (HTTP servers)
   ```bash
   curl -v <server-url>
   ```

3. **Check server logs**
   ```bash
   # 如果服务器有日志输出
   hermes logs | grep -A 20 "MCP server 'X'"
   ```

4. **Check resource limits**
   ```bash
   # 检查文件描述符限制
   ulimit -n
   
   # 检查进程数限制
   ulimit -u
   ```

---

## 🚀 Production Deployment Checklist

### Pre-Deployment

- [ ] **环境检查**: 运行 `hermes mcp doctor` 确认所有依赖已安装
- [ ] **配置验证**: `python3 -c "import yaml; yaml.safe_load(open('$HOME/.hermes/config.yaml'))"`
- [ ] **安全审计**: 运行安全审计脚本（见上方）
- [ ] **性能测试**: 使用预期负载测试 MCP 服务器
- [ ] **监控配置**: 设置日志监控和告警

### Configuration

- [ ] **超时配置**: 根据实际操作调整 `timeout` 和 `connect_timeout`
- [ ] **重试策略**: 评估是否需要调整默认重试次数（需修改代码）
- [ ] **资源限制**: 设置合理的进程资源限制（CPU、内存）
- [ ] **日志级别**: 生产环境设置为 `WARNING` 或 `ERROR`
- [ ] **备份配置**: 定期备份 `~/.hermes/config.yaml`

### Security

- [ ] **凭证管理**: 使用环境变量而非配置文件存储敏感信息
- [ ] **文件权限**: `chmod 600 ~/.hermes/config.yaml`
- [ ] **HTTPS**: 所有 HTTP 服务器使用 HTTPS
- [ ] **访问控制**: 限制 MCP 服务器的网络访问范围
- [ ] **审计日志**: 启用 sampling 审计日志

### Monitoring

- [ ] **连接状态**: 监控 MCP 服务器连接状态
- [ ] **错误率**: 监控工具调用失败率
- [ ] **延迟**: 监控工具调用延迟
- [ ] **资源使用**: 监控内存、CPU、文件描述符使用

### Maintenance

- [ ] **定期更新**: 定期更新 `mcp` 包和 MCP 服务器
- [ ] **日志轮转**: 确保日志文件自动轮转
- [ ] **备份恢复**: 定期测试配置恢复流程

---

## 📊 Performance Tuning

### Connection Optimization

```yaml
# 针对高延迟服务器
mcp_servers:
  remote_api:
    url: "https://remote-server.com/mcp"
    timeout: 300           # 增加超时
    connect_timeout: 120   # 增加连接超时
```

### Resource Optimization

```bash
# 增加文件描述符限制（系统级）
ulimit -n 65536

# 增加进程数限制（系统级）
ulimit -u 4096
```

### Concurrency Optimization

MCP 工具调用默认在单线程事件循环中处理。如果需要更高的并发：

1. **使用多个 MCP 服务器实例**（负载分散）
2. **调整工具超时**（避免阻塞）
3. **监控事件循环延迟**（使用 `asyncio` 诊断工具）

### Memory Optimization

```yaml
# 限制单个工具调用的内存使用（通过环境变量）
mcp_servers:
  my_server:
    command: "python3"
    args: ["my_mcp_server.py"]
    env:
      PYTHONHASHSEED: "0"
      # 如果服务器支持内存限制
      MAX_MEMORY_MB: "512"
```

---

## 📝 Examples

### Time Server (uvx)

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

**Tools**: `mcp_time_get_current_time`

### Filesystem Server (npx)

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/documents"]
    timeout: 30
```

**Tools**: `mcp_filesystem_read_file`, `mcp_filesystem_write_file`, `mcp_filesystem_list_directory`

### GitHub Server with Authentication

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xx...xxxx"
    timeout: 60
```

**Tools**: `mcp_github_list_issues`, `mcp_github_create_pull_request`, etc.

### Remote HTTP Server

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.mycompany.com/v1/mcp"
    headers:
      Authorization: "Bearer sk-xxx...xxxx"
      X-Team-Id: "engineering"
    timeout: 180
    connect_timeout: 30
```

### Multiple Servers

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]

  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]

  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xx...xxxx"

  company_api:
    url: "https://mcp.internal.company.com/mcp"
    headers:
      Authorization: "Bearer sk-xxx...xxxx"
    timeout: 300
```

**Note**: All tools from all servers are registered and available simultaneously. Each server's tools are prefixed with its name to avoid collisions.

---

## 🔄 Sampling (Server-Initiated LLM Requests)

Hermes supports MCP's `sampling/createMessage` capability — MCP servers can request LLM completions through the agent during tool execution. This enables agent-in-the-loop workflows (data analysis, content generation, decision-making).

### Configuration

Sampling is **enabled by default**. Configure per server:

```yaml
mcp_servers:
  my_server:
    command: "npx"
    args: ["-y", "my-mcp-server"]
    sampling:
      enabled: true           # default: true
      model: "gemini-3-flash" # model override (optional)
      max_tokens_cap: 4096    # max tokens per request
      timeout: 30             # LLM call timeout (seconds)
      max_rpm: 10             # max requests per minute
      allowed_models: []      # model whitelist (empty = all)
      max_tool_rounds: 5      # tool loop limit (0 = disable)
      log_level: "info"       # audit verbosity
```

### Safety Considerations

- Servers can include `tools` in sampling requests for multi-turn tool-augmented workflows
- The `max_tool_rounds` config prevents infinite tool loops
- Per-server audit metrics (requests, errors, tokens, tool use count) are tracked via `get_mcp_status()`
- **Disable sampling for untrusted servers** with `sampling: { enabled: false }`

---

## 🛠️ Advanced Topics

### Custom MCP Server Development

To create your own MCP server:

```python
# my_mcp_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("my-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="hello",
            description="Say hello",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "hello":
        return [TextContent(type="text", text="Hello from MCP!")]
    raise ValueError(f"Unknown tool: {name}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run())
```

**Configuration**:
```yaml
mcp_servers:
  my_server:
    command: "python3"
    args: ["/path/to/my_mcp_server.py"]
```

### Health Checks

```bash
# 检查所有 MCP 服务器状态
hermes mcp status

# 检查特定服务器
hermes mcp status <server_name>

# 运行诊断
hermes mcp diagnose
```

### Graceful Restart

```bash
# 重启所有 MCP 连接（不重启 Hermes）
hermes mcp restart

# 重启特定服务器
hermes mcp restart <server_name>
```

---

## 📚 Notes

- MCP tools are called synchronously from the agent's perspective but run asynchronously on a dedicated background event loop
- Tool results are returned as JSON with either `{"result": "..."}` or `{"error": "..."}`
- The native MCP client is independent of `mcporter` — you can use both simultaneously
- Server connections are persistent and shared across all conversations in the same agent process
- **Adding or removing servers requires restarting the agent** (no hot-reload currently)
- MCP servers are isolated in separate processes — a crash in one server doesn't affect others

---

## 🔗 Related Resources

- [MCP Specification](https://modelcontextprotocol.io)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [Hermes Agent Documentation](https://hermes-agent.nousresearch.com/docs)
- `mcporter` skill: Ad-hoc MCP tool calls without configuration

---

## ⚠️ Known Gotchas

### 连接问题

- **MCP 服务器启动失败**: 命令不正确
  ```yaml
  # config.yaml 配置
  mcp_servers:
    filesystem:
      command: "npx"  # ❌ 可能找不到
      args: ["-y", "@modelcontextprotocol/server-filesystem"]
  
  # ✅ 正确: 使用完整路径
  command: "/usr/bin/npx"
  ```

- **stdio 传输阻塞**: 缓冲区满
  ```python
  # 确保服务器及时 flush
  # MCP 服务器代码
  sys.stdout.flush()  # 每次输出后刷新
  ```

### 工具注册问题

- **工具名称冲突**: 多个服务器提供同名工具
  ```yaml
  # config.yaml 使用前缀
  mcp_servers:
    server1:
      tool_prefix: "s1_"  # 工具名变为 s1_tool_name
  ```

- **工具参数不兼容**: Schema 不匹配
  ```python
  # 检查工具 Schema
  tool_schema = mcp_client.get_tool_schema("tool_name")
  print(tool_schema)
  
  # 调整参数格式
  ```

### 性能问题

- **启动慢**: 多个 MCP 服务器串行启动
  ```yaml
  # 并行启动
  mcp_config:
    parallel_startup: true
    startup_timeout: 30  # 秒
  ```

- **工具调用慢**: 网络延迟
  ```python
  # 使用缓存
  # 或切换到本地 stdio 服务器
  ```
