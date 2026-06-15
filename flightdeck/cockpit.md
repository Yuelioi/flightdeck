# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-16 by 月离 (land `skill-constraint-imperative-hardening`：7 处 skill 强命令式硬化 + pre-read 红旗护栏，spec+plan 归档，verify 待行为验证)
**Active focus**: flightdeck 3.0 alpha 打磨——`skill-constraint-imperative-hardening` 已 land（强命令式措辞 + pre-read 红旗护栏）；剩 `cockpit-bloat-control` 待复核/排期。「AI 化精简」两支柱已 land。

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-16-cockpit-bloat-control.md](specs/2026-06-16-cockpit-bloat-control.md) — cockpit 膨胀治理：着陆归档时自动排空引用刚归档 artifact 的冗余散文（可逆，自动）；规范字段替换而非追加 + 逐字段密度检查（门控 trim）；walkaround 守卫野章节 + active 计数非阻塞提示。规范字段集本就精简，膨胀来自野章节与散文不排空。
<!-- /AUTO -->

## Next

- **复核 `cockpit-bloat-control`**（着陆排空冗余散文 + 字段密度门控 trim + walkaround 野章节/active 计数）→ 满意则写 plan 执行。

## Key Context

- **de-scope 红线**：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。
- **de-scope 单一真相源**：`docs/descope-baseline.md`（职责边界·无向后兼容·校验只在 walkaround·preflight 纯读零写·热/冷预算；含两轮外评结论）。原 spec 已 graduate 至此、plan 归档。
- **测试/度量**：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。记忆 `flightdeck-3.0-descope-v0`。本机 `test_hooks.py` 17 失败=WSL bash 遮蔽 Git Bash（环境噪音，见 incidents）。
- **AI 化精简两支柱（已 land）**：运行契约真相源 = `protocol § Act-report-close loop`（banner/翻回/判据/恢复）+ `§ Rule resolution order`（deck `### Rules` > 推断 > 默认）。净字符 Spec 1 +8.8k（新契约）/ Spec 2 −3.1k（删开关）。
- **`cockpit-bloat-control`（active，待复核）**：组件 A 着陆排空冗余散文·B 字段密度门控 trim·C walkaround 野章节 + active 计数；graduate=false。
- **`skill-constraint-imperative-hardening`（已 land/归档）**：硬约束统一强命令式（MUST/NEVER/DO NOT）；记忆 `constraints-use-strong-imperatives` + `dont-preread-siblings-with-authoritative-skill`。⚠verify：下次走 `/flightdeck:new` 看是否还预读兄弟文件。

## Pending Review

- [AI 化精简两 spec 实现] Spec 1 `act-report-close-loop` + Spec 2 `ai-authored-config` 均已 land（多个 per-task commit、160 测试绿、spec/plan 归档）。复核：审 diff 或跑 app（看 banner / `### Rules`）；**不满意就说「翻回」**撤最近着陆单元。已 commit，验证通过无需额外动作。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
