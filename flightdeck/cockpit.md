# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-06 by 月离 (本会话**清空 specs/ 积压**——4 spec 全做完整簇归档进 `archive/`：①**structural-edit-guard** `flightdeck_lint` 加 `audit_required_structure`（cockpit 必备块 `## 进行中`/AUTO 锚点/`## 下一步`/`## Hanging tasks` 缺→CRITICAL，抓多行 Edit 静默吞结构块）；②**scrapped 退役** 取消 `scrapped` status 值，否决=直接删文件（git 留史+commit body 记因），清 `STATUS_ORDER`/`WORKFLOW_STATUSES`/`folder_summary`/`_specs_grouped_body`/`layout_verdict` 特例 + ~35 处文档对齐 + 连带删过时 `docs/lifecycle.md` & 修 3 README，顺带消灭"计数≠可见行"+"文档↔代码漂移"俩 bug；③**status-spec-co-advance** landing 对账 `spec_advance_candidates`+CLI `--advance-candidates`（plan 全 done 而 spec 滞后→confirm-gated offer 推进）；④**incident-recurrence** 翻 done。另删 v1x backlog 池。**144 tests 绿**。改了 build input（脚本/skill）→ 下会话 reload 后 live 复验。)
**Active focus**: flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。本会话清空 specs/ 积压（4 spec 全做完归档）；specs/ 现空、无 active。

## 进行中

<!-- AUTO:inprogress -->

<!-- /AUTO -->

## 下一步

- 下会话 **reload 后 live 复验**本会话脚本/skill 改动：structural-edit-guard（lint `required-structure` 抓 cockpit 缺块）、`--advance-candidates`（landing co-advance 对账）、scrapped 退役（遗留 `status: scrapped` 被 lint 标 illegal、`/flightdeck:new --status` 无 scrapped 选项）。
- specs/ 已清空；新工作按需起 idea。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
