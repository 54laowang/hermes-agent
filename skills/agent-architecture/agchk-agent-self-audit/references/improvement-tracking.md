# 安全改进追踪参考

## 改进追踪脚本

**位置**: `scripts/track_improvements.py`

**用途**: 记录改进效果，生成趋势报告，量化安全提升

## 使用方法

### 记录改进

```bash
python scripts/track_improvements.py record "P0 权限策略加固"
```

输出示例：
```
📝 记录改进: P0 权限策略加固
🔍 运行 agchk 审计...
✅ 设置基线: 青铜时代 (30/100)

📊 改进效果:
  基线: 30/100
  当前: 32/100
  变化: +2

  问题数:
    基线: 121
    当前: 115
    减少: 6
```

### 查看状态

```bash
python scripts/track_improvements.py status
```

输出：
```
📊 当前状态

  文明等级: 青铜时代
  成熟度评分: 32/100
  整体健康: critical
  最后审计: 2026-04-30T10:15:00

  问题分布:
    critical: 1
    high: 5
    medium: 35
    low: 74

📈 与基线对比:
  评分变化: +2
```

### 查看趋势

```bash
python scripts/track_improvements.py trend
```

输出：
```
📈 改进趋势

1. 2026-04-30 - P0 权限策略加固
   青铜时代 (32/100) | Δ+2

2. 2026-04-30 - P2 自动化改进机制
   青铜时代 (32/100) | Δ+2

📊 评分趋势:

  1 | ░░░░░░░░░░░░░░░░░░░░ 30
  2 | ██░░░░░░░░░░░░░░░░░░ 32
```

### 生成报告

```bash
python scripts/track_improvements.py report
```

报告保存在 `~/.hermes/improvements-report.md`

## 数据结构

**存储位置**: `~/.hermes/improvements.json`

**结构**:
```json
{
  "improvements": [
    {
      "timestamp": "2026-04-30T10:15:00",
      "description": "P0 权限策略加固",
      "audit": {
        "score": 32,
        "era": "青铜时代",
        "health": "critical",
        "severity_summary": {
          "critical": 1,
          "high": 5,
          "medium": 35,
          "low": 74
        }
      }
    }
  ],
  "baseline": {
    "score": 30,
    "era": "青铜时代",
    "health": "critical",
    "severity_summary": {...}
  },
  "current": {...}
}
```

## 工作流集成

### 改进后自动记录

```bash
# 1. 完成改进
# ... 修复安全问题 ...

# 2. 提交代码
git commit -m "security: 修复 exec/eval 使用"

# 3. 记录改进
python scripts/track_improvements.py record "修复 exec/eval 使用"

# 4. 查看效果
python scripts/track_improvements.py status
```

### 定期报告

```bash
# 每周一生成周报
python scripts/track_improvements.py report

# 每月生成月报
python scripts/track_improvements.py report
```

## 最佳实践

1. **及时记录**: 每次改进后立即运行 `record`
2. **定期查看**: 每周查看 `trend` 了解改进趋势
3. **量化目标**: 设定明确的评分目标（如达到铁器时代）
4. **对比分析**: 使用报告对比改进前后的差异

## 集成点

- **agchk 审计**: 每次记录时自动运行审计
- **改进报告**: 生成 Markdown 格式报告
- **数据分析**: JSON 格式数据便于程序化分析
- **基线对比**: 自动对比基线和当前状态

## 参考文档

- [安全自动化使用指南](../SECURITY-AUTOMATION-GUIDE.md)
- [P0 权限策略改进报告](../SECURITY-IMPROVEMENT-P0-PERMISSION-POLICY.md)
- [P2 自动化改进报告](../SECURITY-IMPROVEMENT-P2-AUTOMATION.md)
