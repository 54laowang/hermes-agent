# Done When 实施记录 - 2026-05-03

## 实施背景

用户发现 Skills 虽然有检查点，但缺少明确的"完成判据"，导致 Agent 无法判断任务是否真正完成。

**问题**：Agent 从"我猜我做完了"到"我需要确认我做完了"，但缺少确认标准。

**解决方案**：引入 Done When 完成判据机制，受 OpenAI Codex 官方文档启发。

---

## 实施内容

### 一、Skills 更新

#### 1. stock-data-acquisition

**文件位置**：`~/.hermes/skills/stock-data-acquisition/SKILL.md`

**新增内容**：
- Done When 章节（位于"注意事项"后）
- 四大支柱表格（Goal/Context/Constraints/Done When）
- 必检项：
  - 单只股票数据获取（4 项）
  - 自选股管理（3 项）
- 可选项：
  - 多源交叉验证
  - 缓存命中率统计
- 失败处理：4 种场景
- 自检代码示例

**关键改进**：
- 时间锚定验证：从"检查点"升级为"必检项"
- 数据溯源标注：明确要求标注来源 + 时间戳
- 缓存更新验证：检查文件写入 + 内容完整性

---

#### 2. stock-analysis-framework

**文件位置**：`~/.hermes/skills/stock-analysis-framework/SKILL.md`

**新增内容**：
- Done When 章节
- 必检项：
  - A股个股分析（5 项）：时间锚定、数据来源、技术分析、风险控制、研判结论
  - ST公司借壳研判（4 项）：ST类型、亏损拆解、借壳概率、风险提示
  - 量化回测（4 项）：回测引擎、因子有效性、统计显著性、过拟合检查
- 可选项：
  - 多市场交叉验证
  - 反事实分析
  - 行为偏差诊断
- 失败处理：4 种场景

**关键改进**：
- 技术分析要求三视角（艾尔德 + 爱在冰川 + 淘股吧）
- ST 研判要求量化概率（借壳概率 XX%）
- 回测要求统计显著性（p值 < 0.05）

---

#### 3. hierarchical-memory-system

**文件位置**：`~/.hermes/skills/core/hierarchical-memory-system/SKILL.md`

**新增内容**：
- Done When 章节
- 必检项：
  - 事实提取到 fact_store（3 项）
  - L2 短期记忆摘要（4 项）
  - L3 长期记忆归档（4 项）
  - L4 Skill 提取（3 项）
- 可选项：
  - MemPalace Tunnel 创建
  - Embedding 相似度检测
- 失败处理：4 种场景

**关键改进**：
- 事实提取要求去重验证（SQL 检查）
- L2 摘要要求字数限制（≤500 字）
- L3 归档要求双写（fact_store + MemPalace）

---

### 二、配置文件创建

#### context_triggers.yaml

**文件位置**：`~/.hermes/context_triggers.yaml`
**文件大小**：4,704 字节

**触发词分类**：

| 类别 | 示例 | 优先级 |
|------|------|--------|
| 股票类 | `\d{6}\.(SH\|SZ)`、股价、行情 | high |
| 技术分析类 | EMA、MACD、艾尔德、爱在冰川 | high |
| 项目类 | hermes、darwin、网格交易 | high |
| 记忆架构类 | memory、fact_store、mempalace | high |
| 工作时间类 | 夜班、下班、上班 | low |

**性能配置**：
- max_latency_ms: 500
- token_saving_target: 30%
- accuracy_target: 95%
- error_rate_target: 5%

---

#### context_discovery.py

**文件位置**：`~/.hermes/hooks/context_discovery.py`
**文件大小**：9,522 字节

**核心函数**：

```python
def scan_triggers(user_message, config) -> List[Dict]:
    """第一层：触发词扫描（<10ms）"""
    # 正则匹配 + 关键词匹配
    
def semantic_search(user_message, actions, config) -> List[Dict]:
    """第二层：语义检索（100-300ms）"""
    # 返回工具调用建议（不直接调用）
    
def discover_associations(user_message, triggers, config) -> List[Dict]:
    """第三层：关联发现（<500ms）"""
    # Tunnel 追踪 + 跨会话模式
```

**输出格式**：

```json
{
  "matched_triggers": [...],
  "tools_to_call": [
    {
      "tool": "skill_view",
      "args": {"name": "stock-data-acquisition"},
      "reason": "触发词匹配，加载 Skill"
    }
  ],
  "associations": [...],
  "stats": {
    "trigger_count": 1,
    "tool_count": 3,
    "latency_ms": 125.3
  }
}
```

---

#### config.yaml 更新

**文件位置**：`~/.hermes/config.yaml`

**更新内容**：

```yaml
hooks:
  pre_llm_call:
    # ... 其他 hooks ...
    - command: /Users/me/.hermes/hooks/context_discovery.py
      timeout: 10
```

**说明**：
- 添加到 `pre_llm_call` 阶段（在用户消息发送给 LLM 前执行）
- timeout: 10 秒（上下文发现三层架构总耗时 <500ms）

---

## 设计决策

### 为什么选择 Shell Hook 方案？

**备选方案对比**：

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **Shell Hook 预处理** | 响应快、无侵入、易调试 | 需要配置文件 | ✅ 采用 |
| **Skill 内置发现** | 无需配置 | 每个 Skill 都要实现 | ❌ 不采用 |
| **LLM 后处理** | 智能 | 延迟高、Token 消耗 | ❌ 不采用 |

**关键理由**：
1. Shell Hook 在 `pre_llm_call` 阶段执行，不占用 LLM Token
2. 三层架构分层降级，超时 500ms 直接跳过
3. 配置文件可动态更新，无需修改代码

---

### 为什么 Done When 要有四大支柱？

**来源**：OpenAI Codex 官方文档

**核心思想**：
- **Goal**：明确目标，避免偏题
- **Context**：明确数据来源，避免盲猜
- **Constraints**：明确约束，避免违规
- **Done When**：明确完成标准，避免"我以为我做完了"

**应用**：
- stock-data-acquisition：Goal=获取数据、Context=数据源、Constraints=时间锚定
- stock-analysis-framework：Goal=分析研判、Context=市场数据、Constraints=风险控制

---

## 预期效果

### Done When 标准化

| 指标 | 目标 | 测量方法 |
|------|------|---------|
| 错误率降低 | 50% | 对比实施前后错误报告 |
| 自检覆盖率 | 80% | 必检项数 / 总检查点数 |
| Agent 能力提升 | 从"我猜"→"我确认" | 用户反馈 |

### 上下文发现

| 指标 | 目标 | 测量方法 |
|------|------|---------|
| Token 节省 | 30% | 统计对比 |
| 准确率提升 | +20%（达 95%） | 上下文相关性评分 |
| 错误率降低 | -50%（降至 5%） | 错误触发统计 |
| 响应延迟 | <500ms | 平均延迟监控 |

---

## 后续优化方向

### 短期（1 周内）

1. **测试验证**
   - 测试 Hook：`echo "测试" | python3 ~/.hermes/hooks/context_discovery.py`
   - 查看日志：`cat ~/.hermes/logs/context_discovery.log`
   - 监控性能：`cat ~/.hermes/logs/context_discovery_stats.json`

2. **触发词扩展**
   - 根据实际使用补充触发词
   - 调整优先级
   - 优化正则表达式

### 中期（1 个月内）

3. **Done When 扩展**
   - 为高频 Skills 添加 Done When（如 vibe-trading-integration）
   - 优化必检项设计（根据用户反馈）
   - 编写测试用例

4. **上下文发现优化**
   - 优化语义检索阈值
   - 扩展关联发现规则
   - 添加更多 Tunnel

### 长期（3 个月内）

5. **自动化验证**
   - 自动化 Done When 验证脚本
   - CI/CD 集成
   - 性能监控告警

---

## 归档信息

- **创建时间**：2026-05-03 10:40:09
- **实施人员**：Hermes Agent
- **状态**：✅ 已完成
- **fact_store 记录**：fact_id=142

---

## 参考资料

- OpenAI Codex 上下文工程文档
- Claude Code 对照实战经验
- Hermes Agent 记忆架构 v1.5.0
