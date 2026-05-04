用户 fork 的 Hermes Agent 仓库地址：https://github.com/54laowang/hermes-agent（注意仓库名是 hermes-agent 不是 hermes）
§
Holographic Memory 引入时间：2026-03-29（commit 44b7df409），核心技术：HRR (Holographic Reduced Representations) + Phase Encoding + Trust Scoring + Entity Resolution。位于 plugins/memory/holographic/，含 9 个 fact_store 操作。
§
self-improving 概念首次提出：2026-03-06（commit 2dbbedc05），从 "grows with you" 演变为 "self-improving AI agent"。自进化系统实现在 hermes-agent/agent/self_evolution_*.py，共 6 个模块。
§
用户通过询问"RTK启用了吗"确认了 RTK (Rust Token Killer) 的使用状态。RTK 已安装并运行良好：版本 0.36.0，已节省 263.4K tokens (83.1%)。RTK 配置在 HERMES.md 中，所有 git 命令均使用 rtk 前缀。
§
Hook 冲突已解决：创建了 unified_time_awareness.py 统一模块，合并了 supervisor-precheck 和 time-sense-injector 的时间感知逻辑。财经任务注入完整时间锚定 (~800 tokens)，非财经任务仅注入基础时间 (~200 tokens)，节省 60%+ tokens。其他冲突修复：删除重复 CLAUDE.md、添加 *.db 到 .gitignore、忽略 skills/.archive/ 目录。
§
学习了 14 个 Claude Skill 编写模式（Bilgin Ibryam 系列）。核心洞见：1) 触发是生死关口 - description 必须包含触发词和排除条款；2) 约束太死是普遍错误 - 用 Explain-the-Why 替代 MUST/NEVER；3) Gotchas 价值最高 - 只能从真实失败案例提取；4) 渐进式披露省 Token - SKILL.md < 500 行；5) 模板+示例组合 - 骨架+肉。当前 Hermes Skills 现状：503 个，97% 缺排除条款，99.4% 缺 Gotchas。