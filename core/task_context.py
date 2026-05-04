#!/usr/bin/env python3
"""
L5 Context Memory - 任务上下文管理
补齐 Hermes 记忆系统最后一块拼图

功能：
- 任务特定上下文管理
- 步骤追踪
- 中间结果有序存储
- 约束条件管理
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger('TaskContext')


@dataclass
class TaskStep:
    """任务步骤"""
    name: str
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class TaskContext:
    """任务上下文"""
    task_id: str
    goal: str
    current_step: str = ""
    steps: List[TaskStep] = field(default_factory=list)
    intermediate_results: List[Dict] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_step(self, step_name: str, status: str = "pending"):
        """添加步骤"""
        step = TaskStep(name=step_name, status=status)
        self.steps.append(step)
        self.updated_at = datetime.now()
    
    def update_step(self, step_name: str, status: str = None, result: Any = None, error: str = None):
        """更新步骤状态"""
        for step in self.steps:
            if step.name == step_name:
                if status:
                    step.status = status
                    if status == "in_progress":
                        step.started_at = datetime.now()
                    elif status in ["completed", "failed"]:
                        step.completed_at = datetime.now()
                
                if result is not None:
                    step.result = result
                
                if error:
                    step.error = error
                
                self.updated_at = datetime.now()
                return
        
        # 如果步骤不存在，创建新步骤
        self.add_step(step_name, status or "in_progress")
    
    def add_result(self, step: str, result: Any, metadata: dict = None):
        """添加中间结果"""
        self.intermediate_results.append({
            "step": step,
            "result": result,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def add_constraint(self, constraint: str):
        """添加约束条件"""
        if constraint not in self.constraints:
            self.constraints.append(constraint)
            self.updated_at = datetime.now()
    
    def get_progress(self) -> Dict[str, int]:
        """获取任务进度"""
        total = len(self.steps)
        completed = sum(1 for s in self.steps if s.status == "completed")
        failed = sum(1 for s in self.steps if s.status == "failed")
        pending = sum(1 for s in self.steps if s.status == "pending")
        in_progress = sum(1 for s in self.steps if s.status == "in_progress")
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "in_progress": in_progress,
            "progress_percent": int(completed / total * 100) if total > 0 else 0
        }
    
    def get_context_prompt(self, max_results: int = 3) -> str:
        """生成上下文 Prompt"""
        prompt = f"### Task Context\n\n"
        prompt += f"**Task ID**: {self.task_id}\n"
        prompt += f"**Goal**: {self.goal}\n\n"
        
        # 进度信息
        progress = self.get_progress()
        if progress["total"] > 0:
            prompt += f"**Progress**: {progress['completed']}/{progress['total']} ({progress['progress_percent']}%)\n\n"
        
        # 当前步骤
        if self.current_step:
            prompt += f"**Current Step**: {self.current_step}\n\n"
        
        # 步骤列表
        if self.steps:
            prompt += "**Steps**:\n"
            for i, step in enumerate(self.steps, 1):
                status_icon = {
                    "pending": "⏸️",
                    "in_progress": "▶️",
                    "completed": "✅",
                    "failed": "❌"
                }.get(step.status, "❓")
                
                marker = "→" if step.name == self.current_step else " "
                prompt += f"{marker} {status_icon} {i}. {step.name}"
                
                if step.error:
                    prompt += f" (错误: {step.error[:50]}...)"
                
                prompt += "\n"
            prompt += "\n"
        
        # 约束条件
        if self.constraints:
            prompt += "**Constraints**:\n"
            for c in self.constraints:
                prompt += f"- {c}\n"
            prompt += "\n"
        
        # 最近结果
        if self.intermediate_results:
            prompt += f"**Recent Results** (last {max_results}):\n"
            for r in self.intermediate_results[-max_results:]:
                result_str = str(r['result'])
                if len(result_str) > 100:
                    result_str = result_str[:100] + "..."
                prompt += f"- [{r['step']}]: {result_str}\n"
            prompt += "\n"
        
        # 持续时间
        duration = (self.updated_at - self.created_at).total_seconds()
        if duration > 60:
            prompt += f"**Duration**: {int(duration // 60)}m {int(duration % 60)}s\n"
        
        return prompt
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "goal": self.goal,
            "current_step": self.current_step,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "result": s.result,
                    "error": s.error,
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None
                }
                for s in self.steps
            ],
            "intermediate_results": self.intermediate_results,
            "constraints": self.constraints,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def save(self, filepath: str):
        """保存到文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"Task context saved: {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'TaskContext':
        """从文件加载"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        ctx = cls(
            task_id=data["task_id"],
            goal=data["goal"],
            current_step=data.get("current_step", ""),
            constraints=data.get("constraints", []),
            metadata=data.get("metadata", {})
        )
        
        ctx.created_at = datetime.fromisoformat(data["created_at"])
        ctx.updated_at = datetime.fromisoformat(data["updated_at"])
        
        # 加载步骤
        for s in data.get("steps", []):
            step = TaskStep(
                name=s["name"],
                status=s["status"],
                result=s.get("result"),
                error=s.get("error")
            )
            if s.get("started_at"):
                step.started_at = datetime.fromisoformat(s["started_at"])
            if s.get("completed_at"):
                step.completed_at = datetime.fromisoformat(s["completed_at"])
            ctx.steps.append(step)
        
        # 加载中间结果
        ctx.intermediate_results = data.get("intermediate_results", [])
        
        return ctx


class TaskContextManager:
    """任务上下文管理器"""
    
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or os.path.expanduser("~/.hermes/task_contexts")
        self.contexts: Dict[str, TaskContext] = {}
        self.current_task_id: Optional[str] = None
        
        # 加载现有任务
        self._load_existing_tasks()
    
    def _load_existing_tasks(self):
        """加载现有任务"""
        if not os.path.exists(self.storage_dir):
            return
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.storage_dir, filename)
                    ctx = TaskContext.load(filepath)
                    self.contexts[ctx.task_id] = ctx
                except Exception as e:
                    logger.warning(f"Failed to load task context {filename}: {e}")
    
    def create_task(
        self, 
        task_id: str = None, 
        goal: str = "", 
        constraints: List[str] = None,
        steps: List[str] = None,
        metadata: dict = None
    ) -> TaskContext:
        """创建新任务"""
        # 自动生成 task_id
        if not task_id:
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建上下文
        ctx = TaskContext(
            task_id=task_id,
            goal=goal,
            constraints=constraints or [],
            metadata=metadata or {}
        )
        
        # 添加步骤
        if steps:
            for step in steps:
                ctx.add_step(step)
        
        # 保存到内存和磁盘
        self.contexts[task_id] = ctx
        self.current_task_id = task_id
        ctx.save(self._get_filepath(task_id))
        
        logger.info(f"Created task: {task_id} - {goal}")
        return ctx
    
    def get_task(self, task_id: str = None) -> Optional[TaskContext]:
        """获取任务"""
        if not task_id:
            task_id = self.current_task_id
        
        return self.contexts.get(task_id)
    
    def update_step(
        self, 
        step_name: str, 
        status: str = None, 
        result: Any = None, 
        error: str = None,
        task_id: str = None
    ):
        """更新步骤"""
        ctx = self.get_task(task_id)
        if ctx:
            ctx.update_step(step_name, status, result, error)
            ctx.save(self._get_filepath(ctx.task_id))
    
    def add_result(self, step: str, result: Any, metadata: dict = None, task_id: str = None):
        """添加结果"""
        ctx = self.get_task(task_id)
        if ctx:
            ctx.add_result(step, result, metadata)
            ctx.save(self._get_filepath(ctx.task_id))
    
    def set_current_step(self, step_name: str, task_id: str = None):
        """设置当前步骤"""
        ctx = self.get_task(task_id)
        if ctx:
            ctx.current_step = step_name
            ctx.updated_at = datetime.now()
            ctx.save(self._get_filepath(ctx.task_id))
    
    def complete_task(self, task_id: str = None, final_result: Any = None):
        """完成任务"""
        ctx = self.get_task(task_id)
        if ctx:
            if final_result:
                ctx.add_result("final", final_result)
            
            # 标记所有未完成步骤为完成
            for step in ctx.steps:
                if step.status in ["pending", "in_progress"]:
                    step.status = "completed"
                    step.completed_at = datetime.now()
            
            ctx.updated_at = datetime.now()
            ctx.save(self._get_filepath(ctx.task_id))
            logger.info(f"Task completed: {ctx.task_id}")
    
    def fail_task(self, error: str, task_id: str = None):
        """任务失败"""
        ctx = self.get_task(task_id)
        if ctx:
            ctx.add_result("error", error)
            ctx.updated_at = datetime.now()
            ctx.save(self._get_filepath(ctx.task_id))
            logger.error(f"Task failed: {ctx.task_id} - {error}")
    
    def clear_task(self, task_id: str = None):
        """清理任务"""
        if not task_id:
            task_id = self.current_task_id
        
        if task_id and task_id in self.contexts:
            # 删除文件
            filepath = self._get_filepath(task_id)
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # 从内存移除
            del self.contexts[task_id]
            
            # 如果是当前任务，清除引用
            if self.current_task_id == task_id:
                self.current_task_id = None
            
            logger.info(f"Task cleared: {task_id}")
    
    def list_tasks(self, status: str = None) -> List[Dict]:
        """列出任务"""
        tasks = []
        for task_id, ctx in self.contexts.items():
            progress = ctx.get_progress()
            task_info = {
                "task_id": task_id,
                "goal": ctx.goal,
                "current_step": ctx.current_step,
                "progress": progress,
                "created_at": ctx.created_at.isoformat(),
                "updated_at": ctx.updated_at.isoformat()
            }
            
            # 状态过滤
            if status:
                if status == "in_progress" and progress["in_progress"] > 0:
                    tasks.append(task_info)
                elif status == "completed" and progress["pending"] == 0 and progress["in_progress"] == 0:
                    tasks.append(task_info)
            else:
                tasks.append(task_info)
        
        return sorted(tasks, key=lambda x: x["updated_at"], reverse=True)
    
    def get_context_prompt(self, task_id: str = None, max_results: int = 3) -> str:
        """获取上下文 Prompt"""
        ctx = self.get_task(task_id)
        if ctx:
            return ctx.get_context_prompt(max_results)
        return ""
    
    def _get_filepath(self, task_id: str) -> str:
        """获取任务文件路径"""
        return os.path.join(self.storage_dir, f"{task_id}.json")


# 全局单例
_task_context_manager = None

def get_task_context_manager() -> TaskContextManager:
    """获取全局任务上下文管理器"""
    global _task_context_manager
    if _task_context_manager is None:
        _task_context_manager = TaskContextManager()
    return _task_context_manager


# 便捷函数
def create_task(goal: str, constraints: List[str] = None, steps: List[str] = None) -> TaskContext:
    """创建任务"""
    return get_task_context_manager().create_task(goal=goal, constraints=constraints, steps=steps)

def get_current_task() -> Optional[TaskContext]:
    """获取当前任务"""
    return get_task_context_manager().get_task()

def update_step(step_name: str, status: str = None, result: Any = None):
    """更新步骤"""
    get_task_context_manager().update_step(step_name, status, result)

def add_result(step: str, result: Any):
    """添加结果"""
    get_task_context_manager().add_result(step, result)

def get_context_prompt() -> str:
    """获取上下文 Prompt"""
    return get_task_context_manager().get_context_prompt()


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 创建任务
    manager = get_task_context_manager()
    task = manager.create_task(
        goal="分析 A 股市场近期走势",
        constraints=[
            "必须验证时间戳",
            "至少 3 个数据源交叉验证",
            "优先使用 P0 级数据源"
        ],
        steps=[
            "获取当前时间",
            "判断市场状态",
            "获取行情数据",
            "交叉验证",
            "生成分析报告"
        ]
    )
    
    print(task.get_context_prompt())
    
    # 更新步骤
    manager.update_step("获取当前时间", "completed", "2026-05-04 06:20:00")
    manager.set_current_step("判断市场状态")
    manager.update_step("判断市场状态", "in_progress")
    
    print("\n" + "="*50 + "\n")
    print(task.get_context_prompt())
    
    # 添加结果
    manager.add_result("判断市场状态", "A股已收盘（15:00后）")
    manager.update_step("判断市场状态", "completed")
    
    print("\n" + "="*50 + "\n")
    print(task.get_context_prompt())
