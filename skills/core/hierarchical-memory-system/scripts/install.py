#!/usr/bin/env python3
"""
分层记忆系统 - 安装脚本
设置目录结构、配置 cron job、配置 hooks
"""

import os
import sys
from pathlib import Path
import yaml

HERMES_DIR = Path.home() / ".hermes"
CONFIG_FILE = HERMES_DIR / "config.yaml"
SKILL_DIR = HERMES_DIR / "skills" / "core" / "hierarchical-memory-system"


def make_executable(path: Path):
    """给文件加执行权限"""
    mode = path.stat().st_mode
    path.chmod(mode | 0o111)


def setup_directories():
    """创建目录结构"""
    print("📁 创建目录结构...")
    
    directories = [
        HERMES_DIR / "memory" / "short-term",
        HERMES_DIR / "memory" / "long-term",
    ]
    
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {d.relative_to(Path.home())}")


def setup_hooks():
    """配置 post_llm_call hook 自动提取事实"""
    print("\n🔗 配置 Hook...")
    
    fact_extractor_script = SKILL_DIR / "scripts" / "fact-extractor.py"
    make_executable(fact_extractor_script)
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    hooks = config.get("hooks", {})
    post_hooks = hooks.get("post_llm_call", [])
    
    # 检查是否已经配置
    hook_cmd = str(fact_extractor_script)
    if any(hook_cmd in str(h.get("command", "")) for h in post_hooks):
        print(f"  ⏭️  Fact Extractor Hook 已配置，跳过")
    else:
        post_hooks.append({
            "command": hook_cmd,
            "timeout": 10,
        })
        hooks["post_llm_call"] = post_hooks
        config["hooks"] = hooks
        print(f"  ✅ 已添加 Fact Extractor Hook")
    
    # 写回配置
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def setup_cron_job():
    """设置每日摘要 cron job（每天 23:55 运行）"""
    print("\n⏰ 设置每日摘要定时任务...")
    
    daily_summarizer = SKILL_DIR / "scripts" / "daily-summarizer.py"
    make_executable(daily_summarizer)
    
    cron_config = f"""name: 每日记忆摘要（L1 → L2）
command: /usr/bin/env python3 {daily_summarizer}
schedule: "55 23 * * *"
notify: false
"""
    
    cron_file = SKILL_DIR / "cron.yaml"
    cron_file.write_text(cron_config, encoding="utf-8")
    print(f"  ✅ Cron 配置已写入 {cron_file.relative_to(Path.home())}")
    print(f"  ⏰ 执行时间：每天 23:55")
    print(f"  ℹ️  提示：请在 Hermes 中手动加载这个 cron job，或复制命令到 cron")


def init_l3_files():
    """初始化 L3 长期记忆分类文件"""
    print("\n📚 初始化 L3 长期记忆分类...")
    
    l3_dir = HERMES_DIR / "memory" / "long-term"
    
    categories = {
        "user-preference.md": """# 用户偏好 User Preferences

用户明确表达的喜好、习惯、禁忌。

---

""",
        "environment-facts.md": """# 环境事实 Environment Facts

系统、工具、路径等客观事实。

---

""",
        "project-notes.md": """# 项目记录 Project Notes

项目相关的重要信息、决策记录。

---

""",
        "technical-knowledge.md": """# 技术知识 Technical Knowledge

学到的重要技术知识、架构、方法论。

---

""",
        "general.md": """# 通用记忆 General

其他需要长期记住的信息。

---

""",
    }
    
    for filename, content in categories.items():
        filepath = l3_dir / filename
        if not filepath.exists():
            filepath.write_text(content, encoding="utf-8")
            print(f"  ✅ {filename}")
        else:
            print(f"  ⏭️ {filename} 已存在")


def main():
    print("=" * 60)
    print("   🧠 分层记忆系统 Hierarchical Memory System")
    print("   安装程序")
    print("=" * 60)
    
    setup_directories()
    setup_hooks()
    setup_cron_job()
    init_l3_files()
    
    print("\n" + "=" * 60)
    print("   ✅ 安装完成！")
    print("=" * 60)
    print(f"""
📋 功能清单：

✅ L1 会话记忆
   - 本次对话完整保留
   - 由 Hermes 原生支持

✅ L2 短期记忆
   - 每日自动摘要（每天 23:55）
   - 保留 7 天后自动过期
   - 位置：~/.hermes/memory/short-term/YYYY-MM-DD.md

✅ L3 长期记忆
   - 自动提取用户偏好和重要事实
   - 触发词：记住、记得、下次、以后、偏好、喜欢、不要...
   - 分类存储：用户偏好 / 环境事实 / 项目记录 / 技术知识
   - 位置：~/.hermes/memory/long-term/*.md

⏳ L4 技能记忆
   - 待实现：重复操作自动提示提取为 Skill

🔧 手动命令：

  # 手动生成今日摘要
  python3 {SKILL_DIR / 'scripts' / 'daily-summarizer.py'}

  # 测试事实提取
  python3 {SKILL_DIR / 'scripts' / 'fact-extractor.py'} test

  # 查看今日 L2 记忆
  cat ~/.hermes/memory/short-term/$(date +%Y-%m-%d).md

  # 查看 L3 长期记忆
  ls ~/.hermes/memory/long-term/
""")


if __name__ == "__main__":
    main()
