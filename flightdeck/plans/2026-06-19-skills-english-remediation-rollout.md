---
status: active
summary: 翻译 10 个 skill 文件到纯英文：先拆结构坑（中文 heading→英文+全锚点同步改；## 评审纪要→## Review notes 改定义+全引用），再逐文件翻译（语义不动）；每文件翻完 rg 自验零 Han，全部完成后 rg -lP Han skills scaffolds 为空（version-bump 英文门转绿）+ walkaround Audit 7 零断链。
last_updated: 2026-06-19
implements: specs/2026-06-19-skills-english-remediation.md
---

# skills/ 纯英文整顿 rollout — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。**纯翻译苦力**——可在原会话内联，亦适合派子代理（机械、低设计耦合）。Steps use `- [ ]`. **顺序铁律：结构坑（Task 1-2）必须先于逐文件翻译（Task 3+）**，否则改 heading 会与翻译撞车 + 断锚点。

**Goal:** `rg -lP '\p{Han}' skills scaffolds` 返回空（version-bump 英文发版门转绿），且 walkaround Audit 7 零断链、语义零漂。

**Architecture:** 两阶段——先原子处理结构坑（中文 heading + 锚点、中文约定名），再逐文件翻译散文。只动语言不动语义/契约/结构。

**Tech Stack:** markdown skill prose（→英文）；`rg` 自验；`uv run pytest` 回归。

**当前 CJK footprint（rg -cP，翻完应全为 0）：** sync 44 · protocol 35 · templates 32 · walkaround 27 · exit-ritual 27 · landing 6 · new 5 · status 3 · folder-semantics 3 · preflight/SKILL 2。

---

### Task 0: 术语表（一次性，贴在本 plan 执行时参照）

- [ ] **Step 1:** 固定译法，全 skills 统一（避免同词多译）：
  退场/着陆=landing · 出场=on-exit · 预检=preflight · 字面量=literal · 门控=gated · 排空=drain · 毕业=graduate · 逼问=prompt-to-resolve · 漂移=drift · 收敛=converge · 中转暂存=transient staging · 恢复载荷=recovery payload · 非阻塞=non-blocking · 待复核=pending-review (stale) · 待验证=pending-verify · 净字符=net chars · 评审纪要=Review notes · 母库=master store · 扇出=fanout · 注册表=registry。

---

### Task 1: 结构坑 A — 中文 heading + 全锚点同步改（原子）

**Files:** `skills/preflight/protocol.md`（中文标题源）+ 所有锚链它的文件（`status/SKILL.md`、`preflight/SKILL.md`、`exit-ritual.md` 等）

- [ ] **Step 1: 盘点** — `rg -nP '^#{1,4}\s+.*\p{Han}' skills/`（中文 heading）+ `rg -nP '\]\(#[^)]*\p{Han}[^)]*\)' skills/` 与 `rg -nP '\]\([^)]*#[^)]*\p{Han}' skills/`（中文 anchor 链接）。已知：`protocol.md` 的 `验证非阻塞-non-blocking-verification`、`§ verify` 类、`写工件 body 的质量` 等。
- [ ] **Step 2:** 逐个中文 heading：改英文标题 → 计算新 anchor（GitHub 规则：小写、空格→`-`、去标点）→ `rg` 找出所有指向旧中文 anchor 的链接，逐一改成新 anchor。**一个 heading 一组（标题+所有锚）一起改、立即 `rg` 复验该 anchor 零残留再下一个**。
- [ ] **Step 3: Verify** — `rg -nP '\]\(#[^)]*\p{Han}' skills/` 与中文 heading 盘点均为空；`/flightdeck:walkaround` Audit 7 零断链。
- [ ] **Step 4: Commit** — `git commit -m "i18n(skills): anglicize Chinese headings + sync all anchor links"`

---

### Task 2: 结构坑 B — `## 评审纪要` 约定名 → `## Review notes`（原子）

**Files:** `skills/preflight/folder-semantics.md`（定义处）+ 全部引用处（`exit-ritual.md`、`landing/SKILL.md` 等，`rg -n '评审纪要' skills/`）

- [ ] **Step 1:** `rg -n '评审纪要' skills/` 盘点全部出现。定义处 + 每个引用处统一改 `## Review notes`。**注**：这是 ship 面*约定名*，指导的是用户 deck 里的 section；deck 内容随用户语言，故 skill 散文/示例用英文名即可，不强制用户写英文 section。
- [ ] **Step 2: Verify** — `rg -n '评审纪要' skills/` 为空。
- [ ] **Step 3: Commit** — `git commit -m "i18n(skills): rename ## 评审纪要 convention → ## Review notes across skills"`

---

### Task 3–N: 逐文件翻译（语义不动），小→大

每个文件一个 task，同一模板：**读全文 → 把所有中文散文译成英文（保留代码/路径/锚点/契约语义，只换语言）→ `rg -P '\p{Han}' <file>` 自验零残留 → commit**。顺序按 footprint 小→大，先易后难建立术语手感：

- [ ] **Task 3:** `skills/preflight/SKILL.md`（2）— 如 `(零写入)`→`(zero-write)`、line 11 banner 中文。Commit `i18n(preflight): SKILL.md to English`。
- [ ] **Task 4:** `skills/preflight/folder-semantics.md`（剩余，Task 2 后）。Commit。
- [ ] **Task 5:** `skills/status/SKILL.md`（3）。Commit。
- [ ] **Task 6:** `skills/new/SKILL.md`（5）。Commit。
- [ ] **Task 7:** `skills/landing/SKILL.md`（6 + 残留 `待复核`/`⚠未验证` 字面量按术语表）。Commit。
- [ ] **Task 8:** `skills/walkaround/SKILL.md`（27，整篇 audit）。Commit。
- [ ] **Task 9:** `skills/preflight/exit-ritual.md`（27 剩余段）。Commit。
- [ ] **Task 10:** `skills/preflight/templates.md`（32 剩余段）。Commit。
- [ ] **Task 11:** `skills/preflight/protocol.md`（35 剩余段，Task 1 后）。Commit。
- [ ] **Task 12:** `skills/sync/SKILL.md`（44，整篇）。Commit。

每个 task 内：翻完即 `rg -P '\p{Han}' <file>` 必须空再 commit。

---

### Task 13: 全局收口验证

- [ ] **Step 1:** `rg -lP '\p{Han}' skills scaffolds` 返回空（= version-bump 英文发版门转绿）。
- [ ] **Step 2:** `/flightdeck:walkaround` Audit 7 零断链（heading 改名后所有 anchor 解析）。
- [ ] **Step 3:** `uv run pytest scripts/tests/ -q` 全绿（若某测试 assert 了中文串则同步改期望）。
- [ ] **Step 4:** 抽读 sync / walkaround（译得最多）确认英文通顺、语义未漂。
- [ ] **Step 5: Commit**（若 Step 3 有测试改动）。

---

## Self-review（对 spec 核一遍）

- 结构坑（heading+anchor / 评审纪要）→ Task 1-2（必须先做）· 10 文件翻译 → Task 3-12 · 收口（rg 空 + Audit 7 + pytest）→ Task 13。spec 待翻译清单逐文件有 task。
- 非目标守住：不翻 dogfood deck / 本仓 CLAUDE.md / README.zh.md / 用户 deck；不借翻译重构语义；守卫不进 shipped walkaround/lint（已在 version-bump 门）。
- scope 外不碰：`flightdeck/` 下中文（specs/incidents/plans 等 dogfood 内容）保持中文。
