# 14 个 Claude Skill 编写模式 - 实践要点

**来源**: 丁光华《什点悟智》（Bilgin Ibryam 系列第三篇）
**应用**: Hermes Skills 编写与优化

---

## 快速检查清单

### ✅ Skill 触发检查（必做）

```markdown
- [ ] description 包含"做什么"
- [ ] description 包含"什么时候触发"（触发词）
- [ ] description 包含排除条款（Do NOT use for...）
- [ ] description 字符数 < 1024（开放 spec）/< 1536（Claude Code）
```

### ✅ Token 经济检查（必做）

```markdown
- [ ] SKILL.md < 500 行
- [ ] 删除 Claude 已知的背景知识
- [ ] 术语一致
- [ ] 无时间敏感措辞
- [ ] 详细内容拆到独立文件
- [ ] 长文件顶部有目录
```

### ✅ 指令校准检查（推荐）

```markdown
- [ ] 自由度匹配任务脆弱度
- [ ] 无 MUST/ALWAYS/NEVER（除非必要）
- [ ] 关键规则解释 why
- [ ] 有模板（如输出结构重要）
- [ ] 有示例（如调性重要）
- [ ] 有 Known Gotchas 节
```

---

## 核心洞见（记忆要点）

### 1. 触发是生死关口

> **会话开始时，Claude 只看到所有 skill 的 name + description**
> 
> 如果在 metadata-only 环节被刷掉，后面写得再漂亮也没用

**Action**: 
- description 必须包含：做什么 + 什么时候触发 + 什么时候别触发
- 写得稍微"推销"一点（模型有保守倾向）

### 2. 约束太死是普遍错误

> **作者们会无意识地往"约束太死"那边走**
> 
> 严格的指令感觉更安全，但它不安全——**它只是换了一种失败方式**

**Action**: 用 Explain-the-Why 替代 MUST/NEVER

### 3. Gotchas 价值最高

> **成熟 skill 里 gotchas 这一节的价值最高**
> 
> 只能从"真实跑出来的失败案例"里捞——brainstorm 写不出来

**Action**: 每次失败后，立即补充到 Known Gotchas

### 4. 渐进式披露省 Token

> **SKILL.md 是目录，不是百科全书**
> 
> 800 行全塞进去 → 每次会话不管用不用都得加载

**Action**: 
- SKILL.md < 500 行
- 详细内容拆到 references/、templates/、scripts/

### 5. 模板 + 示例 = 骨架 + 肉

> **模板给的是骨架，例子给的是肉**
> 
> 模板定形，例子定味

**Action**: 
- Strict 模板：机器解析场景
- Flexible 模板 + Few-shot 示例：人读场景

---

## 实用模板

### Description 模板

```yaml
description: |
  [做什么] 简洁描述功能。
  
  [什么时候触发] Use when: keyword1, keyword2, "user says X".
  
  [什么时候别触发] Do NOT use for: related-but-different tasks.
```

### Known Gotchas 模板

```markdown
## Known Gotchas

### Platform Issues
- **macOS `date -d` 不工作**: Use `gdate` from coreutils

### Library Quirks
- **PDF library 静默返回空数组**: Always check page type first

### Common Mistakes
- **忘记设置 timeout**: Default 30s may not be enough for large files
```

---

## 自由度对照表

| 自由度 | 用什么形式 | 什么任务 |
|--------|-----------|----------|
| **高自由** | 文字指令、"用你的判断" | 代码 review（多种合理做法） |
| **中自由** | 伪代码、可参数化的脚本 | 部署 runbook（有偏好但灵活） |
| **低自由** | 精确脚本、不允许任何 flag、"do not modify" | 数据库迁移（错一步全完） |

---

## Hermes 当前状态（2026-05-05）

| 指标 | 数值 | 状态 |
|------|------|------|
| 总 Skills 数 | 503 | ✅ |
| 缺少排除条款 | 485 (97.0%) | ❌ 需优化 |
| 缺少 Known Gotchas | 497 (99.4%) | ❌ 需优化 |
| 超过 500 行 | 75 (15.0%) | ⚠️ 需拆分 |
| 缺少触发词 | 457 (91.4%) | ❌ 需优化 |

---

## 优化策略

### 渐进式优化（推荐）

1. **立即行动**：手动优化 5-10 个核心 Skills
2. **建立机制**：每次失败后补充 Gotchas
3. **定期审计**：每月运行质量检查脚本

### 批量优化（谨慎）

使用 `~/.hermes/scripts/skill_optimizer.py`，但需：
- 先备份整个仓库
- 在测试分支执行
- 逐个检查结果

---

## 相关文档

- `docs/claude-skill-patterns-14.md` - 完整学习笔记
- `SKILLS_OPTIMIZATION_PLAN.md` - 系统优化计划
- `scripts/skill_optimizer.py` - 批量优化脚本

---

**学习时间**: 2026-05-05
**应用范围**: 所有 Hermes Skills 编写
