<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0 收尾——所有核心工作（model-v4 / scriptable lint / preflight 瘦身+launch 拆分 / `/flightdeck:new`）已实施 + dogfood + land 归档完毕；**只剩发布**（version-bump + CHANGELOG + marketplace + tag + 合并 main），外加可选的 reload 后 live 复验。

## 进行中

- [2026-06-03-incident-recurrence-autocount-design.md](flightdeck/specs/2026-06-03-incident-recurrence-autocount-design.md) — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证

## 下一步

- **发布 3.0**：version-bump + CHANGELOG（写 `/flightdeck:launch`、`/flightdeck:new` 两条 + preflight deckless 行为变更 + 本会话两 bugfix）+ marketplace + tag + 合并 → main（见 [checklists/version-bump.md](flightdeck/checklists/version-bump.md)）。
- （可选，非阻塞）sync+reload 后 live 复验：用修后 build 跑 `/flightdeck:new` 各 kind（重点 `doc` 恒-dateless、`chart→references/`）验 fallback 修复；并验 `incident-recurrence`（唯一留 active）的 dogfood 行为 + model-v4 残项（idea→active 实地翻转带动 `## 进行中`、landing 写两区）。

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

To author a new deck artifact (spec/plan/incident/checklist/chart), run `/flightdeck:new` — it stamps the correct frontmatter + naming and regenerates INDEX/cockpit. Don't hand-write deck artifacts or place them under `docs/`.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
