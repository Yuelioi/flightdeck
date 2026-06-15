---
status: active
summary: 删 7 magic-string 开关 + resolution-order 教学机器；rules.md ### Autonomy overrides→### Rules（AI 按用户自然话落盘）；protocol/templates/scaffold/skills/tests/外圈同步；保留 version:3.0 + 环境推断 + 默认；verify wc-m 这次净降 + pytest 绿 + landing
last_updated: 2026-06-16
implements: specs/2026-06-16-ai-authored-config.md
---

# AI-authored config Implementation Plan

> **For agentic workers:** 用 superpowers:executing-plans / subagent-driven-development 逐任务实现。步骤用 `- [ ]` 跟踪。

**Goal:** 删人工配置面（7 magic-string 开关 + resolution-order 教学机器），rules.md 改由 AI 按用户自然话落盘规则；**不删配置能力**（AI 读 deck 规则 > 默认）。

**Architecture:** 先在 `protocol.md` 把「Rule resolution order」从「magic-string 表 + lenient 匹配机器」收成「读 deck `### Rules` 自由文 > 环境推断 > 内置默认」的精简授权序（单一真相源）；再把 templates/scaffold/skills/外圈的开关词汇表删干净，对齐到 `### Rules`。**删 > 留**：净瘦身（与 Spec 1 的净增相对）。

**Tech Stack:** Markdown + Python（`uv run pytest`）+ `flightdeck_index.py`/`flightdeck_lint.py`。

**设计见** [spec](../specs/2026-06-16-ai-authored-config.md)。**字符串契约：** 段名 `### Autonomy overrides` → **`### Rules`**；保留 `### Project conventions`。**保留不删**：`version: 3.0` 戳 · 环境推断（git 探测 / emit-AGENTS「有才 regen」）· 内置默认（commit 本地自动 / push 先问 · status auto-start · landing auto-run · 五仪式自调）· 授权序 `CLAUDE.md > deck 规则 > 默认`。

---

### Task 0: Baseline

- [ ] **Step 1: 记 baseline**（这次预期净降）
Run: `wc -m skills/preflight/protocol.md skills/preflight/templates.md skills/landing/SKILL.md skills/status/SKILL.md skills/_shared/bootstrap.md` → 记入 Progress。
- [ ] **Step 2: 绿底** — `uv run pytest scripts/tests/ -q`（PASS）；`flightdeck_index.py flightdeck --check`（clean）。

---

### Task 1: protocol.md — 收 Rule resolution order（单一真相源）

**Files:** Modify `skills/preflight/protocol.md`

- [ ] **Step 1: 重写「## Rule resolution order」**（现 L26-52 区）
删：standard-phrase 表（7 行 magic-string）、behavioral-override lenient-substring 匹配机器、legacy-Chinese compat 段、「no self-invoke override / no auto land toggle」清单。
留并收成精简三步：① deck `### Rules`（自由文，AI 读+遵守，高于默认）② 环境推断（git 探测 / emit-AGENTS 有才 regen）③ 内置默认（commit 本地自动·push 先问 / status auto-start / landing auto-run / 五仪式自调）。授权序一行：`CLAUDE.md（项目）> deck 规则（rules.md ### Rules）> flightdeck 默认`。

- [ ] **Step 2: 改「## Project rules (rules.md)」段**（L15-24）
`### Autonomy overrides` → `### Rules`；把「7 toggle / magic-string」表述改为「AI 按用户自然话维护的自由文行为规则」。保留 `version` 是唯一结构字段、`### Project conventions`。

- [ ] **Step 3: 清扫散落引用** — grep `protocol.md` 内剩余 `Autonomy overrides` / `commit: ask` / `don't auto-…` / 具体 toggle 串，逐处改指 `### Rules` 或删。frontmatter 字段表（`version` 行等）保留。

- [ ] **Step 4: verify** — `flightdeck_index.py flightdeck --check` clean；通读授权序自洽，Spec 1 的 Act-report-close loop 引用不受影响。
- [ ] **Step 5: commit** — `docs(protocol): 收 Rule resolution order 为 deck-rules>推断>默认，删 magic-string 机器` + `Flightdeck-Sync: main`。

---

### Task 2: templates.md — 重写 rules.md 模板

**Files:** Modify `skills/preflight/templates.md`

- [ ] **Step 1: rules.md 模板段**（含 toggle 示例 L26-30 + 解释 L35-45）
删 toggle magic-string 示例块（`commit: ask` / `don't auto-commit` / `this deck doesn't use git` / `has AGENTS.md but don't auto-regen` 等）+ resolution 教学表；改为：rules.md = `version: 3.0`（唯一结构字段）+ `### Project conventions` + `### Rules`（AI 按你自然话追加的行为规则，自由文，注来源/日期；无则留空/省略）。保留 `version` 必备 + 授权序指针到 protocol。
- [ ] **Step 2: verify** — `--check` clean。
- [ ] **Step 3: commit** — `docs(templates): rules.md 模板删 toggle 目录，改 ### Rules AI-authored`。

---

### Task 3: scaffold + dogfood rules.md

**Files:** Modify `scaffolds/full/flightdeck/rules.md` · `flightdeck/rules.md`

- [ ] **Step 1: scaffold rules.md** — 出厂样板：`version: 3.0` + `### Project conventions`（占位）+ `### Rules`（空 + 一句注释「AI 按你的自然话在此落盘行为规则」）。删 toggle 示例。
- [ ] **Step 2: dogfood rules.md** — 本仓 `flightdeck/rules.md` 的空 `### Autonomy overrides` → `### Rules`（保留 version + Project conventions 的中文 dogfood 内容）。
- [ ] **Step 3: verify** — `flightdeck_lint.py flightdeck` rc=0（rules.md 仍合规：有 version）。
- [ ] **Step 4: commit** — `docs(scaffold,rules): rules.md 模板/本仓改 ### Rules，删 toggle 示例`。

---

### Task 4: skills — 删 Overrides 分支 + 加「落盘用户规则」

**Files:** Modify `skills/landing/SKILL.md` · `skills/status/SKILL.md` · `skills/preflight/SKILL.md` · `skills/emit-agents-md/SKILL.md` · `skills/walkaround/SKILL.md` · `skills/launch/SKILL.md` · `skills/preflight/folder-semantics.md`

- [ ] **Step 1: 删 toggle 分支**
- landing Step 11 / Output：`Overrides: commit: ask / don't auto-commit` → 删 magic-string，改「commit 默认本地自动；若 deck `### Rules` 有相关规则则遵守」。
- status：`House Rule status: don't auto start` → 删；改「auto-start 默认开，deck `### Rules` 可改」。
- preflight Step 1 / emit-agents Step 0 / walkaround / launch / folder-semantics：把 `House Rule <magic-string>` 引用改为「deck `### Rules`（若有）」或删具体串；环境推断（git/emit）表述保留。
- [ ] **Step 2: 加「持久指令落盘」**（landing 或 status + protocol）
识别用户 `以后/每次/always/never` 类持久行为指令 → AI 在 `rules.md ### Rules` 追加一条自由文规则（注来源/日期）+ banner 报告（这是 Spec 1 覆盖的可逆动作）。
- [ ] **Step 3: verify** — Grep `skills/` 确认 7 magic-string 与 `Autonomy overrides` 归零（除 protocol 历史/Spec 引用）：`Autonomy overrides|commit: ask|don't auto-commit|don't auto start|this deck doesn't use git|has AGENTS.md but don't|nudge on done|don't soft-land`。`--check` clean。
- [ ] **Step 4: commit** — `feat(skills): 删 toggle Overrides 分支，加用户规则落盘 ### Rules`。

---

### Task 5: 测试同步

**Files:** Modify `scripts/tests/test_flightdeck_init.py`（+ 任何断言 toggle 的用例）

- [ ] **Step 1: 跑全量找红** — `uv run pytest scripts/tests/ -q`；列出依赖 toggle/Autonomy-overrides/标准短语匹配的红用例。
- [ ] **Step 2: 改用例** — 删/改断言「magic-string 匹配 / 标准短语表」的测试；若有测 scaffold rules.md 内容的断言，对齐新模板（version + ### Project conventions + ### Rules）。
- [ ] **Step 3: verify** — `uv run pytest scripts/tests/ -q` PASS。
- [ ] **Step 4: commit** — `test: 同步删 toggle 词汇表 + rules.md ### Rules 模板`。

---

### Task 6: 外圈文档 + descope

**Files:** Modify `README.md` · `README.zh.md` · `CHANGELOG.md` · `docs/architecture.md` · `docs/README.md` · `flightdeck/docs/descope-baseline.md`

- [ ] **Step 1: 外圈** — README/zh 删 toggle 清单（L171 区的 `commit: ask` 等），改述「行为偏好＝用自然话告诉 AI，AI 落 rules.md ### Rules」；CHANGELOG 记破坏性（删 toggle 词汇表）；architecture/docs README 同步。
- [ ] **Step 2: descope-baseline** — 在「自治交互边界」节补一句：配置面已无人工 toggle 目录，rules.md AI-authored（指向 protocol § Rule resolution order）。
- [ ] **Step 3: verify** — `--check` clean。
- [ ] **Step 4: commit** — `docs: 外圈 + descope 同步 ai-authored-config`。

---

### Task 7: dogfood verify + landing

- [ ] **Step 1: wc -m 复测** — 对 Task 0 文件复跑 `wc -m`，确认热路径**净降**（删 toggle 机器的瘦身收益，与 Spec 1 净增相对）；记 Progress。
- [ ] **Step 2: 全量 verify** — `uv run pytest scripts/tests/ -q` PASS；`flightdeck_index.py flightdeck --check` clean；`flightdeck_lint.py flightdeck` rc=0。
- [ ] **Step 3: AGENTS.md** — 若 cockpit 渲染字段变则 re-emit。
- [ ] **Step 4: landing** — flip spec/plan done、归档、cockpit 同步、commit（不 push）。graduate 否。

---

## Progress

- Task 0 baseline: （执行时填）
- （逐 Task）

## Self-Review（plan vs spec 覆盖）

- 删开关目录（Part 1）→ Task 1 + Task 2 + Task 3 + Task 4。
- rules.md AI-authored（Part 2）→ Task 2 + Task 3 + Task 4 Step 2。
- 保留语义 / 授权序 → Task 1 Step 1。
- 环境推断 / version 戳 / 默认 保留 → Task 1（不删推断/默认）+ Task 3（version）。
- 验证（wc-m 净降 + pytest）→ Task 0 + Task 5 + Task 7。
- 红线不动 → version:3.0 / 推断 / preflight 纯读 / CLAUDE.md 最高层全程不碰。
