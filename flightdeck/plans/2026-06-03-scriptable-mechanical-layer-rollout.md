---
status: pending
implements: specs/2026-06-03-scriptable-mechanical-layer-design.md
summary: 机械层脚本化 rollout —— INDEX-regen 接进 landing/walkaround/status 双轨 + rules scripts 开关 + 版本 guard + walkaround lint 子命令；分 3 phase，INDEX-regen PoC 已交付
---

# Scriptable mechanical layer — rollout

实现 [spec](../specs/2026-06-03-scriptable-mechanical-layer-design.md) 的剩余部分。INDEX-regen PoC 已交付并提交（spec § Delivered），本 plan 是把它接进契约 + 扩面。

## Phase 1 — INDEX-regen 接进 skill 双轨

- [ ] landing step 3（regen INDEX）/ walkaround INDEX↔frontmatter 审计 / status：各加一句"脚本可用则 `python scripts/flightdeck_index.py <deck>`（审计用 `--check`），否则按现有 prose 手动重生"。
- [ ] 保留 prose 慢路径原文不动（= fallback）。
- [ ] **Verify**：有 python / 无 python 两种环境都能完成 INDEX 同步；`--check` 在 walkaround 里能抓漂移。

## Phase 2 — rules `scripts:` 开关 + 版本 guard

- [ ] rules.md schema 加 `scripts: auto | off | <runtime|path>`；更新 `templates.md` 的 rules 模板 + `protocol.md` 解析说明。
- [ ] 首次探测可用 runtime → 钉进 rules（`auto` → `python3`）；opt-in 提示（信任闸 + 可发现性）。
- [ ] 脚本加**版本 guard**：读 deck `rules.md version` 对 `MIGRATION.md current`，不符则拒跑 + 提示退化手动。
- [ ] **Verify**：`scripts: off` 时全程走 prose；版本不符时脚本拒跑。

## Phase 3 — walkaround lint 子命令（待前置）

- [ ] **前置**：等 [preflight-tri-review-triage](../sketches/preflight-tri-review-triage.md) 的范围重构（A1 拆 migration 等）落定，避免脚本化一坨又被重构掉。
- [ ] `flightdeck.py lint`：把 Audit 1–10 的机械项（INDEX↔文件夹一致性、orphan、dangling ref、stray file、status 合法性）脚本化，吐 JSON；模型读结果做判断/叙述。
- [ ] **Verify**：lint 输出与现 walkaround 人工审计结论一致；token 实测对比。

## Notes

- 分界线（spec）：脚本只 generate/count/lint/extract，判断留模型。
- 纯 Python stdlib；Windows-first，不碰 shell/bash。
