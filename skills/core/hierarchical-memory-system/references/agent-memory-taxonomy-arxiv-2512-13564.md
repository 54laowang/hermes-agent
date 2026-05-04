# AI Agent 记忆统一分类体系 - arXiv:2512.13564

## 论文信息

- **标题**: Memory in the Age of AI Agents: A Survey
- **作者**: 46 位作者（NUS、人大、复旦、北大等）
- **时间**: 2025-12 发布，2026-01 修订
- **论文地址**: https://arxiv.org/abs/2512.13564
- **GitHub**: https://github.com/Shichun-Liu/Agent-Memory-Paper-List
- **规模**: 107 页，46 万字

---

## 核心贡献

**传统分类（长/短期记忆）已不足以描述当代 Agent 记忆系统的多样性。**

本文提出 **三维统一分类体系**：

```
Form（形式）× Function（功能）× Dynamics（动态）
```

---

## 一、Form（形式）：记忆载体是什么？

### 1. Token-level Memory（词元级记忆）

**定义**：以离散 token 序列形式存储的记忆

#### Flat Memory (1D)

- **结构**：线性序列
- **示例**：对话历史、文档片段
- **优势**：简单直接，易于检索
- **劣势**：难以组织复杂关系

#### Planar Memory (2D)

- **结构**：表格、知识图谱
- **示例**：用户画像表、实体关系图
- **优势**：结构化，支持复杂查询
- **劣势**：需要预处理和schema设计

#### Hierarchical Memory (3D)

- **结构**：树状组织，多层摘要
- **示例**：摘要树、概念层次
- **优势**：可扩展，支持多粒度检索
- **劣势**：构建和维护成本高

### 2. Parametric Memory（参数级记忆）

**定义**：存储在模型参数中的记忆

#### Internal Parametric Memory

- **方式**：微调、RL 训练
- **示例**：领域适配、技能内化
- **优势**：推理时无额外开销
- **劣势**：更新成本高，难以修改

#### External Parametric Memory

- **方式**：LoRA、Prefix Tuning、Adapter
- **示例**：用户特定适配器、任务特定 prefix
- **优势**：模块化，易于切换
- **劣势**：需要管理多个适配器

### 3. Latent Memory（隐状态记忆）

**定义**：以隐向量形式存储的记忆

#### Generate

- **方式**：动态生成记忆内容
- **示例**：基于查询生成相关记忆
- **优势**：灵活，不受固定存储限制
- **劣势**：可能产生幻觉

#### Reuse

- **方式**：复用历史 KV Cache
- **示例**：长对话中的 checkpoint
- **优势**：性能提升 30-50%
- **劣势**：需要管理 cache 生命周期

#### Transform

- **方式**：变换记忆表示
- **示例**：压缩、编码、投影
- **优势**：减少存储空间
- **劣势**：可能丢失信息

---

## 二、Function（功能）：为什么需要记忆？

### 1. Factual Memory（事实记忆）

**定义**：存储客观事实和知识的记忆

#### User Factual Memory

- **内容**：用户偏好、个人画像、历史交互
- **示例**：用户喜欢中文、关注 AI 前沿、夜班工作
- **应用**：个性化对话、推荐系统

#### Environment Factual Memory

- **内容**：世界知识、环境状态、可用资源
- **示例**：API 文档、系统配置、数据库 schema
- **应用**：任务规划、工具调用

### 2. Experiential Memory（经验记忆）

**定义**：存储经历和经验教训的记忆

#### Case-based Memory

- **内容**：具体案例、成功/失败经历
- **示例**：上次解决 X 问题的完整过程
- **应用**：类比推理、案例检索

#### Strategy-based Memory

- **内容**：抽象的策略、规则、启发式
- **示例**：遇到 X 类型问题，优先尝试 Y
- **应用**：策略选择、决策支持

#### Skill-based Memory

- **内容**：编码的可执行技能
- **示例**：完整的工作流程、操作步骤
- **应用**：技能复用、自动化执行

#### Hybrid Memory

- **内容**：混合多种类型
- **示例**：案例 + 策略 + 技能
- **应用**：复杂任务处理

### 3. Working Memory（工作记忆）

**定义**：临时存储用于当前任务的信息

#### Single-turn Working Memory

- **内容**：当前任务相关的临时信息
- **示例**：用户提问、检索结果、中间推理
- **应用**：单轮问答、即时响应

#### Multi-turn Working Memory

- **内容**：跨多轮的上下文信息
- **示例**：对话状态、任务进度、待办事项
- **应用**：多轮对话、长期任务

---

## 三、Dynamics（动态）：记忆如何演化？

### 1. Memory Formation（记忆形成）

#### Semantic Summarization

- **方式**：提取核心语义，压缩冗余
- **示例**：对话摘要、文档摘要
- **工具**：LLM、抽取式摘要

#### Knowledge Distillation

- **方式**：从大量数据中蒸馏知识
- **示例**：从对话中提取用户画像
- **工具**：LLM、知识图谱构建

#### Structured Construction

- **方式**：构建结构化表示
- **示例**：构建知识图谱、表格
- **工具**：IE、NER、关系抽取

#### Latent Representation

- **方式**：编码为隐向量
- **示例**：embedding、KV Cache
- **工具**：Encoder、RAG

#### Parametric Internalization

- **方式**：内化到模型参数
- **示例**：微调、RL 训练
- **工具**：LoRA、Prefix Tuning

### 2. Memory Evolution（记忆演化）

#### Consolidation（巩固）

- **机制**：重复经历 → 强化记忆
- **示例**：多次提及 → strength++
- **算法**：Ebbinghaus 遗忘曲线

#### Updating（更新）

- **机制**：环境变化 → 记忆同步
- **示例**：用户偏好改变 → 更新画像
- **算法**：版本控制、时间衰减

#### Forgetting（遗忘）

- **机制**：低价值记忆 → 删除
- **示例**：7 天未访问 → 自动删除
- **算法**：LRU、LFU、retrieval_count

### 3. Memory Retrieval（记忆检索）

#### Retrieval Timing

- **时机**：何时检索记忆
- **策略**：任务开始时、需要时、定期
- **示例**：每轮对话前检索相关记忆

#### Query Construction

- **方式**：如何构建查询
- **策略**：关键词、语义、混合
- **示例**：从用户问题中提取关键词

#### Retrieval Strategies

- **方式**：如何检索
- **策略**：
  - 相似度检索（embedding）
  - 关键词检索（BM25）
  - 混合检索（Hybrid）
  - 分层检索（Hierarchical）
- **示例**：先用 BM25 粗筛，再用 semantic 精排

#### Post-Retrieval Processing

- **方式**：检索后如何处理
- **策略**：重排序、压缩、过滤
- **示例**：去除重复、按时间排序

---

## 四、Agent Memory vs 相关概念

### Agent Memory vs LLM Memory

| 维度 | LLM Memory | Agent Memory |
|------|-----------|-------------|
| **位置** | 模型内部 | 外部构建 |
| **更新** | 需要重新训练 | 实时更新 |
| **控制** | 模型自主 | Agent 主动管理 |
| **持久性** | 永久（参数中） | 可配置生命周期 |

### Agent Memory vs RAG

| 维度 | RAG | Agent Memory |
|------|-----|-------------|
| **目标** | 增强生成质量 | 支持持续进化 |
| **数据源** | 静态文档库 | 动态交互历史 |
| **演化** | 无 | 有（形成/更新/遗忘） |
| **个性化** | 无 | 有（用户特定） |

### Agent Memory vs Context Engineering

| 维度 | Context Engineering | Agent Memory |
|------|-------------------|-------------|
| **性质** | 静态优化 | 动态管理 |
| **范围** | 当前上下文 | 跨会话持久 |
| **主动性** | 被动填充 | 主动检索/更新 |
| **演化** | 无 | 有 |

---

## 五、前沿研究方向

### 1. Memory Retrieval vs Generation

- **趋势**：从检索记忆到生成记忆
- **挑战**：如何平衡准确性和创造性
- **方向**：混合检索+生成架构

### 2. Automated Memory Management

- **趋势**：手工设计 → 自动化
- **挑战**：何时形成、何时遗忘、如何更新
- **方向**：基于 RL 的记忆管理策略

### 3. RL Meets Agent Memory

- **趋势**：RL 内化记忆管理能力
- **挑战**：奖励设计、状态空间
- **方向**：Memory-augmented RL

### 4. Multimodal Memory

- **趋势**：文本 → 多模态
- **挑战**：跨模态检索、统一表示
- **方向**：CLIP-like embedding

### 5. Shared Memory in Multi-Agent

- **趋势**：孤立记忆 → 共享认知
- **挑战**：一致性、冲突解决
- **方向**：分布式记忆架构

### 6. Memory for World Model

- **趋势**：记忆构建世界模型
- **挑战**：因果推理、反事实
- **方向**：Memory-based World Model

### 7. Trustworthy Memory

- **趋势**：安全性、隐私、可解释性
- **挑战**：对抗攻击、隐私泄露
- **方向**：加密记忆、差分隐私

### 8. Human-Cognitive Connections

- **趋势**：借鉴人类认知科学
- **挑战**：验证、可解释性
- **方向**：认知启发的记忆架构

---

## 六、对 Hermes 记忆架构的启示

### 当前架构映射

| Hermes 层级 | 论文分类 | 匹配度 |
|------------|---------|--------|
| L1 会话记忆 | Token-level + Working Memory | ★★★★☆ |
| L2 短期记忆 | Token-level + Factual Memory | ★★★★☆ |
| L3 长期记忆 | Parametric/Token-level + Factual/Experiential | ★★★☆☆ |
| L4 技能记忆 | Experiential (Skill-based) | ★★☆☆☆ |
| fact_store | Token-level + Factual Memory | ★★★★☆ |
| MemPalace | Token-level + Factual/Experiential | ★★★☆☆ |

### 优化方向

| 优先级 | 方向 | 当前差距 | 论文参考 |
|--------|------|---------|---------|
| **P0** | Experiential Memory | Skills 偏弱，无案例→策略→技能抽象 | §4.2 |
| **P0** | Latent Memory | 未实现 KV Cache 复用 | §3.3 |
| **P1** | Memory Evolution | 仅过期清理，无巩固/更新 | §5.2 |
| **P2** | Parametric Memory | 未使用 LoRA 适配器 | §3.2 |
| **P2** | Multimodal Memory | 仅支持文本 | §7.4 |

---

## 七、开源框架推荐

### Mem0

- **定位**：Universal memory layer for AI Agents
- **特点**：Single-pass ADD-only，去重，自动分类
- **GitHub**：https://github.com/mem0ai/mem0

### MemGPT

- **定位**：Virtual context management
- **特点**：分层上下文，自动换入换出
- **GitHub**：https://github.com/cpacker/memgpt

### Letta

- **定位**：Stateful LLM framework
- **特点**：持久化状态，多轮对话
- **GitHub**：https://github.com/letta-ai/letta

---

## 八、实施建议

### Phase 1：Experiential Memory（1-2 周）

**目标**：从案例 → 策略 → 技能 的渐进抽象

**步骤**：
1. 扩展 fact_store 支持 `experiential_case` / `experiential_strategy` / `experiential_skill` 类型
2. 实现案例提取算法
3. 实现案例 → 策略抽象（LLM 辅助）
4. 实现策略 → 技能编码（生成 Skill.md）

### Phase 2：Memory Evolution（1 周）

**目标**：智能记忆管理

**步骤**：
1. 增加 `strength` 字段（记忆强度）
2. 实现巩固机制（retrieval_count++ → strength++）
3. 实现更新机制（检测变化 → 触发更新）
4. 实现遗忘机制（strength-based forgetting）

### Phase 3：Latent Memory（2-3 周）

**目标**：KV Cache 复用

**步骤**：
1. 研究 vLLM/KV Cache 管理机制
2. 设计 checkpoint 策略（关键节点保存）
3. 实现检索机制（embedding 相似度）
4. 集成到 Hermes 推理流程

---

## 参考文献

1. Hu, Y., et al. (2026). Memory in the Age of AI Agents. arXiv:2512.13564.
2. Park, J., et al. (2023). Generative Agents: Interactive Simulacra of Human Behavior.
3. Zhong, W., et al. (2024). MemoryBank: Enhancing Large Language Models with Long-Term Memory.
4. Wang, L., et al. (2024). RecMind: Large Language Model Powered Agent for Recommendation.
