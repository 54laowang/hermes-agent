#!/usr/bin/env python3
"""
股价智能缓存系统
功能：自动缓存股价数据，根据交易时间智能更新
作者：Hermes Agent
创建时间：2026-04-30
"""

import json
import os
import urllib.request
from datetime import datetime, time, timedelta
from pathlib import Path

# 缓存目录
CACHE_DIR = Path.home() / ".hermes" / "stock_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_trading_status():
    """
    判断当前交易状态
    返回：'pre_market'（盘前）、'trading'（交易中）、'after_market'（盘后）、'holiday'（节假日）
    """
    now = datetime.now()
    current_time = now.time()
    
    # 简化版：工作日判断（不考虑节假日）
    if now.weekday() >= 5:  # 周六、周日
        return 'holiday'
    
    # 交易时间判断
    market_open = time(9, 30)
    market_close = time(15, 0)
    
    if current_time < market_open:
        return 'pre_market'
    elif market_open <= current_time <= market_close:
        return 'trading'
    else:
        return 'after_market'

def get_cache_validity():
    """
    根据交易状态返回缓存有效期（秒）
    """
    status = get_trading_status()
    
    if status == 'trading':
        return 300  # 盘中：5分钟
    elif status == 'after_market':
        return 86400  # 盘后：24小时
    else:
        return 86400  # 盘前/节假日：24小时

def get_cache_path(stock_code):
    """获取缓存文件路径"""
    return CACHE_DIR / f"{stock_code}.json"

def load_cache(stock_code):
    """
    加载缓存数据
    返回：缓存数据（如果有效）或 None
    """
    cache_file = get_cache_path(stock_code)
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # 检查缓存是否过期
        cache_time = datetime.fromisoformat(cache_data['cache_time'])
        validity_seconds = get_cache_validity()
        
        if (datetime.now() - cache_time).total_seconds() < validity_seconds:
            return cache_data['data']
        else:
            return None
    except Exception as e:
        print(f"缓存读取失败: {e}")
        return None

def save_cache(stock_code, data):
    """保存缓存数据"""
    cache_file = get_cache_path(stock_code)
    
    cache_data = {
        "stock_code": stock_code,
        "cache_time": datetime.now().isoformat(),
        "trading_status": get_trading_status(),
        "data": data
    }
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"缓存保存失败: {e}")
        return False

def get_sina_stock_quote(stock_code):
    """使用新浪财经 API 获取股票行情"""
    # 判断市场
    if stock_code.startswith('6'):
        market = 'sh'
    else:
        market = 'sz'
    
    url = f"http://hq.sinajs.cn/list={market}{stock_code}"
    
    req = urllib.request.Request(url)
    req.add_header('Referer', 'http://finance.sina.com.cn')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            # 新浪返回 GBK 编码
            content = response.read().decode('gbk')
            
            # 解析数据
            if 'hq_str_' in content:
                data_str = content.split('"')[1]
                fields = data_str.split(',')
                
                if len(fields) >= 32:
                    return {
                        "name": fields[0],
                        "open": float(fields[1]),
                        "last_close": float(fields[2]),
                        "price": float(fields[3]),
                        "high": float(fields[4]),
                        "low": float(fields[5]),
                        "volume": int(fields[8]),
                        "amount": float(fields[9]),
                        "date": fields[30],
                        "time": fields[31],
                        "source": "新浪财经",
                        "fetch_time": datetime.now().isoformat()
                    }
            return None
    except Exception as e:
        print(f"新浪API获取失败: {e}")
        return None

def get_stock_price(stock_code, force_update=False):
    """
    获取股票价格（带缓存）
    
    参数：
        stock_code: 股票代码（如 '300536'）
        force_update: 是否强制更新（忽略缓存）
    
    返回：
        股价数据字典
    """
    # 1. 检查缓存
    if not force_update:
        cache_data = load_cache(stock_code)
        if cache_data:
            print(f"✅ 使用缓存数据（{stock_code}）")
            cache_data['from_cache'] = True
            return cache_data
    
    # 2. 获取新数据
    print(f"🔄 获取最新数据（{stock_code}）...")
    data = get_sina_stock_quote(stock_code)
    
    if data:
        # 3. 保存缓存
        save_cache(stock_code, data)
        data['from_cache'] = False
        return data
    else:
        # 4. 如果获取失败，尝试使用过期缓存
        cache_data = load_cache(stock_code)
        if cache_data:
            print(f"⚠️ API获取失败，使用过期缓存")
            cache_data['from_cache'] = True
            cache_data['cache_expired'] = True
            return cache_data
        else:
            return {"error": "无法获取股价数据"}

def batch_get_stock_prices(stock_codes, force_update=False):
    """
    批量获取股票价格
    
    参数：
        stock_codes: 股票代码列表
        force_update: 是否强制更新
    
    返回：
        {股票代码: 股价数据} 字典
    """
    results = {}
    
    for code in stock_codes:
        results[code] = get_stock_price(code, force_update)
    
    return results

def clear_cache(stock_code=None):
    """
    清除缓存
    
    参数：
        stock_code: 股票代码（None表示清除所有缓存）
    """
    if stock_code:
        cache_file = get_cache_path(stock_code)
        if cache_file.exists():
            cache_file.unlink()
            print(f"✅ 已清除缓存：{stock_code}")
    else:
        for cache_file in CACHE_DIR.glob("*.json"):
            cache_file.unlink()
        print(f"✅ 已清除所有缓存")

def show_cache_status():
    """显示缓存状态"""
    print(f"\n📊 缓存目录：{CACHE_DIR}")
    print(f"🕐 当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 交易状态：{get_trading_status()}")
    print(f"⏱️  缓存有效期：{get_cache_validity()}秒\n")
    
    cache_files = list(CACHE_DIR.glob("*.json"))
    
    if cache_files:
        print("缓存文件列表：")
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                cache_time = datetime.fromisoformat(data['cache_time'])
                age = datetime.now() - cache_time
                
                print(f"  - {data['stock_code']}: {data['data']['name']} "
                      f"{data['data']['price']:.2f}元 "
                      f"(缓存时间: {cache_time.strftime('%H:%M:%S')}, "
                      f"距今: {int(age.total_seconds()/60)}分钟前)")
            except Exception as e:
                print(f"  - {cache_file.name}: 读取失败 ({e})")
    else:
        print("暂无缓存文件")

# 示例用法
if __name__ == "__main__":
    # 显示缓存状态
    show_cache_status()
    
    # 获取单只股票价格
    print("\n" + "="*50)
    print("获取农尚环境（300536）股价：")
    print("="*50)
    data = get_stock_price('300536')
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # 批量获取
    print("\n" + "="*50)
    print("批量获取股价：")
    print("="*50)
    results = batch_get_stock_prices(['300536', '002388'])
    for code, data in results.items():
        print(f"\n{code}: {data.get('name', 'N/A')} - {data.get('price', 'N/A')}元")
