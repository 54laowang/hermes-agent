# Docker Desktop 安装故障排查记录

## 问题: 残留文件冲突

### 错误信息
```
Error: It seems there is already a Binary at '/usr/local/bin/hub-tool'.
```

### 根因分析

Docker Desktop 卸载后，部分二进制文件残留在 `/usr/local/bin/` 目录：
- `/usr/local/bin/hub-tool` → 符号链接到已删除的 Docker.app
- `/usr/local/bin/docker*` → 可能残留的 Docker CLI 工具

### 解决方案

#### 方案 A: 自动清理脚本（需要密码）

```bash
#!/bin/bash
# 清理残留文件
sudo rm -f /usr/local/bin/hub-tool
sudo rm -f /usr/local/bin/docker
sudo rm -f /usr/local/bin/docker-compose
sudo rm -f /usr/local/bin/docker-credential-osxkeychain

# 重新安装
brew install --cask docker
```

#### 方案 B: 手动下载安装（推荐）

```bash
# 下载 Docker Desktop
open https://desktop.docker.com/mac/main/arm64/Docker.dmg

# 双击 DMG → 拖到 Applications → 启动 Docker.app
```

### 验证步骤

```bash
# 检查安装
docker --version
# 期望: Docker version 29.4.1, build xxxxx

# 检查运行状态
docker ps
# 期望: 显示容器列表（可能为空）

# 检查 Docker Desktop
ls -la /Applications/Docker.app
# 期望: 显示 Docker.app 目录
```

---

## 问题: Docker Desktop 未启动

### 错误信息
```bash
docker ps
# Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running on this host?
```

### 解决方案

```bash
# 启动 Docker Desktop
open -a Docker

# 等待启动（30-60秒）
# 菜单栏 Docker 图标稳定后继续

# 验证
docker info
```

### 启动时间参考

| 系统 | 启动时间 |
|------|---------|
| macOS M1/M2 | 30-45秒 |
| macOS Intel | 45-60秒 |
| Windows WSL2 | 60-90秒 |

---

## 问题: Homebrew 安装需要密码

### 错误信息
```
sudo: a terminal is required to read the password; either use the -S option to read from standard input or configure an askpass helper
```

### 解决方案

Homebrew 安装 Docker Desktop 时需要 sudo 权限来创建 `/usr/local/cli-plugins` 目录。

**方案 A: 在终端手动运行**
```bash
# 在你的终端运行（非 Hermes 终端）
brew install --cask docker
# 根据提示输入密码
```

**方案 B: 预先创建目录**
```bash
# 预先创建需要的目录（需要密码）
sudo mkdir -p /usr/local/cli-plugins

# 然后安装（无需密码）
brew install --cask docker
```

---

## 最佳实践

### 1. 卸载 Docker Desktop

完整卸载步骤：
```bash
# 停止 Docker
pkill -x Docker

# 卸载应用
sudo rm -rf /Applications/Docker.app

# 清理二进制文件
sudo rm -f /usr/local/bin/docker*
sudo rm -f /usr/local/bin/hub-tool

# 清理数据（可选，会删除所有容器和镜像）
rm -rf ~/Library/Containers/com.docker.docker
rm -rf ~/.docker
```

### 2. 首次启动检查清单

- [ ] Docker Desktop 图标出现在菜单栏
- [ ] 图标从动画变为静止状态
- [ ] `docker info` 返回系统信息
- [ ] `docker ps` 不报错（可能为空列表）
- [ ] `docker run hello-world` 成功运行

### 3. 性能优化（macOS）

```bash
# 调整 Docker Desktop 资源限制
# 打开 Docker Desktop → Settings → Resources

# 推荐配置（M1/M2/M3 16GB 内存）
# CPUs: 4-6
# Memory: 8-10 GB
# Swap: 2 GB
# Disk image size: 60 GB
```

---

## 相关文件

- Docker Desktop 下载: https://desktop.docker.com/mac/main/arm64/Docker.dmg
- Homebrew Cask: `brew install --cask docker`
- Docker 官方文档: https://docs.docker.com/desktop/install/mac-install/

---

**创建时间**: 2026-05-02
**验证环境**: macOS 14.0 (Sonoma), Apple Silicon M2, Docker Desktop 4.71.0
