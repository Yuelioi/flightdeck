# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-16 by 月离 (land 首个反馈驱动变更「cockpit 模型升级」：段名英文化 + Pending Review 段 + 累积段排水纪律，spec/plan 归档；新方向＝把工具推向「几乎零人工操作」纯 AI 调用。)
**Active focus**: flightdeck 3.0 alpha——「cockpit 模型升级」已 land（段名英文化 + `Pending Review` 段 + 累积段排水纪律）。**新方向：把工具推向「几乎零人工操作」的纯 AI 调用**——盘点并删减历史上为「人工手改」而写的内容（看板维护/改状态/人工旋钮），先 brainstorm 出清单。**核心卖点=随时可关、上下文不丢（红线）**；de-scope 基线见 `docs/descope-baseline.md`。

## In Progress

<!-- AUTO:inprogress -->

<!-- /AUTO -->

## Next

- **界定「AI 化精简」范围**：盘点历史上为「人工手动维护/修改」而写的内容（看板维护指引、改状态、人工开关/旋钮），判断纯 AI 调用下哪些可删——先 brainstorm 出清单再动手成 spec。

## Key Context

- **de-scope 红线**：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。
- **de-scope 单一真相源**：`docs/descope-baseline.md`（职责边界·无向后兼容·校验只在 walkaround·preflight 纯读零写·热/冷预算；含两轮外评结论）。原 spec 已 graduate 至此、plan 归档。
- **测试/度量**：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。记忆 `flightdeck-3.0-descope-v0`。本机 `test_hooks.py` 17 失败=WSL bash 遮蔽 Git Bash（环境噪音，见 incidents）。

## Pending Review

- (none)

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
