# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-19 by 月离 (cockpit-bloat-control v2 land：spec 重订 A/C.1 剔除→只留 B 字段密度门控 + C.2 active 计数，已落 exit-ritual/landing/preflight；spec 归档、169 测试绿、descope-baseline 触 stale 保鲜)
**Active focus**: flightdeck 3.0 alpha 打磨——发版 `v3.0.0-alpha.2` 准备中（README shared-knowledge 节已加待过目 → 接 version-bump）；`shared-knowledge-sync` v2 待跨项目 `--fanout` live 实证。

## In Progress

<!-- AUTO:inprogress -->

<!-- /AUTO -->

## Next

- **发版 `v3.0.0-alpha.2`**（用户拍板）：① `README.md` + `README.zh.md` 已加「shared-knowledge / 母库」节（`~/.flightdeck` + `synced` vendoring + `consumers`/`--fanout`，待用户过目，**未 commit**）。② 用户确认 README → 走 `checklists/version-bump.md` bump 到 `3.0.0-alpha.2`（含 README badge 第 7 行、各 manifest、CHANGELOG）。
- **复核 `shared-knowledge-sync` v2**（审分支 diff `feat/shared-knowledge-sync-v2`，未并 main；真 vendor 第二个项目跑 `/flightdeck:sync --fanout` 做跨项目 live 实证）。

## Key Context

- **de-scope 红线**：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。
- **de-scope 单一真相源**：`docs/descope-baseline.md`（职责边界·无向后兼容·校验只在 walkaround·preflight 纯读零写·热/冷预算；含两轮外评结论）。原 spec 已 graduate 至此、plan 归档。
- **测试/度量**：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。记忆 `flightdeck-3.0-descope-v0`。本机 `test_hooks.py` 17 失败=WSL bash 遮蔽 Git Bash（环境噪音，见 incidents）。
- **AI 化精简两支柱（已 land）**：运行契约真相源 = `protocol § Act-report-close loop`（banner/翻回/判据/恢复）+ `§ Rule resolution order`（deck `### Rules` > 推断 > 默认）。净字符 Spec 1 +8.8k（新契约）/ Spec 2 −3.1k（删开关）。
- **`shared-knowledge-sync`（v2 已 land/graduate）**：当前真相 = `docs/shared-knowledge-sync.md`——母库固定 `~/.flightdeck`（symlink/junction 逃生口）、`synced: true` 标记 + relpath 不变量、`consumers` 注册表（register/list/prune，母库专属拷贝时剔除）、`/flightdeck:sync --fanout` 编排。事实=`--sync-status`（`state<TAB>relpath`）、walkaround Audit 15。

## Pending Review

- [AI 化精简两 spec 实现] Spec 1 `act-report-close-loop` + Spec 2 `ai-authored-config` 均已 land（多个 per-task commit、160 测试绿、spec/plan 归档）。复核：审 diff 或跑 app（看 banner / `### Rules`）；**不满意就说「翻回」**撤最近着陆单元。已 commit，验证通过无需额外动作。
- [shared-knowledge-sync **v2** 实现] 9 任务 land（169 测试绿、子代理两段评审 + opus 终审 ready；spec graduate→`docs/shared-knowledge-sync.md`、plan 归档）；母库已**物理移到** `~/.flightdeck`、本仓两 vendored 文件 `synced_from`→`synced` 迁移 + 补注册（`--list-consumers` 命中本仓、`in-sync`）。**跨项目 `--fanout` live 实证待做**（需第二个消费 deck）。审分支 diff `feat/shared-knowledge-sync-v2`；**不满意说「翻回」**。分支**未并入 main**（本仓只本地、不 push）。
- ⚠待复核 `docs/script-layer.md`：本会话 v2 又加 `--register/list/prune-consumers` + 改 `sync_status`（继上次 `--sync-status` 之后），脚本层文档仍未补；下次补齐这批 flag。
- [cockpit-bloat-control v2 实现] spec 重订（A 并入 accumulator-drain、C.1 因 Pending Review 转正作废，剔除）→ 只实现 B（landing 出场逐字段密度门控 trim）+ C.2（active>5 非阻塞提示），落 `exit-ritual.md`/`landing`/`preflight` SKILL；spec 已归档、169 测试绿。复核：审三处措辞 diff；**不满意说「翻回」**。
- ⚠待复核 `docs/descope-baseline.md`（触 stale）：改了 preflight/landing SKILL 散文（加密度检查 + active 计数），该 doc 对 preflight/landing 职责的枚举可能要补这两项——我读后判断仍成立（line 39 已钉「软上限=警戒线非截断」），人确认即可消 stale。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
