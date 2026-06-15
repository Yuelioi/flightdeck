---
status: done
summary: 按 spec 落地：baseline → protocol.md 单一真相源(判据表+banner 规范+翻回+Hanging 窄定义+阶段派生) → bootstrap 最小指针 → skills 删门+banner → 模板/scaffold → 测试 → 外圈文档+descope 归宿 → dogfood verify(pytest 绿；wc-m 反转：净增非减，瘦身留 Spec 2)+landing
last_updated: 2026-06-16
implements: specs/2026-06-16-act-report-close-loop.md
---

# Act-report-close loop Implementation Plan

> **For agentic workers:** 用 superpowers:subagent-driven-development 或 executing-plans 逐任务实现。步骤用 `- [ ]` 跟踪。

**Goal:** 让可逆 deck 动作无门自动执行 + 统一「翻回」撤销 + 所有流程统一末尾 banner + 全生命周期可恢复，落地铁律「纯 AI 操作 + 随时可关可恢复」。

**Architecture:** `protocol.md` 立为 banner 格式 + 可逆判据 + 翻回 + Hanging 窄定义 + 阶段派生的**单一真相源**；`bootstrap.md` 只留最小运行时指针；各 skill / 模板 / 文档**引用不重定义**。先立真相源 → 再改引用方 → 最后外圈同步 → verify + landing。

**Tech Stack:** Markdown（skills/protocol/templates/docs）+ Python（scripts/tests，`uv run pytest`）+ `flightdeck_index.py`/`flightdeck_lint.py` 自检。

**设计见** [spec](../specs/2026-06-16-act-report-close-loop.md)。**Spec 1 / Spec 2 边界**：本 plan **只删可逆动作的硬确认门**（promotion 恒 user-gated / status 仅 confirm 应用 / `--advance-candidates` confirm-gated），**不动 7 个 magic-string 开关 + resolution-order**（那是 Spec 2）。

**字符串契约（全程一致）：** banner `─── <icon> <flow> ───`；字段标签英文 `[Stage] [Saved] [No change] [Pending] [Failed]`；icon `preflight`🛫 `soft landing`🛬 `landing`🛬 `new`✍️ `walkaround`🔎。Pending Review 行 `- [<topic>] <做了什么 · 怎么验> → 验证通过后：<怎么 commit / 下一步>`。

---

### Task 0: Baseline（度量 + 绿底确认）

**Files:** 无改动（只读度量）

- [ ] **Step 1: 记 baseline 字符数**（热路径，作删门「瘦 prompt」对照）

Run（Bash）:
```
wc -m skills/_shared/bootstrap.md skills/preflight/protocol.md skills/landing/SKILL.md skills/status/SKILL.md skills/preflight/exit-ritual.md skills/preflight/SKILL.md
```
把结果记进本 plan 的 `## Progress`（Task 0）。

- [ ] **Step 2: 确认起点全绿**

Run: `uv run pytest scripts/tests/ -q` → Expected: PASS（本机若现 WSL bash 噪音另记）。
Run: `python scripts/flightdeck_index.py flightdeck --check` → Expected: `clean`。

---

### Task 1: protocol.md = 单一真相源（原子核）

**Files:** Modify `skills/preflight/protocol.md`（新增章节，**不动** Rule resolution order——留给 Spec 2）

- [ ] **Step 1: 加「可逆/不可逆判据表」**

新增一节，给出权威表：可逆（自动）= 改动只落 deck 内文件/git 本地、可反向编辑或 git 本地回退（枚举：status flip · `--advance-candidates` · incident→checklist promotion · done 归档 · 应用 status 建议 · stale 翻转 · cockpit 段维护）；不可逆/外发（先问）= push / 对外发布 / 调外部服务；`commit` 本地=可逆。注明：破坏用户手写内容的可逆编辑须在 banner 显式报告。

- [ ] **Step 2: 加「统一输出格式 / banner 规范」**

定义：回合=一次用户输入→一次完整响应；一回合一个聚合 banner、恒在末尾；触发=跑 flow/做实际工作的回合（纯对话/澄清不出）；嵌套只出最外层 + 内层 `[Saved]`/`[Pending]` 并入；失败态出 `[Failed]`。字段集：`[Stage]` + 末行可关信号恒在；`[Saved]`/`[No change]` 二选一；`[Pending]` 仅 Pending Review 非空时出；各 flow 最小字段集（preflight 至少 `[Next]`+路由计数）。格式串见上「字符串契约」。

- [ ] **Step 3: 加「翻回 / 撤销单元」规范**

撤销单元=最近一个着陆单元（一次 landing/checkpoint commit，或本回合未提交 deck 变更）整体；跨会话 fallback：读 `git log -1 --oneline`，带 `landing:`/`checkpoint:` 标记→回退该单元，未标记/跨多回合/歧义→求用户澄清；push 不可撤。

- [ ] **Step 4: 加「Hanging Tasks 窄定义」+「阶段派生」+「两种恢复语境」**

Hanging=真有外部依赖/未完成阻塞，只挡 landing、不挡回合内可逆动作。阶段派生优先级 plan status > spec status > cockpit Active focus。恢复语境：preflight 只读 cockpit+INDEX；翻回读 git+看板（独立动作）。

- [ ] **Step 5: verify**

Run: `python scripts/flightdeck_index.py flightdeck --check` → `clean`；`python scripts/flightdeck_lint.py flightdeck`（rc=0，无新增 CRITICAL）。通读自洽。

- [ ] **Step 6: commit** — `git commit`（不 push）：`docs(protocol): 立 banner/判据/翻回/阶段派生单一真相源` + `Flightdeck-Sync: main`。

---

### Task 2: bootstrap.md 最小运行时指针

**Files:** Modify `skills/_shared/bootstrap.md`（On exit 段）

- [ ] **Step 1: 重写 On exit 段**

按 spec Part 2 delta：执行回合→出 soft-landing banner；有知识→`[Saved]`、纯状态→checkpoint 一句话、无增量→`[No change]`（Pending Review 非空带 `[Pending]`）；纯对话不出。**最小**——banner 完整规范指向 `protocol.md`，此处不重定义。

- [ ] **Step 2: verify** — `--check` clean；读 directive 简洁无重复定义。

- [ ] **Step 3: commit** — `docs(bootstrap): On exit 改统一 banner 退场契约（指针化）`。

---

### Task 3: skills 散文——删可逆动作硬门 + 接 banner

**Files:** Modify `skills/landing/SKILL.md` · `skills/preflight/exit-ritual.md` · `skills/status/SKILL.md` · `skills/preflight/SKILL.md` · `skills/new/SKILL.md` · `skills/walkaround/SKILL.md` · `skills/emit-agents-md/SKILL.md`

- [ ] **Step 1: landing/SKILL + exit-ritual——删硬门**

删/改写：`promotion is always user-gated`→按判据自动 + 浮 Pending Review；`--advance-candidates → confirm-gated offer`→自动推进（归档幂等）；`Status … applied only on user confirm`→自动应用 + 报告；`retire prompt`→自动 + 报告。加：Pending Review 行格式、生命周期恢复、banner 引用 protocol。**不动** `commit: ask`/`don't auto-commit`（Spec 2）。

- [ ] **Step 2: status/SKILL——删 confirm**

`suggest next status … applied only on user confirm`→自动应用 + banner 报告。

- [ ] **Step 3: 各 flow 接统一 banner**

`preflight/SKILL`（🛫 输出走统一 banner，至少 `[Next]`+路由）· `new`（✍️）· `walkaround`（🔎）· `emit-agents-md` 输出末尾统一 banner；格式指向 protocol。

- [ ] **Step 4: verify** — grep 确认硬门措辞已清：
```
rg -n "user-gated|applied only on user confirm|confirm-gated" skills/
```
`--check` clean；`flightdeck_lint.py` rc=0。

- [ ] **Step 5: commit** — `feat(skills): 删可逆动作硬确认门，输出统一 banner`。

---

### Task 4: 模板 + scaffold

**Files:** Modify `skills/preflight/templates.md` · `scaffolds/full/flightdeck/cockpit.md`

- [ ] **Step 1: templates.md** — cockpit 模板补 Pending Review 行格式 + banner 说明（引用 protocol，不重定义）。
- [ ] **Step 2: scaffolds cockpit.md** — Pending Review 示例行用新格式。
- [ ] **Step 3: verify** — 对 scaffold 跑 `flightdeck_lint.py`/`flightdeck_index.py --check` 应 clean（scaffold 是出厂样板，须自洽）。
- [ ] **Step 4: commit** — `docs(templates,scaffold): Pending Review 行格式 + banner 说明`。

---

### Task 5: 测试同步

**Files:** Modify `scripts/tests/test_flightdeck_*.py` / `test_hooks.py`（按命中改）

- [ ] **Step 1: 跑全量找红**

Run: `uv run pytest scripts/tests/ -q`。若有断言依赖旧门措辞 / 旧 cockpit 输出 → 列出。

- [ ] **Step 2: 改/加用例**

按 spec 验证场景补可机检者：cockpit Pending Review 行格式（若已有结构断言）、banner 字段（若可测）、删门后无回归。**不**为 drain/翻回加 regex 解析（设计上靠判断）。逐个写 + 跑绿。

- [ ] **Step 3: verify** — `uv run pytest scripts/tests/ -q` → PASS（160+，WSL 噪音另记）。

- [ ] **Step 4: commit** — `test: 同步删门 + banner/Pending Review 格式`。

---

### Task 6: 外圈文档 + 知识归宿

**Files:** Modify `README.md` · `README.zh.md` · `docs/architecture.md` · `docs/session-flow.md` · `TEST_PLAN.md` · `flightdeck/docs/descope-baseline.md`

- [ ] **Step 1: 外圈措辞校准** — 「自动着陆 / 随时可关 / 统一输出 / 删门自治」表述对齐新语义；README 卖点不超协议（守 `dont-overclaim`）。
- [ ] **Step 2: descope-baseline 加段** — 记「可逆-自动 + 统一撤销 + 统一输出格式 + 全生命周期恢复 + 零损失收窄定义」这条交互边界（红线单一真相源）。
- [ ] **Step 3: verify** — `--check` clean；通读不与 protocol 真相源冲突。
- [ ] **Step 4: commit** — `docs: 外圈 + descope 同步 act-report-close-loop 语义`。

---

### Task 7: dogfood verify + landing

- [ ] **Step 1: wc -m 复测** — 对 Task 0 的文件复跑 `wc -m`，确认热路径（bootstrap + 各 SKILL）净字符**下降**（删门收益）；记入 Progress。涨了则复查是否把散文从热路径漏灌冷路径。
- [ ] **Step 2: 全量 verify** — `uv run pytest scripts/tests/ -q` PASS；`flightdeck_index.py flightdeck --check` clean；`flightdeck_lint.py flightdeck` rc=0。
- [ ] **Step 3: 自我 dogfood 检查** — 本会话从此按新 banner 输出（一回合一个、末尾、英文字段标签）已生效，作活体验证。
- [ ] **Step 4: landing** — 跑 `/flightdeck:landing`：flip spec/plan→done、归档、cockpit 同步、commit（不 push）。graduate 倾向否。

---

## Progress

- Task 0 baseline: （执行时填 wc -m 数值 + pytest 状态）
- （逐 Task 勾选）

## Self-Review（plan vs spec 覆盖）

- 删门（Part 1）→ Task 3；翻回（Part 1）→ Task 1 Step3；判据单一源 → Task 1 Step1；Hanging 窄定义 → Task 1 Step4。
- 统一输出格式/banner（Part 2）→ Task 1 Step2 + Task 2 + Task 3 Step3；字段集/失败态/嵌套 → Task 1 Step2。
- 全生命周期恢复 + 阶段派生（Part 3）→ Task 1 Step4 + Task 3 Step1（生命周期写 exit-ritual）。
- Pending Review 恢复完整性 → Task 3 Step1 + Task 4。
- 国际化（决策7）→ 全程英文字段标签（字符串契约）。
- 验证（测试场景 + wc-m baseline）→ Task 0 + Task 5 + Task 7。
- 红线不动 → 全程不碰 cockpit+INDEX 载荷 / push 先问 / preflight 纯读 / version 戳；Spec 2 范围（开关）不碰。
