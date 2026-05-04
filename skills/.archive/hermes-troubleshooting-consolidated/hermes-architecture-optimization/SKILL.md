---
name: hermes-architecture-optimization
description: Hermes Agent 完整架构优化流程 - 4层记忆架构 + 4阶段弹性建设 + SOP标准化
version: 2.0.0
created: 2026-04-26
updated: 2026-04-26
source: lsdefine/GenericAgent + 实战经验
tags: [hermes, architecture, resilience, monitoring, memory, optimization]
---

# Hermes 架构优化完整指南

## 两大优化支柱

```
┌─────────────────────────────────────────────────────────────┐
│                     Hermes 架构优化                          │
├─────────────────────────────────┬───────────────────────────┤
│                                 │                           │
│   🧠 记忆架构优化              │   🛡️ 弹性层优化          │
│   (4层记忆 + SOP 标准化)        │   (监控 + 限流 + 熔断)   │
│                                 │                           │
│   - 解决"忘了怎么做事"          │   - 解决"系统崩了没人管" │
│   - 把经验变成可复用流程        │   - 把被动救火变主动防御 │
│                                 │                           │
└─────────────────────────────────┴───────────────────────────┘
```

---

## 第一部分：记忆架构优化 (基于 GenericAgent)

### 1. 四层记忆架构

**设计公理**：信息按使用频率和可执行性分层，越高层越精简、越可执行。

```
L1_Insight_Index (极简索引层)
├── 红线规则（绝对不可违背）
├── 高频场景指针（快速定位）
└── 低频关键词（模糊检索）
目标：≤30 行，查找速度 <3 秒

L2_Global_Facts (全局事实库)
├── 用户偏好（邮箱、时区、语言）
├── 环境配置（OS、工具、路径）
├── 项目状态（长期项目追踪）
└── 市场规则（财经分析准则）
目标：验证过的事实，不包含推测

L3_SOP (可执行流程库)
├── 复杂任务处理 SOP
├── 市场分析 SOP
├── 微信推送 SOP
└── ... (按需扩展)
目标：步骤化、可执行、包含坑点提示

L4_Raw_Sessions (原始会话归档)
├── 按日期归档原始对话
├── 长期存储，不常访问
└── 仅在需要回溯时查询
目标：完整保留，支持搜索
```

### 2. 核心设计原则

#### 无行动，不记忆
- 每条记忆必须对应具体的行动或决策
- 如果一条信息不能指导未来的行为，它就是噪声
- 记忆的价值 = 复用次数 × 决策质量提升

#### SOP 即代码
- 把踩过的坑变成标准化流程
- SOP 的价值 = 节省的注意力 - 维护成本
- 好的 SOP 让你不需要思考流程，只需要专注判断

#### Plan 四阶段流程
```
Phase 1: 探索 → Phase 2: 规划 → Phase 3: 执行 → Phase 4: 验证
```

#### 对抗性验证机制
完成后站在最挑剔的用户视角再找一遍问题

### 3. 实施步骤

```bash
# Step 1: 创建目录结构
cd ~/.hermes
mkdir -p memory/L3_sop memory/L4_raw_sessions

# Step 2: 备份原有记忆
cp memories/MEMORY.md memory/L4_raw_sessions/$(date +%Y-%m-%d)_original_memory_backup.md

# Step 3: 创建 L1 极简索引
# 参考: references/l1_insight_index_template.txt

# Step 4: 创建 L2 全局事实库
# 参考: references/l2_global_facts_template.txt

# Step 5: 创建核心 SOP (高频场景优先)
```

详细模板文件见 `references/` 目录。

---

## 第二部分：弹性层优化 (实战经验)

### 四阶段弹性建设框架

```
Phase 1: 基础能力增强 → Phase 2: 弹性层建设 → Phase 3: 监控告警 → Phase 4: 自愈闭环
     ↓                    ↓                     ↓                     ↓
  统一配置中心         熔断器/舱壁          Prometheus +          自动重启/
  健康检查标准化       限流/降级策略        Grafana 可视化        配置热重载
```

---

### Phase 1: 基础能力增强

#### 1. 统一配置中心

**目标**：将分散在 `extra` 中的超时、重试、限流配置统一管理

**实现模式** (在 `config.yaml` 顶部添加):
```yaml
resilience:
  # 全局超时配置
  timeouts:
    stream_stale: 600
    non_stream: 900
    provider_default: 480
    platform_default: 30

  # 全局重试策略
  retry:
    max_retries: 3
    base_delay: 2
    retry_on: [timeout, connection_error, 5xx]

  # 限流配置
  rate_limit:
    enabled: true
    global_requests_per_minute: 600

  # 熔断器配置
  circuit_breaker:
    enabled: true
    failure_threshold: 5
    recovery_timeout: 30

  # 健康检查配置
  health_check:
    enabled: true
    interval_seconds: 30
    unhealthy_threshold: 3

  # 舱壁隔离配置
  bulkhead:
    enabled: true
    max_concurrent_per_platform: 100
```

**分层原则** (优先级从低到高):
1. `resilience.*` = 全局默认值
2. `providers.*.extra` = 单 Provider 覆盖值
3. `platforms.*.extra` = 单平台覆盖值

#### 2. 健康检查标准化

**核心设计**:
- 四状态分级: `healthy` / `degraded` / `unhealthy` / `unknown`
- 基于历史记录的状态判断（防抖动）
- 统一输出格式 (Prometheus + CLI 彩色)

**标准检查项**:
- `config` - 配置文件存在且可解析
- `gateway` - 网关进程运行中
- `disk` - 磁盘空间 (<80% 健康, <90% 降级)
- `logs` - 近期错误数量 (<10 健康, <100 降级)
- `provider:*` - 所有 Provider 网络连通性
- `platform:*` - 所有消息平台状态

**状态判断算法**:
```python
def calculate_status(component, current_healthy):
    history = record_check(component, current_healthy)
    
    if not current_healthy:
        consecutive_fail = count_consecutive_failures(history)
        if consecutive_fail >= UNHEALTHY_THRESHOLD:
            return UNHEALTHY
        return DEGRADED
    
    recent_healthy = sum(history[-HEALTHY_THRESHOLD:])
    if recent_healthy >= HEALTHY_THRESHOLD:
        return HEALTHY
    return DEGRADED
```

**CLI 退出码约定**:
- `0` = 全部健康
- `1` = 部分降级
- `2` = 存在异常

**参考实现**: `~/.hermes/scripts/hermes_health_check.py`

**使用方法**:
```bash
python3 ~/.hermes/scripts/hermes_health_check.py
```

#### 3. Prometheus 指标采集基础

**设计原则**:
- 标准 Prometheus 格式 (`/metrics` 端点)
- 可扩展的收集器注册机制
- 低性能开销

**核心指标集**:
```python
# 基础指标
hermes_uptime_seconds              # 运行时间
hermes_python_gc_objects           # GC 对象数

# 资源指标
hermes_disk_total_bytes           # 总磁盘空间
hermes_disk_used_bytes            # 已用磁盘空间
hermes_disk_free_bytes            # 可用磁盘空间

# 业务指标
hermes_active_sessions            # 活跃会话数
hermes_cron_jobs_total            # Cron 任务总数
hermes_cron_jobs_enabled          # 已启用 Cron 任务数
```

**扩展收集器模式**:
```python
def register_collector(collector_func):
    """注册自定义指标收集器
    
    collector_func 可以是同步或异步函数
    在函数内部调用 add_metric() 添加指标
    """
```

**参考实现**: `~/.hermes/scripts/hermes_metrics_server.py`

**启动方式**:
```bash
python3 ~/.hermes/scripts/hermes_metrics_server.py 9090
```

---

### Phase 1 验证清单

实施后必须验证：

- [ ] `resilience` 配置区域已添加到 `config.yaml`
- [ ] 健康检查脚本可以正常运行并输出彩色报告
- [ ] 指标服务器可以启动，`/metrics` 端点有响应
- [ ] 网关重启后所有配置正常加载
- [ ] 生成完整的完成报告文档

---

## 典型问题解决方案库

### 问题 1: InvalidToken 每日宕机
**现象**: 每天约 3:23 AM 出现 InvalidToken 错误，触发级联故障

**解决方案**:
1. 更换 Volcengine Ark API key
2. 添加每日 token 验证 cron (3:25 AM)
3. 自动检测 token 失效后重启网关

**参考脚本**: `~/.hermes/scripts/monitor-token-status.py`

### 问题 2: 长消息发送"卡死"
**现象**: 发送长文本时平台限流，消息被拆分发送后卡死

**解决方案**:
```yaml
platforms:
  weixin:
    extra:
      send_chunk_delay_seconds: 0.8   # 从 0.35 增加到 0.8
      send_chunk_retries: 3            # 重试次数
```

### 问题 3: 长上下文超时
**现象**: GLM-5 等模型处理 13K token 需要 515 秒，但默认超时仅 180 秒

**解决方案**:
```python
# 上下文超时梯度缩放
if token_count > 50000:
    timeout = 900
elif token_count > 20000:
    timeout = 720
elif token_count > 10000:
    timeout = 600
elif token_count > 5000:
    timeout = 480
else:
    timeout = 180  # 默认
```

### 问题 4: Cronjob deliver 异步错误
**现象**: 使用 cronjob deliver 推送微信时出现 "Timeout context manager should be used inside a task"

**解决方案**:
```bash
# ❌ 错误方式：使用 deliver 字段
hermes cron add --deliver "wechat:xxx"

# ✅ 正确方式：在任务内部调用 send_message
# 让 Hermes 提取内容后自己推送，不依赖 deliver
```

---

## 交付物标准模板

每个阶段完成后必须生成：

1. **完成报告** (`PHASEX-COMPLETION-REPORT.md`)
   - 执行时间和状态
   - 已完成工作详细说明
   - 配置示例和代码片段
   - 验证结果表格
   - 下一阶段预览

2. **脚本文件** (`~/.hermes/scripts/*.py`)
   - 有完整的文档字符串
   - 可独立运行
   - 有命令行帮助信息

3. **配置变更记录**
   - 修改前 / 修改后对比
   - 回滚方法说明

---

## 参考资料

- [GenericAgent GitHub](https://github.com/lsdefine/GenericAgent)
- [Hermes Timeout & Rate Limit Optimization](./fix-hermes-message-rate-limit)
- [Hermes Gateway 消息平台配置与故障排查](./gateway-platform-config)
- [Hermes 配置诊断与模型切换修复](./provider-config-diagnosis)
