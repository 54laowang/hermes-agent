---
name: llama-cpp
description: 在 CPU、Apple Silicon 和消费级 GPU 上运行 LLM 推理，无需 NVIDIA 硬件。用于边缘部署、M1/M2/M3 Mac、AMD/Intel GPU 或 CUDA 不可用时。支持 GGUF 量化 (1.5-8 bit) 减少内存，CPU 上比 PyTorch 快 4-10 倍。
version: 1.1.0
author: Orchestra Research
license: MIT
dependencies: [llama-cpp-python]
metadata:
  hermes:
    tags: [Inference Serving, Llama.cpp, CPU Inference, Apple Silicon, Edge Deployment, GGUF, Quantization, Non-NVIDIA, AMD GPUs, Intel GPUs, Embedded]

---

# llama.cpp

Pure C/C++ LLM inference with minimal dependencies, optimized for CPUs and non-NVIDIA hardware.

## When to use llama.cpp

**Use llama.cpp when:**
- Running on CPU-only machines
- Deploying on Apple Silicon (M1/M2/M3/M4)
- Using AMD or Intel GPUs (no CUDA)
- Edge deployment (Raspberry Pi, embedded systems)
- Need simple deployment without Docker/Python

**Use TensorRT-LLM instead when:**
- Have NVIDIA GPUs (A100/H100)
- Need maximum throughput (100K+ tok/s)
- Running in datacenter with CUDA

**Use vLLM instead when:**
- Have NVIDIA GPUs
- Need Python-first API
- Want PagedAttention

## Quick start

### Installation

```bash
# macOS/Linux
brew install llama.cpp

# Or build from source
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# With Metal (Apple Silicon)
make LLAMA_METAL=1

# With CUDA (NVIDIA)
make LLAMA_CUDA=1

# With ROCm (AMD)
make LLAMA_HIP=1
```

#### ✅ 检查点：验证安装

```bash
# 1. 检查二进制文件
./llama-cli --version
./llama-server --version

# 2. 检查 Metal 支持（macOS）
./llama-cli --version | grep -i metal
# 应看到: "Metal support enabled"

# 3. 检查 CUDA 支持
./llama-cli --version | grep -i cuda
# 应看到: "CUDA support enabled"

# 4. 测试推理（使用小模型）
./llama-cli -m models/tinyllama-1.1b-chat.Q4_K_M.gguf -p "Hi" -n 10
```

#### ⚠️ 常见安装问题

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| **Metal 未启用** | `Metal support: disabled` | `make clean && make LLAMA_METAL=1` |
| **CUDA 未找到** | `cuda.h not found` | 安装 CUDA Toolkit，设置 `CUDA_PATH` |
| **ROCm 编译失败** | `hiprtc.h not found` | 安装 ROCm，设置 `ROCM_PATH` |
| **权限错误** | `Permission denied` | `chmod +x llama-cli llama-server` |

### Download model

```bash
# Download from HuggingFace (GGUF format)
huggingface-cli download \
    TheBloke/Llama-2-7B-Chat-GGUF \
    llama-2-7b-chat.Q4_K_M.gguf \
    --local-dir models/

# Or convert from HuggingFace
python convert_hf_to_gguf.py models/llama-2-7b-chat/
```

#### ✅ 检查点：验证模型

```bash
# 1. 检查文件完整性
ls -lh models/*.gguf
# 确认文件大小合理（7B Q4 约 4-5GB）

# 2. 验证 GGUF 格式
./llama-cli -m models/model.gguf --test-tokenizer
# 应输出: "tokenizer test passed"

# 3. 检查模型元数据
./llama-cli -m models/model.gguf --info
# 查看: context_length, embedding_length, n_layers

# 4. 内存估算（经验公式）
# 所需内存 ≈ 文件大小 × 1.5
# 例: 4.5GB GGUF → 需要 ~7GB RAM
```

#### ⚠️ 模型下载问题

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| **文件损坏** | `failed to load model` | 重新下载，校验 SHA256 |
| **内存不足** | `out of memory` | 使用更小量化（Q2/Q3） |
| **磁盘空间** | `no space left` | 清理空间，用 `df -h` 检查 |
| **网络超时** | `download timeout` | 使用镜像站或断点续传 |

### Run inference

```bash
# Simple chat
./llama-cli \
    -m models/llama-2-7b-chat.Q4_K_M.gguf \
    -p "Explain quantum computing" \
    -n 256  # Max tokens

# Interactive chat
./llama-cli \
    -m models/llama-2-7b-chat.Q4_K_M.gguf \
    --interactive
```

#### ✅ 检查点：推理验证

```bash
# 1. 测试基础推理
./llama-cli -m model.gguf -p "2+2=" -n 5 --temp 0
# 预期输出: "4" 或 "4."（确定性输出）

# 2. 检查生成速度
./llama-cli -m model.gguf -p "test" -n 100 --log-disable
# 关注: "eval time = X.XX ms / 100 tokens"
# 计算: tok/s = 100 / (X.XX / 1000)

# 3. 测试上下文长度
./llama-cli -m model.gguf -c 4096 -p "$(python -c 'print("x"*3000)')"
# 观察: 是否出现 context overflow 错误

# 4. 多轮对话测试
./llama-cli -m model.gguf --interactive --conversation
# 输入多轮对话，检查上下文是否保持
```

#### ⚠️ 推理异常处理

| 错误信息 | 原因 | 解决方案 |
|---------|------|----------|
| `memory allocation failed` | 内存不足 | 减小 `--batch-size` 或换小模型 |
| `context overflow` | 上下文超限 | 增大 `-c` 参数或使用长上下文模型 |
| `invalid token` | tokenizer 错误 | 重新下载模型或检查格式 |
| `segmentation fault` | 编译问题 | 重新编译 `make clean && make` |
| `unrecognized argument` | 版本过旧 | 更新到最新版本 |

### Server mode

```bash
# Start OpenAI-compatible server
./llama-server \
    -m models/llama-2-7b-chat.Q4_K_M.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    -ngl 32  # Offload 32 layers to GPU

# Client request
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-2-7b-chat",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

#### ✅ 检查点：服务器验证

```bash
# 1. 健康检查
curl http://localhost:8080/health
# 预期: {"status": "ok"}

# 2. 模型列表
curl http://localhost:8080/v1/models
# 预期: 返回已加载模型信息

# 3. 性能测试（ab 工具）
ab -n 100 -c 10 -p request.json -T application/json \
    http://localhost:8080/v1/chat/completions
# 关注: Requests per second, Time per request

# 4. 并发测试
for i in {1..10}; do
    curl -s http://localhost:8080/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{"model":"test","messages":[{"role":"user","content":"test"}]}' &
done
wait
# 观察: 是否所有请求都成功返回

# 5. 日志监控
tail -f /var/log/llama-server.log
# 检查: 错误日志、内存使用、请求统计
```

#### ⚠️ 服务器异常处理

| 错误现象 | 诊断步骤 | 解决方案 |
|---------|---------|---------|
| **端口被占用** | `lsof -i:8080` | 杀死占用进程或换端口 |
| **内存泄漏** | 监控 `top/htop` | 重启服务，设置定时重启 |
| **请求超时** | 检查 `--timeout` 参数 | 增大超时或优化模型 |
| **GPU 未使用** | `nvidia-smi` 监控 | 确认 `-ngl` 参数正确 |
| **响应乱码** | 检查编码设置 | 确保使用 UTF-8 |
| **并发崩溃** | 检查日志堆栈 | 减小 `--batch-size` |

## Quantization formats

### GGUF format overview

| Format | Bits | Size (7B) | Speed | Quality | Use Case |
|--------|------|-----------|-------|---------|----------|
| **Q4_K_M** | 4.5 | 4.1 GB | Fast | Good | **Recommended default** |
| Q4_K_S | 4.3 | 3.9 GB | Faster | Lower | Speed critical |
| Q5_K_M | 5.5 | 4.8 GB | Medium | Better | Quality critical |
| Q6_K | 6.5 | 5.5 GB | Slower | Best | Maximum quality |
| Q8_0 | 8.0 | 7.0 GB | Slow | Excellent | Minimal degradation |
| Q2_K | 2.5 | 2.7 GB | Fastest | Poor | Testing only |

### Choosing quantization

```bash
# General use (balanced)
Q4_K_M  # 4-bit, medium quality

# Maximum speed (more degradation)
Q2_K or Q3_K_M

# Maximum quality (slower)
Q6_K or Q8_0

# Very large models (70B, 405B)
Q3_K_M or Q4_K_S  # Lower bits to fit in memory
```

#### ✅ 检查点：量化选择验证

```bash
# 1. 内存约束检查
free -h  # Linux
vm_stat  # macOS
# 计算可用内存 vs 模型大小

# 2. 质量对比测试（同一提示词）
./llama-cli -m model-Q2_K.gguf -p "测试文本" -n 50 > output_q2.txt
./llama-cli -m model-Q4_K_M.gguf -p "测试文本" -n 50 > output_q4.txt
./llama-cli -m model-Q8_0.gguf -p "测试文本" -n 50 > output_q8.txt
diff output_q2.txt output_q8.txt

# 3. 速度基准测试
time ./llama-cli -m model-Q4_K_M.gguf -p "test" -n 100
time ./llama-cli -m model-Q8_0.gguf -p "test" -n 100
# 对比: tok/s 和 real time

# 4. 边界测试：极限内存情况
# 尝试加载刚好超过物理内存的模型
./llama-cli -m huge-model.Q4_K_M.gguf --mlock
# 观察: 是否使用 swap，性能下降多少
```

#### ⚠️ 量化选择陷阱

| 场景 | 错误选择 | 后果 | 正确选择 |
|------|---------|------|---------|
| **8GB RAM + 13B 模型** | Q8_0 | OOM 崩溃 | Q2_K 或 Q3_K_M |
| **质量敏感任务** | Q2_K | 输出质量差 | Q6_K 或 Q8_0 |
| **树莓派 4GB** | Q4_K_M | 内存不足 | Q2_K + swap |
| **生产环境** | Q2_K | 质量不稳定 | Q4_K_M + 监控 |

## Hardware acceleration

### Apple Silicon (Metal)

```bash
# Build with Metal
make LLAMA_METAL=1

# Run with GPU acceleration (automatic)
./llama-cli -m model.gguf -ngl 999  # Offload all layers

# Performance: M3 Max 40-60 tokens/sec (Llama 2-7B Q4_K_M)
```

#### ✅ 检查点：Metal 加速验证

```bash
# 1. 检查 Metal 编译
./llama-cli --version | grep -i metal
# 必须看到: "Metal support enabled"

# 2. 测试 GPU offload
./llama-cli -m model.gguf -ngl 0 -p "test" -n 100  # CPU only
./llama-cli -m model.gguf -ngl 999 -p "test" -n 100  # GPU
# 对比速度差异（应该快 2-5 倍）

# 3. 监控 GPU 使用（macOS）
sudo powermetrics --samplers gpu_power -i 1000
# 观察: GPU active ratio

# 4. 内存压力测试
./llama-cli -m model.gguf -ngl 999 --mlock
# 打开活动监视器，观察内存压力
# 警告: 黄色表示接近上限，红色表示危险
```

#### ⚠️ Metal 常见问题

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| **Metal 未编译** | `Metal support: disabled` | `make clean && make LLAMA_METAL=1` |
| **GPU 未使用** | 速度与 CPU 相同 | 确认 `-ngl` 参数 > 0 |
| **内存压力高** | 系统变慢 | 减小 `-ngl` 或使用更小量化 |
| **Metal 错误** | `MTLCreateSystemDefaultDevice failed` | 更新 macOS 或重启 |

### NVIDIA GPUs (CUDA)

```bash
# Build with CUDA
make LLAMA_CUDA=1

# Offload layers to GPU
./llama-cli -m model.gguf -ngl 35  # Offload 35/40 layers

# Hybrid CPU+GPU for large models
./llama-cli -m llama-70b.Q4_K_M.gguf -ngl 20  # GPU: 20 layers, CPU: rest
```

#### ✅ 检查点：CUDA 加速验证

```bash
# 1. 检查 CUDA 编译
./llama-cli --version | grep -i cuda
# 必须看到: "CUDA support enabled"

# 2. 验证 GPU 检测
nvidia-smi
./llama-cli -m model.gguf --verbose 2>&1 | grep -i cuda
# 应看到: "CUDA GPU 0: [GPU Name]"

# 3. 性能对比
./llama-cli -m model.gguf -ngl 0 -p "test" -n 100 2>&1 | grep "eval time"
./llama-cli -m model.gguf -ngl 999 -p "test" -n 100 2>&1 | grep "eval time"
# 应该有明显速度提升

# 4. GPU 内存监控
watch -n 1 nvidia-smi
# 观察: Memory-Usage, GPU-Util

# 5. 多 GPU 测试（如有）
./llama-cli -m model.gguf -ngl 999 -ts 0.5,0.5  # 双 GPU 均分
```

#### ⚠️ CUDA 常见问题

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| **CUDA 未编译** | `CUDA support: disabled` | `make clean && make LLAMA_CUDA=1` |
| **GPU 未检测到** | `no CUDA devices found` | 检查 `nvidia-smi`，更新驱动 |
| **内存不足** | `CUDA out of memory` | 减小 `-ngl` 或使用更小量化 |
| **版本不兼容** | `CUDA driver version insufficient` | 更新 CUDA Toolkit 和驱动 |

### AMD GPUs (ROCm)

```bash
# Build with ROCm
make LLAMA_HIP=1

# Run with AMD GPU
./llama-cli -m model.gguf -ngl 999
```

#### ✅ 检查点：ROCm 加速验证

```bash
# 1. 检查 ROCm 编译
./llama-cli --version | grep -i hip
# 必须看到: "HIP (ROCm) support enabled"

# 2. 验证 GPU 检测
rocminfo
./llama-cli -m model.gguf --verbose 2>&1 | grep -i hip

# 3. 性能测试
./llama-cli -m model.gguf -ngl 0 -p "test" -n 100
./llama-cli -m model.gguf -ngl 999 -p "test" -n 100

# 4. 监控 GPU
rocm-smi
# 或: watch -n 1 rocm-smi
```

## Common patterns

### Batch processing

```bash
# Process multiple prompts from file
cat prompts.txt | ./llama-cli \
    -m model.gguf \
    --batch-size 512 \
    -n 100
```

#### ✅ 检查点：批量处理验证

```bash
# 1. 准备测试数据
echo -e "问题1\n问题2\n问题3" > prompts.txt

# 2. 运行批量处理
cat prompts.txt | ./llama-cli -m model.gguf -n 50 --batch-size 128 > outputs.txt

# 3. 验证输出
wc -l prompts.txt outputs.txt
# 确保输出行数与输入匹配

# 4. 错误处理
cat prompts.txt | ./llama-cli -m model.gguf -n 50 2>&1 | tee batch.log
grep -i "error" batch.log
# 检查是否有失败请求

# 5. 性能优化
# 测试不同 batch size
for bs in 128 256 512 1024; do
    time cat prompts.txt | ./llama-cli -m model.gguf -n 100 --batch-size $bs > /dev/null
done
```

#### ⚠️ 批量处理陷阱

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| **内存溢出** | 批量时崩溃 | 减小 `--batch-size` |
| **输出错位** | 行数不匹配 | 检查输入格式，避免空行 |
| **性能下降** | 大批量反而慢 | 找最优 batch size（通常 256-512） |
| **部分失败** | 某些输出缺失 | 添加重试逻辑，记录失败项 |

### Constrained generation

```bash
# JSON output with grammar
./llama-cli \
    -m model.gguf \
    -p "Generate a person: " \
    --grammar-file grammars/json.gbnf

# Outputs valid JSON only
```

#### ✅ 检查点：约束生成验证

```bash
# 1. 测试 JSON grammar
./llama-cli -m model.gguf -p "Create JSON:" --grammar-file grammars/json.gbnf -n 100 | jq .
# 应该能被 jq 解析

# 2. 测试自定义 grammar
# 创建 test.gbnf
cat > grammars/test.gbnf << 'EOF'
root ::= "Hello" | "World"
EOF
./llama-cli -m model.gguf -p "" --grammar-file grammars/test.gbnf -n 10
# 应该只输出 "Hello" 或 "World"

# 3. 错误处理
./llama-cli -m model.gguf -p "test" --grammar-file nonexistent.gbnf 2>&1 | grep -i error
# 应该报错并退出

# 4. 性能影响测试
time ./llama-cli -m model.gguf -p "test" -n 100
time ./llama-cli -m model.gguf -p "test" --grammar-file grammars/json.gbnf -n 100
# 对比性能差异（通常慢 10-20%）
```

### Context size

```bash
# Increase context (default 512)
./llama-cli \
    -m model.gguf \
    -c 4096  # 4K context window

# Very long context (if model supports)
./llama-cli -m model.gguf -c 32768  # 32K context
```

#### ✅ 检查点：上下文长度验证

```bash
# 1. 测试默认上下文
./llama-cli -m model.gguf -p "$(python -c 'print("x"*500)')" -n 10
# 应该正常工作

# 2. 测试扩展上下文
./llama-cli -m model.gguf -c 4096 -p "$(python -c 'print("x"*3000)')" -n 10
# 观察是否支持

# 3. 超限测试
./llama-cli -m model.gguf -c 512 -p "$(python -c 'print("x"*1000)')" -n 10 2>&1
# 应该报错或截断

# 4. 内存影响
free -h
./llama-cli -m model.gguf -c 512 --verbose 2>&1 | grep memory
./llama-cli -m model.gguf -c 4096 --verbose 2>&1 | grep memory
# 观察内存分配差异
```

#### ⚠️ 上下文陷阱

| 场景 | 错误操作 | 后果 | 正确做法 |
|------|---------|------|---------|
| **超过模型限制** | `-c 32768` 在 4K 模型上 | 错误或质量下降 | 检查模型最大上下文 |
| **内存不足** | 大上下文 + 小内存 | OOM 崩溃 | 先计算所需内存 |
| **忽略 KV cache** | 只看模型大小 | 内存估算不准 | 总内存 = 模型 + KV cache |
| **长文档 RAG** | 一次塞入所有文档 | 上下文溢出 | 分段处理 + 摘要 |

## Performance benchmarks

### CPU performance (Llama 2-7B Q4_K_M)

| CPU | Threads | Speed | Cost |
|-----|---------|-------|------|
| Apple M3 Max | 16 | 50 tok/s | $0 (local) |
| AMD Ryzen 9 7950X | 32 | 35 tok/s | $0.50/hour |
| Intel i9-13900K | 32 | 30 tok/s | $0.40/hour |
| AWS c7i.16xlarge | 64 | 40 tok/s | $2.88/hour |

### GPU acceleration (Llama 2-7B Q4_K_M)

| GPU | Speed | vs CPU | Cost |
|-----|-------|--------|------|
| NVIDIA RTX 4090 | 120 tok/s | 3-4× | $0 (local) |
| NVIDIA A10 | 80 tok/s | 2-3× | $1.00/hour |
| AMD MI250 | 70 tok/s | 2× | $2.00/hour |
| Apple M3 Max (Metal) | 50 tok/s | ~Same | $0 (local) |

## Supported models

**LLaMA family**:
- Llama 2 (7B, 13B, 70B)
- Llama 3 (8B, 70B, 405B)
- Code Llama

**Mistral family**:
- Mistral 7B
- Mixtral 8x7B, 8x22B

**Other**:
- Falcon, BLOOM, GPT-J
- Phi-3, Gemma, Qwen
- LLaVA (vision), Whisper (audio)

**Find models**: https://huggingface.co/models?library=gguf

## Production deployment checklist

### ✅ 部署前检查

- [ ] **模型验证**: GGUF 文件完整性校验（SHA256）
- [ ] **内存预留**: 至少预留 20% 额外内存给系统
- [ ] **GPU 驱动**: CUDA/Metal/ROCm 版本兼容性
- [ ] **日志配置**: 设置日志轮转，避免磁盘满
- [ ] **超时设置**: 合理设置请求超时（默认 60s）
- [ ] **并发限制**: 设置最大并发请求（`--parallel`）
- [ ] **监控指标**: 配置 Prometheus/Grafana 监控

### ✅ 运行时监控

```bash
# 1. 基础监控
watch -n 1 'ps aux | grep llama'
watch -n 1 'nvidia-smi'  # NVIDIA
watch -n 1 'rocm-smi'    # AMD
watch -n 1 'sudo powermetrics --samplers gpu_power'  # macOS

# 2. 性能指标
curl http://localhost:8080/metrics  # Prometheus 格式
curl http://localhost:8080/stats    # JSON 统计

# 3. 日志监控
tail -f /var/log/llama-server.log | grep -E "error|warning"

# 4. 资源限制
# systemd service 示例
[Service]
MemoryMax=16G
CPUQuota=800%
TimeoutStopSec=30
Restart=on-failure
RestartSec=10
```

### ✅ 故障恢复

| 故障类型 | 检测方法 | 恢复策略 |
|---------|---------|---------|
| **内存泄漏** | 内存持续增长 | 定时重启（每日/每周） |
| **GPU 挂起** | GPU 利用率 0% | 自动重启服务 |
| **请求堆积** | 队列长度超限 | 拒绝新请求 + 告警 |
| **响应慢** | 延迟 > 阈值 | 降级到更小模型 |

## Troubleshooting guide

### 常见错误速查表

| 错误信息 | 分类 | 快速诊断 | 解决方案 |
|---------|------|---------|---------|
| `failed to load model` | 模型 | 文件损坏/路径错误 | 校验 SHA256，检查路径 |
| `out of memory` | 内存 | 内存不足 | 减小量化/batch/context |
| `context overflow` | 上下文 | 输入过长 | 增大 `-c` 或分段处理 |
| `CUDA error: out of memory` | GPU | GPU 显存不足 | 减小 `-ngl` 或换小模型 |
| `Metal device not found` | GPU | Metal 未启用 | 重编译 `LLAMA_METAL=1` |
| `invalid token id` | Tokenizer | 模型格式错误 | 重新下载/转换模型 |
| `segmentation fault` | 编译 | 编译问题 | `make clean && make` |
| `unrecognized argument` | 版本 | 版本过旧 | 更新到最新版 |

### 性能调优决策树

```
性能问题？
├─ 速度慢？
│  ├─ CPU 100%？ → 增加线程 (`-t`) 或换 GPU
│  ├─ GPU 0%？ → 检查 GPU offload (`-ngl`)
│  ├─ 内存交换？ → 减小模型/量化
│  └─ 批量慢？ → 调整 `--batch-size`
├─ 内存不足？
│  ├─ 单请求？ → 更小量化 (Q2/Q3)
│  ├─ 多请求？ → 减小并发数
│  └─ 大上下文？ → 减小 `-c`
└─ 质量差？
   ├─ 量化过低？ → 升级到 Q4/Q5
   ├─ 温度太高？ → 降低 `--temp`
   └─ 提示词差？ → 优化 prompt engineering
```

## References

- **[Quantization Guide](references/quantization.md)** - GGUF formats, conversion, quality comparison
- **[Server Deployment](references/server.md)** - API endpoints, Docker, monitoring
- **[Optimization](references/optimization.md)** - Performance tuning, hybrid CPU+GPU

## Resources

- **GitHub**: https://github.com/ggerganov/llama.cpp
- **Models**: https://huggingface.co/models?library=gguf
- **Discord**: https://discord.gg/llama-cpp

