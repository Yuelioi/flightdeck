# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-03 by 月离 (本会话：preflight 三方审核 19 项全 dispositioned + sketch→spec；错题本计数升级 + here-string 错题；token-reduction 批2(净 -47 行) + A1/A4 评估关闭；全仓 anchor 校验修 1 既存 dangling link、脚本测试 24 passed。**减重完成、QA 通过**，待 reload dogfood。分支仍 unpushed)
**Active focus**: flightdeck 3.0 分支 code-complete、未 push；preflight skill 整改 + 减重已完成、QA 通过（anchor/测试/INDEX 全绿）；待 reload dogfood → 发布 → 合并 main。

## Next session

1. **行为 dogfood（reload/重装插件后）—— 减重完成，进入测试**：①3.0——git/emit 推断、`### Autonomy overrides` 标准句覆盖、2.3→3.0 迁移改写、when-to-land signal 1/2、walkaround 不报假阳性；②init 重做——干净目录跑首次建档全程。
2. **发布 3.0** [checklists/version-bump.md](checklists/version-bump.md)（marketplace + tag + 同步插件缓存），然后合并分支 → main。
3. 仍开放：INDEX-row `—` 分隔符冲突 [incidents/index-row-summary-delimiter.md](incidents/index-row-summary-delimiter.md)；spec §8 的 no-git HISTORY 格式；walkaround 压缩（归 [scriptable lint](specs/2026-06-03-scriptable-mechanical-layer-design.md)）。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
