# specs/ — INDEX

<!-- AUTO:specs -->
### 待启动（idea）
- [2026-06-03-status-spec-co-advance-design.md](2026-06-03-status-spec-co-advance-design.md) — idea — status 只推进正在执行的工件，spec 会停在 pending 而其 plan 已 done；提议 plan 翻 done/awaiting-review 时 confirm-gated 地 offer 推进其 implements 的 spec，或交由 landing 对账。由 sketch 提升
- [2026-06-03-structural-edit-guard-design.md](2026-06-03-structural-edit-guard-design.md) — idea — 抓 markdown 多行 Edit 的"静默结构丢失"（标题/区块被替换跨度吞掉，link/anchor 检查抓不到）；把结构检查并进 scriptable lint。动机=本会话 cockpit `## Next session` 标题被 reorder Edit 误删
- [scrapped-artifact-disposition.md](scrapped-artifact-disposition.md) — idea — scrapped 现状=留 specs/「已否决」分组当墓碑、root 计数却排除它(→计数≠可见行)、Land Routine 不归档；多处 docstring/SKILL 说「scrapped never appears」与代码 ### 已否决 分组矛盾。重定 scrapped 处置(倾向直接删、git 留史，符合果断删减) vs archive vs 留墓碑，并修计数≠可见行 + 文档↔代码漂移
- [v1x-deferred-ideas.md](v1x-deferred-ideas.md) — idea — v1.x 长期想法暂存（MCP server、boomerang 子 agent、continuance benchmark、spec 压缩、可选文件夹）；找到时机再促成 spec

### 进行中·完成（active·done）
- [2026-06-05-incident-error-library-lifecycle.md](2026-06-05-incident-error-library-lifecycle.md) — active — 错误库生命周期完善(方向C之Spec1)：生=正文加可grep的 ## Signature 块(symptom/error_type/where/trigger)+分节标准化；用=recurrence sweep 加确定性签名指纹精确匹配去重(脚本算,AI只管模糊层)；死=resolved_by + status:obsolete 从活跃路由退出(物理删/归档交 scrapped-disposition 统一定)。Signature 放正文+退役缩集→省token；B(两层manifest)留作超大deck未来升级备注
- [2026-06-03-incident-recurrence-autocount-design.md](2026-06-03-incident-recurrence-autocount-design.md) — active — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
<!-- /AUTO -->
