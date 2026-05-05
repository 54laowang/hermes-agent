#!/usr/bin/env python3
"""
全局约束检查器
在任务执行前后自动检查约束合规性
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class ConstraintChecker:
    """全局约束检查器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(Path.home() / ".hermes" / "constraints.yaml")
        self.constraints = self._load_constraints()
        self.violations = []
    
    def _load_constraints(self) -> Dict:
        """加载约束配置"""
        # 默认约束配置
        return {
            "time_awareness": {
                "late_night": {"start": 0, "end": 5, "priority": "highest", "action": "提醒休息"},
                "night": {"start": 22, "end": 24, "priority": "high", "action": "提醒休息"},
                "early_morning": {"start": 5, "end": 8, "priority": "medium", "action": "关心夜班状态"},
                "weekend": ["Saturday", "Sunday"],
            },
            "user_context": {
                "night_shift_worker": True,
                "work_hours": {"start": 20, "end": 8},  # 20:00-08:00
                "continuous_work_threshold": 3600,  # 1小时（秒）
                "task_count_threshold": 5,
            },
            "skill_execution": {
                "iwencai-integration": {
                    "forbidden_tools": ["web_search", "read_url", "mcp_vibe_trading_web_search"],
                    "required_tools": ["execute_code"],
                    "data_source": "同花顺问财",
                },
            },
            "data_validation": {
                "min_sources": 3,
                "require_timestamp": True,
                "allowed_sources": {
                    "P0": ["财联社电报", "交易所公告", "官方财报"],
                    "P1": ["东方财富", "同花顺", "Wind", "Choice"],
                    "P2": ["新浪财经", "证券时报", "上海证券报"],
                },
            },
        }
    
    def check_time_constraints(self) -> Dict[str, Any]:
        """检查时间约束"""
        now = datetime.now()
        hour = now.hour
        weekday = now.strftime("%A")
        weekday_num = now.isoweekday()  # 1=Monday, 7=Sunday
        
        result = {
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "hour": hour,
            "weekday": weekday,
            "time_period": self._get_time_period(hour),
            "is_late_night": 0 <= hour < 5,
            "is_night": hour >= 22,
            "is_early_morning": 5 <= hour < 8,
            "is_weekend": weekday_num >= 6,
            "alerts": [],
        }
        
        # 生成时间提醒
        if result["is_late_night"]:
            result["alerts"].append({
                "level": "highest",
                "message": "🌙 凌晨时段：最高优先级提醒用户休息",
                "action": "开场白必须提醒休息，禁止主动推送工作内容"
            })
        
        if result["is_night"]:
            result["alerts"].append({
                "level": "high",
                "message": "🌙 深夜时段：提醒用户休息",
                "action": "可选提醒休息，任务执行简洁高效"
            })
        
        if result["is_early_morning"]:
            result["alerts"].append({
                "level": "medium",
                "message": "🌅 清晨时段：关心夜班工作者状态",
                "action": "先关心休息，简洁执行"
            })
        
        if result["is_weekend"]:
            result["alerts"].append({
                "level": "low",
                "message": "🎉 周末时段：轻松语气",
                "action": "不主动推送工作话题"
            })
        
        # 检查夜班工作者状态
        if self.constraints["user_context"]["night_shift_worker"]:
            work_start = self.constraints["user_context"]["work_hours"]["start"]
            work_end = self.constraints["user_context"]["work_hours"]["end"]
            
            # 刚下夜班（6:00-8:00）
            if work_end <= hour < work_end + 2:
                result["just_got_off_work"] = True
                result["alerts"].append({
                    "level": "high",
                    "message": "🌅 用户刚下夜班：关心休息",
                    "action": "先关心休息，简洁执行，不拖延"
                })
            
            # 工作时段（20:00-08:00）
            if hour >= work_start or hour < work_end:
                result["is_working_hours"] = True
                result["alerts"].append({
                    "level": "medium",
                    "message": "⏰ 用户可能在工作中",
                    "action": "输出简洁，方便快速阅读"
                })
        
        return result
    
    def _get_time_period(self, hour: int) -> str:
        """获取时间段名称"""
        if 0 <= hour < 5:
            return "凌晨"
        elif 5 <= hour < 8:
            return "清晨"
        elif 8 <= hour < 12:
            return "上午"
        elif 12 <= hour < 14:
            return "中午"
        elif 14 <= hour < 18:
            return "下午"
        elif 18 <= hour < 20:
            return "傍晚"
        elif 20 <= hour < 22:
            return "晚上"
        else:
            return "深夜"
    
    def check_skill_constraints(
        self, 
        skill_name: str, 
        tool_choice: str,
        data_sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """检查 Skill 执行约束"""
        result = {
            "valid": True,
            "violations": [],
            "warnings": [],
            "skill": skill_name,
            "tool": tool_choice,
        }
        
        # 获取该 Skill 的约束配置
        skill_constraints = self.constraints["skill_execution"].get(skill_name, {})
        
        if not skill_constraints:
            result["warnings"].append(f"Skill '{skill_name}' 未定义执行约束")
            return result
        
        # 检查禁止工具
        forbidden = skill_constraints.get("forbidden_tools", [])
        if tool_choice in forbidden:
            result["valid"] = False
            result["violations"].append({
                "type": "forbidden_tool",
                "message": f"Skill '{skill_name}' 禁止使用 {tool_choice}",
                "expected": skill_constraints.get("required_tools", []),
            })
        
        # 检查必须工具
        required = skill_constraints.get("required_tools", [])
        if required and tool_choice not in required:
            result["valid"] = False
            result["violations"].append({
                "type": "missing_required_tool",
                "message": f"Skill '{skill_name}' 必须使用 {required}，而非 {tool_choice}",
                "expected": required,
            })
        
        # 检查数据源
        if data_sources:
            expected_source = skill_constraints.get("data_source")
            if expected_source and expected_source not in data_sources:
                result["valid"] = False
                result["violations"].append({
                    "type": "invalid_data_source",
                    "message": f"数据源应为 '{expected_source}'，而非 {data_sources}",
                    "expected": expected_source,
                })
        
        return result
    
    def check_data_constraints(
        self, 
        data_sources: List[str], 
        timestamps: List[str],
        require_p0: bool = False
    ) -> Dict[str, Any]:
        """检查数据约束"""
        result = {
            "valid": True,
            "violations": [],
            "warnings": [],
        }
        
        # 检查数据源数量
        min_sources = self.constraints["data_validation"]["min_sources"]
        if len(data_sources) < min_sources:
            result["valid"] = False
            result["violations"].append({
                "type": "insufficient_sources",
                "message": f"数据源数量不足：{len(data_sources)}/{min_sources}",
                "expected": min_sources,
            })
        
        # 检查时间戳
        if self.constraints["data_validation"]["require_timestamp"]:
            if not timestamps:
                result["valid"] = False
                result["violations"].append({
                    "type": "missing_timestamp",
                    "message": "缺少时间戳，无法验证数据时效性",
                })
        
        # 检查数据源级别（可选）
        if require_p0:
            p0_sources = self.constraints["data_validation"]["allowed_sources"]["P0"]
            has_p0 = any(src in p0_sources for src in data_sources)
            if not has_p0:
                result["valid"] = False
                result["violations"].append({
                    "type": "missing_p0_source",
                    "message": f"缺少 P0 级数据源：{p0_sources}",
                })
        
        return result
    
    def generate_time_awareness_message(self) -> str:
        """生成时间感知提示消息"""
        time_check = self.check_time_constraints()
        
        if not time_check["alerts"]:
            return ""
        
        messages = ["⏰ 时间感知提醒："]
        for alert in time_check["alerts"]:
            messages.append(f"  {alert['message']}")
            messages.append(f"  → {alert['action']}")
        
        return "\n".join(messages)
    
    def log_violation(
        self, 
        violation_type: str, 
        details: Dict[str, Any]
    ) -> None:
        """记录约束违规"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": violation_type,
            "details": details,
        }
        
        self.violations.append(log_entry)
        
        # 写入日志文件
        log_path = Path.home() / ".hermes" / "logs" / "constraint_violations.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_constraint_summary(self) -> str:
        """获取约束检查摘要"""
        time_check = self.check_time_constraints()
        
        summary = [
            f"🕐 当前时间：{time_check['current_time']}",
            f"📅 星期：{time_check['weekday']}",
            f"⏰ 时间段：{time_check['time_period']}",
            f"🎉 是否周末：{'是' if time_check['is_weekend'] else '否'}",
        ]
        
        if time_check.get("just_got_off_work"):
            summary.append("🌅 用户状态：刚下夜班")
        elif time_check.get("is_working_hours"):
            summary.append("⏰ 用户状态：工作中")
        
        if time_check["alerts"]:
            summary.append("\n⚠️ 时间约束提醒：")
            for alert in time_check["alerts"]:
                summary.append(f"  {alert['message']}")
        
        return "\n".join(summary)


def main():
    """主函数 - 用于测试和独立运行"""
    checker = ConstraintChecker()
    
    # 打印约束摘要
    print("=" * 60)
    print("全局约束检查")
    print("=" * 60)
    print(checker.get_constraint_summary())
    print()
    
    # 测试 Skill 约束检查
    print("=" * 60)
    print("Skill 执行约束测试")
    print("=" * 60)
    
    test_cases = [
        ("iwencai-integration", "web_search"),
        ("iwencai-integration", "execute_code"),
        ("unknown-skill", "some_tool"),
    ]
    
    for skill, tool in test_cases:
        result = checker.check_skill_constraints(skill, tool)
        status = "✅" if result["valid"] else "❌"
        print(f"\n{status} {skill} + {tool}")
        if result["violations"]:
            for v in result["violations"]:
                print(f"  ❌ {v['message']}")
        if result["warnings"]:
            for w in result["warnings"]:
                print(f"  ⚠️ {w}")
    
    print()


if __name__ == "__main__":
    main()
