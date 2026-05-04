---
name: hermes-secrets-env-migration
description: 将 Hermes config.yaml 中的硬编码 API Key 安全迁移到环境变量，消除敏感信息泄露风险
version: "1.0.0"
category: hermes
keywords: [hermes, security, secrets, api key, environment variables, config, migration]
created: "2026-04-27"
author: "Hermes Agent"
---

# Hermes API Key 环境变量安全迁移指南

## 问题背景

`config.yaml` 中硬编码的 API Key 存在以下风险：
- 🔓 **泄露风险**: 意外提交到 Git 仓库、配置文件被他人读取
- 🤝 **协作风险**: 分享配置时无法脱敏
- 📝 **管理困难**: 多环境（开发/测试/生产）需要手动维护多份配置
- 🔄 **轮换麻烦**: 更新 Key 时需要修改多处引用

## ✅ 迁移目标

| 状态 | 目标 |
|------|------|
| ❌ 迁移前 | 13+ 处硬编码 API Key |
| ✅ 迁移后 | 0 处硬编码，全部使用 `${VAR_NAME}` 引用 |

## 🔧 迁移步骤

### 步骤 1: 备份当前配置（重要！）

```bash
# 创建时间戳备份
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.backup.$(date +%Y%m%d_%H%M%S)
```

### 步骤 2: 提取唯一 API Key

使用 Python 脚本安全提取去重后的 Key：

```python
import yaml

with open('/Users/me/.hermes/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 收集所有 key
all_keys = set()

# 从 providers 收集
for name, provider in config.get('providers', {}).items():
    if 'api_key' in provider:
        all_keys.add(provider['api_key'])

# 从 custom_providers 收集
for p in config.get('custom_providers', []):
    if 'api_key' in p:
        all_keys.add(p['api_key'])

# 从 fallback_providers 收集
for p in config.get('fallback_providers', []):
    if 'api_key' in p:
        all_keys.add(p['api_key'])

print(f"找到 {len(all_keys)} 个唯一 API Key:")
for i, key in enumerate(sorted(all_keys)):
    print(f"  {i+1}. {key[:15]}...{key[-4:]}")
```

### 步骤 3: 映射环境变量名称

| Key 类型 | 前缀 | 变量名 |
|----------|------|--------|
| Volcengine Ark | `d4ce...` 或 `ark-` | `ARK_API_KEY` |
| ModelScope | `ms-` | `MODELSCOPE_API_KEY` |
| DeepSeek / Edgefn | `sk-` | `EDGEFN_API_KEY` |
| OpenAI | `sk-proj-` | `OPENAI_API_KEY` |
| Custom Provider | 其他 | `{PROVIDER}_API_KEY` |

### 步骤 4: 批量替换为环境变量引用

```python
import yaml
import os

with open('/Users/me/.hermes/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 提取 key（从备份文件读取，避免已经替换后丢失）
with open('/Users/me/.hermes/config.yaml.backup.before_env', 'r') as f:
    backup = yaml.safe_load(f)
    ark_key = backup['providers']['ark']['api_key']
    modelscope_key = backup['providers']['modelscope']['api_key']
    edgefn_key = backup['providers']['edgefn']['api_key']

# 修改 providers 层
for name, provider in config.get('providers', {}).items():
    key = provider.get('api_key', '')
    if key == ark_key or key.startswith('ark-') or key.startswith('d4ce'):
        provider['api_key'] = '${ARK_API_KEY}'
    elif key == modelscope_key or key.startswith('ms-'):
        provider['api_key'] = '${MODELSCOPE_API_KEY}'
    elif key == edgefn_key or key.startswith('sk-'):
        provider['api_key'] = '${EDGEFN_API_KEY}'

# 修改 custom_providers 层
for p in config.get('custom_providers', []):
    key = p.get('api_key', '')
    if key == ark_key or key.startswith('ark-'):
        p['api_key'] = '${ARK_API_KEY}'
    elif key == modelscope_key or key.startswith('ms-'):
        p['api_key'] = '${MODELSCOPE_API_KEY}'
    elif key == edgefn_key or key.startswith('sk-'):
        p['api_key'] = '${EDGEFN_API_KEY}'

# 修改 fallback_providers 层
for p in config.get('fallback_providers', []):
    key = p.get('api_key', '')
    if key == ark_key or key.startswith('ark-'):
        p['api_key'] = '${ARK_API_KEY}'
    elif key == modelscope_key or key.startswith('ms-'):
        p['api_key'] = '${MODELSCOPE_API_KEY}'
    elif key == edgefn_key or key.startswith('sk-'):
        p['api_key'] = '${EDGEFN_API_KEY}'

# 保存修改
with open('/Users/me/.hermes/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print("✅ config.yaml 已更新完成")
```

### 步骤 5: 验证替换效果

```bash
# 统计硬编码 Key 残留数（应该为 0 或仅有注释中的）
cd ~/.hermes && grep -c "sk-\|ark-\|ms-" config.yaml

# 统计环境变量引用数（应该等于原硬编码数）
cd ~/.hermes && grep -c '${' config.yaml
```

**迁移前后对比示例**:
| 指标 | 迁移前 | 迁移后 |
|------|--------|--------|
| 硬编码数量 | 13 | 0-5（仅注释中残留） |
| 环境变量引用 | 0 | 10+ |

### 步骤 6: 配置环境变量

#### 方法 A: 写入 Shell 配置文件

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
cat >> ~/.zshrc << 'EOF'

# Hermes Agent API Keys
export ARK_API_KEY='your-ark-key-here'
export MODELSCOPE_API_KEY='your-modelscope-key-here'
export EDGEFN_API_KEY='your-deepseek-key-here'
EOF
```

⚠️ **注意**: 如果 shell 配置有语法错误，`source` 会失败。可以改用 `zsh -c '...'` 临时传入。

#### 方法 B: 更新 launchd plist（推荐，永久生效）

网关通过 launchd 启动时，需要在 plist 中配置环境变量：

```python
import plistlib

plist_path = '/Users/me/Library/LaunchAgents/ai.hermes.gateway.plist'
with open(plist_path, 'rb') as f:
    plist = plistlib.load(f)

plist['EnvironmentVariables'] = {
    'ARK_API_KEY': 'your-ark-key',
    'MODELSCOPE_API_KEY': 'your-modelscope-key',
    'EDGEFN_API_KEY': 'your-edgefn-key'
}

with open(plist_path, 'wb') as f:
    plistlib.dump(plist, f, sort_keys=False)
```

重新加载 plist:
```bash
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway.plist
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

### 步骤 7: 更新 .gitignore

确保敏感文件不会意外提交：

```bash
cat >> ~/.hermes/.gitignore << 'EOF'

# Sensitive Files
config.yaml
*.key
*.pem
secrets/
.env*
certs/
EOF
```

### 步骤 8: 重启网关并验证

```bash
# 重启网关（带环境变量）
ARK_API_KEY='key' MODELSCOPE_API_KEY='key' EDGEFN_API_KEY='key' hermes gateway restart

# 验证服务状态
sleep 3 && hermes gateway status

# 运行健康检查
python3 ~/.hermes/scripts/health-check.py
```

## 📋 验证 Checklist

- [ ] `config.yaml` 备份已创建
- [ ] 所有硬编码 API Key 已替换为 `${VAR_NAME}`
- [ ] Shell 配置文件已添加环境变量
- [ ] launchd plist 已添加环境变量（关键！）
- [ ] `.gitignore` 已更新敏感文件规则
- [ ] 网关重启成功，PID 正常
- [ ] 健康检查全部通过
- [ ] 测试发送消息，平台响应正常

## ⚠️ 常见坑点与解决方案

### ❌ 问题 1: launchd 不读取 shell 环境变量

**原因**: launchd 是独立的守护进程，不会读取 `~/.zshrc`

**解决方案**: 必须在 plist 的 `EnvironmentVariables` 节点中显式配置

---

### ❌ 问题 2: shell 配置语法错误导致 source 失败

```
syntax error in conditional expression: unexpected token `('
```

**解决方案**: 使用环境变量内联方式启动：
```bash
ARK_API_KEY='key' MODELSCOPE_API_KEY='key' EDGEFN_API_KEY='key' zsh -c 'hermes gateway restart'
```

---

### ❌ 问题 3: YAML 解析错误

**原因**: 修改时缩进错误或引号不匹配

**解决方案**: 始终使用 Python yaml 库进行修改，不要手动编辑
```python
# ✅ 正确：使用 yaml 库
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
# 修改...
with open('config.yaml', 'w') as f:
    yaml.dump(config, f, sort_keys=False)

# ❌ 错误：手动编辑
# vim config.yaml  # 容易出错
```

---

### ❌ 问题 4: 替换后 Key 不匹配

**原因**: 同一个 Provider 有多个不同的 Key

**解决方案**: 使用「Key 前缀匹配 + 精确值匹配」双重判断

```python
# 不仅仅是前缀匹配，还要精确匹配从备份中提取的原始值
if key == ark_key or key.startswith('ark-') or key.startswith('d4ce'):
    p['api_key'] = '${ARK_API_KEY}'
```

## 📁 交付物清单

| 文件 | 用途 |
|------|------|
| `~/.hermes/config.yaml.backup.before_env` | 迁移前备份，回滚用 |
| `~/.hermes/config.yaml` | 迁移后的配置 |
| `~/.hermes/.gitignore` | 敏感文件过滤规则 |
| `~/Library/LaunchAgents/ai.hermes.gateway.plist` | 带环境变量的启动配置 |
| `~/.hermes/scripts/health-check.py` | 健康检查脚本 |

## 🔄 回滚方案

如果迁移失败，一键回滚：

```bash
# 恢复备份
cp ~/.hermes/config.yaml.backup.before_env ~/.hermes/config.yaml

# 重启网关
hermes gateway restart
```

## 📊 安全提升效果

| 安全指标 | 迁移前 | 迁移后 |
|----------|--------|--------|
| 配置文件中明文 Key | 13 处 | 0 处 |
| Git 泄露风险 | 高 | 低 |
| 配置文件可分享性 | ❌ 不能 | ✅ 可以 |
| Key 轮换成本 | 修改 N 处 | 修改 1 处 |
| 环境隔离能力 | ❌ 无 | ✅ 支持 |

## 📚 相关技能

- `hermes-token-expiry-monitor` - Token 过期监控
- `fix-hermes-message-rate-limit` - 消息限流修复
- `Hermes Gateway 消息平台配置与故障排查` - 平台接入指南
