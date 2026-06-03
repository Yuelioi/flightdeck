# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-03 by 月离 (本会话：preflight 三方审核 19 项 + sketch→spec；token-reduction 批2 + A1/A4 关闭；**incident 复发 auto-count**（recurrences 提 frontmatter、上 INDEX 行 recur:N、landing 自动计数、晋级仍人工闸门——派生"待晋升"不加 status，守 2.0 红线，[spec](specs/2026-06-03-incident-recurrence-autocount-design.md)）；QA 全绿(anchor / 27 tests / INDEX)。待 reload dogfood。分支仍 unpushed)
**Active focus**: flightdeck 3.0 分支 code-complete、未 push；preflight skill 整改 + 减重 + incident 复发 auto-count 已完成、QA 通过；待 reload dogfood → 发布 → 合并 main。

## Next session

1. **行为 dogfood（reload/重装插件后）—— 进入测试**：①3.0——git/emit 推断、`### Autonomy overrides` 标准句覆盖、2.3→3.0 迁移改写、when-to-land signal 1/2、walkaround 不报假阳性；②init 重做——干净目录跑首次建档全程；③**incident 复发 auto-count**——landing 真的自动 append [Case N] + bump recurrences、INDEX 显 recur:N、晋级 gate 触发。
2. **结构性 Edit 守卫**（pending，下个对话启动）[specs/2026-06-03-structural-edit-guard-design.md](specs/2026-06-03-structural-edit-guard-design.md)：lint 加"必备结构块"断言，防多行 Edit 静默吞标题（本会话 cockpit `## Next session` 被误删的根因）。
3. **发布 3.0** [checklists/version-bump.md](checklists/version-bump.md)（marketplace + tag + 同步插件缓存），然后合并分支 → main。
4. 仍开放：INDEX-row `—` 分隔符冲突 [incidents/index-row-summary-delimiter.md](incidents/index-row-summary-delimiter.md)；spec §8 的 no-git HISTORY 格式；walkaround 压缩（归 [scriptable lint](specs/2026-06-03-scriptable-mechanical-layer-design.md)）。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
