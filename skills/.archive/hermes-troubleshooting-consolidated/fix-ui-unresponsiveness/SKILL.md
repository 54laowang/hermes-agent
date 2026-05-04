---
name: fix-ui-unresponsiveness
description: 修复 UI 无响应问题的标准化流程 - 识别性能瓶颈、优化超时设置、改进用户体验
---

# UI 无响应问题修复指南

## 问题识别

当用户报告"无响应"、"卡住"、"长时间加载"等问题时，按照以下步骤诊断和修复：

### 1. 找到请求源头
- 定位到触发无响应的组件/页面
- 识别发出的网络请求或异步操作
- 检查请求的超时设置和错误处理

### 2. 检查关键参数
```
✗ 默认超时太长（> 30秒）→ 应缩短到 10-30 秒
✗ 无错误处理 → 用户永远等待
✗ 无重试机制 → 一次失败就卡住
✗ 没有加载状态 → 用户不知道正在发生什么
```

## 修复步骤

### 第一步：缩短前端超时
```typescript
// 在 GatewayClient 或 fetch 调用中设置合理的超时
gw.request("model.options", params, 30_000) // 30秒，而非默认120秒
```

**最佳实践**：
- 交互式操作（如选择器、弹窗）：10-30 秒
- 后台加载：30-60 秒
- 文件上传/大请求：按实际情况调整

### 第二步：添加友好的错误提示
```typescript
.catch((e) => {
  const msg = e instanceof Error ? e.message : String(e);
  if (msg.includes("timeout") || msg.includes("timed out")) {
    setError("网络超时 — 检查连接后重试");
  } else if (msg.includes("network") || msg.includes("fetch")) {
    setError("网络连接失败 — 请检查网络设置");
  } else {
    setError(msg);
  }
});
```

### 第三步：添加重试按钮
```typescript
const loadData = () => {
  setLoading(true);
  setError(null);
  gw.request(...).then(...).catch(...);
};

// 在错误显示区域添加：
{error && (
  <div>
    <div className="text-error">{error}</div>
    <button onClick={loadData} disabled={loading}>
      {loading ? "加载中…" : "重试"}
    </button>
  </div>
)}
```

### 第四步：优化后端超时（如果有控制权）
对于后端的网络请求，同样需要缩短超时：

```python
# 交互式操作使用更短的超时
response = requests.get(url, timeout=5)  # 5秒而非15秒
```

**后端超时原则**：
- 交互式 API：3-5 秒
- 后台任务：10-30 秒
- 必须有缓存机制，失败时回退到缓存

### 第五步：清理配置和验证修复效果

1. ✅ **检查重复配置**：验证 fallback_providers 中没有与主模型完全重复的条目
   ```yaml
   # ❌ 避免：备用模型与主模型完全相同（浪费重试时间）
   fallback_providers:
     - model: ark-code-latest  # 与主模型相同，冗余
       provider: ark.cn-beijing.volces.com
   
   # ✅ 正确：备用模型应该是不同的提供商/模型
   fallback_providers:
     - model: deepseek-ai/DeepSeek-V3.2
       provider: modelscope
     - model: GLM-5
       provider: edgefn
   ```

2. ✅ 检查超时时间是否合理
3. ✅ 验证错误信息是否友好
4. ✅ 测试重试按钮是否工作
5. ✅ 确保加载状态正确显示
6. ✅ 模拟网络失败场景验证鲁棒性

## 常见模式

### 模型选择器无响应
```
问题：打开模型选择器后长时间无响应
原因：models.dev API 超时 15秒 + 前端默认超时 120秒
修复：
  - 前端：30秒超时
  - 后端：models.dev 请求缩短到 5秒
  - 添加重试按钮
  - 友好的超时提示
```

### 长列表加载无响应
```
问题：滚动加载长列表时卡住
修复：
  - 分页加载
  - 虚拟滚动
  - 加载骨架屏
  - 取消未完成的请求
```

### 表单提交无响应
```
问题：点击提交后无反馈
修复：
  - 按钮禁用状态
  - 加载动画
  - 乐观更新（先显示成功，失败再回滚）
  - 超时后自动重试（幂等操作）
```

### CLI 退出时虚假错误报告
```
问题：Ctrl+C 退出后显示 "OSError 5: Input/output error"
原因：macOS uv Python 环境下 asyncio stdin 注册在 shutdown 时抛出无害错误
修复：
  - 在错误处理中捕获并忽略该特定错误
  - 添加条件判断：`if e.errno != 5 or "Input/output error" not in str(e)`
```

## 关键原则

1. **用户感知优先**：宁可快速失败并让用户重试，也不要让用户无限等待
2. **超时分层**：前端超时 > 后端超时（确保前端先捕获超时）
3. **错误透明**：用户应该知道发生了什么，以及可以做什么
4. **渐进降级**：网络失败时回退到缓存或基本功能
5. **可恢复性**：提供重试机制，让用户可以从错误中恢复

## 验收标准

修复完成后，应该满足：
- [ ] 最长等待时间 < 30 秒（交互式操作）
- [ ] 错误信息清晰，用户知道发生了什么
- [ ] 提供重试或其他恢复方式
- [ ] 加载状态明确反馈
- [ ] 模拟网络异常场景测试通过
