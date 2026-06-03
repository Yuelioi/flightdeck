# specs/ — INDEX

<!-- AUTO:specs -->
- [2026-06-03-incident-recurrence-autocount-design.md](2026-06-03-incident-recurrence-autocount-design.md) — active — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
- [2026-06-03-init-redesign-single-scaffold-design.md](2026-06-03-init-redesign-single-scaffold-design.md) — done — 删 minimal scaffold（留 scaffolds/full 目录名）；install 与 preflight 首次建档统一为 copy-the-scaffold（修注释丢失 + 消双流程）；加可跳过的演示式 onboarding 教程（样例 spec，结束清理）；init 加 git 检测提醒 + AGENTS.md opt-in 询问
- [2026-06-03-preflight-tri-review-remediation.md](2026-06-03-preflight-tri-review-remediation.md) — active — preflight 三方审核(claude/ds/gpt)19 项整改总账 spec（由同名 sketch 提升）；减重 A1/A3/A4 已并入 token-reduction spec，纠错 B + 措辞 C 在本 spec 跟踪；记录每项处置/done/deferred
- [2026-06-03-rules-simplification-design.md](2026-06-03-rules-simplification-design.md) — done — 溶解 rules.md 结构化 toggle 集（推断 / 默认+House Rules / 仅留 disabled_folders），House Rules 升为 flightdeck 局部权威覆盖并定职责边界，附 0 配置 when-to-land
- [2026-06-03-scriptable-mechanical-layer-design.md](2026-06-03-scriptable-mechanical-layer-design.md) — active — 机械层（INDEX 重生 / walkaround lint / AGENTS emit / 对账）脚本化降 token、模型只留判断；单语言 Python stdlib + markdown fallback 双轨 + rules scripts 开关 + 机械-判断分界 + 字母序；INDEX-regen PoC 已交付，余见 rollout plan
- [2026-06-03-token-reduction-design.md](2026-06-03-token-reduction-design.md) — active — 按 load 频率降 skill token + 治流程过长：常驻 SKILL 优先、dedup-to-canonical / defer-to-companion / script-owns / summarize；不改行为、保双轨 fallback。第一批已落（SKILL 瘦身 + 5 漂移修），余下分批
<!-- /AUTO -->
