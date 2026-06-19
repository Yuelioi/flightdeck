---
status: active
summary: 实现 accumulator-convergence：Key Context 重述为中转暂存（B1 referent 死即排空 / B2 耐用毕业上迁到 home-by-kind）+ Pending Review 老条目 landing 逼问（A）+ 去 CLAUDE.md 写死（protocol/templates 三处改 agent 中立）+ home-by-kind 表（rules/docs/agent根文件）。落 exit-ritual+protocol+templates+landing，dogfood cockpit 真瘦身。新写英文。
last_updated: 2026-06-19
implements: specs/2026-06-19-cockpit-accumulator-convergence.md
---

# Cockpit accumulator 收敛 rollout — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans（原会话内联，设计上下文在对话里）。Steps use `- [ ]`. **前置依赖**：field-redesign rollout 已落（exit-ritual 字段结构=新；本 plan 在其上改 Key Context/Pending Review 生命周期）。

**Goal:** 让 cockpit 两个 accumulator 真正收敛——Key Context 变中转暂存（耐用毕业、临时排空），Pending Review 老条目被 landing 逼问，且毕业目标家 agent 中立（去 CLAUDE.md 写死）。

**Architecture:** 真相源 = `exit-ritual.md` §Cockpit update（Key Context/Pending Review 段 + Accumulator-drain）。纯散文契约改 + dogfood 应用；无脚本改（B1 排空借 landing 已知的「本会话归档集」，判断活）。新写英文。

**Tech Stack:** markdown skill prose（英文）。无新测试（纯契约；`uv run pytest scripts/tests/` 回归确认不破）。

---

### Task 1: Key Context → 中转暂存模型（exit-ritual，英文）

**Files:** Modify `skills/preflight/exit-ritual.md`（`## Key Context is the recovery slot` 段 + 其 per-entry drain 子条）

- [ ] **Step 1:** 重写 Key Context 段：从「recovery slot + 原地 drain/shrink」改为**中转暂存区**——cockpit 不是任何条目的永久住址，两个出口，landing 时走：
  - **B1 drain（近确定性）**：条目 referent（指向的 spec/plan/incident）本会话 archived/graduated/done → 死指针 → drop（活细节挪 specs）。借 landing 已知的本会话归档集反查，自动 drop + landing 报告列出（可 undo），不预问。
  - **B2 graduate（判断，与 spec 毕业同质）**：耐用、不指向会死件的条目 → 毕业上迁到 home-by-kind（Task 4 的表），从 cockpit 删。
  - 耐用原则不指向会死件 → 天然不被 B1 碰；B2 请它出 cockpit。取消「pin / 原地保护 / 按年龄逼问 Key Context」。
- [ ] **Step 2:** 加 home-by-kind 表（英文）：behavior red line/convention → `rules.md`（每仪式全文读）· design rationale/decision → `docs/`（when_to_read 路由）· standing meta → **the project's agent instruction file (CLAUDE.md / AGENTS.md / GEMINI.md, per the running agent)** — 强调常驻预算克制、多数耐用条目归 docs。
- [ ] **Step 3: Verify** — `rg -n 'transient staging|graduate|home-by-kind|referent' skills/preflight/exit-ritual.md` 命中；与 field-redesign 的 Focus/Updated 角色不冲突（人读对账）。
- [ ] **Step 4: Commit** — `git commit -m "feat(exit-ritual): Key Context as transient staging — drain on referent-death, graduate durable (accumulator)"`

---

### Task 2: Pending Review 老条目 landing 逼问（A，exit-ritual，英文）

**Files:** Modify `skills/preflight/exit-ritual.md`（`## Pending Review is the sign-off queue` 段）

- [ ] **Step 1:** 加 forcing function（保留显式签收）：landing 时对**跨了 ≥1 个 landing 仍未签收**的 Pending Review 条目，单独拎出逐条逼问「sign off / keep / drop」。不自动删（安全不变），只停止静默堆积。复用现有「drains when reviewed」，新增「aged → 必须本次摊出来问」。
- [ ] **Step 2: Verify** — `rg -n 'aged|prompt.*sign|crossed.*landing' skills/preflight/exit-ritual.md` 命中。
- [ ] **Step 3: Commit** — `git commit -m "feat(exit-ritual): landing prompts aged Pending Review items (accumulator A)"`

---

### Task 3: Accumulator-drain discipline 段更新（exit-ritual，英文）

**Files:** Modify `skills/preflight/exit-ritual.md`（`Accumulator-drain discipline` 段）

- [ ] **Step 1:** 更新该段以反映新机制：Key Context = drain(B1)/graduate(B2) 双出口；Pending Review = sign-off + aged-prompt。引用 Audit 14（walkaround 已浮出 referent-died/oversized Key Context，**无需新 audit**）。
- [ ] **Step 2: Verify** — 人读对账 Task 1/2 一致，无重复矛盾。
- [ ] **Step 3: Commit** — `git commit -m "feat(exit-ritual): align Accumulator-drain discipline with graduate/drain/aged-prompt (accumulator)"`

---

### Task 4: 去 CLAUDE.md 写死（protocol + templates，英文）

**Files:** Modify `skills/preflight/protocol.md`（Override authority 行）+ `skills/preflight/templates.md`（2 处 Authority / belong-in-CLAUDE.md）

- [ ] **Step 1:** 三处把写死的 `CLAUDE.md` 改 agent 中立措辞，例：`the project's agent instruction file (CLAUDE.md / AGENTS.md / GEMINI.md, per the running agent)`。语义（override 权威序：项目 agent 文件 > deck rules > defaults）不变，只去 Claude 专属假设。
  - `protocol.md` — `**Override authority** … CLAUDE.md (project) > deck rules > defaults`
  - `templates.md` — `Authority: CLAUDE.md > deck ### Rules > defaults … belong in CLAUDE.md`（两处）
- [ ] **Step 2: Verify** — `rg -n 'CLAUDE\.md' skills/` 仅剩 agent-中立列举（`CLAUDE.md / AGENTS.md / GEMINI.md` 这种），无单独把 CLAUDE.md 当唯一 agent 文件的句子。
- [ ] **Step 3: Commit** — `git commit -m "fix(protocol,templates): de-hardcode CLAUDE.md → agent-neutral instruction file (accumulator C)"`

---

### Task 5: landing Step 8 跟随（英文）

**Files:** Modify `skills/landing/SKILL.md`（Step 8）

- [ ] **Step 1:** Step 8 的 Key Context/Pending Review 措辞跟随新生命周期：Key Context graduate/drain、Pending Review sign-off + aged-prompt（checklist 面，指向 exit-ritual 真相源，不重述）。英文。
- [ ] **Step 2: Verify** — `rg -n 'graduate|aged|drain' skills/landing/SKILL.md` 命中且与 exit-ritual 一致。
- [ ] **Step 3: Commit** — `git commit -m "feat(landing): Step 8 follows Key Context graduate/drain + Pending Review aged-prompt (accumulator)"`

---

### Task 6: dogfood — 本仓 cockpit 真瘦身

**Files:** Modify `flightdeck/cockpit.md`（dogfood，中文 OK）+ 可能 graduate 目标（`rules.md` / `docs/` / `CLAUDE.md`）

- [ ] **Step 1: Key Context 5 条逐条处理**（按 Task 1 模型）：
  - de-scope 红线 / 单一真相源 → 已在 `docs/descope-baseline.md`（referent 活）→ 耐用 → 毕业：cockpit 留 ≤1 行指针或删（家在 docs）。
  - 测试/度量命令 → 常驻事实 → 毕业进 `rules.md` 或 `CLAUDE.md`（按 home-by-kind）。
  - AI 化精简两支柱 / shared-knowledge-sync → 指向已 land/graduate 的 docs → referent 死/已有家 → drain 或留薄指针。
- [ ] **Step 2: Pending Review 5 条逼问**：逐条向用户问 sign off / keep / drop（AI 化精简、shared-knowledge v2、script-layer 待复核、cockpit-bloat-control v2、descope-baseline 待复核）。**这步要用户参与**（A 的本意）——执行时把 5 条摊给用户裁决，不自动删。
- [ ] **Step 3:** `uv run scripts/flightdeck_index.py flightdeck` regen；`wc -m flightdeck/cockpit.md` 看相对 field-redesign 后（3934）的进一步净降。
- [ ] **Step 4:** `uv run pytest scripts/tests/ -q` 全绿。
- [ ] **Step 5: Commit** — `git commit -m "refactor(dogfood): drain/graduate cockpit Key Context + resolve Pending Review (accumulator)"`

---

## Self-review（对 spec 核一遍）

- A Pending Review aged-prompt → Task 2/5 · B1 drain → Task 1/6 · B2 graduate → Task 1/6 · C home-by-kind + de-hardcode → Task 1/4 · landing 跟随 → Task 5。spec 落地面每项有对应 task。
- 非目标守住：不加 pin 字段 / 脚本硬校验（纯判断）、不自动删 Pending Review（只逼问）、不按年龄过期 Key Context、不碰 In Progress/Next/Updated 机制（field-redesign 已定）、不新增 walkaround audit（Audit 14 已覆盖 referent-died）。
- 命名一致：transient staging / drain(B1) / graduate(B2) / home-by-kind / aged-prompt 全 plan 统一。
