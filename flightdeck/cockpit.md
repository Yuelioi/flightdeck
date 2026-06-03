# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-03 by 月离 (分支 `flightdeck-3.0-rules-simplification` 现含三块、全部 code-complete 且 unpushed：①3.0 rules.md 简化 ②init 重做+单一 scaffold ③README 瘦身+抽出 docs/；本次 land 另记 [incidents/scaffold-ships-verbatim.md](incidents/scaffold-ships-verbatim.md) 教训。仍未做 runtime dogfood)
**Active focus**: flightdeck 3.0 + init 重做 + README/docs 三块都在分支上 code-complete、未 push；待 reload 插件做 runtime dogfood，再发布 + 合并 main。

## Next session

1. **行为 dogfood（reload/重装插件后）**：①3.0——git/emit 推断、`### Autonomy overrides` 标准句覆盖、2.3→3.0 迁移改写、when-to-land signal 1/2、walkaround 不报假阳性；②init 重做——干净目录跑首次建档全程（git 检测+copy 全布局+interview+AGENTS 询问+onboarding 教程+cleanup）。
2. **发布 3.0** [checklists/version-bump.md](checklists/version-bump.md)（marketplace + tag + 同步插件缓存），然后合并分支 → main。
3. 仍开放：INDEX-row `—` 分隔符冲突 [incidents/index-row-summary-delimiter.md](incidents/index-row-summary-delimiter.md)；spec §8 的 no-git HISTORY 格式。

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
