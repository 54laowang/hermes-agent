# 桌面宠物置顶功能说明

## 当前状态
✅ 默认**始终置顶**（WindowStaysOnTopHint）

## 如何切换置顶

### 方法1：右键菜单
1. 右键点击宠物
2. 选择 **📌 取消置顶** 或 **📌 始终置顶**
3. 宠物会显示气泡提示当前状态

### 方法2：双击
- 双击宠物可快速切换置顶状态
- 取消置顶后，宠物会被其他窗口遮挡
- 再次双击恢复置顶

## macOS 专属优化
- 添加了 `WindowDoesNotAcceptFocus` 标志
- 宠物不会抢占输入焦点
- 设置为浮动窗口层级（floating）

## 窗口属性
- ✅ 无边框（FramelessWindowHint）
- ✅ 始终置顶（WindowStaysOnTopHint）
- ✅ 工具窗口（Tool）- 不显示在任务栏
- ✅ 不接受焦点（WindowDoesNotAcceptFocus）
- ✅ 透明背景（WA_TranslucentBackground）
- ✅ 不激活显示（WA_ShowWithoutActivating）

## 测试
```bash
# 检查状态
python3 pet_control.py health

# 发送测试消息
python3 pet_control.py msg "测试消息"
```

## 注意事项
- 切换置顶后窗口会重新显示，这是正常行为
- 如果宠物消失，检查是否在其他桌面空间
- 拖动宠物位置会自动保存（需要配置持久化功能）
