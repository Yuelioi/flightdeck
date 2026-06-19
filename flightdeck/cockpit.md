# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-19 · 月离 · Stage: v3.0.0-alpha.3 已发布；正在做 launch-recorded-config（相 1 ✅ / 相 2 Node 移植 ✅，相 2 散文+相 3/4 待续）

Focus: launch-recorded-config 全 spec → specs/2026-06-19-launch-recorded-config.md

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-19-launch-recorded-config.md](specs/2026-06-19-launch-recorded-config.md) — Shift flightdeck from inference/fallback to recorded settings + required runtime…
- [2026-06-19-launch-recorded-config-1-config-git.md](plans/2026-06-19-launch-recorded-config-1-config-git.md) — Phase 1 of launch-recorded-config: declare the rules.md frontmatter settings sch…
- [2026-06-19-launch-recorded-config-2-runtime-node.md](plans/2026-06-19-launch-recorded-config-2-runtime-node.md) — Phase 2 of launch-recorded-config: force a script runtime by deleting every hand…
<!-- /AUTO -->

## Next

- **相 2 收尾**：Task 7（删各 skill 的手写 markdown 兜底，runtime 现强制）+ Task 8（launch 探测收窄到 git+runtime、拒绝路径、runtime dispatch）。注意 `status/landing` 链入 `exit-ritual.md` 的 `#script-fast-path-*` / `#index-regeneration-*` 锚点——删段须同步改链，否则 dangling-ref 审计红。
- **相 3**：plan + 实现——`agents_md`/`runtime` 字段 *读取* 接入 landing/status/emit-agents-md；runtime 失效硬失败（spec §5）。
- **相 4**：plan + 实现——走 `checklists/version-bump.md` 到 `3.0.0-alpha.4` + CHANGELOG。**用户定：做版本号+CHANGELOG，不 push、不打 tag。**
- （**parked**）跨项目本地验 alpha.3 → `checklists/local-plugin-testing.md`。
- （**parked**）复核 `shared-knowledge-sync` v2（`feat/shared-knowledge-sync-v2`，未并 main）。

## Key Context

- **launch-recorded-config 相 2 Node 移植已落（本会话）**：`scripts/flightdeck_lib.js` + `flightdeck_index/lint/init/new.js`（零 npm 依赖），byte-parity 锚定——`scripts/tests/parity/` 金标 fixture + `test_parity*.py`（24 parity 测试），全 200 测试绿。harness 暴露并修了 Python 参考 3 个真 bug：lint stdout 未强制 UTF-8（cp936 下 em-dash/CJK mojibake）、`KNOWLEDGE_FOLDERS` 集合序非确定（PYTHONHASHSEED）、`_collect_md` 未排序。parity 契约/落点详见 `plans/2026-06-19-launch-recorded-config-2-runtime-node.md`。
- 相 1（已提交）带病提交过一个坏测试（Task 3 改 scaffold 注释但 init 测试断言没跟），本会话 commit `e31c9b8` 修掉。

## Pending Review

- [shared-knowledge-sync **v2** 实现] 9 任务 land（169 测试绿、子代理两段评审 + opus 终审 ready；spec graduate→`docs/shared-knowledge-sync.md`、plan 归档）；母库已**物理移到** `~/.flightdeck`、本仓两 vendored 文件 `synced_from`→`synced` 迁移 + 补注册（`--list-consumers` 命中本仓、`in-sync`）。**跨项目 `--fanout` live 实证待做**（需第二个消费 deck）。审分支 diff `feat/shared-knowledge-sync-v2`；**不满意说「翻回」**。分支**未并入 main**（本仓只本地、不 push）。
- ⚠待复核 `docs/script-layer.md`：本会话 v2 又加 `--register/list/prune-consumers` + 改 `sync_status`（继上次 `--sync-status` 之后），脚本层文档仍未补；下次补齐这批 flag。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
