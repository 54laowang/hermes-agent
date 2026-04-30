# 自动化安全改进机制使用指南

**建立日期**: 2026-04-30
**维护者**: Hermes Agent Team

---

## 🎯 概述

本机制提供三层安全防护：

1. **Pre-commit Hook** - 提交前自动检查
2. **CI/CD 集成** - 定期自动审计
3. **改进追踪** - 记录改进效果

---

## 📦 安装

### 1. 安装依赖

```bash
# 安装 pre-commit
pip install pre-commit

# 安装 agchk
pip install agchk

# 安装其他工具
pip install black isort flake8
```

### 2. 激活 Pre-commit Hooks

```bash
cd ~/.hermes/hermes-agent

# 安装 hooks
pre-commit install

# 可选：安装 pre-push hooks（更严格的检查）
pre-commit install --hook-type pre-push
```

### 3. 验证安装

```bash
# 运行所有 hooks
pre-commit run --all-files

# 运行特定 hook
pre-commit run security-check --all-files
```

---

## 🔧 使用方法

### Pre-commit Hook

**自动触发**：
- 每次 `git commit` 前自动运行
- 发现问题会阻止提交

**手动运行**：
```bash
# 检查所有文件
pre-commit run --all-files

# 检查特定文件
pre-commit run --files path/to/file.py

# 跳过 hooks（不推荐）
git commit --no-verify
```

**配置修改**：
编辑 `.pre-commit-config.yaml`：
```yaml
# 禁用某个 hook
repos:
  - repo: local
    hooks:
      - id: security-check
        stages: [manual]  # 改为手动触发

# 添加新的检查
      - id: my-custom-check
        name: My Custom Check
        entry: python scripts/my_check.py
        language: system
```

### CI/CD 集成

**自动触发**：
- Push 到 main/develop 分支
- Pull Request 到 main 分支
- 每周一早上 6:00（定时审计）

**手动触发**：
1. 访问 GitHub Actions 页面
2. 选择 "Security & Architecture Audit" workflow
3. 点击 "Run workflow"

**查看结果**：
- GitHub Actions → Security & Architecture Audit
- Artifacts 下载审计报告
- Step Summary 查看摘要

**配置通知**：
在 GitHub 仓库设置添加 Secret：
- `SLACK_WEBHOOK_URL`: Slack webhook 地址（可选）

### 改进追踪

**记录改进**：
```bash
python scripts/track_improvements.py record "P0 权限策略加固"
```

**查看状态**：
```bash
python scripts/track_improvements.py status
```

**查看趋势**：
```bash
python scripts/track_improvements.py trend
```

**生成报告**：
```bash
python scripts/track_improvements.py report
```

---

## 🔍 安全检查脚本

### 直接运行

```bash
# 检查当前目录
python scripts/security_check.py

# 检查特定文件
python scripts/security_check.py path/to/file.py

# 静默模式（只返回退出码）
python scripts/security_check.py --quiet
```

### 检查项

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| `subprocess(shell=True)` | HIGH | 命令注入风险 |
| `exec()/eval()` | MEDIUM | 代码注入风险 |
| 硬编码密钥 | HIGH | 凭证泄露风险 |
| 危险导入 | MEDIUM | pickle/marshal 等 |

### 排除规则

脚本自动排除：
- 测试文件（`test_*.py`）
- 注释行（`#`）
- 示例文件（`example`/`template`）
- 配置模板

手动排除：
```python
# 在代码中添加注释
subprocess.run(cmd, shell=True)  # noqa: security
```

---

## 📊 架构审计

### 运行审计

```bash
# 基础审计
agchk audit --profile personal . -o audit.json -r report.md

# 企业级审计（更严格）
agchk audit --profile enterprise . -o audit.json -r report.md

# 失败时退出
agchk audit --profile personal . --fail-on high
```

### 配置排除

编辑 `.agchk.yaml`：
```yaml
exclude_patterns:
  - "tests/**/test_redact.py"
  - "build/**"

false_positive_markers:
  - "# TEST DATA"
  - "# pragma: no cover"

design_choices:
  internal_orchestration:
    rationale: "Multi-agent system by design"
```

### 解读结果

**文明等级**：
| 等级 | 分数范围 | 说明 |
|------|---------|------|
| 石器时代 | 0-20 | 原始提示 + 工具调用 |
| 青铜时代 | 21-40 | 方法论层 + 基础记忆 |
| 铁器时代 | 41-60 | 状态恢复 + 技能系统 |
| 蒸汽机时代 | 61-75 | 语义分页 + 页面故障恢复 |
| 内燃机时代 | 76-85 | 印象指针 + 能力表 |
| 新能源时代 | 86-95 | 公平调度 + 语义 VFS |
| 人工智能时代 | 96-100 | 完整 Agent OS |

---

## 🔄 工作流集成

### 开发流程

```
1. 编写代码
   ↓
2. git commit
   ↓
3. Pre-commit Hook 自动运行
   ├─ ✅ 通过 → 提交成功
   └─ ❌ 失败 → 阻止提交，修复问题
   ↓
4. git push
   ↓
5. GitHub Actions 自动运行
   ├─ Security Check
   ├─ Architecture Audit
   └─ Code Quality Check
   ↓
6. 查看审计报告
   ├─ 发现问题 → 修复 → 回到步骤 1
   └─ 无问题 → 合并成功
```

### 定期审计

**每周审计**：
- 时间：每周一早上 6:00
- 内容：完整架构审计
- 结果：生成报告 + 发送通知

**改进追踪**：
- 每次改进后运行 `track_improvements.py record`
- 定期查看趋势：`track_improvements.py trend`
- 生成季度报告：`track_improvements.py report`

---

## 🛠️ 故障排查

### Pre-commit Hook 失败

**问题**: Hook 运行失败
**解决**:
```bash
# 查看详细日志
pre-commit run security-check --all-files --verbose

# 清除缓存
pre-commit clean

# 重新安装
pre-commit install --install-hooks
```

### agchk 审计超时

**问题**: 审计时间过长
**解决**:
```bash
# 排除大目录
# 在 .agchk.yaml 添加：
exclude_patterns:
  - "node_modules/**"
  - ".venv/**"
  - "build/**"
```

### CI/CD 失败

**问题**: GitHub Actions 失败
**解决**:
1. 查看 Actions 日志
2. 下载 Artifacts 查看详细报告
3. 本地运行相同命令验证
4. 修复问题后重新 push

---

## 📈 最佳实践

### 1. 提交前检查

**推荐**：
```bash
# 提交前手动运行
pre-commit run --all-files

# 或使用 git alias
git config alias.c '!pre-commit run --all-files && git commit'
```

### 2. 定期改进

**推荐流程**：
```
1. 每周一查看审计报告
2. 选择优先级最高的问题
3. 修复并记录改进
4. 查看改进趋势
5. 调整改进计划
```

### 3. 团队协作

**推荐**：
- PR 必须通过安全检查
- 定期分享改进报告
- 建立安全编码规范
- 培训团队成员

---

## 📚 参考资料

### 内部文档

- [P0 权限策略改进验证报告](SECURITY-IMPROVEMENT-P0-PERMISSION-POLICY.md)
- [架构审计报告](AGCHK-ARCHITECTURE-AUDIT-20260430.md)
- [安全配置](.agchk.yaml)

### 外部资源

- [Pre-commit 文档](https://pre-commit.com)
- [agchk 文档](https://github.com/huangrichao2020/agchk)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

---

## 🎯 下一步

### 短期（1周）

- [ ] 团队培训安全编码规范
- [ ] 建立问题响应流程
- [ ] 配置 Slack 通知

### 中期（1月）

- [ ] 添加更多安全检查规则
- [ ] 建立 RBAC 权限模型
- [ ] 集成依赖扫描

### 长期（3月）

- [ ] 建立安全认证体系
- [ ] 实现权限策略引擎
- [ ] 达到铁器时代（41-60分）

---

**维护指南**: 每月更新本文档，确保与实际流程一致。
