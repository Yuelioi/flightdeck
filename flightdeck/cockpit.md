# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-22 · 月离 · Stage: v3.0.0-alpha.4 已发布；exit-ritual 收紧 soft-landing 知识落库反模式（知识增量回合当回合落 incident，不推迟到整盘 landing）

Focus: stage/land 生命周期重构 → `specs/2026-06-22-stage-land-lifecycle.md`（spec 收敛完，待拆 plan）

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-22-stage-land-lifecycle.md](specs/2026-06-22-stage-land-lifecycle.md) — Two-phase lifecycle replacing the checkpoint/soft-landing/full-landing split: st…
<!-- /AUTO -->

## Next

- 写 **plan 1（数据模型 + 脚本地基）** for stage/land：`## Staged` 派生视图脚本 + Land Routine 触发点（取消 signal-1 自动 archive）+ commit 移 stage 侧（先读 `scripts/flightdeck_index.py` 现状）。implements `specs/2026-06-22-stage-land-lifecycle.md`。后续 plan 2（散文重写）/ plan 3（signal 体系 + walkaround 翻转）。
- （**parked**）跨项目本地验 alpha.4 → `checklists/local-plugin-testing.md`。
- （**parked**）复核 `shared-knowledge-sync` v2（`feat/shared-knowledge-sync-v2`，未并 main）。

## Key Context

- deck-format-conform 落地：设计真相源 `docs/deck-format-conform.md`；脚本 `scripts/flightdeck_conform.py/.js`（byte-parity，`ConformParity`）、skill `skills/conform/SKILL.md`、walkaround Audit 16 → 指向 `/flightdeck:conform`。`references/` 排除出 walk（IMPORTED_KIND）。

## Pending Review

- [shared-knowledge-sync **v2** 实现] 9 任务 land（169 测试绿、子代理两段评审 + opus 终审 ready；spec graduate→`docs/shared-knowledge-sync.md`、plan 归档）；母库已**物理移到** `~/.flightdeck`、本仓两 vendored 文件 `synced_from`→`synced` 迁移 + 补注册（`--list-consumers` 命中本仓、`in-sync`）。**跨项目 `--fanout` live 实证待做**（需第二个消费 deck）。审分支 diff `feat/shared-knowledge-sync-v2`；**不满意说「翻回」**。分支**未并入 main**（本仓只本地、不 push）。
- ⚠待复核 `docs/script-layer.md`：本会话 v2 又加 `--register/list/prune-consumers` + 改 `sync_status`（继上次 `--sync-status` 之后），脚本层文档仍未补；下次补齐这批 flag。
- [exit-ritual soft-landing hardening] heuristic (a) + signal-3 定义两段散文，钉死「知识增量回合推迟到整盘 landing 才落 incident」反模式 + 指明「未验证→照写+verify: 债，非推迟理由」；沉淀 incident `soft-landing-knowledge-defer-drift`。改的是**产品发布面协议散文**（governance edit）——复核两段英文措辞是否合意 · 看 `skills/preflight/exit-ritual.md`（heuristic (a) 末尾 + signal 3 那段）。**未 commit**。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
