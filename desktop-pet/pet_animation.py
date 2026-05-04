"""
Pet Animation - 动画系统
支持 GIF 和 Sprite Sheet 两种格式
"""
import json
from pathlib import Path
from PIL import Image
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class AnimationLoader:
    """动画加载器"""
    
    def __init__(self, skin_dir):
        self.skin_dir = Path(skin_dir)
        self.config = None
    
    def load_config(self):
        """加载 skin.json 配置"""
        config_file = self.skin_dir / "skin.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"skin.json 不存在: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        return self.config
    
    def load_animation(self, state="idle"):
        """加载指定状态的动画帧"""
        if not self.config:
            self.load_config()
        
        if state not in self.config["animations"]:
            raise ValueError(f"动画状态不存在: {state}")
        
        anim_config = self.config["animations"][state]
        format_type = self.config.get("format", "gif")
        
        if format_type == "gif":
            frames = self._load_gif(anim_config)
        elif format_type == "sprite":
            frames = self._load_sprite(anim_config)
        else:
            raise ValueError(f"不支持的格式: {format_type}")
        
        # 转换为 QPixmap
        return [self._pil_to_qpixmap(frame) for frame in frames]
    
    def _load_gif(self, anim_config):
        """加载 GIF 动画"""
        file_path = self.skin_dir / anim_config["file"]
        
        if not file_path.exists():
            raise FileNotFoundError(f"GIF 文件不存在: {file_path}")
        
        gif = Image.open(file_path)
        frames = []
        
        try:
            while True:
                # 转换为 RGBA
                frame = gif.copy().convert('RGBA')
                frames.append(frame)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        
        return frames
    
    def _load_sprite(self, anim_config):
        """加载 Sprite Sheet"""
        file_path = self.skin_dir / anim_config["file"]
        sprite_config = anim_config["sprite"]
        
        if not file_path.exists():
            raise FileNotFoundError(f"Sprite 文件不存在: {file_path}")
        
        img = Image.open(file_path)
        frames = []
        
        frame_width = sprite_config["frameWidth"]
        frame_height = sprite_config["frameHeight"]
        frame_count = sprite_config["frameCount"]
        columns = sprite_config["columns"]
        start_frame = sprite_config.get("startFrame", 0)
        
        for i in range(frame_count):
            frame_idx = start_frame + i
            row = frame_idx // columns
            col = frame_idx % columns
            
            x = col * frame_width
            y = row * frame_height
            
            frame = img.crop((x, y, x + frame_width, y + frame_height))
            frames.append(frame.convert('RGBA'))
        
        return frames
    
    @staticmethod
    def _pil_to_qpixmap(pil_image):
        """PIL Image 转 QPixmap"""
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(
            data,
            pil_image.width,
            pil_image.height,
            pil_image.width * 4,
            QImage.Format.Format_RGBA8888
        )
        return QPixmap.fromImage(qimage)
