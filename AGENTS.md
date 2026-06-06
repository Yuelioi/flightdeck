<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。**核心卖点=随时可关对话、下次 preflight 干净接手、上下文不丢**；载体 checkpoint + soft-landing + 本轮 HISTORY 移除/gitignored-deck 接缝 已实施，待 resync 部署 + live 复验。

## 进行中

- `specs/2026-06-06-end-of-turn-soft-landing.md` — soft-landing（end-of-turn 知识增量→自动落盘+「已保存」标记，不 commit、不归档，landing 幂等）
- `plans/2026-06-06-soft-landing-rollout.md` — 把 soft-landing 铺进 exit-ritual/landing/protocol/status + dogfood session-flow 的逐文件实施

## 下一步

- **resync + reload**：两批 skill 改动同步进 plugin 缓存重载——① soft-landing + checkpoint ② 本轮 HISTORY 移除 + gitignored-deck git-mode 接缝——live 生效。
- **live 复验**：① soft-landing + checkpoint 子路径；② 真·gitignored deck 上跑 landing（不写 HISTORY、`mv` 不报错、INDEX 一次到位）。通过 → 批准 soft-landing spec+plan done → 归档。

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

To author a new deck artifact (spec/plan/incident/checklist/chart), run `/flightdeck:new` — it stamps the correct frontmatter + naming and regenerates INDEX/cockpit. Don't hand-write deck artifacts or place them under `docs/`.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
