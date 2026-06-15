# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-16 by 月离 (land Spec 2 `ai-authored-config`：删 toggle 目录、rules.md 改 AI 落盘，wc-m 净降 3143、160 测试绿、归档。「AI 化精简」两支柱均完成。)
**Active focus**: flightdeck 3.0 alpha——**「AI 化精简」方向两根支柱均已 land**：Spec 1 `act-report-close-loop`（可逆无门自动 + 统一翻回 + 全 flow banner + 全生命周期恢复）+ Spec 2 `ai-authored-config`（删 7 人工开关 + resolution-order、rules.md 改 AI 落盘）。**铁律＝纯 AI 操作 + 上下文随时可关可恢复** 已落地。运行契约真相源 = `protocol § Act-report-close loop` + `§ Rule resolution order`；de-scope 基线见 `docs/descope-baseline.md`。

## In Progress

<!-- AUTO:inprogress -->

<!-- /AUTO -->

## Next

- **复核两 spec 实现**（act-report-close-loop + ai-authored-config；不满意可「翻回」最近着陆单元）。之后回到 3.0 alpha 整体打磨 / 待你指方向。

## Key Context

- **de-scope 红线**：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。
- **de-scope 单一真相源**：`docs/descope-baseline.md`（职责边界·无向后兼容·校验只在 walkaround·preflight 纯读零写·热/冷预算；含两轮外评结论）。原 spec 已 graduate 至此、plan 归档。
- **测试/度量**：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。记忆 `flightdeck-3.0-descope-v0`。本机 `test_hooks.py` 17 失败=WSL bash 遮蔽 Git Bash（环境噪音，见 incidents）。
- **AI 化精简两支柱（已 land）**：运行契约真相源 = `protocol § Act-report-close loop`（banner/翻回/判据/恢复）+ `§ Rule resolution order`（deck `### Rules` > 推断 > 默认）。净字符 Spec 1 +8.8k（新契约）/ Spec 2 −3.1k（删开关）。

## Pending Review

- [AI 化精简两 spec 实现] Spec 1 `act-report-close-loop` + Spec 2 `ai-authored-config` 均已 land（多个 per-task commit、160 测试绿、spec/plan 归档）。复核：审 diff 或跑 app（看 banner / `### Rules`）；**不满意就说「翻回」**撤最近着陆单元。已 commit，验证通过无需额外动作。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
