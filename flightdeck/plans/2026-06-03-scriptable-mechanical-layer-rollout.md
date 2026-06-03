---
status: active
implements: specs/2026-06-03-scriptable-mechanical-layer-design.md
summary: 机械层脚本化 rollout —— INDEX-regen 接进 landing/walkaround/status 双轨 + rules scripts 开关 + 版本 guard + walkaround lint 子命令；分 3 phase，INDEX-regen PoC 已交付
last_updated: 2026-06-03
---

# Scriptable mechanical layer — rollout

实现 [spec](../specs/2026-06-03-scriptable-mechanical-layer-design.md) 的剩余部分。INDEX-regen PoC 已交付并提交（spec § Delivered），本 plan 是把它接进契约 + 扩面。

## Phase 1 — INDEX-regen 接进 skill 双轨

- [x] exit-ritual § INDEX regeneration 加 "Script fast path" 双轨（单一真相）；walkaround Audit 5 + status Step 5 引用它；walkaround "not a CLI binary" 句改双轨措辞。
- [x] 保留 prose 慢路径原文不动（= fallback）。
- [x] **init 脚本化**（续）：`flightdeck_init.py` 接进 preflight Branch-0（双轨，门控=runtime 探测而非 House Rule，因 rules.md 此刻才建）；省 ~5k token + verbatim 灭 scaffold-ships-verbatim。
- [x] **Verify**：默认走 prose（无 House Rule）；脚本路径 `--check` 抓漂移已实测；judgment 仍留 markdown。

## Phase 2 — rules `scripts:` 开关 + 版本 guard

- [x] `scripts` 作 **House Rule**（非 frontmatter toggle —— 3.0 只保留 `disabled_folders` 一个结构化 toggle）：`### Autonomy overrides` 写 `run scripts [with <runtime>]`，默认 manual。protocol 标准句表 + 默认 + templates 模板/示例 + 本项目 rules.md dogfood（`run scripts with python3`）。
- [x] 脚本加**版本 guard**：`version_mismatch()` 读 deck `rules.md version` 对 bundled `MIGRATION.md current`，不符则拒跑（exit 2）+ 提示手动 / `--force`。TDD 3 用例。
- [x] **Verify**：默认（无 House Rule）走 prose；版本不符时脚本 exit 2；15 测试绿。

## Phase 3 — walkaround lint 子命令（待前置）

- [ ] **前置**：等 [preflight-tri-review-remediation](../specs/2026-06-03-preflight-tri-review-remediation.md) 的范围重构（A1 拆 migration 等）落定，避免脚本化一坨又被重构掉。
- [ ] `flightdeck.py lint`：把 Audit 1–10 的机械项（INDEX↔文件夹一致性、orphan、dangling ref、stray file、status 合法性）脚本化，吐 JSON；模型读结果做判断/叙述。
- [ ] **Verify**：lint 输出与现 walkaround 人工审计结论一致；token 实测对比。

## Notes

- 分界线（spec）：脚本只 generate/count/lint/extract，判断留模型。
- 纯 Python stdlib；Windows-first，不碰 shell/bash。
