---
status: done
summary: 分 P1–P5 实施 rules.md 3.0 简化（推断 git/emit、删 disabled_gates、autonomy 默认化+House Rules 覆盖、迁移、when-to-land），P2 前置内层门审计，dogfood 验证，末尾单次提交
last_updated: 2026-06-03
implements: landed/specs/2026-06-03-rules-simplification-design.md
---

# rules.md 简化 (3.0) 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans 或 subagent-driven-development，逐任务实施。步骤用 `- [ ]`。

**Goal:** 把 flightdeck `rules.md` 从 7-toggle 配置中心简化为 `version` + `disabled_folders` + House Rules（推断 + 默认 + 散文覆盖），并附 0 配置 when-to-land。

**Architecture:** 编辑 `skills/*` 的 markdown 指令（非可单测代码）；"测试" = 在一次性 scratch deck 上跑 preflight/landing/status 观察行为（dogfood）。破坏性 schema 变更 → 3.0，3.x 兼容读旧 key、4.0 删。

**Tech Stack:** flightdeck 技能（markdown SKILL.md / protocol.md / templates.md / exit-ritual.md）、scaffolds、MIGRATION.md。

**提交策略（用户指定）:** 全程不分提交，P1–P5 全部完成 + dogfood 通过后**一次性提交**（spec + debrief + plan + 实现，同一逻辑改动）。各 Phase 末的 dogfood 是 review 检查点，不是提交点。

**单一真相源参考:**
- 标准句表 / Rule resolution order → 新写入 `skills/preflight/protocol.md`。
- Land-readiness check → 新写入 `skills/preflight/exit-ritual.md`。

---

## Phase 1 — 推断 git / emit_agents_md；删 disabled_gates（低风险，无破坏性动作）

### Task 1.1：protocol.md 新增 "Rule resolution order" 专节

**Files:** Modify `skills/preflight/protocol.md`（toggle 章节附近）

- [ ] 新增一节，内容定为单一真相源：

  ```markdown
  ## Rule resolution order（所有 skill 共用）

  每个 skill 读配置时按此序，**先命中先用**：

  1. **House Rules 覆盖**（`rules.md` 的 `### 行为覆盖` 段）—— 命中则用，**跳过推断**。
  2. **环境推断** —— git: deck root 是否含 `.git`；emit: deck root 是否已有 `AGENTS.md`。
  3. **内置默认** —— commit=confirm；所有 ritual 可自调；status_auto=start+land 全开。

  **deck root** = 含 `rules.md` 的目录；找不到回退 cwd **并警告**（不静默）。

  **权威顺序**：CLAUDE.md（项目） > flightdeck House Rules（deck） > flightdeck 默认。

  **行为覆盖识别（穿针版，非 YAML toggle）**：
  - `### 行为覆盖` 是**字面量标题**；skill 优先在该段内按"标准句表"做**宽松子串匹配**。
  - 匹配**跳过 HTML 注释行**（`<!-- ... -->`）。
  - 段不存在 → 退回全 House Rules 语义领会（容错，不报错）。
  - **House Rules 内部冲突 = 用户责任**：不做自动择一（否决 last-match）；skill 至多被动提示矛盾，绝不静默解析。

  **标准句表**（迁移生成即用这些；手写推荐照写）：

  | 行为 | 标准句 |
  |---|---|
  | commit 自动 | "提交不必询问，直接 commit" |
  | commit 手动 | "不要自动 commit，留给我或 CI" |
  | 某 ritual 不自调 | "`<ritual>` 不要自调，我手动跑" |
  | status 不自动转换 | "status 不要自动 `<transition>`" |
  | 不走 git | "本 deck 不走 git，历史记 landed/HISTORY.md" |
  | 有 AGENTS.md 但不 regen | "有 AGENTS.md 但不要自动 regen" |
  ```

- [ ] **Verify:** `grep -n "Rule resolution order" skills/preflight/protocol.md` → 命中。

### Task 1.2：protocol.md / templates.md 改写 toggle 章节为新模型

**Files:** Modify `skills/preflight/protocol.md`、`skills/preflight/templates.md`

- [ ] templates.md `## rules.md` 模板替换为瘦身版（含两小节 + 注释式覆盖范例 + 边界说明）：

  ```markdown
  ---
  version: 3.0
  disabled_folders: []     # 唯一留存的结构化 toggle
  ---

  ## House rules

  ### 项目约定
  （只放 flightdeck 自己的约定，如 "specs 用中文"、"不建 sketches/"。通用项目约定写进 CLAUDE.md，不在这里。）

  ### 行为覆盖
  （Autonomy Policy；不写=用默认。可选，照"标准句"写：）
  <!-- 提交不必询问，直接 commit。 -->
  <!-- landing 不要自调，我手动跑。 -->
  ```

- [ ] templates.md 闭合 toggle 表：删 `git`/`emit_agents_md`/`disabled_gates`/`model_invocable`/`status_auto`/`commit_mode` 六行说明，仅留 `disabled_folders`；加"其余行为靠推断 + House Rules，见 protocol Rule resolution order"。
- [ ] templates.md 明写 **emit 不对称**：从无 AGENTS.md 出发只有 `/flightdeck:emit-agents-md` 能 bootstrap。
- [ ] protocol.md 旧 toggle 列表同步精简，链到 Rule resolution order。
- [ ] **Verify:** `grep -nE "commit_mode|model_invocable|status_auto|disabled_gates" skills/preflight/templates.md` → 仅出现在"已删/迁移"语境，不再作为 active toggle。

### Task 1.3：preflight/landing/status/walkaround/emit 的 Step-0 读法改为推断 + 兼容读旧 key

**Files:** Modify `skills/preflight/SKILL.md`、`skills/landing/SKILL.md`、`skills/status/SKILL.md`、`skills/walkaround/SKILL.md`、`skills/emit-agents-md/SKILL.md`

- [ ] 每个 SKILL.md 的 Step-0/读配置段：把"读结构化 toggle"改为"按 protocol Rule resolution order 解析（House Rules 覆盖 → 推断 → 默认）"。
- [ ] git 用法：从读 `git:` 改为 deck root 有无 `.git`（House Rules "不走 git" 覆盖优先）。
- [ ] emit-agents-md：gate 改为"自动 regen 仅当 deck root 已有 AGENTS.md；显式命令永远创建"。
- [ ] **兼容读旧 key（3.x）**：每个 skill 若见到旧 key（`git`/`commit_mode`/`model_invocable`/`status_auto`/`emit_agents_md`/`disabled_gates`）**仍 honor**，加一行"（3.x 兼容；4.0 移除）"。
- [ ] walkaround：toggle 审计逻辑从 7 key 改为 `disabled_folders` + 旧 key 兼容；不把缺失的旧 key 报成错。
- [ ] **Verify（dogfood）:** 建一次性 scratch deck（仅 `version: 3.0` + `disabled_folders: []` + House Rules），跑 `/flightdeck:preflight` → 不报缺 toggle；无 `.git` 时走 no-git；有 AGENTS.md 时 landing 会 regen、无则不创建。

---

## Phase 2 — autonomy 默认化（含硬前置审计）⚠ 破坏性

### Task 2.0（硬前置门槛）：内层 confirm 门审计

**Files:** 只读 `skills/*`、`scaffolds/*` 源码/指令

- [ ] 按 spec §3 审计表逐项核对每个会写/移/删文件的动作有无内层 confirm：landing 移文件、commit、migration 改写、status frontmatter 写、emit 覆盖写、**scaffold/模板改写**。
- [ ] 重点闭合 scaffold：读 preflight 首次安装流程——scaffold 写入是否被首次安装的确认拦住？
  - 若**有**门（首次安装会先问）→ 记"scaffold 已被 first-time-setup 确认门覆盖"，继续。
  - 若**无**门 → 走 spec §3 两出口之一：(i) 给 scaffold 写加 confirm；(ii) 局部保留 `model_invocable` 对该动作的 gate。
- [ ] **Verify:** 审计结论写进本 plan Task 2.0 下方（勾选 + 一行结论）；**任一可改文件动作缺门未闭合 → 不得进 Task 2.1**。

### Task 2.1：删 `model_invocable` / `status_auto` / `commit_mode` 的结构化语义，改默认全开 + House Rules 覆盖

**Files:** Modify `skills/status/SKILL.md`（Step-0 gate + status_auto）、`skills/landing/SKILL.md`（commit step）、`skills/preflight/SKILL.md`、`skills/walkaround/SKILL.md`、`skills/emit-agents-md/SKILL.md`（各自的 model-invocation gate）

- [ ] 各 ritual 的 Step-0 model-invocation gate：默认**允许**自调；仅当 House Rules 命中"`<ritual>` 不要自调"才退回手动。保留"显式 `/flightdeck:<x>` 永远允许"。
- [ ] status：`status_auto` 默认 start+land 全开；House Rules "status 不要自动 `<transition>`" 可关。
- [ ] landing commit step：默认 confirm；House Rules 标准句切 auto/manual。
- [ ] 全部经 protocol Rule resolution order，**不**再读结构化 key（旧 key 仍兼容读，见 1.3）。
- [ ] **Verify（dogfood）:** scratch deck 默认（无 `### 行为覆盖`）→ status 自动翻转、landing 走 confirm；加 House Rule "提交不必询问" → landing 不再问、直接 commit；加 "landing 不要自调" → 模型自调 landing 时 STOP。

---

## Phase 3 — House Rules 边界 / 权威顺序 / templates 清洗

### Task 3.1：落实两小节结构 + 边界说明 + 清洗通用范例

**Files:** Modify `skills/preflight/templates.md`、`skills/preflight/protocol.md`、`skills/preflight/exit-ritual.md`（凡提及 House Rules 处）

- [ ] templates.md / protocol.md：House Rules 固定 `### 项目约定` / `### 行为覆盖` 两小节；删现有"always branch before committing"这类**通用范例**，加一句"通用约定写进 CLAUDE.md/AGENTS.md，这里只放 flightdeck 自己的规矩"。
- [ ] 确认 protocol 已含权威顺序 CLAUDE.md > House Rules > 默认（Task 1.1 已写，此处交叉引用）。
- [ ] **Verify:** `grep -n "branch before commit\|always branch" skills/preflight/templates.md` → 无（已清洗）。

---

## Phase 4 — 迁移（依赖 Phase 3 完成）⚠ 破坏性

### Task 4.1：MIGRATION.md 新条目 + current bump + layout_need_update

**Files:** Modify `MIGRATION.md`

- [ ] frontmatter：`current: 3.0`；`layout_need_update: [2.2, 3.0]`。
- [ ] 新增 `## 2.3 → 3.0 — rules.md 简化（破坏性）` 节：说明删 key、推断、House Rules 升权威、3.x 兼容读 / 4.0 删；附非默认值 → 标准句翻译表（同 protocol）；每条迁移句带 `<!-- migrated from <key>:<value> -->`；注明"emit_agents_md:false 且无 AGENTS.md → 静默丢弃为预期"。
- [ ] **Verify:** `grep -n "current: 3.0" MIGRATION.md` 且 `grep -n "3.0" ...` layout 行命中。

### Task 4.2：preflight 迁移检测 → 提议改写 rules.md

**Files:** Modify `skills/preflight/SKILL.md`（migration 检测段）

- [ ] preflight Step 2：检测 deck `version < 3.0` 或仍含旧 key → **非静默**提议改写：剥旧 key，把非默认值按标准句表译进 `### 行为覆盖`（带 `<!-- migrated from -->` 注释），用户确认后写。
- [ ] **Verify（dogfood）:** 建一个"旧 schema" scratch deck（`version: 2.3` + `commit_mode: auto` + `model_invocable: [status]`），跑 preflight → 提议改写；确认后 rules.md 变成 `version: 3.0` + `disabled_folders` + `### 行为覆盖` 含两条带注释标准句（"提交不必询问"、"`landing`/`walkaround`/... 不要自调"）。

---

## Phase 5 — when-to-land（land-readiness check，0 配置）

### Task 5.1：exit-ritual.md 新增 Land-readiness check 节

**Files:** Modify `skills/preflight/exit-ritual.md`

- [ ] 新增（与 Land Routine 并列）：

  ```markdown
  ## Land-readiness check（共享判据；status + preflight 调用）

  **landable** = signal 1 或 signal 2：
  - **signal 1**：本次 `status` 真把某 artifact 翻到 `done`/`awaiting-review`。
  - **signal 2**：进场时 `git status` 显示 `flightdeck/` ≥ 5 个改动文件（git:false 时关闭）。

  - signal 1 由 `status` 在执行翻转的**同一调用**里搭出（边沿=翻转动作本身，无需存状态；幂等重跑遇已 done → no-op，不重复）。
  - signal 2 由 `preflight` 进场报告，作为**最后一行 / 单独 `## Land-readiness` 小节**，一次进场一次。
  - 提示后要不要自动跑 landing，复用 Rule resolution order（默认可自调 + House Rules）。
  - 故意缺口：超长单会话纯 churn 无 flip → 等下次进场（不做中途水位线）。
  ```

### Task 5.2：在 status / preflight 挂载调用

**Files:** Modify `skills/status/SKILL.md`、`skills/preflight/SKILL.md`

- [ ] status：翻转 + INDEX sync 后，调用 Land-readiness check（signal 1）。
- [ ] preflight：reconcile 末尾调用（signal 2），输出在最后。
- [ ] **Verify（dogfood）:** scratch deck 翻一个 artifact 到 done → status 搭出 land 提示；进场堆 ≥5 改动 → preflight 末行报 land 提示；堆 4 个 → 不报。

---

## Phase 6 — 同步 scaffolds / adapters / dogfood 自迁移

### Task 6.1：scaffolds 瘦身

**Files:** Modify `scaffolds/full/flightdeck/rules.md`、`scaffolds/minimal/flightdeck/rules.md`

- [ ] 两个 scaffold rules.md 换成 3.0 瘦身模板（`version: 3.0` + `disabled_folders: []` + 两小节空 House Rules）。
- [ ] **Verify:** `grep -rnE "commit_mode|model_invocable|status_auto" scaffolds/` → 无。

### Task 6.2：adapters README 同步

**Files:** Modify `adapters/{claude,codex,cursor,gemini}/README.md`（仅被删 toggle 处）

- [ ] grep 各 README 是否提被删 toggle，提到则更新指向新模型。
- [ ] **Verify:** `grep -rnE "commit_mode|model_invocable|status_auto|disabled_gates" adapters/` → 无残留。

### Task 6.3：本 deck 自迁移（dogfood 收尾）

**Files:** Modify `flightdeck/rules.md`（本项目自己的 deck）

- [ ] 跑迁移：本 deck 现为 `version: 2.3` + `model_invocable: [status]` + `status_auto: [start, land]`。改写为 `version: 3.0` + `disabled_folders: []` + `### 行为覆盖` 含 `<!-- migrated from model_invocable -->` "`preflight`/`landing`/`walkaround`/`emit-agents-md` 不要自调，我手动跑"（保留 status 可自调 = 不写它）。保留现有 `### 项目约定`（dogfood + applies_to 规则）。
- [ ] **Verify:** 跑 `/flightdeck:preflight` 与 `/flightdeck:walkaround` 全过，无 toggle 报错；status 仍可自调、其余手动。

---

## 末尾：一次性提交

- [ ] 全部 Phase 的 dogfood 通过后，`git add -A` 提交 spec + debrief + plan + 全部实现，单 commit，message 用 `checklists/commits.md` 风格、中文 body、无 AI 署名。
- [ ] 提交前 `git status` 确认无遗漏、无 scratch 残留。

---

## Self-Review（覆盖核对）

- spec §1 溶解图 → Task 1.2/1.3/2.1/6.1 ✓
- spec §2 推断（顺序/deck root/emit 不对称/警告）→ Task 1.1/1.3 ✓
- spec §3 内层门审计（硬前置 + scaffold 两出口）→ Task 2.0 ✓
- spec §4 House Rules 升权威 + 穿针匹配 + 两小节 + 冲突=用户责任 → Task 1.1/3.1 ✓
- spec §5 when-to-land（signal 1/2、位置、缺口）→ Task 5.1/5.2 ✓
- spec §6 迁移（3.0、3.x兼容、翻译表、注释、emit缺口）→ Task 4.1/4.2 ✓
- spec §7 影响文件 → Phase 1–6 全覆盖（含 scaffolds/adapters）✓
- spec §8 开放项（no-git HISTORY 格式）→ 未在本计划闭合，保留为 writing 期 TODO（spec §8 已记，非阻塞）。
