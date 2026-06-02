---
status: done
implements: specs/2026-06-01-flightdeck-1.2-index-status-design.md
---

# flightdeck 1.2 — INDEX + 显式 status 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Steps use `- [ ]` checkboxes.

**Goal:** 把当前分支(已实现 2.0 正交模型)简化回退到 1.2——文件夹=kind、frontmatter=status、每目录+根 INDEX.md、cockpit 纯焦点、命令优先读 INDEX——并整理本仓库自身 + 发布为 1.2.0。

**Architecture:** 纯 markdown 约定,无测试;验证 = ripgrep + 结构核对。**全量重写**每个 skill 到 1.2 目标(不逐句撤 2.0)。三相:A 核心约定 skill,B 入口 skill(读 INDEX),C 发布物(scaffolds/MIGRATION/README/版本/CHANGELOG),D 本仓库整理 + 发布 STOP。

**权威设计:** `flightdeck/specs/2026-06-01-flightdeck-1.2-index-status-design.md`(下称 spec;当前 untracked)。每个重写 task 先读 spec 对应 §。

**起点状态:**
- 分支 `v2-entry-collapse-and-rules`,46 commits(2.0 skills/scaffolds 已提交)。
- 工作树:2.0 自迁移未提交(cockpit/AGENTS 2.0、本仓库 `landed/work-items/` 布局、VERSION+5manifest=2.0.0、README 2.0 版)。
- untracked:`flightdeck/specs/`(1.2 spec)、`flightdeck/landed/work-items/`(迁入的设计文档)、`flightdeck/landed/HISTORY.md`、`flightdeck/sketches/`、`tmp/`(审核)。

**全局约定:**
- 不 `git add -A`;只 add 各 task 指名文件(保护 untracked spec/tmp)。
- 全程在本分支;**Phase D 末 STOP**,发布(tag/push/merge)等用户确认。
- "验证移除/存在" = ripgrep 断言。skill 文件是英文,新内容写英文,grep 用英文关键词。
- 术语统一:`status`(标签)、`implements`、`INDEX.md`、`incidents/`、`debriefs/`、`specs/`/`plans/`/`sketches/`;**禁用** `kind:`frontmatter、`form`、`work-item`/`work-items`、`task`(作 kind)、`## Tasks`、`transition table`、转移动词、bundle README。

---

## Phase A — 核心约定 skill(`skills/workflow/`)

### Task A1: SKILL.md 重写为 1.2
**Files:** Modify `skills/workflow/SKILL.md`

- [ ] **Step 1** 读 spec §2–§7。重写这些节为 1.2:
  - `## Data model`:**文件夹 = kind(隐含,不写 frontmatter)**;**文件 frontmatter = status**(必填)+ 知识路由字段 + plan 的可选 `implements:`。无 kind/form。
  - `## Status`:取值固定(工作流 `pending/active/awaiting-review/blocked/done/scrapped`;知识 `active/obsolete/superseded`)+ 推荐流转图(`pending→active→awaiting-review→done`;`active↔blocked`;`→scrapped`)。**无转移表/转移动词**。AI 只建议下一状态、用户随时改。
  - `## INDEX`:每目录(含 sketches)一个 INDEX.md = 派生索引(文件+status+摘要);根 `flightdeck/INDEX.md` = 子目录导览+全局状态摘要(可降级组件)。**命令优先读 INDEX,按需才下钻读单文件**。
  - `## Folder map`:`sketches/ specs/ plans/ incidents/ checklists/ charts/ debriefs/ landed/` + cockpit/rules/INDEX。
  - `## Commands`:preflight/landing/walkaround/emit-agents-md(纯仪式,无转移动词)。
  - `## Lifecycle`:sketch→spec(promote=写设计)→plan(implements spec);location active↔landed 派生;无 form。
  - authority order:`项目规则 > rules.md > cockpit.md > 各目录(specs/plans/...) > landed/`。
  - 删除一切 form/work-item/work-items/kind-frontmatter/transition-table/转移动词/bundle 内容。
- [ ] **Step 2** 验证移除:`rg -ni 'form:|work-item|work-items|kind: (work-item|task|spec|plan)|transition table|## Tasks' skills/workflow/SKILL.md` → 无。
- [ ] **Step 3** 验证存在:`rg -n 'Folder = kind|文件夹.*kind|status|INDEX|incidents|debriefs|read the INDEX' skills/workflow/SKILL.md`(英文等义)。
- [ ] **Step 4** commit:`git add skills/workflow/SKILL.md && git commit -m "feat(1.2): SKILL.md — folder=kind, status label, per-folder+root INDEX, commands read INDEX"`

### Task A2: folder-semantics.md 重写为 1.2
**Files:** Modify `skills/workflow/folder-semantics.md`

- [ ] **Step 1** 读 spec §3/§5/§8/§9/§10。重写:目录布局(specs/plans/incidents/debriefs);每目录 INDEX + 根 INDEX(格式+AUTO区+重生成范围+charts特殊不计status);**无子文件夹 bundle**(多文件主题=同目录多文件+INDEX手工分组;charts/ 外部项目例外);README→INDEX(约定内;仓库根 README.md 不受影响);spec↔plan(implements 单向,spec 无反向字段)。删 work-items/锚/bundle/form。
- [ ] **Step 2** 验证:`rg -ni 'work-item|bundle|form:|reading_order' skills/workflow/folder-semantics.md` → 无(除非历史叙述);`rg -n 'specs/|plans/|incidents/|debriefs/|INDEX.md|charts/.*INDEX' skills/workflow/folder-semantics.md` → 有。
- [ ] **Step 3** commit:`git add skills/workflow/folder-semantics.md && git commit -m "feat(1.2): folder-semantics — specs/plans + per-folder INDEX, no bundle subfolders"`

### Task A3: templates.md 重写为 1.2(核心新内容全文)
**Files:** Modify `skills/workflow/templates.md`

- [ ] **Step 1** 读 spec §3/§4/§5。模板集替换为(全文):

````markdown
## spec / sketch frontmatter
```markdown
---
status: active        # spec: pending/active/awaiting-review/blocked/done/scrapped — sketch: active/scrapped only
---
```

## plan frontmatter
```markdown
---
status: active
implements: specs/<x>.md   # optional; relative to flightdeck root; absent → walkaround flags "orphan plan"
---
```

## knowledge frontmatter (incident / checklist / chart / debrief)
```markdown
---
status: active            # active / obsolete / superseded
when_to_read: <one-line trigger>
applies_to: [<tag>, ...]
last_updated: YYYY-MM-DD
# superseded only: superseded_by: <path>
---
```

## INDEX.md — per folder
```markdown
# <folder>/ — INDEX

<!-- AUTO:<folder> -->
- [<file>](<file>) — <status> — <one-line summary>
<!-- /AUTO -->

<!-- optional hand-maintained area below (grouping notes); AI does not touch -->
```
(Knowledge folders add `when_to_read` / `applies_to` to each row. `implements` does NOT go into the INDEX.)

## INDEX.md — root (flightdeck/INDEX.md)
```markdown
# flightdeck — INDEX

<!-- AUTO:root -->
- specs/ — 3 (2 active, 1 done)
- plans/ — 2 (1 active, 1 blocked)
- incidents/ — 1 active
- checklists/ — 1 active
- charts/ — 2 projects imported
- debriefs/ — 1 active
- sketches/ — 4
<!-- /AUTO -->
```

## status flow (recommended, not enforced)
```
pending → active → awaiting-review → done
active ↔ blocked
any active state → scrapped
knowledge: active → obsolete | superseded
```
````

  并:更新 cockpit.md 模板(纯焦点:Last updated/Active focus/Next session/Hanging tasks,**无 In flight**);删除 work-item/task/## Tasks/转移表/bundle README 模板。
- [ ] **Step 2** 验证:`rg -n '## spec / sketch frontmatter|## plan frontmatter|## knowledge frontmatter|## INDEX.md — per folder|## INDEX.md — root|status flow' skills/workflow/templates.md`;`rg -ni 'work-item|## Tasks|reading_order|form:' skills/workflow/templates.md` → 无。
- [ ] **Step 3** commit:`git add skills/workflow/templates.md && git commit -m "feat(1.2): templates — minimal frontmatter + INDEX.md (folder & root) + status flow"`

### Task A4: exit-ritual.md 重写为 1.2
**Files:** Modify `skills/workflow/exit-ritual.md`

- [ ] **Step 1** 读 spec §4/§5/§6。重写 landing:分类新知识→对应目录(设计→specs/、计划→plans/带 implements、教训→incidents/、流程→checklists/、外部→charts/、复盘→debriefs/);**只重生成本会话有变动目录的 INDEX**(新增/改/移/land/status变),其余 INDEX 只读;AI 可建议 status 下一态、用户确认;land 终态→landed/;hanging tasks 手工维护。删转移表驱动/work-item lifecycle。
- [ ] **Step 2** 验证:`rg -ni 'transition table|work-item|## Tasks|advance' skills/workflow/exit-ritual.md` → 无;`rg -n 'INDEX|regenerate|implements|incidents|debriefs' skills/workflow/exit-ritual.md` → 有。
- [ ] **Step 3** commit:`git add skills/workflow/exit-ritual.md && git commit -m "feat(1.2): exit-ritual — classify to specs/plans/.., regenerate changed-folder INDEX"`

---

## Phase B — 入口 skill(读 INDEX)

### Task B1: preflight/SKILL.md 1.2
**Files:** Modify `skills/preflight/SKILL.md`
- [ ] **Step 1** 读 spec §5.1/§8。reconcile 读根 INDEX + cockpit;**路由目录改读 `checklists/INDEX.md` + `incidents/INDEX.md`(或根 INDEX)而非逐文件读 frontmatter**,只在要用某条时下钻;1.1.x→1.2 旧布局检测(manifest/logbook/kneeboard/flight-plans/incident-reports/safety-reviews 任一→提示迁移);删 (form,status)/work-item/转移检测。
- [ ] **Step 2** 验证:`rg -n 'INDEX|read the .*INDEX|1.1.x|incidents' skills/preflight/SKILL.md`;`rg -ni 'work-item|form,|transition' skills/preflight/SKILL.md` → 无。
- [ ] **Step 3** commit:`git add skills/preflight/SKILL.md && git commit -m "feat(1.2): preflight reads INDEX (not per-file frontmatter); 1.1.x->1.2 detect"`

### Task B2: landing/SKILL.md 1.2
**Files:** Modify `skills/landing/SKILL.md`
- [ ] **Step 1** 读 spec §4/§5/§6。引用 exit-ritual;明确 INDEX 重生成范围(本会话变动目录);AI 建议 status;land→landed/;hanging 手工;smoke-check 目录用 1.2(specs/plans/incidents/debriefs/...);删 (form,status)/work-items/转移。
- [ ] **Step 2** 验证:`rg -n 'INDEX|regenerate|implements|landed' skills/landing/SKILL.md`;`rg -ni 'work-item|form,|transition|## Tasks' skills/landing/SKILL.md` → 无。
- [ ] **Step 3** commit:`git add skills/landing/SKILL.md && git commit -m "feat(1.2): landing — regenerate changed-folder INDEX, suggest status, land"`

### Task B3: walkaround/SKILL.md 1.2 审计
**Files:** Modify `skills/walkaround/SKILL.md`
- [ ] **Step 1** 读 spec §4/§5。审计集(1.2):① 文件 frontmatter status 必填+值合法(按目录:工作流域/知识域);② **INDEX↔frontmatter 一致**(每目录 + 根,AUTO 区是否反映实际文件+status);③ landed/ 里不应有非终态;④ knowledge `superseded` 须有 `superseded_by`;⑤ **孤儿 plan**(plans/ 下无 implements → INFO);⑥ 知识路由字段缺失;⑦ 流转偏离 → warn 不阻断;⑧ 旧布局路径(flight-plans/incident-reports/safety-reviews/work-items)→ 提示迁移;⑨ 孤儿/stray 文件。删 2.0 状态机/transition/form×status/zombie-task 审计。
- [ ] **Step 2** 验证:`rg -n 'INDEX.*frontmatter|orphan plan|superseded_by|status' skills/walkaround/SKILL.md`;`rg -ni 'transition|form×status|work-item|zombie' skills/walkaround/SKILL.md` → 无。
- [ ] **Step 3** commit:`git add skills/walkaround/SKILL.md && git commit -m "feat(1.2): walkaround — status validity + INDEX consistency + orphan plan"`

### Task B4: emit-agents-md/SKILL.md 1.2
**Files:** Modify `skills/emit-agents-md/SKILL.md`
- [ ] **Step 1** 从 cockpit 渲染 Current focus / Next session / Hanging tasks(去 In flight,因 cockpit 无 In flight);保留 markers/链接前缀/determinism。
- [ ] **Step 2** 验证:`rg -ni 'In flight|form,|work-item' skills/emit-agents-md/SKILL.md` → 无(In flight 块移除);`rg -n 'Current focus|Next session|Hanging' skills/emit-agents-md/SKILL.md` → 有。
- [ ] **Step 3** commit:`git add skills/emit-agents-md/SKILL.md && git commit -m "feat(1.2): emit-agents-md — focus/next/hanging, drop In flight"`

---

## Phase C — 发布物

### Task C1: scaffolds 1.2
**Files:** `scaffolds/full/flightdeck/**`, `scaffolds/minimal/`
- [ ] **Step 1** full:目录占位改 `specs/ plans/ incidents/ debriefs/`(取代 work-items/、incident-reports/、safety-reviews/);每目录加 `INDEX.md`(含 AUTO 区占位)+ 根 `flightdeck/INDEX.md`;cockpit.md 去 In flight;rules.md/landed 保留。minimal 保持 cockpit-only(确认无旧引用)。`git rm` 旧的 work-items/incident-reports/safety-reviews 占位。
- [ ] **Step 2** 验证:`rg -ni 'work-items|incident-reports|safety-reviews|In flight' scaffolds/` → 无;`ls scaffolds/full/flightdeck/specs scaffolds/full/flightdeck/plans scaffolds/full/flightdeck/incidents scaffolds/full/flightdeck/debriefs` + 各 INDEX.md。
- [ ] **Step 3** commit:`git add scaffolds/ && git commit -m "feat(1.2): scaffolds — specs/plans/incidents/debriefs + INDEX.md (folder & root)"`

### Task C2: MIGRATION.md 1.1.x → 1.2
**Files:** Modify `MIGRATION.md`
- [ ] **Step 1** 读 spec §11/§13。把现有 `## 1.1.x → 2.0` 段改为 `## 1.1.x → 1.2`:步骤=移除 manifest/logbook/kneeboard(→cockpit/HISTORY/tmp);`flight-plans/`→`plans/`、`incident-reports/`→`incidents/`、`safety-reviews/`→`debriefs/`;`specs/` 不变;每个制品**文件补 `status:`**;每目录建 `INDEX.md` + 根 INDEX;可选 rules.md。交互+幂等。对照表(1.1.x→1.2)。
- [ ] **Step 2** 验证:`rg -n '## 1.1.x → 1.2|status:|INDEX.md|plans/|incidents/|debriefs/' MIGRATION.md`;`rg -n 'work-items|form|transition|→ 2.0' MIGRATION.md` → 无。
- [ ] **Step 3** commit:`git add MIGRATION.md && git commit -m "docs(1.2): MIGRATION 1.1.x->1.2 (rename + add status + build INDEX)"`

### Task C3: README EN/ZH 1.2
**Files:** Modify `README.md`, `README.zh.md`
- [ ] **Step 1** `rg -n 'work-items|kind|form|transition|In flight' README.md README.zh.md` 找 2.0 残留;改为 1.2:文件夹结构(specs/plans/incidents/debriefs + 各 INDEX + 根 INDEX)、模型介绍(文件夹=kind、frontmatter=status、INDEX=派生视图、cockpit=焦点)、去 form/work-item/transition。EN/ZH 同步。
- [ ] **Step 2** 验证:`rg -ni 'work-items|form axis|transition table|In flight' README.md README.zh.md` → 无;`rg -n 'INDEX|status|specs/|plans/' README.md README.zh.md` → 有。
- [ ] **Step 3** commit:`git add README.md README.zh.md && git commit -m "docs(1.2): READMEs — folder=kind/status/INDEX model (EN/ZH)"`

### Task C4: 版本 2.0.0 → 1.2.0 + CHANGELOG
**Files:** `VERSION`, 5 manifests, `CHANGELOG.md`
- [ ] **Step 1** VERSION + 5 manifest(.claude-plugin/plugin.json+marketplace.json、.codex-plugin/plugin.json、.cursor-plugin/plugin.json、gemini-extension.json)从 `2.0.0` 改 `1.2.0`(全部一致)。
- [ ] **Step 2** CHANGELOG:把 `## [2.0.0]` 条目改为 `## [1.2.0] — 2026-06-01`,内容重写为 1.2:Added(显式 status 元数据、每目录+根 INDEX、命令读 INDEX、rules.md、landed/HISTORY);Changed(cockpit 收敛为焦点、folder=kind/status 显式;incident-reports→incidents、safety-reviews→debriefs;约定内 README→INDEX);Removed(manifest/logbook/kneeboard)。**不提** form/work-item/transition(从未发布)。链 MIGRATION + 设计 spec。
- [ ] **Step 3** 验证:`rg -n '"version"' .claude-plugin .codex-plugin .cursor-plugin gemini-extension.json; cat VERSION`(全 1.2.0);`rg -n '## \[1.2.0\]' CHANGELOG.md`;`rg -n '2.0.0|work-item|form' CHANGELOG.md`(仅历史条目允许)。
- [ ] **Step 4** commit:`git add VERSION .claude-plugin .codex-plugin .cursor-plugin gemini-extension.json CHANGELOG.md && git commit -m "release(1.2): version 1.2.0 + CHANGELOG [1.2.0]"`

---

## Phase D — 本仓库整理 + 发布 STOP

### Task D1: 整理本仓库 flightdeck/ 到 1.2
**Files:** 本仓库 `flightdeck/`
- [ ] **Step 1** 现状:工作树是 2.0 自迁移态(活跃区 `checklists/version-bump.md`、`charts/`(外部)、`sketches/v1x-deferred-ideas.md`;无活跃 spec/plan——历史设计都在 `landed/work-items/`)。1.2 整理(活跃区,landed/ 历史归档**保留不动**):
  - 活跃区无 spec/plan(都 done),故 `specs/`/`plans/`/`incidents/`/`debriefs/` 暂不建(按需);保留 `checklists/`、`charts/`、`sketches/`。
  - 给 `checklists/`、`charts/`、`sketches/` 各建 `INDEX.md`(列其文件+status+摘要;charts/ 标项目导览、不计 status);建根 `flightdeck/INDEX.md`(子目录摘要)。
  - `checklists/version-bump.md`、`sketches/v1x-deferred-ideas.md` 已有 `status`(2.0 自迁移时加的 kind 字段**删掉**——1.2 无 kind);确认只剩 `status`(+ checklist 路由字段)。
  - `cockpit.md`:去任何 2.0 残留措辞(In flight/work-items),确认纯焦点;`AGENTS.md` 重生成(去 In flight)。
  - `landed/work-items/` 历史归档:保留(done 历史,landed 不审计;名字不影响)。`landed/safety-reviews/`→可留或改 `landed/debriefs/`(可选,历史)。
- [ ] **Step 2** 跑 `/flightdeck:walkaround`(1.2 版,B3 完成后)核对本仓库活跃区:status 合法、INDEX↔frontmatter 一致、无旧布局活引用、无 kind 字段残留。
- [ ] **Step 3** 验证:`rg -ni 'kind:|work-item|In flight|form:' flightdeck/cockpit.md flightdeck/checklists/ flightdeck/sketches/ flightdeck/INDEX.md flightdeck/*/INDEX.md` → 无(charts/ 外部材料除外);各 INDEX 存在。
- [ ] **Step 4** **先不 commit**——并入 D2 发布决策(避免提前提交 untracked 设计文档/审核)。

### Task D2: 发布收尾(STOP)
**Files:** 全仓库
- [ ] **Step 1** 全仓 1.2 一致性 grep:`git grep -ni 'work-item|work-items|form:|transition table|## Tasks|incident-reports/|safety-reviews/|flight-plans/' -- skills/ scaffolds/ README.md README.zh.md MIGRATION.md`(只允许 MIGRATION/walkaround 的 legacy-detection 语境)。修任何真残留。
- [ ] **Step 2** 决定 untracked 设计文档/审核去向:`flightdeck/specs/2026-06-01-flightdeck-1.2-...-design.md` + 本 plan(`flightdeck/plans/`)→ done 后归 `landed/`(或保留);`tmp/` 审核是 scratch(gitignore,不提交)。**询问用户**。
- [ ] **Step 3** **STOP — 不 commit/tag/push。** 向用户呈现完整 branch diff + 待决:(a) 提交本仓库整理 + 设计文档去向;(b) `git tag -a v1.2.0` + push --follow-tags + merge main(按 `checklists/version-bump.md`)。仅用户确认后执行;branch 操作前确认不污染 main。

---

## Self-Review
- **Spec coverage:** §2→A1;§3→A1/A2/A3;§4→A1/A3/A4/B3;§5+§5.1→A1/A2/A3/B1/B2/B3;§6→A4/B2;§7→A2/A3;§8→C2/B1;§9→A/B/C;§10→A2/C3;§11→C2;§12→全 plan(撤2.0);§13→C/D;§14→设计已记;§15→D。全覆盖。
- **No placeholder:** 核心新内容(最小 frontmatter ×4、INDEX 模板 ×2、status 流转图)在 A3 给全文;重写类给 1.2 落地要点 + spec § + grep。
- **一致性:** status/implements/INDEX.md/incidents/debriefs/specs/plans/sketches 全 plan 一致,且与 spec 一致;禁用词清单统一。
- **顺序:** A(模型)→B(消费模型的入口 skill,含读 INDEX)→C(发布物)→D(本仓库整理依赖 B3 walkaround;末 STOP)。
- **注意:** 本 plan 自带 `status: active` + `implements:` frontmatter(dogfood 1.2)。
