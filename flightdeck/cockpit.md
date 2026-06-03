# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-03 by 月离 (rules.md 3.0 简化 designed (spec + two tri-review rounds, disposition complete) AND implemented on branch `flightdeck-3.0-rules-simplification` — 21 files: toggle 集溶解为推断+House Rules、删 disabled_gates、autonomy 默认全开、迁移、when-to-land；本 deck 已自迁移到 3.0)
**Active focus**: flightdeck 3.0 (rules.md 简化) 已在分支上落地实现；**未做行为级 dogfood**（本会话加载的是缓存里的旧 2.3 skill），待按 3.0 reload 插件后验证，再发布 + 合并。

## Next session

1. **行为 dogfood 3.0**（reload/重装插件到 3.0 后）：scratch deck 上验 git/emit 推断、`### Autonomy overrides` 标准句覆盖、2.3→3.0 迁移改写、when-to-land signal 1/2；跑 walkaround 不报假阳性。
2. **发布 3.0** [checklists/version-bump.md](checklists/version-bump.md)（marketplace + tag + 同步插件缓存），然后合并分支 `flightdeck-3.0-rules-simplification` → main。
3. 仍开放：INDEX-row `—` 分隔符冲突 [incidents/index-row-summary-delimiter.md](incidents/index-row-summary-delimiter.md)（3.0 未触及）；spec §8 的 no-git HISTORY 格式 + scaffold 门实测。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.

---

**Cockpit hygiene** (skill: workflow):
- **80 lines hard ceiling.** Cockpit is operational, not archival. History lives in `git log` / `landed/HISTORY.md`.
- `Last updated` bumps ONLY when: Next session changes / Active focus shifts / a major task completes / an artifact lands.
- Finished items leave `Next session`; they are not logged in cockpit.
- Artifact state is tracked via `status:` frontmatter + the folder `INDEX.md` files, not here.
