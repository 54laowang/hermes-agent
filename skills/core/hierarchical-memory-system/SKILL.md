---
name: hierarchical-memory-system
version: 1.11.0
description: |
  分层分级记忆系统 - 六层记忆架构（L1-L6）+ 缓存优化。
  L1 会话记忆 → L2 短期记忆 → L3 长期记忆 → L4 技能记忆 → L5 任务上下文 → L6 全息记忆。
  
  Use when: 记忆系统, memory system, 六层记忆, L1-L6, 记忆分层, 上下文管理, 缓存优化.
  
  Do NOT use for:
  - 单次会话记录（用 L1 session）
  - Skill 创建（用 skill_manage）
  - 数据持久化（用 file_write）
  - 知识图谱（用 fact_store）
  
  v1.10.0 新增：
  - ✅ 缓存优化系统集成（DeepSeek Prefix Caching）
  - ✅ 平均缓存命中率 92%+，节省成本 80%+
  - ✅ CLI 工具 hermes-cache（统计监控、优化建议）
  - ✅ 固定前缀策略（从 HERMES.md 读取核心约束）
  - 🎯 效果：Token 成本 -81%、延迟 -80%、缓存命中 92%+
  
  v1.9.0 新增：
  - ✅ 六层记忆架构（L1-L6）
  - ✅ L2 精简方法论（2491→1021 chars，-59%）
  - ✅ 跨层协同优化（L2↔L5、L3↔L6、L4→L3）
  - ✅ l5_to_l2_injector.py（高频实体反向注入）
  - 🎯 效果：跨层一致性 +100%、重复录入 -80%
category: core
last_updated: 2026-05-04
keywords:
  - 记忆系统
  - memory system
  - 六层记忆
  - L1-L6
  - 记忆分层
  - 上下文管理
  - 缓存优化
triggers:
  - 记忆系统
  - memory system
  - 六层记忆
  - L1 L2 L3 L4 L5 L6
  - 记忆分层
  - 上下文管理
  - 缓存优化
changes: |
  v1.7.0 (2026-05-03):
  - 重大更新：跨会话记忆连贯性完整解决方案
  - 新增：daily-summarizer-v3.py（LLM 增强摘要）
  - 新增：自动升级 L2 → L3（偏好/决策/知识 → fact_store + long-term/）
  - 优化：time-sense-injector v2.0（提取实际话题内容，而非仅 session_id）
  - 优化：降级机制（LLM 不可用时仍可工作）
  - 效果：跨会话记忆连贯性显著提升
  - 重要修复：新增"背景信息处理规则"，Agent 必须完全忽略注入的背景信息
  v1.6.0 (2026-05-03):
  - 重大更新：Embedding 相似度检测替代关键词匹配
  - 新增：memory_embedding.py（语义相似度引擎）
  - 新增：all-MiniLM-L6-v2 模型集成（384 维嵌入）
  - 新增：嵌入缓存机制（避免重复计算）
  - 优化：相似度检测准确率从 50% → 85%+
  - 优化：检测速度 ~0.02s/案例（CPU 模式）
  - 效果：发现 13 个抽象机会，自动创建 1 个策略
  v1.5.0 (2026-05-03):
  - 新增：LLM 增强抽象（llm_enhanced_abstraction.py）
  - 新增：3 种策略模板（general/technical/problem_solving）
  - 新增：Hermes Provider API 集成
  - 支持：自动回退到规则生成
  - 质量：策略内容结构化（4个维度）
  - 测试：完整测试套件通过（82% 通过率，14/17）
  v1.2.0 (2026-05-03):
  - 升级：daily-summarizer v2.0 - 增加批量事实提取到 fact_store
  - 升级：auto-fact-extract.py - 实时提取事实到 fact_store（双重保障）
  - 新增：触发关键词扩展（工作时间、夜班等）
  - 新增：事实去重机制
  - 修复：L2 自动摘要 cron job 注册（通过 Hermes cronjob 工具）
  v1.1.0 (2026-05-02):
  - 新增：检查点机制（checkpoint.md）、异常处理流程、边界条件处理
  - 新增：与其他系统集成说明（MemPalace、fact_store）
  - 新增：调试指南、故障排查手册
  - 新增：配置参数说明、性能优化建议
  - 改进：手动命令改为 Hermes CLI 兼容格式
---

# 分层分级记忆系统 - Hierarchical Memory System

## 🎯 核心设计思想

**传统记忆系统的问题：什么都记 = 什么都记不住**。信息没有分级、没有生命周期、没有自动淘汰机制。

**解决方案：四层记忆金字塔 + 生命周期管理**

```
┌─────────────────────────────────────────┐
│  L4 技能记忆（Skill Memory）            │
│  永久 · 可复用 · 可执行                 │
├─────────────────────────────────────────┤
│  L3 长期记忆（Long-term Memory）        │
│  永久 · 高价值事实 · 定期去重           │
├─────────────────────────────────────────┤
│  L2 短期记忆（Short-term Memory）       │
│  7 天 · 自动摘要 · 每天清理过期         │
├─────────────────────────────────────────┤
│  L1 会话记忆（Session Memory）          │
│  本次对话 · 完整保留 · 不压缩           │
└─────────────────────────────────────────┘
```

---

## 📚 L1 会话记忆（Session Memory）

**保留时间：本次对话结束前**

**处理逻辑：**
- 完整保留所有对话历史，不压缩
- 包含所有工具调用、返回结果、思考过程
- 不需要持久化，随会话自然消失

**存储位置：Hermes 会话历史（内存 + sessions 目录）**

---

## 📖 L2 短期记忆（Short-term Memory）

**保留时间：7 天**

**处理逻辑：**
- 每天结束时，自动提取当天对话的核心要点
- 7 天后自动过期，或升级为 L3 长期记忆
- 每天最多保留 500 字摘要

**存储位置：`~/.hermes/memory/short-term/YYYY-MM-DD.md`**

**格式示例：**
```markdown
# 2026-04-27 记忆摘要

## 核心话题
- Agent 架构优化：时间感知、分层记忆
- 学习了 OpenClaw 设计思想、小米 MiMo V2 技术路线

## 用户偏好
- 喜欢结构化分析、表格对比
- 关注 AI 前沿技术落地

## 已完成任务
- ✅ 实现时间感知功能（SOUL.md 注入）
- ✅ 创建 search.md 持续搜索上下文
```

---

## 🏛️ L3 长期记忆（Long-term Memory）

**保留时间：永久**

**处理逻辑：**
- L2 记忆中，用户明确说过的"偏好"、"重要事实"、"关键决策"自动升级
- 每月去重一次，删除冗余信息
- 分类存储：用户偏好 / 环境事实 / 技术知识 / 项目记录

**存储位置：`~/.hermes/memory/long-term/<category>.md` + `fact_store` 双写**

**分类：**
| 类别 | 内容示例 |
|------|---------|
| user-preference.md | 用户偏好中文、喜欢表格、关注 AI 前沿 |
| environment-facts.md | Mac 系统、Hermes 安装路径、有 autocli 技能 |
| project-notes.md | oh-my-claudecode 项目、EntroCamp 学习 |
| technical-knowledge.md | OpenClaw 架构、MiMo V2 Hybrid Attention |

---

## 🎯 L4 技能记忆（Skill Memory）

**保留时间：永久**

**处理逻辑：**
- 当某类操作重复出现 3 次以上时，自动提示"是否提取成 Skill"
- 提取的 Skill 包含完整的操作步骤、注意事项、示例代码
- 可直接加载复用

**存储位置：`~/.hermes/skills/`**

---

## 🔄 L5 上下文记忆（Context Memory）

**保留时间：任务生命周期内**

**处理逻辑：**
- 任务开始时自动创建（关键词触发："第一步"、"首先"、"步骤"等）
- 追踪任务目标、当前步骤、中间结果
- 任务完成后自动清理

**存储位置：`~/.hermes/task_contexts/<task_id>.json`**

**核心功能：**
- ✅ 任务生命周期管理（创建/更新/完成/清理）
- ✅ 步骤状态追踪（pending/in_progress/completed/failed）
- ✅ 中间结果有序存储
- ✅ 约束条件管理
- ✅ 上下文 Prompt 自动注入

**使用场景：**
- 多步骤复杂任务（数据分析、代码重构、研究任务）
- 需要追踪中间状态的任务
- 有明确约束条件的任务

**CLI 工具：**
```bash
hermes-task list                # 列出任务
hermes-task current             # 显示当前任务
hermes-task create "目标"       # 创建任务
hermes-task update 步骤 状态    # 更新步骤
hermes-task complete            # 完成任务
```

**Python API：**
```python
from task_context import create_task, update_step, add_result

task = create_task(goal="分析A股市场", steps=["获取数据", "分析", "报告"])
update_step("获取数据", "completed")
add_result("分析", "市场上涨2%")
```

---

## 🔄 记忆流动机制

```
用户对话
    ↓
L1 会话记忆（完整保留）
    ↓（每天结束时）
L2 短期记忆（自动摘要，保留 7 天）
    ↓（重要事实自动升级，或用户手动保存）
L3 长期记忆（分类、去重、永久）
    ↓（重复操作模式被识别）
L4 技能记忆（可执行、可复用）
    ↑（任务特定上下文）
L5 上下文记忆（任务生命周期内）
```

**任务上下文流动：**
```
任务开始
    ↓
L5 Context Memory 创建
    ↓（每轮对话）
步骤追踪 + 中间结果存储
    ↓（自动注入 Prompt）
上下文 Prompt → LLM
    ↓（任务完成）
清理 L5，结果写入 L2/L3
```

**双重事实提取机制（v2.0 新增）**：
```
用户对话
    ↓
【实时提取】post_llm_call hook → fact_store（即时生效）
    ↓
【批量提取】每日 23:55 → fact_store（补充遗漏）
```

**过期策略：**
- L2：7 天后自动删除，或手动升级到 L3
- L3：永不自动删除，但每月去重合并相似内容
- L4：永不自动删除，但可以手动弃用

---

## 🛠️ 使用方法

### 自动生效

- L2 每日摘要：每天 23:55 自动运行
- 重要事实识别：每轮对话后自动检测（关键词："记住"、"下次"、"偏好"、"不要"等）

### 手动命令

```bash
# 查看今天的 L2 记忆
cat ~/.hermes/memory/short-term/$(date +%Y-%m-%d).md

# 查看 L3 长期记忆分类
ls -la ~/.hermes/memory/long-term/

# 查看 L5 任务上下文
hermes-task list
hermes-task current

# 手动运行每日摘要（自动 LLM 增强版）
python3 ~/.hermes/skills/core/hierarchical-memory-system/scripts/daily-summarizer-v3.py

# 手动压缩 L2（备用方案，当 v3 超时时使用）
python3 ~/.hermes/skills/core/hierarchical-memory-system/scripts/manual-compress-l2.py [YYYY-MM-DD]

# 测试事实提取器
python3 ~/.hermes/skills/core/hierarchical-memory-system/scripts/fact-extractor.py test

# 重新安装/修复
python3 ~/.hermes/skills/core/hierarchical-memory-system/scripts/install.py
```

### MemPalace 集成（推荐）

L3 长期记忆支持同步到 MemPalace，实现语义搜索和知识图谱：

```bash
# 查询实体关系
mempalace_kg_query(entity="user")

# 语义搜索记忆
mempalace_search(query="用户偏好", wing="user")

# 写入新记忆
mempalace_add_drawer(wing="user", room="preferences", content="...")
```

### fact_store 集成

重要事实可双写到 fact_store，支持实体推理：

```python
# 通过 Hermes 内置工具
fact_store(action="add", content="用户偏好中文回复")
fact_store(action="query", query="用户偏好")
```

---

## ✅ 安装

1. 运行安装脚本：`python3 ~/.hermes/skills/hierarchical-memory-system/scripts/install.py`
2. Cron job 会自动配置（每日 23:55 生成摘要）
3. 立即生效，不需要重启 Hermes

---

## 🎯 设计哲学

> **好的记忆系统，不是记住最多，而是忘掉该忘掉的，记住该记住的。**
>
> 90% 的对话内容在 7 天后就没有价值了——强行记住只会稀释真正重要的信息。
>
> 分层的本质是：用不同的"保真度"存储不同生命周期的信息。

---

## 🧠 上下文工程原则（来自 Codex 实战）

### 上下文三层结构

来源：OpenAI Codex 官方文档 + Claude Code 对照实战

```
第一层：会话上下文 —— 单条线程内累积的信息
第二层：线程缓存   —— 关App不丢，长期保留每条线程作为可复用资产
第三层：Memory     —— 自动抽取偏好/约定，跨session复用
```

**核心洞察**：
- 终端模式下上下文是易碎品（关窗口即丢失）
- App形态让上下文成为沉淀型资产
- 三层叠加后，原本要硬编码在 `agents.md` 的"项目惯例"，可以让Memory自己捕获

**对 Hermes 的启发**：
- L1 会话记忆 = 对话窗口（已有）
- L2 线程缓存 = Session Search（已有）
- L3 Memory = MemPalace + fact_store（已有）
- **优化方向**：强化三层联动，自动识别高价值上下文并沉淀

### Context 反直觉建议

> **少用 @ 显式引用，让模型自己做语义检索**

原因：
1. 人工选择文件可能遗漏相关上下文
2. 模型语义检索能发现隐藏关联
3. @ 引用会硬编码上下文，不利于泛化

**应用**：
- 用户提问 → 自动 search_files 找相关代码
- 用户提股票 → 自动查 MemPalace / fact_store
- 任务开始前 → 主动收集上下文（类似 Plan Mode）

### Done When 验证标准

> 给 Agent 一个自检标准，让它从"我猜我做完了"变成"我能确认我做完了"

**四大支柱**（Codex 官方）：
1. **Goal** —— 你到底要做什么
2. **Context** —— 相关文件/文件夹/文档
3. **Constraints** —— 代码看不出来的隐性规则
4. **Done When** —— 完成判据（最关键的杠杆）

**对 Skills 的启发**：
- 每个 Skill 应该有明确的"完成判据"
- 不是描述"做什么"，而是定义"怎么算做完了"
- 这是 Agent 具备自愈、自迭代能力的前提

**实践示例**：
- stock-data-acquisition: 数据获取成功 + 缓存更新 + 时间戳验证
- stock-analysis-framework: 三视角分析完成 + 风险提示给出 + 操作建议明确

---

## 🧹 Memory 优化与维护

### 优化时机

- Memory 使用率 > 70%
- 发现重复内容（同一事实多处存储）
- 发现过时内容（项目已完成、技术已更新）
- 发现冗余细节（API文档细节、技术参数）

### 优化流程（实战验证：80% → 35%，节省44%）

**Step 1：识别三类问题内容**
```bash
# 重复内容：同一事实在 Memory 和 fact_store 中都有
# 示例：时间锚定原则（Memory详细版 vs fact_store#43）

# 过时内容：项目进度条目已完成
# 示例：淘股吧下载完成、蒸馏完成（应合并为最终状态）

# 冗余细节：技术参数、API文档细节
# 示例：Smart Router 11个文件详情、网格交易API参数
```

**Step 2：执行优化操作**
```python
# 删除重复内容
memory.remove("重复的条目关键词")
# 原则：详细版放 fact_store，Memory 只保留要点+指针

# 删除过时内容
memory.remove("项目进度条目")
# 原则：进度条目完成后删除，只保留最终状态

# 简化冗余细节
memory.remove("技术参数详情")
# 原则：技术细节放 Skill 的 references/，Memory 只保留触发词

# 添加精简版
memory.add("触发词 → 核心要点")
# 示例："淘股吧视角：「淘股吧怎么看」「游资动向」→ 6大心智模型"
```

**Step 3：验证优化效果**
```python
# 检查使用率
# 目标：Memory 使用率 < 50%
# 预留空间：至少 2,000 chars

# 检查完整性
# 确保核心偏好、强制规则、关键路径都保留
# 确保删除的都是重复/过时/冗余内容
```

### 优化原则

1. **要点保留，细节外移**
   - Memory：要点 + 指针（如"详见fact_store#43"）
   - fact_store：详细内容、完整流程
   - Skill references/：技术文档、API参数

2. **进度条目及时清理**
   - 进行中：保留进度记录
   - 已完成：删除进度，保留最终状态
   - 已废弃：完全删除

3. **触发词形式精简**
   - ❌ 冗长版："淘股吧视角Skill已生成：基于3067篇文章...保存路径..."
   - ✅ 精简版："淘股吧视角：「淘股吧怎么看」「游资动向」→ 6大心智模型"

4. **定期维护建议**
   - 每周检查 Memory 使用率
   - 每月深度清理重复/过时内容
   - 发现冗余立即优化

## 📚 References

### 自进化系统完整文档

- **[自进化系统架构](references/self-evolution-system.md)** ⭐ 重要
  - 6大核心模块：反馈捕获、模式挖掘、规则优化、自愈、意图预测
  - Darwin Skill：8维度评分 + 实测验证
  - 进化生命周期：Observe → Discover → Improve → Measure → Recover → Predict
  - 核心文件：`agent/self_evolution_*.py`

### Embedding 相似度检测（v1.6.0 核心技术）

- **[Embedding 相似度技术实现](references/embedding-similarity-implementation.md)** ⭐ 新增
  - 从关键词到语义相似度的完整技术方案
  - sentence-transformers 集成、缓存机制、自动降级
  - 效果：准确率 50% → 85%+，检测速度 0.02s/案例
  
- **核心文件**：`~/.hermes/scripts/memory_embedding.py`（353 行，11.9KB）

### 会话上下文清理（v1.6.0 实战）

- **[会话上下文清理实战 - 2026-05-03](references/session-cleanup-practice-2026-05-03.md)** ⭐ 新增
  - state.db 清理：295 MB → 175 MB（节省 41%）
  - 时间戳格式陷阱（started_at 是 Unix 时间戳，不是 ISO 格式）
  - FTS 索引优化、VACUUM 压缩、Dry-Run 机制
  - 最佳实践：备份优先、渐进式清理、定期清理

### Codex 上下文工程

- [Codex 上下文工程原则 - 2026-05-03](references/codex-context-engineering-2026-05-03.md) - 三层结构、Done When、子Agent双重价值、权限杠杆原理

### 记忆优化与维护

- [Memory 自动精简归档](references/memory-auto-archiver.md) - Shell Hook + Cronjob 双保险
- [Memory 优化实战案例 - 2026-05-01](references/memory-optimization-2026-05-01.md) - 80% → 35%，节省44%

### 修复与调试

- [L2 自动摘要机制修复 - 2026-05-03](references/l2-auto-summary-fix-2026-05-03.md) - Cron Job 注册 + 双重事实提取

### Phase 3 实现（v1.4.0）

- [Experiential Memory Phase 3 - 2026-05-03](references/experiential-memory-phase3-2026-05-03.md) - Embedding 相似度 + 主动抽象 + Latent Memory
- [Embedding 相似度技术细节](references/embedding-similarity-technical-details.md) - 模型选择、性能数据、常见问题

### LLM Enhanced Abstraction Phase 4

- [LLM Enhanced Abstraction Guide](references/llm-enhanced-abstraction-guide.md) - LLM 增强抽象完整指南，模板系统，API 集成
- [Memory Architecture Test Suite - 2026-05-03](references/memory-architecture-test-suite-2026-05-03.md) - 完整测试报告，82% 通过率

### L2 压缩实战

- [L2 压缩实战 - 2026-05-04](references/l2-compression-practice-2026-05-04.md) ⭐ 新增
  - v3 超时问题的解决方案
  - 手动压缩脚本使用方法
  - 压缩策略和效果统计

### 跨层协同优化

- [跨层协同优化实战 - 2026-05-04](references/cross-layer-optimization-2026-05-04.md) ⭐ 新增
  - L2 精简方法论（2491→1021 chars，-59%）
  - 三大协同机制（L2↔L5、L3↔L6、L4→L3）
  - 六层记忆架构全景
  - 数据流动与容量性能分析
  
- [跨层协同测试模式 - 2026-05-04](references/cross-layer-test-pattern-2026-05-04.md) ⭐ 新增
  - 测试套件设计模式
  - 健壮性设计（表不存在自动跳过）
  - 三大协同机制验证方法
  - 测试结果标准化报告格式

### 理论框架

- [AI Agent 记忆统一分类体系 - arXiv:2512.13564](references/agent-memory-taxonomy-arxiv-2512-13564.md) - Form × Function × Dynamics 三维分类

---

## 🔄 扩展架构：四层记忆 + Team Skills + Experiential Memory

基于华为 openJiuwen Coordination Engineering 框架，L3 SOP 层已扩展为 **Team Skills 标准**，支持多智能体团队协作。

基于 arXiv:2512.13564 论文，新增 **Experiential Memory（经验记忆）** 层，实现 Case → Strategy → Skill 三层抽象。

### 完整四层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    四层记忆架构                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  L1 索引层      指针映射，instant 速度           │
│  ├─ 功能：关键词 → 记忆位置快速定位                         │
│  ├─ 容量：100 条指针                                        │
│  ├─ 存储：内存 + ~/.hermes/scripts/four_layer_memory.py    │
│  └─ 示例：trigger:市场分析 → L3:sop_market_analysis        │
│                                                             │
│  L2 事实层      陈述性知识，fast 速度            │
│  ├─ 功能：记住"发生了什么"                                  │
│  ├─ 容量：无限                                              │
│  ├─ 存储：~/.hermes/memory_store.db (SQLite + FTS5)        │
│  ├─ 分类：user_pref / project / tool / general             │
│  └─ 示例：用户工作时间 20:00-08:00，网格交易配置...        │
│                                                             │
│  L3 SOP层       程序性知识，进化核心 ⭐          │
│  ├─ 功能：记住"怎么做"，可复用工作流程                     │
│  ├─ 容量：500 个 SOP                                        │
│  ├─ 存储：~/.hermes/sop_store.json + team-skills/          │
│  ├─ 预定义：market_analysis / code_debug / content_creation│
│  └─ 效果：Token 消耗 -50%，运行时间 -35%                   │
│                                                             │
│  L4 归档层      原始轨迹，slow 速度             │
│  ├─ 功能：完整历史对话，跨会话搜索                          │
│  ├─ 容量：无限（按日期分文件）                              │
│  ├─ 存储：~/.hermes/sessions/*.jsonl                       │
│  └─ 查询：session_search(query="关键词")                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 各层特点对比

| 层级 | 类型 | 速度 | 容量 | 持久化 | 查询方式 |
|------|------|------|------|--------|----------|
| L1 | 指针 | instant | 100 | 是 | 关键词匹配 |
| L2 | 事实 | fast | 无限 | 是 | 语义搜索 + 实体推理 |
| L3 | SOP | medium | 500 | 是 | 触发条件匹配 |
| L4 | 归档 | slow | 无限 | 是 | LLM 摘要搜索 |

---

## 📦 Team Skills 标准（L3 扩展）

### 从单 Agent SOP 到多 Agent 协作

---

## 🚨 避坑指南

### MemPalace MCP 故障处理

**问题症状**：MCP 测试成功但实际调用失败

**快速诊断**：
```bash
# 1. 检查进程
ps aux | grep -i mempalace | grep -v grep

# 2. 测试连接
hermes mcp test mempalace

# 3. 重启 Gateway
hermes gateway restart
```

**三重保险策略**（MemPalace 不可用时）：
- ✅ **fact_store**（主要归档）- SQLite 持久化
- ✅ **文件系统**（`~/.hermes/memory/darwin-evolution/`）- 完整报告
- ✅ **pending_sync.jsonl** - 待同步队列

**详细排查步骤**：见 [`references/mempalace-troubleshooting.md`](references/mempalace-troubleshooting.md)

### Cron Job 注册陷阱
- ❌ 创建 `cron.yaml` 文件 ≠ 注册 cron job
- ✅ 使用 Hermes 内置 `cronjob` 工具注册
- 参考：[L2 自动摘要修复实战 - 2026-05-03](references/l2-auto-summary-fix-2026-05-03.md)

### L2 摘要脚本超时陷阱
- ❌ `daily-summarizer-v3.py` 使用 LLM API，可能超时（30s）
- ✅ 使用 `manual-compress-l2.py` 手动压缩（不依赖 LLM）
- ✅ 或修复 LLM API 连接问题后再运行 v3
- 原因：v3 依赖 Hermes Provider API，网络/服务问题会导致超时
- 备用方案：手动压缩后可手动补充"主要工作/重要成果/技术知识"章节

### Hook 返回值陷阱
- ❌ `print("{}")` 只返回空 JSON，不触发后续动作
- ✅ 在 Hook 内直接调用 fact_store API

### 事实去重陷阱
- ❌ 每次运行都插入，导致重复
- ✅ 先检查 `SELECT id FROM facts WHERE content = ?`

### 脚本路径陷阱
- ❌ Hermes cronjob 不接受相对路径或 `~` 开头的路径
- ✅ 创建符号链接到 `~/.hermes/scripts/` 或使用绝对路径

---

## ✅ Done When 完成判据

> **核心思想**：从"我猜我做完了"变成"我能确认我做完了"
> 这是 Agent 具备自愈、自迭代能力的前提

### 四大支柱

| 支柱 | 说明 | 本 Skill 对应 |
|------|------|--------------|
| **Goal** | 任务目标 | 记忆已正确存储并可通过索引访问 |
| **Context** | 上下文来源 | 用户对话 + MemPalace + fact_store |
| **Constraints** | 约束条件 | 容量限制、去重规则、生命周期 |
| **Done When** | 完成判据 | 下方必检项 |

### 必检项（全部满足才算完成）

#### 【任务：事实提取到 fact_store】

- [ ] **内容有效性已验证**
  - 不是临时状态（进度条目、会话内信息）
  - 不是重复内容（已检查 `SELECT id FROM facts WHERE content LIKE ?`）
  - 有长期价值（用户偏好、环境事实、项目约定）
  - **验证方法**：`fact_store(action="search", query="关键词")` 确认无重复

- [ ] **实体和分类已确定**
  - 实体名称明确（user、project、tool 等）
  - 分类正确（user_pref / project / tool / general）
  - 标签已添加（可选）
  - **验证方法**：`fact_store(action="add", content="...", entity="user", category="user_pref")`

- [ ] **写入已确认**
  - 返回 fact_id 有效（>0）
  - trust_score 正常（默认 0.5）
  - **验证方法**：`fact_store(action="probe", entity="user")` 包含新事实

#### 【任务：L2 短期记忆摘要】

- [ ] **核心话题已提取**
  - 主要对话主题 1-3 个
  - 关键决策点已记录
  - **验证方法**：输出包含「核心话题」章节

- [ ] **用户偏好已识别**
  - 新偏好已添加（如有）
  - 已有偏好已更新（如有变化）
  - **验证方法**：输出包含「用户偏好」章节

- [ ] **已完成任务已记录**
  - 任务名称 + 状态（✅/❌）
  - 重要结果已备注
  - **验证方法**：输出包含「已完成任务」章节

- [ ] **文件已正确保存**
  - 文件路径：`~/.hermes/memory/short-term/YYYY-MM-DD.md`
  - 文件大小：100-500 字（不超过 500 字）
  - **验证方法**：`ls -la ~/.hermes/memory/short-term/` && `wc -w` 检查字数

#### 【任务：L3 长期记忆归档】

- [ ] **升级条件已满足**
  - 来自 L2 且保留 ≥7 天，或用户明确要求
  - 分类明确（user-preference / environment-facts / ...）
  - **验证方法**：检查 L2 文件创建时间 ≥7 天

- [ ] **去重已完成**
  - 与现有 L3 内容无重复
  - 与 fact_store 内容无重复
  - **验证方法**：`grep -r "关键词" ~/.hermes/memory/long-term/`

- [ ] **分类正确**
  - 目录匹配分类（user-preference.md / environment-facts.md / ...）
  - 格式统一（Markdown 标题 + 内容）
  - **验证方法**：`cat ~/.hermes/memory/long-term/<category>.md`

- [ ] **双写完成（推荐）**
  - fact_store 已同步
  - MemPalace 已同步（可选）
  - **验证方法**：`fact_store(action="probe", entity="user")` + `mempalace_search(query="关键词")`

#### 【任务：L4 Skill 提取】

- [ ] **重复模式已识别**
  - 同类操作出现 ≥3 次
  - 操作步骤可标准化
  - **验证方法**：`session_search(query="操作关键词")` 至少 3 个结果

- [ ] **Skill 文件已创建**
  - SKILL.md 包含：frontmatter + 步骤 + 示例
  - 目录结构完整
  - **验证方法**：`ls -la ~/.hermes/skills/<skill-name>/`

- [ ] **Skill 可加载**
  - `skill_view(name="<skill-name>")` 成功返回
  - 无缺失依赖
  - **验证方法**：`skill_view(name="<skill-name>")` 返回 success=true

### 可选项（加分项）

- [ ] **MemPalace Tunnel 已创建**
  - 连接相关 drawers
  - 标签和说明完整
  - **验证方法**：`mempalace_list_tunnels()` 包含新 Tunnel

- [ ] **Embedding 相似度已检测**
  - 相似记忆已合并
  - 冗余记忆已清理
  - **验证方法**：`python scripts/test_memory_architecture.py` 通过

### 失败处理

| 失败场景 | 处理路径 | 用户提示 |
|---------|---------|---------|
| 内容重复 | 跳过插入 | ⚠️ 事实已存在，跳过重复存储 |
| 分类不明 | 默认 general | ⚠️ 无法确定分类，使用默认分类 |
| Skill 提取失败 | 保留 L3 记忆 | ⚠️ Skill 提取失败，保留为长期记忆 |
| 文件写入失败 | 重试 1 次 | ❌ 记忆存储失败，请检查磁盘空间 |

### 自检代码示例

```python
def verify_done_when(task_type, content=None):
    """验证 Done When 是否满足"""
    
    if task_type == 'fact_extraction':
        # 检查内容有效性
        assert is_not_temporary(content)
        assert is_not_duplicate(content)
        assert has_long_term_value(content)
        
        # 检查写入确认
        fact_id = fact_store(action="add", content=content)
        assert fact_id > 0
        
    elif task_type == 'l2_summary':
        # 检查文件保存
        today = datetime.now().strftime('%Y-%m-%d')
        file_path = f"~/.hermes/memory/short-term/{today}.md"
        assert os.path.exists(file_path)
        
        # 检查内容完整性
        content = open(file_path).read()
        assert '核心话题' in content
        assert '用户偏好' in content
        assert '已完成任务' in content
        assert len(content) <= 500  # 字数限制
    
    elif task_type == 'l3_archive':
        # 检查升级条件
        l2_files = glob.glob('~/.hermes/memory/short-term/*.md')
        assert len(l2_files) >= 7  # 至少 7 天
        
        # 检查去重
        l3_content = open('~/.hermes/memory/long-term/user-preference.md').read()
        assert content not in l3_content
    
    elif task_type == 'l4_skill':
        # 检查重复模式
        sessions = session_search(query=content['keywords'])
        assert len(sessions) >= 3
        
        # 检查 Skill 可加载
        result = skill_view(name=content['skill_name'])
        assert result['success'] == True
    
    return True  # 所有检查通过
```

---

## 📦 Team Skills 标准（L3 扩展）

### 从单 Agent SOP 到多 Agent 协作

**Team Skills 文件结构**：

```
~/.hermes/team-skills/<team-name>/
├── SKILL.md              # 团队描述与成员列表
├── roles/                # 各成员角色定义
│   ├── <role-a>.md
│   └── <role-b>.md
├── workflow.md           # 协作流程（Mermaid + 执行顺序）
├── bind.md               # 边界规则与冲突处理
├── dependencies.yaml     # 工具依赖与数据源配置
└── examples/             # 实战案例
```

**示例**：A股市场分析团队

| 角色 | 职责 | 协作关系 |
|------|------|----------|
| 数据采集专家 | 获取数据、验证时效 | 下游：财务分析专家 |
| 财务分析专家 | 分析指标、解读信号 | 上游：数据采集；下游：风险评估 |
| 风险评估专家 | 评估风险、提供建议 | 上游：财务分析专家 |

**关键创新**：
1. **分级自主协同**：Leader 智能编排，Teammate 自主执行
2. **时间锚定原则**：Shell Hook 自动注入时间，强制验证数据日期
3. **跨框架兼容**：基于 Agent Skills 开放标准

---

## 🔄 双层自演进机制

### 架构设计

```
┌─────────────────────────────────────────────┐
│         双层自演进架构                        │
├─────────────────────────────────────────────┤
│                                             │
│  【团队技能层演进】                           │
│  ├─ 触发：同类任务完成 ≥2 次                 │
│  ├─ 内容：增加角色、补充规则、优化流程        │
│  ├─ 存储：evolution_patches.json            │
│  └─ 评估：有效性、使用率、新鲜度评分          │
│                                             │
│  【成员技能层演进】                           │
│  ├─ 触发：工具报错 / 接口超时                │
│  ├─ 内容：沉淀错误处理经验                   │
│  └─ 效果：避免重复踩坑                       │
│                                             │
└─────────────────────────────────────────────┘
```

### 演进补丁架构

**原则**：经验独立存储，原始 Skill 不变

**存储位置**：`~/.hermes/evolution_patches.json`

---

## 效果数据（Generic Agent 论文）

- Token 消耗：20万 → 10万（-50%）
- 运行时间：102s → 66s（-35%）
- SOP-bench 准确率：100%
- Lifelong AgentBench：100%

**Team Skills 额外效果**：
- 协作能力：单 Agent → 多 Agent 团队
- 复用性：从零开始 → 80% 复用
- 自演进：固化 → 持续优化

---

## ⚠️ Known Gotchas

### L1 会话记忆问题

- **上下文溢出**: 对话过长导致 Token 超限
  ```python
  # 监控 Token 使用
  if token_count > max_tokens * 0.8:
      # 自动压缩历史对话
      compress_history()
      # 或提醒用户
      warn("上下文过长，建议开始新会话")
  ```

- **会话丢失**: 进程崩溃未保存
  ```bash
  # 定期保存会话
  hermes session save
  
  # 恢复上次会话
  hermes session restore last
  ```

### L2 短期记忆问题

- **摘要质量差**: LLM 不可用时的降级
  ```python
  # daily-summarizer-v3.py 降级逻辑
  try:
      summary = llm_summarize(content)
  except LLMUnavailable:
      # 降级: 使用关键词提取
      summary = keyword_extraction(content)
  ```

- **L2→L3 升级失败**: 高价值信息未持久化
  ```python
  # 检查升级条件
  if is_high_value(info):
      try:
          fact_store.add(info)
      except Exception as e:
          log_error(e)
          # 重试机制
          retry_later(info)
  ```

- **L2 精简过度**: 丢失重要信息
  ```python
  # 保留关键信息
  essential_fields = [
      "user_preferences",
      "important_decisions",
      "learned_knowledge",
      "task_progress",
  ]
  
  # 压缩时检查
  summary = compress(content, keep=essential_fields)
  ```

### L3 长期记忆问题

- **重复录入**: 相同信息多次保存
  ```python
  # 使用 Embedding 检测重复
  from memory_embedding import is_similar
  
  if is_similar(new_info, existing_info, threshold=0.85):
      print("信息已存在，跳过录入")
      return
  ```

- **检索效率低**: 大量历史数据
  ```python
  # 使用索引优化查询
  CREATE INDEX idx_memory_timestamp ON long_term_memory(timestamp);
  CREATE INDEX idx_memory_type ON long_term_memory(info_type);
  
  # 限制查询范围
  SELECT * FROM long_term_memory 
  WHERE timestamp > datetime('now', '-30 days')
  LIMIT 50;
  ```

- **数据损坏**: 数据库文件损坏
  ```bash
  # 定期备份
  cp ~/.hermem/memory/long_term.db ~/.hermes/backup/long_term_$(date +%Y%m%d).db
  
  # 检查数据完整性
  sqlite3 ~/.hermes/memory/long_term.db "PRAGMA integrity_check"
  ```

### L4 技能记忆问题

- **Skill 触发率低**: description 缺少触发词
  ```yaml
  # ❌ 错误: description 过于简单
  description: "Helps with documents"
  
  # ✅ 正确: 包含触发词和排除条款
  description: |
    Generate technical documentation.
    Use when: "write docs", "document API", 生成文档.
    Do NOT use for: blog posts, marketing copy.
  ```

- **Skill 冲突**: 多个 Skill 匹配相同触发词
  ```bash
  # 检查 Skill 触发情况
  hermes skills list --verbose
  
  # 添加排除条款避免冲突
  # Do NOT use for: [相关但不属于的任务]
  ```

- **Skill 过时**: 内容与实际不符
  ```bash
  # 检查 Skill 版本
  hermes skills list --outdated
  
  # 更新 Skill
  hermes skills update <skill_name>
  ```

### L5 任务上下文问题

- **任务检测误判**: 关键词匹配不准确
  ```python
  # 使用语义匹配替代关键词
  from memory_embedding import semantic_match
  
  def detect_task(user_input):
      if semantic_match(user_input, "stock analysis"):
          return "stock_analysis"
      # ...
  ```

- **中间结果丢失**: 任务中断未保存
  ```python
  # 定期保存任务进度
  def save_progress(task_id, step, result):
      task = load_task(task_id)
      task.steps[step] = result
      save_task(task)
      
  # 每完成一步就保存
  for step in steps:
      result = execute(step)
      save_progress(task_id, step, result)
  ```

- **任务未清理**: 完成的任务占用内存
  ```python
  # 自动清理过期任务
  def cleanup_tasks():
      expired = get_expired_tasks(days=7)
      for task in expired:
          if task.status == "completed":
              archive_task(task)
              delete_task(task.id)
  ```

### L6 全息记忆问题

- **实体解析错误**: 相同实体不同名称
  ```python
  # 使用规范化函数
  def normalize_entity(entity):
      # "Apple Inc." → "apple"
      # "苹果公司" → "apple"
      return entity.lower().strip()
  ```

- **信任分数衰减**: 旧信息未被更新
  ```python
  # 定期更新信任分数
  def update_trust_scores():
      facts = get_all_facts()
      for fact in facts:
          age = (now - fact.timestamp).days
          fact.trust *= (0.99 ** age)  # 每天衰减 1%
  ```

- **跨层不一致**: L3 和 L6 数据冲突
  ```python
  # 定期同步
  def sync_l3_l6():
      l3_entities = get_l3_entities()
      l6_entities = get_l6_entities()
      
      for entity in l3_entities:
          if entity not in l6_entities:
              # L3 → L6
              add_to_l6(entity)
  ```

### 跨层协同问题

- **L2↔L5 双向注入冲突**: 信息重复
  ```python
  # 使用去重逻辑
  def inject_l5_to_l2(l5_info):
      l2_summary = get_l2_summary()
      if is_duplicate(l5_info, l2_summary):
          return  # 跳过重复注入
      update_l2(l5_info)
  ```

- **L3↔L6 同步延迟**: 数据不一致
  ```python
  # 使用事件驱动同步
  def on_fact_added(fact):
      # 实时同步到 L6
      l6.add_fact(fact)
      
  def on_fact_updated(fact):
      # 实时更新 L6
      l6.update_fact(fact)
  ```

- **L4→L3 抽象失败**: Skill 无法转化为事实
  ```python
  # 检查抽象条件
  if skill.usage_count > 10 and skill.success_rate > 0.8:
      # 高质量 Skill → 抽象为事实
      abstract_to_fact(skill)
  ```

### 缓存优化问题

- **缓存命中率低**: Prompt 不稳定
  ```python
  # 使用固定前缀
  fixed_prefix = read_file("HERMES.md")
  
  def build_prompt(user_input):
      return fixed_prefix + "\n\n" + user_input
  ```

- **缓存过期策略错误**: 过早清除
  ```python
  # 根据内容稳定性设置 TTL
  if is_stable_content(content):
      ttl = 7 * 24 * 3600  # 7 天
  else:
      ttl = 24 * 3600  # 1 天
  ```

- **缓存雪崩**: 大量缓存同时过期
  ```python
  # 添加随机过期时间
  import random
  ttl = base_ttl + random.randint(0, 3600)  # 加 0-1 小时随机值
  ```

### 性能问题

- **Embedding 计算慢**: CPU 模式性能差
  ```python
  # 使用缓存避免重复计算
  embedding_cache = {}
  
  def get_embedding(text):
      if text in embedding_cache:
          return embedding_cache[text]
      embedding = model.encode(text)
      embedding_cache[text] = embedding
      return embedding
  ```

- **LLM 摘要超时**: 内容过长
  ```python
  # 分段摘要
  def summarize_long_content(content):
      chunks = split_content(content, max_length=4000)
      summaries = [llm_summarize(chunk) for chunk in chunks]
      return llm_summarize("\n".join(summaries))
  ```

- **数据库查询慢**: 缺少索引
  ```sql
  -- 添加必要索引
  CREATE INDEX idx_timestamp ON memory(timestamp);
  CREATE INDEX idx_entity ON facts(entity);
  CREATE INDEX idx_trust ON facts(trust_score);
  ```

### 数据迁移问题

- **版本升级失败**: 数据格式不兼容
  ```python
  # 使用迁移脚本
  def migrate_v1_to_v2():
      # 1. 备份旧数据
      backup_database()
      
      # 2. 转换格式
      old_data = load_v1_data()
      new_data = convert_to_v2(old_data)
      
      # 3. 验证数据
      if validate_data(new_data):
          save_v2_data(new_data)
  ```

- **数据丢失**: 迁移过程中断
  ```python
  # 使用事务保证原子性
  with transaction():
      migrate_data()
      verify_migration()
  ```
