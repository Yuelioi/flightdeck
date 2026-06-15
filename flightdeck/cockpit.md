# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-16 by 月离 (brainstorm「AI 化精简」方向 → 拆成 2 spec：Spec 1 act-report-close-loop active 待复核、Spec 2 ai-authored-config 暂泊 idea。)
**Active focus**: flightdeck 3.0 alpha——「AI 化精简」方向已 brainstorm 成形并拆为 2 spec。**Spec 1 `act-report-close-loop`（active，待你复核 → 写 plan）**：可逆动作无门自动执行 + 统一「翻回」撤销 + 显式 soft-landing banner + Pending Review 恢复完整性。**Spec 2 `ai-authored-config`（idea，排队）**：删人工开关目录、rules.md 改 AI 落盘。**铁律＝纯 AI 操作 + 上下文随时可关可恢复（红线）**；de-scope 基线见 `docs/descope-baseline.md`。

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-16-act-report-close-loop.md](specs/2026-06-16-act-report-close-loop.md) — 统一所有流程输出格式（先正文 → 末尾一个标准 banner，状态/着陆恒在最后、一回合一个）+ 可逆动作无门自动执行 + 统一「翻回」撤销 + soft-landing 覆盖全生命周期状态（brainstorm/spec/plan/部分/待审/通过/即席）+ Pending Review 写明验证后动作；确保随时关闭、下次 preflight 从看板恢复
- [2026-06-16-act-report-close-loop.md](plans/2026-06-16-act-report-close-loop.md) — 按 spec 落地：baseline → protocol.md 单一真相源(判据表+banner 规范+翻回+Hanging 窄定义+阶段派生) → bootstrap 最小指针 → skills 删门+banner → 模板/scaffold → 测试 → 外圈文档+descope 归宿 → dogfood verify(wc-m 降+pytest 绿)+landing
<!-- /AUTO -->

## Next

- **复核 Spec 1 `act-report-close-loop`**（specs/2026-06-16-act-report-close-loop.md）；确认后用 writing-plans 写 plan 并执行落地。Spec 2 `ai-authored-config` 排队（Spec 1 落地后启动）。

## Key Context

- **de-scope 红线**：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。
- **de-scope 单一真相源**：`docs/descope-baseline.md`（职责边界·无向后兼容·校验只在 walkaround·preflight 纯读零写·热/冷预算；含两轮外评结论）。原 spec 已 graduate 至此、plan 归档。
- **测试/度量**：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。记忆 `flightdeck-3.0-descope-v0`。本机 `test_hooks.py` 17 失败=WSL bash 遮蔽 Git Bash（环境噪音，见 incidents）。

## Pending Review

- [AI 化精简 2 spec] 已写 Spec 1 `act-report-close-loop`(active) + Spec 2 `ai-authored-config`(idea/Backlog) 待你复核（见 [specs INDEX](specs/INDEX.md)）。验证通过后：写 Spec 1 的 plan 并执行；Spec 2 启动。未 commit（复核中）。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
