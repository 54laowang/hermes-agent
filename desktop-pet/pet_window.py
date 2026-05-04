"""
Pet Window - 宠物窗口管理
跨平台透明窗口，支持动画和交互
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QLabel, QMenu
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPixmap, QCursor

from pet_animation import AnimationLoader
from pet_bubble import BubbleManager


class PetWindow(QWidget):
    """桌面宠物窗口"""
    
    def __init__(self, skin_name="default"):
        super().__init__()
        
        self.skin_name = skin_name
        self.skin_dir = Path(__file__).parent / "skins" / skin_name
        
        # 状态
        self.current_state = "idle"
        self.frame_idx = 0
        self.frames = []
        self.fps = 8
        
        # 初始化窗口
        self._init_window()
        
        # 加载皮肤
        self._load_skin()
        
        # 初始化气泡管理器
        self.bubble_manager = BubbleManager(self)
        
        # 动画定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)
        self.timer.start(1000 // self.fps)
        
        # 拖动相关
        self.drag_pos = None
    
    def _init_window(self):
        """初始化窗口属性"""
        # 窗口标志：无边框 + 置顶 + 工具窗口
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus  # 不接受焦点
        )
        
        # 透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        
        # 不显示在任务栏
        self.setWindowModality(Qt.WindowModality.NonModal)
        
        # macOS 专属：强制置顶
        if sys.platform == 'darwin':
            # 延迟调用，确保窗口已创建
            QTimer.singleShot(100, self._force_stay_on_top)
    
    def _force_stay_on_top(self):
        """macOS 强制置顶"""
        try:
            import subprocess
            # 使用 AppleScript 激活窗口
            script = '''
            tell application "System Events"
                try
                    set frontmost of first process whose name contains "Python" to true
                end try
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, timeout=2)
        except:
            pass
    
    def _load_skin(self):
        """加载皮肤"""
        try:
            loader = AnimationLoader(self.skin_dir)
            config = loader.load_config()
            self.frames = loader.load_animation(self.current_state)
            self.fps = config["animations"][self.current_state].get("fps", 8)
            
            # 设置窗口大小为第一帧大小
            if self.frames:
                size = self.frames[0].size()
                self.setFixedSize(size)
                self._display_frame(0)
                
        except Exception as e:
            print(f"❌ 加载皮肤失败: {e}")
            self._create_default_pet()
    
    def _create_default_pet(self):
        """创建默认宠物（备用）"""
        from PyQt6.QtGui import QPainter, QColor, QBrush
        
        # 创建一个简单的圆形宠物
        size = 80
        self.setFixedSize(size, size)
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(100, 150, 255, 200)))
        painter.drawEllipse(10, 10, size - 20, size - 20)
        painter.end()
        
        self.frames = [pixmap]
        self._display_frame(0)
    
    def _display_frame(self, idx):
        """显示指定帧"""
        if not self.frames:
            return
        
        frame = self.frames[idx]
        
        # 创建 QLabel 显示图像
        if not hasattr(self, 'label'):
            self.label = QLabel(self)
            self.label.setGeometry(0, 0, frame.width(), frame.height())
        
        self.label.setPixmap(frame)
    
    def _next_frame(self):
        """播放下一帧"""
        if not self.frames:
            return
        
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        self._display_frame(self.frame_idx)
    
    def show_message(self, text, duration=3000):
        """显示消息气泡"""
        self.bubble_manager.show_bubble(text, duration)
    
    def change_state(self, state):
        """切换动画状态"""
        if state == self.current_state:
            return
        
        try:
            loader = AnimationLoader(self.skin_dir)
            self.frames = loader.load_animation(state)
            self.current_state = state
            self.frame_idx = 0
            
            # 更新帧率
            config = loader.load_config()
            self.fps = config["animations"][state].get("fps", 8)
            self.timer.setInterval(1000 // self.fps)
            
        except Exception as e:
            print(f"❌ 切换状态失败: {e}")
    
    # ========== 鼠标事件 ==========
    
    def mousePressEvent(self, event):
        """鼠标按下 - 开始拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """鼠标移动 - 拖动窗口"""
        if self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        self.drag_pos = None
    
    def mouseDoubleClickEvent(self, event):
        """双击 - 切换置顶状态"""
        # 双击切换置顶，而不是关闭
        if self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Tool
            )
            self.show_message("已取消置顶")
        else:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool
            )
            self.show_message("已恢复置顶")
        
        # 重新显示窗口
        self.show()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    
    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)
        
        # 切换动画状态
        for state in ["idle", "walk", "run", "sprint"]:
            action = menu.addAction(f"🎬 {state}")
            action.triggered.connect(lambda checked, s=state: self.change_state(s))
        
        menu.addSeparator()
        
        # 测试消息
        test_action = menu.addAction("💬 测试消息")
        test_action.triggered.connect(lambda: self.show_message("你好！我是桌面宠物 🐱"))
        
        menu.addSeparator()
        
        # 置顶切换
        stay_on_top = self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
        top_action = menu.addAction("📌 取消置顶" if stay_on_top else "📌 始终置顶")
        top_action.triggered.connect(self._toggle_stay_on_top)
        
        menu.addSeparator()
        
        # 退出
        quit_action = menu.addAction("❌ 退出")
        quit_action.triggered.connect(self.close)
    
    def _toggle_stay_on_top(self):
        """切换置顶状态"""
        if self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Tool
            )
            self.show_message("已取消置顶")
        else:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool
            )
            self.show_message("已恢复置顶")
        
        # 重新显示窗口
        self.show()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        menu.exec(QCursor.pos())
