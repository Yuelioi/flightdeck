# specs/ — INDEX

<!-- AUTO:specs -->
### 待启动（idea）
- [2026-06-03-preflight-silent-bump-nudge-design.md](2026-06-03-preflight-silent-bump-nudge-design.md) — idea — preflight 静默 bump 版本时新的 autonomy/commit 默认对升级者不可见；提议在静默 bump 的那一回合打一行一次性提示，指向对应 MIGRATION 段。由 sketch 提升
- [2026-06-03-status-spec-co-advance-design.md](2026-06-03-status-spec-co-advance-design.md) — idea — status 只推进正在执行的工件，spec 会停在 pending 而其 plan 已 done；提议 plan 翻 done/awaiting-review 时 confirm-gated 地 offer 推进其 implements 的 spec，或交由 landing 对账。由 sketch 提升
- [2026-06-03-structural-edit-guard-design.md](2026-06-03-structural-edit-guard-design.md) — idea — 抓 markdown 多行 Edit 的"静默结构丢失"（标题/区块被替换跨度吞掉，link/anchor 检查抓不到）；把结构检查并进 scriptable lint。动机=本会话 cockpit `## Next session` 标题被 reorder Edit 误删
- [v1x-deferred-ideas.md](v1x-deferred-ideas.md) — idea — v1.x 长期想法暂存（MCP server、boomerang 子 agent、continuance benchmark、spec 压缩、可选文件夹）；找到时机再促成 spec

### 进行中·完成（active·done）
- [2026-06-03-incident-recurrence-autocount-design.md](2026-06-03-incident-recurrence-autocount-design.md) — active — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
<!-- /AUTO -->
