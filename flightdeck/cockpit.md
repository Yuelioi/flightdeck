# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-11 by 月离 (v3.0.0-alpha.1 已 ff 合并进 main + docs/ 人类叙事三篇对齐 3.0；剩用户 push --follow-tags。)
**Active focus**: flightdeck 3.0 alpha 试用期——**v3.0.0-alpha.1 已发布（main 上 commit+tag，待维护者 push）**，邀请早期试用者收集反馈；alpha 期间仍可破坏性调整，正式 3.0.0 完善到位再发。**核心卖点=随时可关、下次 preflight 干净接手、上下文不丢（红线）**。de-scope 基线见 `docs/descope-baseline.md`。

## 进行中

<!-- AUTO:inprogress -->

<!-- /AUTO -->

## 下一步

- **alpha 发布收尾（维护者手动）**：已在 main 上，执行 `git push origin main --follow-tags` 即对外可装 v3.0.0-alpha.1；push 后 `git ls-remote --tags origin` 确认 tag 到位。本仓库 AI 绝不 push。
- **skills 失实清扫已全量收口 ✅**（处置纪要见 [archive/specs/2026-06-10-skills-doc-drift-cleanup.md](archive/specs/2026-06-10-skills-doc-drift-cleanup.md)）。欠账=同步 cache 后新会话跑一次完整 landing 验证（verify 标记会自动浮出）。
- **Backlog（下一步从这里挑）**：消化 alpha 试用反馈、#1 写门负例（纯 prompt 低风险）、#7 恢复回归测试（待恢复模型稳定再做，首个核心价值行为测试）。

## 关键上下文

- **de-scope 红线**：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。
- **de-scope 单一真相源**：`docs/descope-baseline.md`（职责边界·无向后兼容·校验只在 walkaround·preflight 纯读零写·热/冷预算；含两轮外评结论）。原 spec 已 graduate 至此、plan 归档。
- **测试/度量**：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。记忆 `flightdeck-3.0-descope-v0`。本机 `test_hooks.py` 17 失败=WSL bash 遮蔽 Git Bash（环境噪音，见 incidents）。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
