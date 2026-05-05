#!/usr/bin/env python3
"""
Pillow 直接绘制信息图（无需浏览器）
适用于浏览器工具不可用的场景
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap
import sys

def create_infographic(title, subtitle, items, output_path="/tmp/output.png"):
    """
    生成米色暖系信息图
    
    Args:
        title: 主标题
        subtitle: 副标题
        items: 列表项 [{"title": "标题", "desc": "描述"}]
        output_path: 输出路径
    """
    # 图片尺寸
    WIDTH = 1080
    HEIGHT = 1920
    MARGIN = 60
    
    # 配色（米色暖系）
    BG_COLOR = "#f5f0e8"
    CARD_BG = "#ffffff"
    ACCENT_COLOR = "#8b6f47"
    TEXT_COLOR = "#2d2d2d"
    SUBTEXT_COLOR = "#666666"
    
    # 创建图片
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 56)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 28)
        number_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        item_title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 32)
        item_desc_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
        footer_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 20)
    except:
        # 降级到默认字体
        title_font = ImageFont.load_default()
        subtitle_font = title_font
        number_font = title_font
        item_title_font = title_font
        item_desc_font = title_font
        footer_font = title_font
    
    # 绘制标题
    y = MARGIN
    draw.text((MARGIN, y), title, fill=TEXT_COLOR, font=title_font)
    y += 70
    
    if subtitle:
        draw.text((MARGIN, y), subtitle, fill=SUBTEXT_COLOR, font=subtitle_font)
        y += 80
    
    # 绘制卡片
    card_width = WIDTH - 2 * MARGIN
    card_height = 200
    card_spacing = 20
    
    for i, item in enumerate(items, 1):
        # 卡片背景
        x1, y1 = MARGIN, y
        x2, y2 = MARGIN + card_width, y + card_height
        
        # 绘制矩形背景
        draw.rectangle([x1, y1, x2, y2], fill=CARD_BG)
        
        # 绘制圆形数字
        circle_x = x1 + 50
        circle_y = y1 + 50
        draw.ellipse([circle_x-36, circle_y-36, circle_x+36, circle_y+36], fill=ACCENT_COLOR)
        draw.text((circle_x, circle_y), str(i), fill="white", font=number_font, anchor="mm")
        
        # 绘制标题和描述
        text_x = x1 + 120
        draw.text((text_x, y1 + 30), item["title"], fill=TEXT_COLOR, font=item_title_font)
        
        # 自动换行描述文字
        desc_lines = textwrap.wrap(item["desc"], width=35)
        desc_y = y1 + 80
        for line in desc_lines:
            draw.text((text_x, desc_y), line, fill=SUBTEXT_COLOR, font=item_desc_font)
            desc_y += 35
        
        y = y2 + card_spacing
    
    # 绘制底部
    from datetime import datetime
    y = HEIGHT - MARGIN - 60
    draw.line([(MARGIN, y), (WIDTH - MARGIN, y)], fill="#dddddd", width=2)
    y += 20
    
    today = datetime.now().strftime("%Y-%m-%d")
    draw.text((MARGIN, y), today, fill="#999999", font=footer_font)
    
    # 保存图片
    img.save(output_path, quality=95)
    return output_path


def main():
    """示例用法"""
    items = [
        {"title": "Software 3.0 已来", "desc": "程序形态变了：从代码文件到上下文"},
        {"title": "Vibe Coding 拉高地板", "desc": "解决'能不能跑'，门槛降到零"},
        {"title": "Agentic Engineering", "desc": "解决'对不对'，人负责质量"},
    ]
    
    output = create_infographic(
        title="从 Vibe Coding 到 Agentic Engineering",
        subtitle="Karpathy：工程师从执行者变成管理者",
        items=items
    )
    
    print(f"✓ 信息图生成成功: {output}")


if __name__ == "__main__":
    main()
