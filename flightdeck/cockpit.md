# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-19 by 月离 (shared-knowledge-sync 投入试用：vendor 首份共享内容 comments.md+commits.md（in-sync）、工作树已 robocopy 进插件缓存（build 1c931ee7，--check current）；**需重启会话加载新 skill**，试用几天)
**Active focus**: flightdeck 3.0 alpha 打磨——`shared-knowledge-sync` 已 land（跨项目共享知识 vendoring：/flightdeck:sync + --sync-status + synced_from/shared_master），待端到端实证；`cockpit-bloat-control` 仍待复核/排期。

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-16-cockpit-bloat-control.md](specs/2026-06-16-cockpit-bloat-control.md) — cockpit 膨胀治理：着陆归档时自动排空引用刚归档 artifact 的冗余散文（可逆，自动）；规范字段替换而非追加 + 逐字段密度检查（门控 trim）；walkaround 守卫野章节 + active 计数非阻塞提示。规范字段集本就精简，膨胀来自野章节与散文不排空。
<!-- /AUTO -->

## Next

- **复核 `shared-knowledge-sync`**（审 diff，或真 vendor 一份共享文件跑 `/flightdeck:sync` 做端到端实证）；之后回到 `cockpit-bloat-control` 复核/排期。

## Key Context

- **de-scope 红线**：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。
- **de-scope 单一真相源**：`docs/descope-baseline.md`（职责边界·无向后兼容·校验只在 walkaround·preflight 纯读零写·热/冷预算；含两轮外评结论）。原 spec 已 graduate 至此、plan 归档。
- **测试/度量**：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。记忆 `flightdeck-3.0-descope-v0`。本机 `test_hooks.py` 17 失败=WSL bash 遮蔽 Git Bash（环境噪音，见 incidents）。
- **AI 化精简两支柱（已 land）**：运行契约真相源 = `protocol § Act-report-close loop`（banner/翻回/判据/恢复）+ `§ Rule resolution order`（deck `### Rules` > 推断 > 默认）。净字符 Spec 1 +8.8k（新契约）/ Spec 2 −3.1k（删开关）。
- **`cockpit-bloat-control`（active，待复核）**：组件 A 着陆排空冗余散文·B 字段密度门控 trim·C walkaround 野章节 + active 计数；graduate=false。
- **`skill-constraint-imperative-hardening`（已 land/归档）**：硬约束统一强命令式（MUST/NEVER/DO NOT）；记忆 `constraints-use-strong-imperatives` + `dont-preread-siblings-with-authoritative-skill`。⚠verify：下次走 `/flightdeck:new` 看是否还预读兄弟文件。
- **`shared-knowledge-sync`（已 land/归档，全栈自测过）**：母库为准·谁新谁赢（比 `last_updated`，无 hash）；`synced_from` 可选血缘；母库=`E:\projects\agent\flightdeck`，解析 `$FLIGHTDECK_SHARED_MASTER` → gitignored `<deck>/.shared-master` →（AI）全局 CLAUDE.md。pull（`/flightdeck:sync` 刷正文保 `## 项目覆盖`）+ push（`sync push` promote/回流，覆盖段不上推）；事实=`--sync-status`、walkaround Audit 15。

## Pending Review

- [AI 化精简两 spec 实现] Spec 1 `act-report-close-loop` + Spec 2 `ai-authored-config` 均已 land（多个 per-task commit、160 测试绿、spec/plan 归档）。复核：审 diff 或跑 app（看 banner / `### Rules`）；**不满意就说「翻回」**撤最近着陆单元。已 commit，验证通过无需额外动作。
- [shared-knowledge-sync 实现] 8 任务全 land（66 测试绿、spec 合规 + 终审 ready、spec+plan 归档）；端到端**已自测通过**（real 母库 comments.md：scan→merge→in-sync、`## 项目覆盖` 保留）；首份共享内容已 vendor（comments.md/commits.md，in-sync）、插件缓存已同步——**试用几天中**（需重启会话加载新 skill）。剩你审 diff / 拍板；**不满意说「翻回」**。
- ⚠待复核 `docs/script-layer.md`：本会话给 `flightdeck_index.py` 加了 `--sync-status` 扫描，脚本层文档未提及，下次补。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
