#!/usr/bin/env python3
"""
任务上下文检测 Hook
自动检测 LLM 输出中的任务关键词，创建/更新任务上下文

触发时机：post_llm_call（LLM 回复后）
功能：
1. 检测任务关键词（"第一步"、"首先"、"步骤"等）
2. 自动创建 TaskContext
3. 提取任务目标和约束
4. 注入上下文 Prompt 到下一轮对话
"""

import sys
import os
import re
import json
from datetime import datetime

# 添加 Hermes core 到路径
sys.path.insert(0, os.path.expanduser("~/.hermes/core"))

try:
    from task_context import get_task_context_manager, TaskContext
except ImportError:
    print("[TaskContext Hook] Warning: task_context module not found", file=sys.stderr)
    sys.exit(0)


def detect_task_keywords(text: str) -> dict:
    """检测任务关键词"""
    
    # 任务开始关键词
    start_keywords = [
        "第一步", "第二步", "第三步", "首先", "然后", "接着", "最后",
        "步骤", "流程", "计划", "我将", "我来", "让我",
        "Step 1", "Step 2", "First", "Then", "Finally"
    ]
    
    # 目标关键词
    goal_patterns = [
        r"目标[是为：:]\s*(.+)",
        r"任务[是为：:]\s*(.+)",
        r"我要(.+)",
        r"我来帮你(.+)",
        r"首先，?我[将 会](.+)"
    ]
    
    # 约束关键词
    constraint_keywords = [
        "必须", "需要", "要求", "注意", "确保", "避免", "禁止"
    ]
    
    result = {
        "has_task": False,
        "goal": None,
        "steps": [],
        "constraints": []
    }
    
    # 检测任务开始
    for keyword in start_keywords:
        if keyword in text:
            result["has_task"] = True
            break
    
    if not result["has_task"]:
        return result
    
    # 提取目标
    for pattern in goal_patterns:
        match = re.search(pattern, text)
        if match:
            result["goal"] = match.group(1).strip()
            break
    
    # 如果没有明确目标，尝试从第一句话提取
    if not result["goal"]:
        sentences = text.split("。")
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) < 100:
                result["goal"] = first_sentence
    
    # 提取步骤
    step_patterns = [
        r"第[一二三四五六七八九十]+步[，：:]?\s*(.+)",
        r"首先[，：:]?\s*(.+)",
        r"然后[，：:]?\s*(.+)",
        r"接着[，：:]?\s*(.+)",
        r"最后[，：:]?\s*(.+)",
        r"Step\s*\d+[：:.]?\s*(.+)",
    ]
    
    for pattern in step_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            step_text = match.group(1).strip()
            if step_text and len(step_text) > 2:
                result["steps"].append(step_text)
    
    # 提取约束
    sentences = text.split("。")
    for sentence in sentences:
        for keyword in constraint_keywords:
            if keyword in sentence:
                constraint = sentence.strip()
                if len(constraint) > 5 and constraint not in result["constraints"]:
                    result["constraints"].append(constraint)
                break
    
    return result


def extract_current_step(text: str) -> str:
    """提取当前步骤"""
    
    # 匹配 "正在...", "现在...", "接下来..."
    patterns = [
        r"现在[我正]?在(.+)",
        r"正在(.+)",
        r"接下来[我将会]?(.+)",
        r"我将开始(.+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    return ""


def detect_completion(text: str) -> bool:
    """检测任务完成"""
    
    completion_keywords = [
        "完成", "结束", "搞定", "done", "finished", "completed",
        "已完成", "已结束", "全部完成", "任务完成"
    ]
    
    return any(kw in text.lower() for kw in completion_keywords)


def main():
    """主函数"""
    
    # 读取 LLM 输出
    llm_output = sys.stdin.read()
    
    if not llm_output:
        sys.exit(0)
    
    # 获取任务管理器
    manager = get_task_context_manager()
    
    # 检测任务关键词
    task_info = detect_task_keywords(llm_output)
    
    # 获取当前任务
    current_task = manager.get_task()
    
    # 情况1：检测到新任务
    if task_info["has_task"] and not current_task:
        
        # 创建新任务
        task = manager.create_task(
            goal=task_info["goal"] or "未明确目标",
            constraints=task_info["constraints"],
            steps=task_info["steps"]
        )
        
        # 输出提示（会被注入到下一轮 Prompt）
        print(f"\n[TaskContext] 检测到新任务: {task.task_id}")
        print(f"[TaskContext] 目标: {task.goal}")
        if task_info["steps"]:
            print(f"[TaskContext] 步骤: {len(task_info['steps'])} 个")
        
        # 保存任务上下文提示到文件
        context_file = os.path.expanduser("~/.hermes/temp/task_context_inject.txt")
        os.makedirs(os.path.dirname(context_file), exist_ok=True)
        with open(context_file, 'w', encoding='utf-8') as f:
            f.write(task.get_context_prompt())
    
    # 情况2：已有任务，检测步骤更新
    elif current_task:
        
        # 检测当前步骤
        current_step = extract_current_step(llm_output)
        if current_step:
            manager.set_current_step(current_step)
            print(f"[TaskContext] 当前步骤: {current_step}")
        
        # 检测完成
        if detect_completion(llm_output):
            manager.complete_task()
            print(f"[TaskContext] 任务完成: {current_task.task_id}")
        else:
            # 更新上下文提示
            context_file = os.path.expanduser("~/.hermes/temp/task_context_inject.txt")
            os.makedirs(os.path.dirname(context_file), exist_ok=True)
            with open(context_file, 'w', encoding='utf-8') as f:
                f.write(current_task.get_context_prompt())


if __name__ == "__main__":
    main()
