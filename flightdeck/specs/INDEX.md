# specs/ — INDEX

<!-- AUTO:specs -->
### 待启动（idea）
- [2026-06-03-preflight-silent-bump-nudge-design.md](2026-06-03-preflight-silent-bump-nudge-design.md) — idea — preflight 静默 bump 版本时新的 autonomy/commit 默认对升级者不可见；提议在静默 bump 的那一回合打一行一次性提示，指向对应 MIGRATION 段。由 sketch 提升
- [2026-06-03-status-spec-co-advance-design.md](2026-06-03-status-spec-co-advance-design.md) — idea — status 只推进正在执行的工件，spec 会停在 pending 而其 plan 已 done；提议 plan 翻 done/awaiting-review 时 confirm-gated 地 offer 推进其 implements 的 spec，或交由 landing 对账。由 sketch 提升
- [2026-06-03-structural-edit-guard-design.md](2026-06-03-structural-edit-guard-design.md) — idea — 抓 markdown 多行 Edit 的"静默结构丢失"（标题/区块被替换跨度吞掉，link/anchor 检查抓不到）；把结构检查并进 scriptable lint。动机=本会话 cockpit `## Next session` 标题被 reorder Edit 误删
- [v1x-deferred-ideas.md](v1x-deferred-ideas.md) — idea — v1.x 长期想法暂存（MCP server、boomerang 子 agent、continuance benchmark、spec 压缩、可选文件夹）；找到时机再促成 spec

### 进行中·完成（active·done）
- [2026-06-03-scriptable-mechanical-layer-design.md](2026-06-03-scriptable-mechanical-layer-design.md) — done — 机械层（INDEX 重生 / walkaround lint / AGENTS emit / 对账）脚本化降 token、模型只留判断；单语言 Python stdlib + markdown fallback 双轨 + rules scripts 开关 + 机械-判断分界 + 字母序；全 rollout 完成（index/init/bump/lint 四脚本）
- [2026-06-03-model-v4-folder-state-cockpit-design.md](2026-06-03-model-v4-folder-state-cockpit-design.md) — active — flightdeck 模型 v4——folder 7→5（sketches 并入 specs、删 debriefs）、workflow 状态 6→4（idea/active/done/scrapped）、cockpit 由 AI 全自动驱动（进行中区 AUTO 派生 + 下一步自动维护），并入 3.0
- [2026-06-03-incident-recurrence-autocount-design.md](2026-06-03-incident-recurrence-autocount-design.md) — active — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
<!-- /AUTO -->
