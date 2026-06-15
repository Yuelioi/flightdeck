---
name: walkaround
description: Use when explicitly invoking the flightdeck integrity audit — checks cockpit.md / rules.md / specs / plans / incidents / checklists / docs / references for status validity, INDEX↔folder consistency (incl. nested knowledge areas), cockpit `## In Progress` AUTO-region consistency, orphan plans, dangling references, stray files, AGENTS.md drift, and (INFO) done-but-unlanded + missing workflow summary/last_updated + dangling supersedes/related edges + oversized Key Context. Triggered by `/flightdeck:walkaround`.
---

# Flightdeck Walkaround

User-triggered integrity audit of a flightdeck for protocol drift. Surfaces drift loudly so the author can fix it. The markdown checklist below is always the source of truth; mechanical audits (Audits 1/4/5/7/8) MAY use `flightdeck_lint.py` (JSON findings) or `flightdeck_index.py --check` as optional fast paths.

**只审不修（walkaround invariant）：** walkaround 只浮出漂移，**不改任何文件**。修复路径 = `flightdeck_index.py <deck>` 或 `/flightdeck:landing`。

**Field authority**: [protocol.md § Frontmatter field reference](../preflight/protocol.md#frontmatter-field-reference-canonical) is the source of truth; these audits check against it.

## Severity legend

- **CRITICAL** — protocol contract broken. Fix before new work.
- **WARNING** — drift that accumulates. Fix soon.
- **INFO** — heads-up, judge per item.

## Audits

Run all 14 in order. First read `flightdeck/rules.md` if present; resolve behavior per [protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order). Empty/unused folders are not findings. Report each finding with its severity tag.

**Audit 1** — 查各非-archive `.md` 的 `status` 字段 → flag 缺失（CRITICAL）、非法值（WARNING；`specs/plans` 合法: `idea/active/done`；knowledge 合法: `active/stale/obsolete`；已退役旧值 `pending/awaiting-review/blocked/superseded` 均为 WARNING）。

**Audit 2** — 查非-archive knowledge 文件（`incidents/checklists/docs/references/` 顶层作者 `.md`）的路由字段 → flag 缺失 `when_to_read`/`applies_to`/`last_updated`（WARNING）；`incidents/` 的 `recurrences` 计数与叙事段不符（INFO）。

**Audit 3** — 查非-archive knowledge 文件的退役-3.0 字段 → flag 仍存在 `superseded_by` 字段（WARNING；应删字段，新件加 `supersedes:`）或 `status: superseded`（WARNING；按 Audit 1 迁移）。

**Audit 4** — 查 `plans/`（非 archive）各文件 → flag 无 `implements:` 字段者（INFO；考虑链接 spec 或确认独立）。

**Audit 5** — 查各 artifact 文件夹的 `INDEX.md` → flag 缺 INDEX（WARNING）、文件无对应行（WARNING）、行对应文件不存在（WARNING）、行 status 与实际 frontmatter 不符（WARNING）；检查嵌套 knowledge area 子目录的 INDEX 及父 INDEX 引用行。快速路径：`flightdeck_index.py --check <deck>`。

**Audit 6** — 查 `archive/` 下各带 `status` 的 `.md` → flag workflow 文件非 `done`（WARNING）、knowledge 文件非 `obsolete`（WARNING）。

**Audit 7** — 查 `flightdeck/` 及 repo 根 `*.md` 内所有非 HTTP、非纯锚点的 markdown 链接 → flag 目标文件不存在者（CRITICAL；报 source file:line + 断链路径）。

**Audit 8** — 查 `flightdeck/` 下不属于已知文件夹/已知根条目且不被任何已知入口链接的 `.md` → flag 孤立文件（WARNING）；知识文件夹下的 `<area>/` 子目录不算 stray；`status: idea` spec 不算 orphan；`specs/plans/` 内的子目录算 WARNING；未被文件夹语义覆盖的非 `.md` 文件（WARNING）。

**Audit 9** — 若 repo 根 `AGENTS.md` 带 flightdeck 标记块 → 逐字段比对 `cockpit.md`（active focus / `## In Progress` / `## Next` / hanging tasks）与块内内容 → flag 任何字段偏差（WARNING；说明偏差字段）。

**Audit 10** — 查 `specs/plans/`（非 archive）各文件 → 汇总缺 `summary` / `last_updated` 的文件 → 各输出**一条** aggregated INFO（不逐文件报，避免淹没）。

**Audit 11** — 查非-archive workflow 文件的 `supersedes:`/`related:` 字段值 → flag 目标在 active 树和 `archive/` 均不存在者（INFO；指向 archive 的边正常，不 flag）。

**Audit 12** — 查 `cockpit.md` 的 `<!-- AUTO:inprogress -->` 块 → 计算期望集（所有非 archive `status: active` spec/plan）→ flag active 文件无对应行（WARNING）、行对应文件非 active（WARNING）、摘要/note 文字差异（INFO；下次 regen 自愈）；块完全缺失为 WARNING。快速路径：`flightdeck_index.py --check <deck>` 的 `cockpit` drift 标签。

**Audit 13** — 查 `specs/plans/`（非 archive）中 `status: done` 文件 → flag 有 active 入边（`implements:` 指向它）者为 "blocked done"（INFO；报 blocker）、无 active 入边者为 "landable done 可 land"（INFO；运行 `/flightdeck:landing`）。快速路径：`flightdeck_index.py <deck> --archivable`。

**Audit 14** — 查 `cockpit.md` 的 `## Key Context` 累积卫生（非阻塞）→ flag 条目疑似 stale（指向已 archive/已 graduate 的目标）或单条已长成散文而非 literal 指针、或整段明显超长（INFO；提示在下次 `/flightdeck:landing` 做逐条 drain/收缩，见 [exit-ritual § Accumulator-drain](../preflight/exit-ritual.md#cockpit-update--what-changes)）。walkaround 只浮出、不 drain。

## Output format

```
=== 🔍 /flightdeck:walkaround report ===
Audit run: <ISO date>
Flightdeck root: <path>

CRITICAL findings (N):
  - <file:line> — <issue>

WARNING findings (N):
  - ...

INFO findings (N):
  - ...

Total: N findings (X CRITICAL, Y WARNING, Z INFO)
```

若无任何发现则输出 `✅ Clean.`。忽略 count=0 的 severity 行。某 audit 对应文件夹不存在 → N/A，不算 finding。

## Don't do

- Don't auto-fix — walkaround 只浮出，作者决策。`rules.md` version 是 `launch` 写入的静态戳，walkaround 不读、不写、不 bump。
- Don't run against other repos / foreign `flightdeck/` — 误报。
- Don't include archive 文件于大多数 audit（Audit 6 除外）。
- Don't flag empty-but-present folders / INDEX — 空是正常初始态；missing known folder 才是 INFO。
