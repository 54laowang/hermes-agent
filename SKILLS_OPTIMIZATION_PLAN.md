# Hermes Skills 系统优化计划

**基于**: 14 个 Claude Skill 编写模式
**时间**: 2026-05-05
**目标**: 提升触发率、降低 Token 消耗、增强可靠性

---

## 📊 现状分析

### 整体状况

| 指标 | 数值 | 占比 | 状态 |
|------|------|------|------|
| **总 Skills 数** | 503 | - | ✅ |
| **活跃 Skills** | 500 | 99.4% | ✅ |
| **已合并 Skills** | 1 | 0.2% | ✅ |
| **缺少排除条款** | 485 | **97.0%** | ❌ 严重 |
| **缺少 Known Gotchas** | 497 | **99.4%** | ❌ 严重 |
| **超过 500 行** | 75 | 15.0% | ⚠️ 中等 |
| **description 过短** | 100 | 20.0% | ⚠️ 中等 |
| **缺少触发词** | 457 | 91.4% | ❌ 严重 |

---

## 🎯 优化目标

### 短期目标（1周）

| 指标 | 当前 | 目标 | 改进 |
|------|------|------|------|
| 排除条款覆盖率 | 3.0% | **50%** | +47% |
| Known Gotchas 覆盖率 | 0.6% | **20%** | +19.4% |
| 触发词覆盖率 | 8.6% | **60%** | +51.4% |
| description 合格率 | 80% | **95%** | +15% |

### 中期目标（1月）

| 指标 | 当前 | 目标 | 改进 |
|------|------|------|------|
| 排除条款覆盖率 | 3.0% | **90%** | +87% |
| Known Gotchas 覆盖率 | 0.6% | **50%** | +49.4% |
| 超长 SKILL.md | 75个 | **20个** | -73% |
| 触发词覆盖率 | 8.6% | **95%** | +86.4% |

---

## 📋 优化分类

### P0：核心 Skills（立即优化）

**优先级最高**，影响面最大的 Skills：

1. **hermes-agent** (1362行) - 核心文档
2. **stock-analysis-framework** (1345行) - 财经分析核心
3. **stock-data-acquisition** (1317行) - 数据获取核心
4. **github-repo-management** (515行) - Git 操作核心
5. **humanizer** (577行) - 内容处理核心

### P1：高频使用 Skills（本周优化）

**使用频率高**，优化收益大：

1. **grid-trading-monitor** (607行) - 网格交易
2. **turix-mac** (660行) - macOS 自动化
3. **open-source-project-evaluation** (556行) - 项目评估
4. **mitmproxy-credential-interception** (544行) - 凭证拦截
5. **research-paper-writing** (2375行) - 论文写作

### P2：归档清理（批量处理）

**.archive 目录**已加入 .gitignore，需确认是否：

- ✅ 已正确标记 status: archived
- ✅ 排除条款明确
- ✅ 无重复加载风险

---

## 🔧 优化流程

### 流程 1：添加排除条款（批量）

**适用**: 所有活跃 Skills

**模板**：
```yaml
---
name: skill-name
description: |
  Brief description of what this skill does.
  
  Use when: keyword1, keyword2, scenario descriptions.
  
  Do NOT use for: related-but-different tasks.
---
```

**执行方式**：
```bash
# 批量添加排除条款模板
for skill in skills/*/SKILL.md; do
  # 检查是否已有排除条款
  if ! grep -q "NOT use" "$skill"; then
    # 添加排除条款模板
  fi
done
```

### 流程 2：拆分超长 SKILL.md

**适用**: 超过 500 行的 Skills

**原则**：
- SKILL.md < 500 行（核心逻辑 + 目录）
- 详细内容 → `references/`, `templates/`, `scripts/`
- 顶部加目录

**示例**：
```
skills/stock-analysis-framework/
├── SKILL.md              (主文档，<500行)
├── references/
│   ├── technical-analysis.md
│   ├── fundamental-analysis.md
│   └── risk-management.md
├── templates/
│   └── analysis-report.md
└── scripts/
    └── data-fetcher.py
```

### 流程 3：添加 Known Gotchas

**适用**: 核心和高频 Skills

**内容来源**：
1. 真实失败案例（最高价值）
2. 已知边界情况
3. 平台/环境差异
4. 依赖库坑位

**模板**：
```markdown
## Known Gotchas

- [具体场景]: [问题描述] → [解决方案]
- macOS `date -d` 不工作 → 使用 `gdate` (coreutils)
- Scanned PDFs return [] → Check page type first
```

### 流程 4：优化 description

**适用**: description 过短的 Skills

**检查项**：
- [ ] 包含"做什么"
- [ ] 包含"什么时候触发"（关键词、场景）
- [ ] 包含"什么时候别触发"（排除条款）
- [ ] 字符数 < 1024（开放 spec）

---

## 📝 优化模板

### 模板 1：完整 SKILL.md 结构

```markdown
---
name: skill-name
version: 1.0.0
description: |
  [做什么] 简洁描述功能。
  
  [什么时候触发] Use when: keyword1, keyword2, "user says X".
  
  [什么时候别触发] Do NOT use for: related-but-different tasks.
category: category-name
keywords:
  - keyword1
  - keyword2
triggers:
  - trigger phrase 1
  - trigger phrase 2
dependencies:
  - dependency1
---

# Skill Name

## Overview

[一句话说明]

## When to Use

[触发场景详细说明]

## When NOT to Use

[排除场景详细说明]

## How It Works

[核心逻辑]

## Known Gotchas

- [具体坑位 1]
- [具体坑位 2]

## Examples

### Example 1: [场景]
Input: ...
Output: ...

## References

- [references/file1.md](详细文档)
- [templates/template1.md](模板文件)

## Scripts

- `scripts/script1.py` - [脚本说明]
```

### 模板 2：排除条款写法

```yaml
# ✅ 正确示例
description: |
  Generate technical documentation from code.
  
  Use when: "write docs", "document API", "add comments", 生成文档.
  
  Do NOT use for: blog posts, marketing copy, creative writing.

# ❌ 错误示例
description: |
  Helps with documents.
```

### 模板 3：Known Gotchas 写法

```markdown
## Known Gotchas

### Platform Issues

- **macOS `date -d` 不工作**: Use `gdate` from coreutils instead
  ```bash
  brew install coreutils
  gdate -d "2024-01-01"
  ```

### Library Quirks

- **PDF library 静默返回空数组**: Always check page type before processing
  ```python
  if page.type != 'text':
      continue
  ```

### Common Mistakes

- **忘记设置 timeout**: Default timeout is 30s, may not be enough for large files
  ```python
  fetch_data(timeout=300)  # 5 minutes
  ```
```

---

## 🚀 执行计划

### 第 1 周：核心 Skills 优化

| 日期 | 任务 | Skills |
|------|------|--------|
| Day 1 | 添加排除条款 | hermes-agent, stock-analysis-framework |
| Day 2 | 拆分超长文件 | stock-data-acquisition, research-paper-writing |
| Day 3 | 添加 Gotchas | github-repo-management, humanizer |
| Day 4 | 优化 description | grid-trading-monitor, turix-mac |
| Day 5 | 批量优化 | 20 个高频 Skills |

### 第 2-4 周：批量优化

| 周次 | 任务 | 数量 |
|------|------|------|
| 第 2 周 | 添加排除条款（批量） | 200 个 |
| 第 3 周 | 添加触发词（批量） | 200 个 |
| 第 4 周 | 添加 Gotchas | 50 个核心 Skills |

---

## 📊 质量检查

### 自动化检查脚本

```python
#!/usr/bin/env python3
"""Skills 质量检查器"""

def check_skill(skill_path):
    issues = []
    
    # 1. 检查 description 长度
    if len(description) < 50:
        issues.append("description 过短")
    
    # 2. 检查排除条款
    if "NOT use" not in content:
        issues.append("缺少排除条款")
    
    # 3. 检查 Known Gotchas
    if "Gotchas" not in content:
        issues.append("缺少 Known Gotchas")
    
    # 4. 检查行数
    if line_count > 500:
        issues.append(f"超过 500 行 ({line_count})")
    
    # 5. 检查触发词
    if not triggers and not keywords:
        issues.append("缺少触发词")
    
    return issues
```

### 质量报告

```bash
# 每周生成质量报告
python scripts/skill_quality_checker.py > reports/quality_$(date +%Y%m%d).md
```

---

## 📈 预期收益

### Token 节省

| 优化项 | 节省 Tokens | 说明 |
|--------|------------|------|
| 拆分超长 SKILL.md | **~500K** | 75个 × 平均节省 6.7K |
| 删除重复背景知识 | **~100K** | 假设 50% 有冗余 |
| 渐进式披露 | **~200K** | 只加载需要的文件 |
| **总计** | **~800K** | 相当于 10+ 次 API 调用 |

### 触发率提升

| 优化项 | 提升 | 说明 |
|--------|------|------|
| 添加触发词 | **+50%** | 从 8.6% → 60%+ |
| 添加排除条款 | **+20%** | 减少错误触发 |
| 优化 description | **+15%** | 更清晰的触发信号 |

### 可靠性提升

| 优化项 | 提升 | 说明 |
|--------|------|------|
| Known Gotchas | **+30%** | 减少边界情况失败 |
| 模板脚手架 | **+20%** | 输出格式一致性 |
| 执行清单 | **+25%** | 减少流程跳步 |

---

## 🎯 成功指标

### 定量指标

| 指标 | 当前 | 1周目标 | 1月目标 |
|------|------|---------|---------|
| 排除条款覆盖率 | 3.0% | 50% | 90% |
| Known Gotchas 覆盖率 | 0.6% | 20% | 50% |
| 触发词覆盖率 | 8.6% | 60% | 95% |
| 超长 SKILL.md 数量 | 75 | 60 | 20 |
| 平均 description 长度 | ? | >50字符 | >80字符 |

### 定性指标

- ✅ 新 Skill 作者有清晰的模板可参考
- ✅ 真实失败案例系统化归档到 Gotchas
- ✅ 用户触发 Skill 的成功率显著提升
- ✅ Token 消耗明显下降（RTK 统计）

---

## 📚 参考文档

- `docs/claude-skill-patterns-14.md` - 14 个编写模式
- `HERMES.md` - 项目配置
- `HOOK_CONFLICT_RESOLUTION.md` - Hook 冲突解决方案
- `CONFLICT_DETECTION_REPORT.md` - 冲突检测报告

---

**创建时间**: 2026-05-05
**负责人**: Hermes Agent
**状态**: 规划中
