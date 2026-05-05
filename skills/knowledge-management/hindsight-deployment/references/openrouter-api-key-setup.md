# OpenRouter API Key 配置指南

## 什么是 OpenRouter

OpenRouter 是一个统一的 LLM API 网关，提供：
- 免费额度（每月 $5）
- 多模型支持（GPT-4, Claude, Llama, Gemini 等）
- 统一 API 格式
- 按使用量付费

## 获取 API Key

### Step 1: 注册账号

访问: https://openrouter.ai/signup

支持：
- Google 账号登录
- GitHub 账号登录
- 邮箱注册

### Step 2: 创建 API Key

1. 登录后访问: https://openrouter.ai/keys
2. 点击 "Create Key"
3. 输入 Key 名称（如: "Hindsight"）
4. 复制生成的 Key（格式: `sk-or-v1-xxxxx`）

⚠️ **重要**: API Key 只显示一次，务必保存！

### Step 3: 免费额度

新用户可获得每月 $5 免费额度：
- 自动发放
- 每月重置
- 足够支持 Hindsight 日常使用

---

## 配置方式

### 方式 1: 环境变量（推荐）

```bash
# 临时生效（当前会话）
export OPENROUTER_API_KEY='sk-or-v1-xxxxx'

# 永久生效（添加到 shell 配置）
echo 'export OPENROUTER_API_KEY="sk-or-v1-xxxxx"' >> ~/.zshrc
source ~/.zshrc

# 验证
echo $OPENROUTER_API_KEY
```

### 方式 2: Hermes 配置文件

```bash
# 添加到 Hermes .env
echo "OPENROUTER_API_KEY=sk-or-v1-xxxxx" >> ~/.hermes/.env
```

### 方式 3: Docker 启动参数

```bash
docker run -d \
    -e HINDSIGHT_API_LLM_API_KEY=$OPENROUTER_API_KEY \
    ...
```

---

## 使用场景

### 场景 1: Hindsight 记忆系统

```bash
# 使用 OpenRouter 免费模型
-e HINDSIGHT_API_LLM_PROVIDER=openai \
-e HINDSIGHT_API_LLM_API_KEY=$OPENROUTER_API_KEY \
-e HINDSIGHT_API_LLM_MODEL=openrouter/free \
-e HINDSIGHT_API_LLM_BASE_URL=https://openrouter.ai/api/v1
```

### 场景 2: Hermes Agent

编辑 `~/.hermes/config.yaml`:
```yaml
providers:
  openrouter:
    api_key: ${OPENROUTER_API_KEY}
    base_url: https://openrouter.ai/api/v1
    default_model: openrouter/free
    name: openrouter
```

### 场景 3: Python 项目

```python
import openai

client = openai.OpenAI(
    api_key="sk-or-v1-xxxxx",
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="openrouter/free",  # 或其他模型
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

## 模型选择

### 免费模型

| 模型 | 提供商 | 特点 |
|------|--------|------|
| `openrouter/free` | 多模型轮询 | 免费层推荐 |
| `nousresearch/hermes-3-llama-3.1-405b:free` | Nous Research | 405B 参数大模型 |
| `meta-llama/llama-3.1-8b-instruct:free` | Meta | 快速响应 |

### 付费模型（按需选择）

| 模型 | 价格 | 适用场景 |
|------|------|---------|
| `openai/gpt-4o-mini` | $0.15/1M tokens | 日常对话 |
| `anthropic/claude-sonnet-4` | $3/1M tokens | 复杂推理 |
| `google/gemini-flash-1.5` | $0.075/1M tokens | 长文本 |

完整模型列表: https://openrouter.ai/models

---

## 安全最佳实践

### 1. 环境变量管理

✅ **推荐**:
```bash
# 使用环境变量
export OPENROUTER_API_KEY='sk-or-v1-xxxxx'
```

❌ **避免**:
```bash
# 硬编码在脚本中
python app.py --api-key sk-or-v1-xxxxx  # 不安全！
```

### 2. Git 忽略

添加到 `.gitignore`:
```
.env
.env.local
*.key
secrets.yaml
```

### 3. 权限控制

```bash
# 设置文件权限
chmod 600 ~/.hermes/.env
chmod 600 ~/.zshrc
```

### 4. Key 轮换

定期更新 API Key：
1. 访问 https://openrouter.ai/keys
2. 删除旧 Key
3. 创建新 Key
4. 更新配置文件

---

## 故障排查

### 问题 1: API Key 未识别

**症状**:
```bash
echo $OPENROUTER_API_KEY
# 空输出
```

**解决方案**:
```bash
# 检查 shell 配置
cat ~/.zshrc | grep OPENROUTER_API_KEY

# 重新加载配置
source ~/.zshrc

# 或重新设置
export OPENROUTER_API_KEY='sk-or-v1-xxxxx'
```

### 问题 2: API 调用失败

**症状**:
```json
{"error": {"message": "Invalid API key", "type": "invalid_request_error"}}
```

**解决方案**:
```bash
# 验证 Key 格式
echo $OPENROUTER_API_KEY | grep -E '^sk-or-v1-'
# 应输出完整的 Key

# 测试 API
curl https://openrouter.ai/api/v1/models \
    -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

### 问题 3: 额度用尽

**症状**:
```json
{"error": {"message": "Insufficient credits", "type": "insufficient_quota"}}
```

**解决方案**:
1. 检查使用量: https://openrouter.ai/credits
2. 等待下月重置（免费额度）
3. 或充值付费额度

---

## 费用估算

### Hindsight 日常使用

假设：
- 每天存储 10 条记忆
- 每条记忆平均 100 tokens
- 使用 `openrouter/free` 模型

**月度费用**: $0（免费额度足够）

### 高频使用

假设：
- 每天存储 100 条记忆
- 每条记忆平均 200 tokens
- 使用 `gpt-4o-mini` 模型

**月度费用**:
- 输入: 100 * 200 * 30 = 600,000 tokens
- 费用: 0.6 * $0.15 = $0.09

---

## 相关资源

- OpenRouter 官网: https://openrouter.ai
- API 文档: https://openrouter.ai/docs
- 模型列表: https://openrouter.ai/models
- 费用查询: https://openrouter.ai/credits

---

**创建时间**: 2026-05-02
**验证环境**: OpenRouter API v1, Hindsight v0.1.6
