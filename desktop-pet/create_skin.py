#!/usr/bin/env python3
"""
创建默认皮肤动画
用 PIL 生成简单的猫咪动画
"""
from PIL import Image, ImageDraw
from pathlib import Path

def create_cat_frame(size=80, frame_idx=0, state="idle"):
    """创建猫咪单帧"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 身体颜色
    body_color = (255, 180, 100, 255)
    eye_color = (50, 50, 50, 255)
    
    # 根据状态调整动画
    if state == "idle":
        # 待机：轻微上下浮动
        offset_y = int(3 * (frame_idx % 2))
        
        # 身体
        draw.ellipse([15, 25 + offset_y, 65, 65 + offset_y], fill=body_color)
        
        # 头部
        draw.ellipse([20, 10 + offset_y, 60, 50 + offset_y], fill=body_color)
        
        # 耳朵
        draw.polygon([(25, 15 + offset_y), (20, 5 + offset_y), (35, 20 + offset_y)], fill=body_color)
        draw.polygon([(55, 15 + offset_y), (60, 5 + offset_y), (45, 20 + offset_y)], fill=body_color)
        
        # 眼睛
        eye_offset = 1 if frame_idx % 4 == 0 else 0  # 眨眼
        draw.ellipse([30, 25 + offset_y, 35, 30 + offset_y + eye_offset], fill=eye_color)
        draw.ellipse([45, 25 + offset_y, 50, 30 + offset_y + eye_offset], fill=eye_color)
        
        # 鼻子
        draw.polygon([(40, 35 + offset_y), (37, 38 + offset_y), (43, 38 + offset_y)], fill=(255, 150, 150))
        
        # 尾巴
        draw.arc([55, 40 + offset_y, 75, 60 + offset_y], 0, 180, fill=body_color, width=3)
    
    elif state == "walk":
        # 行走：左右摇摆
        offset_x = int(3 * ((frame_idx % 2) - 0.5))
        
        # 身体
        draw.ellipse([15 + offset_x, 25, 65 + offset_x, 65], fill=body_color)
        
        # 头部
        draw.ellipse([20 + offset_x, 10, 60 + offset_x, 50], fill=body_color)
        
        # 耳朵
        draw.polygon([(25 + offset_x, 15), (20 + offset_x, 5), (35 + offset_x, 20)], fill=body_color)
        draw.polygon([(55 + offset_x, 15), (60 + offset_x, 5), (45 + offset_x, 20)], fill=body_color)
        
        # 眼睛
        draw.ellipse([30 + offset_x, 25, 35 + offset_x, 30], fill=eye_color)
        draw.ellipse([45 + offset_x, 25, 50 + offset_x, 30], fill=eye_color)
        
        # 鼻子
        draw.polygon([(40 + offset_x, 35), (37 + offset_x, 38), (43 + offset_x, 38)], fill=(255, 150, 150))
        
        # 腿（走路动画）
        if frame_idx % 2 == 0:
            draw.ellipse([20, 60, 30, 70], fill=body_color)
            draw.ellipse([50, 55, 60, 65], fill=body_color)
        else:
            draw.ellipse([20, 55, 30, 65], fill=body_color)
            draw.ellipse([50, 60, 60, 70], fill=body_color)
    
    return img


def create_gif(state="idle", frame_count=8, duration=125):
    """创建 GIF 动画"""
    frames = []
    
    for i in range(frame_count):
        frame = create_cat_frame(frame_idx=i, state=state)
        frames.append(frame)
    
    # 保存为 GIF
    output_dir = Path(__file__).parent / "skins" / "default"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{state}.gif"
    
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        disposal=2
    )
    
    print(f"✅ 创建 {state}.gif: {output_path}")
    return output_path


if __name__ == '__main__':
    print("🐱 创建默认猫咪皮肤...")
    
    # 创建 idle 和 walk 动画
    create_gif("idle", frame_count=8, duration=125)  # 8帧，8fps
    create_gif("walk", frame_count=10, duration=100)  # 10帧，10fps
    
    print("\n✨ 默认皮肤创建完成！")
