# Hermes Agent 架构审计误报分类指南

基于 2026-04-30 的实际审计结果（青铜时代，30/100，121 issues）整理。

## 典型误报模式

### 1. 测试数据中的敏感信息

**检测器**: Hardcoded Secrets
**严重性**: CRITICAL
**症状**: `Secret pattern found at test_redact.py:70`

**误报原因**:
- 测试文件中包含模拟的 API Key/Token
- 用于验证敏感信息脱敏功能
- 文件名通常为 `test_redact.py`, `test_secrets.py`, `test_credentials.py`

**验证方法**:
```bash
# 检查文件上下文
grep -B 5 -A 5 "MY_SECRET_TOKEN" tests/agent/test_redact.py
# 如果看到 assert 语句验证脱敏功能，则为测试数据
```

**处理方式**:
```yaml
# .agchk.yaml
exclude_patterns:
  - "tests/**/test_redact.py"
```

---

### 2. 多智能体编排蔓延

**检测器**: Internal Orchestration Sprawl
**严重性**: HIGH
**症状**: "Too many planning, routing, delegation, scheduling, and recovery layers"

**误报原因**:
- Hermes 设计为多智能体系统
- 支持并行委派、监察者模式、Tool Router
- 多层编排是架构选择，不是设计缺陷

**Hermes 架构验证**:
```
agent/tool_router*.py        → Tool Router v2.0 (智能路由)
agent/self_evolution*.py     → 自进化架构 (5层闭环)
tools/supervisor_integration.py → 监察者模式 (wrapper)
```

**处理方式**:
```yaml
# .agchk.yaml
design_choices:
  internal_orchestration:
    rationale: "Multi-agent orchestration system by design"
```

---

### 3. 内存新鲜度混乱

**检测器**: Memory Freshness Confusion
**严重性**: HIGH
**症状**: "Multiple checkpoints, archives, summaries, histories, and session notes overlap"

**误报原因**:
- Hermes 采用四层记忆架构
- L1 MemPalace (索引层) + L2 fact_store (事实层) + L3 SOP (程序层) + L4 session_search (归档层)
- 多内存表面是分层设计的核心特性

**Hermes 记忆架构**:
```
L1: ~/.hermes/mempalace/          → 快速定位索引
L2: ~/.hermes/memory_store.db     → fact_store 向量推理
L3: ~/.hermes/sop_store.json      → 程序性知识
L4: ~/.hermes/sessions/           → session_search 归档
```

**处理方式**:
```yaml
design_choices:
  memory_surfaces:
    rationale: "Four-layer memory architecture by design"
```

---

### 4. 启动表面蔓延

**检测器**: Startup Surface Sprawl
**严重性**: HIGH
**症状**: "Multiple startup paths without a clear canonical boot flow"

**误报原因**:
- Hermes 支持多平台：CLI、Web UI、Gateway、API Server
- 每个平台有独立的启动入口
- 这是跨平台设计的必然结果

**Hermes 启动入口**:
```bash
# CLI 模式
hermes

# Web UI 模式
hermes --web

# Gateway 模式（多平台消息）
python gateway/run.py

# API Server 模式
hermes api-server
```

**处理方式**:
```yaml
design_choices:
  startup_surfaces:
    rationale: "Multi-platform support requires multiple entry points"
```

---

### 5. 运行时表面蔓延

**检测器**: Runtime Surface Sprawl
**严重性**: HIGH
**症状**: "Mixing too many runtime surfaces"

**误报原因**:
- Hermes 是全栈平台
- Python 后端 + TypeScript 前端
- 多运行时是技术栈选择

**Hermes 运行时**:
```
Python:   run_agent.py, cli.py, gateway/, agent/
TS:       ui-tui/, web/src/
```

**处理方式**:
```yaml
design_choices:
  runtime_surfaces:
    rationale: "Full-stack agent platform - Python backend + TS frontend"
```

---

### 6. 角色扮演切换编排

**检测器**: Role-Play Handoff Orchestration
**严重性**: HIGH
**症状**: "Agent systems that mirror company departments"

**误报原因**:
- Hermes Skill 系统支持角色专业化
- PM、架构师、编码、审查等角色是方法论，不是蔓延
- 通过 Skill 定义角色边界和职责

**Hermes Skill 示例**:
```
~/.hermes/skills/
├── engineering-engineer.code-reviewer
├── project-management-project-shepherd
├── specialized-chief-of-staff
└── ...
```

**处理方式**:
```yaml
design_choices:
  skill_system:
    rationale: "Skill system supports role-based agents - methodology not sprawl"
```

---

### 7. Shell 执行风险

**检测器**: Unrestricted Code Execution
**严重性**: MEDIUM/CRITICAL
**症状**: "subprocess(shell=True), exec(), eval()"

**误报原因**:
- Hermes 提供 Terminal 工具
- Shell 执行是核心功能，用于运行系统命令
- 已有容器化隔离机制（environments/）

**验证方法**:
```bash
# 检查是否有环境隔离
ls tools/environments/
# docker, ssh, modal, daytona, singularity 等隔离后端
```

**处理方式**:
```yaml
design_choices:
  shell_execution:
    rationale: "Terminal tool requires shell execution - containerized isolation available"
```

---

## 快速分类流程

```python
# 审计结果解析脚本
import json

with open('/tmp/hermes-audit-results.json') as f:
    data = json.load(f)

# 自动分类
false_positives = []
real_issues = []

for finding in data['findings']:
    # 测试数据误报
    if 'test_redact.py' in str(finding.get('evidence_refs', [])):
        false_positives.append(finding)
    
    # 多智能体设计选择
    elif finding['title'] in [
        'Internal orchestration sprawl detected',
        'Memory freshness / generation confusion detected',
        'Startup surface sprawl detected',
        'Runtime surface sprawl detected',
        'Role-play handoff orchestration detected',
    ]:
        false_positives.append(finding)
    
    # 其他需要人工审查
    else:
        real_issues.append(finding)

print(f"误报: {len(false_positives)}")
print(f"真实问题: {len(real_issues)}")
```

---

## 配置文件最佳实践

### 最小配置

```yaml
exclude_patterns:
  - "tests/**/test_redact.py"
  - "build/**"
  - "node_modules/**"
  - ".venv/**"
```

### 推荐配置

```bash
# 使用 Hermes 专用模板
cp ~/.hermes/skills/agent-architecture/agchk-agent-self-audit/templates/hermes-agchk.yaml .agchk.yaml
```

### 完整配置

参考 `templates/hermes-agchk.yaml`，包含：
- 所有常见误报排除
- 设计选择声明
- 项目特定规则
- 持续审计配置

---

## 审计报告保存

```bash
# 保存到项目目录
cp /tmp/hermes-audit-results.json AGCHK-AUDIT-$(date +%Y%m%d).json
cp /tmp/hermes-audit-report.md AGCHK-ARCHITECTURE-AUDIT-$(date +%Y%m%d).md

# 提交到版本控制
git add AGCHK-*.json AGCHK-*.md .agchk.yaml
git commit -m "docs: 添加架构审计报告"
```

---

**文档版本**: 2026-04-30
**适用版本**: Hermes Agent v2.x
**审计工具**: agchk 1.2.6
