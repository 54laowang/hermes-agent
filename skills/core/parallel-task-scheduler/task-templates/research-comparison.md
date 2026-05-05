# 多方案对比调研模板

## 使用方法
```
并行执行以下 {{n}} 个调研任务：

{% for topic in topics %}
任务 {{loop.index}}：深度调研 {{topic}} 的架构、优缺点、适用场景
{% endfor %}

输出要求：
1. 每个方案用表格对比核心指标
2. 交叉验证不同方案之间的矛盾点
3. 最后给出选型建议和适用场景
```

## 常用调研主题
- 向量数据库：Pinecone / Chroma / Weaviate / Milvus
- Agent 框架：OpenClaw / Claude Code / AutoGPT / LangGraph
- 推理后端：vLLM / Text Generation Inference / Ollama
- 多模态模型：GPT-4o / Claude 3 Opus / Gemini Pro
