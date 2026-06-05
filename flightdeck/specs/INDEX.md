# specs/ — INDEX

<!-- AUTO:specs -->
### 待启动（idea）
- [2026-06-03-preflight-silent-bump-nudge-design.md](2026-06-03-preflight-silent-bump-nudge-design.md) — idea — preflight 静默 bump 版本时新的 autonomy/commit 默认对升级者不可见；提议在静默 bump 的那一回合打一行一次性提示，指向对应 MIGRATION 段。由 sketch 提升
- [2026-06-03-status-spec-co-advance-design.md](2026-06-03-status-spec-co-advance-design.md) — idea — status 只推进正在执行的工件，spec 会停在 pending 而其 plan 已 done；提议 plan 翻 done/awaiting-review 时 confirm-gated 地 offer 推进其 implements 的 spec，或交由 landing 对账。由 sketch 提升
- [2026-06-03-structural-edit-guard-design.md](2026-06-03-structural-edit-guard-design.md) — idea — 抓 markdown 多行 Edit 的"静默结构丢失"（标题/区块被替换跨度吞掉，link/anchor 检查抓不到）；把结构检查并进 scriptable lint。动机=本会话 cockpit `## Next session` 标题被 reorder Edit 误删
- [v1x-deferred-ideas.md](v1x-deferred-ideas.md) — idea — v1.x 长期想法暂存（MCP server、boomerang 子 agent、continuance benchmark、spec 压缩、可选文件夹）；找到时机再促成 spec

### 进行中·完成（active·done）
- [2026-06-05-model-coherence-mainstream-naming-design.md](2026-06-05-model-coherence-mainstream-naming-design.md) — active — 彻底理清 flightdeck 生命周期+文件夹模型并立主流命名铁律——status⟂location正交(landed非状态/done≠归档)、done翻转 end-of-turn 防抖接力landing(方案A出厂默认/push先问)、归档判据确定性结构边(脚本可算/不靠AI正文)、航空名只留指令与仪式、数据模型全主流(charts→references、landed→archive、新增docs/)、knowledge可嵌套撑大型项目、status自动翻转收成唯一权威表；并入3.0
- [2026-06-04-preflight-slim-launch-split-design.md](2026-06-04-preflight-slim-launch-split-design.md) — active — preflight 太重（兼管初始化/检查/接管）——拆出 `/flightdeck:launch` 接管首次创建 deck，preflight 瘦成纯接管（读 cockpit/INDEX → 报下一步 + 精简 catalog 预热 + 被动一行 git 提示），删掉与 walkaround 重复的检查（结构性迁移探测/catalog 状态体检/cockpit 漂移/阻塞式 reconcile）。并入 3.0
- [2026-06-04-new-artifact-authoring-convention-design.md](2026-06-04-new-artifact-authoring-convention-design.md) — active — 撰写新 deck 工件每次交"推导税"（按-kind frontmatter / 命名 dateless-vs-dated / 记得 regen——位置实践中已可靠落对 flightdeck/specs/，不是痛点）。选定方向 B：新增 /flightdeck:new skill 包 flightdeck_new.py，确定性盖按-kind frontmatter + 命名 + 落目录 + regen，覆盖全部工件种类，shell-first 交接；SKILL=权威撰写契约文档面（含方向 A）。发现靠常驻指针（protocol 节 + emit-agents-md 模板行 + skill description）——目的是让 agent 用入口而非手搓，不防 docs/。并入 3.0
- [2026-06-04-command-simplify-scriptable-version-design.md](2026-06-04-command-simplify-scriptable-version-design.md) — active — 自治面收敛到底(真删 self-invoke/disabled_folders/run-scripts(转推断)/status:auto-land 开关，换好默认+推断+判断) + 智能 landing(智能归档替 auto-land) + commit 翻默认(本地自调/push 先问，override 保留) + 版本/布局判定脚本化(verdict 源自 MIGRATION frontmatter) + 版本职责单一归属(preflight 只读上报/landing 只读守卫/walkaround 唯一写) + preflight 删 Branch-0；并入 3.0
- [2026-06-03-scriptable-mechanical-layer-design.md](2026-06-03-scriptable-mechanical-layer-design.md) — done — 机械层（INDEX 重生 / walkaround lint / AGENTS emit / 对账）脚本化降 token、模型只留判断；单语言 Python stdlib + markdown fallback 双轨 + rules scripts 开关 + 机械-判断分界 + 字母序；全 rollout 完成（index/init/bump/lint 四脚本）
- [2026-06-03-model-v4-folder-state-cockpit-design.md](2026-06-03-model-v4-folder-state-cockpit-design.md) — active — flightdeck 模型 v4——folder 7→5（sketches 并入 specs、删 debriefs）、workflow 状态 6→4（idea/active/done/scrapped）、cockpit 由 AI 全自动驱动（进行中区 AUTO 派生 + 下一步自动维护），并入 3.0
- [2026-06-03-incident-recurrence-autocount-design.md](2026-06-03-incident-recurrence-autocount-design.md) — active — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
<!-- /AUTO -->
