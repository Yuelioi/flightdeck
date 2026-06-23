---
status: active
summary: Narrowed to the only surfaces touchable without contradicting the still-three-tier exit-ritual: walkaround Audit 13 done-but-unlanded flip (substantive, self-contained) + templates.md ## Staged field doc. status Step 7 (= signal-1 auto-land) and landing (Modes/banner/commit) are signal-coupled → moved to plan 3 with exit-ritual, so the three-tier/signal model is rewritten once, in one place. exit-ritual/protocol/preflight stay plan 3.
last_updated: 2026-06-23
implements: specs/2026-06-22-stage-land-lifecycle.md
---

# Stage/land prose rewrite — independent surfaces (plan 2)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。逐 task，步骤用 `- [ ]`。这是 prose 治理改动，**无 TDD 单测**——验证 = grep 旧术语 + 人读一遍连贯。

**Goal:** 把已敲定的 **stage/land 模型**（spec `2026-06-22-stage-land-lifecycle.md`）落到**不重写三层/ signal 模型**就能安全改的散文位：walkaround Audit 13 的 done-but-unlanded 翻转（实质）、status / templates 的轻触 + plan-3 seam。

**Architecture:** 纯发布面英文散文，零代码。**反矛盾纪律（核心）**：三层模型（checkpoint/soft-landing/full-landing + signal 1/2/3）的真相源是 `exit-ritual.md`，归 **plan 3**。本 plan **不抢先**把别处改成与 exit-ritual 现状硬矛盾的措辞（例：不在 templates 写「drain at stage」，因 `stage` 仪式要等 plan 3 在 exit-ritual 定义——会造成「templates 说 stage / exit-ritual 说 checkpoint」的悬空引用）。凡耦合处 → 做**自洽的安全部分** + 留 `<!-- plan-3 seam: … -->`。

**Tech Stack:** Markdown skill 散文 + `skills/preflight/templates.md`。验证 = `grep` + 人读。

## Global Constraints

- **发布面英文：** `skills/` 散文 / heading / 字段标签 / 示例**一律英文**。spec 是中文设计稿，落 skill 必须英文。
- **模型事实（spec 逐字）：** stage = 每回合自动（落知识：待复核 `stale`+`verify:` / 确信 `active`；标 `done`-not-archived；board drain；local commit）；land（`/flightdeck:landing`）= 阀门（archive + 翻牌 + push-ask）；**`done`-not-archived 是 stage 正常常态、非债**。
- **反矛盾纪律（本 plan 第一约束）：** 三层/ signal 模型的重写**全归 plan 3**（landing Modes 表/banner/commit 归属 + exit-ritual + protocol + preflight 一起改，模型只在一处、一次改完）。本 plan 任何会与「exit-ritual 现状」硬矛盾的措辞 → **不写**，留 seam。
- **真·安全 vs 移 plan 3：**
  - **walkaround Audit 13**（done-but-unlanded 翻转）：自洽审计行为，不引用三层模型定义 → **做满**（本 plan）。
  - **templates `## Staged` 字段说明**：documenting plan-1 建好、现实存在的 section，不触 signal 模型 → **安全做**；同文件的 drain 时机 / banner 归属耦合 signal → 只留 seam，不写「at stage」。
  - **status Step 7 = signal-1 auto-land**：碰它必造矛盾（删 auto-land↔exit-ritual / 留 auto-land↔新模型）→ **整段移 plan 3**，不在本 plan 改。
- **提交：** 本地 commit（conventional，见 `checklists/commits.md`），不 push。
- **只读不改的邻居：** `exit-ritual.md` / `protocol.md` / `preflight/SKILL.md` / `landing/SKILL.md` 是 plan 3 的地盘——本 plan **不编辑**它们；本 plan 文件里指向它们的链接锚保持有效（届时 plan 3 收口）。

---

### Task 1: `skills/walkaround/SKILL.md` — Audit 13 done-but-unlanded 翻转（实质、安全）

**Files:**
- Modify: `skills/walkaround/SKILL.md`（Audit 13 line ~48；description frontmatter line 3 顺带）

**改什么（spec § walkaround 语义翻转 + Open Q5）：** Audit 13 现状把 `status: done` in specs/plans 的「landable done」报 INFO「run /flightdeck:landing」——即把 done-not-archived 当待办催。翻转为：

1. `done`-not-archived 是 **stage 的正常输出**，walkaround **不再当债 / 不催 land**。
2. 改报 **staging 异常**（spec Open Q5 的可操作判定）：
   - `## Staged` 派生与真相源不一致 = `flightdeck_index --check` 的 `cockpit:staged` drift（手改 INDEX 未 regen / 脚本 bug）→ WARNING；
   - pending-review 知识（`stale`+`verify`）与已 `archive/` 同 relpath 矛盾（既 stale-in-place 又有 archived 副本）→ WARNING。
3. **blocked done**（有 active `implements:` inbound edge）这支**保留为 INFO**，但措辞从「去 land」改为中性「inbound edge 未结，archive 受阻」（这是真依赖未结，非 staging 正常态）。
4. **description frontmatter**（line 3）`(INFO) done-but-unlanded` 列举 → 改为「staging 异常（派生↔真相源 drift / pending-review↔archive 矛盾）」。

> 自洽性：Audit 13 是 walkaround 自己的审计行为，不引用 exit-ritual 的三层模型定义 → 改它不与 plan 3 现状矛盾。

- [ ] **Step 1: 重写 Audit 13**（done-not-archived 不催；新增 staging-异常两条判定；blocked-done 中性化）。
- [ ] **Step 2: 改 description frontmatter**（line 3）列举项。
- [ ] **Step 3: 验证**

```bash
grep -nE "done-but-unlanded|landable done|run ./flightdeck:landing|unlanded" skills/walkaround/SKILL.md
# 人读：Audit 13 不再把 done-not-archived 当债;staging 异常两条有可操作比对键(cockpit:staged drift / archive 同 relpath)
```
Expected: 「done 没归档 = 去 land」语义清零；剩 staging 异常审计 + 中性 blocked-done。

- [ ] **Step 4: commit**

```bash
git add skills/walkaround/SKILL.md
git commit -m "docs(walkaround): done-not-archived is normal staging, audit only staging anomalies"
```

---

### Task 2: `skills/preflight/templates.md` — `## Staged` 字段说明（安全）+ drain 时机 seam（轻触）

**Files:**
- Modify: `skills/preflight/templates.md`（cockpit 字段段 line ~336-346）

**改什么：**

1. **新增 `## Staged (awaiting land)` 字段说明（安全、现实存在）：** plan 1 已建该 section + AUTO 投影。templates.md 补一条「是什么」：派生自 `done`-not-archived workflow + `stale`-with-`verify` 知识；不可手编（AUTO）；land 改真相源后随 regen 自然收缩（与 `## In Progress` 同构）。**这条不依赖 exit-ritual，安全做满。**
2. **drain 时机（line ~341 Accumulator-drain principle）**：现写「draining runs at **landing**, not at the mechanical checkpoint」。新模型要把 drain 下放到 stage——但 `stage` 仪式由 plan 3 在 exit-ritual 定义。**本 plan 不抢写「at stage」**（会悬空），只加 `<!-- plan-3 seam: drain timing moves landing→stage when exit-ritual defines the stage ritual (plan 3) -->`。
3. **Pending Review 字段（line ~340）**的 `soft-landing/landing banner` 引用：同属 banner 归属（plan 3 定 stage banner）→ 留 seam，不改词。

> 纪律：只做 `## Staged` 字段说明（现实成立）；drain/banner 措辞留 seam，不抢先写未定义概念。

- [ ] **Step 1: 加 `## Staged` 字段说明**（按「改什么 1」）。
- [ ] **Step 2: drain principle + Pending Review banner 引用处各加 plan-3 seam**（不改词）。
- [ ] **Step 3: 验证**

```bash
grep -nE "## Staged|Staged \(awaiting|plan-3 seam|drain" skills/preflight/templates.md
# 人读：## Staged 字段有「派生+自然收缩」说明;drain/banner 处留 seam、未写悬空的「stage」概念
```
Expected: `## Staged` 字段就位；drain/banner 处 seam 就位、无悬空 stage 引用。

- [ ] **Step 4: commit**

```bash
git add skills/preflight/templates.md
git commit -m "docs(templates): document ## Staged field; seam drain-timing move to plan 3"
```

---

### Task 3: 跨文件一致性扫 + plan-3 seam 清单

**Files:** （只读审，必要时微调本 plan 的 2 个文件）

- [ ] **Step 1: 扫**

```bash
grep -rnE "done-but-unlanded|landable done|plan-3 seam" \
  skills/walkaround/SKILL.md skills/preflight/templates.md
```
Expected: walkaround 的 done-但-unlanded 当债语义已清；templates 的耦合处都留了 seam。

- [ ] **Step 2: seam 清单**——汇总本 plan 留下的所有 `<!-- plan-3 seam -->`（templates drain 时机 + banner 归属），连同**已知归 plan 3 的整块**（`landing` Modes 表/banner/commit 归属、`status` Step 7 = signal-1 auto-land、`exit-ritual`/`protocol`/`preflight`），写一份「plan 3 待收口」清单进 spec 的 plan-3 范围备查。
- [ ] **Step 3: 人读自洽**——两个文件改完后，单独读各文件不与 `exit-ritual.md`/`landing/SKILL.md`/`status/SKILL.md` 现状硬矛盾（walkaround 自洽；templates 仅 `## Staged` 文档+seam）。
- [ ] **Step 4: commit（若有微调）**

```bash
git add -A
git commit -m "docs(stage-land): plan-2 consistency sweep + plan-3 seam list"
```

---

## Handoff to plan 3（plan 2 punt 的耦合面，逐项交接）

plan 2 只做了「不碰三层/ signal 模型就安全」的两面（walkaround Audit 13 + templates `## Staged` 文档）。以下是 plan 2 **刻意没动**、留给 plan 3 一次改完的清单（plan 3 = 三层/ signal 模型在一处重写）：

1. **`skills/landing/SKILL.md`** — `## Modes` 三层表（full/soft/checkpoint）→ 单一 land 阀门；`soft-landing` banner 归属 → stage；commit 归属（每回合 commit 移 stage，land 仅提交自己 archive/翻牌批次）。
2. **`skills/status/SKILL.md`** — Step 7「land-readiness (signal 1)」= done flip 默认自动 landing；新模型取消 signal-1 自动 land（done 是 staged 常态、不自动 land）；line ~75 的 nudge 引用同步；signal 3 说明随 signal 体系一起收口。
3. **`skills/preflight/templates.md`** — drain 时机（Accumulator-drain principle：`runs at landing, not at the mechanical checkpoint`）→ drain 下放 **stage**；`## Pending Review` 字段里 `soft-landing/landing banner` 引用 → stage/land banner。（plan 2 留原措辞——对现模型正确——不塞 inline seam，由本清单交接。）
4. **`skills/preflight/exit-ritual.md`**（plan 3 主文）— signal 1/2/3 整体重设计 + 三层→stage/land + stage banner + drain 下放主文。
5. **`skills/preflight/protocol.md`** — Act-report-close loop + readiness 重设计（land 纯手动后 readiness = staged 量被动展示）+ Land Routine 触发时机。
6. **`skills/preflight/SKILL.md`** — 入口 readiness 报告：从「催 land」→「报 staged 量供用户决定开阀门」。

> 强依赖（spec Open Q3）：1/2/4/5/6 都绕 signal/readiness 概念，**必须一起敲定**，不可逐条删。plan 3 起草时以此清单 + spec「受影响协议面」+ Open Q3/Q5 为输入。

## 完成标志

- walkaround Audit 13 翻转完成：done-not-archived 不再当债，改审 staging 异常（Open Q5 判定就位）。
- templates `## Staged` 字段说明就位；同文件 drain/banner 耦合处留 seam（不写悬空「stage」）。
- 本 plan 不引入任何与 `exit-ritual.md`/`landing/SKILL.md`/`status/SKILL.md` 现状硬矛盾的措辞。
- plan-3 待收口 seam 清单成形。

**不在本 plan 内**（plan 3，三层/ signal 模型一次改完，避免任何文件被改两遍或自相矛盾）：`skills/landing/SKILL.md`（Modes 表 + banner + commit 归属）、`skills/status/SKILL.md`（Step 7 = signal-1 auto-land：done 不再自动 land）、`exit-ritual.md`（signal 1/2/3 重设计 + 三层→stage/land + stage banner + drain 下放主文）、`protocol.md`（Act-report-close + readiness 重设计 + Land Routine 触发）、`preflight/SKILL.md`（入口 readiness = staged 量被动展示）。
