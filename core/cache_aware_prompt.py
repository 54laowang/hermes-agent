#!/usr/bin/env python3
"""
缓存感知 Prompt 构建器
优化 DeepSeek API 的 prefix caching 命中率

核心原理：
1. 固定前缀 → 最高优先级缓存
2. 半固定内容 → 次优先级缓存
3. 动态内容 → 最后，不缓存
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger('CacheAwarePrompt')


@dataclass
class CacheStats:
    """缓存统计"""
    total_requests: int = 0
    total_input_tokens: int = 0
    total_cached_tokens: int = 0
    total_cost_saved: float = 0.0
    
    @property
    def avg_hit_rate(self) -> float:
        if self.total_input_tokens == 0:
            return 0.0
        return self.total_cached_tokens / self.total_input_tokens


class CacheAwarePromptBuilder:
    """缓存感知的 Prompt 构建器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.expanduser("~/.hermes/cache_aware_config.json")
        self.config = self._load_config()
        
        # 构建固定前缀
        self.fixed_prefix = self._build_fixed_prefix()
        self.fixed_prefix_hash = self._hash_content(self.fixed_prefix)
        
        # 半固定内容（用户偏好、环境配置）
        self.semi_fixed = self._build_semi_fixed()
        self.semi_fixed_hash = self._hash_content(self.semi_fixed)
        
        # 缓存统计
        self.stats = CacheStats()
        self.stats_file = os.path.expanduser("~/.hermes/cache_stats.json")
        self._load_stats()
    
    def _load_config(self) -> dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "fixed_prefix_enabled": True,
            "semi_fixed_update_interval": 3600,  # 1小时更新一次
            "cost_per_1k_tokens": 0.01  # DeepSeek V4 价格
        }
    
    def _build_fixed_prefix(self) -> str:
        """构建完全固定的前缀（最易缓存）
        
        注意：内容来源于 ~/.hermes/HERMES.md
        """
        hermes_md = os.path.expanduser("~/.hermes/HERMES.md")
        if os.path.exists(hermes_md):
            try:
                with open(hermes_md, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取核心部分（前 2000 字符）
                    return content[:2000]
            except Exception as e:
                logger.warning(f"Failed to read HERMES.md: {e}")
        
        # 降级：硬编码的前缀
        return """你是 Hermes Agent，专业的 AI 助手。

## 核心能力
- 📊 市场分析 & 财务研判
- 🤖 AI科技 & 前沿项目追踪
- 📚 知识管理 & Obsidian自动化
- 🎯 任务编排 & 多Agent协作

## 工作准则
1. **时效性优先**：财经和科技新闻必须确认时间戳
2. **准确性至上**：市值、股价等数据必须验证来源和日期
3. **系统化思维**：将零散信息整合成结构化知识
4. **持续进化**：不断学习新工具和方法论，提升能力边界

## 输出规范
- 使用简体中文回复
- 数据驱动，严谨细致
- 提供深度分析和专业解读
- 结构化呈现（表格、列表、分级标题）

## 核心约束
- 数据准确性零容忍
- 时间锚定优先级最高
- 禁止用过时数据凑数
- 禁止推测当事实"""

    def _build_semi_fixed(self) -> str:
        """构建半固定内容（偶尔更新）"""
        # 从 memory tool 加载用户偏好
        user_prefs = self._load_user_preferences()
        
        semi_fixed = "## 用户偏好\n"
        if user_prefs:
            for key, value in user_prefs.items():
                semi_fixed += f"- {key}: {value}\n"
        else:
            semi_fixed += "- 默认配置\n"
        
        # 从 fact_store 加载关键事实
        key_facts = self._load_key_facts()
        if key_facts:
            semi_fixed += "\n## 关键事实\n"
            for fact in key_facts[:5]:  # 最多 5 条
                semi_fixed += f"- {fact}\n"
        
        return semi_fixed
    
    def _load_user_preferences(self) -> dict:
        """加载用户偏好"""
        # TODO: 从 memory tool 或 fact_store 加载
        memory_file = os.path.expanduser("~/.hermes/memory_store.db")
        if not os.path.exists(memory_file):
            return {}
        
        try:
            import sqlite3
            conn = sqlite3.connect(memory_file)
            cursor = conn.cursor()
            
            # 查询用户偏好
            cursor.execute("""
                SELECT content FROM memories 
                WHERE category = 'user_pref' 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            
            prefs = {}
            for row in cursor.fetchall():
                content = row[0]
                # 简单解析
                if "偏好" in content or "preference" in content.lower():
                    prefs[len(prefs)] = content[:100]
            
            conn.close()
            return prefs
        except Exception as e:
            logger.warning(f"Failed to load user preferences: {e}")
            return {}
    
    def _load_key_facts(self) -> List[str]:
        """加载关键事实"""
        # TODO: 从 fact_store 加载
        return [
            "用户偏好中文界面",
            "关注全球财经、A股、AI科技",
            "使用 macOS 系统"
        ]
    
    def _hash_content(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
    
    def build_prompt(
        self,
        user_input: str,
        dynamic_context: str = "",
        session_history: List[Dict] = None,
        tools_context: str = ""
    ) -> List[Dict[str, str]]:
        """构建缓存友好的 Prompt
        
        Args:
            user_input: 用户输入
            dynamic_context: 动态上下文（时间、市场状态等）
            session_history: 会话历史
            tools_context: 工具上下文
        
        Returns:
            缓存优化的 messages 列表
        """
        messages = []
        
        # 1. 固定前缀（最高优先级缓存）
        if self.config.get("fixed_prefix_enabled", True):
            messages.append({
                "role": "system",
                "content": self.fixed_prefix,
                "_cache_priority": "highest"  # 标记缓存优先级
            })
        
        # 2. 半固定内容（次优先级缓存）
        messages.append({
            "role": "system",
            "content": self.semi_fixed,
            "_cache_priority": "high"
        })
        
        # 3. 工具上下文（较固定）
        if tools_context:
            messages.append({
                "role": "system",
                "content": tools_context,
                "_cache_priority": "medium"
            })
        
        # 4. 动态上下文（每次可能不同）
        if dynamic_context:
            messages.append({
                "role": "system",
                "content": dynamic_context,
                "_cache_priority": "low"
            })
        
        # 5. 会话历史（逐步增加，部分缓存）
        if session_history:
            for msg in session_history[-10:]:  # 最近 10 轮
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                    "_cache_priority": "medium"
                })
        
        # 6. 用户输入（不缓存）
        messages.append({
            "role": "user",
            "content": user_input,
            "_cache_priority": "none"
        })
        
        return messages
    
    def optimize_for_deepseek(
        self,
        messages: List[Dict[str, str]]
    ) -> tuple[List[Dict[str, str]], dict]:
        """优化为 DeepSeek API 格式
        
        DeepSeek V4 的 prefix caching 规则：
        - 前面的 messages 更容易被缓存
        - 相同的 system prompt + context = 高命中率
        
        Returns:
            (优化后的 messages, 缓存元数据)
        """
        # 移除缓存优先级标记（DeepSeek API 不需要）
        optimized_messages = []
        cache_metadata = {
            "total_tokens_estimate": 0,
            "cacheable_tokens_estimate": 0,
            "cache_zones": []
        }
        
        current_zone_start = 0
        
        for i, msg in enumerate(messages):
            clean_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            optimized_messages.append(clean_msg)
            
            # 估算 tokens（简化：1 token ≈ 4 chars）
            content_tokens = len(msg["content"]) // 4
            cache_metadata["total_tokens_estimate"] += content_tokens
            
            # 记录缓存区域
            priority = msg.get("_cache_priority", "none")
            if priority in ["highest", "high", "medium"]:
                cache_metadata["cacheable_tokens_estimate"] += content_tokens
                
                if i == 0 or messages[i-1].get("_cache_priority") != priority:
                    current_zone_start = i
                
                if i == len(messages) - 1 or messages[i+1].get("_cache_priority") != priority:
                    cache_metadata["cache_zones"].append({
                        "start": current_zone_start,
                        "end": i,
                        "priority": priority,
                        "tokens": content_tokens
                    })
        
        # 计算预估命中率
        if cache_metadata["total_tokens_estimate"] > 0:
            cache_metadata["estimated_hit_rate"] = (
                cache_metadata["cacheable_tokens_estimate"] / 
                cache_metadata["total_tokens_estimate"]
            )
        else:
            cache_metadata["estimated_hit_rate"] = 0.0
        
        return optimized_messages, cache_metadata
    
    def track_request(
        self,
        input_tokens: int,
        cached_tokens: int,
        model: str = "deepseek-v4-pro"
    ):
        """追踪请求的缓存统计"""
        self.stats.total_requests += 1
        self.stats.total_input_tokens += input_tokens
        self.stats.total_cached_tokens += cached_tokens
        
        # 计算节省成本
        cost_per_1k = self.config.get("cost_per_1k_tokens", 0.01)
        saved = (cached_tokens / 1000) * cost_per_1k
        self.stats.total_cost_saved += saved
        
        # 持久化
        self._save_stats()
        
        logger.info(
            f"Cache hit: {cached_tokens}/{input_tokens} tokens "
            f"({cached_tokens/input_tokens*100:.1f}%), "
            f"saved ${saved:.4f}"
        )
    
    def _load_stats(self):
        """加载统计"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    self.stats.total_requests = data.get("total_requests", 0)
                    self.stats.total_input_tokens = data.get("total_input_tokens", 0)
                    self.stats.total_cached_tokens = data.get("total_cached_tokens", 0)
                    self.stats.total_cost_saved = data.get("total_cost_saved", 0.0)
            except Exception as e:
                logger.warning(f"Failed to load cache stats: {e}")
    
    def _save_stats(self):
        """保存统计"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump({
                    "total_requests": self.stats.total_requests,
                    "total_input_tokens": self.stats.total_input_tokens,
                    "total_cached_tokens": self.stats.total_cached_tokens,
                    "total_cost_saved": self.stats.total_cost_saved,
                    "avg_hit_rate": self.stats.avg_hit_rate,
                    "updated_at": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache stats: {e}")
    
    def get_stats_report(self) -> str:
        """获取统计报告"""
        if self.stats.total_requests == 0:
            return "📊 暂无缓存统计数据"
        
        report = f"""
📊 缓存统计报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**总请求数**: {self.stats.total_requests}
**总输入 tokens**: {self.stats.total_input_tokens:,}
**缓存命中 tokens**: {self.stats.total_cached_tokens:,}
**平均命中率**: {self.stats.avg_hit_rate*100:.1f}%
**节省成本**: ${self.stats.total_cost_saved:.2f}

**固定前缀哈希**: {self.fixed_prefix_hash}
**半固定内容哈希**: {self.semi_fixed_hash}

💡 优化建议：
"""
        
        if self.stats.avg_hit_rate < 0.5:
            report += "- 命中率偏低，建议检查固定前缀是否稳定\n"
        elif self.stats.avg_hit_rate < 0.8:
            report += "- 命中率中等，可优化半固定内容更新频率\n"
        else:
            report += "- ✅ 命中率优秀，缓存策略有效\n"
        
        return report
    
    def update_semi_fixed(self):
        """更新半固定内容"""
        self.semi_fixed = self._build_semi_fixed()
        self.semi_fixed_hash = self._hash_content(self.semi_fixed)
        logger.info(f"Semi-fixed content updated: {self.semi_fixed_hash}")


# 全局单例
_cache_aware_builder = None

def get_cache_aware_builder() -> CacheAwarePromptBuilder:
    """获取全局缓存感知构建器"""
    global _cache_aware_builder
    if _cache_aware_builder is None:
        _cache_aware_builder = CacheAwarePromptBuilder()
    return _cache_aware_builder


# 便捷函数
def build_optimized_prompt(
    user_input: str,
    dynamic_context: str = "",
    session_history: List[Dict] = None,
    tools_context: str = ""
) -> tuple[List[Dict[str, str]], dict]:
    """构建优化后的 Prompt（便捷函数）"""
    builder = get_cache_aware_builder()
    messages = builder.build_prompt(
        user_input,
        dynamic_context,
        session_history,
        tools_context
    )
    return builder.optimize_for_deepseek(messages)


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)
    
    builder = CacheAwarePromptBuilder()
    
    # 构建测试 Prompt
    messages, metadata = build_optimized_prompt(
        user_input="分析 A 股市场今日走势",
        dynamic_context="当前时间：2026-05-04 19:40\n市场状态：收盘",
        tools_context="可用工具：web_search, read_file, terminal",
        session_history=[
            {"role": "user", "content": "之前的对话..."},
            {"role": "assistant", "content": "之前的回复..."}
        ]
    )
    
    print(f"Messages: {len(messages)}")
    print(f"Cache metadata: {json.dumps(metadata, indent=2, ensure_ascii=False)}")
    print("\n" + builder.get_stats_report())
