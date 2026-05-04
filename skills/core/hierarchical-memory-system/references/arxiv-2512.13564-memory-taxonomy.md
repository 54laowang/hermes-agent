# AI Agent 记忆统一分类体系（arXiv:2512.13564）

## 论文信息
- **标题**: Memory in the Age of AI Agents: A Survey
- **作者**: 46 位作者（NUS、人大、复旦、北大等）
- **时间**: 2025-12 发布，2026-01 修订
- **论文地址**: https://arxiv.org/abs/2512.13564
- **GitHub**: https://github.com/Shichun-Liu/Agent-Memory-Paper-List

## 核心贡献

**传统分类（长/短期记忆）已不足以描述当代 Agent 记忆系统的多样性。**

本文提出 **三维统一分类体系**：Form（形式）× Function（功能）× Dynamics（动态）

---

## 一、Form（形式）：记忆载体是什么？

### 1. Token-level Memory（词元级记忆）
- **Flat Memory (1D)**: 线性序列，如对话历史
- **Planar Memory (2D)**: 结构化存储，如表格、知识图谱
- **Hierarchical Memory (3D)**: 分层组织，如摘要树

### 2. Parametric Memory（参数级记忆）
- **Internal Parametric**: 模型参数内部化（微调、RL）
- **External Parametric**: 外部适配器（LoRA、Prefix Tuning）

### 3. Latent Memory（隐 latent 记忆）
- **Generate**: 动态生成记忆内容
- **Reuse**: 复用历史隐状态
- **Transform**: 变换记忆表示

---

## 二、Function（功能）：为什么需要记忆？

### 1. Factual Memory（事实记忆）
- **User Factual Memory**: 用户偏好、个人画像
- **Environment Factual Memory**: 世界知识、环境状态

### 2. Experiential Memory（经验记忆）
- **Case-based Memory**: 具体案例记忆
- **Strategy-based Memory**: 策略/规则记忆
- **Skill-based Memory**: 技能记忆
- **Hybrid Memory**: 混合类型

### 3. Working Memory（工作记忆）
- **Single-turn Working Memory**: 单轮任务执行
- **Multi-turn Working Memory**: 多轮对话/任务规划

---

## 三、Dynamics（动态）：记忆如何演化？

### 1. Memory Formation（记忆形成）
- **Semantic Summarization**: 语义摘要
- **Knowledge Distillation**: 知识蒸馏
- **Structured Construction**: 结构化构建
- **Latent Representation**: 隐表示编码
- **Parametric Internalization**: 参数内化

### 2. Memory Evolution（记忆演化）
- **Consolidation**: 记忆巩固
- **Updating**: 记忆更新
- **Forgetting**: 记忆遗忘

### 3. Memory Retrieval（记忆检索）
- **Retrieval Timing**: 何时检索
- **Query Construction**: 如何构建查询
- **Retrieval Strategies**: 检索策略
- **Post-Retrieval Processing**: 检索后处理

---

## 四、Agent Memory vs 相关概念

| 概念 | 区别 |
|------|------|
| **LLM Memory** | LLM 记忆是模型内部的，Agent 记忆是外部构建的 |
| **RAG** | RAG 是检索增强生成，Agent Memory 包含更复杂的演化机制 |
| **Context Engineering** | 上下文工程是静态优化，Agent Memory 是动态管理 |

---

## 五、前沿研究方向

1. **Memory Retrieval vs Generation**: 从检索记忆到生成记忆
2. **Automated Memory Management**: 自动化记忆管理
3. **RL Meets Agent Memory**: 强化学习与记忆系统集成
4. **Multimodal Memory**: 多模态记忆
5. **Shared Memory in Multi-Agent**: 多智能体共享记忆
6. **Memory for World Model**: 记忆构建世界模型
7. **Trustworthy Memory**: 可信记忆（安全性、隐私）
8. **Human-Cognitive Connections**: 与人类认知的联系

---

## 六、对 Hermes 的启示

### 当前实现映射

| Hermes 层级 | 论文分类 |
|------------|---------|
| L1 会话记忆 | Token-level + Working Memory |
| L2 短期记忆 | Token-level + Factual Memory |
| L3 长期记忆 | Parametric/Token-level + Factual/Experiential |
| L4 技能记忆 | Experiential (Skill-based) |
| fact_store | Token-level + Factual Memory |
| MemPalace | Token-level + Factual/Experiential |

### 待实现方向

| 优先级 | 方向 | 当前差距 |
|--------|------|---------|
| **P0** | Experiential Memory | ✅ Phase 1 已实现 |
| **P0** | Latent Memory | 未实现隐状态复用 |
| **P1** | Memory Evolution | ✅ 基础实现（巩固/遗忘） |
| **P2** | Parametric Memory | 未使用参数级记忆 |
| **P2** | Multimodal Memory | 仅支持文本 |
