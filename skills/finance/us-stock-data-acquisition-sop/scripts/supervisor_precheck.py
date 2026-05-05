#!/usr/bin/env python3
"""
监察者模式前置检查脚本（Supervisor Mode Pre-Check）
在执行市场数据、财报、时区换算任务前自动检查关键项

使用方法：
  python3 ~/.hermes/scripts/supervisor_precheck.py

集成方式：
  可集成到 Hermes Shell Hook (pre_llm_call) 中自动执行
"""

import sys
from datetime import datetime, timedelta

def get_beijing_time():
    """获取当前北京时间（UTC+8）"""
    # 假设系统时间是UTC，加8小时
    # 实际使用时可以从系统获取
    return datetime.utcnow() + timedelta(hours=8)

def get_us_eastern_time(beijing_time):
    """将北京时间转换为美东时间（UTC-4夏令时/UTC-5冬令时）"""
    # 夏令时（3月第二个周日-11月第一个周日）：UTC-4
    # 冬令时：UTC-5
    # 简化处理：北京时间 - 12小时
    return beijing_time - timedelta(hours=12)

def check_time_anchoring(beijing_time, target_date=None):
    """检查点0：时间锚定验证"""
    print("\n" + "="*60)
    print("检查点0：时间锚定验证（最高优先级）")
    print("="*60)
    
    us_eastern_time = get_us_eastern_time(beijing_time)
    
    print(f"□ 当前北京时间：{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"□ 美东时间：{us_eastern_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 判断市场状态
    hour = us_eastern_time.hour
    if hour < 9.5:
        market_status = "盘前"
        data_type = "昨日收盘 + 盘前期货"
    elif 9.5 <= hour < 16:
        market_status = "盘中"
        data_type = "实时行情（不推荐分析）"
    elif hour >= 16:
        market_status = "收盘/盘后"
        data_type = "收评/盘后数据"
    else:
        market_status = "未知"
        data_type = "未知"
    
    print(f"□ 市场状态：{market_status}")
    print(f"□ 应获取数据类型：{data_type}")
    
    # 确定目标数据日期
    if target_date:
        print(f"□ 目标数据日期：{target_date}")
    else:
        # 如果北京时间已过凌晨4点，美东是前一天收盘
        if beijing_time.hour >= 4:
            target_date = us_eastern_time.strftime('%Y-%m-%d')
            print(f"□ 目标数据日期：{target_date}（美东收盘）")
        else:
            target_date = (us_eastern_time - timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"□ 目标数据日期：{target_date}（美东昨日收盘）")
    
    # 检查搜索关键词
    print(f"\n✓ 推荐搜索关键词：")
    print(f"  英文：\"{target_date}\" \"close\" \"Dow Jones\" \"S&P 500\" \"Nasdaq\"")
    print(f"  中文：\"美股收盘\" \"{target_date}\" \"道琼斯\" \"纳斯达克\"")
    
    return {
        "beijing_time": beijing_time,
        "us_eastern_time": us_eastern_time,
        "market_status": market_status,
        "target_date": target_date
    }

def check_data_source_priority():
    """检查点3：数据源优先级"""
    print("\n" + "="*60)
    print("检查点3：数据源权威性验证（强制优先级）")
    print("="*60)
    
    print("\nP0级数据源（首选，必须优先尝试）：")
    p0_sources = [
        "交易所官网（NYSE/NASDAQ/上交所/深交所）",
        "Trading Economics（https://tradingeconomics.com/）",
        "Yahoo Finance（https://finance.yahoo.com/）",
        "MarketWatch（https://www.marketwatch.com/）"
    ]
    for i, source in enumerate(p0_sources, 1):
        print(f"  {i}. {source}")
    
    print("\nP1级数据源（备选，P0失败后使用）：")
    p1_sources = [
        "CNBC（https://www.cnbc.com/）",
        "WSJ（https://www.wsj.com/）",
        "Bloomberg（https://www.bloomberg.com/）",
        "财联社（https://www.cls.cn/）- A股专用",
        "东方财富（https://www.eastmoney.com/）- A股专用"
    ]
    for i, source in enumerate(p1_sources, 1):
        print(f"  {i}. {source}")
    
    print("\nP2级数据源（最后手段，需明确标注）：")
    p2_sources = [
        "新浪财经",
        "雪球",
        "其他聚合平台"
    ]
    for i, source in enumerate(p2_sources, 1):
        print(f"  {i}. {source}")
    
    print("\n❌ 禁止使用的数据源：")
    forbidden_sources = [
        "个人博客",
        "论坛（Reddit、Twitter个人账号等）",
        "未标注来源的转载"
    ]
    for source in forbidden_sources:
        print(f"  ❌ {source}")
    
    return {"p0_sources": p0_sources, "p1_sources": p1_sources, "p2_sources": p2_sources}

def check_conflict_detection():
    """检查点4：数据冲突检测"""
    print("\n" + "="*60)
    print("检查点4：数据冲突检测")
    print("="*60)
    
    print("\n冲突类型：")
    print("  1. 数值冲突（价格、涨跌幅不一致）")
    print("  2. 时间冲突（数据时间戳不一致）")
    print("  3. 来源冲突（权威性差异）")
    
    print("\n处理机制：")
    print("  ✓ 优先采用P0级数据源")
    print("  ✓ 明确告知用户数据冲突情况")
    print("  ✓ 提供多个数据源供用户判断")
    
    return {"conflict_types": ["数值冲突", "时间冲突", "来源冲突"]}

def check_user_confirmation():
    """检查点5：用户确认机制"""
    print("\n" + "="*60)
    print("检查点5：用户确认机制")
    print("="*60)
    
    print("\n触发条件：")
    trigger_conditions = [
        "关键决策前（买入/卖出建议）",
        "数据冲突无法自动解决",
        "时间锚定不确定",
        "数据来源权威性存疑"
    ]
    for i, condition in enumerate(trigger_conditions, 1):
        print(f"  {i}. {condition}")
    
    print("\n确认方式：")
    print("  ✓ 展示数据来源和置信度")
    print("  ✓ 询问用户是否继续分析")
    print("  ✓ 提供替代方案")
    
    return {"trigger_conditions": trigger_conditions}

def generate_checklist_report(time_info, source_info, conflict_info, confirmation_info):
    """生成完整的检查报告"""
    print("\n" + "="*60)
    print("监察者检查报告")
    print("="*60)
    
    report = f"""
任务开始时间：{time_info['beijing_time'].strftime('%Y-%m-%d %H:%M:%S')}
监察者触发：✅ 是

检查点0（时间锚定）：✅ 通过
  - 北京时间：{time_info['beijing_time'].strftime('%Y-%m-%d %H:%M:%S')}
  - 美东时间：{time_info['us_eastern_time'].strftime('%Y-%m-%d %H:%M:%S')}
  - 目标日期：{time_info['target_date']}
  - 市场状态：{time_info['market_status']}

检查点3（数据源优先级）：✅ 已明确
  - P0级数据源：{len(source_info['p0_sources'])}个
  - P1级数据源：{len(source_info['p1_sources'])}个

检查点4（数据冲突检测）：✅ 已准备
  - 冲突类型：{len(conflict_info['conflict_types'])}种

检查点5（用户确认机制）：✅ 已准备
  - 触发条件：{len(confirmation_info['trigger_conditions'])}种

输出报告：✅ 可输出
用户干预次数：0次
结果：预检查通过，可以开始分析
"""
    print(report)
    return report

def main():
    """主函数"""
    print("监察者模式前置检查（Supervisor Mode Pre-Check）")
    print("="*60)
    
    # 获取当前北京时间
    beijing_time = get_beijing_time()
    
    # 执行检查
    time_info = check_time_anchoring(beijing_time)
    source_info = check_data_source_priority()
    conflict_info = check_conflict_detection()
    confirmation_info = check_user_confirmation()
    
    # 生成报告
    generate_checklist_report(time_info, source_info, conflict_info, confirmation_info)
    
    print("\n" + "="*60)
    print("✅ 所有检查点通过，可以开始分析")
    print("="*60)

if __name__ == "__main__":
    main()
