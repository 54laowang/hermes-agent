"""
Pet Bubble - 消息气泡系统
自动换行、多语言支持、透明背景
"""
import re
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QFont, QFontDatabase


class BubbleManager:
    """气泡管理器"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.bubble_window = None
        self.bubble_label = None
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self._hide_bubble)
    
    def show_bubble(self, text, duration=3000):
        """显示气泡消息"""
        # 关闭之前的气泡
        self._hide_bubble()
        
        # 创建气泡图像
        bubble_pixmap = self._create_bubble(text)
        
        # 创建气泡窗口
        self.bubble_window = QWidget()
        self.bubble_window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.bubble_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.bubble_window.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        
        # 设置大小
        self.bubble_window.setFixedSize(bubble_pixmap.size())
        
        # 显示图像
        self.bubble_label = QLabel(self.bubble_window)
        self.bubble_label.setGeometry(0, 0, bubble_pixmap.width(), bubble_pixmap.height())
        self.bubble_label.setPixmap(bubble_pixmap)
        
        # 计算位置（宠物上方）
        self._position_bubble()
        
        # 显示
        self.bubble_window.show()
        
        # 定时隐藏
        if duration > 0:
            self.hide_timer.start(duration)
    
    def _create_bubble(self, text, max_width=250):
        """创建气泡图像"""
        # 文本处理
        text = self._normalize_text(text)
        
        # 字体
        font = self._load_font(14)
        
        # 计算文本尺寸
        from PyQt6.QtGui import QFontMetrics
        fm = QFontMetrics(font)
        
        # 自动换行
        lines = []
        words = text.split('\n')
        
        for word in words:
            if not word:
                lines.append('')
                continue
            
            current = ''
            for ch in word:
                test = current + ch
                if fm.horizontalAdvance(test) > max_width - 40:
                    if current:
                        lines.append(current)
                    current = ch
                else:
                    current = test
            
            if current:
                lines.append(current)
        
        # 气泡尺寸
        text_width = max(fm.horizontalAdvance(line) for line in lines) if lines else 100
        text_height = len(lines) * fm.height()
        
        padding = 20
        width = text_width + padding * 2
        height = text_height + padding * 2
        
        # 创建图像
        from PyQt6.QtGui import QImage
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制圆角矩形背景
        painter.setBrush(QColor(255, 255, 255, 230))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRoundedRect(0, 0, width - 1, height - 1, 15, 15)
        
        # 绘制文本
        painter.setPen(QColor(50, 50, 50))
        painter.setFont(font)
        
        y = padding + fm.ascent()
        for line in lines:
            painter.drawText(padding, y, line)
            y += fm.height()
        
        painter.end()
        
        return QPixmap.fromImage(image)
    
    def _position_bubble(self):
        """定位气泡（宠物上方）"""
        parent_pos = self.parent.pos()
        parent_size = self.parent.size()
        bubble_size = self.bubble_window.size()
        
        # 气泡在宠物上方居中
        x = parent_pos.x() + (parent_size.width() - bubble_size.width()) // 2
        y = parent_pos.y() - bubble_size.height() - 10
        
        # 确保不超出屏幕
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        
        if x < 0:
            x = 0
        elif x + bubble_size.width() > screen.width():
            x = screen.width() - bubble_size.width()
        
        if y < 0:
            y = parent_pos.y() + parent_size.height() + 10
        
        self.bubble_window.move(x, y)
    
    def _hide_bubble(self):
        """隐藏气泡"""
        if self.bubble_window:
            self.bubble_window.close()
            self.bubble_window = None
            self.bubble_label = None
    
    def _normalize_text(self, text):
        """标准化文本"""
        text = (text or '').strip()
        # 移除特殊符号
        text = re.sub(r'^🔄\s*', '', text)
        return text
    
    def _load_font(self, size):
        """加载字体"""
        font_candidates = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            'C:/Windows/Fonts/msyh.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        ]
        
        for font_path in font_candidates:
            if Path(font_path).exists():
                try:
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    if font_id >= 0:
                        families = QFontDatabase.applicationFontFamilies(font_id)
                        if families:
                            return QFont(families[0], size)
                except:
                    pass
        
        return QFont("Arial", size)
