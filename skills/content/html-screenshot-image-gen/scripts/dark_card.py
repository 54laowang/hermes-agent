#!/usr/bin/env python3
"""
深色极简信息图模板（Pillow 直接绘制）
适用于数据卡片、金句图、朋友圈传播
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap
from datetime import datetime


def create_dark_card(highlight, title, subtitle="", items=None, output_path="/tmp/dark-card.png"):
    """
    生成深色极简数据卡片
    
    Args:
        highlight: 高亮数据（大字号）
        title: 主标题
        subtitle: 副标题（可选）
        items: 补充信息列表（可选）
        output_path: 输出路径
    """
    # 图片尺寸
    WIDTH = 1080
    HEIGHT = 1920
    MARGIN = 80
    
    # 配色（深色极简）
    BG_COLOR = "#0d0d0d"
    ACCENT_COLOR = "#4ade80"  # 荧光绿
    TEXT_COLOR = "#ffffff"
    SUBTEXT_COLOR = "#888888"
    
    # 创建图片
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    try:
        highlight_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 180)
        title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 56)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)
        item_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 32)
        footer_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
    except:
        highlight_font = ImageFont.load_default()
        title_font = highlight_font
        subtitle_font = highlight_font
        item_font = highlight_font
        footer_font = highlight_font
    
    # 垂直居中起始位置
    y = HEIGHT // 2 - 300
    
    # 绘制高亮数据
    if highlight:
        draw.text((WIDTH // 2, y), highlight, fill=ACCENT_COLOR, font=highlight_font, anchor="mm")
        y += 150
    
    # 绘制标题
    draw.text((WIDTH // 2, y), title, fill=TEXT_COLOR, font=title_font, anchor="mm")
    y += 80
    
    # 绘制副标题
    if subtitle:
        draw.text((WIDTH // 2, y), subtitle, fill=SUBTEXT_COLOR, font=subtitle_font, anchor="mm")
        y += 80
    
    # 绘制补充信息
    if items:
        y += 60
        for item in items:
            draw.text((WIDTH // 2, y), item, fill="#cccccc", font=item_font, anchor="mm")
            y += 50
    
    # 绘制底部日期
    today = datetime.now().strftime("%Y-%m-%d")
    draw.text((WIDTH // 2, HEIGHT - MARGIN), today, fill="#555555", font=footer_font, anchor="mm")
    
    # 保存图片
    img.save(output_path, quality=95)
    return output_path


def main():
    """示例：生成数据卡片"""
    output = create_dark_card(
        highlight="10x",
        title="效率提升 10 倍，成本降为零",
        subtitle="告别生图 API，拥抱 HTML 截图方案",
        items=["零成本 · 像素级可控 · 中文完美"]
    )
    
    print(f"✓ 深色卡片生成成功: {output}")


if __name__ == "__main__":
    main()
