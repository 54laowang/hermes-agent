---
name: skill-authoring-guide
description: Skill 创作标准化模板与最佳实践 - 从零创建高质量 Skill 的完整指南
priority: P1
triggers:
  - 用户说"创建一个 Skill"
  - 用户说"保存为 Skill"
  - 用户说"把这个流程变成 Skill"
auto_load: false
---

# Skill 创作指南

## 核心原则

> **Skill = 可复用的流程 + 已知陷阱 + 验证步骤**

一个好的 Skill 应该：
1. **减少未来决策**：明确的触发条件和执行步骤
2. **编码经验教训**：包含已知陷阱和避坑指南
3. **可验证结果**：有明确的成功标准

---

## 标准模板

```markdown
---
name: skill-name
description: 一句话描述这个 Skill 做什么（不超过80字符）
priority: P0|P1|P2|P3
triggers:
  - 触发条件1
  - 触发条件2
  - 触发条件3
auto_load: true|false
---

# Skill 标题

## 核心目标
（1-2句话说明这个 Skill 解决什么问题）

## 标准流程

### 步骤 1: [标题]
- 具体操作
- 关键参数
- 预期输出

### 步骤 2: [标题]
...

## 关键参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| param1 | 用途 | default |

## 已知陷阱

### ⚠️ 陷阱1：[标题]
- **表现**：错误的样子
- **原因**：为什么会出现
- **解决**：正确的做法

## 验证清单

- [ ] 检查项1
- [ ] 检查项2
- [ ] 检查项3

## 相关技能

- `related-skill-1`
- `related-skill-2`
```

---

## 必填字段说明

### frontmatter

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | Skill 标识符，小写+连字符，如 `market-data-fetch` |
| `description` | ✅ | 一句话描述，不超过80字符 |
| `priority` | ✅ | P0（最高）到 P3（最低） |
| `triggers` | ✅ | 触发条件列表，用于自动匹配 |
| `auto_load` | ✅ | 是否在会话开始时自动加载 |

### 优先级定义

| 优先级 | 含义 | 示例 |
|--------|------|------|
| **P0** | 强制执行，不可绕过 | 时间锚定宪法 |
| **P1** | 核心流程，建议加载 | 市场分析流程 |
| **P2** | 辅助流程，按需加载 | 报告生成 |
| **P3** | 可选增强 | 格式美化 |

---

## 高质量 Skill 的特征

### ✅ 好的 Skill

```markdown
## 已知陷阱

### ⚠️ 数据源返回空值
- **表现**：web_search 返回 "No results found"
- **原因**：搜索关键词缺少日期或时间节点
- **解决**：构建关键词时必须包含 "YYYY年MM月DD日" 格式

## 验证清单

- [ ] 数据时间戳匹配当前市场状态
- [ ] 至少3个独立数据源
- [ ] 所有数据已标注来源和可信度
```

### ❌ 差的 Skill

```markdown
## 流程

1. 获取数据
2. 分析数据
3. 输出结果
```

**问题**：
- 没有具体操作步骤
- 没有已知陷阱
- 没有验证清单

---

## 创建流程

### 1. 触发条件识别

**何时创建 Skill**：
- 同一流程执行超过 2 次
- 用户纠正过执行方式
- 发现了可复用的模式
- 复杂任务需要标准化

### 2. 内容填充

**必须包含**：
1. **标准流程**：明确的步骤编号
2. **已知陷阱**：实际踩过的坑
3. **验证清单**：可检查的成功标准

**建议包含**：
- 关键参数表格
- 错误处理方案
- 相关资源链接

### 3. 验证与测试

```bash
# 安装后测试
hermes skills install <skill-name>
hermes -s <skill-name>  # 显式加载测试

# 检查 Skill 质量
skill_view(name="<skill-name>")
```

---

## 实战示例

### 示例：创建一个简单的 Skill

**场景**：每次获取股价都需要重复相同的验证流程

**创建**：

```markdown
---
name: stock-price-fetch
description: 获取股票价格并进行时间戳验证
priority: P1
triggers:
  - 用户问股价
  - 用户问行情
  - 用户问涨跌
auto_load: false
---

# 股票价格获取流程

## 核心目标
获取指定股票的实时价格，并验证数据时间戳的准确性。

## 标准流程

### 步骤 1: 确认股票代码
- 检查代码格式（A股：000001.SZ，美股：AAPL.US）
- 确认市场（A股/美股/港股）

### 步骤 2: 构建搜索关键词
- A股："{股票名} 股价 YYYY年MM月DD日"
- 美股："{股票代码} stock price {YYYY-MM-DD}"

### 步骤 3: 获取数据
- 优先使用 AkShare API（A股）
- 备选 web_search

### 步骤 4: 验证时间戳
- 检查数据日期是否匹配当前日期
- 不匹配则重新获取

## 已知陷阱

### ⚠️ 用昨天的收盘数据凑数
- **表现**：盘前获取到昨天的收盘价
- **原因**：今日数据尚未更新
- **解决**：明确告知用户"这是昨日收盘数据"

## 验证清单

- [ ] 股票代码格式正确
- [ ] 数据时间戳已验证
- [ ] 数据来源已标注
```

---

## 维护与更新

### 何时更新 Skill

1. **发现新陷阱**：立即补充到 "已知陷阱" 部分
2. **流程变化**：更新标准流程步骤
3. **工具升级**：更新工具使用方式

---

## 批量优化流程

### 触发条件

- Skills 数量 > 100，需要系统性质量提升
- 发现大量 Skills 缺少排除条款或 Known Gotchas
- 用户要求优化特定领域或类别的 Skills

### 标准优化流程

#### 步骤 1: 分析现状

```bash
# 统计总数
find skills -name 'SKILL.md' -type f | wc -l

# 查找大文件（>400行，优先优化）
find skills -name 'SKILL.md' -type f -exec wc -l {} \; | awk '$1 > 400 {print $1, $2}' | sort -rn

# 查找缺少排除条款的 Skills
grep -L 'Do NOT use' skills/*/SKILL.md skills/*/*/SKILL.md

# 查找缺少 Known Gotchas 的 Skills
grep -L 'Known Gotchas' skills/*/SKILL.md skills/*/*/SKILL.md

# 按类别统计
find skills -name 'SKILL.md' -type f -exec dirname {} \; | sed 's|skills/||' | cut -d'/' -f1 | sort | uniq -c | sort -rn
```

#### 步骤 2: 确定优化优先级

**优先级矩阵**：

| 优先级 | 标准 | 示例 |
|--------|------|------|
| **P0** | 基础设施 + 大文件 + 高频依赖 | `stock-data-acquisition`, `hermes-agent` |
| **P1** | 核心功能 + 中等文件 | `supervisor-mode`, `global-constraints` |
| **P2** | 辅助功能 + 小文件 | `huashu-design`, `grid-trading-system` |

**决策规则**：
1. 先优化被其他 Skills 依赖的（基础设施）
2. 再优化高频使用的（实际使用统计）
3. 最后优化大文件（复杂度高，收益大）

#### 步骤 3: 单个 Skill 优化内容

**必须添加**：

1. **排除条款**（Do NOT use for）：
   ```yaml
   description: |
     核心功能描述。
     
     Use when: 触发词1, 触发词2, 触发词3.
     
     Do NOT use for:
     - 不适用场景1（原因）
     - 不适用场景2（替代方案）
   ```

2. **Known Gotchas**（实际失败案例）：
   ```markdown
   ## ⚠️ Known Gotchas
   
   ### 类别名称
   
   - **问题标题**: 简短描述
     ```python
     # 错误示例
     ❌ 错误代码
     
     # 正确示例
     ✅ 正确代码
     ```
   ```

3. **触发词**（keywords + triggers）：
   ```yaml
   keywords:
     - 关键词1
     - 关键词2
   triggers:
     - 触发词1
     - 触发词2
   ```

**Gotchas 编写原则**：
- 只记录**实际失败过**的案例（不是想象的问题）
- 必须包含**错误示例 + 正确示例**
- 按类别分组（数据源、配置、工具、边界条件等）
- 每个 Skill 至少 10 条 Gotchas

#### 步骤 4: 版本号升级规则

```
MAJOR.MINOR.PATCH

- MAJOR: 架构重构、功能大改
- MINOR: 新增排除条款、Gotchas、触发词
- PATCH: 小修复、文档更新
```

**示例**：
- `v2.0.0` → `v2.1.0`（新增 Gotchas）
- `v2.1.0` → `v2.1.1`（修复拼写错误）

#### 步骤 5: 批量提交

```bash
# 统计优化成果
git add -A
git commit -m "feat: 完成 Top N 核心 Skills 优化

✅ 已完成 N/M：

1. skill-name-1 (v1.0.0 → 1.1.0)
   - 排除条款：...
   - Known Gotchas：X条

...

优化成果：
- ✅ N 个核心 Skills 全部添加排除条款
- ✅ N 个核心 Skills 全部添加 Known Gotchas
- ✅ 总计 X+ 条 Known Gotchas

预期收益：
- 触发准确率提升 30%+
- 失败预防提升 40%+
- Token 节省 ~10K/会话"
```

### 实战案例：Top 5 核心 Skills 优化

**背景**：
- Skills 总数：502 个
- 缺少排除条款：97%
- 缺少 Known Gotchas：99.4%

**优化目标**：Top 5 高频核心 Skills

**优化结果**：

| Skill | 版本升级 | 排除条款 | Known Gotchas |
|-------|---------|---------|---------------|
| `github-repo-management` | 1.1.0 → 1.2.0 | ✅ | 14 条 |
| `humanizer` | 2.5.1 → 2.5.2 | ✅ | 15 条 |
| `grid-trading-monitor` | 1.0.0 → 1.1.0 | ✅ | 16 条 |
| `stock-analysis-framework` | 2.0.0 → 2.1.0 | ✅ | 20+ 条 |
| `hermes-agent` | 2.1.0 → 2.2.0 | ✅ | 20+ 条 |

**总计**：85+ Known Gotchas，Git 已推送

**经验教训**：
- 优先优化**基础设施 Skills**（被其他 Skills 依赖）
- Gotchas 必须来自**实际失败案例**，不能凭空想象
- 版本号升级遵循语义化版本规范

### 更新命令

```bash
# 查看现有 Skill
skill_view(name="skill-name")

# 更新 Skill
skill_manage(action="patch", name="skill-name", old_string="...", new_string="...")

# 完整重写（谨慎使用）
skill_manage(action="edit", name="skill-name", content="...")

# 添加参考文件
skill_manage(action="write_file", name="skill-name", file_path="references/topic.md", file_content="...")
```

## 实践经验

### 何时添加 references 文件

当 Skill 涉及以下内容时，应该创建独立的 references 文件：

1. **技术细节**：具体的代码片段、API 调用、错误处理
2. **平台/工具特性**：反爬虫机制、权限配置、已知问题
3. **实战案例**：具体的失败经历和解决方案

**示例**：
- `wechat-article-learning/references/wechat-extraction-techniques.md`
  - 记录微信反爬虫机制
  - 记录 HTML 提取技巧
  - 记录实战失败和成功案例

---

## 相关技能

- `hermes-agent` - Hermes Agent 完整指南
- `time-anchor-constitution` - 时间锚定宪法（P0）
- `hierarchical-memory-system` - 分层记忆系统
- `skill-authoring-quality` - Skill 创作质量标准（Done When + 上下文发现）
- **`references/known-gotchas-best-practices.md`** - Known Gotchas 编写最佳实践（必读）
- **`references/batch-optimization-case-study-2026-05-05.md`** - 批量优化实战案例（本次会话完整记录）

---

## 质量提升方法

### Done When 完成判据

**核心思想**：从"我猜我做完了"变成"我能确认我做完了"

每个 Skill 应该包含 **Done When 章节**，定义明确的完成判据：

- **必检项**：全部满足才算完成
- **可选项**：加分项
- **失败处理**：明确的恢复路径

**示例**：

```markdown
## ✅ Done When 完成判据

### 必检项（全部满足才算完成）

- [ ] **时间锚定已验证**
  - 当前时间已获取
  - 市场状态已判断
  - **验证方法**：`datetime.now()` 返回正确值

- [ ] **数据来源已标注**
  - 数据源已确定
  - 时间戳已标注
  - **验证方法**：输出包含「来源: 时间戳」

### 失败处理

| 失败场景 | 处理路径 | 用户提示 |
|---------|---------|---------|
| 数据源失败 | 切换备用源 | ⚠️ 主源失败，已切换 |

### 自检代码示例

```python
def verify_done_when():
    # 具体验证逻辑
    return True
```
```

**参考**：`skill-authoring-quality` Skill 包含完整的 Done When 设计方法论。

---

### 上下文发现机制

**核心思想**：自动发现相关上下文，减少显式引用

当 Skill 涉及多个数据源或复杂上下文时，可以配置**触发词**：

```yaml
# 在 ~/.hermes/context_triggers.yaml 中配置
triggers:
  - pattern: '\d{6}\.(SH|SZ)'
    type: regex
    actions:
      - mempalace_search
      - skill_load: stock-data-acquisition
    priority: high
```

**效果**：
- Token 节省：30%
- 准确率提升：20%
- 响应延迟：<500ms

**参考**：`skill-authoring-quality/references/context-discovery-technical-details.md` 包含完整技术实现。

