#!/usr/bin/env python3
"""
并行任务调度器
同时启动 N 个 Hermes sub-agent 并行执行任务，最后汇总结果
"""

import json
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

HERMES_DIR = Path.home() / ".hermes"
SCHEDULER_DIR = HERMES_DIR / "skills" / "core" / "parallel-task-scheduler"


class ParallelTask:
    """单个并行任务"""
    def __init__(self, task_id: str, description: str, system_prompt: str = None):
        self.task_id = task_id
        self.description = description
        self.system_prompt = system_prompt or "你是一个专注的研究助手，只需要回答与任务相关的内容，不要闲聊。"
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.status = "pending"  # pending / running / completed / failed / timeout
    
    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class ParallelScheduler:
    """并行任务调度器"""
    
    def __init__(self, max_concurrent: int = 5, timeout_per_task: int = 300):
        self.max_concurrent = max_concurrent
        self.timeout_per_task = timeout_per_task
        self.tasks: List[ParallelTask] = []
    
    def add_task(self, description: str, system_prompt: str = None, task_id: str = None) -> str:
        """添加一个并行任务"""
        if task_id is None:
            task_id = f"task_{len(self.tasks) + 1}"
        
        task = ParallelTask(task_id, description, system_prompt)
        self.tasks.append(task)
        return task_id
    
    async def run_single_task(self, task: ParallelTask) -> ParallelTask:
        """执行单个任务"""
        task.status = "running"
        task.start_time = datetime.now()
        
        print(f"▶️  开始 [{task.task_id}]: {task.description[:50]}...")
        
        try:
            # 这里调用 Hermes 的 delegate_task 工具
            # 由于是在 Python 脚本中，我们通过 Hermes 工具系统调用
            result = await self._call_delegate_task(
                goal=task.description,
                context=f"你是专门执行这个任务的独立 Agent。任务：{task.description}",
                role="leaf",
            )
            
            task.result = result
            task.status = "completed"
            print(f"✅ 完成 [{task.task_id}] ({task.duration:.1f}s)")
            
        except asyncio.TimeoutError:
            task.status = "timeout"
            task.error = f"任务执行超时（{self.timeout_per_task}s）"
            print(f"⏰ 超时 [{task.task_id}]")
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            print(f"❌ 失败 [{task.task_id}]: {e}")
        finally:
            task.end_time = datetime.now()
        
        return task
    
    async def _call_delegate_task(self, goal: str, context: str, role: str = "leaf") -> dict:
        """调用 Hermes delegate_task 工具"""
        # 注意：在真实运行时，这个脚本会被 Hermes 调用，
        # 所以这里应该使用 Hermes 的内部工具调用机制
        
        # 模拟实现（真正运行时会替换成真实的 delegate_task）
        await asyncio.sleep(1)  # 模拟执行时间
        
        return {
            "status": "completed",
            "summary": f"任务完成：{goal[:30]}...（这是模拟结果）",
            "details": "这是模拟的子任务输出，真实运行时会由真正的 sub-agent 生成",
        }
    
    async def run_all(self) -> Dict:
        """运行所有任务"""
        print(f"\n⚡ 并行任务调度器启动")
        print(f"=" * 60)
        print(f"任务数量：{len(self.tasks)}")
        print(f"最大并发：{self.max_concurrent}")
        print(f"单任务超时：{self.timeout_per_task}s")
        print(f"=" * 60 + "\n")
        
        start_time = datetime.now()
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def run_with_semaphore(task):
            async with semaphore:
                return await self.run_single_task(task)
        
        # 并行执行所有任务
        tasks = [run_with_semaphore(task) for task in self.tasks]
        completed_tasks = await asyncio.gather(*tasks)
        
        total_duration = (datetime.now() - start_time).total_seconds()
        
        # 统计结果
        summary = self._generate_summary(completed_tasks, total_duration)
        
        return summary
    
    def _generate_summary(self, completed_tasks: List[ParallelTask], total_duration: float) -> Dict:
        """生成汇总报告"""
        completed = [t for t in completed_tasks if t.status == "completed"]
        failed = [t for t in completed_tasks if t.status == "failed"]
        timeout = [t for t in completed_tasks if t.status == "timeout"]
        
        results = []
        for task in completed_tasks:
            results.append({
                "task_id": task.task_id,
                "description": task.description,
                "status": task.status,
                "duration": task.duration,
                "result": task.result,
                "error": task.error,
            })
        
        # 交叉验证（检测矛盾点）
        conflicts = self._detect_conflicts(completed)
        
        return {
            "summary": {
                "total_tasks": len(completed_tasks),
                "completed": len(completed),
                "failed": len(failed),
                "timeout": len(timeout),
                "total_duration": total_duration,
                "avg_duration": sum(t.duration for t in completed_tasks) / len(completed_tasks) if completed_tasks else 0,
            },
            "results": results,
            "conflicts": conflicts,
            "recommendations": self._generate_recommendations(completed_tasks, conflicts),
        }
    
    def _detect_conflicts(self, completed_tasks: List[ParallelTask]) -> List[Dict]:
        """检测不同 Agent 结论的矛盾点"""
        # 简单实现：基于关键词的冲突检测
        # 真实实现应该用 Embedding 相似度 + 语义对比
        conflicts = []
        
        # 提取所有结论中的关键声明
        all_statements = []
        for task in completed_tasks:
            if task.result and isinstance(task.result, dict):
                summary = task.result.get("summary", "") or str(task.result)
                statements = [s.strip() for s in summary.split("\n") if s.strip()]
                for s in statements:
                    all_statements.append({"task_id": task.task_id, "statement": s})
        
        # 检测明显矛盾的关键词（简化实现）
        contradiction_pairs = [
            ("支持", "反对"), ("正确", "错误"), ("可行", "不可行"),
            ("推荐", "不推荐"), ("是", "否"), ("有", "没有"),
        ]
        
        for s1 in all_statements:
            for s2 in all_statements:
                if s1["task_id"] >= s2["task_id"]:
                    continue  # 避免重复检测
                for pos, neg in contradiction_pairs:
                    if pos in s1["statement"] and neg in s2["statement"]:
                        conflicts.append({
                            "type": "possible_contradiction",
                            "task_1": s1["task_id"],
                            "task_2": s2["task_id"],
                            "statement_1": s1["statement"][:100],
                            "statement_2": s2["statement"][:100],
                            "keyword_pair": (pos, neg),
                        })
        
        return conflicts
    
    def _generate_recommendations(self, completed_tasks: List[ParallelTask], conflicts: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if conflicts:
            recommendations.append(f"检测到 {len(conflicts)} 个可能的矛盾点，建议人工确认")
        
        failed = [t for t in completed_tasks if t.status in ["failed", "timeout"]]
        if failed:
            recommendations.append(f"有 {len(failed)} 个任务失败/超时，建议重试或降低并发度")
        
        durations = [t.duration for t in completed_tasks if t.duration > 0]
        if durations and max(durations) > 60:
            recommendations.append(f"部分任务执行时间过长（最长 {max(durations):.0f}s），建议拆分成更小的子任务")
        
        if not recommendations:
            recommendations.append("所有任务顺利完成，无明显问题")
        
        return recommendations


def print_report(summary: Dict):
    """打印美观的执行报告"""
    print("\n" + "=" * 60)
    print("   📊 并行任务执行报告")
    print("=" * 60)
    
    s = summary["summary"]
    print(f"""
执行概览：
  总任务数：{s['total_tasks']}
  成功：{s['completed']} ✅
  失败：{s['failed']} ❌
  超时：{s['timeout']} ⏰
  总耗时：{s['total_duration']:.1f}s
  平均耗时：{s['avg_duration']:.1f}s / 任务
""")
    
    print("-" * 60)
    print("任务详情：\n")
    
    for r in summary["results"]:
        status_icon = {"completed": "✅", "failed": "❌", "timeout": "⏰"}.get(r["status"], "❓")
        print(f"{status_icon} [{r['task_id']}] ({r['duration']:>5.1f}s) {r['description'][:40]}...")
    
    if summary["conflicts"]:
        print("\n" + "-" * 60)
        print("⚠️  可能的矛盾点：\n")
        for c in summary["conflicts"][:3]:  # 只显示前 3 个
            print(f"  - [{c['task_1']}] vs [{c['task_2']}]: 可能有矛盾 ({c['keyword_pair'][0]}/{c['keyword_pair'][1]})")
    
    print("\n" + "-" * 60)
    print("💡 建议：\n")
    for rec in summary["recommendations"]:
        print(f"  - {rec}")
    
    print("\n" + "=" * 60)


async def main():
    """测试入口"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 测试模式
        scheduler = ParallelScheduler(max_concurrent=3, timeout_per_task=60)
        
        scheduler.add_task("调研 OpenClaw 的架构设计")
        scheduler.add_task("调研 Claude Code 的架构设计")
        scheduler.add_task("调研 AutoGPT 的架构设计")
        
        summary = await scheduler.run_all()
        print_report(summary)
        
        return 0
    
    # 正常模式：从 stdin 读取任务配置
    config = json.loads(sys.stdin.read())
    
    scheduler = ParallelScheduler(
        max_concurrent=config.get("max_concurrent", 5),
        timeout_per_task=config.get("timeout_per_task", 300),
    )
    
    for task_config in config.get("tasks", []):
        scheduler.add_task(
            description=task_config["description"],
            system_prompt=task_config.get("system_prompt"),
            task_id=task_config.get("task_id"),
        )
    
    summary = await scheduler.run_all()
    
    # 输出 JSON 供 Hermes 后续处理
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    return 0


if __name__ == "__main__":
    asyncio.run(main())
