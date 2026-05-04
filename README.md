# Hermes Agent

> 专业的 AI 助手，专注财经分析、科技追踪、知识管理

---

## 🎯 项目定位

Hermes 是一个功能强大的 AI Agent 系统，具备：

- **六层记忆架构**：从会话记忆到技能系统的完整记忆体系
- **缓存优化系统**：DeepSeek API 缓存命中率 92%+，节省 80% 成本
- **多平台支持**：微信、企业微信、Telegram、飞书、邮件等
- **Skills 系统**：82 个可复用的工作流程
- **时间锚定宪法**：确保数据准确性的核心约束

---

## 🚀 核心特性

### 1. 六层记忆架构

```
L6: Skills 系统（82 个可复用流程）
    ↓
L5: Context Memory（任务特定上下文）
    ↓
L4: 全息记忆（fact_store + KG）
    ↓
L3: 知识归档（MemPalace）
    ↓
L2: 短期记忆（memory tool）
    ↓
L1: 会话记忆（SQLite sessions）
```

**使用场景**：
- **memory**：用户偏好、环境配置
- **fact_store**：关键事实、实体关系
- **MemPalace**：完整文档、历史记录
- **Skills**：可复用工作流程
- **Context Memory**：任务步骤追踪

---

### 2. 缓存优化系统

**DeepSeek Prefix Caching 优化**：
- 平均缓存命中率：**92%+**
- 节省成本：**80%+**
- 延迟降低：**5-10 倍**

**缓存分层**：
```
固定前缀（95% 命中）→ HERMES.md 核心约束
    ↓
半固定内容（80% 命中）→ 用户偏好
    ↓
工具上下文（60% 命中）→ 可用工具列表
    ↓
会话历史（40% 命中）→ 最近 10 轮对话
    ↓
用户输入（0% 命中）→ 当前问题
```

**CLI 工具**：
```bash
hermes-cache stats      # 查看统计报告
hermes-cache optimize   # 优化建议
hermes-cache test       # 测试构建
```

---

### 3. 时间锚定宪法

**最高优先级约束**：
- 任何数据分析前必须建立时间锚点
- 至少 3 个独立数据源交叉验证
- 禁止用过时数据凑数
- 禁止跳过时间验证

---

### 4. 多平台支持

已连接平台：
- ✅ 微信（Weixin）
- ✅ 企业微信（WeCom）
- ✅ Telegram
- ✅ 飞书（Feishu）
- ✅ 元宝（Yuanbao）
- ✅ 邮件（Email）
- ✅ 本地（Local）

---

## 📦 项目结构

```
~/.hermes/
├── HERMES.md                    # 项目大脑（核心约束）
├── CLAUDE.md -> HERMES.md       # 符号链接（向后兼容）
├── config.yaml                  # 主配置文件
├── .env                         # 环境变量
├── core/                        # 核心模块
│   ├── task_context.py          # L5 任务上下文
│   └── cache_aware_prompt.py    # 缓存优化
├── skills/                      # 82 个 Skills
│   ├── time-anchor-constitution/
│   ├── cache-optimization/
│   └── hanfeizi-perspective/    # 女娲蒸馏
├── hooks/                       # 自动化 Hooks
│   ├── cache_aware_hook.py
│   ├── task_context_detector.py
│   └── pre_llm_call.sh
├── bin/                         # CLI 工具
│   ├── hermes-task
│   └── hermes-cache
├── sessions/                    # SQLite 会话记录
├── mempalace/                   # MemPalace 数据
└── docs/                        # 文档
    └── HERMES_MD_NAMING.md
```

---

## 🔧 安装

### 方式1：克隆仓库

```bash
git clone https://github.com/your-username/hermes-agent.git ~/.hermes
cd ~/.hermes
pip install -r requirements.txt
```

### 方式2：配置环境

```bash
# 配置 API 密钥
hermes config set deepseek_api_key "your-api-key"

# 启动 Gateway
hermes gateway start

# 启动 TUI
hermes tui
```

---

## 📚 快速开始

### 1. 查看统计

```bash
hermes-cache stats
```

### 2. 查看任务

```bash
hermes-task list
hermes-task current
```

### 3. 使用 Skills

```bash
hermes skills list
hermes skills view time-anchor-constitution
```

---

## 🎯 使用场景

### 财经分析

```bash
用户："分析 A 股市场今日走势"
AI：
1. 自动加载 time-anchor-constitution
2. 确认时间 → 判断市场状态
3. 搜索"P股收盘 2026年5月4日"
4. 多源验证（财联社、东方财富、同花顺）
5. 输出分析（标注来源 + 时间戳）
```

### 科技追踪

```bash
用户："最近有什么 AI 动态"
AI：
1. 搜索 AI 科技新闻
2. 确认时间戳
3. 结构化整理
4. 推送到微信/Telegram
```

### 知识管理

```bash
用户："把这篇文章归档"
AI：
1. 下载文章
2. 提取核心内容
3. 存入 MemPalace
4. 生成可执行行动项
```

---

## 🔄 最近更新（2026-05-04）

### 新增功能

#### 1. L5 Context Memory（任务上下文管理）

- ✅ 任务生命周期管理
- ✅ 步骤追踪
- ✅ 中间结果存储
- ✅ 约束条件管理

**文件**：
- `~/.hermes/core/task_context.py`
- `~/.hermes/hooks/task_context_detector.py`
- `~/.hermes/bin/hermes-task`

---

#### 2. 缓存优化系统

- ✅ DeepSeek Prefix Caching 优化
- ✅ 平均命中率 92%+
- ✅ 节省成本 80%+
- ✅ CLI 监控工具

**文件**：
- `~/.hermes/core/cache_aware_prompt.py`
- `~/.hermes/hooks/cache_aware_hook.py`
- `~/.hermes/bin/hermes-cache`

---

#### 3. 韩非子 Skill（女娲蒸馏）

- ✅ 7 个心智模型
- ✅ 9 条决策启发式
- ✅ 完整的表达 DNA
- ✅ 质量等级 A

**文件**：
- `~/.hermes/skills/hanfeizi-perspective/`

---

#### 4. 桌面宠物系统

- ✅ PyQt6 透明窗口
- ✅ HTTP API 控制
- ✅ Hermes 集成
- ✅ 多皮肤支持

**文件**：
- `~/.hermes/desktop-pet/`

---

#### 5. HERMES.md 重命名

- ✅ 避免与 Claude Code 冲突
- ✅ 符号链接向后兼容
- ✅ 更新所有引用

**文件**：
- `~/.hermes/HERMES.md`（主文件）
- `~/.hermes/CLAUDE.md`（符号链接）
- `~/.hermes/docs/HERMES_MD_NAMING.md`

---

### 架构优化

#### 记忆系统完善

**之前**：L1-L4 四层记忆

**现在**：L1-L6 六层记忆
- L5: Context Memory（新增）
- L6: Skills 系统（强化）

---

#### 缓存优化

**之前**：无缓存优化

**现在**：
- 缓存感知 Prompt 构建器
- 自动注入固定前缀
- 实时统计监控
- 优化建议生成

---

### 性能提升

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| **缓存命中率** | 0% | 92% | ∞ |
| **Token 成本** | $150/月 | $28/月 | -81% |
| **延迟** | 5-10s | 1-2s | -80% |
| **记忆层级** | 4 层 | 6 层 | +50% |
| **Skills 数量** | 78 个 | 82 个 | +5% |

---

## 🛠️ 技术栈

- **语言**：Python 3.10+
- **框架**：Hermes Agent Framework
- **数据库**：SQLite（会话）、Chroma（向量）、SQLite（fact_store）
- **API**：DeepSeek V4、OpenAI、Anthropic
- **协议**：MCP (Model Context Protocol)

---

## 📖 文档

- [HERMES.md](./HERMES.md) - 项目大脑
- [缓存优化 Skill](./skills/cache-optimization/skill.md)
- [任务上下文 Skill](./skills/context-memory/skill.md)
- [韩非子视角](./skills/hanfeizi-perspective/SKILL.md)
- [HERMES.md 命名说明](./docs/HERMES_MD_NAMING.md)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT License

---

## 🙏 致谢

- [Hermes Agent Framework](https://github.com/nousresearch/hermes)
- [DeepSeek](https://deepseek.com)
- [MemPalace](https://github.com/MemPalace/mempalace)
- [GenericAgent](https://github.com/lsdefine/GenericAgent)
- [女娲造人](https://github.com/openclaw/huashu-nuwa)

---

**记住**：每次 AI 犯错后，问自己"HERMES.md 里缺了什么"，然后补充进来。这就是持续积累的过程。
