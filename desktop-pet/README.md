# 🐱 桌面宠物系统

跨平台透明窗口桌面宠物，支持动画、消息气泡、HTTP 控制、Hermes Agent 集成。

## 快速开始

```bash
# 启动宠物
cd ~/.hermes/desktop-pet
python3 pet_main.py

# 控制宠物
python3 pet_control.py msg "你好世界"
python3 pet_control.py state walk
python3 pet_control.py health
```

## 功能特性

### ✅ 基础功能
- **透明窗口** - 无边框、始终置顶
- **拖动交互** - 单击拖动移动位置
- **动画系统** - 支持 GIF 动画
- **消息气泡** - 自动换行、定时消失

### ✅ HTTP API
- `GET /health` - 健康检查
- `GET /msg?text=Hello` - 显示消息
- `GET /state?name=walk` - 切换状态

### ✅ Hermes 集成
- **任务提醒** - 监听 Hermes 任务完成事件
- **日程提醒** - 接入日历 API（待完善）
- **天气通知** - 定时天气推送（待完善）

## 项目结构

```
~/.hermes/desktop-pet/
├── pet_main.py          # 主入口
├── pet_window.py        # 窗口管理
├── pet_animation.py     # 动画系统
├── pet_bubble.py        # 消息气泡
├── pet_server.py        # HTTP 服务器
├── pet_hermes.py        # Hermes 集成
├── pet_control.py       # 命令行控制
├── hermes_config.json   # Hermes 配置
└── skins/
    └── default/         # 默认皮肤
        └── skin.json
```

## 配置说明

### hermes_config.json

```json
{
  "enabled": true,
  "task_reminder": {
    "enabled": true,
    "success_animation": "idle",
    "fail_animation": "sprint"
  },
  "schedule_reminder": {
    "enabled": true,
    "advance_minutes": 5
  },
  "weather": {
    "enabled": false,
    "city": "北京"
  }
}
```

## 开发计划

- [ ] 更多皮肤素材
- [ ] 语音播报（TTS）
- [ ] 天气 API 集成
- [ ] 日历 API 集成
- [ ] 自定义皮肤编辑器

## 依赖

- Python 3.8+
- PyQt6
- Pillow
- Flask

## License

MIT
