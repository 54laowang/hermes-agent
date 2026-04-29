#!/usr/bin/env python3
"""
自动更新 README_CN.md 的更新日志部分
使用方法: python3 update_readme.py "更新内容描述"
"""

import sys
from datetime import datetime
from pathlib import Path

def update_readme(description: str):
    """更新 README_CN.md 的更新日志"""
    readme_path = Path(__file__).parent.parent / "README_CN.md"
    
    if not readme_path.exists():
        print(f"❌ README_CN.md 不存在: {readme_path}")
        return False
    
    # 读取现有内容
    content = readme_path.read_text(encoding='utf-8')
    
    # 生成新的更新条目
    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M")
    
    # 查找更新日志插入位置
    log_marker = "## 📋 更新日志"
    if log_marker not in content:
        print(f"❌ 未找到更新日志标记: {log_marker}")
        return False
    
    # 构建新条目
    new_entry = f"""
### {today}

{description}

"""
    
    # 插入新条目
    lines = content.split('\n')
    insert_index = None
    
    for i, line in enumerate(lines):
        if line.strip() == log_marker:
            # 找到下一个 ### 的位置
            for j in range(i+1, len(lines)):
                if lines[j].strip().startswith('### 2'):
                    insert_index = j
                    break
            break
    
    if insert_index is None:
        print("❌ 无法找到插入位置")
        return False
    
    # 插入新内容
    lines.insert(insert_index, new_entry.strip())
    
    # 更新最后更新时间
    for i, line in enumerate(lines):
        if line.startswith('**最后更新**:'):
            lines[i] = f'**最后更新**: {today} {time_now}'
        elif line.startswith('**版本**:'):
            # 保持版本号不变，或根据需要更新
            pass
    
    # 写回文件
    new_content = '\n'.join(lines)
    readme_path.write_text(new_content, encoding='utf-8')
    
    print(f"✅ README 已更新: {today}")
    print(f"📝 更新内容: {description}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 update_readme.py '更新内容描述'")
        print("示例: python3 update_readme.py '修复了 XX 问题，优化了 YY 性能'")
        sys.exit(1)
    
    description = ' '.join(sys.argv[1:])
    success = update_readme(description)
    sys.exit(0 if success else 1)
