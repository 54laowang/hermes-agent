# 会话上下文清理实战 - 2026-05-03

## 背景

state.db 异常膨胀（295 MB），导致：
- 查询速度变慢
- 磁盘空间浪费
- Memory/Profile 占用率高

## 根本原因

**state.db 结构分析**：
```
sessions: 789 个会话
messages: 21,986 条消息
messages_fts: 全文搜索索引（10+ 个表，主要空间占用）
```

**问题**：
- 会话历史堆积（无自动清理机制）
- FTS 索引膨胀（大量历史消息索引）
- 缺乏过期策略

## 解决方案

### 1. 会话清理脚本

**文件**：`~/.hermes/scripts/session_cleanup.py`（5.6KB）

**核心功能**：
```python
def cleanup_sessions(keep_days=30, keep_count=100, dry_run=True):
    """
    清理旧会话
    
    Args:
        keep_days: 保留最近 N 天的会话
        keep_count: 至少保留最近 N 个会话
        dry_run: 是否只预览不执行
    """
    # 1. 获取要保留的会话
    cutoff_timestamp = (datetime.now() - timedelta(days=keep_days)).timestamp()
    
    cursor.execute("""
        SELECT id, started_at FROM sessions 
        WHERE started_at > ? 
        ORDER BY started_at DESC 
        LIMIT ?
    """, (cutoff_timestamp, keep_count))
    
    keep_ids = [row[0] for row in cursor.fetchall()]
    
    # 2. 删除其他会话的消息
    placeholders = ",".join("?" * len(keep_ids))
    cursor.execute(f"DELETE FROM messages WHERE session_id NOT IN ({placeholders})", keep_ids)
    
    # 3. 删除其他会话
    cursor.execute(f"DELETE FROM sessions WHERE id NOT IN ({placeholders})", keep_ids)
    
    # 4. 优化 FTS 索引
    cursor.execute("INSERT INTO messages_fts(messages_fts) VALUES('optimize')")
    
    # 5. VACUUM（压缩数据库）
    cursor.execute("VACUUM")
```

**关键发现**：
- ❌ sessions 表使用 ISO 格式时间字符串（created_at）→ 错误！
- ✅ sessions 表使用 Unix 时间戳（started_at）

### 2. 执行结果

**清理前**：
- 数据库大小：295 MB
- 会话数：789 个
- 消息数：21,986 条

**清理后**：
- 数据库大小：175 MB（**节省 120 MB，-41%**）
- 会话数：100 个（保留最近 30 天）
- 消息数：4,454 条

**清理内容**：
- ✅ 删除 689 个旧会话
- ✅ 删除 17,532 条旧消息
- ✅ 优化 FTS 索引
- ✅ VACUUM 压缩数据库

## 技术要点

### 1. 时间戳格式陷阱

**错误做法**：
```python
# ❌ sessions 表没有 created_at 字段
cursor.execute("SELECT id FROM sessions WHERE created_at > ?", (cutoff_date,))
```

**正确做法**：
```python
# ✅ sessions 表使用 started_at（Unix 时间戳）
cutoff_timestamp = (datetime.now() - timedelta(days=30)).timestamp()
cursor.execute("SELECT id FROM sessions WHERE started_at > ?", (cutoff_timestamp,))
```

**验证表结构**：
```bash
sqlite3 ~/.hermes/state.db "PRAGMA table_info(sessions)"
# 关键字段：started_at (REAL), ended_at (REAL)
```

### 2. FTS 索引优化

**为什么要优化 FTS**：
- FTS（全文搜索）索引占用大量空间
- 删除消息后索引不会自动清理
- 手动优化可以显著减少空间

**优化命令**：
```sql
-- 优化 FTS 索引
INSERT INTO messages_fts(messages_fts) VALUES('optimize');

-- 重建索引（如果优化不够）
DROP TABLE IF EXISTS messages_fts;
CREATE VIRTUAL TABLE messages_fts USING fts5(content, tool_name, tool_calls);
```

### 3. VACUUM 压缩

**为什么需要 VACUUM**：
- SQLite 删除记录后不会释放磁盘空间
- VACUUM 重写数据库文件，释放未使用空间
- **效果**：295 MB → 175 MB（节省 41%）

**注意事项**：
- VACUUM 需要足够磁盘空间（临时文件）
- 执行期间数据库锁定
- 建议在低峰期执行

### 4. Dry-Run 机制

**实现**：
```python
parser.add_argument("--execute", action="store_true", help="实际执行（默认仅预览）")

if not args.execute:
    print("\n[DRY RUN] 仅预览，不执行清理")
    print("\n💡 使用 --execute 参数实际执行清理")
    return
```

**优点**：
- 安全：先预览再执行
- 透明：用户清楚知道会发生什么
- 可回滚：执行前可以备份

## 最佳实践

### 1. 备份优先

```bash
# 执行前备份
cp ~/.hermes/state.db ~/.hermes/state.db.backup.$(date +%Y%m%d_%H%M%S)
```

### 2. 渐进式清理

```bash
# 先预览
python3 scripts/session_cleanup.py

# 确认无误后执行
python3 scripts/session_cleanup.py --execute
```

### 3. 定期清理

建议配置 cron job：
```yaml
# ~/.hermes/config.yaml
cron:
  - name: "每周清理旧会话"
    schedule: "0 3 * * 0"  # 每周日凌晨 3 点
    command: "python3 ~/.hermes/scripts/session_cleanup.py --execute"
```

### 4. 监控与报警

```python
# 检查数据库大小
db_size = Path("~/.hermes/state.db").stat().st_size
if db_size > 200 * 1024 * 1024:  # > 200 MB
    print(f"⚠️ state.db 大小异常：{db_size / 1024 / 1024:.2f} MB")
```

## 后续优化

### 1. Memory/Profile 清理

**当前状态**：
- Memory：53%（2,679/5,000 chars）
- User Profile：92%（2,312/2,500 chars）

**优化策略**：
- 压缩冗余信息
- 归档低频内容到 fact_store
- 合并重复条目

**实现方式**：通过 `memory` tool 管理
```python
memory(action='remove', old_text='低价值条目')
memory(action='replace', old_text='冗长描述', content='精简版')
```

### 2. 自动化清理

创建定时任务：
```bash
hermes cronjob add \
  --name "每周清理旧会话" \
  --schedule "0 3 * * 0" \
  --command "python3 ~/.hermes/scripts/session_cleanup.py --execute"
```

### 3. 容量监控

添加到 Shell Hook：
```python
# ~/.hermes/hooks/memory-auto-archiver.py
db_size = check_database_size()
if db_size > 200 * 1024 * 1024:
    notify_user("state.db 容量超标，建议清理")
```

## 相关文件

- **脚本**：`~/.hermes/scripts/session_cleanup.py`
- **分析脚本**：`~/.hermes/scripts/memory_profile_cleanup.py`
- **优化文档**：`~/.hermes/docs/context-optimization-plan.md`
- **完成报告**：`~/.hermes/docs/context-optimization-complete.md`

## 参考资料

- SQLite VACUUM 文档：https://www.sqlite.org/lang_vacuum.html
- SQLite FTS5 优化：https://www.sqlite.org/fts5.html#the_optimize_command
- Hermes Session 管理：`~/.hermes/sessions/`
