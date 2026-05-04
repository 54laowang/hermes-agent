# Hermes Hook 优先级与冲突解决

## 当前 Hook 注册情况

```yaml
# ~/.hermes/hooks/hooks.yaml
hooks:
  pre_llm_call:
    - cache_aware_hook.main        # 优先级1：缓存优化
    - supervisor-precheck.main     # 优先级2：监察者预检（条件触发）
  
  post_llm_call:
    - task_context_detector.main   # 任务上下文检测
```

## 已识别的冲突

### ⚠️ 冲突1：时间感知重复注入

**涉及系统**：
- 监察者模式（supervisor-mode-auto-trigger）
- Context Soul Injector（time-sense-injector.py）

**冲突原因**：
两者都注入时间感知内容，可能导致：
1. Token 浪费（重复信息）
2. 信息矛盾（不同时区计算逻辑）
3. 缓存失效（每次注入内容不同）

### ⚠️ 冲突2：Hook 执行顺序

**当前 pre_llm_call Hook 顺序**：
```
1. cache_aware_hook.main
2. supervisor-precheck.main
```

**未注册但可能添加的**：
- `smart-skill-loader.py`（Smart Skill Router）
- `time-sense-injector.py`（Context Soul Injector）

**问题**：
- 执行顺序未明确
- 后执行的 Hook 可能覆盖前面的注入

## 解决方案

### ✅ 方案A：合并时间感知层（推荐）

**实施步骤**：

1. **创建统一时间感知模块**
```bash
~/.hermes/hooks/unified_time_awareness.py
```

**内容**：
```python
#!/usr/bin/env python3
"""
统一时间感知模块 - 合并监察者模式和 Context Soul Injector 的时间逻辑
"""
import sys
from datetime import datetime, timedelta

def get_time_context(user_message: str) -> dict:
    """
    统一时间上下文获取
    
    返回：
    - beijing_time: 北京时间
    - us_eastern_time: 美东时间
    - market_status: 市场状态（仅财经关键词时）
    - is_finance_task: 是否财经任务
    """
    beijing_time = datetime.utcnow() + timedelta(hours=8)
    
    # 检测财经关键词
    finance_keywords = ["美股", "A股", "道琼斯", "纳斯达克", "上证", "财联社"]
    is_finance = any(kw in user_message for kw in finance_keywords)
    
    context = {
        "beijing_time": beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
        "is_finance_task": is_finance
    }
    
    if is_finance:
        # 财经任务：注入完整时间锚定
        us_eastern_time = beijing_time - timedelta(hours=12)
        hour = us_eastern_time.hour
        
        if hour < 9.5:
            market_status = "盘前"
        elif 9.5 <= hour < 16:
            market_status = "盘中"
        else:
            market_status = "收盘/盘后"
        
        context.update({
            "us_eastern_time": us_eastern_time.strftime('%Y-%m-%d %H:%M:%S'),
            "market_status": market_status
        })
    
    return context

def main(user_message: str):
    """Hook 入口"""
    context = get_time_context(user_message)
    
    # 输出给 Hermes
    print(f"[时间感知] 北京时间: {context['beijing_time']}")
    
    if context['is_finance_task']:
        print(f"[时间感知] 美东时间: {context['us_eastern_time']}")
        print(f"[时间感知] 市场状态: {context['market_status']}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
```

2. **更新 hooks.yaml**
```yaml
hooks:
  pre_llm_call:
    # 优先级1：缓存优化
    - cache_aware_hook.main
    
    # 优先级2：统一时间感知（替代 time-sense-injector 和 supervisor-precheck）
    - unified_time_awareness.main
    
    # 优先级3：Skill 路由
    - smart-skill-loader.main
  
  post_llm_call:
    # 任务上下文检测
    - task_context_detector.main
```

### ✅ 方案B：条件触发机制

**实施方式**：

在 `hooks.yaml` 中添加条件判断：

```yaml
hooks:
  pre_llm_call:
    - cache_aware_hook.main
    
    # 条件触发：仅财经关键词时激活
    - name: supervisor-precheck.main
      condition:
        keywords: ["美股", "A股", "道琼斯", "纳斯达克", "上证", "财联社", "Fed"]
    
    # 默认触发：所有会话
    - name: time-sense-injector.main
      condition:
        default: true
        exclude_keywords: ["美股", "A股"]  # 财经任务时跳过（由 supervisor 处理）
```

### ✅ 方案C：互斥标记

**在 Skill 的 SKILL.md 中添加**：

```yaml
---
name: supervisor-mode-auto-trigger
conflicts_with:
  - context-soul-injector  # 互斥：财经任务时优先使用监察者模式
priority: 10  # 优先级：数字越大越优先
---
```

## Token 消耗对比

| 方案 | 非财经任务 | 财经任务 | 节省 |
|------|-----------|----------|------|
| **当前（重复注入）** | ~500 tokens | ~1300 tokens | - |
| **方案A（合并）** | ~200 tokens | ~800 tokens | 60%+ |
| **方案B（条件触发）** | ~200 tokens | ~800 tokens | 60%+ |

## 推荐方案

**推荐方案A（合并时间感知层）**：

理由：
1. ✅ 彻底解决功能重叠
2. ✅ 代码更易维护
3. ✅ Token 节省 60%+
4. ✅ 缓存命中率提升

## 实施检查清单

- [ ] 创建 `unified_time_awareness.py`
- [ ] 更新 `hooks.yaml` 注册
- [ ] 移除 `supervisor-precheck.main` 和 `time-sense-injector.main`
- [ ] 测试非财经任务时间注入
- [ ] 测试财经任务完整时间锚定
- [ ] 验证 Token 消耗下降
- [ ] 更新相关 Skill 文档

## 相关文件

- `~/.hermes/hooks/hooks.yaml` - Hook 注册配置
- `~/.hermes/hooks/unified_time_awareness.py` - 统一时间感知模块（待创建）
- `skills/supervisor-mode-auto-trigger/SKILL.md` - 监察者模式文档
- `skills/context-soul-injector/SKILL.md` - 灵魂注入器文档
