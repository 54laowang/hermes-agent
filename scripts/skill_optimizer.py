#!/usr/bin/env python3
"""
Skills 批量优化脚本
基于 14 个 Claude Skill 编写模式
"""
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

HERMES_DIR = Path.home() / ".hermes"
skills_dir = HERMES_DIR / "skills"

# 排除条款模板（按类别）
EXCLUSION_TEMPLATES = {
    "github": """
Do NOT use for:
- Committing without reviewing changes
- Force pushing to protected branches
- Deleting remote branches without confirmation
- Modifying .git directory directly""",

    "finance": """
Do NOT use for:
- Real trading without user confirmation
- Accessing sensitive financial data without authorization
- Executing trades in production environment""",

    "creative": """
Do NOT use for:
- Generating academic papers or research
- Technical documentation (use technical-writer skill)
- Legal or medical content""",

    "web": """
Do NOT use for:
- Intercepting traffic without explicit authorization
- Production network debugging
- Modifying system certificates without backup""",

    "research": """
Do NOT use for:
- Making investment decisions
- Medical or legal advice
- Official scientific publications without peer review""",

    "default": """
Do NOT use for tasks outside the scope defined above."""
}

# 触发词模板（按类别）
TRIGGER_TEMPLATES = {
    "github": ["git", "github", "repository", "commit", "push", "pull", "branch", "PR", "issue"],
    "finance": ["stock", "trading", "market", "ETF", "grid", "网格交易", "股票"],
    "creative": ["humanize", "natural", "AI text", "remove AI", "make natural", "人性化"],
    "web": ["mitmproxy", "intercept", "traffic", "credentials", "HTTPS", "proxy"],
    "research": ["evaluate", "project", "open source", "repo analysis", "project assessment"],
    "turix": ["macOS", "automate", "mac automation", "apple script"],
}

def optimize_skill(skill_path: Path) -> Dict:
    """优化单个 Skill"""
    result = {
        'path': str(skill_path.relative_to(HERMES_DIR)),
        'name': '',
        'actions': [],
        'success': False
    }
    
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            result['actions'].append("跳过：无 YAML frontmatter")
            return result
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            result['actions'].append("跳过：YAML 格式错误")
            return result
        
        frontmatter = yaml.safe_load(parts[1])
        body = parts[2]
        
        result['name'] = frontmatter.get('name', skill_path.parent.name)
        
        # 1. 检查并添加排除条款
        if "NOT use" not in body and "DO NOT" not in body:
            category = frontmatter.get('category', 'default')
            exclusion = EXCLUSION_TEMPLATES.get(category, EXCLUSION_TEMPLATES['default'])
            body += f"\n\n## When NOT to Use\n{exclusion}\n"
            result['actions'].append("✅ 添加排除条款")
        
        # 2. 检查并添加触发词
        if not frontmatter.get('triggers') and not frontmatter.get('keywords'):
            category = frontmatter.get('category', 'default')
            triggers = TRIGGER_TEMPLATES.get(category, [])
            if triggers:
                frontmatter['triggers'] = triggers[:5]  # 最多 5 个
                result['actions'].append("✅ 添加触发词")
        
        # 3. 优化 description（如果过短）
        desc = str(frontmatter.get('description', ''))
        if len(desc) < 50:
            skill_name = frontmatter.get('name', '')
            category = frontmatter.get('category', '')
            
            # 生成基础 description
            new_desc = f"{skill_name} - "
            if category:
                triggers = TRIGGER_TEMPLATES.get(category, [])
                if triggers:
                    new_desc += f"Use when: {', '.join(triggers[:3])}. "
            
            if new_desc != f"{skill_name} - ":
                frontmatter['description'] = new_desc.strip()
                result['actions'].append("✅ 优化 description")
        
        # 写回文件
        new_content = '---\n' + yaml.dump(frontmatter, allow_unicode=True, sort_keys=False) + '---' + body
        
        with open(skill_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        result['success'] = True
        
    except Exception as e:
        result['actions'].append(f"❌ 错误: {str(e)}")
    
    return result

def main():
    print("=" * 80)
    print("【Skills 批量优化工具】")
    print("=" * 80)
    
    # 扫描所有活跃 Skills
    skill_files = []
    for skill_file in skills_dir.rglob("SKILL.md"):
        # 跳过归档目录
        if '.archive' in str(skill_file) or '_archived' in str(skill_file):
            continue
        skill_files.append(skill_file)
    
    print(f"\n找到 {len(skill_files)} 个活跃 Skills")
    print("\n开始优化...\n")
    
    # 优化
    results = []
    for i, skill_file in enumerate(skill_files[:10], 1):  # 先优化前 10 个
        result = optimize_skill(skill_file)
        results.append(result)
        
        print(f"{i}. {result['name']}")
        for action in result['actions']:
            print(f"   {action}")
    
    # 统计
    success_count = sum(1 for r in results if r['success'])
    print("\n" + "=" * 80)
    print("【优化结果】")
    print("=" * 80)
    print(f"\n成功优化: {success_count}/{len(results)} 个")
    
    # 显示所有 actions
    all_actions = []
    for r in results:
        all_actions.extend(r['actions'])
    
    action_counts = {}
    for action in all_actions:
        action_type = action.split()[0]  # ✅ 或 ❌
        action_counts[action_type] = action_counts.get(action_type, 0) + 1
    
    print("\n操作统计:")
    for action_type, count in action_counts.items():
        print(f"  {action_type} {count} 次")

if __name__ == "__main__":
    main()
