<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0 alpha 试用期——**v3.0.0-alpha.1 已发布（main 上 commit+tag，待维护者 push）**，邀请早期试用者收集反馈；alpha 期间仍可破坏性调整，正式 3.0.0 完善到位再发。**核心卖点=随时可关、下次 preflight 干净接手、上下文不丢（红线）**。de-scope 基线见 `docs/descope-baseline.md`。

## 进行中

None.

## 下一步

- **alpha 发布收尾（维护者手动）**：已在 main 上，执行 `git push origin main --follow-tags` 即对外可装 v3.0.0-alpha.1；push 后 `git ls-remote --tags origin` 确认 tag 到位。本仓库 AI 绝不 push。
- **skills 失实清扫已全量收口 ✅**（处置纪要见 [archive/specs/2026-06-10-skills-doc-drift-cleanup.md](flightdeck/archive/specs/2026-06-10-skills-doc-drift-cleanup.md)）。欠账=同步 cache 后新会话跑一次完整 landing 验证（verify 标记会自动浮出）。
- **Backlog（下一步从这里挑）**：消化 alpha 试用反馈、#1 写门负例（纯 prompt 低风险）、#7 恢复回归测试（待恢复模型稳定再做，首个核心价值行为测试）。

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

To author a new deck artifact (spec / plan / incident / checklist / reference / doc), run `/flightdeck:new` — it stamps the correct frontmatter + naming and regenerates INDEX/cockpit. Don't hand-write deck artifacts or hand-derive their paths.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
