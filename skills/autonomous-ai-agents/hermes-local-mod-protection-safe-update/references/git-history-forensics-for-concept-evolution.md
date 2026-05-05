# Git History Forensics for Concept Evolution

> 追踪概念/功能在代码库中的演变历史，用于文档完整性验证。

## 使用场景

- 用户问"X呢？"、"Y什么时候有的？"
- 文档中提到某功能，但需要验证其完整性
- 追踪概念从营销描述到技术实现的演进

## 核心命令

### 1. 查找概念引入时间

```bash
# 按关键词搜索 commit message
git log --all --oneline --grep="关键词" -- <文件路径>

# 示例：查找"自进化"概念的引入
git log --all --oneline --grep="自进化\|self.*evolution" -- README.md
```

### 2. 查看具体变更内容

```bash
# 查看某个 commit 的详细变更
git show <commit-hash> -- <文件路径>

# 查看变更统计
git show <commit-hash> --stat
```

### 3. 追踪概念演变

```bash
# 查看文件历史中的关键词演变
git log --all -p -- <文件路径> | grep -A 10 -B 5 "关键词"

# 示例：追踪 README 中"自进化"描述的变化
git log --all -p -- README.md | grep -A 20 -B 5 "self-improving\|自进化"
```

### 4. 时间范围筛选

```bash
# 指定时间范围
git log --all --oneline --after="2026-03-01" --before="2026-04-01"

# 查看某天之前的状态
git show <commit-hash>:README.md | head -30
```

## 实战案例

### 案例：追踪"自进化"概念演变

**问题**：用户问"六层自进化怎么不见了？"

**排查流程**：

```bash
# 1. 查找 README 中的"自进化"相关提交
git log --all --oneline --grep="自进化" -- README.md

# 输出：
# cd79ccd34 docs: 补充完整自进化系统 + Darwin Skill 详细说明

# 2. 查看该提交的详细变更
git show cd79ccd34 -- README.md

# 3. 向前追溯，查找概念引入
git log --all --oneline --before="2026-05-01" -- README.md | head -30

# 4. 找到关键提交
git show 2dbbedc05 -- README.md
# 输出：
# - Lead with the learning loop: autonomous skill creation, skill
#   self-improvement, memory nudges, FTS5 session search, Honcho

# 5. 查看概念变化前后的对比
git show 82f748399:README.md | head -30
# 输出：
# The fully open-source AI agent that grows with you.
```

**发现**：
- 2026-03-06 之前："grows with you"（成长）
- 2026-03-06：首次提出 "self-improving AI agent"（自进化）
- 2026-05-04：补充详细实现说明

### 案例：追踪 Holographic Memory 引入

```bash
# 1. 搜索相关提交
git log --all --oneline --grep="Holographic\|holographic"

# 2. 查看引入提交
git show 44b7df409 --stat

# 输出：
# plugins/hermes-memory-store/holographic.py | 203 ++++++++++
# plugins/hermes-memory-store/store.py       | 572 +++++++++++++++++++++++++++
```

## 文档更新最佳实践

**在更新文档前，必须先读取相关 Skill 完整内容**：

```bash
# 错误：直接编写文档（可能遗漏）
# 直接编辑 FORK_COMPARISON_REPORT.md

# 正确：先读取相关 Skill，确保完整性
skill_view(name="hierarchical-memory-system")
skill_view(name="tiancai-agent-principles")
skill_view(name="supervisor-mode")

# 然后再更新文档
```

## 概念演变时间线模板

| 时间 | 概念 | 提交 | 描述 |
|------|------|------|------|
| YYYY-MM-DD | 概念名 | commit-hash | 概念引入/变化说明 |

## 关键发现模式

1. **营销术语 → 技术实现**：概念先在 README 中出现，后在代码中实现
2. **功能分散 → 整合统一**：多个小功能逐渐整合为完整系统
3. **描述模糊 → 详细说明**：早期描述简洁，后期补充详细技术细节

## 注意事项

- ✅ 使用 `--all` 参数搜索所有分支
- ✅ 使用 `--grep` 支持正则表达式搜索
- ✅ 使用 `-p` 参数查看具体变更内容
- ⚠️ 中文关键词可能需要转义或使用双引号
- ⚠️ Git 历史可能因 rebase 而改变，注意时间线准确性
