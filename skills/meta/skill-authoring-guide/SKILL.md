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

