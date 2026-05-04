<p align="center">
  <img src="assets/banner.png" alt="Hermes Agent" width="100%">
</p>

# Hermes Agent ☤

<p align="center">
  <a href="https://hermes-agent.nousresearch.com/docs/"><img src="https://img.shields.io/badge/文档-hermes--agent.nousresearch.com-FFD700?style=for-the-badge" alt="Documentation"></a>
  <a href="https://discord.gg/NousResearch"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="https://github.com/NousResearch/hermes-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/许可证-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://nousresearch.com"><img src="https://img.shields.io/badge/由%20Nous%20Research%20构建-blueviolet?style=for-the-badge" alt="Built by Nous Research"></a>
</p>

**由 [Nous Research](https://nousresearch.com) 构建的自进化 AI Agent。** 它是唯一一个内置学习循环的 Agent —— 从经验中创建技能，使用中改进技能，主动保存知识，搜索过往对话，跨会话构建对用户的深度理解。可以在 $5 VPS、GPU 集群或空闲时几乎零成本的无服务器基础设施上运行。不局限于你的笔记本电脑 —— 在云端 VM 工作时从 Telegram 与它对话。

使用任意模型 —— [Nous Portal](https://portal.nousresearch.com)、[OpenRouter](https://openrouter.ai)（200+ 模型）、[NVIDIA NIM](https://build.nvidia.com)（Nemotron）、[小米 MiMo](https://platform.xiaomimimo.com)、[z.ai/GLM](https://z.ai)、[Kimi/Moonshot](https://platform.moonshot.ai)、[MiniMax](https://www.minimax.io)、[Hugging Face](https://huggingface.co)、OpenAI 或你自己的端点。通过 `hermes model` 切换 —— 无需代码更改，无锁定。

<table>
<tr><td><b>真正的终端界面</b></td><td>完整 TUI，支持多行编辑、斜杠命令自动补全、对话历史、中断重定向、流式工具输出。</td></tr>
<tr><td><b>随你所处的平台</b></td><td>Telegram、Discord、Slack、WhatsApp、Signal 和 CLI —— 全部来自单一网关进程。语音备忘录转录、跨平台对话连续性。</td></tr>
<tr><td><b>闭环学习</b></td><td>Agent 管理的记忆与周期性提醒。复杂任务后自主创建技能。技能在使用中自我改进。FTS5 会话搜索与 LLM 摘要实现跨会话召回。<a href="https://github.com/plastic-labs/honcho">Honcho</a> 辩证用户建模。兼容 <a href="https://agentskills.io">agentskills.io</a> 开放标准。</td></tr>
<tr><td><b>定时自动化</b></td><td>内置 cron 调度器，可投递到任意平台。日报、夜间备份、周审计 —— 全部用自然语言编写，无人值守运行。</td></tr>
<tr><td><b>委托与并行化</b></td><td>生成隔离的子 agent 进行并行工作流。编写通过 RPC 调用工具的 Python 脚本，将多步骤流水线压缩为零上下文成本的轮次。</td></tr>
<tr><td><b>随处运行，不只是你的笔记本</b></td><td>六种终端后端 —— local、Docker、SSH、Daytona、Singularity 和 Modal。Daytona 和 Modal 提供无服务器持久化 —— 你的 agent 环境空闲时休眠，按需唤醒，会话间几乎零成本。在 $5 VPS 或 GPU 集群上运行。</td></tr>
<tr><td><b>研究就绪</b></td><td>批量轨迹生成、Atropos RL 环境、轨迹压缩，用于训练下一代工具调用模型。</td></tr>
</table>

---

## 🚀 本 Fork 的增强功能

> **基于上游 `NousResearch/hermes-agent`，本项目新增以下功能：**

### 📊 六层记忆架构

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

### 💰 DeepSeek Prefix Caching 优化

**缓存命中率：92%+**，节省 **80%+ Token 成本**

**优化策略**：
```
固定前缀（95% 命中）→ 系统提示、工具定义
半固定前缀（80% 命中）→ 技能上下文
工具上下文（60% 命中）→ 动态加载的工具
会话历史（40% 命中）→ 压缩后的历史
用户输入（0% 命中）→ 每次不同的输入
```

**相关文件**：
- `~/.hermes/core/cache_aware_prompt.py` — 缓存感知 Prompt 构建器
- `~/.hermes/hooks/cache_aware_hook.py` — Hook 集成
- `~/.hermes/bin/hermes-cache` — CLI 统计工具

### 🧠 L5 Context Memory（任务上下文管理器）

**功能**：
- 任务步骤追踪
- 上下文压缩决策
- 子任务生命周期管理

**相关文件**：
- `~/.hermes/core/task_context.py` — 核心模块
- `~/.hermes/hooks/task_context_detector.py` — Hook 集成
- `~/.hermes/bin/hermes-task` — CLI 工具

### 📚 韩非子 Skill（思维框架蒸馏）

**来源**：《韩非子》55 篇、《史记》等权威史料深度调研

**核心内容**：
- 7 个心智模型
- 9 条决策启发式
- 完整表达风格指南

**路径**：`~/.hermes/skills/hanfeizi-perspective/`

### 🐛 其他增强

| 功能 | 说明 |
|------|------|
| **图片 OCR 工作流** | Tesseract 优先，避免 GLM-5 视觉模型幻觉 |
| **股价智能缓存** | 多数据源自动切换 + 智能缓存管理 |
| **时间锚定宪法** | 任何数据分析前必须先建立时间锚点 |
| **A 股交易日历** | 判断指定日期是否为 A 股交易日 |

---

## 📝 更新日志

### 2026-05-04（重大更新）

**新增**：
- ✨ L5 Context Memory — 任务上下文管理器
- ✨ DeepSeek Prefix Caching 优化 — 92%+ 命中率
- ✨ 韩非子 Skill — 思维框架蒸馏

**改进**：
- 📝 重命名 `CLAUDE.md` → `HERMES.md`（避免与 Claude Code 冲突）
- 🐛 图片 OCR 工作流 — 使用 Tesseract 避免 GLM-5 幻觉

**统计**：
- 📊 35 个文件更改
- 📊 4124 行新增代码
- 📊 6 个新模块

---

## 快速安装

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

支持 Linux、macOS、WSL2 和 Android（通过 Termux）。安装程序会自动处理平台特定的设置。

> **Android / Termux：** 测试过的手动路径已记录在 [Termux 指南](https://hermes-agent.nousresearch.com/docs/getting-started/termux)。在 Termux 上，Hermes 安装精简的 `.[termux]` 扩展，因为完整的 `.[all]` 扩展当前会拉取 Android 不兼容的语音依赖。
>
> **Windows：** 原生 Windows 不受支持。请安装 [WSL2](https://learn.microsoft.com/zh-cn/windows/wsl/install) 并运行上述命令。

安装后：

```bash
source ~/.bashrc    # 重载 shell（或：source ~/.zshrc）
hermes              # 开始对话！
```

---

## 快速开始

```bash
hermes              # 交互式 CLI — 开始对话
hermes model        # 选择你的 LLM 提供商和模型
hermes tools        # 配置启用哪些工具
hermes config set   # 设置单个配置值
hermes gateway      # 启动消息网关（Telegram、Discord 等）
hermes setup        # 运行完整设置向导（一次性配置所有内容）
hermes claw migrate # 从 OpenClaw 迁移（如果来自 OpenClaw）
hermes update       # 更新到最新版本
hermes doctor       # 诊断任何问题
```

📖 **[完整文档 →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs 消息平台快速参考

Hermes 有两个入口：用 `hermes` 启动终端 UI，或运行网关并从 Telegram、Discord、Slack、WhatsApp、Signal 或 Email 与它对话。一旦进入对话，许多斜杠命令在两个界面间共享。

| 操作 | CLI | 消息平台 |
|------|-----|----------|
| 开始对话 | `hermes` | 运行 `hermes gateway setup` + `hermes gateway start`，然后给机器人发消息 |
| 开始新对话 | `/new` 或 `/reset` | `/new` 或 `/reset` |
| 更换模型 | `/model [provider:model]` | `/model [provider:model]` |
| 设置人格 | `/personality [name]` | `/personality [name]` |
| 重试或撤销上一轮 | `/retry`、`/undo` | `/retry`、`/undo` |
| 压缩上下文 / 查看用量 | `/compress`、`/usage`、`/insights [--days N]` | `/compress`、`/usage`、`/insights [days]` |
| 浏览技能 | `/skills` 或 `/<skill-name>` | `/<skill-name>` |
| 中断当前工作 | `Ctrl+C` 或发送新消息 | `/stop` 或发送新消息 |
| 平台特定状态 | `/platforms` | `/status`、`/sethome` |

完整命令列表请参阅 [CLI 指南](https://hermes-agent.nousresearch.com/docs/user-guide/cli) 和 [消息网关指南](https://hermes-agent.nousresearch.com/docs/user-guide/messaging)。

---

## 文档

所有文档位于 **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**：

| 章节 | 涵盖内容 |
|------|----------|
| [快速开始](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | 安装 → 设置 → 2 分钟内开始首次对话 |
| [CLI 使用](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | 命令、按键绑定、人格、会话 |
| [配置](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | 配置文件、提供商、模型、所有选项 |
| [消息网关](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram、Discord、Slack、WhatsApp、Signal、Home Assistant |
| [安全](https://hermes-agent.nousresearch.com/docs/user-guide/security) | 命令审批、DM 配对、容器隔离 |
| [工具与工具集](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ 工具、工具集系统、终端后端 |
| [技能系统](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | 程序记忆、技能中心、创建技能 |
| [记忆](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | 持久记忆、用户配置、最佳实践 |
| [MCP 集成](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | 连接任意 MCP 服务器以扩展能力 |
| [Cron 调度](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | 定时任务与平台投递 |
| [上下文文件](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | 塑造每场对话的项目上下文 |
| [架构](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | 项目结构、agent 循环、关键类 |
| [贡献](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | 开发设置、PR 流程、代码风格 |
| [CLI 参考](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | 所有命令和标志 |
| [环境变量](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | 完整环境变量参考 |

---

## 从 OpenClaw 迁移

如果你来自 OpenClaw，Hermes 可以自动导入你的设置、记忆、技能和 API 密钥。

**首次安装时：** 设置向导（`hermes setup`）会自动检测 `~/.openclaw` 并在配置开始前提供迁移选项。

**安装后任意时间：**

```bash
hermes claw migrate              # 交互式迁移（完整预设）
hermes claw migrate --dry-run    # 预览将要迁移的内容
hermes claw migrate --preset user-data   # 不迁移密钥
hermes claw migrate --overwrite  # 覆盖现有冲突
```

导入内容：
- **SOUL.md** — 人格文件
- **Memories** — MEMORY.md 和 USER.md 条目
- **Skills** — 用户创建的技能 → `~/.hermes/skills/openclaw-imports/`
- **命令白名单** — 审批模式
- **消息设置** — 平台配置、允许的用户、工作目录
- **API 密钥** — 白名单密钥（Telegram、OpenRouter、OpenAI、Anthropic、ElevenLabs）
- **TTS 资产** — 工作区音频文件
- **工作区指令** — AGENTS.md（使用 `--workspace-target`）

查看 `hermes claw migrate --help` 了解所有选项，或使用 `openclaw-migration` 技能进行交互式 agent 引导迁移与预览。

---

## 贡献

我们欢迎贡献！请参阅 [贡献指南](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) 了解开发设置、代码风格和 PR 流程。

贡献者快速开始 —— 使用 `setup-hermes.sh` 克隆并运行：

```bash
git clone https://github.com/54laowang/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # 安装 uv、创建 venv、安装 .[all]、符号链接 ~/.local/bin/hermes
./hermes              # 自动检测 venv，无需先 `source`
```

手动路径（等同于上述）：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv venv --python 3.11
source venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

> **RL 训练（可选）：** RL/Atropos 集成（`environments/`）通过 `.[all,dev]` 拉取的 `atroposlib` 和 `tinker` 依赖提供 —— 无需子模块设置。

---

## 社区

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [技能中心](https://agentskills.io)
- 🐛 [问题反馈](https://github.com/54laowang/hermes-agent/issues)
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — 社区微信桥接：在同一微信账号上运行 Hermes Agent 和 OpenClaw。

---

## 许可证

MIT — 详见 [LICENSE](LICENSE)。

由 [Nous Research](https://nousresearch.com) 构建。

---

## 🔄 与上游对比

| 特性 | 上游 | 本 Fork |
|------|------|---------|
| **记忆架构** | L1-L4 四层 | ✅ L1-L6 六层（新增 Context Memory + Skills 系统） |
| **缓存优化** | 无 | ✅ DeepSeek Prefix Caching（92%+ 命中率） |
| **任务上下文** | 无 | ✅ L5 Context Memory（任务步骤追踪） |
| **中文 Skills** | 无 | ✅ 韩非子、淘股吧、财联社等本土化 Skills |
| **OCR 工作流** | 依赖视觉模型 | ✅ Tesseract 优先（避免幻觉） |
| **股价缓存** | 无 | ✅ 多数据源智能切换 |
| **时间锚定** | 无 | ✅ 时间锚定宪法（数据准确性保障） |
| **README** | 英文 | ✅ 中英双语 |

---

**Fork 维护者**：[@54laowang](https://github.com/54laowang)  
**上游仓库**：[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
