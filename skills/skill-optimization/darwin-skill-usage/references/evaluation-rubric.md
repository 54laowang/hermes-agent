# 8维度评估详细标准

> 用于自动化评估Skill质量的详细标准

---

## 评估函数实现

```python
from hermes_tools import read_file

def evaluate_skill(skill_path):
    """评估skill的8个维度"""
    result = read_file(f"{skill_path}/SKILL.md")
    content = result.get("content", "")
    
    scores = {}
    
    # 1. Frontmatter质量（8分）
    has_frontmatter = content.startswith("---")
    has_name = "name:" in content[:500]
    has_desc = "description:" in content[:500]
    desc_length = len(content.split("description:")[1].split("\n")[0]) if has_desc else 0
    
    if has_frontmatter and has_name and has_desc:
        if desc_length > 50 and desc_length <= 1024:
            scores["frontmatter"] = 8
        else:
            scores["frontmatter"] = 6
    else:
        scores["frontmatter"] = 4
    
    # 2. 工作流清晰度（15分）
    has_workflow = any(kw in content.lower() for kw in ["phase", "step", "流程", "步骤", "阶段"])
    has_numbered = any(f"{i}." in content or f"{i})" in content or f"步骤{i}" in content for i in range(1, 10))
    has_io = any(kw in content.lower() for kw in ["输入", "输出", "input", "output"])
    
    if has_workflow and has_numbered and has_io:
        scores["workflow"] = 15
    elif has_workflow and has_numbered:
        scores["workflow"] = 12
    else:
        scores["workflow"] = 8
    
    # 3. 边界条件覆盖（10分）
    has_boundary = any(kw in content.lower() for kw in ["如果", "when", "边界", "异常", "error", "fallback"])
    has_exception = "异常处理" in content or "exception" in content.lower()
    
    if has_exception:
        scores["boundary"] = 10
    elif has_boundary:
        scores["boundary"] = 7
    else:
        scores["boundary"] = 5
    
    # 4. 检查点设计（7分）
    has_checkpoint = any(kw in content.lower() for kw in ["确认", "confirm", "检查点", "checkpoint"])
    has_explicit_checkpoint = "【检查点】" in content
    
    if has_explicit_checkpoint:
        scores["checkpoint"] = 7
    elif has_checkpoint:
        scores["checkpoint"] = 5
    else:
        scores["checkpoint"] = 3
    
    # 5. 指令具体性（15分）
    has_specific = any(kw in content.lower() for kw in ["具体", "example", "示例", "参数", "parameter"])
    has_code = "```" in content
    has_template = "template" in content.lower()
    
    if has_code and has_template:
        scores["specificity"] = 15
    elif has_code or has_specific:
        scores["specificity"] = 12
    else:
        scores["specificity"] = 8
    
    # 6. 资源整合度（5分）
    has_refs = any(kw in content.lower() for kw in ["references", "scripts", "templates", "参考"])
    
    if has_refs:
        scores["resources"] = 5
    else:
        scores["resources"] = 2
    
    # 7. 整体架构（15分）
    has_structure = content.count("##") >= 3
    has_subsections = content.count("###") >= 2
    
    if has_structure and has_subsections:
        scores["architecture"] = 15
    elif has_structure:
        scores["architecture"] = 12
    else:
        scores["architecture"] = 8
    
    # 8. 实测表现（25分）
    # 需要运行test-prompts.json，这里给中等分
    scores["effectiveness"] = 15
    
    total = sum(scores.values())
    
    return {
        "scores": scores,
        "total": total,
        "dimensions": {
            "frontmatter": scores["frontmatter"] / 8,
            "workflow": scores["workflow"] / 15,
            "boundary": scores["boundary"] / 10,
            "checkpoint": scores["checkpoint"] / 7,
            "specificity": scores["specificity"] / 15,
            "resources": scores["resources"] / 5,
            "architecture": scores["architecture"] / 15,
            "effectiveness": scores["effectiveness"] / 25
        }
    }
```

---

## 详细评分标准

### 维度1: Frontmatter质量（8分）

**满分条件**（8分）：
- ✅ 以`---`开头和结尾
- ✅ 包含规范的`name:`字段
- ✅ `description:`字段长度50-1024字符
- ✅ description包含"做什么"+"何时用"+触发词

**部分得分**（6分）：
- ✅ 有frontmatter、name、description
- ⚠️ description过短（<50字符）或过长（>1024字符）

**低分**（4分）：
- ⚠️ 缺少name或description
- ⚠️ frontmatter格式不规范

---

### 维度2: 工作流清晰度（15分）

**满分条件**（15分）：
- ✅ 有明确的Phase/Step/阶段划分
- ✅ 步骤有编号（1. 2. 3. 或 步骤1 步骤2）
- ✅ 每个步骤有明确的输入/输出说明
- ✅ 步骤之间有逻辑顺序

**部分得分**（12分）：
- ✅ 有工作流和编号
- ⚠️ 缺少输入/输出说明

**低分**（8分）：
- ⚠️ 工作流模糊或缺失编号

---

### 维度3: 边界条件覆盖（10分）

**满分条件**（10分）：
- ✅ 有明确的"异常处理"章节
- ✅ 覆盖常见错误场景（文件不存在、网络失败、权限不足等）
- ✅ 每个异常都有明确的处理动作

**部分得分**（7分）：
- ✅ 有边界条件说明（使用"如果"、"when"等）
- ⚠️ 缺少系统化的异常处理章节

**低分**（5分）：
- ⚠️ 偶尔提到边界条件
- ⚠️ 没有明确的异常处理策略

---

### 维度4: 检查点设计（7分）

**满分条件**（7分）：
- ✅ 使用**【检查点】**明确标记
- ✅ 在关键决策前有用户确认环节
- ✅ 说明确认后继续、否认后回滚的逻辑

**部分得分**（5分）：
- ✅ 有"确认"、"检查点"等关键词
- ⚠️ 没有明确的标记格式

**低分**（3分）：
- ⚠️ 缺少用户确认机制

---

### 维度5: 指令具体性（15分）

**满分条件**（15分）：
- ✅ 包含可执行的代码块（```）
- ✅ 引用模板文件（template）
- ✅ 参数有具体的格式说明
- ✅ 有示例输入/输出

**部分得分**（12分）：
- ✅ 有代码块或具体说明
- ⚠️ 缺少模板引用

**低分**（8分）：
- ⚠️ 指令模糊，缺少具体参数

---

### 维度6: 资源整合度（5分）

**满分条件**（5分）：
- ✅ 引用references/目录下的文档
- ✅ 引用scripts/目录下的脚本
- ✅ 引用templates/目录下的模板

**低分**（2分）：
- ⚠️ 缺少资源文件引用

---

### 维度7: 整体架构（15分）

**满分条件**（15分）：
- ✅ 至少3个二级标题（##）
- ✅ 至少2个三级标题（###）
- ✅ 结构层次清晰（概述→流程→细节→参考）

**部分得分**（12分）：
- ✅ 有二级标题结构
- ⚠️ 缺少三级细分

**低分**（8分）：
- ⚠️ 结构扁平，缺少层次

---

### 维度8: 实测表现（25分）

**评估方法**：
1. 读取`test-prompts.json`
2. 运行每个测试prompt
3. 对比输出质量与预期

**评分标准**：

| 分数 | 表现 |
|------|------|
| 25分 | 所有测试prompt输出完全符合预期 |
| 20分 | 80%以上测试通过 |
| 15分 | 中等表现，无严重问题 |
| 10分 | 有明显缺陷但不阻塞使用 |
| 5分 | 基本不可用 |

**简化评分**（无法实测时）：
- 给15分（中等分）
- 标注为"dry_run"

---

## 批量评估脚本

```python
import os
from pathlib import Path

def batch_evaluate(skills_dir="~/.hermes/skills"):
    """批量评估所有skill"""
    skills_path = Path(skills_dir).expanduser()
    results = {}
    
    for skill_dir in skills_path.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            skill_name = skill_dir.name
            try:
                eval_result = evaluate_skill(str(skill_dir))
                results[skill_name] = eval_result
            except Exception as e:
                results[skill_name] = {"error": str(e)}
    
    # 排序输出
    sorted_results = sorted(
        results.items(),
        key=lambda x: x[1].get("total", 0),
        reverse=True
    )
    
    print("=" * 80)
    print(f"{'Skill':40} | {'Score':>6} | {'结构短板':<15} | {'效果短板':<15}")
    print("=" * 80)
    
    for skill, result in sorted_results:
        if "error" not in result:
            score = result["total"]
            dims = result["dimensions"]
            
            # 找短板
            weak_dims = [k for k, v in dims.items() if v < 0.7]
            struct_weak = [d for d in weak_dims if d in ["frontmatter", "workflow", "boundary", "checkpoint", "specificity", "resources", "architecture"]]
            effect_weak = [d for d in weak_dims if d in ["effectiveness"]]
            
            print(f"{skill:40} | {score:6} | {', '.join(struct_weak) or '-':<15} | {', '.join(effect_weak) or '-':<15}")
    
    # 计算平均分
    valid_scores = [r["total"] for r in results.values() if "error" not in r]
    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    print("=" * 80)
    print(f"平均分: {avg_score:.1f}/100")
    
    return results
```

---

## 使用建议

1. **基线评估**：先用`batch_evaluate()`建立起点分数
2. **针对性改进**：优先优化分数最低的维度
3. **持续验证**：每次改进后重新评估，确认提升
4. **记录历史**：在results.tsv中记录每次优化结果

---

## 注意事项

- 评估函数对关键词敏感，确保SKILL.md使用标准术语
- 维度8（实测表现）需要人工验证或子agent执行
- 总分保留1位小数，改进需严格>旧分
