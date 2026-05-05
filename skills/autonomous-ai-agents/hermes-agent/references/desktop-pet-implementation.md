# 桌面宠物系统实现笔记

## 线程安全问题（macOS PyQt6）

### 问题
```
NSInternalInconsistencyException: 'NSWindow should only be instantiated on the main thread!'
```

### 原因
- Flask HTTP 服务器运行在后台线程
- 直接在后台线程调用 PyQt 窗口操作（如 `show_message`）
- macOS 要求所有 UI 操作必须在主线程执行

### 解决方案：Qt 信号槽机制

```python
from PyQt6.QtCore import QObject, pyqtSignal

class PetServer(QObject):
    # 定义信号
    message_signal = pyqtSignal(str, int)  # text, duration
    state_signal = pyqtSignal(str)  # state
    
    def __init__(self, pet_window, port=51983):
        super().__init__()
        self.pet = pet_window
        
        # 连接信号到槽函数
        self.message_signal.connect(self.pet.show_message)
        self.state_signal.connect(self.pet.change_state)
    
    def _setup_routes(self):
        @self.app.route('/msg')
        def show_message():
            text = request.args.get('text', '')
            duration = int(request.args.get('duration', 3000))
            
            if text:
                # 通过信号发送（线程安全）
                self.message_signal.emit(text, duration)
            
            return jsonify({"success": True, "text": text})
```

### 关键点
1. `PetServer` 继承 `QObject`
2. 使用 `pyqtSignal` 定义信号
3. 在 `__init__` 中连接信号到槽函数
4. HTTP 路由中用 `emit()` 发送信号，而非直接调用

---

## 单例模式实现

### 目的
防止用户误启动多个宠物实例

### 实现
```python
import socket

PORT = 51983

def check_singleton():
    """检测是否已有实例运行"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', PORT))
        s.close()
        print(f'⚠️  宠物已在运行 (端口 {PORT})')
        return False
    except ConnectionRefusedError:
        return True
    finally:
        s.close()
```

### 工作原理
- 尝试连接本地端口
- 如果连接成功 → 已有实例运行 → 退出
- 如果连接失败 → 无实例运行 → 启动

---

## PIL 自动生成动画

### 为什么自动生成？
- 用户没有现成的 GIF 素材
- 需要快速提供可运行的默认皮肤

### 实现代码
```python
from PIL import Image, ImageDraw

def create_cat_frame(size=80, frame_idx=0, state="idle"):
    """创建猫咪单帧"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 身体颜色
    body_color = (255, 180, 100, 255)
    
    # 根据状态调整动画
    if state == "idle":
        # 待机：轻微上下浮动
        offset_y = int(3 * (frame_idx % 2))
        draw.ellipse([15, 25 + offset_y, 65, 65 + offset_y], fill=body_color)
        # ... 绘制其他部位
    
    return img

def create_gif(state="idle", frame_count=8, duration=125):
    """创建 GIF 动画"""
    frames = []
    for i in range(frame_count):
        frame = create_cat_frame(frame_idx=i, state=state)
        frames.append(frame)
    
    frames[0].save(
        f"{state}.gif",
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        disposal=2
    )
```

### 技巧
- `disposal=2` 确保透明背景正确处理
- `duration` 单位是毫秒
- `loop=0` 表示无限循环

---

## HTTP API 设计

### RESTful 端点

| 端点 | 方法 | 说明 | 示例 |
|------|------|------|------|
| `/health` | GET | 健康检查 | `curl http://127.0.0.1:51983/health` |
| `/msg` | GET | 显示消息 | `curl "http://127.0.0.1:51983/msg?text=Hello"` |
| `/state` | GET | 切换动画 | `curl "http://127.0.0.1:51983/state?name=run"` |
| `/` | POST | POST消息 | `curl -X POST -d "Hello" http://127.0.0.1:51983/` |

### URL 编码处理
```python
from urllib.parse import unquote

@self.app.route('/msg')
def show_message():
    text = unquote(request.args.get('text', ''))  # 解码中文
    # ...
```

---

## 透明窗口实现

### PyQt6 配置
```python
from PyQt6.QtCore import Qt

# 窗口标志
self.setWindowFlags(
    Qt.WindowType.FramelessWindowHint |    # 无边框
    Qt.WindowType.WindowStaysOnTopHint |   # 置顶
    Qt.WindowType.Tool                      # 不在任务栏显示
)

# 透明背景
self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
```

### 气泡窗口
```python
# 气泡也需要透明
self.bubble_window.setWindowFlags(
    Qt.WindowType.FramelessWindowHint |
    Qt.WindowType.WindowStaysOnTopHint |
    Qt.WindowType.Tool |
    Qt.WindowType.WindowTransparentForInput  # 鼠标穿透
)
self.bubble_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
```

---

## 跨平台字体加载

### 按优先级尝试字体
```python
def _load_font(size):
    font_candidates = [
        '/System/Library/Fonts/PingFang.ttc',           # macOS 中文
        '/System/Library/Fonts/STHeiti Light.ttc',      # macOS 黑体
        'C:/Windows/Fonts/msyh.ttc',                    # Windows 微软雅黑
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',  # Linux
    ]
    
    for font_path in font_candidates:
        if Path(font_path).exists():
            try:
                return QFont(font_path, size)
            except:
                continue
    
    return QFont("Arial", size)  # 兜底
```

---

## 文件结构

```
~/.hermes/desktop-pet/
├── pet_main.py          # 主入口，单例检测
├── pet_window.py        # 窗口管理，交互逻辑
├── pet_animation.py     # GIF/Sprite 动画系统
├── pet_bubble.py        # 消息气泡，自动换行
├── pet_server.py        # HTTP服务器，线程安全
├── pet_hermes.py        # Hermes集成（预留）
├── create_skin.py       # 皮肤生成工具
├── start.sh             # 启动脚本
└── skins/
    └── default/         # 默认猫咪皮肤
        ├── skin.json
        ├── idle.gif
        └── walk.gif
```

---

## 已知问题

1. **中文 URL 编码**：需要手动 `unquote` 解码
2. **macOS 主线程限制**：必须用信号槽机制
3. **GIF 透明度**：需要 `disposal=2` 参数

---

## 扩展方向

- [ ] 多皮肤切换菜单
- [ ] Hermes 任务监听集成
- [ ] 日程提醒功能
- [ ] 语音播报（TTS）
- [ ] 天气更新通知
