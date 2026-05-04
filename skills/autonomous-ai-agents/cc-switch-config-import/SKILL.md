---
name: cc-switch-config-import
description: 从 CC-Switch 桌面应用的 SQLite 数据库批量导入 Claude Code 配置到命令行 ccs 工具
category: autonomous-ai-agents
---

# CC-Switch 配置批量导入技能

从 CC-Switch 桌面应用的 SQLite 数据库中提取所有 Claude Code 提供商配置，批量导入到命令行 ccs (Claude Code Switcher) 工具中。

## 使用场景

当你已经在 CC-Switch 桌面应用中配置了多个提供商，但希望在终端/命令行环境中也能快速切换时使用。

## 配置位置

CC-Switch 桌面应用的配置存储在：
```
~/.cc-switch/cc-switch.db
```

## 操作步骤

### 1. 验证数据库存在并查看表结构
```bash
# 查看数据库中的表
sqlite3 ~/.cc-switch/cc-switch.db ".tables"

# 查看 providers 表结构
sqlite3 ~/.cc-switch/cc-switch.db ".schema providers"

# 查看所有已配置的提供商
sqlite3 ~/.cc-switch/cc-switch.db "SELECT name FROM providers WHERE app_type = 'claude';"
```

### 2. 使用 Python 脚本批量导入

```python
import sqlite3
import json
import subprocess

# 连接数据库
conn = sqlite3.connect('/Users/me/.cc-switch/cc-switch.db')
cursor = conn.cursor()

# 获取所有 Claude 配置
cursor.execute("SELECT name, settings_config FROM providers WHERE app_type = 'claude'")
providers = cursor.fetchall()
conn.close()

print("📋 找到以下 Claude 配置:")
print("-" * 50)

for name, settings_config in providers:
    try:
        config = json.loads(settings_config)
        env = config.get('env', {})
        
        url = env.get('ANTHROPIC_BASE_URL', '')
        token = env.get('ANTHROPIC_AUTH_TOKEN', '') or env.get('ANTHROPIC_API_KEY', '')
        
        if url and token:
            print(f"\n✅ {name}")
            print(f"   URL: {url}")
            print(f"   Token: {token[:15]}...")
            
            # 添加到命令行 ccs
            result = subprocess.run(
                ['ccs', 'add', name.lower().replace(' ', '-'), url, token],
                capture_output=True, text=True
            )
            if 'successfully' in result.stdout or '已成功' in result.stdout:
                print(f"   → 已导入到 ccs")
            else:
                print(f"   → 跳过 (可能已存在)")
        else:
            print(f"\n⚠️  {name} - 缺少 URL 或 Token，跳过")
            
    except Exception as e:
        print(f"\n❌ {name} - 解析错误: {e}")

print("\n" + "-" * 50)
print("\n📦 导入完成！运行 'ccs list' 查看所有配置")
```

### 3. 验证导入结果
```bash
ccs list
```

## 数据库结构说明

CC-Switch 使用 SQLite 数据库存储配置，核心表包括：

| 表名 | 用途 |
|------|------|
| `providers` | 提供商配置（URL、Token、模型等） |
| `provider_endpoints` | 提供商端点列表 |
| `proxy_config` | 代理服务器配置 |
| `mcp_servers` | MCP 服务器配置 |
| `skills` | 技能库配置 |
| `proxy_request_logs` | 请求日志和成本统计 |
| `model_pricing` | 模型定价信息 |

## local-proxy 模式优势

推荐激活 `local-proxy` 配置连接到桌面应用的代理服务器：

- ✅ **故障转移** - 自动切换可用提供商
- ✅ **成本统计** - 实时查看 Token 消耗和成本
- ✅ **健康检查** - 自动监控 API 状态
- ✅ **桌面同步** - 桌面应用切换配置后终端自动同步

```bash
# 激活代理模式
ccs use local-proxy

# 启动 Claude Code
claude
```

## 常见提供商

从桌面应用导入的典型配置包括：

| 提供商 | 类型 |
|--------|------|
| DouBaoSeed | 火山引擎（豆包编码版） |
| Longcat | 国内 API |
| OpenRouter | 聚合平台 |
| Nvidia | Nvidia API |
| poixe | 第三方提供商 |
| baishan | 白山云 |

## 故障排除

1. **数据库不存在**：确保已安装并运行 CC-Switch 桌面应用
2. **ccs 命令未找到**：确保已全局安装 `claude-code-switcher`
3. **导入失败**：检查环境变量 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN`
