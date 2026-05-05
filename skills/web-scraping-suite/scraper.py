#!/usr/bin/env python3.11
"""
Web Scraping Suite - 四重爬虫快速调用脚本
用法: python3.11 scraper.py [jina|crawl4ai|scrapling|camoufox URL
"""
import sys
import asyncio
import requests

def jina_reader(url):
    """Jina Reader - 最快的单页抓取"""
    print("="*50)
    print(f"[Jina Reader] 抓取: " + url)
    print("="*50)
    resp = requests.get(f"https://r.jina.ai/{url}", timeout=30)
    print(resp.text[:3000])
    if len(resp.text) > 3000:
        print(f"\n... (截断，总长度 {len(resp.text)} 字符)")

async def crawl4ai_fetch(url):
    """Crawl4AI - 深度抓取"""
    from crawl4ai import AsyncWebCrawler
    print("="*50)
    print(f"[Crawl4AI] 深度抓取: " + url)
    print("="*50)
    async with AsyncWebCrawler(verbose=False) as crawler:
        result = await crawler.arun(url=url, bypass_cache=True)
        print(result.markdown[:3000])
        if len(result.markdown) > 3000:
            print(f"\n... (截断，总长度 {len(result.markdown)} 字符)")

def scrapling_fetch(url):
    """Scrapling - 反爬绕过"""
    from scrapling import StealthyFetcher
    print("="*50)
    print(f"[Scrapling] 反爬抓取: " + url)
    print("="*50)
    fetcher = StealthyFetcher()
    resp = fetcher.fetch(url, timeout=30)
    print(f"状态码: {resp.status}")
    print(f"页面长度: {len(resp.html_content)}")
    print("\n标题:", resp.html_content[:1000])

async def camoufox_fetch(url):
    """CamouFox - 隐身浏览器"""
    from camoufox import AsyncCamoufox
    print("="*50)
    print(f"[CamouFox] 隐身浏览抓取: " + url)
    print("="*50)
    async with AsyncCamoufox(headless=True, rotate_fingerprint=True) as browser:
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        title = await page.title()
        content = await page.content()
        print(f"页面标题: {title}")
        print(f"页面长度: {len(content)}")
        print("\n内容预览:\n" + content[:1000])

def print_help():
    print("""
Web Scraping Suite - 四重爬虫工具箱
用法: python3.11 scraper.py <工具> <URL>
工具:
  jina      - Jina Reader (最快，单页)
  crawl4ai  - Crawl4AI (深度抓取，Markdown)
  scrapling - Scrapling (反爬绕过)
  camoufox  - CamouFox (隐身浏览器)
示例:
  python3.11 scraper.py jina https://example.com
    """)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_help()
        sys.exit(1)
    
    tool = sys.argv[1]
    url = sys.argv[2]
    
    try:
        if tool == "jina":
            jina_reader(url)
        elif tool == "crawl4ai":
            asyncio.run(crawl4ai_fetch(url))
        elif tool == "scrapling":
            scrapling_fetch(url)
        elif tool == "camoufox":
            asyncio.run(camoufox_fetch(url))
        else:
            print(f"未知工具: {tool}")
            print_help()
    except Exception as e:
        print(f"错误: {e}")
