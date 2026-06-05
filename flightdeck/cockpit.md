# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-05 by 月离 (本会话：从"怎么让 AI 快速定位错误库"讨论 → brainstorm → spec → plan → 实现 **incident 错误库生命周期**：可 grep 的 `## Signature`（4 键放正文、preflight 不读=零路由 token）+ 确定性签名指纹去重（`--match-signature`，归一化剥易变 token/保语义键）+ obsolete 退役出路由（留盘仍进匹配）+ gated 回归复活。subagent-driven 6 phase / 14 task（每 phase 实现+评审），spec 吸收 2 轮外部评审、回填 4 条现有 incident，**131 tests 绿**、`--check`/lint 干净，spec+plan 翻 done 整簇 land 进 `archive/`。改了 build input（脚本/skill）→ 下会话 reload 后 live 复验。  早先本会话：dogfood item#1 修两缺陷（SKILL kind 表 / KeyError）+ 5 组 spec+plan land。)
**Active focus**: flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。最新落成 incident 错误库生命周期；active 只剩 `incident-recurrence`（待 dogfood 行为验证）+ 若干 idea。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-03-incident-recurrence-autocount-design.md](specs/2026-06-03-incident-recurrence-autocount-design.md) — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
<!-- /AUTO -->

## 下一步

- 下会话 **reload 后 live 复验**本会话新功能：`/flightdeck:new` 建 incident 带 `## Signature`、`--match-signature` 建前查重、obsolete 退役出路由、landing gated 回归复活。
- `incident-recurrence`（唯一 active）补 dogfood 行为验证。
- 待办 idea 按需推进：status-spec-co-advance / structural-edit-guard / scrapped-artifact-disposition。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
