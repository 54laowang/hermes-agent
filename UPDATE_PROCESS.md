# 保守式更新流程

本文档记录如何安全地更新 Hermes Agent 并保留本地定制内容。

## 📋 标准更新流程

### 1. 更新前准备

```bash
# 进入项目目录
cd ~/.hermes/hermes-agent

# 检查当前状态
git status

# 备份当前修改（可选，但推荐）
mkdir -p ~/.hermes/patch-backups
git diff > ~/.hermes/patch-backups/pre-update-$(date +%Y%m%d_%H%M%S).patch
```

### 2. 同步上游

```bash
# 拉取上游更新
git fetch origin

# 查看待合并的提交数
git log --oneline HEAD..origin/main | wc -l

# 使用 rebase 合并（保持线性历史）
git pull --rebase origin main
```

### 3. 解决冲突（如有）

如果出现冲突：

```bash
# 查看冲突文件
git status

# 编辑冲突文件，保留本地优化代码
# 冲突标记格式:
# <<<<<<< Updated upstream
# 上游代码
# =======
# 本地代码
# >>>>>>> Stashed changes

# 标记冲突已解决
git add <冲突文件>

# 继续 rebase
GIT_EDITOR=true git rebase --continue
```

**冲突解决原则：**
- ✅ **保留本地性能优化**（浅拷贝、缓存等）
- ✅ **融合上游新功能**（vision 检测等）
- ✅ **保持代码简洁**
- ❌ **不要简单选择一方，要合并双方优势**

### 4. 验证功能

```bash
# 激活虚拟环境
source .venv/bin/activate

# 测试 Tool Router
python3 -c "from agent.tool_router import ToolRouter; print('✓ Tool Router 正常')"

# 测试自进化模块
python3 -c "from agent.self_evolution_agent import SelfEvolvingRouter; print('✓ 自进化模块正常')"

# 测试核心 Agent
python3 -c "from run_agent import AIAgent; print('✓ AIAgent 正常')"
```

### 5. 更新文档

```bash
# 使用自动化脚本更新 README
python3 scripts/update_readme.py "更新内容描述"

# 或手动编辑 README_CN.md
# 在"## 📋 更新日志"部分添加新条目
```

### 6. 提交并推送

```bash
# 提交所有更改
git add -A
git commit -m "docs: 更新 README - 记录 $(date +%Y-%m-%d) 更新"

# 推送到您的 Fork
git push user-fork main
```

---

## 🛡️ 本地保护的关键修改

### 必须保留的优化

1. **run_agent.py - 浅拷贝优化**
   ```python
   # 位置: _prepare_anthropic_messages_for_api 方法
   # 原: transformed = deepcopy(api_messages)  # 0.088ms
   # 改: transformed = [dict(msg) for msg in api_messages]  # <0.001ms
   # 性能提升: 50-100x
   ```

2. **agent/tool_router*.py - Tool Router v2.0**
   - 智能工具选择
   - Token 节省 60-70%
   - 响应时间 0.07ms

3. **agent/self_evolution*.py - 自进化架构**
   - 6 个核心模块
   - 行为学习和优化

4. **gateway/platforms/base.py - split-brain 修复**
   - 死锁问题修复
   - 网关稳定性提升

---

## 📊 冲突解决案例

### 案例 1: run_agent.py 冲突

**冲突场景：**
- 上游添加了 vision 模型检测逻辑
- 本地有浅拷贝性能优化

**解决方案：**
```python
def _prepare_anthropic_messages_for_api(self, api_messages: list) -> list:
    # 保留: 快速路径优化（本地）
    if not any(...):
        return api_messages
    
    # 融合: vision 模型检测（上游）
    if self._model_supports_vision():
        return api_messages
    
    # 保留: 浅拷贝优化（本地）
    transformed = [dict(msg) for msg in api_messages]  # ← 关键优化
    # ... 处理逻辑
    return transformed
```

**结果：** 双方优势合并，零性能损失

---

## 🔧 自动化脚本

### update_readme.py

自动更新 README_CN.md 的更新日志：

```bash
python3 scripts/update_readme.py "修复了 XX 问题，优化了 YY 性能"
```

功能：
- 自动添加日期和更新内容
- 更新"最后更新"时间戳
- 保持格式一致性

---

## 📝 检查清单

每次更新前确认：

- [ ] 已备份本地修改
- [ ] 已提交未提交的更改
- [ ] 已查看待合并提交数
- [ ] 准备好解决冲突

每次更新后确认：

- [ ] 功能验证通过
- [ ] 性能优化保留
- [ ] README 已更新
- [ ] 已推送到 Fork

---

## 🚨 紧急回滚

如果更新后出现问题：

```bash
# 方式 1: 使用备份 patch
git checkout main
git reset --hard origin/main
git am ~/hermes-backups/*.patch

# 方式 2: 使用 git reflog
git reflog
git reset --hard HEAD@{N}  # N 为回退步数

# 方式 3: 重新应用 stash
git stash list
git stash pop stash@{0}
```

---

## 📚 相关文档

- [备份文件说明](~/hermes-backups/README.md)
- [Tool Router 文档](agent/tool_router.py)
- [自进化架构文档](agent/self_evolution_agent.py)

---

**维护者**: @54laowang  
**最后更新**: 2026-04-29  
**版本**: v1.0
