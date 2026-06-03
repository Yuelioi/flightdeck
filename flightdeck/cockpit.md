# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-03 by 月离 (本会话：tri-review 整改 + token-reduction（均完成→done）+ incident 复发 auto-count（实现+27 tests）+ structural-edit-guard spec（pending）；用新版 landing 演示 Step5a。**重建 Next session 为 3.0 发布前清单**——之前散落的 spec 全汇齐。待 reload dogfood。分支领先 main、未 push)
**Active focus**: flightdeck 3.0 分支 code-complete、未 push；preflight 整改 + 减重 + auto-count 已完成、QA 通过；**发布前剩 dogfood + scriptable lint + 几个开放项**（见下），然后发布 → 合并 main。

## Next session — 3.0 发布前清单

1. **重同步缓存 → 行为 dogfood（reload）** ← 发布前总闸：①3.0 软配置面（git/emit 推断、`### Autonomy overrides` 覆盖、2.3→3.0 迁移、when-to-land、walkaround 不报假阳性）②init 重做（干净目录首次建档全程）③**incident 复发 auto-count** [spec](specs/2026-06-03-incident-recurrence-autocount-design.md)（landing 自动 [Case N]+recur:N、晋级 gate）。
2. **scriptable 机械层** [plan](plans/2026-06-03-scriptable-mechanical-layer-rollout.md) / [spec](specs/2026-06-03-scriptable-mechanical-layer-design.md)：Phase 2 把 INDEX-regen 接进 landing/walkaround/status 双轨；Phase 3 **lint 子命令**——status 合法性 / dangling-ref / stray / **必备结构块断言（=[structural-edit-guard](specs/2026-06-03-structural-edit-guard-design.md)，防多行 Edit 吞标题）** / **recur 校验**。walkaround 压缩待此。
3. **决策：recur≥3 已晋级在 INDEX 可见？** 现 INDEX 区分不出"待晋级 vs 已晋级"（晋级记在 body `Promoted:`）；定方案（promoted frontmatter 标 / 翻 superseded / 保持现状），归 [autocount spec](specs/2026-06-03-incident-recurrence-autocount-design.md)。
4. **小开放项**：INDEX-row `—` 分隔符冲突 [incident](incidents/index-row-summary-delimiter.md)；no-git HISTORY 格式（scriptable spec §8）。
5. **发布 3.0**（最后）[checklists/version-bump.md](checklists/version-bump.md)：version-bump + marketplace + tag + 合并分支 → main。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
