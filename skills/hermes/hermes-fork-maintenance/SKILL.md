---
skill: hermes-fork-maintenance
name: Hermes Fork 仓库维护
version: 1.0.0
description: 保守式更新 Hermes Agent fork 仓库，跟踪上游更新并保护本地修改
tags:
  - hermes
  - git
  - fork
  - maintenance
---

# Hermes Fork 仓库维护

## 概述

定期维护 `https://github.com/54laowang/hermes-agent` fork 仓库，采用**保守式更新策略**跟踪上游更新，同时保护本地修改不被覆盖。

## 触发条件

- 用户提到"保守式更新"、"更新 fork"、"合并上游"
- 需要同步上游 bug 修复或新功能
- 定期维护任务

## 保守式更新流程

### 1. 检查上游更新

```bash
cd ~/.hermes/hermes-agent
git fetch origin
git status
```

检查：
- 本地分支状态
- 上游新提交数量
- 是否有分叉（diverged）

### 2. 审查上游变更

```bash
# 查看上游新提交列表
git log --oneline origin/main --not main | head -20

# 查看变更统计
git diff --stat HEAD origin/main
```

**关注点**：
- Bug 修复数量
- 新功能数量
- 是否有破坏性变更
- 是否影响本地修改的文件

### 3. 执行合并

```bash
# 保守式合并（保留本地修改）
git merge origin/main --no-edit
```

**冲突处理原则**：
- 本地修改优先保留
- 如果是 README 冲突，手动合并上游新内容 + 本地自定义内容
- 记录冲突解决过程

### 4. 验证合并结果

```bash
# 查看合并提交
git log --oneline -3

# 验证本地修改保留
grep -A 5 "本地关键内容" README.md
```

### 5. 推送到 Fork

```bash
git push user-fork main
```

**Fork 远程配置**：
```bash
# 查看远程配置
git remote -v

# 预期输出：
# origin    https://github.com/NousResearch/hermes-agent (upstream)
# user-fork https://github.com/54laowang/hermes-agent (fork)
```

## 本地保护内容

以下内容需要保护，合并时不可覆盖：

### README 自定义章节
- 🧬 达尔文进化方法论实施
- 📚 记忆系统优化
- 其他本地增强内容

### 本地增强文件
- `~/.hermes/context_triggers.yaml` — 触发词库
- `~/.hermes/hooks/context_discovery.py` — 上下文发现 Hook
- `~/.hermes/memory/darwin-evolution/` — Darwin 进化记录

## 用户偏好

- **保守式更新**：不使用 `git pull --rebase`，避免破坏本地历史
- **保留修改**：README 等本地修改文件需要手动验证保留
- **Fork 推送**：使用 `user-fork` 远程而非 `origin`
- **记录归档**：每次更新完成后记录到 fact_store

## 常见场景

### 场景 1：纯上游 bug 修复

直接合并，无冲突风险。

### 场景 2：README 冲突

1. 查看冲突内容
2. 手动合并：保留本地章节 + 整合上游新章节
3. 验证完整性
4. 提交并推送

### 场景 3：大规模重构

1. 评估上游变更范围
2. 暂存本地修改（`git stash`）
3. 合并上游
4. 手动恢复本地修改
5. 测试验证

## 完成判据 (Done When)

必检项：
- [ ] 上游提交已审查并记录数量
- [ ] 合并已完成且无未解决冲突
- [ ] 本地修改已验证保留（grep 关键内容）
- [ ] 已推送到 `user-fork` 远程
- [ ] 已记录到 fact_store

可选项：
- [ ] README 自定义章节完整
- [ ] 本地增强文件未受影响

## 相关文件

- `references/update-history.md` — 更新历史记录（按日期记录合并详情）
- `scripts/verify-local-modifications.sh` — 本地修改验证脚本（合并后自动检查）

## 注意事项

- **禁止使用 `origin` 推送**：origin 指向官方仓库，无推送权限
- **禁止强制推送**：会破坏 fork 历史
- **优先保留本地修改**：遇到冲突时以本地为准

## 更新记录

- 2026-05-04：v1.0.0 初版，基于 61 commits 合并经验创建
