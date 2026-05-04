---
name: supervisor-mode
description: |
  监察者模式 - 主 Agent 不干活，只监控 subagent 执行过程，通过干预文件实时纠偏。适用于复杂多步骤任务、高风险操作、需要质量把关的场景。
  
  Use when: 监察者, supervisor, 监控agent, 纠偏, 质量把关, subagent监控, 任务监督.
  
  Do NOT use for:
  - 直接执行任务（用其他执行类 skills）
  - 简单单步任务（无需监控）
  - 低风险操作（测试环境、本地实验）
  - 实时交互任务（需要用户反馈的任务）
version: 1.3.0
category: agent-optimization
author: Hermes + GenericAgent
tags: [monitoring, subagent, quality-control, intervention]
keywords:
  - 监察者
  - supervisor
  - 监控agent
  - 纠偏
  - 质量把关
  - subagent监控
triggers:
  - 监察者模式
  - supervisor mode
  - 监控agent
  - 纠偏
  - 质量把关
  - 任务监督
---

# 监察者模式 (Supervisor Mode)

## 核心理念

> 你是挑刺的监工，不是干活的工人。你的唯一任务：确保工作 agent 高质量完成任务。有 SOP 按 SOP 约束，无 SOP 凭常理和经验把关。

**三大红线**：
1. ❌ **禁止下场干活**：不操作浏览器、不写代码、不执行任务步骤
2. ✅ **可以读环境**：`file_read` / `web_scan` / `code_run(只读命令)` 获取情报
3. ✅ **只做判断和干预**：检查约束、发现偏差、实时纠偏

## 使用场景

### 场景 1：有 SOP 的任务（推荐）
```
用户任务：用 A股市场分析标准化流程 分析今日大盘
启动命令：python agentmain.py --task stock_analysis --bg --verbose
监察重点：
  - 是否先获取精确时间
  - 是否判断盘前/盘后状态
  - 数据源是否使用财联社（P0级）
  - 时间戳是否三重校验
```

### 场景 2：无 SOP 的复杂任务
```
用户任务：爬取某网站数据并生成报告
启动命令：python agentmain.py --task web_scrape --bg
监察重点：
  - 是否遵循 robots.txt
  - 是否处理反爬机制
  - 错误是否优雅降级
  - 输出格式是否符合预期
```

### 场景 3：高风险操作
```
用户任务：部署到生产环境
启动命令：python agentmain.py --task deploy_prod --bg
监察重点：
  - 是否有备份
  - 是否有回滚计划
  - 是否通知相关方
  - 是否验证结果
```

## 完整工作流程

### 第零步：环境预检（新增）

> ⚠️ **必须在启动监控前执行**，确保环境就绪。

#### 0.1 环境检查清单
```python
def pre_flight_check():
    """
    监控启动前的环境检查
    """
    checks = []
    
    # 检查 1：任务目录是否存在
    task_dir = f"~/.hermes/tasks/{task_id}"
    if not os.path.exists(task_dir):
        os.makedirs(task_dir, exist_ok=True)
        checks.append(("task_dir", "created", "OK"))
    else:
        checks.append(("task_dir", "exists", "OK"))
    
    # 检查 2：输出文件是否可写
    output_file = f"{task_dir}/output.txt"
    try:
        with open(output_file, 'a') as f:
            f.write("")  # 测试写入
        checks.append(("output_file", "writable", "OK"))
    except PermissionError:
        checks.append(("output_file", "permission_denied", "FAIL"))
        raise EnvironmentError(f"无法写入输出文件: {output_file}")
    
    # 检查 3：干预文件目录权限
    for intervention_file in ["_intervene", "_keyinfo", "_stop"]:
        try:
            test_path = f"{task_dir}/{intervention_file}"
            if os.path.exists(test_path):
                os.remove(test_path)  # 清理旧文件
        except Exception as e:
            checks.append((intervention_file, str(e), "WARN"))
    
    # 检查 4：日志目录
    log_dir = "~/.hermes/logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        checks.append(("log_dir", "created", "OK"))
    
    # 检查 5：依赖文件（如 SOP）
    if sop_name:
        sop_path = f"~/.hermes/skills/{sop_name}/SKILL.md"
        if not os.path.exists(sop_path):
            checks.append(("sop_file", "not_found", "WARN"))
            print(f"警告：SOP 文件不存在: {sop_path}")
        else:
            checks.append(("sop_file", "exists", "OK"))
    
    return {
        "status": "READY" if all(c[2] == "OK" for c in checks) else "WARNINGS",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }
```

#### 0.2 快速检查模板
```python
# 在启动监控前调用
result = pre_flight_check()
if result["status"] != "READY":
    print(f"⚠️ 环境检查有警告：{result['checks']}")
    # 决定是否继续
```

---

### 第一步：准备阶段

#### 1.1 提取约束清单
```python
# 如果有 SOP
sop_content = read_file("~/.hermes/skills/a-stock-market-time-aware-analysis/SKILL.md")
constraints = extract_constraints(sop_content)  # 提取 ⚠️/禁止/必须/格式要求

# 如果无 SOP
constraints = infer_constraints_from_task(task_description)
```

#### 1.2 启动 subagent
```bash
# 在 Hermes 中使用 delegate_task
result = delegate_task(
    goal="用 A股市场分析标准化流程 分析今日大盘",
    context="当前时间：2026-04-30 01:54，深夜，需注意数据时效性",
    role="leaf",
    toolsets=["web", "terminal", "file"]
)

# 获取 task_id 用于后续监控
task_id = result.get("task_id")
```

#### 1.3 记录初始状态
```python
working_memory = {
    "task_id": task_id,
    "constraints": constraints,
    "current_step": "启动",
    "start_time": "2026-04-30 01:54:34",
    "output_file": f"~/.hermes/tasks/{task_id}/output.txt",
    "interventions": []
}
```

### 第二步：监控循环

#### 2.1 轮询输出文件
```python
import time

def monitor_subagent(task_id, constraints, poll_interval=2):
    """
    持续监控 subagent 执行过程
    """
    output_file = f"~/.hermes/tasks/{task_id}/output.txt"
    last_position = 0
    
    while True:
        # 读取新增内容
        with open(output_file, 'r') as f:
            f.seek(last_position)
            new_content = f.read()
            last_position = f.tell()
        
        if new_content:
            # 分析新输出
            analysis = analyze_output(new_content, constraints)
            
            # 判断是否需要干预
            if analysis.needs_intervention:
                apply_intervention(task_id, analysis.intervention_type, analysis.message)
        
        # 检查是否完成
        if is_task_complete(new_content):
            break
        
        time.sleep(poll_interval)
```

#### 2.2 分析输出
```python
def analyze_output(content, constraints):
    """
    分析 subagent 输出，判断是否需要干预
    """
    # 检测当前步骤
    current_step = detect_current_step(content)
    
    # 对照约束清单
    violations = check_constraints(content, constraints)
    
    # 检测异常模式
    anomalies = detect_anomalies(content)
    
    return {
        "current_step": current_step,
        "needs_intervention": len(violations) > 0 or len(anomalies) > 0,
        "intervention_type": determine_intervention_type(violations, anomalies),
        "message": generate_intervention_message(violations, anomalies)
    }
```

#### 2.3 判断逻辑表

| 发现 | 干预类型 | 示例消息 |
|------|---------|---------|
| 跳步 | `_intervene` | "你跳过了 Step 2（获取精确时间），先做这一步" |
| 细节遗漏 | `_intervene` | "你漏了约束：必须使用财联社作为数据源，重做" |
| 光说不做 | `_intervene` | "别分析了，直接执行搜索" |
| 断言无据 | `_intervene` | "你怎么确认数据是最新的？验证一下时间戳" |
| 连续失败 | `_intervene` | "停，先读错误日志 `/tmp/agent_error.log` 再决定" |
| 感觉要偏 | `_intervene` | "去重读 SOP 的 Step 3 再继续" |
| 即将进入关键步骤 | `_keyinfo` | "下一步需要调用财联社 API，注意 token 参数" |
| 严重错误 | `_stop` | "检测到严重错误，立即停止" |

### 第三步：干预机制

#### 3.1 干预文件协议
```python
# 三种干预文件
def apply_intervention(task_id, intervention_type, message):
    """
    应用干预（带异常处理）
    """
    task_dir = os.path.expanduser(f"~/.hermes/tasks/{task_id}")
    
    # 异常处理：任务目录不存在
    if not os.path.exists(task_dir):
        raise FileNotFoundError(
            f"任务目录不存在: {task_dir}\n"
            "可能原因：subagent 未正确启动或 task_id 无效\n"
            "解决方案：检查 delegate_task 返回值，确认 task_id 正确"
        )
    
    try:
        if intervention_type == "_intervene":
            # 追加指令（当前轮结束后生效）
            file_path = f"{task_dir}/_intervene"
            with open(file_path, 'w') as f:
                f.write(f"[{datetime.now().isoformat()}] {message}")
            log_intervention(task_id, intervention_type, message, "success")
        
        elif intervention_type == "_keyinfo":
            # 注入 working memory（立即生效）
            file_path = f"{task_dir}/_keyinfo"
            with open(file_path, 'w') as f:
                f.write(f"[{datetime.now().isoformat()}] {message}")
            log_intervention(task_id, intervention_type, message, "success")
        
        elif intervention_type == "_stop":
            # 停止任务
            file_path = f"{task_dir}/_stop"
            with open(file_path, 'w') as f:
                f.write(f"[{datetime.now().isoformat()}] {message}")
            log_intervention(task_id, intervention_type, message, "success")
        
        else:
            raise ValueError(f"未知的干预类型: {intervention_type}")
    
    except PermissionError as e:
        log_intervention(task_id, intervention_type, message, f"permission_error: {e}")
        raise PermissionError(
            f"无法写入干预文件: {file_path}\n"
            "可能原因：权限不足\n"
            "解决方案：检查目录权限或使用 sudo"
        )
    
    except IOError as e:
        log_intervention(task_id, intervention_type, message, f"io_error: {e}")
        raise IOError(
            f"写入干预文件失败: {file_path}\n"
            f"错误详情: {e}\n"
            "解决方案：检查磁盘空间和文件系统状态"
        )

def log_intervention(task_id, intervention_type, message, status):
    """记录干预行为到日志"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "task_id": task_id,
        "type": intervention_type,
        "message": message,
        "status": status
    }
    log_file = os.path.expanduser(f"~/.hermes/logs/interventions_{datetime.now().strftime('%Y%m%d')}.jsonl")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + "\n")
```

#### 3.2 干预文件不存在时的处理

```python
def read_intervention_file(task_id, intervention_type):
    """
    安全读取干预文件（带降级处理）
    """
    task_dir = os.path.expanduser(f"~/.hermes/tasks/{task_id}")
    file_path = f"{task_dir}/{intervention_type}"
    
    if not os.path.exists(file_path):
        return None  # 文件不存在，返回 None（正常情况）
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # 读取后删除文件（避免重复执行）
        os.remove(file_path)
        
        return content
    
    except PermissionError:
        print(f"警告：无法读取干预文件 {file_path}，权限不足")
        return None
    
    except IOError as e:
        print(f"警告：读取干预文件失败 {file_path}: {e}")
        return None
```

---

### 第四步：Subagent 失败恢复机制（新增）

> ⚠️ **关键边界条件**：当 subagent 失败时，需要自动恢复或优雅降级。

#### 4.1 失败检测与分类

```python
class SubagentFailure:
    """Subagent 失败类型枚举"""
    TIMEOUT = "timeout"           # 超时
    CRASH = "crash"               # 进程崩溃
    STUCK = "stuck"               # 卡住无输出
    CONSTRAINT_VIOLATION = "constraint_violation"  # 约束违规
    RESOURCE_ERROR = "resource_error"  # 资源错误（内存、磁盘等）

def detect_failure(output_content, last_activity_time, timeout=300):
    """
    检测 subagent 失败类型
    
    Args:
        output_content: 当前输出内容
        last_activity_time: 最后活动时间
        timeout: 超时阈值（秒）
    
    Returns:
        SubagentFailure | None
    """
    # 检测超时
    if time.time() - last_activity_time > timeout:
        return SubagentFailure.TIMEOUT
    
    # 检测崩溃（关键词匹配）
    crash_patterns = [
        "Traceback (most recent call last)",
        "Segmentation fault",
        "AssertionError",
        "OutOfMemoryError",
        "Process finished with exit code"
    ]
    for pattern in crash_patterns:
        if pattern in output_content:
            return SubagentFailure.CRASH
    
    # 检测卡住（长时间无输出）
    if len(output_content.strip()) == 0 and time.time() - last_activity_time > 60:
        return SubagentFailure.STUCK
    
    return None
```

#### 4.2 恢复策略

```python
def recover_from_failure(task_id, failure_type, context):
    """
    根据 failure 类型选择恢复策略
    
    Returns:
        dict: {"action": "retry|abort|escalate", "message": "..."}
    """
    recovery_config = {
        SubagentFailure.TIMEOUT: {
            "max_retries": 2,
            "action": "retry",
            "backoff": 5,  # 秒
            "message": "任务超时，正在重试..."
        },
        SubagentFailure.CRASH: {
            "max_retries": 1,
            "action": "retry",
            "backoff": 3,
            "message": "检测到崩溃，尝试重启任务..."
        },
        SubagentFailure.STUCK: {
            "max_retries": 1,
            "action": "intervene",  # 注入干预
            "message": "任务卡住，注入提示继续执行"
        },
        SubagentFailure.CONSTRAINT_VIOLATION: {
            "max_retries": 0,
            "action": "abort",
            "message": "约束违规，终止任务"
        },
        SubagentFailure.RESOURCE_ERROR: {
            "max_retries": 0,
            "action": "escalate",
            "message": "资源不足，需要人工介入"
        }
    }
    
    config = recovery_config.get(failure_type, {"action": "abort", "message": "未知错误"})
    
    # 检查重试次数
    retry_count = context.get("retry_count", 0)
    max_retries = config.get("max_retries", 0)
    
    if retry_count >= max_retries:
        return {
            "action": "abort",
            "message": f"已达到最大重试次数 ({max_retries})，终止任务"
        }
    
    return {
        "action": config["action"],
        "message": config["message"],
        "backoff": config.get("backoff", 0),
        "retry_count": retry_count + 1
    }
```

#### 4.3 自动重试流程

```python
def execute_with_recovery(delegate_func, goal, context, max_total_retries=3):
    """
    带自动恢复的执行流程
    
    Args:
        delegate_func: delegate_task 函数
        goal: 任务目标
        context: 上下文
        max_total_retries: 最大总重试次数
    
    Returns:
        dict: 执行结果
    """
    total_retries = 0
    last_result = None
    
    while total_retries < max_total_retries:
        # 启动任务
        result = delegate_func(goal=goal, context=context)
        task_id = result.get("task_id")
        
        # 启动监控
        monitor = SupervisorMonitor(task_id, constraints=extract_constraints(goal))
        
        try:
            monitor.start()
            
            # 等待完成或失败
            while monitor.is_running():
                failure = detect_failure(
                    monitor.get_output(),
                    monitor.last_activity_time
                )
                
                if failure:
                    recovery = recover_from_failure(
                        task_id, 
                        failure,
                        {"retry_count": total_retries}
                    )
                    
                    if recovery["action"] == "retry":
                        total_retries += 1
                        print(f"🔄 {recovery['message']} (重试 {total_retries}/{max_total_retries})")
                        time.sleep(recovery.get("backoff", 5))
                        break  # 跳出监控循环，重新启动
                    
                    elif recovery["action"] == "abort":
                        return {
                            "status": "failed",
                            "reason": failure,
                            "message": recovery["message"],
                            "output": monitor.get_output()
                        }
                    
                    elif recovery["action"] == "escalate":
                        # 需要人工介入
                        return {
                            "status": "needs_attention",
                            "reason": failure,
                            "message": recovery["message"],
                            "output": monitor.get_output()
                        }
                
                time.sleep(2)  # 轮询间隔
        
        except Exception as e:
            print(f"监控异常: {e}")
            total_retries += 1
            continue
    
    # 达到最大重试次数
    return {
        "status": "failed",
        "reason": "max_retries_exceeded",
        "message": f"已重试 {max_total_retries} 次仍失败",
        "last_result": last_result
    }
```

#### 4.4 失败恢复配置

```yaml
# ~/.hermes/config/supervisor_recovery.yaml
recovery:
  enabled: true
  
  timeouts:
    task_timeout: 3600        # 任务总超时（秒）
    activity_timeout: 300     # 无活动超时（秒）
    output_timeout: 60        # 无输出超时（秒）
  
  retry_policy:
    max_retries: 3
    backoff_strategy: exponential  # linear | exponential
    initial_backoff: 5
    max_backoff: 60
  
  escalation:
    enabled: true
    notify_on: [resource_error, max_retries_exceeded]
    notification_channel: "slack"  # slack | email | log
```

---
#### 3.3 干预原则
1. **沉默为主**：没问题不说话，减少噪音
2. **一句话**：像用户一样直接说，禁止长篇解释
3. **`_keyinfo` 只用于提前预注入**：在工作 agent 到达该步之前塞细节
4. **已经犯错的一律用 `_intervene`** 纠正

---

### 第五步：完成验证

#### 4.1 检查最终结果
```python
def verify_completion(task_id, constraints):
    """
    验证任务完成质量
    """
    output_file = f"~/.hermes/tasks/{task_id}/output.txt"
    result_file = f"~/.hermes/tasks/{task_id}/result.json"
    
    # 读取最终输出
    with open(output_file, 'r') as f:
        final_output = f.read()
    
    # 对照约束清单逐项检查
    checklist = []
    for constraint in constraints:
        is_satisfied = check_constraint(final_output, constraint)
        checklist.append({
            "constraint": constraint,
            "satisfied": is_satisfied,
            "evidence": extract_evidence(final_output, constraint)
        })
    
    # 生成质量报告
    quality_score = sum(1 for item in checklist if item["satisfied"]) / len(checklist)
    
    return {
        "quality_score": quality_score,
        "checklist": checklist,
        "recommendations": generate_recommendations(checklist)
    }
```

#### 4.2 反馈给用户
```python
def report_to_user(task_id, verification_result):
    """
    向用户报告任务完成情况
    """
    score = verification_result["quality_score"]
    
    if score >= 0.9:
        status = "✅ 高质量完成"
    elif score >= 0.7:
        status = "⚠️ 基本完成，部分约束未满足"
    else:
        status = "❌ 质量不达标，建议重新执行"
    
    return f"""
{status}

质量得分：{score*100:.1f}%

约束检查清单：
{format_checklist(verification_result["checklist"])}

建议：
{chr(10).join(f"- {r}" for r in verification_result["recommendations"])}
"""
```

## 高级特性

### 特性 1：智能预判
```python
def predict_next_step(current_step, constraints):
    """
    预测下一步可能遇到的问题，提前注入关键信息
    """
    if current_step == "数据收集" and "时间戳验证" in constraints:
        return "_keyinfo: 下一步需要验证数据时间戳，注意财联社返回的 publish_time 字段"
    
    if current_step == "生成报告" and "表格格式" in constraints:
        return "_keyinfo: 输出需要 Markdown 表格格式，提前准备好列标题"
    
    return None
```

### 特性 2：异常模式库
```python
ANOMALY_PATTERNS = {
    "死循环": {
        "pattern": r"重复执行同一操作超过 3 次",
        "intervention": "_intervene: 检测到可能的死循环，尝试其他方法"
    },
    "过度解释": {
        "pattern": r"连续 5 轮只输出分析不执行",
        "intervention": "_intervene: 别分析了，直接执行"
    },
    "依赖缺失": {
        "pattern": r"ModuleNotFoundError|ImportError",
        "intervention": "_intervene: 缺少依赖，先执行 pip install"
    },
    "权限不足": {
        "pattern": r"Permission denied|Access denied",
        "intervention": "_intervene: 权限不足，尝试 sudo 或更换目录"
    }
}
```

### 特性 3：自适应监控频率
```python
def adjust_poll_interval(current_step, risk_level):
    """
    根据步骤风险等级调整监控频率
    """
    if risk_level == "high":  # 高风险操作
        return 1  # 每秒检查
    elif risk_level == "medium":
        return 2  # 每 2 秒检查
    else:  # 低风险
        return 5  # 每 5 秒检查
    
    # 关键步骤前自动提高频率
    if current_step in ["数据验证", "发布上线", "文件写入"]:
        return 1
```

## 与 Hermes 集成方案

### ✅ 已完成集成（2026-04-30）

监察者模式已通过**非侵入式 Wrapper 模式**集成到 Hermes `delegate_task`。

**核心文件**：
- `~/.hermes/hermes-agent/tools/supervisor_integration.py` (17KB) - 集成模块
- `~/.hermes/config/supervisor_config.yaml` (2.6KB) - 配置示例
- `~/.hermes/scripts/test_supervisor_integration.py` (7.4KB) - 测试套件

**测试状态**: ✅ 5/5 通过

---

### 方式 1：显式调用（推荐）

```python
from tools.supervisor_integration import delegate_task_with_supervisor
from tools.delegate_tool import delegate_task as original_delegate_task

result = delegate_task_with_supervisor(
    original_delegate_task,
    goal="分析今日A股大盘走势",
    context="当前时间：2026-04-30 02:10 深夜",
    supervisor=True,  # 显式启用
    supervisor_config={
        "sop": "a-stock-data-acquisition-sop",
        "risk_level": "high",
        "poll_interval": 1.0
    }
)

# 结果包含监察者报告
result_data = json.loads(result)
print(f"质量得分: {result_data['supervisor']['quality_score']:.1%}")
```

### 方式 2：自动判断

```python
result = delegate_task_with_supervisor(
    original_delegate_task,
    goal="部署到生产环境",  # 自动检测为高风险
    context="版本 v2.0.0",
    # supervisor=None  # 默认，根据关键词自动判断
)
```

**自动判断关键词**：
- 高风险：`生产环境`、`部署`、`删除`、`A股`、`大盘`、`股票`、`爬取`、`分析`
- 系统会自动启用监察者并调整风险等级

### 方式 3：Monkey Patch（全局生效）

```python
# 在启动时执行一次
from tools.supervisor_integration import patch_delegate_task
patch_delegate_task()

# 之后所有 delegate_task 调用都会自动启用监察者
result = delegate_task(
    goal="分析今日A股大盘",
    context="..."
)
```

---

### 配置优先级

```
supervisor_config (调用时传入)
  > supervisor_rules (按模式匹配)
  > supervisor (全局配置)
  > DEFAULT_SUPERVISOR_CONFIG
```

**配置示例**（`~/.hermes/config.yaml`）：

```yaml
supervisor:
  enabled: auto        # true | false | auto
  poll_interval: 2.0   # 轮询间隔（秒）
  timeout: 3600        # 超时时间（秒）
  auto_intervene: true # 是否自动干预
  risk_level: medium   # low | medium | high
  log_interventions: true

supervisor_rules:
  - pattern: "A股|大盘|股票"
    config:
      enabled: true
      sop: a-stock-data-acquisition-sop
      risk_level: high
  
  - pattern: "生产环境|部署"
    config:
      enabled: true
      risk_level: high
      poll_interval: 1.0
```

---

### 集成架构

```
delegate_task (用户调用)
    ↓
delegate_task_with_supervisor (Wrapper)
    ↓
    ├─ 构建监察者配置（关键词匹配 + 配置合并）
    ├─ 创建 SupervisorWrapper（后台线程）
    ├─ 调用原始 delegate_task
    └─ 合并监察者结果
    ↓
返回带 supervisor 字段的结果
```

**非侵入式设计**：
- ✅ 无需修改 Hermes 核心代码
- ✅ 通过 Wrapper 模式包装
- ✅ 后台线程监控，不阻塞执行
- ✅ 配置驱动，灵活可扩展

---

### 方案 4：Shell Hook 自动触发（高级）

```python
# ~/.hermes/hooks/auto-supervisor.py
def pre_delegate_task_hook(goal, context, **kwargs):
    """在 delegate_task 前触发"""
    if should_enable_supervisor(goal, context):
        kwargs["supervisor"] = True
        kwargs["supervisor_config"] = {
            "sop": recommend_sop(goal),
            "risk_level": assess_risk(goal)
        }
    return kwargs
```

**注意**：此方案需要修改 Hermes 启动流程，推荐使用方式 1-3。

## 最佳实践

### 实践 1：SOP 驱动监察
```markdown
# 在 Skill 中添加监察约束
---
name: a-stock-market-analysis
constraints:
  - ⚠️ 必须先获取精确时间
  - ⚠️ 必须判断盘前/盘后状态
  - ❌ 禁止使用非 P0 级数据源
  - ✅ 必须三重校验时间戳
---
```

### 实践 2：分级监察策略
```python
SUPERVISOR_LEVELS = {
    "none": {  # 无监察
        "poll_interval": None,
        "auto_intervene": False
    },
    "light": {  # 轻度监察
        "poll_interval": 10,
        "auto_intervene": False,
        "check_points": ["完成"]
    },
    "normal": {  # 标准监察
        "poll_interval": 2,
        "auto_intervene": True,
        "check_points": ["启动", "数据收集", "分析", "输出"]
    },
    "strict": {  # 严格监察
        "poll_interval": 1,
        "auto_intervene": True,
        "check_points": "all",
        "pre_inject": True
    }
}
```

### 实践 3：监察日志记录
```python
def log_supervisor_action(task_id, action_type, details):
    """
    记录监察行为，用于后续优化
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "task_id": task_id,
        "action": action_type,
        "details": details
    }
    
    with open(f"~/.hermes/logs/supervisor_{date}.jsonl", 'a') as f:
        f.write(json.dumps(log_entry) + "\n")
```

## 故障排查

### 问题 1：监察过于频繁，影响性能
**解决方案**：
- 调高 `poll_interval` 到 5-10 秒
- 只在关键步骤检查
- 使用 `check_points` 限制检查点

### 问题 2：干预消息被忽略
**解决方案**：
- 确保 subagent 定期读取干预文件
- 使用 `_keyinfo` 立即生效而非 `_intervene`
- 检查文件路径是否正确

### 问题 3：约束提取不准确
**解决方案**：
- 在 Skill 中显式声明 `constraints` 字段
- 使用结构化格式（YAML/JSON）
- 添加示例和说明

## 参考资源

- GenericAgent 原始实现：https://github.com/lsdefine/GenericAgent
- 监察者 SOP 原文：`memory/supervisor_sop.md`
- Subagent 协议：`memory/subagent.md`

## 更新日志

- **2026-05-02 v1.2.0**: 新增边界条件处理 - 环境预检（第零步）、干预文件异常处理、Subagent 失败恢复机制（超时/崩溃/卡住/约束违规/资源错误）、自动重试流程
- **2026-04-30 v1.1.0**: 完成 Hermes 集成（非侵入式 Wrapper 模式），新增三种使用方式（显式调用、自动判断、Monkey Patch），测试状态 5/5 通过
- **2026-04-30 v1.0.0**: 初始版本，基于 GenericAgent 监察者模式移植

## 相关文件

- **核心实现**: `~/.hermes/scripts/supervisor.py` (20KB)
- **集成模块**: `~/.hermes/hermes-agent/tools/supervisor_integration.py` (17KB)
- **配置示例**: `~/.hermes/config/supervisor_config.yaml` (2.6KB)
- **测试套件**: `~/.hermes/scripts/test_supervisor_integration.py` (7.4KB)
- **使用指南**: `~/.hermes/docs/SUPERVISOR-INTEGRATION-GUIDE.md` (8.2KB)

---

## ⚠️ Known Gotchas

### 三大红线违反

- **违规下场干活**: 主 Agent 直接操作
  ```python
  # ❌ 错误: 主 Agent 执行任务
  terminal("npm install package")
  write_file("config.yaml", content)
  
  # ✅ 正确: 只监控，不干活
  # 主 Agent 只能:
  # 1. 读取环境: file_read, terminal(只读命令)
  # 2. 检查约束: 验证 SOP 遵循度
  # 3. 写干预文件: 纠偏指令
  ```

- **未获取情报就干预**: 盲目纠偏
  ```python
  # ❌ 错误: 不了解情况就干预
  write_intervention("stop", reason="感觉不对")
  
  # ✅ 正确: 先读取再判断
  log = file_read("~/.hermes/logs/agent.log")
  if "error" in log:
      write_intervention("pause", reason=f"发现错误: {error}")
  ```

- **过度干预**: 频繁打断 Subagent
  ```python
  # ❌ 错误: 每 5 秒干预一次
  while True:
      sleep(5)
      write_intervention("check")
  
  # ✅ 正确: 只在关键节点干预
  # 干预时机:
  # 1. SOP 检查点失败
  # 2. 约束违规
  # 3. 错误累积超过阈值
  ```

### 干预文件问题

- **干预文件格式错误**: Subagent 无法解析
  ```yaml
  # ❌ 错误: 格式不规范
  action: stop
  reason: 觉得不对
  
  # ✅ 正确: 规范格式
  timestamp: "2024-01-01 12:00:00"
  action: pause
  reason: "数据源切换未按 SOP"
  checkpoint: "step_3_data_fetch"
  correction: "使用财联社 P0 数据源"
  ```

- **干预文件路径错误**: Subagent 读不到
  ```python
  # ❌ 错误: 路径不正确
  path = "~/.hermes/intervention.txt"
  
  # ✅ 正确: 使用标准路径
  path = "~/.hermes/runs/{run_id}/intervention.yaml"
  # Subagent 会监听此路径
  ```

- **干预文件冲突**: 多个 Supervisor 同时写
  ```python
  # 使用文件锁避免冲突
  import fcntl
  with open(intervention_file, 'w') as f:
      fcntl.flock(f.fileno(), fcntl.LOCK_EX)
      yaml.dump(intervention, f)
      fcntl.flock(f.fileno(), fcntl.LOCK_UN)
  ```

### Subagent 失败恢复

- **超时未处理**: Subagent 卡住
  ```python
  # ❌ 错误: 无超时机制
  subagent.run()
  
  # ✅ 正确: 设置超时
  import signal
  
  def timeout_handler(signum, frame):
      write_intervention("terminate", reason="超时")
      raise TimeoutError("Subagent 超时")
  
  signal.signal(signal.SIGALRM, timeout_handler)
  signal.alarm(300)  # 5 分钟超时
  try:
      subagent.run()
  finally:
      signal.alarm(0)
  ```

- **崩溃无恢复**: Subagent 异常退出
  ```python
  # ✅ 正确: 异常捕获 + 恢复
  try:
      subagent.run()
  except Exception as e:
      log_error(e)
      
      # 恢复策略
      if recoverable(e):
          # 1. 从检查点恢复
          checkpoint = get_last_checkpoint()
          subagent.resume(checkpoint)
      else:
          # 2. 通知用户
          notify_user(f"任务失败: {e}")
  ```

- **资源泄漏**: 进程/文件未清理
  ```python
  # ✅ 正确: 资源清理
  import atexit
  import os
  
  def cleanup():
      if os.path.exists(temp_dir):
          shutil.rmtree(temp_dir)
      if subagent_process.is_alive():
          subagent_process.terminate()
  
  atexit.register(cleanup)
  ```

### 环境预检陷阱

- **依赖未检查**: 运行时才发现缺失
  ```python
  # ❌ 错误: 直接启动
  subagent.run()
  
  # ✅ 正确: 先检查环境
  def check_environment():
      checks = [
          ("python3", "Python 3.10+"),
          ("node", "Node.js 16+"),
          ("docker", "Docker"),
      ]
      for cmd, desc in checks:
          if not shutil.which(cmd):
              return False, f"缺少 {desc}"
      return True, "环境检查通过"
  
  ok, msg = check_environment()
  if not ok:
      raise EnvironmentError(msg)
  ```

- **权限不足**: Subagent 无法执行关键操作
  ```bash
  # 检查必要权限
  # 1. 文件读写权限
  test -w ~/.hermes/runs
  
  # 2. 网络权限
  curl -I https://api.openai.com
  
  # 3. 进程权限
  ps aux | grep agent
  ```

### SOP 遵循检查

- **SOP 过时**: 文档与实际不符
  ```python
  # 检查 SOP 版本
  sop_version = get_sop_version("stock_analysis")
  if sop_version < "2.0":
      print(f"警告: SOP 版本过旧 ({sop_version})")
  ```

- **检查点遗漏**: 跳过关键步骤
  ```python
  # ❌ 错误: 未检查关键步骤
  if step > 3:
      pass  # 假设前面都做对了
  
  # ✅ 正确: 逐一验证检查点
  checkpoints = [
      "step_1_time_anchor",
      "step_2_market_status",
      "step_3_data_fetch",
  ]
  for cp in checkpoints:
      if not verify_checkpoint(cp):
          write_intervention("pause", reason=f"{cp} 未完成")
  ```

- **约束违规**: Subagent 违反规则
  ```python
  # 常见约束违规:
  # 1. 使用了禁止的数据源
  # 2. 跳过了必需的验证步骤
  # 3. 输出格式不符合规范
  
  # 约束检查函数
  def check_constraints():
      violations = []
      if uses_banned_source():
          violations.append("使用禁止数据源")
      if skips_validation():
          violations.append("跳过验证步骤")
      return violations
  ```

### 性能问题

- **监控频率过高**: 消耗大量资源
  ```python
  # ❌ 错误: 高频轮询
  while True:
      check_subagent()  # 每次都读取日志
  
  # ✅ 正确: 合理轮询间隔
  POLL_INTERVAL = 5  # 5 秒
  while True:
      check_subagent()
      time.sleep(POLL_INTERVAL)
  ```

- **日志过大**: 占满磁盘
  ```python
  # 日志轮转
  import logging
  from logging.handlers import RotatingFileHandler
  
  handler = RotatingFileHandler(
      "supervisor.log",
      maxBytes=10*1024*1024,  # 10MB
      backupCount=5
  )
  ```

- **内存泄漏**: Subagent 占用内存不释放
  ```python
  # 监控内存使用
  import psutil
  
  def check_memory():
      process = psutil.Process(subagent_pid)
      mem = process.memory_info().rss / 1024 / 1024  # MB
      if mem > 1024:  # 1GB
          write_intervention("restart", reason="内存泄漏")
  ```

### 多 Subagent 协调

- **Subagent 间冲突**: 资源竞争
  ```python
  # 使用锁协调
  import threading
  
  resource_lock = threading.Lock()
  
  def coordinate_subagents():
      with resource_lock:
          # 同一时间只有一个 Subagent 操作
          subagent.run()
  ```

- **依赖顺序错误**: 后置任务先执行
  ```python
  # ✅ 正确: 明确依赖关系
  tasks = [
      {"id": "fetch", "deps": []},
      {"id": "process", "deps": ["fetch"]},
      {"id": "report", "deps": ["process"]},
  ]
  
  # 拓扑排序后执行
  for task in topological_sort(tasks):
      run_subagent(task)
  ```

### 与 Hook 系统冲突

- **重复注入时间**: unified_time_awareness 已处理
  ```yaml
  # hooks.yaml 优先级配置
  hooks:
    pre_llm_call:
      - name: unified_time_awareness
        priority: 10  # 最高优先级
      - name: supervisor_precheck
        priority: 20  # 次高优先级
  ```

- **Hook 覆盖**: 监察者模式被其他 Hook 禁用
  ```bash
  # 检查 Hook 状态
  hermes hooks list
  
  # 确保未被禁用
  hermes hooks enable supervisor_precheck
  ```
