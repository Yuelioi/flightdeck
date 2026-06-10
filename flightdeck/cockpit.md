# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-10 by 月离 (签收清板：hook 相位4 live 实证通过（删 verify）；nonblocking-verify + stage-brand-glyphs 两组 spec+plan 翻 done 归档。看板全清，下一步从 Backlog 挑。)
**Active focus**: flightdeck 3.0 完善到位（**不急发布、避免迁移债**）。**核心卖点=随时可关、下次 preflight 干净接手、上下文不丢（红线）**。de-scope 主线已收口（基线见 `docs/descope-baseline.md`）；看板已清空，进入 Backlog 消化阶段。

## 进行中

<!-- AUTO:inprogress -->

<!-- /AUTO -->

## 下一步

- **看板已全清（2026-06-10 签收）**：hook 相位4 live 实证通过、nonblocking-verify 与 stage-brand-glyphs 两组 spec+plan 归档；无 active、无待验证。
- **Backlog（下一步从这里挑）**：#1 写门负例（纯 prompt 低风险）、#7 恢复回归测试（待恢复模型稳定再做，首个核心价值行为测试）。

## 关键上下文

- **de-scope 红线**：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。
- **de-scope 单一真相源**：`docs/descope-baseline.md`（职责边界·无向后兼容·校验只在 walkaround·preflight 纯读零写·热/冷预算；含两轮外评结论）。原 spec 已 graduate 至此、plan 归档。
- **测试/度量**：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。记忆 `flightdeck-3.0-descope-v0`。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
