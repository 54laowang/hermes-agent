# L2 自动摘要机制修复实战 - 2026-05-03

## 问题诊断

### 1. Cron Job 未注册

**现象**：
- L2 短期记忆目录 `~/.hermes/memory/short-term/` 为空
- `crontab -l` 无相关条目

**根因**：
- `install.py` 只创建了 `cron.yaml` 配置文件
- 没有实际注册到 Hermes cronjob 系统

**解决**：
```python
# ❌ 错误方式：只创建文件
cron_file = SKILL_DIR / "cron.yaml"
cron_file.write_text(cron_config)

# ✅ 正确方式：使用 Hermes cronjob 工具
cronjob(action="create", 
        name="每日记忆摘要 L1-L2",
        prompt="运行分层记忆系统的每日摘要生成器。执行命令：python3 ~/.hermes/skills/core/hierarchical-memory-system/scripts/daily-summarizer.py。输出摘要内容。",
        schedule="55 23 * * *")
```

**结果**：
- Job ID: `e391e39f07b3`
- 下次运行: 2026-05-03 23:55

---

### 2. auto-fact-extract.py 只记录日志

**现象**：
- `~/.hermes/logs/auto-facts.log` 有记录
- `fact_store` 中无新增事实

**根因**：
```python
# 旧代码只做了日志记录
def main():
    # ... 
    with open(log_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("{}")  # 返回空 JSON，不做任何操作
```

**解决**：
升级为完整的事实提取器：

```python
#!/usr/bin/env python3
"""
Post-LLM call hook: 自动从对话中提取事实到 fact_store。
实时提取 + 批量分析双重保障。
"""

# 触发关键词（扩展版）
TRIGGER_KEYWORDS = [
    "记住", "记得", "别忘了", "下次", "以后",
    "偏好", "喜欢", "不喜欢", "不要",
    "我习惯", "我一般", "我总是",
    "设置为", "默认为",
    "路径是", "地址是", "在哪个目录", "位置是",
    "核心是", "本质是", "关键是",
    "这个项目", "这个仓库", "这个系统",
    "工作时间", "夜班", "早班",  # 新增
]

def add_fact_to_store(content: str, category: str, tags: str = "") -> bool:
    """添加事实到 fact_store"""
    conn = sqlite3.connect(str(FACT_STORE_DB))
    cursor = conn.cursor()
    
    # 去重检查
    cursor.execute(
        "SELECT id FROM facts WHERE content = ? AND category = ?",
        (content, category)
    )
    if cursor.fetchone():
        conn.close()
        return False
    
    # 插入新事实
    cursor.execute("""
        INSERT INTO facts (content, category, tags, trust_score, created_at, updated_at)
        VALUES (?, ?, ?, 0.5, ?, ?)
    """, (content, category, tags, datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return True
```

---

### 3. daily-summarizer 无事实提取功能

**现象**：
- 生成的摘要只有话题列表
- "用户偏好记录" 和 "重要事实" 标注为"待人工或 LLM 补充"

**解决**：
升级到 v2.0，增加批量事实提取：

```python
def generate_daily_summary(today: str = None) -> tuple:
    """生成每日摘要 + 提取事实，返回 (摘要内容, 提取的事实列表)"""
    
    # ... 扫描所有会话 ...
    
    for msg in user_messages:
        content = msg.get("content", "")
        if contains_trigger(content):
            potential_facts.append(content)
    
    # 去重事实
    unique_facts = list(set(all_facts))
    
    # 生成摘要时包含提取的事实
    if unique_facts:
        content += "## 自动提取的事实\n\n"
        for fact in unique_facts:
            content += f"- {fact}\n"
    
    return content, unique_facts


def save_facts_to_store(facts: list) -> int:
    """批量保存事实到 fact_store"""
    saved = 0
    for fact in facts:
        category = classify_fact(fact)
        tags = "auto-extracted,daily_summarizer"
        if add_fact_to_store(fact, category, tags):
            saved += 1
    return saved
```

---

## 双重保障机制

```
用户对话
    ↓
【实时提取】post_llm_call hook → fact_store（即时生效）
    ├─ 触发词检测（"记住"、"偏好"、"下次"...）
    ├─ 自动分类（user_pref / project / tool / general）
    └─ 去重检查 → 插入
    ↓
【批量提取】每日 23:55 → fact_store（补充遗漏）
    ├─ 扫描当天所有会话
    ├─ 提取包含触发词的消息
    └─ 批量去重 → 插入
```

---

## 验证步骤

### 1. 测试 daily-summarizer

```bash
python3 ~/.hermes/skills/core/hierarchical-memory-system/scripts/daily-summarizer.py --dry-run
```

**预期输出**：
```
🧠 分层记忆系统 - 每日摘要生成器 v2.0
==================================================

📝 生成的摘要：
...

## 自动提取的事实

- 用户说：记住下次用表格
- 用户说：我的工作时间是夜班 20:00-08:00

🔍 检测到 2 条潜在事实
```

### 2. 测试 auto-fact-extract

```bash
echo '{"extra": {"user_message": "记住我的工作时间是夜班 20:00-08:00"}}' | \
  python3 ~/.hermes/agent-hooks/auto-fact-extract.py
```

**预期输出**：
```json
{
  "status": "fact_extracted",
  "category": "user_pref",
  "fact": "记住我的工作时间是夜班 20:00-08:00"
}
```

### 3. 检查 fact_store

```bash
sqlite3 ~/.hermes/memory_store.db "SELECT * FROM facts WHERE tags LIKE '%auto-extracted%' LIMIT 5"
```

---

## 避坑总结

### Cron Job 注册陷阱

| 错误方式 | 正确方式 |
|---------|---------|
| 创建 `cron.yaml` 文件 | 使用 `cronjob` 工具注册 |
| 手动编辑 crontab | Hermes 内置调度器 |
| 相对路径脚本 | 绝对路径或符号链接 |

### Hook 返回值陷阱

| 错误方式 | 正确方式 |
|---------|---------|
| `print("{}")` 只返回空 JSON | 在 Hook 内直接调用 API |
| 期望外部系统处理 | Hook 自包含逻辑 |

### 事实去重陷阱

| 错误方式 | 正确方式 |
|---------|---------|
| 直接 INSERT | 先 SELECT 检查重复 |
| 依赖数据库 UNIQUE 约束 | 应用层主动检查 |

---

## 文件清单

### 修改的文件

1. **`~/.hermes/agent-hooks/auto-fact-extract.py`** (升级)
   - 新增触发关键词（工作时间、夜班等）
   - 新增事实分类逻辑
   - 新增去重检查
   - 新增直接写入 fact_store

2. **`~/.hermes/skills/core/hierarchical-memory-system/scripts/daily-summarizer.py`** (升级 v2.0)
   - 新增批量事实提取
   - 新增事实去重
   - 新增 `--no-fact-store` 参数

### 新增的 Cron Job

- **Job ID**: `e391e39f07b3`
- **名称**: 每日记摘要 L1-L2
- **执行时间**: 每天 23:55
- **状态**: 已启用

---

## 后续维护

### 观察 7 天

1. 检查 L2 摘要是否正常生成
   ```bash
   ls -la ~/.hermes/memory/short-term/
   ```

2. 检查 fact_store 使用率
   ```bash
   sqlite3 ~/.hermes/memory_store.db "SELECT COUNT(*) FROM facts WHERE tags LIKE '%auto-extracted%'"
   ```

3. 检查 retrieval_count 是否增加
   ```bash
   sqlite3 ~/.hermes/memory_store.db "SELECT retrieval_count FROM facts ORDER BY retrieval_count DESC LIMIT 5"
   ```

### 优化建议

1. **触发词优化**：根据实际提取效果调整关键词列表
2. **分类优化**：改进 `classify_fact()` 函数，增加更多分类规则
3. **去重优化**：考虑语义去重（embedding 相似度）而非精确匹配
