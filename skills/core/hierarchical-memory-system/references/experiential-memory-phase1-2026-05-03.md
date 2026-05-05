# L2 自动摘要机制修复 + Experiential Memory Phase 1

## 修复时间

2026-05-03 08:30 - 09:00

## 问题诊断

### L2 自动摘要未运行

**症状**：
- `~/.hermes/memory/short-term/` 目录为空
- 没有每日摘要生成

**根因**：
1. 安装脚本只创建了 `cron.yaml` 文件，没有实际注册到系统 cron
2. `auto-fact-extract.py` 只记录日志，没有真正提取事实到 fact_store

### fact_store 缺少 Experiential Memory 支持

**症状**：
- fact_store 只有 `category` 字段（user_pref/project/tool/general）
- 缺少抽象层级、记忆强度、执行追踪等字段

**根因**：
- Schema 设计早于 arXiv:2512.13564 论文发布，未实现三层抽象

---

## 解决方案

### 1. 注册 L2 自动摘要 Cron Job

**工具**：Hermes 内置 `cronjob` 工具

```python
cronjob(
    action="create",
    name="每日记忆摘要 L1-L2",
    prompt="运行分层记忆系统的每日摘要生成器...",
    schedule="55 23 * * *"
)
```

**结果**：
- Job ID: `e391e39f07b3`
- 下次运行: 2026-05-03 23:55

### 2. 升级 auto-fact-extract.py

**关键改动**：

```python
# 旧版：只记录日志
with open(log_file, "a") as f:
    f.write(json.dumps(entry) + "\n")
print("{}")  # 返回空

# 新版：真正提取到 fact_store
def add_fact_to_store(content: str, category: str, tags: str) -> bool:
    conn = sqlite3.connect(str(FACT_STORE_DB))
    cursor = conn.cursor()
    
    # 检查重复
    cursor.execute(
        "SELECT id FROM facts WHERE content = ? AND category = ?",
        (content, category)
    )
    if cursor.fetchone():
        return False
    
    # 插入新事实
    cursor.execute("""
        INSERT INTO facts (content, category, tags, trust_score, created_at)
        VALUES (?, ?, ?, 0.5, ?)
    """, (content, category, tags, datetime.now().isoformat()))
    
    conn.commit()
    return True
```

**触发关键词扩展**：
- 新增："工作时间"、"夜班"、"早班" 等

### 3. 升级 daily-summarizer v2.0

**新增功能**：
- 批量扫描当天所有会话
- 提取包含触发关键词的用户消息
- 去重后批量写入 fact_store
- 自动清理 7 天前的 L2 记忆

### 4. Schema 升级（Experiential Memory）

**新增字段**：

```sql
ALTER TABLE facts ADD COLUMN memory_type TEXT DEFAULT 'factual';
-- factual / case / strategy / skill

ALTER TABLE facts ADD COLUMN abstraction_level INTEGER DEFAULT 0;
-- 0 = Factual, 1 = Case, 2 = Strategy, 3 = Skill

ALTER TABLE facts ADD COLUMN strength REAL DEFAULT 0.5;
-- 记忆强度（用于巩固/遗忘）

ALTER TABLE facts ADD COLUMN source_fact_ids TEXT DEFAULT '';
-- 来源事实ID（用于追溯抽象来源）

ALTER TABLE facts ADD COLUMN derived_fact_ids TEXT DEFAULT '';
-- 衍生事实ID（用于追踪抽象产物）

ALTER TABLE facts ADD COLUMN execution_count INTEGER DEFAULT 0;
ALTER TABLE facts ADD COLUMN success_count INTEGER DEFAULT 0;
ALTER TABLE facts ADD COLUMN last_used_at TIMESTAMP;
```

**新增触发器**：

```sql
-- 自动巩固
CREATE TRIGGER strengthen_memory AFTER UPDATE OF retrieval_count ON facts
WHEN NEW.retrieval_count > OLD.retrieval_count
BEGIN
    UPDATE facts SET 
        strength = MIN(1.0, strength + 0.1),
        last_used_at = CURRENT_TIMESTAMP
    WHERE fact_id = NEW.fact_id;
END;

-- 自动遗忘标记
CREATE TRIGGER check_forgetting AFTER UPDATE OF strength ON facts
WHEN NEW.strength < 0.1
BEGIN
    UPDATE facts SET tags = tags || ',pending-deletion' 
    WHERE fact_id = NEW.fact_id;
END;
```

---

## 新增文件

```
~/.hermes/
├── memory_store.db               # 已升级
├── memory_store_upgrade.sql      # 升级脚本
└── scripts/
    ├── experiential_memory.py         # 核心管理器（11.7 KB）
    ├── fact_store_extended.py         # 扩展接口（5.4 KB）
    └── skill_memory_integration.py    # Skill 集成（10.7 KB）
```

---

## 使用示例

### 添加案例

```python
from experiential_memory import ExperientialMemoryManager

emm = ExperientialMemoryManager()

case_id = emm.add_case(
    content="使用 time-anchor-constitution Skill 成功解决美股数据时间戳错误",
    category="problem-solving",
    tags="time,validation"
)
```

### 抽象为策略

```python
strategy_id = emm.abstract_cases_to_strategy(
    case_ids=[case_id],
    strategy_content="遇到美股分析任务时，必须先完成时间锚定检查"
)
```

### 记录执行结果

```python
emm.record_strategy_execution(strategy_id, success=True)
```

### 查询策略

```python
strategies = emm.get_strategies(limit=5, min_success_rate=0.5)
```

---

## 验证结果

```
记忆统计：
- factual: 81 条
- case: 26 条
- strategy: 1 条
- skill: 0 条
总计: 108 条
```

---

## 避坑指南

### Cron Job 注册

- ❌ 创建 `cron.yaml` ≠ 注册 cron job
- ✅ 使用 Hermes 内置 `cronjob` 工具

### Hook 返回值

- ❌ `print("{}")` 只返回空 JSON
- ✅ 在 Hook 内直接调用 fact_store API

### 脚本路径

- ❌ Hermes cronjob 不接受 `~` 开头的路径
- ✅ 创建符号链接到 `~/.hermes/scripts/`

### Schema 升级

- ❌ 直接修改 Python 代码不会自动升级数据库
- ✅ 创建 `.sql` 文件并执行 `sqlite3 db < upgrade.sql`

---

## 后续优化（Phase 2）

1. **自动化抽象**：检测相似案例，自动触发抽象
2. **智能遗忘**：基于时间衰减 + 使用频率
3. **跨模态支持**：图像/代码片段作为案例
4. **MemPalace 整合**：同步 Experiential Memory
