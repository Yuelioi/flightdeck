---
status: active
summary: Adopt the decided stage/land model across the signal-independent prose surfaces: landing SKILL (move commit out → valve = archive+flip; Modes table → stage/land naming), status SKILL (Step 7 signal-1 nudge → 'done is normal staged, landing available'), walkaround (Audit 13 done-but-unlanded: stop nagging → flag only staging anomalies, Open Q5), templates.md cockpit field docs. Signal/readiness internals + exit-ritual/protocol/preflight stay plan 3; this plan does the structural flips and leaves readiness-wording seams to plan 3.
last_updated: 2026-06-23
implements: specs/2026-06-22-stage-land-lifecycle.md
---

# Stage/land prose rewrite — independent surfaces (plan 2)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans 或 superpowers:subagent-driven-development，逐 task。步骤用 `- [ ]`。这是 prose 治理改动，**无 TDD 单测**——每 task 的「验证」= grep 旧术语清零 + 跨文件读一遍连贯。

**Goal:** 把已敲定的 **stage/land 两段模型**（spec `2026-06-22-stage-land-lifecycle.md`）落到**不依赖 signal 重设计**的 4 个散文面，让它们停止表达旧三层（checkpoint/soft-landing/full-landing）+ 停止把 `done`-not-archived 当债。

**Architecture:** 纯发布面英文散文编辑，零脚本零代码。改动按「文件」切 task。模型事实从 spec 逐字取，不重新设计。**plan 2 只做模型已决定的结构性翻转**；任何依赖「signal/readiness 怎么重设计」的措辞（nudge 文案、入口 readiness 概念）**显式留 plan 3**，本 plan 在接缝处留 `<!-- plan-3 seam -->` 注脚而非硬写。

**Tech Stack:** Markdown skill 散文（`skills/`）+ `skills/preflight/templates.md`。无测试框架；验证 = `grep` + 人读。

## Global Constraints

- **发布面英文：** 所有 `skills/` 散文、字段标签、heading、示例**一律英文**（国际化）。spec 是中文设计稿，落到 skill 必须英文。
- **模型事实（spec 逐字，不再设计）：** ① stage = 每次对话结束自动，落知识（待复核 `stale`+`verify:`，确信 `active`）+ 标 `done`-not-archived + board drain + **local commit（带 `Flightdeck-Sync:` trailer）**；**不做 archive / push**。② land（`/flightdeck:landing`）= 阀门：done 下沉 archive + 待翻牌知识翻 `active`（sign-off）+ push 仍 ask。③ `done`-not-archived 是 **stage 的正常常态**，不是债。
- **plan-2/plan-3 接缝（关键）：** 本 plan **不**重设计 signal 体系 / readiness 概念（那是 plan 3 + exit-ritual/protocol/preflight）。凡遇「nudge 怎么措辞 / 入口 readiness 是什么」→ 落一句**模型层结论**（如「done 可 land，不催」）+ 留 `<!-- plan-3 seam: readiness wording finalized in plan 3 -->`，**不**写 signal-1/2/3 的新机制。
- **commit 归属（本 plan 决定）：** 「砍掉 landing 的 commit」= 砍掉**「每回合知识 auto-commit」**那份职责（它移到 stage）。**land 仍提交它自己的 archive/翻牌批次**（archive 产生文件移动，必须落 commit）——否则 land 留下未提交的 archive 移动。措辞按此。
- **提交：** 本地 commit（conventional，见 `checklists/commits.md`），不 push。
- **只读不改的邻居：** `exit-ritual.md` / `protocol.md` / `preflight/SKILL.md` 是 plan 3 的地盘——本 plan **不编辑**它们；只在本 plan 4 个文件里**指向**它们的链接保持有效即可（链接目标届时由 plan 3 收口）。

---

### Task 1: `skills/landing/SKILL.md` — landing = 阀门，砍每回合 commit + Modes 重写

**Files:**
- Modify: `skills/landing/SKILL.md`

**改什么：**

1. **Modes 段**（`## Modes — full · soft-landing · checkpoint` 三态表）：三层是旧模型，本 plan 把 **landing 自己的呈现**改为「land = 单一阀门动作」。重写为：landing 不再有 full/soft/checkpoint 三态；它是**显式阀门**，每次跑都做同一件事（archive done + 翻牌 pending-review 知识 + 提交该批 + push-ask）。把「stage 每回合自动做的事（知识落盘 / board drain / 每回合 commit）」明确划到 **stage 侧**，并留 `<!-- plan-3 seam: stage 动作的完整定义 + turn-end 触发在 exit-ritual (plan 3) -->`。
2. **Step 11（Commit + push）**：把「每回合知识 auto-commit」职责删除 / 指向 stage；**保留** land 自己的「提交 archive/翻牌批次」+ push-ask。措辞按 Global Constraints「commit 归属」。
3. **通篇术语**：`soft-landing` / `full landing` / `checkpoint`（作为 landing 的模式）→ 改为 stage / land 语汇；凡描述「每回合收尾」一律归 **stage**，凡描述「显式归档阀门」归 **land**。banner 名 `─── 🛬 landing ───` 保留（land 仍出 banner）；`soft landing` banner 归属 stage → 留 seam 给 plan 3（exit-ritual 定 stage banner）。
4. 受影响的 step 编号/链接（`exit-ritual.md` 锚）保持指向有效。

**不在本 task：** signal 1/2/3、land-readiness 主动 nudge 的机制（plan 3）。

- [ ] **Step 1: 重写 Modes 段**为单一阀门语义（按上「改什么 1」），旧三态表删除/折叠。
- [ ] **Step 2: 改 Step 11** commit 归属（按「改什么 2」）。
- [ ] **Step 3: 通篇术语扫**（按「改什么 3」），soft/full/checkpoint-as-mode 清零或转 stage/land。
- [ ] **Step 4: 验证**

```bash
# 旧三层模式词作「landing 模式」的用法应清零（保留的只能是指向 plan-3 文件的链接锚）
grep -nE "soft-landing|full landing|full-landing|checkpoint ⊂|⊂ soft" skills/landing/SKILL.md
# 人读一遍：landing 段是否只描述「阀门 = archive + 翻牌 + 提交该批 + push-ask」，每回合活是否都归 stage
```
Expected: 无「landing 模式三分」残留；commit 段符合归属决定；seam 注脚就位。

- [ ] **Step 5: commit**

```bash
git add skills/landing/SKILL.md
git commit -m "docs(landing): recast landing as the single land valve (stage owns per-turn commit)"
```

---

### Task 2: `skills/status/SKILL.md` — Step 7 signal-1 nudge → 「done 是正常 staged」

**Files:**
- Modify: `skills/status/SKILL.md`

**现状（已对）：** line 14 / Step 6 已写「status no longer archives」「done 留在源文件夹（done-but-unarchived）」——**这部分不动**，它已符合新模型。

**改什么：**

1. **Step 7「land-readiness (signal 1)」**：标题与正文把 `done` flip 触发的**主动催 land**（signal 1）语义，改成「`done`-not-archived 是 stage 的正常输出；landing 阀门可用但**不催**」。**不**写新的 readiness/signal 机制 → 留 `<!-- plan-3 seam: land-readiness/signal model redesigned in plan 3 -->`。标题里 `(signal 1)` 去掉或中性化（signal 体系是 plan 3 的事，status 不该自称 signal 1）。
2. **Step 6 收尾的 land-readiness nudge 引用**（line 75「Emit the land-readiness nudge (Step 7)」）随 Step 7 一并中性化为「done 已 stage、可 land、不催」。
3. 链接到 `exit-ritual` 的 readiness 锚保持有效（目标由 plan 3 收口）。

- [ ] **Step 1: 改 Step 7**（标题去 `signal 1` + 正文转「正常 staged、不催」+ seam 注脚）。
- [ ] **Step 2: 改 Step 6 line ~75** 的 nudge 引用同步中性化。
- [ ] **Step 3: 验证**

```bash
grep -nE "signal 1|land-readiness|nudge" skills/status/SKILL.md
# 人读：status 是否不再把 done 描述成「该去 land 的债」，而是「正常 staged，可 land 不催」；seam 就位
```
Expected: 无「signal 1 主动催」语义；done-not-archived 描述为正常态。

- [ ] **Step 4: commit**

```bash
git add skills/status/SKILL.md
git commit -m "docs(status): done-not-archived is normal staged output, not a land-debt nudge"
```

---

### Task 3: `skills/walkaround/SKILL.md` — Audit 13 done-but-unlanded 翻转

**Files:**
- Modify: `skills/walkaround/SKILL.md`（Audit 13，line ~48；description frontmatter line 3 顺带）

**改什么（spec § walkaround 语义翻转 + Open Q5）：**

1. **Audit 13**（`status: done` in specs/plans → 「landable done」INFO「run /flightdeck:landing」）：翻转为——`done`-not-archived 是 **stage 的正常输出**，walkaround **不再把它当债 / 不催 land**。改为：只在 **staging 异常**时报，按 spec Open Q5 给可操作判定：
   - pending-review 知识（`stale`+`verify`）与已 `archive/` 的同名/同签矛盾；
   - `## Staged` 派生与真相源不一致（手改 INDEX 未 regen / 脚本 bug）——即 `flightdeck_index --check` 的 `cockpit:staged` drift。
   「blocked done」（有 active `implements:` inbound edge）这支仍可保留为 INFO（它是真·依赖未结，不是 staging 正常态）——但措辞从「去 land」改为中性「inbound edge 未结，archive 受阻」。
2. **description frontmatter**（line 3）里 `(INFO) done-but-unlanded` 这串列举 → 改为「staging 异常（派生↔真相源 drift / pending-review↔archive 矛盾）」。
3. 关联：Audit 15（sync drift）已在上一个 plan 加了 `marker-missing`，本 task 不碰。

- [ ] **Step 1: 重写 Audit 13**（按「改什么 1」：done-not-archived 不催；新增 staging-异常判定两条；blocked-done 中性化）。
- [ ] **Step 2: 改 description frontmatter**（line 3）列举项。
- [ ] **Step 3: 验证**

```bash
grep -nE "done-but-unlanded|landable done|run ./flightdeck:landing|unlanded" skills/walkaround/SKILL.md
# 人读：Audit 13 是否不再把 done-not-archived 当债；staging 异常两条判定是否可操作（有比对键）
```
Expected: 「done 没归档 = 去 land」语义清零；剩下的是 staging 异常审计 + 中性 blocked-done。

- [ ] **Step 4: commit**

```bash
git add skills/walkaround/SKILL.md
git commit -m "docs(walkaround): done-not-archived is normal staging, audit only staging anomalies"
```

---

### Task 4: `skills/preflight/templates.md` — cockpit 字段说明对齐 stage/land

**Files:**
- Modify: `skills/preflight/templates.md`（cockpit 字段段，line ~336-346；`current:`/checkpoint 段 line ~92-96）

**改什么：**

1. **`## Pending Review` 字段说明**（line ~340）：含 `soft-landing/landing banner` 引用 + 「drain 在 landing」——把 drain 时机从「landing」改为「**stage**（每回合）」（spec 把 accumulator-drain 从 land 下放到 stage）；banner 引用 `soft-landing/landing` → `stage/land` 语汇。
2. **`## Key Context` 字段说明**（line ~338）+ **Accumulator-drain principle**（line ~341）：把「draining runs at **landing**, not at the mechanical checkpoint」改为「runs at **stage**（每回合的 judgment 半），不是 turn-end hook 的机械半」。
3. **`current:` / checkpoint 段**（line ~92-96）：`checkpoint` 作为模式词 → stage 语汇（「stage 在每个 plan-task 边界推进 `current:`」）；链接锚指向 `exit-ritual` 的 stage 段（plan 3 收口）→ 留 seam。
4. **Length cap 段**（line ~342）：`checkpoint` 引用同步。
5. 新增/确认 **`## Staged (awaiting land)` 字段说明**：plan 1 已加 section + AUTO 投影，templates.md 若缺该字段的「是什么」说明则补一条（派生自 done-not-archived workflow + stale-with-verify 知识；不可手编；land 改真相源后随 regen 自然收缩）。

- [ ] **Step 1: 改 Pending Review + Key Context + Accumulator-drain** 三处的 drain 时机（landing→stage）+ banner 语汇。
- [ ] **Step 2: 改 `current:`/checkpoint 段 + Length cap 段**的 checkpoint 词。
- [ ] **Step 3: 补 `## Staged` 字段说明**（若无）。
- [ ] **Step 4: 验证**

```bash
grep -nE "soft-landing|checkpoint|at landing|mechanical checkpoint" skills/preflight/templates.md
# 人读：drain 时机是否一致写成 stage；## Staged 字段是否有「是什么 + 派生 + 自然收缩」说明
```
Expected: drain 归 stage；checkpoint-as-mode 清零或转 stage；## Staged 字段就位；seam 注脚就位。

- [ ] **Step 5: commit**

```bash
git add skills/preflight/templates.md
git commit -m "docs(templates): cockpit field docs adopt stage/land; drain runs at stage"
```

---

### Task 5: 跨文件一致性扫 + seam 清单

**Files:** （只读审，必要时微调本 plan 的 4 个文件）

- [ ] **Step 1: 全 plan-2 文件旧术语扫**

```bash
grep -rnE "soft-landing|full-landing|full landing|checkpoint ⊂|signal 1|signal 2|signal 3" \
  skills/landing/SKILL.md skills/status/SKILL.md skills/walkaround/SKILL.md skills/preflight/templates.md
```
Expected: 命中只剩「指向 plan-3 文件的链接锚」或 seam 注脚；无散文里把旧三层/ signal 当现行模型描述。

- [ ] **Step 2: seam 清单核对**——确认每处依赖 signal/readiness 重设计的地方都留了 `<!-- plan-3 seam: … -->`，给 plan 3 一份「待收口」清单（landing banner 归属、status/walkaround 的 readiness nudge 措辞、templates `current:` 锚、preflight 入口 readiness）。把清单抄进 spec 的 plan-3 范围或本 plan 末尾备查。
- [ ] **Step 3: 人读 stage/land 连贯性**——4 个文件合起来读：stage（每回合自动 + 落知识 + done-not-archived + drain + commit）vs land（阀门 archive + 翻牌 + push-ask）是否前后一致、无残留旧二分。
- [ ] **Step 4: commit（若有微调）**

```bash
git add -A
git commit -m "docs(stage-land): plan-2 cross-file consistency sweep + plan-3 seam list"
```

---

## 完成标志

- 4 个独立散文面（landing / status / walkaround / templates）停止表达旧三层、停止把 `done`-not-archived 当债；改用 stage/land 语汇。
- landing = 单一阀门（archive + 翻牌 + 提交该批 + push-ask）；每回合 commit 归 stage。
- walkaround Audit 13 翻转为 staging-异常审计（Open Q5 判定就位）。
- templates 的 drain 时机 = stage；`## Staged` 字段有说明。
- 所有依赖 signal/readiness 重设计的措辞留 `<!-- plan-3 seam -->`，汇成 plan 3 待收口清单。

**不在本 plan 内**（plan 3）：`exit-ritual.md`（signal 1/2/3 整体重设计 + 三层→stage/land + stage banner + drain 下放的主文）、`protocol.md`（Act-report-close + readiness 重设计 + Land Routine 触发）、`preflight/SKILL.md`（入口 readiness = staged 量被动展示）。
