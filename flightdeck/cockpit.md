# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-10 by 月离 (skills 失实清扫 A1–A7+B3 修毕（含 kind 改名 reference、知识件去日期前缀），138 测试绿；遗留 B1 待讨论、B2 后置。)
**Active focus**: flightdeck 3.0 完善到位（**不急发布、避免迁移债**）。**核心卖点=随时可关、下次 preflight 干净接手、上下文不丢（红线）**。de-scope 主线已收口（基线见 `docs/descope-baseline.md`）；当前在清 skills 文档失实（A 组已修，遗留 B1/B2）+ Backlog 消化。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-10-skills-doc-drift-cleanup.md](specs/2026-06-10-skills-doc-drift-cleanup.md) — 新模型全量 review skills/ 发现 6 组失实/矛盾：root INDEX 残留引用、hook 相位4 已实证但仍标 pending、preflight 补偿路径残留违反纯读零写、version/walkaround 权责矛盾、pre-3.0 向后兼容文案残留违反 descope 基线、new 的 kind 清单与 chart 命名不一致；另 3 项设计层疑点（applies_to tags vs paths、landing SKILL 超重、断锚点）
<!-- /AUTO -->

## 下一步

- **进行中：skills 文档失实清扫**（[2026-06-10-skills-doc-drift-cleanup.md](specs/2026-06-10-skills-doc-drift-cleanup.md)）——A1–A6 + B3 部分已修毕待签收；B1（applies_to tags vs paths）留待单独讨论、B2（landing SKILL 瘦身）后置。
- **Backlog**：#1 写门负例（纯 prompt 低风险）、#7 恢复回归测试（待恢复模型稳定再做，首个核心价值行为测试）。

## 关键上下文

- **de-scope 红线**：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。
- **de-scope 单一真相源**：`docs/descope-baseline.md`（职责边界·无向后兼容·校验只在 walkaround·preflight 纯读零写·热/冷预算；含两轮外评结论）。原 spec 已 graduate 至此、plan 归档。
- **测试/度量**：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。记忆 `flightdeck-3.0-descope-v0`。本机 `test_hooks.py` 17 失败=WSL bash 遮蔽 Git Bash（环境噪音，见 incidents）。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
