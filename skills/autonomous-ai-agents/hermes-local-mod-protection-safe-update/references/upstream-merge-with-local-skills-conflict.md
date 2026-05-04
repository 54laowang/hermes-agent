# 合并上游时本地 Skills 目录冲突处理

## 问题场景

当 fork 的 Hermes Agent 仓库中，`skills/` 目录是一个独立的 Git 仓库（submodule 或嵌套仓库），而上游也有 `skills/` 目录时，合并会产生冲突。

### 症状

```bash
error: The following untracked working tree files would be overwritten by merge:
    skills/apple/DESCRIPTION.md
    skills/apple/apple-notes/SKILL.md
    ...
Aborting
Merge with strategy ort failed.
```

### 根本原因

1. 本地 `skills/` 目录包含 `.git` 子目录（是独立仓库）
2. 上游 `skills/` 也是仓库或目录
3. Git 无法合并两个独立的仓库

---

## 解决方案

### 方案 1: 保留本地 Skills（推荐）

**适用场景**: 你的 skills 目录有大量自定义内容，必须保留

```bash
# 1. 临时移除本地 skills 目录
mv skills skills_backup

# 2. 合并上游代码
git merge upstream/main --allow-unrelated-histories -m "Merge upstream main"

# 3. 解决其他冲突后提交
git add -A
git commit -m "Merge upstream main"

# 4. 恢复本地 skills
rm -rf skills  # 删除上游的 skills（如果有）
mv skills_backup skills

# 5. 提交恢复
git add -A
git commit -m "合并上游后恢复本地 skills 目录"
```

### 方案 2: 使用上游 Skills

**适用场景**: 你愿意放弃本地 skills，使用上游版本

```bash
# 1. 备份本地 skills（以防需要恢复特定文件）
cp -r skills skills_backup_$(date +%Y%m%d)

# 2. 删除本地 skills
rm -rf skills

# 3. 合并上游
git merge upstream/main --allow-unrelated-histories

# 4. skills 目录会自动从上游获取
```

### 方案 3: 将 Skills 转为 Submodule

**适用场景**: 你想保持 skills 作为独立仓库，并正确管理

```bash
# 1. 备份 skills 目录
cp -r skills /tmp/skills_backup

# 2. 移除嵌套的 .git 目录
rm -rf skills/.git

# 3. 合并上游
git merge upstream/main --allow-unrelated-histories

# 4. 如果想转为 submodule（可选）
git submodule add <your-skills-repo-url> skills
git commit -m "chore: 将 skills 转为 submodule"
```

---

## 最佳实践

### 检查 Skills 是否为独立仓库

```bash
# 检查是否存在 .git
ls -la skills/.git

# 检查是否是 submodule
git submodule status
```

### 预防措施

在每次合并上游前，检查：

```bash
# 1. 检查 skills 状态
git status | grep skills

# 2. 如果 skills 被忽略（在 .gitignore 中）
git check-ignore skills/

# 3. 如果是嵌套仓库，先移除再合并
```

### 仓库配置

**推荐配置** - 在 `.gitignore` 中忽略 skills 目录：

```gitignore
# Skills 是独立仓库，不纳入主仓库管理
skills/
```

这样：
- 合并上游时不会冲突
- 你的 skills 保持独立管理
- 可以通过其他方式同步（如单独的 git 仓库）

---

## 相关案例

### 案例: 2026-05-04 Hermes Agent 合并上游

**背景**:
- 本地 `skills/` 是独立 Git 仓库（包含自定义 skills）
- 上游 `nousresearch/hermes-agent` 也有 `skills/` 目录

**执行流程**:
```bash
# 1. 添加上游
git remote add upstream https://github.com/nousresearch/hermes-agent.git
git fetch upstream

# 2. 移除本地 skills
mv skills skills_backup

# 3. 合并
git merge upstream/main --allow-unrelated-histories

# 4. 解决 README.md 冲突（使用上游版本）
git checkout --theirs README.md
git add README.md

# 5. 移除冲突的 skills~HEAD 目录
git rm -rf skills~HEAD

# 6. 提交合并
git commit -m "Merge upstream hermes-agent main branch"

# 7. 恢复本地 skills
rm -rf skills
mv skills_backup skills

# 8. 提交恢复
git add -A
git commit -m "合并上游后恢复本地 skills 目录"

# 9. 推送
git push origin main
```

**结果**:
- ✅ 上游所有代码已合并
- ✅ 本地 skills 完整保留
- ✅ 仓库历史完整

---

## 常见问题

### Q: 为什么 `git stash --include-untracked` 不起作用？

A: Stash 无法处理嵌套仓库（nested repository）。即使暂存后，合并时仍会检测到冲突。

### Q: 如何验证 skills 是否独立仓库？

A: 检查是否存在 `.git` 目录：
```bash
ls -la skills/.git
# 如果存在，说明是独立仓库
```

### Q: 合并后 skills 权限问题怎么办？

A: 确保恢复后权限正确：
```bash
chmod -R 755 skills/
```

### Q: 如何同步 skills 更新？

A: 如果 skills 是独立仓库，可以单独管理：
```bash
cd skills
git pull origin main
```

---

## 相关文档

- `SKILL.md` - Hermes Fork 仓库完整维护指南
- `references/env-backup-system.md` - 环境变量备份系统
