#!/usr/bin/env python3
"""
HTML 截图生图示例脚本
演示如何使用 HTML 模板 + 浏览器截图生成图片
"""

import os
from pathlib import Path

# 示例数据
examples = {
    "warm": {
        "title": "HTML 截图生图三步法",
        "subtitle": "零成本，无限次，像素级可控",
        "items": [
            {"title": "写 HTML 模板", "desc": "固化颜色、布局、字体，只留内容占位符"},
            {"title": "填入动态内容", "desc": "Hermes 自动注入文字、数据、列表"},
            {"title": "浏览器截图", "desc": "browser_navigate + browser_vision，5 秒完成"}
        ],
        "date": "2026-05-03",
        "source": "Hermes Skill"
    },
    "dark": {
        "highlight": "10x",
        "title": "效率提升 10 倍，成本降为零",
        "subtitle": "告别生图 API，拥抱 HTML 截图方案",
        "items": [
            {"highlight": "零成本", "text": "无需调用任何付费 API"},
            {"highlight": "像素级", "text": "版式完全可控"},
            {"highlight": "中文完美", "text": "渲染无错字乱码"}
        ],
        "date": "2026-05-03"
    },
    "cover": {
        "tag": "HERMES SKILL",
        "title": "免费生图方案",
        "subtitle": "HTML 模板 + 浏览器截图"
    },
    "compare": {
        "title": "生图方案对比",
        "subtitle": "选择适合你的方案",
        "column_a_title": "生图 API",
        "column_a_items": [
            "按次收费，成本累积快",
            "版式不可控",
            "中文渲染差",
            "风格难统一"
        ],
        "column_b_title": "HTML 截图",
        "column_b_items": [
            "零成本，无限次",
            "像素级可控",
            "中文完美",
            "模板保证统一"
        ],
        "date": "2026-05-03"
    }
}

def generate_html(template_name, data):
    """根据模板和数据生成 HTML"""
    template_dir = Path(__file__).parent / "references"
    template_path = template_dir / f"template-{template_name}.html"
    
    if not template_path.exists():
        raise FileNotFoundError(f"模板不存在: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 简单的模板替换（实际使用可以用 Jinja2 或其他模板引擎）
    html = template
    for key, value in data.items():
        if isinstance(value, str):
            html = html.replace(f"{{{{{key}}}}}", value)
    
    return html

def main():
    """主函数"""
    print("HTML 截图生图示例")
    print("=" * 50)
    
    # 选择模板
    print("\n可用模板：")
    for name in examples.keys():
        print(f"  - {name}")
    
    template_name = input("\n选择模板 (warm/dark/cover/compare): ").strip()
    
    if template_name not in examples:
        print(f"错误：模板 '{template_name}' 不存在")
        return
    
    # 生成 HTML
    data = examples[template_name]
    html = generate_html(template_name, data)
    
    # 保存到临时文件
    output_dir = Path("/tmp/img-output")
    output_dir.mkdir(exist_ok=True)
    
    html_path = output_dir / "card.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✓ HTML 已生成: {html_path}")
    print(f"\n下一步操作：")
    print(f"  1. 在 Hermes 中使用 browser_navigate 打开 HTML")
    print(f"     browser_navigate('file://{html_path}')")
    print(f"  2. 使用 browser_vision 截图")
    print(f"     browser_vision('截图整个页面')")

if __name__ == "__main__":
    main()
