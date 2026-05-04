---
name: skill-authoring-quality
description: Skill 创作质量标准 - Done When 完成判据、主动上下文发现、检查点设计规范。确保 Skills 具备自检能力，从"我猜我做完了"变成"我能确认我做完了"。
version: 1.0.0
tags: [meta, skill-authoring, done-when, context-discovery, quality]
author: Hermes
created: 2026-05-03
---

# Skill 创作质量标准

## 🎯 核心目标

**从"我猜我做完了"变成"我能确认我做完了"**

这是 Agent 具备自愈、自迭代能力的前提。

---

## 📚 核心方法论

### 一、Done When 完成判据

#### 四大支柱

| 支柱 | 说明 | 示例 |
|------|------|------|
| **Goal** | 任务目标 | 获取股票数据并验证 |
| **Context** | 上下文来源 | MemPalace + fact_store + 缓存 |
| **Constraints** | 约束条件 | 时间锚定、数据源优先级、缓存策略 |
| **Done When** | 完成判据 | 必检项（最关键杠杆） |

#### 标准模板

```markdown
## ✅ Done When 完成判据

### 四大支柱

| 支柱 | 说明 | 本 Skill 对应 |
|------|------|--------------|
| **Goal** | 任务目标 | 【具体目标】 |
| **Context** | 上下文来源 | 【数据源】 |
| **Constraints** | 约束条件 | 【限制规则】 |
| **Done When** | 完成判据 | 下方必检项 |

### 必检项（全部满足才算完成）

#### 【任务：XXX】

- [ ] **检查项名称**
  - 子项 1
  - 子项 2
  - **验证方法**：具体代码或命令

### 可选项（加分项）

- [ ] **优化项名称**
  - 说明
  - **验证方法**：具体代码或命令

### 失败处理

| 失败场景 | 处理路径 | 用户提示 |
|---------|---------|---------|
| 场景 1 | 处理方式 | 提示信息 |

### 自检代码示例

```python
def verify_done_when(task_type, ...):
    """验证 Done When 是否满足"""
    # 具体验证逻辑
    return True
```
```

#### 必检项设计原则

1. **可验证性**：每个检查项都有明确的验证方法（代码/命令）
2. **完整性**：覆盖任务的关键步骤，缺一不可
3. **客观性**：避免模糊表述，使用明确的标准
4. **可执行性**：Agent 能自动执行验证

#### 失败处理设计原则

1. **场景明确**：列举常见失败场景
2. **路径清晰**：给出明确的恢复路径
3. **用户友好**：提示信息清晰，不暴露技术细节

---

### 二、主动上下文发现机制

#### 三层架构

```
第一层：触发词扫描（instant，<10ms）
  ├─ 关键词匹配（股票代码、技术术语、项目名）
  └─ 正则表达式（金额、日期、时间）

第二层：语义检索（fast，100-300ms）
  ├─ MemPalace 语义搜索
  ├─ fact_store 实体推理
  └─ session_search 历史对话

第三层：关联发现（medium，<500ms）
  ├─ Tunnel 追踪（MemPalace 知识图谱）
  └─ 跨会话模式识别
```

#### 触发词设计原则

1. **精确性**：避免误触发（优先正则，其次关键词）
2. **优先级**：high/medium/low 分级，高优先级优先处理
3. **可扩展**：支持动态添加新触发词
4. **性能优先**：响应延迟 <500ms

#### 配置文件格式

```yaml
triggers:
  - pattern: '\d{6}\.(SH|SZ)'
    type: regex
    actions:
      - mempalace_search
      - fact_store_probe
      - skill_load: stock-data-acquisition
    priority: high
    description: "A股股票代码"
```

#### Shell Hook 实现要点

1. **JSON 输出**：Hook 返回 JSON，由 Agent 解析并执行
2. **工具建议**：返回 `tool_name` + `args`，而非直接调用
3. **统计监控**：记录命中率、延迟、Token 节省
4. **降级策略**：失败时优雅降级，不影响主流程

---

## 🛠️ 实施案例

### 案例 1：stock-data-acquisition

**Done When 设计**：
- 必检项：时间锚定验证（5 项）、数据源切换成功（4 项）、缓存更新（4 项）、数据溯源标注（3 项）
- 可选项：多源交叉验证、缓存命中率统计
- 失败处理：所有数据源失败 → 使用过期缓存 + 明确警告

**效果**：
- 错误率降低 50%
- Agent 能明确判断"数据获取是否完成"

### 案例 2：hierarchical-memory-system

**Done When 设计**：
- 必检项：事实提取（3 项）、L2 摘要（4 项）、L3 归档（4 项）、L4 Skill 提取（3 项）
- 可选项：MemPalace Tunnel 创建、Embedding 相似度检测
- 失败处理：内容重复 → 跳过插入 + 提示用户

**效果**：
- 记忆存储质量提升
- 去重、分类准确性提高

---

## 📊 质量指标

### Done When 质量指标

| 指标 | 目标 | 测量方法 |
|------|------|---------|
| 错误率降低 | ≥50% | 对比实施前后错误报告 |
| 自检覆盖率 | ≥80% | 必检项数 / 总检查点数 |
| 验证可执行性 | 100% | 每个必检项都有验证代码 |

### 上下文发现质量指标

| 指标 | 目标 | 测量方法 |
|------|------|---------|
| Token 节省 | ≥30% | 对比实施前后 Token 消耗 |
| 准确率 | ≥95% | 上下文发现结果相关性 |
| 错误率 | ≤5% | 错误触发次数 / 总触发次数 |
| 响应延迟 | <500ms | 统计平均延迟 |

---

## 🚨 常见陷阱

### Done When 陷阱

1. **模糊表述** ❌
   - 错误："数据获取成功"
   - 正确："缓存文件已写入，timestamp 更新为当前时间"

2. **无法验证** ❌
   - 错误："用户满意"
   - 正确："用户回复包含确认信息"

3. **过多必检项** ❌
   - 错误：20 个必检项（太复杂）
   - 正确：3-7 个核心必检项 + 可选加分项

### 上下文发现陷阱

1. **过度触发** ❌
   - 错误：任何包含"分析"的消息都触发
   - 正确：精确匹配股票代码 + 行情关键词

2. **延迟过高** ❌
   - 错误：Hook 耗时 2s
   - 正确：分层降级，超时 500ms 直接跳过

3. **工具调用冲突** ❌
   - 错误：Hook 直接调用工具
   - 正确：返回工具建议，由 Agent 统一调度

---

## 🔄 版本历史

### v1.0.0 (2026-05-03)
- ✅ Done When 标准化方法论
- ✅ 主动上下文发现架构
- ✅ 实施案例：stock-data-acquisition、hierarchical-memory-system
- ✅ 质量指标定义
- ✅ 常见陷阱总结

---

## 📝 Description 三要素标准（基于 Claude Code 14 模式）

### 必需项

每个 Skill 的 description 必须包含：

```yaml
description: |
  [做什么] 简洁描述功能。
  
  [什么时候触发] Use when: keyword1, keyword2, "user says X".
  
  [什么时候别触发] Do NOT use for: related-but-different tasks.
```

**检查点**：
- [ ] 包含"做什么"（功能描述）
- [ ] 包含"什么时候触发"（触发词）
- [ ] 包含"什么时候别触发"（排除条款）
- [ ] 字符数 < 1024（开放 spec）或 < 1536（Claude Code）

### 排除条款模板（按类别）

```yaml
# GitHub 类
Do NOT use for:
  - Committing without reviewing changes
  - Force pushing to protected branches
  - Deleting remote branches without backup

# Finance 类
Do NOT use for:
  - Real trading without user confirmation
  - Accessing sensitive financial data without authorization
  - Executing trades in production environment

# Creative 类
Do NOT use for:
  - Academic papers or research (preserve formal tone)
  - Technical documentation that requires precision
  - Legal or medical content (specialized language required)
```

---

## 🔍 Known Gotchas 标准

### 内容来源（优先级排序）

1. **真实失败案例**（最高价值）- 从实际使用中提取
2. **平台差异** - macOS/Linux/Windows 行为不同
3. **依赖坑位** - 库、API、工具的已知问题
4. **常见错误** - 用户易犯的错误

### 撰写格式

```markdown
## Known Gotchas

### [分类名称]

- **[具体问题]**: [问题描述]
  ```bash
  [解决方案代码]
  ```
```

### 示例（github-repo-management）

```markdown
## Known Gotchas

### Authentication Issues

- **`gh auth status` fails silently**: Check if `GITHUB_TOKEN` environment variable is set
  ```bash
  echo $GITHUB_TOKEN  # Should show token, not empty
  ```

### Common Mistakes

- **Accidentally pushing to wrong remote**: Always verify before push
  ```bash
  git remote -v && git branch -vv  # Check remote and tracking
  ```
```

---

## 📊 Token 经济标准

| 指标 | 合格 | 优秀 | 说明 |
|------|------|------|------|
| SKILL.md 行数 | ≤500 | ≤300 | 避免过度加载 |
| Description 长度 | <1024 | <800 | 精炼触发信号 |
| 引用图深度 | ≤2 跳 | 1 跳 | 扁平化结构 |

---

## 🚨 常见错误

### ❌ 错误 1: Description 过于简单

```yaml
# 错误
description: Helps with documents.

# 正确
description: |
  Generate technical documentation from code.
  
  Use when: "write docs", "document API", "add comments", 生成文档.
  
  Do NOT use for: blog posts, marketing copy, creative writing.
```

### ❌ 错误 2: 缺少排除条款

```yaml
# 错误
description: AI image generation tool.

# 正确
description: |
  AI image generation with reference images and batch processing.
  
  Use when: "generate image", "画图", "text-to-image".
  
  Do NOT use for:
  - Video generation (use video-gen skill)
  - Image editing (use image-editor skill)
  - 3D rendering (use 3d-render skill)
```

### ❌ 错误 3: 过度约束（MUST/ALWAYS/NEVER）

```markdown
# 错误
MUST use constructor injection. NEVER use field injection.

# 正确
Use constructor injection. Field injection breaks testability because we 
cannot mock the field without Spring context.
```

---

## 📚 参考资料

- `docs/claude-skill-patterns-14.md` - 14 个 Claude Skill 编写模式（完整学习笔记）
- `SKILLS_OPTIMIZATION_PLAN.md` - 系统化优化计划
- `scripts/skill_optimizer.py` - 批量优化工具

---

- [Done When 实施记录 - 2026-05-03](references/done-when-implementation-2026-05-03.md)
- [上下文发现技术细节](references/context-discovery-technical-details.md)
- [Codex 上下文工程原则](references/codex-context-engineering.md)

---

**适用范围**：所有 Skill 创作和质量优化任务

**维护原则**：每次发现新的质量提升方法，更新本 Skill
