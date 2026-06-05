# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-06 by 月离 (本会话：先聊定 `execution-checkpoint` 三个 plan 开口——①形态=landing 的 checkpoint 子路径；②进度=plan 正文 `current:` 指针；③默认纯看板落盘**不提交**。据此 flip spec→active 并落成 plan（5 task，纯 skill 散文改、脚本层零改动），待执行。)
**Active focus**: flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。**核心卖点锁定=随时可关对话、下次 preflight 干净接手、上下文不丢**；当前主线＝实现 `execution-checkpoint`（landing 加 checkpoint 轻量子路径 + plan `current:` 指针）。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-06-execution-checkpoint.md](specs/2026-06-06-execution-checkpoint.md) — plan/task 边界自动看板同步（cockpit 下一步 + plan 进度落盘，commit 不强求），让用户随时可关对话、下次 preflight 干净接手、上下文不丢；轻量 checkpoint = 完整 landing 的子集
- [2026-06-06-execution-checkpoint.md](plans/2026-06-06-execution-checkpoint.md) — 在 landing 加 checkpoint 轻量子路径（task 边界只同步看板·不提交）+ plan 正文 current 指针；纯 skill 散文改，脚本层零改动
<!-- /AUTO -->

## 下一步

- 执行 `plans/2026-06-06-execution-checkpoint.md` 的 **Task 1**：在 `skills/preflight/exit-ritual.md` 写下 checkpoint 的 canonical 定义（新 `## Checkpoint` 段 + 改 mid-session/下一步 触发句）。
- 本会话改了 `folder-semantics.md`（build 输入）→ resync + reload 后 live 复验那节文档指南（仍未做）。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
