<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0 完善到位（**不急发布、避免迁移债**）。**核心卖点=随时可关、下次 preflight 干净接手、上下文不丢（红线）**。de-scope 主线已收口（基线见 `docs/descope-baseline.md`）；当前在清 skills 文档失实（A 组已修，遗留 B1/B2）+ Backlog 消化。

## 进行中

- [2026-06-10-skills-doc-drift-cleanup.md](flightdeck/specs/2026-06-10-skills-doc-drift-cleanup.md) — 新模型全量 review skills/ 发现 6 组失实/矛盾：root INDEX 残留引用、hook 相位4 已实证但仍标 pending、preflight 补偿路径残留违反纯读零写、version/walkaround 权责矛盾、pre-3.0 向后兼容文案残留违反 descope 基线、new 的 kind 清单与 chart 命名不一致；另 3 项设计层疑点（applies_to tags vs paths、landing SKILL 超重、断锚点）

## 下一步

- **进行中：skills 文档失实清扫**（[2026-06-10-skills-doc-drift-cleanup.md](flightdeck/specs/2026-06-10-skills-doc-drift-cleanup.md)）——A1–A6 + B3 部分已修毕待签收；B1（applies_to tags vs paths）留待单独讨论、B2（landing SKILL 瘦身）后置。
- **Backlog**：#1 写门负例（纯 prompt 低风险）、#7 恢复回归测试（待恢复模型稳定再做，首个核心价值行为测试）。

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

To author a new deck artifact (spec / plan / incident / checklist / reference / doc), run `/flightdeck:new` — it stamps the correct frontmatter + naming and regenerates INDEX/cockpit. Don't hand-write deck artifacts or hand-derive their paths.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
