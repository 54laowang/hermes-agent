---
name: git-history-forensics
description: |
  Git 历史追溯与文档完整性验证 - 追踪功能/概念的引入时间、演变过程，发现文档遗漏。
  当用户问"X呢"、"Y什么时候加的"、"之前的Z呢"时使用。
  Use when user asks "what about X", "when was Y added", "what happened to Z before date".
version: 1.0.0
keywords:
  - git-history
  - forensics
  - documentation-audit
  - commit-tracing
---

# Git 历史追溯与文档完整性验证

## 触发场景

- 用户问"X呢？"、"Y怎么不见了？"
- 用户问"这个功能什么时候加的？"
- 用户问"某个日期之前的情况？"
- 需要验证文档是否完整覆盖代码变更

## 核心流程

### Step 1: 确认追溯目标

```bash
# 用户说"自进化系统呢"
# 目标：找到所有相关代码文件 + 追踪 README/文档变更
```

### Step 2: 搜索代码文件

```bash
# 找到所有相关文件
find . -name "*keyword*" -type f 2>/dev/null | grep -v ".git" | grep -v "node_modules"

# 示例：自进化系统
find . -name "*self_evolution*" -o -name "*darwin*" 2>/dev/null | grep -v ".git"
```

### Step 3: 追踪 Git 历史

```bash
# 方法1：按关键词搜索提交
git log --all --oneline --grep="keyword" | head -20

# 方法2：按文件路径搜索
git log --all --oneline -- path/to/file | head -20

# 方法3：按日期范围搜索
git log --all --oneline --after="YYYY-MM-DD" --before="YYYY-MM-DD" | head -20

# 方法4：查看具体提交详情
git show <commit-hash> --stat
git show <commit-hash> -- path/to/file
```

### Step 4: 查看文件内容

```bash
# 查看某个历史版本的文件
git show <commit-hash>:path/to/file

# 查看文件的完整 diff
git log --all -p -- path/to/file | grep -A 20 -B 5 "keyword"
```

### Step 5: 验证文档覆盖

```bash
# 检查文档是否提到该功能
grep -n "keyword" README.md
grep -n "keyword" FORK_COMPARISON_REPORT.md

# 如果文档遗漏 → 更新文档
```

## 实战案例

### 案例1：追溯"自进化系统"

```bash
# 1. 找到代码文件
find . -name "*self_evolution*" -type f
# → agent/self_evolution_agent.py 等 6 个文件

# 2. 找到引入时间
git log --all --oneline --grep="self.*evolution" | head -10
# → 找到相关提交

# 3. 追踪 README 变更
git log --all -p -- README.md | grep -A 20 "self-improving"
# → 发现 2026-03-06 首次提出 "self-improving AI agent"
```

### 案例2：追溯"Holographic Memory"

```bash
# 1. 找到代码文件
find . -name "holographic*" -type f
# → plugins/memory/holographic/ 目录

# 2. 找到引入时间
git log --all --oneline -- plugins/memory/holographic/ | head -10
# → 2026-03-29 引入

# 3. 查看提交详情
git show 44b7df409 --stat
# → 发现 HRR 算法、Trust Scoring 等核心特性
```

### 案例3：追溯"某个日期之前"

```bash
# 用户问"5月1日之前的呢"
git log --all --oneline --before="2026-05-01" -- README.md | head -30

# 找到关键提交后查看内容
git show <commit-hash>:README.md | head -50
```

## 输出格式

### 发现遗漏时

```markdown
## 📋 [功能名称] 演变历史

### [日期] (commit [hash])

**提交信息**：
```
[commit message]
```

**核心变更**：
- [变更1]
- [变更2]

**文件列表**：
- `path/to/file1` — 说明
- `path/to/file2` — 说明
```

### 更新文档时

```bash
# 补充到 README.md
# 补充到 FORK_COMPARISON_REPORT.md

git add README.md FORK_COMPARISON_REPORT.md
git commit -m "docs: 补充 [功能名称] 详细说明"
git push
```

## 常用 Git 命令速查

| 场景 | 命令 |
|------|------|
| 搜索提交信息 | `git log --all --oneline --grep="keyword"` |
| 搜索文件变更 | `git log --all --oneline -- path/to/file` |
| 按日期范围 | `git log --all --oneline --after="YYYY-MM-DD" --before="YYYY-MM-DD"` |
| 查看提交详情 | `git show <hash> --stat` |
| 查看历史文件内容 | `git show <hash>:path/to/file` |
| 查看完整 diff | `git log --all -p -- path/to/file` |

## 注意事项

1. **使用 `--all`** — 搜索所有分支，不只是当前分支
2. **使用 `rtk` 前缀** — 节省 token（如 `rtk git log`）
3. **验证文件存在** — `find` 前先确认当前目录
4. **检查文档覆盖** — 追踪完成后必须验证 README/文档是否提到
5. **提交前预览** — `git show` 查看完整内容，避免遗漏

## Done When

- [ ] 找到所有相关代码文件
- [ ] 确定**首次引入时间**和**关键变更时间**
- [ ] 查看核心代码内容（不是只看提交信息）
- [ ] 验证文档是否覆盖（README.md, FORK_COMPARISON_REPORT.md 等）
- [ ] 如果文档遗漏 → 更新文档并提交
- [ ] 更新 Memory（记住关键时间点和技术细节）
