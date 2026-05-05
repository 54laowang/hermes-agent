---
name: 编译安装 FinceptTerminal (macOS Qt 6.11 兼容补丁)
description: 在 macOS 上编译安装开源量化投研终端 FinceptTerminal，解决 Qt 版本兼容性、链接错误和启动崩溃问题
---

# 编译安装 FinceptTerminal (macOS Qt 6.11 兼容补丁

## 描述
在 macOS 上编译安装开源量化投研终端 FinceptTerminal，解决 Qt 版本兼容性问题、编译错误和启动崩溃问题。

FinceptTerminal 是一个专业的开源投研终端，集成了 AkShare 支持 A 股市场数据，支持多资产、量化分析、预测市场等功能。

## 问题与解决方案

### 1. Qt 版本兼容性问题
**问题**：FinceptTerminal 要求 Qt 6.8.3 精确版本，但 Homebrew 已安装 Qt 6.11，无法满足。
**解决方案**：使用 `FINCEPT_ALLOW_QT_DRIFT=ON` 绕过版本检查：

```bash
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qt -DFINCEPT_ALLOW_QT_DRIFT=ON
```

### 2. Unity 构建问题
**问题**：默认开启 Unity Build 会导致链接错误 "undefined symbols"。
**解决方案**：强制禁用 Unity Build：

```cmake
# 在 CMakeLists.txt 中修改
set(CMAKE_UNITY_BUILD OFF)
```

### 3. 核心源文件缺失问题
**问题**：多个核心源文件没有添加到 CMakeLists.txt 的 TRADING_SOURCES/SCREEN_SOURCES/UI_SOURCES 中，导致链接错误。
**解决方案**：手动添加这些文件：
- `ExchangeSession.cpp`, `ExchangeSessionManager.cpp`, `ExchangeDaemonPool.cpp` → TRADING_SOURCES
- `NetSpeedMeter.cpp` → NETWORK_SOURCES
- `VoiceConfigSection.cpp` → SCREEN_SOURCES
- `PolymarketOrderBlotter.cpp` → SCREEN_SOURCES
- `SpeedSparkline.cpp` → UI_SOURCES

### 4. SingleApplication 启动崩溃问题 (macOS 特有)
**问题**：`SingleApplication` 在 macOS 上由于沙箱权限限制无法创建共享内存锁，导致启动崩溃：
```
QSharedMemory::KeyError: QSharedMemoryPrivate::initKey: unable to set key on lock
```

**根本原因**：macOS 对应用程序沙箱不允许在标准路径创建系统级共享内存键，即使移出 `/tmp` 仍然失败。

**解决方案**：完全禁用 SingleApplication，改用标准 QApplication：

```cpp
// 替换 #include <singleapplication.h> 为
#include <QApplication>

// 替换 SingleApplication 构造为
QApplication app(argc, argv);

// 移除所有 isSecondary() 检查和 receivedMessage 信号连接
```

这样就绕过了权限问题，缺点是失去单实例功能，但不影响正常使用（可以多开，大多数用户不需要单实例）。

### 5. macdeployqt 打包问题
**问题**：打包时 codesign 错误，因为 Python 脚本和 yt-dlp 放在错误位置：
```
code has no resources but signature indicates they must be present
```

**解决方案**：将所有非可执行资源移动到 `Contents/Resources`：

```bash
mv FinceptTerminal.app/Contents/MacOS/scripts FinceptTerminal.app/Contents/Resources/
mv FinceptTerminal.app/Contents/MacOS/yt-dlp FinceptTerminal.app/Contents/Resources/
if [ -d "FinceptTerminal.app/Contents/MacOS/resources" ]; then
  mv FinceptTerminal.app/Contents/MacOS/resources/* FinceptTerminal.app/Contents/Resources/
  rm -rf FinceptTerminal.app/Contents/MacOS/resources
fi
```

### 6. Gatekeeper 隔离问题
**问题**：从网络下载或编译的应用带有 `com.apple.provenance` 隔离属性，Finder 阻止打开。

**解决方案**：移除隔离属性：

```bash
xattr -dr com.apple.provenance ~/Applications/FinceptTerminal.app
codesign --force --deep --sign - ~/Applications/FinceptTerminal.app
```

## 完整编译步骤

```bash
# 1. 克隆源码
git clone --depth 1 https://github.com/Fincept-Corporation/FinceptTerminal.git /tmp/FinceptTerminal
cd /tmp/FinceptTerminal/fincept-qt

# 2. 安装 Qt (如果没有)
brew install qt

# 3. 创建构建目录
mkdir -p build && cd build

# 4. 配置 CMake (允许 Qt 版本漂移，禁用 Unity Build)
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qt -DFINCEPT_ALLOW_QT_DRIFT=ON

# 5. 修改 CMakeLists.txt 添加缺失的源文件（见上文问题 3）
# 6. 修改 main.cpp 禁用 SingleApplication（见上文问题 4）

# 7. 编译
make -j$(sysctl -n hw.ncpu)

# 8. 打包 Qt 依赖
/opt/homebrew/bin/macdeployqt FinceptTerminal.app -always-overwrite

# 9. 移动资源到正确位置（见上文问题 5）

# 10. 复制到应用程序目录
cp -R FinceptTerminal.app ~/Applications/

# 11. 移除隔离属性并签名
xattr -dr com.apple.provenance ~/Applications/FinceptTerminal.app
codesign --force --deep --sign - ~/Applications/FinceptTerminal.app
```

## 验证启动
```bash
# 命令行直接启动验证
~/Applications/FinceptTerminal.app/Contents/MacOS/FinceptTerminal
```

## 已知限制
- 单实例功能被禁用，允许多个进程同时运行
- A 股数据需要配置 AkShare，首次启动后需要完成 Python 环境设置
