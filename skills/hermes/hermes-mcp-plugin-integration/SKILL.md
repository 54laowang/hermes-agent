---
name: hermes-mcp-plugin-integration
description: Hermes MCP 插件集成标准流程 - 从发现、安装到配置的完整工作流。涵盖 PyPI 包安装、MCP 服务器配置、环境变量管理、文档生成。
author: Hermes
tags: [hermes, mcp, plugin, integration, workflow]
---

# Hermes MCP 插件集成标准流程

将第三方 AI 工具作为 MCP (Model Context Protocol) 插件集成到 Hermes Agent 的标准化工作流。

## 适用场景

- ✅ 发现新的 AI 工具/平台，希望集成到 Hermes
- ✅ 安装 PyPI 包并配置为 MCP 服务器
- ✅ 解决 MCP 插件权限、环境变量、路径问题
- ✅ 生成集成文档供后续参考

---

## Phase 1: 发现与评估

### 1.1 识别插件价值

**评估维度：**

| 维度 | 评估要点 |
|------|---------|
| **功能价值** | 是否提供 Hermes 缺失的能力？ |
| **维护状态** | 是否活跃维护？最近更新时间？ |
| **依赖冲突** | 是否与 Hermes 现有依赖冲突？ |
| **MCP 支持** | 是否原生支持 MCP？ |
| **文档质量** | 文档是否清晰完整？ |

**决策矩阵：**

```
有 MCP 支持 + 功能互补 + 活跃维护 = ✅ 集成
无 MCP 支持 + 功能重要 = ⚠️ 考虑自建 MCP 封装
依赖冲突 = ❌ 放弃或使用虚拟环境隔离
```

### 1.2 检查依赖兼容性

```bash
# 进入 Hermes 虚拟环境
cd ~/.hermes/hermes-agent
source .venv/bin/activate

# 检查包依赖（dry-run）
pip install <package-name> --dry-run

# 如果有冲突警告，评估影响
```

---

## Phase 2: 安装与配置

### 2.1 安装包

```bash
# 确保 Hermes 虚拟环境激活
source ~/.hermes/hermes-agent/.venv/bin/activate

# 安装包
pip install <package-name>

# 验证安装
which <cli-command>
<cli-command> --version
```

### 2.2 查找 MCP 可执行文件

```bash
# 通常 MCP 服务器命名为 <package>-mcp 或 mcp-<package>
which <package>-mcp

# 或查看包文档
<package> --help | grep -i mcp
```

### 2.3 初始化配置

**方法 A: 交互式初始化（如果支持）**

```bash
<package> init
# 按提示选择 LLM provider、输入 API key 等
```

**方法 B: 手动创建配置文件**

```bash
# 创建配置目录
mkdir -p ~/.<package>/

# 创建配置文件
cat > ~/.<package>/.env << 'EOF'
# LLM Provider 配置（建议与 Hermes 一致）
LANGCHAIN_PROVIDER=deepseek
LANGCHAIN_MODEL_NAME=deepseek-chat
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 其他配置（根据包文档）
# ...
EOF
```

**💡 关键建议**：
- 使用与 Hermes 主模型一致的 LLM provider
- 使用环境变量引用 `${DEEPSEEK_API_KEY}` 而非硬编码
- 配置文件位置通常为 `~/.<package>/.env`

---

## Phase 3: Hermes 集成

### 3.1 添加 MCP 服务器配置

编辑 `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  # ... 现有服务器 ...
  
  <package-name>:
    command: /Users/me/.hermes/hermes-agent/.venv/bin/<package>-mcp
    transport: stdio
    enabled: true
    connect_timeout: 60
    timeout: 300
    env:
      LANGCHAIN_PROVIDER: deepseek
      LANGCHAIN_MODEL_NAME: deepseek-chat
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      DEEPSEEK_BASE_URL: https://api.deepseek.com/v1
      # 其他必需的环境变量
```

**配置要点：**

| 字段 | 说明 | 建议 |
|------|------|------|
| `command` | MCP 可执行文件绝对路径 | 使用 Hermes 虚拟环境中的路径 |
| `transport` | 传输协议 | 通常为 `stdio` |
| `enabled` | 是否启用 | `true` |
| `connect_timeout` | 连接超时（秒） | 60s（首次初始化可能较慢） |
| `timeout` | 操作超时（秒） | 300s（处理大量数据时需要） |
| `env` | 环境变量 | 继承 Hermes 的 LLM 配置 |

### 3.2 重启 Hermes Gateway

```bash
# 重启 Gateway（必须）
hermes gateway restart

# 或重启 CLI 会话
hermes
```

### 3.3 验证集成

```bash
# 检查 MCP 服务器状态
hermes mcp status

# 查看可用工具
hermes tools --mcp
```

**在对话中测试：**

```
用户: 用 <package> 分析一下 <示例任务>

Hermes: [应自动调用 MCP 工具]
        正在加载 <package> 工具...
        执行分析...
        ...
```

---

## Phase 4: 文档生成

### 4.1 创建集成文档

**标准文档结构：**

```markdown
# <Package> MCP 集成到 Hermes Agent

**集成时间**: YYYY-MM-DD HH:MM
**集成方式**: MCP (Model Context Protocol) 插件

---

## ✅ 集成完成

### 📦 安装信息

| 项目 | 详情 |
|------|------|
| **包名** | `<package-name>` |
| **版本** | vX.Y.Z |
| **安装位置** | `/Users/me/.hermes/hermes-agent/.venv/` |
| **可执行文件** | `<cli-command>`, `<package>-mcp` |

### 🔧 配置位置

**Hermes 配置**: `~/.hermes/config.yaml`
**<Package> 配置**: `~/.<package>/.env`

---

## 🚀 使用方法

### 方法 1: 直接在 Hermes 中使用（推荐）

[示例对话和使用场景]

### 方法 2: 独立运行

```bash
# 启动 CLI
<cli-command>

# 启动 Web UI（如果有）
<cli-command> serve --port 8899
```

---

## 🛠️ 可用工具

[工具列表和功能说明]

---

## 💡 使用示例

[3-5 个典型示例]

---

## 🔧 高级配置

[自定义配置选项]

---

## 🚨 注意事项

[已知问题和解决方案]

---

## 📚 学习资源

[官方文档、GitHub 等]
```

### 4.2 保存文档位置

```bash
# 保存到 Hermes 文档目录
/Users/me/.hermes/<PACKAGE>-INTEGRATION.md
```

---

## Phase 5: 常见问题处理

### 问题 1: MCP 工具未加载

**症状**: Hermes 无法识别新工具

**排查步骤**：

```bash
# 1. 检查 MCP 服务器状态
hermes mcp status

# 2. 验证可执行文件
which <package>-mcp
<package>-mcp --help

# 3. 测试 MCP 服务器
<package>-mcp --transport stdio

# 4. 检查配置语法
cat ~/.hermes/config.yaml | grep -A 15 "<package-name>:"
```

**常见原因**：
- ❌ 未重启 Gateway
- ❌ 可执行文件路径错误
- ❌ 环境变量未设置
- ❌ **YAML 缩进错误（最常见）**

**⚠️ YAML 缩进错误详解（2026-05-01 实战案例）**

**错误示例**：
```yaml
mcp_servers:
  mempalace:
    command: /path/to/mempalace-mcp
    ...
  wechat-download:
    command: /path/to/wechat-download
    ...
vibe-trading:  # ❌ 错误：与 mcp_servers 同级
  command: /path/to/vibe-trading-mcp
  ...
```

**正确示例**：
```yaml
mcp_servers:
  mempalace:
    command: /path/to/mempalace-mcp
    ...
  wechat-download:
    command: /path/to/wechat-download
    ...
  vibe-trading:  # ✅ 正确：嵌套在 mcp_servers 下
    command: /path/to/vibe-trading-mcp
    ...
```

**验证方法**：
```bash
# 检查 YAML 格式
python3 -c "import yaml; config = yaml.safe_load(open('$HOME/.hermes/config.yaml')); print(config.get('mcp_servers', {}).keys())"

# 应该输出包含所有 MCP 服务器名称
# dict_keys(['mempalace', 'wechat-download', 'vibe-trading'])
```

**诊断脚本**：
```bash
# 创建快速诊断脚本
cat > /tmp/diagnose-mcp.sh << 'EOF'
#!/bin/bash
echo "=== MCP 配置诊断 ==="

# 1. 检查可执行文件
echo -e "\n1. 检查 vibe-trading-mcp 可执行文件:"
which vibe-trading-mcp

# 2. 检查环境变量
echo -e "\n2. 检查 DEEPSEEK_API_KEY:"
if [ -z "$DEEPSEEK_API_KEY" ]; then
  echo "❌ DEEPSEEK_API_KEY 未设置"
else
  echo "✅ DEEPSEEK_API_KEY 已设置（长度: ${#DEEPSEEK_API_KEY}）"
fi

# 3. 检查 YAML 配置
echo -e "\n3. 检查 YAML 配置:"
python3 -c "
import yaml
with open('$HOME/.hermes/config.yaml') as f:
    config = yaml.safe_load(f)
servers = config.get('mcp_servers', {})
if 'vibe-trading' in servers:
    print('✅ vibe-trading 在 mcp_servers 下')
    print(f\"   command: {servers['vibe-trading'].get('command')}\")
else:
    print('❌ vibe-trading 不在 mcp_servers 下')
"

# 4. 测试 MCP 启动
echo -e "\n4. 测试 MCP 服务器启动:"
timeout 3 vibe-trading-mcp --transport stdio &
PID=$!
sleep 2
if ps -p $PID > /dev/null; then
  echo "✅ MCP 服务器启动成功 (PID: $PID)"
  kill $PID
else
  echo "❌ MCP 服务器启动失败"
fi
EOF

chmod +x /tmp/diagnose-mcp.sh
/tmp/diagnose-mcp.sh
```

### 问题 2: 环境变量未生效

**症状**: "API key not found" 错误

**解决方法**：

```bash
# 方法 A: 在 config.yaml 中硬编码（不推荐）
env:
  DEEPSEEK_API_KEY: sk-xxx

# 方法 B: 在 shell 中设置（临时）
export DEEPSEEK_API_KEY=sk-xxx
hermes

# 方法 C: 在 .env 文件中设置（推荐）
echo 'export DEEPSEEK_API_KEY=sk-xxx' >> ~/.zshrc
source ~/.zshrc
```

### 问题 3: 超时错误

**症状**: "Timeout after 300s"

**解决方法**：

```yaml
# 增加超时时间
mcp_servers:
  <package-name>:
    timeout: 600  # 10 分钟
```

### 问题 4: 依赖冲突

**症状**: pip install 报错依赖冲突

**解决方法**：

```bash
# 方法 A: 升级冲突包（如果兼容）
pip install --upgrade <conflicting-package>

# 方法 B: 使用独立虚拟环境（隔离方案）
python -m venv ~/.<package>-venv
source ~/.<package>-venv/bin/activate
pip install <package-name>

# 修改 config.yaml 使用独立环境
mcp_servers:
  <package-name>:
    command: ~/.<package>-venv/bin/<package>-mcp
```

### 问题 5: MCP 连接成功但工具调用失败（ClosedResourceError）

**症状**：
- `hermes mcp test <name>` 成功
- 实际工具调用失败：`ClosedResourceError: `
- 反复出现相同错误

**根因**：
- stdio MCP 服务器在每次调用时启动新进程
- `hermes mcp test` 在新进程中运行 → 成功
- 当前 CLI 会话的 MCP 客户端连接损坏 → 失败
- 可能原因：会话长时间运行、多次 Gateway 重启、进程冲突

**诊断步骤**：

```bash
# 1. 检查是否有多个 Hermes 进程
ps aux | grep -i hermes | grep -v grep

# 2. 测试 MCP 服务器本身是否正常
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | /path/to/<package>-mcp --transport stdio

# 3. 在新会话中测试
hermes chat -q "调用 <mcp-tool> 测试"
```

**解决方法**：

```bash
# 方法 A: 在新会话中操作（推荐，快速）
hermes chat -q "调用 mempalace_add_drawer 归档内容..."

# 方法 B: 退出当前会话重新进入
/exit
hermes

# 方法 C: 重启所有 Hermes 进程（彻底）
hermes gateway stop
pkill -f 'hermes mcp serve'
hermes gateway start
```

**⚠️ 注意**：当前会话损坏时，无法通过 `mcp_reconnect` 恢复，必须使用新会话。

**预防措施**：
- 定期重启长时间运行的 CLI 会话
- 避免在 Gateway 运行时频繁重启 MCP 配置
- 使用 `hermes mcp serve` 统一管理（如需要长期运行）

**实战案例**（2026-05-03）：
- **问题**：MemPalace MCP 在当前会话失败，但 `hermes mcp test mempalace` 成功
- **诊断**：发现 `ClosedResourceError`，确认是当前会话连接损坏
- **解决**：通过新会话 `hermes chat -q "..."` 成功归档
- **经验**：stdio MCP 的进程生命周期与 CLI 会话绑定，长时间运行后可能损坏

---

## 最佳实践

### 1. LLM Provider 一致性

**✅ 推荐**: 与 Hermes 使用相同的 provider
```yaml
env:
  LANGCHAIN_PROVIDER: deepseek
  LANGCHAIN_MODEL_NAME: deepseek-chat
```

**原因**：
- 统一计费和监控
- 避免多模型切换成本
- 简化配置管理

### 2. 环境变量管理

**✅ 推荐**: 使用环境变量引用
```yaml
env:
  DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
```

**❌ 避免**: 硬编码敏感信息
```yaml
env:
  DEEPSEEK_API_KEY: sk-xxx  # 不安全
```

### 3. 超时设置策略

| 任务类型 | 推荐超时 |
|---------|---------|
| 快速查询 | 60s |
| 数据分析 | 300s (5分钟) |
| 复杂回测 | 600s (10分钟) |
| 长时间训练 | 1800s (30分钟) |

### 4. 文档维护

- ✅ 记录集成日期和版本
- ✅ 保存典型使用示例
- ✅ 记录遇到的问题和解决方案
- ✅ 定期更新（版本升级时）

---

## 实战案例

### 案例 1: Vibe-Trading 金融分析平台集成（2026-05-01）

**背景**：
- 项目：Vibe-Trading (HKUDS 出品)
- 功能：多智能体金融分析平台
- MCP 支持：原生支持

**集成过程**：

```bash
# 1. 安装
pip install vibe-trading-ai

# 2. 验证
which vibe-trading-mcp
vibe-trading --version

# 3. 配置
mkdir -p ~/.vibe-trading
cat > ~/.vibe-trading/.env << 'EOF'
LANGCHAIN_PROVIDER=deepseek
LANGCHAIN_MODEL_NAME=deepseek-chat
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
EOF

# 4. 添加到 Hermes
# 编辑 ~/.hermes/config.yaml
# 添加 vibe-trading MCP 服务器配置

# 5. 重启 Gateway
hermes gateway restart

# 6. 测试
用户: 用 Vibe-Trading 分析比亚迪
Hermes: [成功调用 MCP 工具]
```

**集成结果**：
- ✅ 72 个金融技能可用
- ✅ 29 个团队预设可用
- ✅ 27 个专业工具可用
- ✅ 6 个数据源集成

**关键经验**：
- 🔑 使用与 Hermes 一致的 LLM provider
- 🔑 配置合理的超时时间（金融分析通常 5-10 分钟）
- 🔑 生成完整集成文档供后续参考
- 🔑 测试基本功能确保正常工作

---

## 检查清单

完成集成后，验证以下项目：

- [ ] 包已安装到 Hermes 虚拟环境
- [ ] MCP 可执行文件路径正确
- [ ] 配置文件已创建
- [ ] Hermes config.yaml 已更新
- [ ] Gateway 已重启
- [ ] MCP 工具在 Hermes 中可见
- [ ] 基本功能测试通过
- [ ] 集成文档已生成

---

## 相关技能

- `hermes-agent` - Hermes Agent 完整使用指南
- `hermes-local-mod-protection-safe-update` - Fork 仓库维护
- `native-mcp` - MCP 协议详解

---

## 参考资源

- [MCP 规范](https://modelcontextprotocol.io/)
- [Hermes MCP 文档](https://hermes-agent.nousresearch.com/docs/mcp)
- [Hermes Agent 技能系统](https://hermes-agent.nousresearch.com/docs/skills)

### 实战案例

- **Vibe-Trading 集成** (`references/vibe-trading-integration-20260501.md`) - 完整的金融分析平台集成记录，包含安装步骤、配置细节、工具列表、使用示例、故障排查
