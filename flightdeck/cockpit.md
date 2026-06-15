# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-16 by 月离 (land Spec 1 `act-report-close-loop`：7 任务实现完、160 测试绿、spec/plan 归档；下一步启动 Spec 2 ai-authored-config。)
**Active focus**: flightdeck 3.0 alpha——**Spec 1 `act-report-close-loop` 已 land**（可逆动作无门自动执行 + 统一「翻回」+ 所有 flow 统一 banner + 全生命周期恢复；运行契约真相源 = `protocol § Act-report-close loop`）。**下一步：启动 Spec 2 `ai-authored-config`**（删 7 人工开关 + resolution-order、rules.md 改 AI 落盘——真正的热路径瘦身在此）。**铁律＝纯 AI 操作 + 上下文随时可关可恢复（红线）**；de-scope 基线见 `docs/descope-baseline.md`。

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-16-ai-authored-config.md](specs/2026-06-16-ai-authored-config.md) — 删人工开关目录（7 个 magic-string toggle）+ resolution-order 教学机器；rules.md 从「人手填语法」改为「用户自然话→AI 落盘规则」，保留 version:3.0 戳 + Project conventions；AI 读 rule 高于默认执行，化解删开关后『别人没逃生舱』
- [2026-06-16-ai-authored-config.md](plans/2026-06-16-ai-authored-config.md) — 删 7 magic-string 开关 + resolution-order 教学机器；rules.md ### Autonomy overrides→### Rules（AI 按用户自然话落盘）；protocol/templates/scaffold/skills/tests/外圈同步；保留 version:3.0 + 环境推断 + 默认；verify wc-m 这次净降 + pytest 绿 + landing
<!-- /AUTO -->

## Next

- **启动 Spec 2 `ai-authored-config`**（specs/ai-authored-config.md，idea）：flip active → 写 plan → 执行。同时 **复核 Spec 1 实现**（见 Pending Review；不满意可「翻回」）。

## Key Context

- **de-scope 红线**：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。
- **de-scope 单一真相源**：`docs/descope-baseline.md`（职责边界·无向后兼容·校验只在 walkaround·preflight 纯读零写·热/冷预算；含两轮外评结论）。原 spec 已 graduate 至此、plan 归档。
- **测试/度量**：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。记忆 `flightdeck-3.0-descope-v0`。本机 `test_hooks.py` 17 失败=WSL bash 遮蔽 Git Bash（环境噪音，见 incidents）。
- **act-report-close-loop**：运行契约（可逆判据/banner/翻回/阶段派生/恢复）单一真相源 = `skills/preflight/protocol.md` § Act-report-close loop。该 spec 净增字符（删门省的被新契约盖过；热路径瘦身留 Spec 2）。

## Pending Review

- [Spec 1 act-report-close-loop 实现] 已 land：7 任务、160 测试绿、per-task commit、spec/plan 归档。复核：审 diff（protocol/bootstrap/skills/templates/外圈）或跑 app 看 banner；**不满意就说「翻回」**撤最近着陆单元。验证通过后无需额外动作（已 commit）→ 直接启动 Spec 2。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
