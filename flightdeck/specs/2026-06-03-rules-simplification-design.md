---
status: done
summary: 溶解 rules.md 结构化 toggle 集（推断 / 默认+House Rules / 仅留 disabled_folders），House Rules 升为 flightdeck 局部权威覆盖并定职责边界，附 0 配置 when-to-land
last_updated: 2026-06-03
related: [sketches/preflight-upgrade-nudge.md, sketches/status-spec-lags-plan.md]
---

# rules.md 简化 + 主动 land-readiness — 设计

## 背景与动机

`rules.md` 的 toggle 集发散到七个（`git` · `emit_agents_md` · `disabled_folders` · `disabled_gates` · `model_invocable` · `status_auto` · `commit_mode`），其中 `model_invocable` / `status_auto` / `commit_mode` **是同一件事"自主程度"的三种不同形状**（ritual 列表 / transition 列表 / 枚举）。配置过载，且多数 toggle 要么**可从环境推断**，要么**可用 House Rules 散文表达**。

借这次瘦身，顺带厘清 flightdeck 世界里"规则"的三个家的职责边界（House Rules vs CLAUDE.md vs checklists）。

## 目标 / 非目标

**目标**
- `rules.md` 瘦到 `version` + `disabled_folders` + House Rules。
- `git` / `emit_agents_md` 改为**从环境推断**，无 toggle。
- `commit` / `model_invocable` / `status_auto` 改为**给定默认 + House Rules 覆盖**。
- House Rules 限定 **flightdeck 作用域**，并定清权威顺序。
- 附带一个 **0 配置 when-to-land**（land-readiness 主动提示）。

**非目标**
- 不改 1.2 folder 布局（无文件夹重命名）。
- 不引入任何**新结构化 toggle**（when-to-land 走 0 配置）。
- 不改 `version` 字段本身的 migration-detection 机制。

## 1. Toggle 溶解图

| 现 toggle | 去向 | 说明 |
|---|---|---|
| `git` | **推断** | 工作区有 `.git` → git 模式；否则 no-git（staleness/history 走 `landed/HISTORY.md`） |
| `emit_agents_md` | **推断** | 自动 regen 仅当 repo root 已有 `AGENTS.md`；显式 `/flightdeck:emit-agents-md` 永远创建 |
| `commit_mode` | **默认 + House Rules** | 默认 `confirm`；House Rules 可改 auto / manual |
| `model_invocable` | **默认全开 + House Rules** | 默认所有 ritual 可自调；House Rules 可限 |
| `status_auto` | **默认全开 + House Rules** | 默认 `start` + `land` 都开；House Rules 可限 |
| `disabled_gates` | **删** | 实测从不偏离默认 → YAGNI |
| `disabled_folders` | **保留结构化** | 真在用，且"空文件夹 ≠ 主动禁用"推断分不清 |
| `version` | **不动** | migration detection 的家 |

瘦身后的 `rules.md`：

```markdown
---
version: <next>
disabled_folders: []
---

## House rules
- （仅 flightdeck 自己的约定 + 行为覆盖，散文）
```

## 2. 推断规则（精确）

**执行顺序（写死，防 skill 漂移）**：每个 skill **先读 House Rules 的相关覆盖**；命中则直接用、**跳过推断**；未命中才走下面的环境推断。（评审 #2）

**deck root 定义**（推断的锚点；无 `.git` 时也要有）：含 `rules.md` 的目录（即 `flightdeck/` 的父目录）即 deck root，`AGENTS.md` 落在该 root；找不到则回退 cwd **并附一条警告**（评审 #22，不静默——否则初次配置者会误以为 skill 在正确位置运行）。（评审 #3）

- **git**：从 deck root 向上找是否含 `.git`。有 → 走 git reconcile/commit + `git log` staleness；无 → 跳过 git，staleness/history 用 `landed/HISTORY.md`。House Rules 覆盖优先于推断（"本 deck 不走 git"）。
- **emit_agents_md**：**自动**路径（landing Step 5）—— 仅当 deck root 已存在 `AGENTS.md` 才 regen（不给没 opt-in 的项目硬塞文件）；**显式** `/flightdeck:emit-agents-md` —— 永远创建/覆盖（你跑它就是想要）。无 toggle。
  - **不对称须在 `templates.md` 明说**（评审 #10）：从"无 AGENTS.md"出发，**只有显式命令能 bootstrap** 它——否则用户会困惑"为什么 landing 不帮我生成"。
  - **例外**（迁移缺口，评审 #5）：用户**有 AGENTS.md 但不想让 flightdeck 动它** → 推断会误判成自动 regen，须靠一条 House Rule 关闭（见 §6 翻译表）。

## 3. 默认 + House Rules 覆盖

- `commit`：默认 `confirm`（生成 commit 后问 Y/n）。House Rules 例："提交不必询问，直接 commit"（=auto）/ "不要自动 commit，留给我或 CI"（=manual）。
- `model_invocable`：默认**所有 ritual 可自调**。House Rules 例："landing 不要自调，我手动 `/flightdeck:landing`"。
- `status_auto`：默认 **start + land 都开**。House Rules 可限其一。

**安全性论证（为何敢溶解 `model_invocable` 这个 gate）—— 这是一条「待 P2 前核对确认」的假设，不是已确认事实（评审 #1/#8）**：*假设*真正有破坏性的动作内层各自已有 confirm 门——commit 默认 confirm、land 归档移文件要 confirm、migration 要先问。若成立，外层 `model_invocable` gate 即 belt-and-suspenders 冗余。代价：失去一个**确定性 STOP**（结构化 gate 机械停住 → 改由 House Rules **软**约束承接，二者不等价）。

**内层 confirm 门审计 = P2 的硬前置条件**（不是风险备注）。审计**按副作用维度**看（评审 #19，不看 ritual 名——最终关心的是"是否产生不可逆副作用"）。**审计方法**：逐条在对应 skill/scaffold 代码里找 `write`/`move`/`delete` 调用，确认是否有 confirm 分支。**任一可改文件动作缺门者不得仅靠 House Rules 承接，须保留某种显式确认**：

| 动作 | 写文件 | 删除 | 移动 | 已有确认门 |
|---|---|---|---|---|
| landing（Land Routine） | ✓ | ✓ | ✓ | 有（archive confirm） |
| commit | — | — | — | 有（默认 confirm） |
| migration 改写 rules.md | ✓ | — | — | 有（提议改写询问） |
| status transition | ✓(frontmatter) | — | — | 通常无破坏性 — 核对 |
| emit-agents-md 覆盖写 | ✓ | — | — | 破坏性低 — 标注 |
| scaffold/模板改写 | ✓ | ? | — | **待核对** |

**scaffold 若审计发现无门**（评审 #20），两个出口：(i) 给 scaffold 改写加一个 confirm 询问；(ii) **局部保留 `model_invocable` 对该单一动作的结构化 gate**（保留既有字段子集，不算新 toggle）。P2 前置审计须先闭合此项，否则卡住 P2。

## 4. House Rules 职责边界 + 权威顺序

三个"规则之家"，按**作用域 + 形状**分工：

| 家 | 作用域 | 形状 |
|---|---|---|
| CLAUDE.md / AGENTS.md | 全项目、跨 agent | 项目 agent 规则 |
| flightdeck `rules.md` House Rules | **只管 flightdeck**（本 deck 局部） | 短、常驻约定 + flightdeck 行为覆盖 |
| flightdeck `checklists/` | flightdeck 路由的流程 | 长、按 trigger 加载、分步 |

- **House Rules 作用域收紧为只管 flightdeck**：本 deck 约定（"specs 用中文"、"不建 sketches/"）+ flightdeck 行为覆盖（commit/autonomy/git）。
- **通用项目约定推出去**：`"commit 前先开分支"` 这类通用规矩属 CLAUDE.md，**不该**进 House Rules。`templates.md` 现有范例混了这类，需**清洗**并明写边界。
- **权威顺序**（把 protocol 里含糊的"不能压过 agent rules"定清）：

  ```
  CLAUDE.md（项目） > flightdeck House Rules（deck） > flightdeck 默认
  ```

- **两小节结构**（评审 #12，采 GPT 建议）：House Rules 固定分

  ```markdown
  ## House rules
  ### 项目约定        ← "specs 用中文"、"不建 sketches/" 等
  ### 行为覆盖        ← Autonomy Policy：commit/autonomy/git 的覆盖
  ```

  概念名定为 **Autonomy Policy**（`### 行为覆盖` 段的内容），避免 House Rules 漫成一大段混杂。

- **行为覆盖的确定性识别 —— 穿针版**（评审 #12，用户拍板；**不**引入新 YAML toggle）：
  - 迁移**生成的**覆盖一律用 §6 翻译表的**固定标准句式**（视为"标准措辞"）；skill 对这些标准句做**宽松子串匹配**，**不依赖**逐次语义理解 → 跨模型（Claude/Gemini/Copilot/Codex）一致、可测。
  - **手写**的覆盖也认（语义领会），但 `templates.md` 推荐照标准句写。
  - 这解决了原稿"`### 行为覆盖` 是可选习惯、解析却依赖它"的矛盾：`### 行为覆盖` 段是**推荐约定**（写进 protocol），skill 优先在该段按标准句抓取；段不存在时退回全 House Rules 语义领会（容错，不报错）。
  - **被否的备选**（disposition #13）：保留 `model_invocable` 结构化形式、或 `commit: auto` 极简标记 —— 均为"在 prose 里重新长出配置"，与本设计初衷冲突，不采。
  - **匹配规则的单一真相源**（评审 #15/#16）：标准句表 + 匹配规则集中写进 `protocol.md` 一个专节（建议名 **Rule resolution order**），所有 skill **引用**它、不各自硬编码（防词表漂移）。`### 行为覆盖` 作为**字面量标题**写死在 protocol，skill 优先在该段内抓取。
  - **匹配范围跳过 HTML 注释行**（评审 #17）：子串匹配须忽略 `<!-- ... -->` 行，否则 `<!-- migrated from commit_mode:auto -->` 可能被误匹配。
- **House Rules 内部冲突 = 用户责任**（评审 #25，用户拍板）：本设计**不**定"同一行为多覆盖时自动择一"的解析语义（否决 last-match-wins）。House Rules 自身一致性由用户负责；skill 至多**被动提示**明显矛盾，**绝不静默择一**。

## 5. when-to-land（0 配置，收编）

- `exit-ritual.md` 新增 `## Land-readiness check`（单一真相源，与 Land Routine 并列）。判据：

  > **landable = 「刚有 artifact 翻到 done/awaiting-review」（signal 1） 或 「进场时 `git status` 显示 flightdeck/ ≥N 个改动」（signal 2）**

  N 默认 5，写死不配置；`git:false`（推断为 no-git）时 signal 2 关闭。（评审 #11：deck 很小（如 3 文件）可能永不触发 signal 2，但小 deck 的 land 紧迫性也低，非真问题；未来如需可让 N 随 deck 结构自适应，当前无此必要。评审 #24：no-git 关 signal 2 后留路标——未来可用 `landed/HISTORY.md` 的修改时间/行数增长替代。）
- **载体**：`status` 真翻一件事时搭一句（signal 1）；`preflight` 进场报一句（signal 2，一次进场一次，永不 nag）。
- **signal 1 的边沿如何实现**（评审 #4，stateless 澄清）：提示**就在 status 执行那次翻转的同一调用里**搭出——它**不是**一个独立的"检测到刚发生过 flip"的二次检查，而是翻转动作的附带输出。status 本就只在**真翻转**时动（forward-only，否则 no-op），所以"边沿"= 翻转动作本身，**无需存上一次状态**；幂等重跑遇 artifact 已 done → no-op → 不再响。不会重复 nag，也不会漏。
- **signal 2 的输出位置**（评审 #21）：作为 preflight 的**最后一行**或单独 `## Land-readiness` 小节，**不插在主输出中间**，免得用户没看到 preflight 主体就被打断。
- **力度**：要不要接着自动跑 landing，**复用** §3 的"默认全开 + House Rules"，不另加配置。
- **故意缺口（YAGNI）**：超长单会话里一直 churn 又从不翻 status 的情况，中途不提醒，等下次进场。不做"中途累积水位线"（需跨调用记状态，stateless skill 别扭、且最易演变成 nag）。将来真咬到再加。

## 6. 迁移（破坏性，双保险）

删 key = 破坏性 schema 变更（folder 布局未变）。版本号定 **3.0**（评审 #6；schema 不兼容比标 2.4 诚实）。把 3.0 列入 `MIGRATION.md` `layout_need_update`，触发**非静默**迁移。

- **(a) 兼容读旧 key —— 整个 3.x 保持读，4.0 删除**（评审 #7）：3.x 期间 skills 若见到旧 key（`git` / `commit_mode` / `model_invocable` / …）**仍 honor**，不在 3.x 中途 break 既有 deck；4.0 移除旧 schema 支持。
- **(b) 提议改写**：`preflight` 检测到旧 schema → 提议改写 `rules.md`：剥掉被溶解的 key，并把**非默认值翻译成 House Rules 句子**写进 `### 行为覆盖` 段。用户确认后改写（不静默）。
- **生成的 prose 带来源注释**（评审 #9/#26）：每条迁移句前加 `<!-- migrated from <key>:<value> -->`，用户知道出处、日后可自行清理；实现时**不得删**此注释（溯源价值）。匹配须跳过注释行（见 §4）。
- **预期的静默丢弃**（评审 #23）：旧 deck 有 `emit_agents_md: false` 但**根本没有** AGENTS.md → 推断已等价，迁移**静默丢弃**该条是**预期行为**，非遗漏 bug（实施卡注明）。

**非默认值 → prose 翻译表**（迁移用；这些即 §4 的"标准措辞"，skill 宽松子串匹配）：

| 旧 | 译成 House Rule（`### 行为覆盖` 内） |
|---|---|
| `commit_mode: auto` | `<!-- migrated from commit_mode:auto -->` "提交不必询问，直接 commit" |
| `commit_mode: manual` | `<!-- migrated from commit_mode:manual -->` "不要自动 commit，留给我或 CI" |
| `model_invocable` 缺某 ritual | "`<ritual>` 不要自调，我手动跑" |
| `status_auto` 缺 start/land | "status 不要自动 `<transition>`" |
| `git: false` | "本 deck 不走 git，历史记 landed/HISTORY.md" |
| `emit_agents_md: false` | **（评审 #5，不能丢）** "有 AGENTS.md 但不要自动 regen" —— 仅当 deck 确有 AGENTS.md 时译；若无则推断已等价、无需译 |
| `disabled_gates: [...]` | 删（已 YAGNI；若真用过，逐条转 prose 或保留警告） |

## 7. 影响文件

- `skills/preflight/SKILL.md` —— Step 0/1 读法改（推断 + 扫 House Rules）；migration 提议改写；进场 land-readiness signal 2。
- `skills/landing/SKILL.md` —— Step 0 读法改；commit step 读 House Rules 覆盖。
- `skills/status/SKILL.md` —— Step 0/1 读法改；land-readiness signal 1 搭话。
- `skills/walkaround/...` —— toggle 审计逻辑改（少了 5 个 key）。
- `skills/emit-agents-md/...` —— gate 改为 AGENTS.md 存在性推断。
- `skills/preflight/protocol.md` —— toggle 章节、authority order、inference 规则。
- `skills/preflight/templates.md` —— `rules.md` 模板瘦身、House Rules 范例清洗 + 边界说明 + 注释式覆盖范例。
- `skills/preflight/exit-ritual.md` —— 新增 `## Land-readiness check`。
- `MIGRATION.md` —— 新迁移条目 + `current` bump + `layout_need_update` 入账 + 翻译表。
- `scaffolds/...` —— 新 deck 的 `rules.md` 模板瘦身。
- `adapters/*/README` —— 若提到被删 toggle，更新。

## 8. 风险 / 开放问题

**已随三方评审解决（见 [debriefs/2026-06-03-rules-simplification-tri-review.md](../debriefs/2026-06-03-rules-simplification-tri-review.md)）：**
- ~~prose 覆盖可靠性~~ → §4 穿针版（标准句式 + 宽松匹配，非 toggle）。
- ~~失去确定性 STOP 的兜底~~ → §3 内层门审计升为 P2 硬前置。
- ~~版本号 minor vs major~~ → **3.0**。
- ~~兼容读旧 key 保留期~~ → 整个 3.x，4.0 删。

**仍开放：**
- **无 git 下 `landed/HISTORY.md` 维护规范**（评审 #14, defer）：各 skill 改写该文件的格式细节未定；不阻塞本设计，writing-plans 阶段排期。
- **内层 confirm 门审计的实测结论**：§3 表里 `scaffold/模板改写` 标"待核对"——P2 动手前须落实，若缺门则该动作不可仅靠 House Rules。

## 9. 验证（dogfood）

- 本 deck 先自迁移（剥 key + 翻译 House Rules），观察 friction。
- scratch deck 验：when-to-land signal 1/2 触发正确；House Rules 的 commit/autonomy 覆盖被各 skill 正确 honor；推断的 git/emit 行为正确。
- `walkaround` 全跑通（toggle 审计不报假阳性）。

## 实施分期（给 writing-plans 的提示）

- **P1**（低风险）：推断 `git` / `emit_agents_md`（含执行顺序 + deck root 定义 + emit 不对称文档）；删 `disabled_gates`。
- **P2 前置（硬门槛）**：完成 §3 的**内层 confirm 门审计表**；任一可改文件动作缺门 → 先补显式确认，再溶解 `model_invocable`。
- **P2**：`commit`/`model_invocable`/`status_auto` 默认化 + House Rules 覆盖（穿针版标准句式 + 宽松匹配）+ 兼容读旧 key（整个 3.x）。
- **P3**：House Rules 边界 / 权威顺序 / 两小节结构（`### 项目约定` / `### 行为覆盖`）/ `templates.md` 清洗 + 注释式覆盖范例。
- **P4**（**依赖 P3 完成** — 评审 #18：迁移生成的 prose 要写进 `### 行为覆盖` 段，该段结构/模板须先到位）：迁移（提议改写 + 翻译表 + `<!-- migrated from -->` 注释）；3.0 入 `layout_need_update`。
- **P5**：when-to-land（land-readiness check）。
