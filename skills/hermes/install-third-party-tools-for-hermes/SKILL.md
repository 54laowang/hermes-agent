---
     2|name: install-third-party-tools-for-hermes
     3|description: |
  为 Hermes Agent 发现、评估和安装第三方 Skill/MCP 工具。当用户问"有没有其他开源方案""下载安装某个工具""给 Hermes 添加 XX 能力"时使用。覆盖 GitHub 搜索评估、MCP/Skill 选择决策、配置写入和安装验证全流程。
  
  Use when: 安装工具, install tools, 第三方工具, third party tools, Skill发现, MCP插件, 工具评估.
  
  Do NOT use for:
  - Hermes 配置（用 hermes-agent）、创建 Skills（用 skill_manage）、编码任务（用 coding skills）
     4|
keywords:
  - 安装工具
  - install tools
  - 第三方工具
  - third party tools
  - Skill发现
triggers:
  - 安装工具
  - install tools
  - 第三方工具
  - third party tools
  - Skill发现
---

# 为 Hermes 安装第三方工具

系统化流程：发现 → 评估 → 选择 → 安装 → 验证

## 1. 发现阶段

### GitHub 搜索策略

```bash
# 按关键词搜索
curl -s "https://api.github.com/search/repositories?q=wechat+article+download+export&sort=stars&order=desc&per_page=15" | jq -r '.items[] | "\(.stargazers_count)|\(.full_name)|\(.description)|\(.html_url)"'

# 查看特定仓库
curl -s "https://api.github.com/repos/{owner}/{repo}" | jq -r '.stargazers_count, .description, .html_url'
```

### 评估维度

| 维度 | 权重 | 检查项 |
|------|------|--------|
| Stars | 30% | >1000 优选，>5000 优秀 |
| 活跃度 | 25% | 最近 commit 时间、issue 响应 |
| 功能完整 | 25% | README 描述、支持格式、API 设计 |
| 集成方式 | 20% | MCP / Skill / CLI / 桌面应用 |

## 2. 集成方式选择

### 方式一：MCP 服务器（推荐用于 API 服务）

**适用场景**：远程服务、无需本地运行、跨平台

**配置格式**（写入 `~/.hermes/config.yaml`）：
```yaml
mcp_servers:
  tool-name:
    type: streamableHttp
    url: https://api.example.com/mcp
    enabled: true
    connect_timeout: 30
    timeout: 60
```

**验证方法**：
```bash
# 测试连接
curl -s -X POST "https://api.example.com/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","id":1}' | jq .

# 列出工具
curl -s -X POST "https://api.example.com/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":2}' | jq -r '.result.tools[].name'
```

### 方式二：Skill 文件（推荐用于本地工具）

**适用场景**：需要本地环境、复杂配置、多文件支持

**安装步骤**：
```bash
# 1. 克隆仓库
cd ~/.hermes
git clone https://github.com/xxx/tool.git temp_tool

# 2. 复制 Skill
mkdir -p ~/.hermes/skills/skill-name
cp -r temp_tool/skills/xxx/* ~/.hermes/skills/skill-name/

# 3. 清理临时文件
rm -rf temp_tool
```

### 方式二-A：使用 `npx skills add` 自动安装（推荐）

**适用场景**：Skills.sh 生态的技能，GitHub 仓库支持 `npx skills add` 安装

**标准流程**：

```bash
# 一键安装（自动处理依赖、配置、验证）
npx skills add owner/skill-repo

# 示例：安装达尔文.skill
npx skills add alchaincyf/darwin-skill

# 跳过确认直接安装
npx skills add owner/skill-repo --yes
```

**安装位置**：
- 自动安装到 `.agents/skills/` 目录（当前项目）
- 符号链接到其他 Agent 平台（Claude Code、OpenClaw 等）
- 不需要手动克隆、复制、配置

**输出示例**：
```
✓ ./.agents/skills/darwin-skill
  universal: Codex, Gemini CLI, OpenCode, Amp, Antigravity +8 more
  symlinked: Claude Code, OpenClaw, Qwen Code, Trae, Trae CN
```

**验证安装**：
```bash
# 查看安装的 Skill
ls .agents/skills/skill-name/

# 检查 SKILL.md 格式
cat .agents/skills/skill-name/SKILL.md | head -10
```

**优点**：
- ✅ 自动化程度高（一键安装）
- ✅ 跨平台支持（Universal + Symlinked）
- ✅ 自动安全扫描（Safe, 0 alerts）
- ✅ 无需手动清理临时文件

**注意事项**：
1. 需要网络连接（从 GitHub 克隆）
2. 安装位置是当前项目的 `.agents/skills/`，不是 `~/.hermes/skills/`
3. 如需全局使用，可以手动复制到 `~/.hermes/skills/`

### 方式二-B：从 GitHub Skills 仓库手动安装（传统方式）

**适用场景**：
- 不支持 `npx skills add` 的仓库
- 需要自定义安装位置
- 需要修改 Skill 内容

**标准流程**：

```bash
# 1. 克隆到临时目录
cd /tmp
git clone https://github.com/owner/skills-repo.git

# 2. 查看仓库结构
ls -la skills-repo/
# 常见结构：
# - 根目录直接是 Skill 文件夹（skill-name/SKILL.md）
# - 有 skills/ 子目录
# - 有多个 Skill 文件夹

# 3. 复制 Skill 到 Hermes
# 如果根目录直接是 Skill：
cp -r /tmp/skills-repo/skill-name ~/.hermes/skills/

# 如果有 skills/ 子目录：
cp -r /tmp/skills-repo/skills/* ~/.hermes/skills/

# 4. 验证安装
hermes skills list | grep skill-name

# 5. 清理临时文件
rm -rf /tmp/skills-repo
```

**验证检查清单**：
- [ ] Skill 目录存在：`ls .agents/skills/skill-name/` 或 `ls ~/.hermes/skills/skill-name/`
- [ ] SKILL.md 文件存在：`ls .agents/skills/skill-name/SKILL.md`
- [ ] Skill 已识别：`hermes skills list | grep skill-name`（Hermes）或直接测试（Skills.sh）
- [ ] 文件格式正确：frontmatter 包含 name 和 description

**常见仓库结构**：

| 结构 | 说明 | 安装方式 |\n|------|------|----------|\n| Skills.sh 生态 | 支持 `npx skills add` | `npx skills add owner/repo --yes` |\n| `repo/skill-name/SKILL.md` | 根目录直接是 Skill | `cp -r repo/skill-name ~/.hermes/skills/` |\n| `repo/skills/skill-name/` | 有 skills 子目录 | `cp -r repo/skills/* ~/.hermes/skills/` |\n| `repo/category/skill-name/` | 按分类组织 | `cp -r repo/category/skill-name ~/.hermes/skills/category/` |

**注意事项**：
1. **先查看 README**：了解 Skill 功能、依赖、配置要求
2. **检查 SKILL.md 格式**：必须有 YAML frontmatter（name, description）
3. **一次性安装多个**：如果仓库有多个 Skill，可以全部复制
4. **Prompt 文件处理**：有些仓库还有 prompts/ 目录，是纯文本 prompt，不是 Skill
5. **依赖安装**：如果 Skill 包含 Node.js 脚本，需要安装依赖：
   ```bash
   cd ~/.hermes/skills/skill-name
   npm init -y
   npm install dependency-name
   ```
6. **超时处理**：测试脚本时如遇到 `timeout` 命令不存在，使用 Perl 替代：
   ```bash
   perl -e 'alarm shift; exec @ARGV' 10 node scripts/test.js "args"
   ```

### 方式三：桌面应用（需要 GUI 交互）

**适用场景**：需要用户手动操作、OAuth 登录、浏览器交互

**处理方式**：
1. 提供下载链接
2. 说明安装步骤
3. 如果支持 MCP，配置本地 MCP 服务（`http://127.0.0.1:端口/mcp`）

## 3. 配置写入

### 读取现有配置

```bash
# 查看 MCP 配置
grep -A 10 "mcp_servers:" ~/.hermes/config.yaml

# 或使用 Read 工具
```

### 添加新配置

使用 Patch 工具在 `mcp_servers:` 部分添加新条目：

```yaml
mcp_servers:
  existing-server:
    ...
  new-tool:  # 新增
    type: streamableHttp
    url: https://api.new-tool.com/mcp
    enabled: true
    connect_timeout: 30
    timeout: 60
```

## 4. 验证流程

### 步骤清单

- [ ] MCP 连接测试（curl initialize）
- [ ] 工具列表获取（tools/list）
- [ ] Skill 文件检查（ls ~/.hermes/skills/xxx/）
- [ ] 功能测试（实际调用一个工具）

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 连接超时 | 网络问题/服务不可用 | 检查 URL、重试、换网络 |
| 工具列表为空 | API 变更/权限问题 | 查看 GitHub issues |
| Skill 不生效 | 文件格式错误 | 检查 SKILL.md frontmatter |

## 5. 记录安装信息

### 写入 memory

```
新安装工具：{tool-name}
- 来源：{GitHub URL}
- Stars：{数量}
- 功能：{描述}
- 集成方式：MCP/Skill/桌面应用
- 配置位置：~/.hermes/config.yaml 或 ~/.hermes/skills/
- 验证状态：✅/❌
```

## 模板：安装报告

```markdown
## ✅ 安装完成！

### 📦 安装内容

| 组件 | 状态 | 说明 |
|------|------|------|
| MCP 服务器 | ✅ | `{url}` |
| Skill 文件 | ✅ | `~/.hermes/skills/{name}/` |
| 连接测试 | ✅ | 服务器名: `{server_name}` |

### 🛠️ 可用工具

1. **`tool-1`** - 功能描述
2. **`tool-2`** - 功能描述

### 📝 使用方式

直接说："下载这篇微信文章：https://..."
```

## Skill 生命周期管理

### 归档不常用的 Skill 分类

**适用场景**：Skill 数量过多、用户想精简系统、保留但不常使用

**操作流程**：

```bash
# 1. 创建归档目录
mkdir -p ~/.hermes/skills/_archived/{source-name}

# 2. 统计各分类角色数量（Python 脚本）
from pathlib import Path
skills_dir = Path.home() / ".hermes" / "skills"
stats = {}
for cat in skills_dir.iterdir():
    if cat.is_dir() and not cat.name.startswith("_"):
        count = len([d for d in cat.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])
        stats[cat.name] = count

# 按数量排序输出
for cat, count in sorted(stats.items(), key=lambda x: -x[1]):
    print(f"{cat:25s} {count:3d} 个角色")

# 3. 移动不常用的分类到归档目录
import shutil
archive_categories = ["marketing", "testing", "design"]  # 根据统计结果选择
archive_dir = skills_dir / "_archived" / "source-name"
archive_dir.mkdir(parents=True, exist_ok=True)

for cat in archive_categories:
    src = skills_dir / cat
    if src.exists():
        shutil.move(str(src), str(archive_dir / cat))
        print(f"✅ 已归档: {cat}")
```

**示例**：agency-agents-zh 归档（2026-04-29）
- 保留：finance（18）、engineering（33）等常用分类
- 归档：marketing（35）、specialized（45）等 15 个分类
- 结果：保留 51 个角色，归档 155 个角色
- 归档位置：`~/.hermes/skills/_archived/agency-agents-zh/`

### 重新启用归档的 Skill

```bash
# 恢复单个分类
mv ~/.hermes/skills/_archived/agency-agents-zh/marketing ~/.hermes/skills/

# 批量恢复多个分类
for cat in marketing sales; do
    mv ~/.hermes/skills/_archived/agency-agents-zh/$cat ~/.hermes/skills/
done
```

**注意**：
- Hermes 没有"启用/禁用"开关，所有在 `~/.hermes/skills/` 目录下的 Skill 都会被自动加载
- 归档是"移出目录"，恢复是"移回目录"
- 归档后需要重启 Hermes Gateway 才能生效（`hermes restart`）

## 参考文档

- [达尔文.skill 完整指南](references/darwin-skill-guide.md) - Skills.sh 生态的自主进化 Skill 系统，包含核心原则、8维度评估体系、优化流程等
- [Hindsight 部署案例](references/hindsight-deployment-example.md) - Docker 容器化工具集成完整案例，包含 OpenRouter 适配、三层记忆系统架构、部署流程等
- [Camofox Browser 集成案例](references/camofox-browser-integration.md) - AI Agent 反检测浏览器服务集成，解决登录态保持、风控绕过、稳定状态管理等核心问题

## 陷阱与注意事项

1. **不要重复安装**：先用 `skills_list` 检查是否已存在
2. **API 限流**：GitHub API 60次/小时（未认证），必要时用浏览器访问
3. **配置格式**：YAML 缩进必须正确，使用 Patch 而非手动拼接
4. **清理临时文件**：克隆的仓库安装后要删除，避免占用空间
5. **Cloudflare 验证**：部分网站有安全验证，使用 `browser_navigate` + `sleep 5` 等待通过
6. **技能格式差异**：外部技能可能不是标准 SKILL.md 格式，需要手动转换为 Hermes 格式
7. **安全警告**：涉及真实资金/敏感操作的工具（如加密货币钱包），必须：
   - 明确告知用户风险
   - 建议先在测试环境验证
   - 提供安全配置选项（如限制额度、白名单等）
   - 记录到 MemPalace 作为参考案例，而非直接安装
8. **测试脚本导入**：动态导入 SkillRouter 时必须使用 `importlib.util`，避免模块路径问题：
   ```python
   import importlib.util
   spec = importlib.util.spec_from_file_location("skill_router", hooks_dir / "skill-router.py")
   skill_router = importlib.util.module_from_spec(spec)
   spec.loader.exec_module(skill_router)
   SkillRouter = skill_router.SkillRouter
   ```
9. **Smart Skill Router 更新**：patch `skill-router.py` 时，新领域必须添加在 `SKILL_ROUTES` 字典的**最后一个领域之后、结束大括号之前**
10. **双重记忆保存**：集成完成后必须同时保存到 MemPalace（详细报告）和 fact_store（摘要），确保跨会话可查询

## 特殊场景处理

### 场景一：容器化工具集成（Docker 部署）

**适用场景**：
- 需要 Docker 容器运行的第三方服务
- 有独立 API 和 UI 的自托管工具
- 需要持久化数据存储的服务

**标准流程**：

#### 1. 环境检查

```bash
# 检查 Docker
docker --version

# 检查端口占用
lsof -i:8888  # API 端口
lsof -i:9999  # UI 端口
```

#### 2. 克隆仓库

```bash
cd ~
git clone https://github.com/owner/tool.git
cd tool
```

#### 3. 配置文件准备

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置（重点是 API Key）
vim .env
```

**关键配置项**：
- `LLM_PROVIDER`: 兼容 OpenAI API 的 provider
- `LLM_API_KEY`: API 密钥
- `LLM_MODEL`: 模型选择
- `LLM_BASE_URL`: API 端点（如 OpenRouter）

#### 4. 创建启动脚本

**start-tool.sh**（后台模式）：

```bash
#!/bin/bash
# 检查环境变量
if [ -z "$API_KEY" ]; then
    echo "❌ 未找到 API_KEY 环境变量"
    exit 1
fi

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    exit 1
fi

# 检查是否已运行
if docker ps | grep -q tool-name; then
    echo "✅ Tool 已在运行"
    exit 0
fi

# 创建数据目录
mkdir -p ~/.tool-data

# 后台启动
docker run -d --pull always \
    -p 8888:8888 \
    -p 9999:9999 \
    --name tool-name \
    --restart unless-stopped \
    -e API_KEY=$API_KEY \
    -v $HOME/.tool-data:/home/tool/.data \
    ghcr.io/owner/tool:latest

echo "✅ Tool 已启动"
echo "API: http://localhost:8888"
echo "UI:  http://localhost:9999"
```

#### 5. 集成到 Hermes

**安装 Python Client**：

```bash
pip install tool-client -U
```

**配置 Hermes**（`~/.hermes/config.yaml`）：

```yaml
memory:
  extended_memory:
    tool-name:
      enabled: true
      api_url: http://localhost:8888
      collection: hermes-agent
```

**创建 Hook**（`~/.hermes/hooks/tool_integration.py`）：

```python
#!/usr/bin/env python3
"""Tool 集成 Hook"""

import os
import requests

API_URL = os.getenv('TOOL_API_URL', 'http://localhost:8888')

def store_data(content: str, metadata: dict = None):
    """存储数据到 Tool"""
    try:
        response = requests.post(
            f"{API_URL}/v1/store",
            json={'content': content, 'metadata': metadata or {}}
        )
        return response.json()
    except Exception as e:
        print(f"Tool 存储失败: {e}")
        return None

def retrieve_data(query: str, limit: int = 5):
    """从 Tool 检索数据"""
    try:
        response = requests.post(
            f"{API_URL}/v1/search",
            json={'query': query, 'limit': limit}
        )
        return response.json().get('results', [])
    except Exception as e:
        print(f"Tool 检索失败: {e}")
        return []
```

#### 6. 验证集成

```bash
# 测试 API
curl http://localhost:8888/v1/health

# 测试存储
curl -X POST http://localhost:8888/v1/store \
  -H "Content-Type: application/json" \
  -d '{"content": "测试内容"}'

# 测试检索
curl -X POST http://localhost:8888/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "测试"}'
```

#### 7. 管理脚本

**stop-tool.sh**：

```bash
#!/bin/bash
docker stop tool-name
docker rm tool-name
echo "✅ Tool 已停止"
```

**backup-tool.sh**：

```bash
#!/bin/bash
tar -czf tool-backup-$(date +%Y%m%d).tar.gz ~/.tool-data
```

**注意事项**：
1. **端口冲突**：确保端口未被占用，或修改映射
2. **数据持久化**：必须挂载 volume 避免数据丢失
3. **自动重启**：使用 `--restart unless-stopped` 确保服务稳定
4. **API Key 安全**：使用环境变量而非硬编码
5. **OpenRouter 兼容**：很多工具支持 OpenAI API 格式，可使用 OpenRouter

**完整案例**：Hindsight 记忆系统集成（2026-05-02）
- **仓库**：vectorize-io/hindsight
- **部署方式**：Docker 容器
- **API 端口**：8888（API）、9999（UI）
- **LLM Provider**：OpenRouter（兼容 OpenAI API）
- **数据存储**：~/.hindsight-docker
- **集成方式**：Python Client + Hermes Hook
- **参考文档**：`references/hindsight-deployment-example.md`

### 场景二：加密货币钱包/支付工具

**风险评估**：高风险 - 涉及真实资金

**处理流程**：
1. 获取技能定义 → 分析功能范围
2. 评估安全机制 → 私钥管理、权限控制、审计日志
3. **不建议直接安装** → 记录到 MemPalace 作为参考
4. 如用户坚持安装 → 提供安全配置清单 + 限制额度建议

**示例**：FluxA Agent Wallet (Base 链 USDC 钱包)
- ✅ 无需私钥管理（安全）
- ✅ 支持预算管理
- ⚠️ 仍涉及真实资金操作
- 建议：先记录参考，确认安全后再集成

### 场景二：非标准技能格式

**问题**：外部技能可能使用简化格式（如纯 Markdown），缺少 SKILL.md frontmatter

**解决**：
1. 手动创建 SKILL.md，添加 frontmatter
2. 转换安装命令为 Hermes 格式
3. 添加中文文档和使用示例
4. 集成到 Smart Skill Router

### 场景三：完整技能封装与集成（推荐用于复杂技能）

**适用场景**：
- 外部技能功能复杂，需要完整文档化
- 需要创建安装脚本、测试脚本
- 需要集成到 Smart Skill Router
- 用户希望有完整的中文文档和参考文档

**完整封装流程**：

#### 1. 获取技能定义

```bash
# 方式1：直接访问 skill.md URL
curl -s https://example.com/skill.md

# 方式2：从 GitHub 仓库获取
curl -s https://raw.githubusercontent.com/owner/repo/main/skills/skill-name/SKILL.md

# 方式3：浏览器访问（如有 Cloudflare 验证）
browser_navigate https://example.com/skill.md
# 等待 5 秒通过验证
sleep 5
browser_console "document.body.innerText"
```

#### 2. 创建技能目录结构

```bash
# 标准结构
~/.hermes/skills/{category}/{skill-name}/
├── SKILL.md              # 主文档（完整中文版）
├── README.md             # 快速参考指南
├── INTEGRATION_REPORT.md # 集成报告（可选）
├── scripts/
│   ├── install.sh        # 自动安装脚本
│   └── test_integration.py # 集成测试脚本
└── references/           # 官方参考文档
    ├── GUIDE-1.md
    ├── GUIDE-2.md
    └── ...
```

#### 3. 创建 SKILL.md（完整中文文档）

**必需 frontmatter 字段**：

```yaml
---
name: skill-name
description: >-
  技能描述（用于 Smart Skill Router 自动识别）
version: x.x.x
cli_version: package-name@x.x.x  # 如有 CLI
network: Network Name            # 如涉及网络
category: category-name
tags: [tag1, tag2, tag3]
---
```

**必需章节**：

1. 核心特性（功能列表）
2. 快速开始（安装 + 初始化）
3. 能力矩阵（功能对照表）
4. 安全注意事项（如有风险）
5. Hermes 集成特性（触发关键词、关联技能）
6. 参考资料（链接到 references/）

#### 4. 下载参考文档

```bash
# 创建 references 目录
mkdir -p ~/.hermes/skills/{category}/{skill-name}/references

# 下载官方文档
cd ~/.hermes/skills/{category}/{skill-name}/references
curl -sO https://raw.githubusercontent.com/.../GUIDE-1.md
curl -sO https://raw.githubusercontent.com/.../GUIDE-2.md
# ...
```

#### 5. 创建安装脚本

**scripts/install.sh**：

```bash
#!/bin/bash
# 技能名称 安装脚本

set -e

echo "🦄 技能名称 安装脚本"
echo "================================"
echo ""

# 检查依赖
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"

# 安装 CLI（如有）
npm install -g package-name@version

echo ""
echo "✅ 安装完成！"
echo ""
echo "下一步："
echo "1. 运行初始化命令"
echo "2. 查看文档: ~/.hermes/skills/{category}/{skill-name}/SKILL.md"
```

**赋予执行权限**：

```bash
chmod +x ~/.hermes/skills/{category}/{skill-name}/scripts/install.sh
```

#### 6. 创建集成测试脚本

**scripts/test_integration.py**：

```python
#!/usr/bin/env python3
"""
技能名称 集成测试
验证 Smart Skill Router 是否正确识别并加载此技能
"""

import sys
from pathlib import Path

# 动态导入 SkillRouter
hooks_dir = Path.home() / ".hermes" / "hooks"
sys.path.insert(0, str(hooks_dir))

import importlib.util
spec = importlib.util.spec_from_file_location("skill_router", hooks_dir / "skill-router.py")
skill_router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skill_router)

SkillRouter = skill_router.SkillRouter


def test_triggers():
    """测试触发词识别"""
    router = SkillRouter()
    
    test_cases = [
        ("关键词1", ["skill-name"]),
        ("关键词2", ["skill-name"]),
        ("关键词3", ["skill-name"]),
    ]
    
    print("🧪 测试触发词识别\n")
    
    passed = 0
    for message, expected in test_cases:
        recommended = router.recommend_skills(message)
        matched = all(skill in recommended for skill in expected)
        
        status = "✅" if matched else "❌"
        print(f"{status} \"{message}\" → {recommended}")
        
        if matched:
            passed += 1
    
    print(f"\n结果: {passed}/{len(test_cases)} 通过")
    return passed == len(test_cases)


def test_structure():
    """测试文件结构"""
    skill_dir = Path.home() / ".hermes" / "skills" / "{category}" / "{skill-name}"
    
    required_files = [
        "SKILL.md",
        "README.md",
        "scripts/install.sh",
        "scripts/test_integration.py",
    ]
    
    print("\n🧪 测试文件结构\n")
    
    passed = 0
    for file_path in required_files:
        exists = (skill_dir / file_path).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        
        if exists:
            passed += 1
    
    print(f"\n结果: {passed}/{len(required_files)} 存在")
    return passed == len(required_files)


def main():
    results = {
        "触发词识别": test_triggers(),
        "文件结构": test_structure(),
    }
    
    print("\n" + "=" * 60)
    print("📊 最终测试结果")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
    
    if all(results.values()):
        print("\n🎉 所有测试通过！")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

#### 7. 更新 Smart Skill Router

编辑 `~/.hermes/hooks/skill-router.py`，在 `SKILL_ROUTES` 中添加新领域：

```python
SKILL_ROUTES = {
    # ... 现有领域 ...
    
    "new_domain": {
        "triggers": ["关键词1", "关键词2", "关键词3"],
        "skills": {
            "primary": ["skill-name"],
            "secondary": ["backup-skill"],
            "specific": {
                "特定触发词": "specific-skill",
            }
        },
        "priority": 9  # 高优先级
    },
}
```

#### 8. 运行集成测试

```bash
python3 ~/.hermes/skills/{category}/{skill-name}/scripts/test_integration.py
```

**预期输出**：

```
============================================================
🧪 测试触发词识别

✅ "关键词1" → ['skill-name', 'backup-skill']
✅ "关键词2" → ['skill-name', 'backup-skill']
✅ "关键词3" → ['skill-name', 'backup-skill']

结果: 3/3 通过

🧪 测试文件结构

✅ SKILL.md
✅ README.md
✅ scripts/install.sh
✅ scripts/test_integration.py

结果: 4/4 存在

============================================================
📊 最终测试结果
============================================================
✅ 通过 - 触发词识别
✅ 通过 - 文件结构

🎉 所有测试通过！
```

#### 9. 保存到记忆系统

**MemPalace**：

```bash
mcp_mempalace_mempalace_add_drawer \
  --wing "hermes-integration" \
  --room "agent-skills" \
  --content "技能名称 v1.0.0 已成功封装为 Hermes Skill..." \
  --source_file "~/.hermes/skills/{category}/{skill-name}/INTEGRATION_REPORT.md"
```

**fact_store**：

```python
fact_store(
  action="add",
  category="project",
  content="技能名称 v1.0.0 已成功封装为 Hermes Skill，集成到 Smart Skill Router。所有测试通过，文档完整（XXKB），自动加载触发词已配置。",
  tags="skill,integration,hermes"
)
```

#### 10. 创建集成报告

**INTEGRATION_REPORT.md**：

```markdown
# 技能名称 - Hermes Skill 封装完成报告

## ✅ 集成状态

**状态：** 已完成并通过所有测试
**日期：** YYYY-MM-DD
**版本：** 技能名称 vX.X.X

## 📦 已创建文件

- SKILL.md (XXKB)
- README.md (XXKB)
- scripts/install.sh (XXKB)
- scripts/test_integration.py (XXKB)
- references/ (X 个文档，共 XXKB)

**总计：** X 个文件，约 XXKB 文档

## 🧪 测试结果

✅ 触发词识别 - X/X 通过
✅ 文件结构 - X/X 存在
✅ 元数据检查 - X/X 通过

## 🔧 Smart Skill Router 集成

新增 "{domain}" 领域，优先级 X

触发关键词：关键词1、关键词2、关键词3

## 📚 核心功能

1. 功能1
2. 功能2
3. ...

## 🚀 快速开始

```bash
~/.hermes/skills/{category}/{skill-name}/scripts/install.sh
```

## ⚠️ 安全提示

（如有风险，列出安全注意事项）

## 🔗 相关链接

- GitHub: ...
- 官方文档: ...
```

#### 11. 验证自动加载

测试 Smart Skill Router 是否正确识别：

```bash
python3 ~/.hermes/hooks/skill-router.py "测试关键词"
```

**预期输出**：

```json
{
  "recommended_skills": ["skill-name"],
  "context": "[Skill Router] 检测到相关领域..."
}
```

**实际验证示例**（FluxA Agent Wallet）：

```bash
# 测试触发词识别
python3 ~/.hermes/hooks/skill-router.py "转账USDC"

# 预期输出：
# {
#   "recommended_skills": ["fluxa-agent-wallet", "engineering-solidity-smart-contract-engineer"],
#   "context": "[Skill Router] 检测到 crypto 领域..."
# }
```

**成功标志**：
- ✅ 所有测试通过（100%）
- ✅ Smart Skill Router 正确识别
- ✅ 文档完整且符合规范
- ✅ 保存到记忆系统
- ✅ 集成报告生成

**示例**：FluxA Agent Wallet 完整封装（已验证 ✅）
- **日期**：2026-04-29
- **文件**：9 个文件，约 58KB 文档
- **测试**：18 项测试 100% 通过
- **集成**：Smart Skill Router 新增 crypto 领域（优先级 9）
- **文档**：完整中文文档 + 5 个参考文档
- **脚本**：install.sh + test_integration.py
- **触发词**：钱包、支付、转账、USDC、Base、x402、ClawPI、龙虾朋友圈等 14 个
- **安全**：涉及真实资金，已添加安全提示
- **状态**：已安装并验证（Agent ID: 4c7299df-b7b8-43d5-83ba-be9e000d7da6）

**关键经验**：
1. ✅ 完整封装流程耗时约 30 分钟（含文档编写、测试验证）
2. ✅ 测试脚本必须动态导入 SkillRouter（避免模块路径问题）
3. ✅ Smart Skill Router 的 patch 需要在 SKILL_ROUTES 字典结束前添加
4. ✅ 安全提示必须在 SKILL.md 中明确标注（涉及真实资金/敏感操作）
5. ✅ 集成报告应保存到 MemPalace 和 fact_store 双重记忆系统

### 场景四：反检测浏览器服务集成（Node.js 服务）

**适用场景**：
- AI Agent 需要访问登录后的网站（知识库、后台系统）
- 网站有严格的风控检测（Cloudflare、Bot 检测）
- 需要长期保持浏览器状态（登录态、Cookie、Profile）

**核心痛点**：
传统无头浏览器（Playwright、Puppeteer）容易被网站识别：
- 指纹特征明显（WebGL、AudioContext、WebRTC）
- 登录态丢失，每次都像新用户
- 触发风控后无法继续操作

**解决方案：Camofox Browser**

**技术特点**：
- 基于 Firefox 分支，底层指纹伪装
- 不是简单改 User-Agent，而是在 JS 读取前伪装浏览器特征
- 提供独立的 Node.js 服务（API 调用，无需 Python 依赖）

**集成流程**：

#### 1. 安装服务

```bash
# 克隆仓库
cd ~/projects
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser

# 安装依赖
npm install

# 启动服务（后台运行）
nohup npm start > ~/logs/camofox.log 2>&1 &

# 验证服务
curl http://localhost:9377/health
# 预期输出: {"status": "ok", "service": "camofox-browser"}
```

#### 2. 配置 Hermes

编辑 `~/.hermes/config.yaml`：

```yaml
browser:
  camofox:
    url: http://localhost:9377
    managed_persistence: true  # 启用登录态持久化
```

#### 3. 核心能力

| 能力 | 说明 | 价值 |
|------|------|------|
| **登录态持久化** | 按 userId 隔离 session | 像长期使用的工作浏览器 |
| **Accessibility Snapshot** | 页面压缩 90% | 模型低成本理解页面 |
| **Stable Element Refs** | `@e1`、`@e2` 元素引用 | 点击稳定，不因 DOM 变化失效 |
| **本地部署** | 所有状态在自己机器 | 敏感登录态不交给第三方 |

#### 4. API 工具

| 工具 | 功能 | 示例 |
|------|------|------|
| `browser_navigate` | 打开网页 | `browser_navigate("https://example.com")` |
| `browser_snapshot` | 读取页面结构 | 返回 accessibility tree（小 90%） |
| `browser_click` | 点击元素 | `browser_click("@e1")` |
| `browser_type` | 输入文本 | `browser_type("@e2", "搜索内容")` |
| `browser_scroll` | 滚动页面 | `browser_scroll("down")` |

#### 5. 典型应用场景

**场景A：访问登录后的资料库**
- 会员站、知识库、课程后台、内部文档系统
- 首次用户扫码授权 → Camofox 保存登录态 → 后续自动使用
- Hermes 整理资料成笔记/文章

**场景B：操作复杂后台**
- 广告后台、电商后台、CRM、数据看板
- 需要连续点击、筛选、下载、翻页
- Camofox 提供稳定身份，Hermes 提供任务编排

**场景C：读取高风控网页**
- 小红书、电商平台、订阅服务
- 案例：小红书评论抓取（未登录只看十几条 → 用户扫码 → Agent 继续操作找第 200 条）

**场景D：配合现有工具**
- `iwencai-integration`: 问财接口登录后查看完整数据
- `grid-trading-monitor`: ETF 监控访问券商网站避免频繁登录

#### 6. 验证集成

```python
import requests

CAMOFOX_URL = "http://localhost:9377"

# 测试打开网页
resp = requests.post(f"{CAMOFOX_URL}/browser_navigate", 
    json={"url": "https://example.com"})
print("状态:", resp.json()["status"])

# 测试获取快照
snapshot = requests.post(f"{CAMOFOX_URL}/browser_snapshot").json()
print("快照大小:", len(snapshot["content"]), "字符")

# 测试元素引用
print("可点击元素:", [e for e in snapshot["elements"] if e["clickable"]])
```

#### 7. 安全注意事项

**✅ 适用场景**：
- 访问自己的账号和后台
- 自动化个人工作流
- 整理个人订阅内容
- 操作授权的业务系统

**❌ 不适用场景**：
- 非法采集数据
- 绕过付费内容
- 攻击网站或服务
- 批量注册账号、刷量刷单

**安全原则**：
1. **本地优先**：敏感登录态不交给第三方
2. **用户授权**：敏感操作需要用户确认
3. **状态隔离**：不同用户使用不同 profile
4. **可观测可关闭**：随时可以停止服务和删除数据

#### 8. 与 web-scraping-suite 的配合

**工具矩阵升级**：

| 工具 | 适用场景 | Camofox 加入后 |
|------|---------|---------------|
| Jina Reader | 普通文章、新闻 | 不变（公开网页） |
| Crawl4AI | 批量整站抓取 | 不变（公开网页） |
| Scrapling | 反爬网站 | 不变（单次抓取） |
| **CamouFox** | 反检测 Python 库 | 不变（代码调用） |
| **Camofox Browser** | **登录态、长期状态** | **新增（服务调用）** |

**决策树更新**：

```
是否需要登录？
 ├─ 是 → 使用 Camofox Browser（长期状态管理）
 └─ 否 → 继续判断

是否有反爬？
 ├─ 是 → 使用 Scrapling
 └─ 否 → 继续判断

单页还是多页？
 ├─ 单页 → Jina Reader
 └─ 多页 → Crawl4AI
```

#### 9. 常见问题

**Q: Camofox 和 CamouFox 有什么区别？**

| 项目 | 类型 | 定位 |
|------|------|------|
| **CamouFox** | Python 库 | 反检测浏览器库，代码调用 |
| **Camofox Browser** | Node.js 服务 | 浏览器服务器，API 调用 |

**Q: 如何处理验证码？**
- 推荐：检测到验证码 → 告知用户 → 用户处理 → Agent 继续
- 不推荐：自动绕过验证码（违反网站条款）

**Q: 登录态能保持多久？**
- 取决于网站 Cookie 有效期（一般 7-30 天）
- 银行/金融可能需要定期重新授权
- 建议：在 Skill 中添加登录态检查逻辑

**完整案例**：Camofox Browser 集成（2026-05-03）
- **仓库**：jo-inc/camofox-browser
- **部署方式**：Node.js 服务（本地运行）
- **API 端口**：http://localhost:9377
- **集成方式**：Hermes config.yaml 配置 + API 调用
- **参考文档**：`references/camofox-browser-integration.md`
- **典型应用**：小红书评论抓取、问财数据获取、券商后台访问

---

## ⚠️ Known Gotchas

### 工具发现问题

- **工具仓库不全**: 未覆盖所有可用工具
  ```bash
  # 多源搜索
  # 1. GitHub: topic:hermes-skill, topic:mcp-server
  # 2. PyPI: 搜索 hermes-*
  # 3. NPM: 搜索 @hermes/*
  # 4. Awesome Lists: awesome-ai-agents
  ```

- **工具质量参差不齐**: 缺少质量评估
  ```python
  # 评估维度
  # 1. GitHub Stars > 100
  # 2. 最近更新 < 6 个月
  # 3. 有文档和示例
  # 4. 有测试覆盖
  # 5. 开源许可证
  ```

### 安装问题

- **依赖冲突**: 工具依赖与 Hermes 冲突
  ```bash
  # 使用虚拟环境
  python3 -m venv ~/.hermes/venv
  source ~/.hermes/venv/bin/activate
  pip install tool-name
  ```

- **权限问题**: 无法写入安装目录
  ```bash
  # 检查权限
  ls -la ~/.hermes/tools
  
  # 修复权限
  chmod -R u+rw ~/.hermes/tools
  ```

### 兼容性问题

- **Hermes 版本不兼容**: 工具需要特定版本
  ```bash
  # 检查 Hermes 版本
  hermes --version
  
  # 查看工具要求
  cat tool/requirements.txt | grep hermes
  ```

- **Python 版本冲突**: 工具需要不同 Python
  ```bash
  # 使用 pyenv 管理多版本
  pyenv install 3.10.13
  pyenv shell 3.10.13
  ```
