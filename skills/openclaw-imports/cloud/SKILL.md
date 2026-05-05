---
name: cloud
description: >
  Browser Use Cloud 文档参考 — 浏览器自动化的托管 API 和 SDK。当用户需要帮助处理
  Cloud REST API (v2 或 v3)、browser-use-sdk (Python 或 TypeScript)、
  X-Browser-Use-API-Key 认证、云会话、浏览器配置文件、配置文件同步、CDP WebSocket 连接、
  隐身浏览器、住宅代理、CAPTCHA 处理、webhooks、工作区、skills 市场、liveUrl 流媒体、
  定价或集成模式（聊天 UI、子代理、向现有代理添加浏览器工具）时使用此 skill。
  也可用于 n8n/Make/Zapier 集成、云基础设施上的 Playwright/Puppeteer/Selenium
  或 1Password 保险库集成问题。不要用于开源 Python 库（Agent、Browser、Tools 配置）
  — 改用 open-source skill。
allowed-tools: Read
---

# Browser Use Cloud Reference

Reference docs for the Cloud REST API, SDKs, and integration patterns.
Read the relevant file based on what the user needs.

## API & Platform

| Topic | Read |
|-------|------|
| Setup, first task, pricing, FAQ | `references/quickstart.md` |
| v2 REST API: all 30 endpoints, cURL examples, schemas | `references/api-v2.md` |
| v3 BU Agent API: sessions, messages, files, workspaces | `references/api-v3.md` |
| Sessions, profiles, auth strategies, 1Password | `references/sessions.md` |
| CDP direct access, Playwright/Puppeteer/Selenium | `references/browser-api.md` |
| Proxies, webhooks, workspaces, skills, MCP, live view | `references/features.md` |
| Parallel, streaming, geo-scraping, tutorials | `references/patterns.md` |

## Integration Guides

| Topic | Read |
|-------|------|
| Building a chat interface with live browser view | `references/guides/chat-ui.md` |
| Using browser-use as a subagent (task in → result out) | `references/guides/subagent.md` |
| Adding browser-use tools to an existing agent | `references/guides/tools-integration.md` |

## Critical Notes

- Cloud API base URL: `https://api.browser-use.com/api/v2/` (v2) or `https://api.browser-use.com/api/v3` (v3)
- Auth header: `X-Browser-Use-API-Key: <key>`
- Get API key: https://cloud.browser-use.com/new-api-key
- Set env var: `BROWSER_USE_API_KEY=<key>`
- Cloud SDK: `uv pip install browser-use-sdk` (Python) or `npm install browser-use-sdk` (TypeScript)
- Python v2: `from browser_use_sdk import AsyncBrowserUse`
- Python v3: `from browser_use_sdk.v3 import AsyncBrowserUse`
- TypeScript v2: `import { BrowserUse } from "browser-use-sdk"`
- TypeScript v3: `import { BrowserUse } from "browser-use-sdk/v3"`
- CDP WebSocket: `wss://connect.browser-use.com?apiKey=KEY&proxyCountryCode=us`
