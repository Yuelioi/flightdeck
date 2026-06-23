---
status: done
summary: Rewrite the three-tier (checkpoint/soft-landing/full-landing) + signal 1/2/3 model into the two-phase stage/land model in one coordinated pass across exit-ritual, landing, status, protocol, preflight, templates — model defined in one place, no file edited twice or left self-contradictory.
last_updated: 2026-06-23
implements: specs/2026-06-22-stage-land-lifecycle.md
verify: human-read the 6-file English prose (exit-ritual/protocol/landing/status/preflight/templates/bootstrap) for tone + coherence; then land to graduate the spec to docs/
---

# Stage/land model — one-pass rewrite across the signal/three-tier surfaces

> **For agentic workers:** REQUIRED SUB-SKILL: `superpowers:executing-plans`。逐 task，步骤用 `- [ ]`。这是 **prose 治理改动，无 TDD 单测**——验证 = grep 旧术语清零 + 锚点链接不悬空 + 人读每文件自洽。脚本侧 `## Staged` 投影 **plan 1 已建**、`## Staged` 字段说明 **plan 2 已写**——本 plan **零脚本、零 scaffold**，纯 `skills/` 散文。

**Goal:** 把已敲定的 **stage/land 两段模型**（spec `2026-06-22-stage-land-lifecycle.md`）**一次性**落到三层/signal 模型现在散落的 6 个 `skills/` 面，使「checkpoint ⊂ soft-landing ⊂ full-landing + signal 1/2/3」整套词汇在发布面消失、替换为「stage（每回合自动暂存口）/ land（手动阀门）」，且**模型只在 `exit-ritual.md` 一处定义、其余文件引用它**。

**Architecture（核心纪律 = 单一真相源 + 一次改完）：**
- **`exit-ritual.md` = 模型真相源。** 三层表、signal 1/2/3、Land-readiness、soft-landing banner、checkpoint 子路径、drain 时机——全在这里**重写**为 stage/land。其余 5 个文件**只引用**，不复述模型。
- **本 plan 与 plan 2 的纪律相反。** plan 2 的第一约束是「**不抢先**改三层模型、留 seam」；本 plan 就是来**收口所有 seam**、把模型**一次改完**——因为模型耦合，逐文件改会留下「A 说 stage / B 说 checkpoint」的悬空。所以 6 个文件 + 锚点重命名 + 全部 inbound 链接**在同一 plan 内闭合**。
- **锚点协调（一次改完的硬理由）。** `exit-ritual.md` 的 heading 改名会让所有 inbound `#anchor` 链接悬空。必须按 **§ Anchor map** 同步改 heading + 每个引用它的文件里的链接锚。

**Tech Stack:** Markdown skill 散文（`skills/**`）。验证 = `grep` 旧术语 + `grep` 悬空锚 + 人读。

## Global Constraints

- **发布面英文（铁律）：** `skills/` 散文 / heading / 字段标签 / banner / 示例**一律英文**。spec 是中文设计稿；本 plan 散文中文（dogfood deck 内部），但**所有落进 `skills/` 的内容片段必须英文**。
- **`archive/` 冻结。** `archive/**` 里的旧 `soft-landing`/`full-landing`/`checkpoint`/`signal N` 是**历史记录、不动**（spec 迁移节：旧术语在归档里作冷史留存）。grep 验证一律 `--glob '!**/archive/**'` 排除。
- **本 deck 自身 `flightdeck/{cockpit,docs,incidents}` 不在本 plan 改。** 它们是 dogfood deck 的内容（describe the tool），改 `skills/` 后会被 stale-detection 在 land 时自动翻 `stale`；逐字重写归 **§ Downstream**，非本 plan。
- **模型事实（spec 逐字，落英文时照此）：**
  - **stage** = 每个**执行回合**结束自动跑（无 soft/full 强度判断、无阈值）：分类落知识（待复核 `stale`+`verify:` / 确信 `active`）、标 `done`-not-archived、board drain（Key Context + Pending Review）、**local commit（带 `Flightdeck-Sync:` trailer）**；**不** archive、**不** push。纯对话回合（deck 无改动）→ 不 stage、无 banner。
  - **land**（`/flightdeck:landing`，手动阀门）= archive `done`（Land Routine）+ 翻牌待复核知识（`stale→active` sign-off）+ push（仍 ask）+ 提交**自己这批** archive/翻牌的 commit。
  - **commit 每回合自动**（接受的噪音代价）：stage 侧每回合 commit，land 侧提交自己批次；push 永远 ask（红线不变）。
- **banner：** turn-end 安全可关 banner = **`─── 📥 staged ───`**（新 glyph，与 land 的 🛬 区分；用户已选）。land 仍 `─── 🛬 landing ───`。
- **提交：** 本地 commit（conventional，见 `checklists/commits.md`），逐 task 一 commit；不 push。

## Anchor map（`exit-ritual.md` heading 改名 → 全仓 inbound 链接同步）

> 改 heading 的**同一 task** 内，grep 出所有 inbound `](…exit-ritual.md#<old>)` 并改锚。这张表是 Task 1 与 Task 2–6 之间的契约。

| 旧 heading / anchor | 新 heading / anchor | 语义变化 |
|---|---|---|
| `## Checkpoint — lightweight board-sync subpath` (`#checkpoint--lightweight-board-sync-subpath`) | `## Stage — turn-end persist + board-sync` (`#stage--turn-end-persist--board-sync`) | checkpoint + soft-landing 合并为 stage（每回合无条件） |
| `## Land-readiness check` (`#land-readiness-check`) | `## Readiness — the staged amount` (`#readiness--the-staged-amount`) | 主动 nudge → 被动展示 staged 量 |
| `### Soft-landing banner — the visible safe-to-close signal` (`#soft-landing-banner--the-visible-safe-to-close-signal`) | `### Staged banner — the visible safe-to-close signal` (`#staged-banner--the-visible-safe-to-close-signal`) | 🛬 soft landing → 📥 staged |

已知 inbound 引用（Task 8 grep 复核兜底）：`landing/SKILL.md`、`status/SKILL.md`、`protocol.md`、`templates.md`、`SKILL.md` 均链向上面三个锚之一。

---

### Task 1: `skills/preflight/exit-ritual.md` — 模型真相源重写（primary）

**Files:** Modify `skills/preflight/exit-ritual.md`

**改什么：** 把三层/signal 模型整段重写为 stage/land。逐节：

1. **`## Core principle` 之后的 Decision tree（Step 1–5）**：保留分类/INDEX/graduate/stale 各步，但 Step 5 commit 的措辞从「soft-land 不 commit / full-land 才 commit」改为「**stage 每回合 local commit（带 `Flightdeck-Sync:` trailer）**」。Step 3c 的「landing/soft-landing = single on-exit ritual」→「**stage = the single on-exit ritual**（每回合）」。
2. **`## Checkpoint — lightweight board-sync subpath` → `## Stage — turn-end persist + board-sync`**（见 Anchor map）：
   - 删三层表（checkpoint ⊂ soft-landing ⊂ full landing）。换成**两段说明**：stage（每回合自动：persist 知识 + 标 done-not-archived + board drain + **commit**；不 archive/push）vs land（手动阀门）。
   - 「Three tiers, one landing」整段 → 「**Two phases: stage (auto, every turn) and land (manual valve)**」。
   - checkpoint 的「exactly two board writes / no commit」段 → stage 的动作清单（含 commit）。删「Why no commit」整段（commit 现在每回合做）——换成「**Why commit every turn**」简述（撤回无风险 / git 追踪 / 噪音已接受；引 spec tradeoff）。
   - 保留「mechanical half welded by turn-end hook」段（hook 焊 `## In Progress`+INDEX+`## Staged` AUTO；judgment 半 = 知识分类/drain/`## Next`/commit 归 AI）。
3. **`### Soft-landing banner` → `### Staged banner`**（见 Anchor map）：banner 改 `─── 📥 staged ───`；`[Saved]` 行**加 commit hash**（stage commits：`committed locally <sha> (Flightdeck-Sync: <ref>)`）——删旧「no commit hash — soft-landing does not commit」注。`[No change]` 分支保留（无新知识但 board 动仍可 commit → commit 行照出）。纯对话回合无 banner 规则不变。
4. **`## Land-readiness check` → `## Readiness — the staged amount`**（见 Anchor map）：
   - 删 signal 1/2/3 三信号体系。重写为：**land 纯手动**，无自动触发；**readiness = 被动展示 staged 量**（`## Staged` 派生视图的条数），preflight 入口报一行中性 staged count（无 ⚠/nudge）。
   - 删「signal 1 auto-landing end-of-turn debounced」「signal 2 reported by preflight」「signal 3 fires a soft-landing」全部 signal mechanics。
   - 删「soft-landing dedup is stateless」整段（无 signal 3 即无此去重问题）；保留「Stop hook 只焊 AUTO 区」澄清（改 stage 语境）。
   - 「Deliberate gap (YAGNI)」段：state-only / 无知识增量回合**现在也 stage + commit**（不再是 gap），此段删或改为「stage 每回合无条件覆盖，无 mid-session watermark 需求」。
5. **`## Land Routine`**：原样保留（搬档 + edge 重写机械逻辑不变），仅触发措辞从「signal 1 自动 / 显式 landing」收窄为「**仅显式 land（阀门）**」。「Landing failure does not roll back done」保留。
6. **`## Self-asserting done` / `### Resolving a verify debt` / `## Hanging Tasks` / `## INDEX regeneration` / `## Cockpit update` / `## Classification heuristics`**：把内嵌的 `soft-landing`/`checkpoint`/`full landing` 词替换为 stage/land；**`## Cockpit update` 的 Accumulator-drain 段**：drain「runs at **landing**, not at the mechanical checkpoint」→「runs at **stage**（每回合）」（**这是 plan 2 templates seam 的真相源端**）。

- [ ] **Step 1: 重写 `## Stage` 段**（前 `## Checkpoint`）：删三层表，写 stage/land 两段 + commit-every-turn。
- [ ] **Step 2: 重写 `### Staged banner` 段**（前 soft-landing banner）：📥 staged + commit hash。
- [ ] **Step 3: 重写 `## Readiness` 段**（前 Land-readiness）：删 signal 1/2/3，写 staged-量被动展示。
- [ ] **Step 4: 改 heading 名 + 同文件内部自引锚**（按 Anchor map 三条）；Decision tree Step 5 commit 措辞 + Step 3c on-exit ritual 措辞 + Accumulator-drain `at stage`。
- [ ] **Step 5: 全文残留术语扫**：
```bash
grep -nEi "soft.?land|full landing|checkpoint|signal [123]|three.?tier" skills/preflight/exit-ritual.md
# 人读：仅剩 stage/land；done-not-archived = staged 常态；commit 每回合；readiness = staged 量被动
```
Expected: 三层/signal 词汇清零（archive 引用 N/A——本文件不在 archive）。
- [ ] **Step 6: commit** — `docs(exit-ritual): rewrite three-tier/signal model into stage/land two-phase`

---

### Task 2: `skills/preflight/protocol.md` — 模型引用对齐 + Brand glyph

**Files:** Modify `skills/preflight/protocol.md`

**改什么（全是引用 Task 1 的下游）：**

1. **`## Rule resolution order` item 3（built-in default）**：删 **`landing` auto-runs on `done`（debounced）** 默认——新模型 land 纯手动。`status` 仍 auto-flip `start`/`done`、**仍 never archive**；新增「**stage auto-runs every turn-end（persist + commit）**」。同节末「no `auto land` toggle」保留。
2. **`### The status / landing seam`**：`→done` 不再是「landing's trigger point / end-of-turn debounce」。改为：**`done` = staged 常态，不触发任何自动 land**；land 由用户开阀门。删「End-of-turn debounce」整条 bullet。`--archivable` / 「Drain, don't accumulate」/「Landing failure does not roll back done」保留（land 阀门内仍适用）。
3. **`## Lifecycle`**：「end-of-turn knowledge increment auto-runs a soft-landing (signal 3)」整段 → 「**every execution turn-end auto-runs stage**（classify + drain + regen changed INDEX + cockpit board + **local commit** + 📥 staged banner；no archive/push）」。turn-end hook 段保留（焊 AUTO）。checkpoint 引用改 stage。
4. **`## Act-report-close loop`**：
   - Reversible 表「`done` archival」「local `git commit`」保留 reversible-auto；确认 archival 现在只在 land 阀门内发生（措辞）。
   - Unified flow output banner 示例 `─── 🛬 soft landing ───` → `─── 📥 staged ───`；`[Saved]` 示例加 commit。
   - Lifecycle recovery 表里 `soft land`/checkpoint 词 → stage。
5. **`## Brand glyphs (per command)`**：表是**命令** glyph；stage/staged 非命令（自动 turn-end，旧 soft-landing 同理也不在表内、glyph 由 exit-ritual 持有）。加一行注：📥 staged = the turn-end stage banner（non-command；glyph authority = [exit-ritual § Staged banner](exit-ritual.md#staged-banner--the-visible-safe-to-close-signal)），避免孤儿 glyph。
6. **`## Exit ritual` 小节 + `## Common mistakes`**：内嵌 soft-landing/checkpoint 词 → stage/land。
7. **inbound 锚**：全文 `](#land-readiness…)`/`exit-ritual.md#checkpoint…`/`#soft-landing-banner…` 按 Anchor map 改。

- [ ] **Step 1: Rule resolution order + status/landing seam**（删 auto-land-on-done；done=staged 常态）。
- [ ] **Step 2: Lifecycle + Act-report-close banner/表**（soft-landing→stage；commit；锚）。
- [ ] **Step 3: Brand glyph 注（📥）+ 残余词扫**。
```bash
grep -nEi "soft.?land|full landing|checkpoint|signal [123]|auto.?land|debounce" skills/preflight/protocol.md
grep -nE "exit-ritual.md#(checkpoint|land-readiness|soft-landing)" skills/preflight/protocol.md   # 悬空锚=0
```
Expected: 模型词清零；无悬空锚。
- [ ] **Step 4: commit** — `docs(protocol): align model refs to stage/land; drop auto-land-on-done; 📥 glyph`

---

### Task 3: `skills/landing/SKILL.md` — Modes 表收口 + commit 归属

**Files:** Modify `skills/landing/SKILL.md`

**改什么（plan-2 handoff #1）：**

1. **`## Modes — full · soft-landing · checkpoint`** → **`## Land — the manual valve`**（或保留 landing 命令、说明它现在是阀门）：删三列 Modes 表（`checkpoint ⊂ soft-landing ⊂ full`）。landing 现在**只有阀门一态**：archive `done` + 翻牌待复核 + 提交本批 + push-ask。说明「每回合 persist/commit 已由 **stage** 做」，引 [exit-ritual § Stage](exit-ritual.md#stage--turn-end-persist--board-sync)。
2. **顶部 description frontmatter（line 3）+ 「checklist face」段**：「session wrap / natural pause / mid-session board refresh」→ 收窄为「the manual land valve: archive done + flip pending-review knowledge live + commit this batch」。
3. **Run-this-checklist Steps**：Step 5「stale detection (landing/soft-landing)」→「stale detection 现由 **stage** 每回合做」——land 步骤里改为引用，**或** land 仍兜底重扫（择一，与 Task 1 Readiness 一致：stage 已每回合扫，land 不必重扫——改为引用 stage）。Step 11 commit：land 提交**自己 archive/翻牌批次**（仍带 `Flightdeck-Sync:` trailer）；每回合 commit 归 stage（措辞）。
4. **Output format banner**：`─── 🛬 landing ───` **不变**（land 仍 🛬）；但若 SKILL 内出现 soft-landing banner 示例 → 删/改 stage。
5. **inbound 锚**：`#checkpoint…`/`#land-readiness…`/`#soft-landing-banner…` 按 Anchor map。

- [ ] **Step 1: Modes 表 → 单一 land 阀门**说明 + description/face 收窄。
- [ ] **Step 2: Steps（stale→引用 stage；commit 批次归属）+ 锚改**。
- [ ] **Step 3: 扫**：
```bash
grep -nEi "soft.?land|checkpoint|modes|signal [123]" skills/landing/SKILL.md
grep -nE "exit-ritual.md#(checkpoint|land-readiness|soft-landing)" skills/landing/SKILL.md
```
Expected: Modes/三层/soft-landing 清零；land = 阀门；无悬空锚。
- [ ] **Step 4: commit** — `docs(landing): land = manual valve (archive + flip + batch commit); per-turn commit is stage's`

---

### Task 4: `skills/status/SKILL.md` — 删 signal-1 auto-land（done = staged 常态）

**Files:** Modify `skills/status/SKILL.md`

**改什么（plan-2 handoff #2）：**

1. **`## Step 7 — land-readiness (signal 1)` 整段删/重写**：`done` flip **不再 queue landing**。改为：`done` 是 staged 常态——status 仅置 `done` + regen `## In Progress`，**不发任何 land 信号、不 debounce、不 nudge**（land 是用户开阀门）。删「end-of-turn debounce」「nudge-on-done deck rule」。
2. **`## Step 6` 末「Emit the land-readiness nudge (Step 7)」**：删该指引（无 signal 1 nudge）。done 后什么都不催；staged 量在 preflight 入口被动展示。
3. **「signal 3 does NOT go through status」段**：signal 3 已不存在 → 删整段；保留「status 只动 `## In Progress` AUTO」事实（改措辞，去 signal 词）。
4. **description frontmatter + Step 1 + Don't-do**：去 signal/auto-land/landing-trigger 措辞；「status no longer archives」「done 后归 land 判断」保留（land 现在纯手动这点更强）。
5. **inbound 锚**：`exit-ritual.md#land-readiness-check` → `#readiness--the-staged-amount`（或删引用，若该句整删）。

- [ ] **Step 1: 删/重写 Step 7**（done≠land 触发；无 signal 1）。
- [ ] **Step 2: Step 6 nudge 指引删 + signal-3 段删 + frontmatter/Don't-do 去 signal 词 + 锚**。
- [ ] **Step 3: 扫**：
```bash
grep -nEi "signal [123]|land-readiness|auto.?land|debounce|nudge" skills/status/SKILL.md
grep -nE "exit-ritual.md#land-readiness" skills/status/SKILL.md
```
Expected: signal/auto-land 清零；done=staged 常态、不触发 land；无悬空锚。
- [ ] **Step 4: commit** — `docs(status): done is normal staged state, no signal-1 auto-land`

---

### Task 5: `skills/preflight/SKILL.md` + `templates.md` + `folder-semantics.md` — 入口 readiness 被动化 + 收 plan-2 seam

**Files:** Modify `skills/preflight/SKILL.md`, `skills/preflight/templates.md`, `skills/preflight/folder-semantics.md`

**改什么：**

1. **`SKILL.md`（plan-2 handoff #6）**：preflight 入口 banner 末行**从催 land 改为被动报 staged 量**。现状（Step 5）：`≥ 5 changed files → ⚠ N unlanded changes — consider /flightdeck:landing`。改为：报 **`## Staged` 视图条数**——`N staged (awaiting land)`，中性、无 ⚠、无 "consider"（land 是用户决定开的阀门）。`> ~5 active threads` 的 focus-loss nudge 保留（与 land 无关）。
2. **`templates.md`（plan-2 handoff #3 + plan-2 留的两处 seam）**：
   - **Accumulator-drain principle** 处的 `<!-- plan-3 seam -->` → 落实：drain「runs at **stage**（every turn）」（真相源端在 Task 1）。删 seam 注。
   - **`## Pending Review` 字段**的 `soft-landing/landing banner` 引用 → `stage/land banner`（📥 staged / 🛬 landing）。删 banner seam 注。
   - **`## Staged (awaiting land)` 字段说明**（plan 2 已写）：复核与新模型一致（派生 + land 改真相源后自然收缩），必要时补一句「stage 每回合 regen，land 改真相源使其收缩」。
3. **`folder-semantics.md`**：1 处 soft-landing/checkpoint 引用 → stage/land。
4. **inbound 锚**：三文件里指向 exit-ritual 三锚的链接按 Anchor map。

- [ ] **Step 1: `SKILL.md` 入口 readiness 行被动化**（staged count，去 ⚠/consider）。
- [ ] **Step 2: `templates.md` 收两处 seam**（drain at stage / banner 命名）+ `## Staged` 字段复核。
- [ ] **Step 3: `folder-semantics.md` 1 处 + 三文件锚改 + 扫**：
```bash
grep -nEi "soft.?land|checkpoint|signal [123]|plan-3 seam|unlanded changes" skills/preflight/SKILL.md skills/preflight/templates.md skills/preflight/folder-semantics.md
grep -nE "exit-ritual.md#(checkpoint|land-readiness|soft-landing)" skills/preflight/*.md
```
Expected: seam 清零；入口被动报 staged；无悬空锚。
- [ ] **Step 4: commit** — `docs(preflight): passive staged-count readiness; close plan-3 seams (drain-at-stage, banner naming)`

---

### Task 6: `skills/_shared/bootstrap.md` — 跨宿主注入指针对齐

**Files:** Modify `skills/_shared/bootstrap.md`

**改什么（载荷面——这段被注入每个会话的 system reminder）：** 把「execution turn ends with exactly one **soft-landing** banner `─── 🛬 soft landing ───`」「write-gated knowledge → soft-land」「state-only → checkpoint」整套三层措辞 → **stage** 语言：执行回合结束 = 一个 **`─── 📥 staged ───`** banner（persist + board-sync + **local commit**）；`[Saved]`（有知识增量）/ `[No change]`（board 动无新知识）/ 纯对话无 banner。Board-sync 机械半（hook 焊 `## In Progress`+INDEX）vs judgment 半（分类/`## Next`/`Focus`/commit）保留。引向 `/flightdeck:preflight` / protocol 不变。

- [ ] **Step 1: 重写 on-exit 段**（soft-landing/checkpoint → stage；📥 staged；commit 每回合）。
- [ ] **Step 2: 扫**：
```bash
grep -nEi "soft.?land|checkpoint|signal [123]|🛬 soft" skills/_shared/bootstrap.md
```
Expected: 三层词清零；on-exit = 📥 staged + commit。
- [ ] **Step 3: commit** — `docs(bootstrap): turn-end stage banner (📥) replaces soft-landing in the injected pointer`

---

### Task 7: 跨文件自洽 + 锚点闭合 + 全发布面扫（收尾）

**Files:** 只读审；必要时微调前 6 task 的文件。

- [ ] **Step 1: 发布面全扫（archive 排除）**：
```bash
grep -rnEi "soft.?land|full landing|checkpoint|signal [123]|three.?tier|three tiers" \
  skills/ --glob '!**/archive/**'
# 期望:仅剩「stage」「staged」「stage/land」「(no) checkpoint」否定式提及;无遗漏旧术语
```
- [ ] **Step 2: 悬空锚全扫**：
```bash
grep -rnE "exit-ritual.md#(checkpoint--lightweight|land-readiness-check|soft-landing-banner)" skills/
# 期望:0(全部 inbound 已按 Anchor map 改到新锚)
grep -rnE "#(stage--turn-end|readiness--the-staged|staged-banner)" skills/   # 新锚被正确引用
```
- [ ] **Step 3: 人读自洽**——逐文件读：`exit-ritual`(模型源) → `protocol`/`landing`/`status`/`preflight`/`bootstrap`(引用) 无「A 说 stage / B 说 checkpoint」矛盾；commit 归属一致（stage 每回合 + land 批次）；readiness 一致（被动 staged 量）；banner 一致（📥 staged / 🛬 landing）。
- [ ] **Step 4: commit（若有微调）** — `docs(stage-land): final cross-file coherence + anchor closure sweep`

---

## 完成标志

- `skills/**`（archive 外）的「checkpoint/soft-landing/full-landing + signal 1/2/3 + three-tier」整套词汇**清零**，替换为 stage/land 两段。
- 模型**只在 `exit-ritual.md` 定义**；`protocol`/`landing`/`status`/`preflight`/`bootstrap` 只引用，无复述、无矛盾。
- **commit 每回合归 stage**（带 `Flightdeck-Sync:` trailer）、archive/翻牌归 land 阀门、push 仍 ask。
- **land 纯手动**（删 signal-1 auto-land、删 auto-land-on-done 默认）；**readiness = 被动展示 staged 量**（preflight 入口中性报 count）。
- turn-end banner = **`─── 📥 staged ───`**（含 commit hash）；land banner 仍 🛬。
- Anchor map 三个 heading 改名 + 全部 inbound 链接闭合，**零悬空锚**。
- plan 2 留的两处 `<!-- plan-3 seam -->`（templates drain 时机 + banner 命名）**收口删除**。

## Downstream（**不在本 plan**——本 plan 只动 `skills/`）

land 时这些会被 stale-detection 自动翻 `stale`，逐字重写另起 follow-on（或下次 land 顺手）：

1. **`flightdeck/docs/session-flow.md`**（~20 hits）——describe 会话生命周期，三层/signal 描述需重写为 stage/land。
2. **`flightdeck/docs/spec-lifecycle.md`、`cross-host-hooks.md`**——少量 checkpoint/soft-landing 引用。
3. **`flightdeck/incidents/soft-landing-knowledge-defer-drift.md`**——其核心教训「别把知识增量 defer 到批 landing」在新模型下**被 stage 结构性强制**（每回合 persist），原 incident 部分失效：land 时复核——加 `## [Case]` 说明「stage 每回合 persist 使此失败模式结构性消失」或翻 `obsolete`（用户定）。
4. **`README.md` / `README.zh.md` / `CHANGELOG.md`**——卖点/术语面的 soft-landing 提及；按 `incidents/outer-ring-docs-drift.md`（recur:2）的外环同步纪律单独走。
5. **`AGENTS.md`**——由 cockpit 经 `/flightdeck:emit-agents-md` 重生，非手改。
6. **`scaffolds/full` 的 cockpit 模板**——`## Staged` section plan 1 已建；若模板里有三层散文注释，顺带（本 plan 未纳入——确认 scaffold 无 signal 散文即可，有则补一 task）。
