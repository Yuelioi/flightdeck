# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-03 by 月离 (本会话再落：删 init onboarding 教程；删 cockpit hygiene footer（模版+deck）；机械层脚本化 PoC —— `scripts/flightdeck_index.py` INDEX-regen 建+测(10)+落地，当场修了 deck 4 处 INDEX 漂移；preflight 三方审核 triage。分支仍 unpushed、未 runtime dogfood)
**Active focus**: flightdeck 3.0 分支全部 code-complete、未 push（rules 简化 / init 重做 / README+docs / 删教程 / 删 hygiene footer / 机械层脚本 PoC）；待 reload dogfood → 发布 → 合并 main。

## Next session

1. **行为 dogfood（reload/重装插件后）**：①3.0——git/emit 推断、`### Autonomy overrides` 标准句覆盖、2.3→3.0 迁移改写、when-to-land signal 1/2、walkaround 不报假阳性；②init 重做——干净目录跑首次建档全程（git 检测+copy 全布局+interview+AGENTS 询问）。
2. **发布 3.0** [checklists/version-bump.md](checklists/version-bump.md)（marketplace + tag + 同步插件缓存），然后合并分支 → main。
3. **机械层脚本化 rollout** [sketches/scriptable-mechanical-layer.md](sketches/scriptable-mechanical-layer.md)：INDEX-regen 接进 landing/walkaround/status（双轨 fallback）+ rules `scripts:` 开关 + 版本钉死 guard；后续 walkaround lint。
4. **preflight 减重/纠错** [sketches/preflight-tri-review-triage.md](sketches/preflight-tri-review-triage.md)：B1/B3 顺手修，A1 拆 migration 独立 spec。
5. 仍开放：INDEX-row `—` 分隔符冲突 [incidents/index-row-summary-delimiter.md](incidents/index-row-summary-delimiter.md)；spec §8 的 no-git HISTORY 格式。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
