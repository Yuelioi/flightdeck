# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-19 · 月离 · Stage: v3.0.0-alpha.3 已发布；launch-recorded-config 相 1 ✅ / 相 2 ✅（Node 移植 + 散文强制 runtime 全落），相 3/4 待续

Focus: launch-recorded-config 全 spec → specs/2026-06-19-launch-recorded-config.md

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-19-launch-recorded-config.md](specs/2026-06-19-launch-recorded-config.md) — Shift flightdeck from inference/fallback to recorded settings + required runtime…
- [2026-06-19-launch-recorded-config-1-config-git.md](plans/2026-06-19-launch-recorded-config-1-config-git.md) — Phase 1 of launch-recorded-config: declare the rules.md frontmatter settings sch…
- [2026-06-19-launch-recorded-config-2-runtime-node.md](plans/2026-06-19-launch-recorded-config-2-runtime-node.md) — Phase 2 of launch-recorded-config: force a script runtime by deleting every hand…
- [2026-06-19-launch-recorded-config-3-field-semantics.md](plans/2026-06-19-launch-recorded-config-3-field-semantics.md) — Phase 3 of launch-recorded-config: wire the recorded rules.md frontmatter fields…
<!-- /AUTO -->

## Next

- **相 3**：plan + 实现——`agents_md`/`runtime` 字段 *读取* 接入 landing/status/emit-agents-md；runtime 失效硬失败（spec §5）。注意散文契约已在相 2 落地（protocol § Rule resolution order 的 **Runtime dispatch** 段 + 各 ritual 删兜底）——相 3 是让脚本调用真正按字段派发 + 失效硬失败的*实现*。
- **相 4**：plan + 实现——走 `checklists/version-bump.md` 到 `3.0.0-alpha.4` + CHANGELOG。**用户定：做版本号+CHANGELOG，不 push、不打 tag。**
- （**parked**）跨项目本地验 alpha.3 → `checklists/local-plugin-testing.md`。
- （**parked**）复核 `shared-knowledge-sync` v2（`feat/shared-knowledge-sync-v2`，未并 main）。

## Key Context

- **launch-recorded-config 相 2 Node 移植已落（本会话）**：`scripts/flightdeck_lib.js` + `flightdeck_index/lint/init/new.js`（零 npm 依赖），byte-parity 锚定——`scripts/tests/parity/` 金标 fixture + `test_parity*.py`（24 parity 测试），全 200 测试绿。harness 暴露并修了 Python 参考 3 个真 bug：lint stdout 未强制 UTF-8（cp936 下 em-dash/CJK mojibake）、`KNOWLEDGE_FOLDERS` 集合序非确定（PYTHONHASHSEED）、`_collect_md` 未排序。parity 契约/落点详见 `plans/2026-06-19-launch-recorded-config-2-runtime-node.md`。
- 相 1（已提交）带病提交过一个坏测试（Task 3 改 scaffold 注释但 init 测试断言没跟），本会话 commit `e31c9b8` 修掉。
- **相 2 散文（本会话 Task 7+8，commit `b3bdbf0`+`c8d4c26`）**：runtime 现为 3.0 强制——删 exit-ritual/status/landing/new/walkaround 的「无 runtime → 手写 markdown」双写 + Land Routine/stale 的 no-Python-runtime 兜底；exit-ritual `### Script fast path (optional accelerator)` 改名 `### Script path (the mechanical engine)`（旧锚 `#script-fast-path-optional-accelerator` 唯一入链已随 status 改写移除）。protocol § Rule resolution order 新增 **Runtime dispatch** 段（`.py`/`.js` 孪生按 `runtime` 选调用形、失效硬失败、preflight 只读不修）。launch 收窄到 git+runtime 双拒绝，init 后由 **launch 直接写** `runtime:` 字段（init 不 stamp）。phase-2 plan 全任务 done+验证绿，可随时 flip done+land（暂仿 phase-1 plan 留 active）。lint 188 条 dangling-ref 全在 vendored `references/`，与本次改动无关（pre-existing）。

## Pending Review

- [shared-knowledge-sync **v2** 实现] 9 任务 land（169 测试绿、子代理两段评审 + opus 终审 ready；spec graduate→`docs/shared-knowledge-sync.md`、plan 归档）；母库已**物理移到** `~/.flightdeck`、本仓两 vendored 文件 `synced_from`→`synced` 迁移 + 补注册（`--list-consumers` 命中本仓、`in-sync`）。**跨项目 `--fanout` live 实证待做**（需第二个消费 deck）。审分支 diff `feat/shared-knowledge-sync-v2`；**不满意说「翻回」**。分支**未并入 main**（本仓只本地、不 push）。
- ⚠待复核 `docs/script-layer.md`：本会话 v2 又加 `--register/list/prune-consumers` + 改 `sync_status`（继上次 `--sync-status` 之后），脚本层文档仍未补；下次补齐这批 flag。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
