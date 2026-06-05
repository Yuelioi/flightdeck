---
status: done
implements: archive/specs/2026-06-03-scriptable-mechanical-layer-design.md
summary: 机械层脚本化 rollout —— INDEX-regen 接进 landing/walkaround/status 双轨 + rules scripts 开关 + 版本 guard + walkaround lint 子命令；3 phase 全完成（lint=flightdeck_lint.py，Audit 1/4/5/7/8）
last_updated: 2026-06-04
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

- [x] **前置已解**（2026-06-03）：A1 拆 migration / A4 拆 protocol 均评估后**关闭**（见 [token-reduction spec 结论](../archive/specs/2026-06-03-token-reduction-design.md)）——protocol 不会再大改，可安全脚本化。
- [x] **lint 子命令**（2026-06-04）：交付为 `scripts/flightdeck_lint.py`（**分立脚本**，非 `flightdeck.py <cmd>`——遵 spec「职责分多脚本、统一待脚本变多 YAGNI」的已锁决策）。覆盖机械子集 Audit **1/4/5/7/8**（status 合法性 / orphan plan / INDEX↔folder drift〔复用 `flightdeck_index.index_drift`〕/ dangling ref / stray file 无歧义子集），吐 `{"findings":[…]}` JSON、有 CRITICAL/WARNING 时 exit≠0；判断项（知识分类 / migration / AGENTS 语义 drift / stray 完整可达性）留模型。dangling-ref 加**代码区剥离**（fenced/inline code 内的链接例不误报）。30 unittest（TDD）。已配线进 [exit-ritual § Script fast path](../../skills/preflight/exit-ritual.md) + walkaround intro。
- [x] **lint 候选：untracked outstanding spec —— 由 model-v4 吸收，不再实现**（2026-06-04 决策）：model-v4 把 cockpit `## 进行中` 改为「从每个 `status: active` spec/plan **AUTO 派生**」，故「active spec 未被 cockpit 追踪」结构上不可能；walkaround Audit 13（进行中 AUTO 区一致性）已确定性兜底该不变量。原痛点（本会话 spec 没当场汇进 Next session）的根因——cockpit 手维护——已消失。结构块断言守卫仍是独立的 [structural-edit-guard](../specs/2026-06-03-structural-edit-guard-design.md)（idea），与本项无关。
- [x] **Verify**（2026-06-04）：在本仓库 deck 实跑 `flightdeck_lint.py flightdeck`——当场抓出 3 处**真实** dangling ref（`CHANGELOG.md` 指向已归档进 `landed/specs/` 的 3 个 2026-06-02 spec，旧路径未改写），与人工 Audit 7 结论一致；已修 CHANGELOG 链接，deck 现 lint 干净（findings: []）。token 实测：脚本读文件在子进程、不进上下文，模型只见一行 JSON。

## Notes

- 分界线（spec）：脚本只 generate/count/lint/extract，判断留模型。
- 纯 Python stdlib；Windows-first，不碰 shell/bash。
