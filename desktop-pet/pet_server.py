"""
Pet Server - HTTP 服务器
远程控制桌面宠物（线程安全版本）
"""
from flask import Flask, request, jsonify
from PyQt6.QtCore import QObject, pyqtSignal


class PetServer(QObject):
    """HTTP 控制服务器"""
    
    # 信号：用于跨线程通信
    message_signal = pyqtSignal(str, int)  # text, duration
    state_signal = pyqtSignal(str)  # state
    
    def __init__(self, pet_window, port=51983):
        super().__init__()
        self.pet = pet_window
        self.port = port
        self.app = Flask(__name__)
        
        # 连接信号
        self.message_signal.connect(self.pet.show_message)
        self.state_signal.connect(self.pet.change_state)
        
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/health')
        def health():
            """健康检查"""
            return jsonify({
                "status": "ok",
                "skin": self.pet.skin_name,
                "state": self.pet.current_state
            })
        
        @self.app.route('/msg')
        def show_message():
            """显示消息"""
            from urllib.parse import unquote
            text = unquote(request.args.get('text', ''))
            duration = int(request.args.get('duration', 3000))
            
            if text:
                # 通过信号发送（线程安全）
                self.message_signal.emit(text, duration)
            
            return jsonify({"success": True, "text": text})
        
        @self.app.route('/state')
        def change_state():
            """切换动画状态"""
            state = request.args.get('name', 'idle')
            
            if state in ['idle', 'walk', 'run', 'sprint']:
                # 通过信号发送（线程安全）
                self.state_signal.emit(state)
            
            return jsonify({"success": True, "state": state})
        
        @self.app.route('/', methods=['POST'])
        def post_message():
            """POST 消息"""
            text = request.get_data(as_text=True)
            if text:
                self.message_signal.emit(text, 3000)
            
            return jsonify({"success": True})
    
    def run(self):
        """运行服务器"""
        # 静默模式
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        try:
            self.app.run(
                host='127.0.0.1',
                port=self.port,
                threaded=True,
                use_reloader=False
            )
        except OSError as e:
            print(f"❌ 端口 {self.port} 已被占用: {e}")
