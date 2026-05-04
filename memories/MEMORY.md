用户 fork 的 Hermes Agent 仓库地址：https://github.com/54laowang/hermes-agent（注意仓库名是 hermes-agent 不是 hermes）
§
Holographic Memory 引入时间：2026-03-29（commit 44b7df409），核心技术：HRR (Holographic Reduced Representations) + Phase Encoding + Trust Scoring + Entity Resolution。位于 plugins/memory/holographic/，含 9 个 fact_store 操作。
§
self-improving 概念首次提出：2026-03-06（commit 2dbbedc05），从 "grows with you" 演变为 "self-improving AI agent"。自进化系统实现在 hermes-agent/agent/self_evolution_*.py，共 6 个模块。