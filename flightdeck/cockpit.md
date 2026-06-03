# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-03 by 月离 (本会话续：scriptable-mechanical-layer 升 spec+plan；rollout Phase 1+2 落地——脚本接进 landing/walkaround/status 双轨、`run scripts` House Rule(opt-in)、版本 guard、uv 适配。Phase 3 walkaround-lint 待 preflight 重构解锁。分支仍 unpushed、未 runtime dogfood)
**Active focus**: flightdeck 3.0 分支全部 code-complete、未 push；机械层脚本化 INDEX-regen 已接进 skill 双轨(opt-in，markdown fallback)；待 reload dogfood → 发布 → 合并 main。

## Next session

1. **行为 dogfood（reload/重装插件后）**：①3.0——git/emit 推断、`### Autonomy overrides` 标准句覆盖、2.3→3.0 迁移改写、when-to-land signal 1/2、walkaround 不报假阳性；②init 重做——干净目录跑首次建档全程（git 检测+copy 全布局+interview+AGENTS 询问）。
2. **发布 3.0** [checklists/version-bump.md](checklists/version-bump.md)（marketplace + tag + 同步插件缓存），然后合并分支 → main。
3. **preflight 减重/纠错** [sketches/preflight-tri-review-triage.md](sketches/preflight-tri-review-triage.md)：B1/B3 顺手修，A1 拆 migration 独立 spec（顺带解锁机械层 [rollout](plans/2026-06-03-scriptable-mechanical-layer-rollout.md) Phase 3 walkaround lint）。
4. 仍开放：INDEX-row `—` 分隔符冲突 [incidents/index-row-summary-delimiter.md](incidents/index-row-summary-delimiter.md)；spec §8 的 no-git HISTORY 格式。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
