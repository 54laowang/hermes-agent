#!/usr/bin/env python3
"""
统一时间感知模块 - 合并监察者模式和 Context Soul Injector 的时间逻辑

优先级：pre_llm_call 第二顺位（cache_aware_hook 之后）

功能：
1. 基础时间感知（所有任务）：北京时间
2. 财经时间锚定（财经任务）：美东时间 + 市场状态 + 数据源优先级
3. 搜索上下文注入（所有任务）：从 search.md 加载

Token 优化：
- 非财经任务：~200 tokens
- 财经任务：~800 tokens
- 相比原方案节省 60%+
"""
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# 配置
HERMES_DIR = Path.home() / ".hermes"
SEARCH_MD = HERMES_DIR / "search.md"

# 财经关键词（触发完整时间锚定）
FINANCE_KEYWORDS = [
    "美股", "A股", "港股", "欧股",
    "道琼斯", "纳斯达克", "标普", "S&P",
    "上证", "深证", "创业板", "科创",
    "财联社", "Trading Economics", "MarketWatch",
    "Fed", "美联储", "央行", "降息", "加息",
    "财报", "季报", "年报", "业绩",
    "GDP", "CPI", "PMI", "非农"
]


def get_beijing_time() -> datetime:
    """获取北京时间（UTC+8）"""
    return datetime.utcnow() + timedelta(hours=8)


def get_us_eastern_time(beijing_time: datetime) -> datetime:
    """
    将北京时间转换为美东时间
    
    夏令时（3月第二个周日-11月第一个周日）：UTC-4
    冬令时：UTC-5
    
    简化处理：北京时间 - 12小时（夏令时）
    """
    return beijing_time - timedelta(hours=12)


def get_market_status(us_eastern_time: datetime) -> tuple:
    """
    判断美股市场状态
    
    返回：(状态, 数据类型建议)
    """
    hour = us_eastern_time.hour
    
    if hour < 9.5:
        return "盘前", "昨日收盘 + 盘前期货"
    elif 9.5 <= hour < 16:
        return "盘中", "实时行情（不推荐分析）"
    elif 16 <= hour < 18:
        return "收盘", "当日收盘数据"
    else:
        return "盘后", "收评/盘后数据"


def detect_finance_task(user_message: str) -> bool:
    """检测是否为财经任务"""
    return any(kw in user_message for kw in FINANCE_KEYWORDS)


def load_search_context() -> str:
    """
    加载搜索上下文（从 search.md）
    
    返回：最近 5 条搜索记录
    """
    if not SEARCH_MD.exists():
        return ""
    
    try:
        with open(SEARCH_MD, "r", encoding="utf-8") as f:
            lines = f.readlines()[-5:]  # 最近 5 条
            return "".join(lines).strip()
    except Exception:
        return ""


def generate_time_context(user_message: str) -> dict:
    """
    生成统一时间上下文
    
    返回：
    {
        "beijing_time": str,
        "is_finance": bool,
        "us_eastern_time": str (仅财经),
        "market_status": str (仅财经),
        "data_type": str (仅财经),
        "search_context": str
    }
    """
    beijing_time = get_beijing_time()
    is_finance = detect_finance_task(user_message)
    
    context = {
        "beijing_time": beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
        "is_finance": is_finance,
        "search_context": load_search_context()
    }
    
    if is_finance:
        us_eastern_time = get_us_eastern_time(beijing_time)
        market_status, data_type = get_market_status(us_eastern_time)
        
        context.update({
            "us_eastern_time": us_eastern_time.strftime('%Y-%m-%d %H:%M:%S'),
            "market_status": market_status,
            "data_type": data_type
        })
    
    return context


def format_output(context: dict) -> str:
    """格式化输出给 Hermes"""
    lines = []
    
    # 基础时间（所有任务）
    lines.append(f"⏰ 当前时间：{context['beijing_time']} (北京时间)")
    
    # 财经时间锚定
    if context['is_finance']:
        lines.append("")
        lines.append("=" * 60)
        lines.append("📊 财经时间锚定")
        lines.append("=" * 60)
        lines.append(f"🇺🇸 美东时间：{context['us_eastern_time']}")
        lines.append(f"📈 市场状态：{context['market_status']}")
        lines.append(f"📋 数据类型：{context['data_type']}")
        lines.append("")
        lines.append("✅ 数据源优先级：")
        lines.append("  P0: Trading Economics > Yahoo Finance > MarketWatch")
        lines.append("  P1: CNBC > Reuters > Bloomberg")
    
    # 搜索上下文
    if context['search_context']:
        lines.append("")
        lines.append("📚 最近搜索：")
        lines.append(context['search_context'])
    
    return "\n".join(lines)


def main(user_message: str = ""):
    """Hook 入口"""
    context = generate_time_context(user_message)
    output = format_output(context)
    print(output)


if __name__ == "__main__":
    # 从命令行参数获取用户消息
    user_message = sys.argv[1] if len(sys.argv) > 1 else ""
    main(user_message)
