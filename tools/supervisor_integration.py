#!/usr/bin/env python3
"""
监察者模式集成模块 - Supervisor Mode Integration

非侵入式集成到 Hermes delegate_task
通过 wrapper 模式，无需修改核心代码

使用方法：
    from tools.supervisor_integration import delegate_task_with_supervisor
    
    result = delegate_task_with_supervisor(
        goal="...",
        context="...",
        supervisor=True,
        supervisor_config={...}
    )
"""

import json
import logging
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# 导入监察者核心
SUPERVISOR_AVAILABLE = False
try:
    sys.path.insert(0, str(Path.home() / ".hermes" / "scripts"))
    from supervisor import (
        Supervisor,
        Constraint,
        ConstraintExtractor,
        InterventionType,
    )
    SUPERVISOR_AVAILABLE = True
    logger.info("监察者模块已加载")
except ImportError as e:
    logger.warning(f"监察者模块未找到: {e}")


# ============================================================================
# 配置
# ============================================================================

DEFAULT_SUPERVISOR_CONFIG = {
    "enabled": False,
    "poll_interval": 2.0,
    "timeout": 3600,
    "auto_intervene": True,
    "sop": None,
    "constraints": [],
    "risk_level": "medium",  # low | medium | high
    "log_interventions": True,
}

RISK_LEVEL_POLL_INTERVALS = {
    "low": 5.0,
    "medium": 2.0,
    "high": 1.0,
}


# ============================================================================
# 辅助函数
# ============================================================================

def should_enable_supervisor(goal: str, context: str) -> bool:
    """判断是否应该启用监察者"""
    if not SUPERVISOR_AVAILABLE:
        return False
    
    high_risk_keywords = [
        "生产环境", "部署", "删除", "修改配置",
        "A股", "大盘", "股票", "数据分析", "爬取", "重要",
        "关键", "风险", "敏感", "分析"
    ]
    
    text = f"{goal} {context}"
    for keyword in high_risk_keywords:
        if keyword in text:
            return True
    
    return False


def extract_constraints_from_goal(goal: str, context: str) -> List[Constraint]:
    """从任务描述中提取约束"""
    constraints = []
    
    # 关键词匹配
    constraint_patterns = {
        "必须验证时间戳": ["时间戳", "时间", "日期", "时效性"],
        "必须使用权威数据源": ["数据源", "权威", "财联社", "官方"],
        "禁止使用过期数据": ["最新", "实时", "过期"],
        "必须遵循SOP": ["SOP", "流程", "标准化"],
        "必须处理错误": ["错误处理", "异常", "容错"],
    }
    
    text = f"{goal} {context}"
    for constraint_desc, keywords in constraint_patterns.items():
        for keyword in keywords:
            if keyword in text:
                constraints.append(Constraint(
                    description=constraint_desc,
                    type="must",
                    check_pattern=None,
                    severity="high"
                ))
                break
    
    return constraints


def build_supervisor_config(
    goal: str,
    context: str,
    user_config: Optional[Dict] = None
) -> Dict:
    """构建监察者配置"""
    config = DEFAULT_SUPERVISOR_CONFIG.copy()
    
    # 用户配置覆盖
    if user_config:
        config.update(user_config)
    
    # 自动判断是否启用
    if config["enabled"] is None or config["enabled"] == "auto":
        config["enabled"] = should_enable_supervisor(goal, context)
    
    # 根据风险等级调整轮询间隔
    risk_level = config.get("risk_level", "medium")
    if risk_level in RISK_LEVEL_POLL_INTERVALS:
        config["poll_interval"] = RISK_LEVEL_POLL_INTERVALS[risk_level]
    
    # 提取约束
    if not config.get("constraints"):
        config["constraints"] = extract_constraints_from_goal(goal, context)
    
    # 如果有 SOP，提取约束
    if config.get("sop"):
        try:
            extractor = ConstraintExtractor()
            sop_path = Path.home() / ".hermes" / "skills" / config["sop"] / "SKILL.md"
            if sop_path.exists():
                sop_constraints = extractor.extract_from_file(str(sop_path))
                config["constraints"].extend(sop_constraints)
        except Exception as e:
            logger.warning(f"提取 SOP 约束失败: {e}")
    
    return config


# ============================================================================
# 集成 Wrapper
# ============================================================================

class SupervisorWrapper:
    """监察者包装器 - 包装 delegate_task 结果"""
    
    def __init__(
        self,
        task_id: str,
        goal: str,
        context: str,
        supervisor_config: Dict,
        output_file: Path
    ):
        self.task_id = task_id
        self.goal = goal
        self.context = context
        self.config = supervisor_config
        self.output_file = output_file
        
        self.supervisor = None
        self.monitor_thread = None
        self.monitoring_active = False
        self.result = {
            "task_id": task_id,
            "status": "running",
            "interventions": [],
            "violations": [],
            "quality_score": None
        }
    
    def start_monitoring(self):
        """启动监控（后台线程）"""
        if not self.config.get("enabled"):
            return
        
        if not SUPERVISOR_AVAILABLE:
            logger.warning("监察者模块不可用，跳过监控")
            return
        
        try:
            # 创建监察者
            self.supervisor = Supervisor(
                task_id=self.task_id,
                constraints=self.config.get("constraints", []),
                sop_name=self.config.get("sop"),
                poll_interval=self.config.get("poll_interval", 2.0),
                auto_intervene=self.config.get("auto_intervene", True),
                task_dir=str(self.output_file.parent)
            )
            
            # 启动后台监控线程
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True
            )
            self.monitor_thread.start()
            
            logger.info(f"监察者已启动: {self.task_id}")
        
        except Exception as e:
            logger.error(f"启动监察者失败: {e}")
    
    def _monitor_loop(self):
        """监控循环（后台线程）"""
        try:
            # 简化的监控逻辑（避免阻塞）
            timeout = self.config.get("timeout", 3600)
            start_time = time.time()
            
            while self.monitoring_active:
                # 检查超时
                if time.time() - start_time > timeout:
                    self.result["status"] = "timeout"
                    break
                
                # 检查是否完成
                if self._is_task_complete():
                    self.result["status"] = "completed"
                    break
                
                # 读取输出
                new_content = self._read_new_output()
                if new_content:
                    # 分析输出
                    analysis = self.supervisor._analyze_output(new_content)
                    
                    # 应用干预
                    if analysis.get("needs_intervention") and self.config.get("auto_intervene"):
                        self.supervisor._apply_intervention(analysis)
                        self.result["interventions"].extend(
                            self.supervisor.state.interventions
                        )
                    
                    # 记录违规
                    if analysis.get("violations"):
                        self.result["violations"].extend(analysis["violations"])
                
                time.sleep(self.config.get("poll_interval", 2.0))
            
            # 验证完成质量
            if self.result["status"] == "completed":
                verification = self.supervisor._verify_completion()
                self.result["quality_score"] = verification.get("quality_score", 0)
        
        except Exception as e:
            logger.error(f"监控循环异常: {e}")
            self.result["status"] = "error"
            self.result["error"] = str(e)
    
    def _read_new_output(self) -> str:
        """读取新增输出"""
        try:
            if not self.output_file.exists():
                return ""
            
            with open(self.output_file, 'r', encoding='utf-8') as f:
                # 简化：读取最后 1KB
                f.seek(max(0, self.output_file.stat().st_size - 1024))
                return f.read()
        except Exception:
            return ""
    
    def _is_task_complete(self) -> bool:
        """检查任务是否完成"""
        try:
            # 检查停止文件
            stop_file = self.output_file.parent / "_stop"
            if stop_file.exists():
                return True
            
            # 检查输出中的完成标记
            content = self._read_new_output()
            completion_markers = ["任务完成", "TASK_COMPLETE", "SUCCESS", "[DONE]"]
            for marker in completion_markers:
                if marker in content:
                    return True
            
            return False
        except Exception:
            return False
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
    
    def get_result(self) -> Dict:
        """获取监控结果"""
        return self.result


# ============================================================================
# 集成入口
# ============================================================================

def delegate_task_with_supervisor(
    original_delegate_task,
    goal: Optional[str] = None,
    context: Optional[str] = None,
    toolsets: Optional[List[str]] = None,
    tasks: Optional[List[Dict[str, Any]]] = None,
    supervisor: Optional[bool] = None,
    supervisor_config: Optional[Dict] = None,
    **kwargs
) -> str:
    """
    带监察者的 delegate_task 包装器
    
    Args:
        original_delegate_task: 原始 delegate_task 函数
        goal: 任务目标
        context: 任务上下文
        toolsets: 工具集
        tasks: 批量任务
        supervisor: 是否启用监察者 (None=自动判断)
        supervisor_config: 监察者配置
        **kwargs: 其他参数
    
    Returns:
        JSON 字符串结果
    """
    # 构建监察者配置
    goal_text = goal or (tasks[0].get("goal", "") if tasks else "")
    context_text = context or (tasks[0].get("context", "") if tasks else "")
    
    config = build_supervisor_config(goal_text, context_text, supervisor_config or {})
    
    # 如果明确禁用或不可用，直接调用原函数
    if supervisor is False or not SUPERVISOR_AVAILABLE:
        return original_delegate_task(
            goal=goal,
            context=context,
            toolsets=toolsets,
            tasks=tasks,
            **kwargs
        )
    
    # 如果配置为启用或自动判断为启用
    if supervisor is True or config.get("enabled"):
        # 准备任务目录
        import uuid
        task_id = f"task_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        task_dir = Path.home() / ".hermes" / "tasks" / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = task_dir / "output.txt"
        output_file.touch()
        
        # 创建监察者包装器
        wrapper = SupervisorWrapper(
            task_id=task_id,
            goal=goal_text,
            context=context_text,
            supervisor_config=config,
            output_file=output_file
        )
        
        # 启动监控
        wrapper.start_monitoring()
        
        try:
            # 调用原始 delegate_task
            result_json = original_delegate_task(
                goal=goal,
                context=context,
                toolsets=toolsets,
                tasks=tasks,
                **kwargs
            )
            
            # 解析结果
            result = json.loads(result_json) if isinstance(result_json, str) else result_json
            
            # 停止监控
            wrapper.stop_monitoring()
            
            # 获取监察结果
            supervisor_result = wrapper.get_result()
            
            # 合并结果
            if isinstance(result, dict):
                result["supervisor"] = supervisor_result
            elif isinstance(result, list):
                for item in result:
                    if isinstance(item, dict):
                        item["supervisor"] = supervisor_result
            
            # 记录日志
            if config.get("log_interventions") and supervisor_result.get("interventions"):
                log_file = Path.home() / ".hermes" / "logs" / "supervisor_interventions.jsonl"
                log_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    log_entry = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "task_id": task_id,
                        "goal": goal_text[:100],
                        "interventions": supervisor_result["interventions"],
                        "quality_score": supervisor_result.get("quality_score")
                    }
                    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
            return json.dumps(result, ensure_ascii=False)
        
        except Exception as e:
            logger.error(f"delegate_task 执行失败: {e}")
            wrapper.stop_monitoring()
            
            return json.dumps({
                "error": str(e),
                "supervisor": wrapper.get_result()
            })
    
    else:
        # 未启用监察者，直接调用原函数
        return original_delegate_task(
            goal=goal,
            context=context,
            toolsets=toolsets,
            tasks=tasks,
            **kwargs
        )


# ============================================================================
# Monkey Patch 方式（可选）
# ============================================================================

def patch_delegate_task():
    """
    Monkey patch 方式替换 delegate_task
    
    使用方法：
        from tools.supervisor_integration import patch_delegate_task
        patch_delegate_task()
        
        # 之后所有 delegate_task 调用都会自动启用监察者
    """
    try:
        from tools import delegate_tool
        
        original_func = delegate_tool.delegate_task
        
        def patched_delegate_task(*args, **kwargs):
            return delegate_task_with_supervisor(
                original_func,
                *args,
                **kwargs
            )
        
        delegate_tool.delegate_task = patched_delegate_task
        logger.info("✅ delegate_task 已被监察者包装")
        
        return True
    except Exception as e:
        logger.error(f"Patch 失败: {e}")
        return False


# ============================================================================
# CLI 测试
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="监察者集成测试")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--patch", action="store_true", help="应用 monkey patch")
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 测试监察者集成")
        
        # 测试配置构建
        config = build_supervisor_config(
            "分析今日A股大盘走势",
            "当前时间：2026-04-30 02:10 深夜"
        )
        
        print(f"\n配置: {json.dumps(config, indent=2, ensure_ascii=False, default=str)}")
        
        # 测试约束提取
        constraints = extract_constraints_from_goal(
            "分析今日A股大盘，注意时间戳验证",
            "必须使用财联社数据源"
        )
        
        print(f"\n提取的约束 ({len(constraints)} 个):")
        for i, c in enumerate(constraints, 1):
            print(f"  {i}. {c.description}")
    
    elif args.patch:
        print("🔧 应用 monkey patch...")
        success = patch_delegate_task()
        print(f"结果: {'成功' if success else '失败'}")
