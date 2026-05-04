# 全局约束管理 - 快速使用指南

## 🚀 快速开始

### 1. 自动注入（推荐）

全局约束已通过 Shell Hook 自动生效，无需手动操作。

**验证是否生效**：
```bash
# 查看当前时间约束
python3 ~/.hermes/skills/core/global-constraints/scripts/constraint_checker.py
```

---

## 📋 约束检查清单

### 时间感知约束 ✅

| 时间段 | 自动行为 |
|--------|---------|
| 凌晨 00:00-05:00 | 🌙 强制提醒休息 |
| 清晨 05:00-08:00 | 🌅 关心夜班状态 |
| 深夜 22:00-24:00 | 🌙 提醒休息 |
| 周末 | 🎉 轻松语气 |

### Skill 执行约束 ✅

| Skill | 禁止工具 | 必须工具 |
|-------|---------|---------|
| iwencai-integration | web_search, read_url | execute_code |
| vibe-trading-integration | - | mcp_vibe_trading_* |

### 数据验证约束 ✅

- ✅ 最少 3 个数据源
- ✅ 必须有时间戳
- ✅ P0 级数据源优先

---

## 🔍 常用命令

### 查看当前约束状态

```bash
python3 ~/.hermes/skills/core/global-constraints/scripts/constraint_checker.py
```

### 查看约束配置

```bash
cat ~/.hermes/skills/core/global-constraints/references/constraints.yaml
```

### 查看违规日志

```bash
tail -50 ~/.hermes/logs/constraint_violations.log
```

---

## 💡 使用示例

### 示例 1：凌晨时段的请求

```
用户（02:30）：帮我分析茅台

【自动约束】：
- 检测到凌晨时段
- 自动注入提醒

【预期响应】：
🌙 现在凌晨2点半了，这么晚还在关心股票？
身体要紧，建议先休息。
如果一定要看，我简要总结一下...
```

### 示例 2：刚下夜班的请求

```
用户（06:45）：今天行情怎么样

【自动约束】：
- 检测到清晨时段
- 识别为夜班工作者刚下班

【预期响应】：
🌅 刚下夜班吧？辛苦了！
简要说一下：
- A股今天休市
- 美股昨晚收涨
详细的醒了再看，先休息！
```

### 示例 3：Skill 执行违规拦截

```
我：用 web_search 查询问财...

【自动约束】：
- 检测到禁止工具 web_search
- 自动拦截并记录

【系统提示】：
⚠️ 约束违规：Skill 'iwencai-integration' 禁止使用 web_search
必须使用：['execute_code']

【预期行为】：
- 停止执行
- 重新按规范执行
- 道歉并纠正
```

---

## 🛠️ 自定义配置

### 修改约束规则

编辑配置文件：
```bash
vim ~/.hermes/skills/core/global-constraints/references/constraints.yaml
```

### 添加新的 Skill 约束

在 `constraints.yaml` 中添加：
```yaml
skill_execution:
  your-skill-name:
    forbidden_tools:
      - tool1
      - tool2
    required_tools:
      - tool3
    data_source: "指定数据源"
    enforcement: strict
```

---

## 📊 监控与审计

### 每周审计

建议每周执行一次：
```bash
# 查看违规日志统计
cat ~/.hermes/logs/constraint_violations.log | jq -r '.type' | sort | uniq -c

# 识别高频违规
cat ~/.hermes/logs/constraint_violations.log | jq -r '.details.skill' | sort | uniq -c | sort -rn
```

### 违规类型统计

```bash
# 按违规类型统计
grep "forbidden_tool" ~/.hermes/logs/constraint_violations.log | wc -l
grep "missing_required_tool" ~/.hermes/logs/constraint_violations.log | wc -l
```

---

## ⚠️ 注意事项

1. **强制约束不可绕过**
   - 凌晨时段的提醒休息是最高优先级
   - Skill 禁止工具无法通过其他方式绕过

2. **违规记录永久保存**
   - 所有违规行为都会记录到日志
   - 可用于后续改进和审计

3. **约束优先级**
   ```
   时间约束 > 情境约束 > Skill约束 > 数据约束
   ```

4. **配置修改需重启**
   - 修改 `constraints.yaml` 后
   - 需要重启 Hermes 才能生效

---

## 🔗 相关资源

- **Skill 文档**：`~/.hermes/skills/core/global-constraints/SKILL.md`
- **约束配置**：`~/.hermes/skills/core/global-constraints/references/constraints.yaml`
- **检查器脚本**：`~/.hermes/skills/core/global-constraints/scripts/constraint_checker.py`
- **时间注入脚本**：`~/.hermes/skills/core/global-constraints/scripts/time_awareness_injector.sh`
- **违规日志**：`~/.hermes/logs/constraint_violations.log`

---

## 📞 问题排查

### 问题：约束检查器不生效

**检查**：
```bash
# 1. 确认文件存在
ls -la ~/.hermes/skills/core/global-constraints/scripts/

# 2. 确认有执行权限
chmod +x ~/.hermes/skills/core/global-constraints/scripts/*.py
chmod +x ~/.hermes/skills/core/global-constraints/scripts/*.sh
```

### 问题：时间注入未生效

**检查**：
```bash
# 1. 确认 Shell Hook 配置
grep "time_awareness_injector" ~/.hermes/config.yaml

# 2. 手动测试注入脚本
bash ~/.hermes/skills/core/global-constraints/scripts/time_awareness_injector.sh
```

---

## 🎯 最佳实践

1. **定期审查违规日志**
   - 每周查看高频违规场景
   - 针对性优化 Skill 或约束规则

2. **根据实际情况调整阈值**
   - 连续工作时间阈值
   - 数据源最小数量
   - 时间段划分

3. **保持约束配置同步**
   - 修改约束后更新 Skill 文档
   - 记录变更原因和影响

---

**最后更新**：2026-05-02 18:20
