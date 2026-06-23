---
status: done
summary: Implement spec ship-project-marker-by-default: (1) TDD a marker-less-drift detector in flightdeck_index.py/.js (synced + no marker + shared drifted), (2) stamp marker+stub onto vendorable master files, (3) re-pull this repo's vendored copies, (4) teach promote to re-stamp, (5) flip the doc/SKILL/scaffold prose, (6) wire the WARN into walkaround.
last_updated: 2026-06-23
implements: specs/2026-06-23-ship-project-marker-by-default.md
---

# Default the project-section marker into vendorable master files

实现 `specs/2026-06-23-ship-project-marker-by-default.md`。方案 A(母库自带 marker + stub)+
安全网 WARN。测试入口 `uv run pytest scripts/tests/`;脚本改动须 py/js byte-parity。

**Canonical stub**(所有母库 vendorable shared 文件的固定收尾;英文,随产品 ship):

```
<!-- flightdeck:project-specific -->

## Project overrides

_This section is yours — sync never overwrites anything below the marker above._
```

先做安全网(Task 1,纯脚本、可 TDD),再做数据/约定(2–4),最后散文/审计(5–6)。

---

## Task 1 — TDD: marker-less-drift 检测（脚本核心） ✅ done 2026-06-23

> `sync_status` 新增 `marker-missing`（synced + 无 marker + 指纹不等），先于 stale 判。py
> (`flightdeck_index.py`) + js 平价同改；docstring 更新。`--sync-pull` 沿用 `state != "stale"`
> 过滤 → marker-missing **自动不被 pull**（防静默覆盖），加回归测试 `test_marker_missing_file_is_not_pulled`。
> 全量 `uv run pytest scripts/tests/` 251 绿（含 parity 同验 py+js）。**未 commit。**

**目标**:`flightdeck_index.py` 暴露一个判定:`synced: true` 的 consumer 文件，
**无 PROJECT_MARKER** 且其 body 与母库 shared 指纹**不一致** → 高危（本地补充将被 `--sync-pull`
静默覆盖）。挂到 `--sync-status`（新增一类 state，如 `marker-missing`，**先判于 stale/in-sync**：
有 master、relpath 命中、但 consumer 无 marker 且指纹不等）。

- **Test first**（`scripts/tests/test_*`，py + 对应 js）:
  - synced + 无 marker + body == master shared → 不报（纯 shared 文件合法，整 body 即 shared）。
  - synced + 无 marker + body != master shared → `marker-missing`。
  - synced + 有 marker + 指纹不等 → 仍 `stale`（不受影响）。
  - `master-missing` / `dangling` 优先级不变（先判根、再判文件存在）。
- **Impl**:在 `sync_status`/相关分类里加这一支；保持 `--sync-status` 输出 `state<TAB>relpath` 形态。
- **js 平价**:同步改 `flightdeck_index.js`，跑现有 byte-parity 测试。
- **Verify**:`uv run pytest scripts/tests/ -k sync` 全绿;`--sync-status` 在构造的无-marker drift fixture 上输出 `marker-missing`。

## Task 2 — 母库 vendorable 文件 stamp marker + stub ✅ done 2026-06-23

> canonical stub 定 = marker + 可见英文 `## Project overrides` + 斜体注（用户选 B）。已 stamp
> `~/.flightdeck/checklists/{comments,commits,subagent-guide}.md`（各 marker 计数=1）。验证:stamp 在
> marker 以下 → 母库 shared 指纹不变 → 本仓两副本仍 `in-sync`（`--sync-status` 实证）。

**目标**:给 `~/.flightdeck` 里**打算被 vendor**的 shared 文件补 canonical stub 收尾。
现有：`checklists/comments.md`、`checklists/commits.md`、`checklists/subagent-guide.md`
（逐个确认是否 vendorable；纯内部母库文件不动）。

- stub 文本逐字用上面的 canonical 块。
- 确认 `shared_fingerprint` 仍只算 marker 以上 → 补 stub **不改**母库 shared 指纹
  （Task 1 的 fixture 已覆盖；这里手验一个文件 stamp 前后 `--sync-status` 对消费端的判定不翻车）。
- **Verify**:对本仓消费副本跑 `--sync-status`，stamp 母库后应判 `stale`（因为母库 body 现在多了
  marker 以下内容？——不,stub 在 marker 以下不进指纹,故应仍 `in-sync`;若变 `stale` 说明指纹边界
  算错,回 Task 1 修)。

## Task 3 — 本仓 vendored 副本对齐 ✅ done 2026-06-23

> commits.md 已有 marker + 中文项目段「## 项目覆盖」(consumer-owned) → **不动**(不拿英文 canonical
> 覆盖本地化项目段)。comments.md 原本全无 marker → 补 marker + 同款中文空项目段(对齐本仓既有约定,
> 非英文 canonical)。两者 `--sync-status` 仍 `in-sync`。**未 commit。**

**目标**:本仓 `flightdeck/checklists/comments.md`、`commits.md` 收敛到「marker + canonical stub」形。
`commits.md` 已手加 marker + 一段 `### 7 …` 项目内容 → **保留其项目内容**,但把 stub 标题/提示语
对齐 canonical（项目实质内容在 stub 之下）。`comments.md` 当前无 marker → 补 marker + stub。

- 用 `--sync-pull`(机械 splice)处理 shared 段,marker 以下手工对齐 stub 包裹。
- **Verify**:`--sync-status` 两文件 `in-sync`;`--verify-pending` 无新债;diff 只动预期区域。

## Task 4 — promote(mode C)re-stamp 母库 ✅ done 2026-06-23

> `skills/sync/SKILL.md` mode-C 步骤 2 + 设计 doc mode-C 均加「上提后给母库副本补 canonical 锚+stub」。

**目标**:promote 把 consumer shared body 上提母库后,**给母库补回 marker + canonical stub**,
否则上提的母库文件退化成无 marker,破坏不变量。mode C 是 sync SKILL 编排的 AI 步 → 改
`skills/sync/SKILL.md` mode-C 散文,显式要求 promote 末尾 stamp stub。

- **Verify**:走查 SKILL mode-C 步骤含「append canonical stub to the master copy」。

## Task 5 — 散文翻转（doc / SKILL / scaffold） ✅ done 2026-06-23

> 翻「母库无 marker」旧约定 → 「可 vendor 母库文件自带锚+stub」于:`skills/sync/SKILL.md`（boundary
> marker 节 + mode-A 状态表 + 报告 banner）、`flightdeck/docs/shared-knowledge-sync.md`（边界锚节 +
> 状态语义 + mode A/C + frontmatter summary/last_updated）、**外加** plan 未列的两处遗漏断言
> `skills/preflight/protocol.md`、`skills/preflight/templates.md`。scaffold **无示例 vendored 文件 → 无对象可改，跳过**。

**目标**:把「母库文件不带 marker」的旧约定翻成「**可 vendor 的**母库 shared 文件应以 marker + stub 收尾」。

- `docs/shared-knowledge-sync.md`:边界锚节(现第 37 行「母库自己的文件通常无锚」)+ 模式 B/C 改写;
  `last_updated` 2026-06-23;若触发 `when_to_update` 条件确认 status。
- `skills/sync/SKILL.md`:`## The boundary marker`、mode-B、mode-C、Don't-do 同步。
- `scaffolds/full/**`:若 scaffold 带示例 vendored 文件,示范 marker + stub 收尾。
- 发布面一律英文。
- **Verify**:doc/SKILL 不再出现「master files carry no marker」式断言;scaffold 示例含 stub。

## Task 6 — walkaround 纳入 WARN ✅ done 2026-06-23

> `skills/walkaround/SKILL.md` Audit 15 加 `marker-missing` → WARNING「local additions will be
> overwritten on next pull — add the project-specific marker before syncing」。

**目标**:`skills/walkaround/SKILL.md` 的 sync-drift 审计(现 Audit：vendored stale/dangling)
纳入 Task 1 的 `marker-missing`,报 WARN「local additions will be overwritten on next pull —
add the project-specific marker first」。

- **Verify**:walkaround SKILL 散文含该 WARN 来源 + 文案;若 walkaround 有脚本支撑,跑其测试。

---

## 收尾

- 全程 `uv run pytest scripts/tests/` 绿(WSL bash 遮蔽致 `test_hooks.py` 127 = 环境噪音,见 incident)。
- land 时:spec graduate 默认不标(真相折进 `docs/shared-knowledge-sync.md`);本仓只本地 commit,push 需显式批准。
- 未发布前并入当前 3.0 alpha,不另问版本。
