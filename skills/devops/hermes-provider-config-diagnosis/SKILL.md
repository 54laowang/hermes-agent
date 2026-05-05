---
name: Hermes Provider 配置诊断与模型切换修复
description: 诊断和修复 Hermes 模型切换无响应问题，包括配置结构验证、超时优化、前端错误处理
version: "1.0"
category: devops
keywords: [hermes, config, model-switch, provider, diagnosis, timeout]
---

# 问题场景
当 Web UI 的 ModelPickerDialog 出现加载超时或切换模型无响应时，按以下步骤诊断和修复。

## 🔍 诊断步骤

### 1. 验证配置结构
**关键发现：`providers` 必须是字典格式，不是列表格式**

```yaml
# ✅ 正确格式 (字典格式)
providers:
  modelscope:
    api_key: xxx
    base_url: https://api-inference.modelscope.cn/v1
    default_model: deepseek-ai/DeepSeek-V3.2
    name: modelscope
    slug: modelscope
    type: openai

# ❌ 错误格式 (列表格式 - 会导致 provider 解析失败)
providers:
  - name: modelscope
    api_key: xxx
```

### 2. 检查 Provider 解析逻辑
查看源码确认配置格式要求：
```python
# hermes_cli/providers.py: resolve_user_provider()
# 期望 providers 是 dict，key 是提供商名称
entry = user_config.get(name)  # 通过 key 查找
```

### 3. 验证模型切换功能
```python
from hermes_cli.model_switch import switch_model

result = switch_model(
    raw_input="deepseek-ai/DeepSeek-V3.2",
    current_provider="custom:ark.cn-beijing.volces.com",
    current_model="ark-code-latest",
    current_base_url="https://ark.cn-beijing.volces.com/api/coding/v3",
    current_api_key="",
    is_global=False,
    explicit_provider="modelscope",
)
print(result.success, result.new_model, result.target_provider)
```

## 🛠️ 修复方案

### A. 配置修复
1. 将 `providers` 从列表改为字典格式
2. 为每个提供商添加 `slug` 字段（前端必需）
3. 确保 `fallback_providers` 引用正确的 provider 名称

### B. 超时优化
**文件：`web/src/components/ModelPickerDialog.tsx`**
- 将 `model.options` RPC 请求超时从默认 120s 改为 **30s**
- 添加 "加载超时" 友好错误提示
- 添加「重试」按钮，无需重新打开对话框

**文件：`agent/models_dev.py`**
- 网络请求超时从 15s 改为 **5s**

**文件：`hermes_cli/models.py`**
- `fetch_ollama_cloud_models` 超时从 8s 改为 **5s**

### C. 前端错误处理增强
```tsx
// 添加重试按钮到错误状态
const handleRetry = async () => {
  setError(null);
  setLoadingProviders(true);
  await loadProviders();
};
```

### D. 重新加载配置
```bash
# 找到 gateway 进程
ps aux | grep "hermes.*gateway"

# 发送 HUP 信号重新加载配置（无需重启）
kill -HUP <PID>
```

## ✅ 验证检查清单
- [ ] `hermes model` 命令无报错
- [ ] Python API `switch_model()` 返回 `success=True`
- [ ] Web UI ModelPickerDialog 可正常加载提供商列表
- [ ] 切换到备用模型（modelscope, edgefn）正常工作
- [ ] 超时错误时有友好提示和重试选项

## 💡 经验总结
1. **配置结构不一致是常见坑**：`providers` 是字典，`custom_providers` 是列表，不要混淆
2. **前端 slug 字段必需**：没有 slug 会导致前端无法正确选择
3. **超时设置要考虑交互式体验**：120s 对 CLI 可以，对 Web UI 太长
4. **HUP 信号热重载**：修改配置后无需重启 gateway，优雅重载

## 🔗 相关源码位置
- `hermes_cli/providers.py:482` - `resolve_user_provider()`
- `hermes_cli/model_switch.py:635` - `switch_model()`
- `web/src/components/ModelPickerDialog.tsx` - 前端对话框
- `agent/models_dev.py:208` - `fetch_models_dev()`
