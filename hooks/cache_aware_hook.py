#!/usr/bin/env python3
"""
缓存感知 Hook
在 LLM 调用前构建缓存优化的 Prompt

触发时机：pre_llm_call
功能：
1. 使用缓存感知构建器优化 Prompt
2. 注入缓存元数据到上下文
3. 追踪缓存命中率
"""

import os
import sys
import json
import logging
from datetime import datetime

# 添加 Hermes core 到路径
sys.path.insert(0, os.path.expanduser("~/.hermes/core"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CacheAwareHook')


def main():
    """主入口"""
    # 读取上下文
    context_file = os.environ.get("HERMES_CONTEXT_FILE")
    if not context_file:
        logger.warning("No HERMES_CONTEXT_FILE env var")
        return
    
    try:
        with open(context_file, 'r') as f:
            context = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to read context: {e}")
        return
    
    # 导入缓存感知构建器
    try:
        from cache_aware_prompt import get_cache_aware_builder
    except ImportError:
        logger.warning("cache_aware_prompt module not found, skipping cache optimization")
        return
    
    builder = get_cache_aware_builder()
    
    # 构建缓存优化的 Prompt
    user_input = context.get("user_input", "")
    dynamic_context = context.get("dynamic_context", "")
    session_history = context.get("session_history", [])
    tools_context = context.get("tools_context", "")
    
    # 构建并优化
    messages, cache_metadata = builder.build_prompt(
        user_input,
        dynamic_context,
        session_history,
        tools_context
    )
    
    # 注入缓存元数据到上下文
    context["cache_metadata"] = cache_metadata
    context["optimized_messages"] = messages
    
    # 预估节省成本
    if cache_metadata.get("cacheable_tokens_estimate", 0) > 0:
        estimated_savings = (
            cache_metadata["cacheable_tokens_estimate"] / 1000
        ) * 0.01  # $0.01 per 1K tokens
        context["estimated_cache_savings"] = estimated_savings
        
        logger.info(
            f"Cache optimization: {cache_metadata['estimated_hit_rate']*100:.1f}% "
            f"estimated hit rate, ${estimated_savings:.4f} potential savings"
        )
    
    # 写回上下文
    try:
        with open(context_file, 'w') as f:
            json.dump(context, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Failed to write context: {e}")


if __name__ == "__main__":
    main()
