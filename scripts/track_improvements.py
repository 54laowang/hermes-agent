#!/usr/bin/env python3
"""
安全改进追踪脚本
记录每次改进的效果，生成改进趋势报告

使用方法：
    python scripts/track_improvements.py [command]

命令：
    record <description>  - 记录一次改进
    status               - 查看当前状态
    trend                - 查看改进趋势
    report               - 生成完整报告

数据存储：
    ~/.hermes/improvements.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# 数据文件
DATA_FILE = Path.home() / ".hermes" / "improvements.json"


def load_data() -> Dict[str, Any]:
    """加载改进数据"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"improvements": [], "baseline": None, "current": None}


def save_data(data: Dict[str, Any]):
    """保存改进数据"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def run_agchk() -> Dict[str, Any]:
    """运行 agchk 审计并返回结果"""
    import subprocess

    try:
        # 运行 agchk
        result = subprocess.run(
            [
                "agchk",
                "audit",
                "--profile",
                "personal",
                ".",
                "-o",
                "/tmp/track-audit.json",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        # 读取结果
        with open("/tmp/track-audit.json", "r") as f:
            audit_data = json.load(f)

        return {
            "score": audit_data["maturity_score"]["score"],
            "era": audit_data["maturity_score"]["era_name"],
            "health": audit_data["executive_verdict"]["overall_health"],
            "severity_summary": audit_data["severity_summary"],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


def record_improvement(description: str):
    """记录一次改进"""
    print(f"📝 记录改进: {description}")

    # 运行审计
    print("🔍 运行 agchk 审计...")
    audit_result = run_agchk()

    if "error" in audit_result:
        print(f"❌ 审计失败: {audit_result['error']}")
        return

    # 加载数据
    data = load_data()

    # 设置基线（如果是第一次）
    if data["baseline"] is None:
        data["baseline"] = audit_result
        print(f"✅ 设置基线: {audit_result['era']} ({audit_result['score']}/100)")

    # 添加改进记录
    improvement = {
        "timestamp": datetime.now().isoformat(),
        "description": description,
        "audit": audit_result,
    }
    data["improvements"].append(improvement)

    # 更新当前状态
    data["current"] = audit_result

    # 保存
    save_data(data)

    # 显示对比
    if data["baseline"]:
        baseline_score = data["baseline"]["score"]
        current_score = audit_result["score"]
        delta = current_score - baseline_score

        print(f"\n📊 改进效果:")
        print(f"  基线: {baseline_score}/100")
        print(f"  当前: {current_score}/100")
        print(f"  变化: {'+' if delta >= 0 else ''}{delta}")

        # 问题减少统计
        baseline_issues = sum(data["baseline"]["severity_summary"].values())
        current_issues = sum(audit_result["severity_summary"].values())
        issues_delta = baseline_issues - current_issues

        print(f"\n  问题数:")
        print(f"    基线: {baseline_issues}")
        print(f"    当前: {current_issues}")
        print(f"    减少: {issues_delta}")


def show_status():
    """显示当前状态"""
    data = load_data()

    if data["current"] is None:
        print("❌ 无改进记录，请先运行 record 命令")
        return

    current = data["current"]

    print("📊 当前状态\n")
    print(f"  文明等级: {current['era']}")
    print(f"  成熟度评分: {current['score']}/100")
    print(f"  整体健康: {current['health']}")
    print(f"  最后审计: {current['timestamp']}\n")

    print("  问题分布:")
    for severity, count in current["severity_summary"].items():
        print(f"    {severity}: {count}")

    if data["baseline"]:
        print(f"\n📈 与基线对比:")
        delta = current["score"] - data["baseline"]["score"]
        print(f"  评分变化: {'+' if delta >= 0 else ''}{delta}")


def show_trend():
    """显示改进趋势"""
    data = load_data()

    if not data["improvements"]:
        print("❌ 无改进记录")
        return

    print("📈 改进趋势\n")

    # 显示每次改进
    for i, imp in enumerate(data["improvements"], 1):
        audit = imp["audit"]
        if "error" in audit:
            continue

        baseline_score = (
            data["baseline"]["score"] if data["baseline"] else audit["score"]
        )
        delta = audit["score"] - baseline_score

        print(f"{i}. {imp['timestamp'][:10]} - {imp['description'][:50]}")
        print(f"   {audit['era']} ({audit['score']}/100) | Δ{delta:+d}")

    # 趋势图（简单文本版）
    if len(data["improvements"]) > 1:
        print("\n📊 评分趋势:\n")
        scores = [
            imp["audit"]["score"]
            for imp in data["improvements"]
            if "error" not in imp["audit"]
        ]

        if scores:
            min_score = min(scores)
            max_score = max(scores)

            for i, score in enumerate(scores):
                bar_len = int((score - min_score) / max(1, max_score - min_score) * 20)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                print(f"  {i+1:2d} | {bar} {score}")


def generate_report():
    """生成完整报告"""
    data = load_data()

    if not data["improvements"]:
        print("❌ 无改进记录")
        return

    report = f"""# Hermes Agent 安全改进报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📊 执行摘要

"""

    if data["baseline"] and data["current"]:
        baseline = data["baseline"]
        current = data["current"]

        report += f"""| 指标 | 基线 | 当前 | 变化 |
|------|------|------|------|
| 文明等级 | {baseline['era']} | {current['era']} | - |
| 成熟度评分 | {baseline['score']}/100 | {current['score']}/100 | {current['score'] - baseline['score']:+d} |
| 整体健康 | {baseline['health']} | {current['health']} | - |

"""

    # 改进历史
    report += "## 📜 改进历史\n\n"

    for i, imp in enumerate(data["improvements"], 1):
        audit = imp["audit"]
        if "error" in audit:
            continue

        report += f"""### {i}. {imp['description']}

**时间**: {imp['timestamp'][:19]}
**等级**: {audit['era']} ({audit['score']}/100)

**问题分布**:
"""
        for severity, count in audit["severity_summary"].items():
            report += f"- {severity}: {count}\n"

        report += "\n"

    # 保存报告
    report_file = Path.home() / ".hermes" / "improvements-report.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report)

    print(f"✅ 报告已生成: {report_file}")
    print(f"\n{report}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "record":
        if len(sys.argv) < 3:
            print("用法: python scripts/track_improvements.py record <description>")
            return
        description = " ".join(sys.argv[2:])
        record_improvement(description)

    elif command == "status":
        show_status()

    elif command == "trend":
        show_trend()

    elif command == "report":
        generate_report()

    else:
        print(f"未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
