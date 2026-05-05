# LLM Enhanced Abstraction Guide

**Version**: v1.5.0  
**Date**: 2026-05-03  
**Component**: `llm_enhanced_abstraction.py`

---

## 🎯 Overview

LLM-Enhanced Abstraction replaces simple rule-based strategy generation with intelligent, structured strategy synthesis using LLM APIs. This dramatically improves the quality and actionability of abstracted strategies from similar cases.

---

## 🏗️ Architecture

```
相似案例检测
    ↓
案例分析 (关键词提取, 相似度计算)
    ↓
策略生成
    ├─ 规则生成 (快速, <1ms, 简洁)
    └─ LLM 生成 (智能, 1-3s, 结构化)
        ├─ general 模板
        ├─ technical 模板
        └─ problem_solving 模板
    ↓
策略存储 (fact_store + 元数据)
```

---

## 📦 Core Components

### LLMEnhancedAbstraction Class

**Location**: `~/.hermes/scripts/llm_enhanced_abstraction.py`

**Key Methods**:

```python
# 分析案例
analyze_cases(case_ids: List[int]) -> Dict
# 返回: case_count, keywords, avg_similarity, contents

# 生成策略
generate_strategy(case_ids, template="general", use_llm=True) -> Dict
# 返回: strategy_content, strategy_source, keywords, avg_similarity

# 完整抽象流程
abstract_with_llm(case_ids, template="general", auto_save=True) -> Dict
# 返回: strategy_id, strategy_content, ...
```

---

## 🎨 Strategy Templates

### 1. General Template (200字)

**适用场景**: 通用场景，大多数案例抽象

**输出维度**:
1. **核心模式** - 共同特征识别
2. **关键原则** - 通用原则提炼
3. **适用场景** - 应用场景界定
4. **注意事项** - 执行注意点

**示例输出**:
```
1. **核心模式**：通过多轮迭代，持续优化语义匹配核心组件，并辅以性能保障机制。
2. **关键原则**：功能升级与鲁棒性增强并重；主动性能优化（如缓存预热）。
3. **适用场景**：智能路由系统、依赖复杂匹配与高可用的服务组件持续改进。
4. **注意事项**：变更需充分测试，避免影响现有功能。
```

---

### 2. Technical Template (300字)

**适用场景**: 技术问题、代码优化、架构设计

**输出维度**:
1. **技术模式** - 识别技术模式
2. **实现要点** - 关键实现步骤
3. **最佳实践** - 推荐做法
4. **避坑指南** - 需要避免的问题

**示例输出**:
```
**1. 技术模式**
- 模式一：技能导向的智能路由
- 模式二：存量技能的资源池化管理

**2. 实现要点**
- 构建技能标签体系，实现与路由规则的动态绑定
- 建立版本与生命周期管理

**3. 最佳实践**
- 优先使用语义匹配而非关键词匹配
- 实现自动回退机制

**4. 避坑指南**
- 避免硬编码路由规则
- 注意缓存失效策略
```

---

### 3. Problem Solving Template (250字)

**适用场景**: 故障排查、问题解决、性能调优

**输出维度**:
1. **问题特征** - 识别问题类型
2. **解决步骤** - 标准解决流程
3. **验证方法** - 如何验证解决效果
4. **预防措施** - 如何避免类似问题

---

## ⚙️ Configuration

### Provider Configuration

**Hermes config.yaml**:

```yaml
providers:
  modelscope:
    api_key: ms-b53c44e9-f313-4a3d-9547-2ce19c88729d
    base_url: https://api-inference.modelscope.cn/v1
    default_model: deepseek-ai/DeepSeek-V3.2
```

**支持的 Providers**:
- `modelscope` (推荐，稳定，DeepSeek V3.2)
- `edgefn` (GLM-5)
- `ark` (豆包系列模型)

---

## 🔧 Usage

### 命令行测试

```bash
# 测试 LLM 增强抽象
python3 ~/.hermes/scripts/llm_enhanced_abstraction.py

# 测试质量对比
python3 ~/.hermes/scripts/test_llm_abstraction.py
```

### API 调用

```python
from llm_enhanced_abstraction import LLMEnhancedAbstraction

# 初始化
llea = LLMEnhancedAbstraction(
    provider="modelscope",
    model="deepseek-ai/DeepSeek-V3.2"
)

# 分析案例
analysis = llea.analyze_cases([131, 132])
# 返回: case_count, keywords, avg_similarity

# 生成策略（规则）
result_rule = llea.generate_strategy([131, 132], use_llm=False)

# 生成策略（LLM）
result_llm = llea.generate_strategy(
    [131, 132], 
    template="technical", 
    use_llm=True
)

# 完整抽象流程
result = llea.abstract_with_llm([131, 132], auto_save=True)
# 返回: strategy_id, strategy_content, ...
```

---

## 📊 Quality Comparison

| 维度 | 规则生成 | LLM 生成 |
|------|----------|----------|
| **速度** | < 1ms | 1-3s |
| **长度** | < 100字 | 200-300字 |
| **结构** | 无 | 4维度结构化 |
| **适应性** | 通用 | 领域定制 |
| **可读性** | 一般 | 高 |
| **可操作性** | 低 | 高 |

---

## 🎯 When to Use Which

### 使用规则生成

- ✅ 快速原型阶段
- ✅ 低相似度案例 (< 70%)
- ✅ 简单场景
- ✅ API 配额受限
- ✅ 批量抽象（性能优先）

### 使用 LLM 生成

- ✅ 高质量策略库
- ✅ 高相似度案例 (>= 70%)
- ✅ 复杂技术场景
- ✅ 需要结构化输出
- ✅ 用户决策支持
- ✅ 知识文档生成

---

## 🔍 Performance Data

### 测试案例

**输入**: 案例 [131, 132] (相似度 69%)

**规则生成** (< 1ms):
```
基于 2 个相似案例的经验，涉及关键词: skill, router, smart。
建议在遇到类似场景时参考这些案例，注意分析具体上下文后再应用。
```

**LLM 生成** (1.2s):
```
**技术策略文档**

**1. 技术模式**
- 模式一：技能导向的智能路由。根据动态输入的"skill"类型，
  通过"smart router"智能分配任务或流量，需优化匹配算法。
- 模式二：存量技能的资源池化管理。将"skills"作为可复用资产
  纳入"stock"库存体系，支持长期规划（如至2026年）。

**2. 实现要点**
- 构建技能标签体系，实现与路由规则的动态绑定。
...
```

---

## 🚨 Common Issues

### 1. API 调用失败 (403)

**原因**: API Key 格式错误或未正确加载

**解决**:
```python
# 检查配置
llea = LLMEnhancedAbstraction(provider="modelscope")
print(llea.api_config)

# 确认 api_key 不包含 "..." 占位符
```

### 2. 自动回退到规则生成

**原因**: API 超时、网络错误、配额耗尽

**解决**: 检查 `result["strategy_source"]`，值为 "llm" 表示成功，"rule" 表示回退

### 3. JSON 序列化错误

**原因**: numpy float32 未转换

**解决**: 代码已处理 `float(similarity)` 转换

---

## 🔗 Integration Points

### 与 Active Abstraction 集成

```python
from active_abstraction import ActiveAbstractionEngine
from llm_enhanced_abstraction import LLMEnhancedAbstraction

aae = ActiveAbstractionEngine()
llea = LLMEnhancedAbstraction()

# 扫描抽象机会
suggestions = aae.scan_all_cases(threshold=0.7)

# 使用 LLM 生成策略
for sug in suggestions:
    result = llea.abstract_with_llm(
        sug["case_ids"],
        template="technical",
        auto_save=True
    )
```

### 与 Memory Evolution Hook 集成

在 `memory_evolution_hook.py` 中可集成 LLM 抽象：

```python
# 检测到抽象机会时
if opportunities:
    from llm_enhanced_abstraction import LLMEnhancedAbstraction
    llea = LLMEnhancedAbstraction()
    
    for opp in opportunities:
        result = llea.abstract_with_llm(
            opp["case_ids"],
            auto_save=True
        )
```

---

## 📚 Related Files

| 文件 | 用途 | 大小 |
|------|------|------|
| `llm_enhanced_abstraction.py` | 核心实现 | 13KB |
| `test_llm_abstraction.py` | 测试脚本 | 3.5KB |
| `active_abstraction.py` | 基础抽象引擎 | 8KB |
| `embedding_similarity.py` | 相似度检测 | 13KB |

---

## 🎓 Best Practices

1. **优先使用高相似度案例** - 相似度 >= 70% 时 LLM 生成效果最佳
2. **选择合适模板** - 技术问题用 technical，故障排查用 problem_solving
3. **检查 strategy_source** - 确认是否 LLM 成功生成
4. **保留规则生成作为备选** - API 失败时自动回退
5. **批量抽象时控制频率** - 避免 API 限流

---

## 🔮 Future Enhancements

**Phase 4 后续方向**:
- 跨模态案例（图像/代码作为案例）
- 自适应阈值（根据领域动态调整）
- LLM 生成的策略质量评分
- 多轮对话式策略优化

---

## 📖 References

- [Experiential Memory Phase 3](experiential-memory-phase3-2026-05-03.md)
- [Embedding Similarity Technical Details](embedding-similarity-technical-details.md)
- [Active Abstraction Engine Guide](active-abstraction-guide.md)
