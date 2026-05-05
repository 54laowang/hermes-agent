# Embedding 相似度检测技术细节

## 模型选择

**推荐模型**: `all-MiniLM-L6-v2`

| 模型 | 大小 | 速度 | 质量 | 用途 |
|------|------|------|------|------|
| all-MiniLM-L6-v2 | 80MB | 快 | 中 | 英文通用（推荐）|
| paraphrase-multilingual-MiniLM-L12-v2 | 420MB | 中 | 高 | 多语言支持 |
| all-mpnet-base-v2 | 420MB | 慢 | 最高 | 高精度需求 |

## 性能数据

- **编码速度**: ~50 texts/s (CPU)
- **内存占用**: ~50MB (模型)
- **缓存命中**: ~80% (二次查询)
- **相似度阈值**: 0.7-0.8（推荐）

## 缓存机制

```python
# 缓存位置
~/.hermes/embedding_cache/{fact_id}.npy

# 更新缓存
es = EmbeddingSimilarity()
updated = es.update_embeddings_cache(batch_size=50)
```

## 常见问题

### 1. 模型下载慢

```bash
# 使用国内镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### 2. 内存不足

```python
# 使用更小的模型
es = EmbeddingSimilarity(model_name="all-MiniLM-L6-v2")
```

### 3. 相似度不准确

```python
# 调整阈值
similar = es.find_similar_cases_semantic(case_id, threshold=0.6)  # 降低阈值
```

## 与 Jaccard 对比

| 方法 | 优点 | 缺点 |
|------|------|------|
| Jaccard | 快速、无依赖 | 仅关键词匹配 |
| Embedding | 语义理解 | 需要模型、慢 |

**推荐**: Embedding 用于关键场景，Jaccard 用于快速筛选。
