---
status: done
summary: 结构性设计 spec 完工后本体变身常驻 docs；配 when_to_update→stale 失效信号防悄悄过期；knowledge status 砍成 {active, stale, obsolete}（删 superseded 状态值），obsolete=knowledge 版 done 排水态，检测落进出场双仪式
last_updated: 2026-06-07
---

# 设计稿 graduate + 知识保鲜（when_to_update / stale）

## 一句话

让**结构性/设计约束类**的 spec 完工后**本体变身成常驻 docs**（当前真相层），并给这层配一个**失效信号**（`when_to_update` → `stale`），使它不会悄悄过期；同时把 knowledge 的 status 轴收成 `{active, stale, obsolete}` 三档，与 workflow 轴对称。

## 背景与动机

`spec-lifecycle.md` 第 6 步「graduate —— 知识沉淀进 docs/」已经描述了方向：特性上线后 spec 落进 `archive/`（冻结历史），而"它到底怎么运作"的耐久知识 graduate 进 `docs/`（当前真相）。但现状有两个缺口：

1. **graduate 是纯手工**——文档明说"没有 `source_spec` 字段追踪这次毕业（人手编辑）"。没有任何机制提醒/触发"这个 spec 该变成 docs"，依赖人记得手动搬。
2. **不分类型**——模型不区分"i18n 设计 / 错误码设计 / 插件系统"这种**结构性·大概率复用**的设计稿，和"修个 bug、加个一次性特性"这种用完即归档的 spec。前者本该沉淀，后者不该。

更深的风险：一旦让设计稿沉淀成常驻 docs，**docs 会悄悄撒谎**——i18n 改了、错误码体系重构了，但那份 docs 还停在旧真相上，新人/AI 读了反被误导。这比"没有文档"更糟。所以 graduate 必须配一个失效信号，否则就是在生产"自信的过期知识"。

**知识进 docs 有两条路**（本 spec 只新增第一条的机制，但要写明区分）：
- **graduate**：一份结构性设计**新建**成一份 docs（本 spec 的主题）。
- **实现直接更新既有 docs**：实现一个特性时顺手改 `model-architecture.md` 等既有 docs。**本 spec 自己走的就是这条**——它的耐久知识沉进既有 `model-architecture.md`/`spec-lifecycle.md`，不 graduate 成新 doc，所以本 spec frontmatter **不打 `graduate: true`**（不是遗漏，是用对了路）。

**使用前提**：本仓库 99% 是用户自己用 / AI 用，核心消费者是 AI；目标是"AI 跑完 preflight 就掌握项目结构性设计的当前真相 + 哪些发黄了"。不为人类新手另设专门入口（见 § 明确不做）。

## 设计

### 1. Graduate 机制

**从宽前置标记（创建/规划时）**

- 触发判据（命中**任一**即可，从宽——把关的是用户那一下点头，AI 不怕误标）：
  - **约束后续开发**：定义了后续代码必须遵守的规范/契约/接口（错误码表、i18n key 规范、插件协议、UI 设计 token）——"立规矩"而非"做一件事"。
  - **大概率被反复参考**：将来会被反复打开查阅，而非做完即不再看。
- 负例（像设计稿但**不该** graduate，给作者/AI 校准边界）：一次性 bugfix 的修复设计；只为排一次迁移步骤的 plan 式 spec；用完即弃的实验/探针设计；某个具体功能的实现方案（除非它顺带立了后续要守的规矩）。
- **两条路判据**（承接 § 背景）：该结构性知识若**已有 docs 条目在管**该主题 → 走"更新既有 doc"（不 graduate）；若是**全新结构域** → 走 graduate 新建。
- 触发点（**flag 窗口=整个 active 生命周期，非创建一瞬**）：`/flightdeck:new` 创建时、**或在执行 plan 的任意时刻**发现它符合，AI 都可主动问「标记为 graduate？」。降低"一次漏标即永久丢失"的风险——只要在翻 done 前任意时刻补标即可。
- 用户点头 → 在 spec frontmatter 打 **`graduate: true`**。把"要不要沉淀"的人类决策**前移到注意力还在这份设计上的时候**。

**承认的 tradeoff（诚实记账）**：
- **从宽 vs 误标疲劳**：AI 从宽提问可能误标、用户每次否决也是负担。这是刻意取舍——宁可偶尔多问一句，也不愿漏掉结构性知识。若实测误标率过高，降级手段是收紧判据话术（非加兜底）。
- **无 hint 漏标 = 用户责任**：完工时**不**二次识别、不兜底。代价是"早期被低估的设计"可能漏沉淀；换来的是零 landing 心智负担。用户已拍板接受。

**完工时收尾（landing，preflight 兜底——见 § 4）**

- 见 `graduate: true` 的 **done** spec → 把本体**改写成解释性 docs**（"当前真相"视角），搬进 `docs/`，落 `docs/INDEX`。
- **改写可保留 rationale**：graduate 不是强制失忆。若"当时为何这么设计 / 否决了哪些方案"有长期价值，改写后的 doc **可留一节 `## 设计权衡`** 承载。但承认一个 tradeoff：spec 里随手写的推理过程若不显式保留，改写成"当前真相"后会淡出，git log 能找回文件内容但不等价于结构化决策史——**这个损失是已知且接受的**（用户："历史当垃圾堆"）。
- **一份工件**：graduate 的 spec **不留 archive 双胞胎**（区别于现有 spec-lifecycle 的"历史+真相两份"）。原 `specs/` 下的文件在 graduate 时**改写后移动**成 `docs/` 那一份，源处不留。
- **新 doc 补齐 knowledge frontmatter**：graduate 改写时给新 doc 补 `when_to_read` / `applies_to` / **`when_to_update`**（spec 本无这些字段；不补则它一沉淀就脱离保鲜网）。
- **幂等 + 主/补偿**：graduate 转换 **landing=主路径、preflight=补偿**（§ 4）。幂等键=**可观察态**："`graduate: true` 的 done spec **仍在 `specs/`**" 才触发——一旦 landing 改写移走，触发键消失，preflight 扫不到、不会重复改写；若 landing 中途失败源文件还在，preflight 接着做。无需额外加锁/标记。
- **无 hint → 普通归档**：不沉淀、不二次识别。

### 2. 知识保鲜：`when_to_update` + `stale`

**`when_to_update` 字段（含格式约束）**

- graduate 出的 docs（及一般 knowledge 工件）frontmatter 加 **`when_to_update`**：一句"什么样的改动会让我失效"的触发条件。
- 与现有字段的区别：`when_to_read`="**读**它的时机"（消费侧路由）；`when_to_update`="什么样的改动让它**失效**"——与 `when_to_read` 对称。例：插件系统 docs — `when_to_read`=写新插件前；`when_to_update`=改了插件加载协议/加了生命周期钩子时。
- **格式约束（防误报/漏报）**——拆清"脚本能管"和"只能软引导"，别混（接 `external-memory-borrowings #3`）：
  - **lint 形式地板（脚本强制）**：`when_to_update` 非空 + 含 ≥1 个具体名词/路径 + 不含泛词黑名单（"任何/所有/all/any"）。`flightdeck_lint.py` 只做到这层。
  - **够不够具体（作者软指引，非脚本）**：诚实承认——"改了 X 协议"是否够具体是语义判断，lint 拦不住"改了错误码格式"这种仍含糊的写法。靠 templates 的**好/坏对照示例** + 作者自律，**不假装 lint 能强制语义**。

**检测落在进出场双仪式（修掉"持久化空头承诺"）**

- 失效检测（"本回合/上次干净以来的改动是否命中某 docs 的 `when_to_update`"）是 AI 语义判断，落在**两个**仪式：
  1. **exit-ritual（soft-landing/landing）**：回合末 AI 本就在分类新知识，对称加一问。命中 → 自动翻 `stale`。
  2. **preflight（进场·回溯安全网）**：进场必跑、比 landing 可靠。preflight 比对"**自锚点以来** git 改动 vs 各 docs 的 `when_to_update`"，补检 exit-ritual 漏跑的窗口。
- **锚点定义（3 家审核齐戳，设计级定死）**：锚点 = **上次退出仪式（landing/soft-land/checkpoint）记录的 git ref**；preflight diff `anchor..HEAD` + 工作树未提交改动；跑完把锚点推进到当前。**确切存储**（trailer / 小指针文件 / cockpit 字段）**落 plan**，但必须是**一个具体记录的 ref，不能是"凭感觉"**。
- **幂等**：stale 检测幂等——已 `stale` 的 doc 再命中=no-op；exit-ritual 先翻了，preflight 再判同一份只是确认同结果，不重复副作用。
- **为何要双仪式**：`stale` 的持久化只护**已写入**的标，不解决**检测本身漏跑**——exit-ritual 没跑（硬关对话）就没人写 stale，preflight 也只能读已存在的 stale、变不出来。把检测**也**放进 preflight（进场端），才真正补上"landing 不一定 100% 触发"的洞。两端同构、互为兜底。
- 命中即**自动翻 `status: stale`**（不先提议）：翻 stale 可逆、本地、纯警告，"docs 悄悄撒谎"是最坏结局，宁可多翻、错一秒就清；先提议会把每回合心智负担请回来。

**持久化 + 复核出口**

- `stale` 钉进 frontmatter + `docs/INDEX` + cockpit 浮一行待复核——状态钉在文件上，不随某次仪式漏跑而丢。
- 用户复核 → 改新使其当前 → 翻回 `active`；或确认已死 → 翻 `obsolete`（见 § 3，随后被排进 archive）。
- **退出闸是用户断言、非机械证据**：`stale → active` 同 workflow 的 `→ done` 一样——由**用户断言"我已让它当前"**触发，AI 不自评、不设"必须覆盖命中点 N 行"的机械门。一致沿用模型"用户断言、AI 不自certify"哲学。
- **规模 YAGNI**：不做 stale 优先级/去重/静默期。几十-百工件规模下，一次大改动命中多份 docs 是**信号非噪音**（确实都该复核）。疲劳风险已知且接受；真出现规模问题再议。

### 3. status 轴：`{active, stale, obsolete}`，删 `superseded`

knowledge status 从 `{active, obsolete, superseded}` 调成 `{active, stale, obsolete}`：

- **加 `stale`**（疑似过期·待复核）：§ 2 的黄灯。
- **删 `superseded`（状态值）**：grep 证实无 live knowledge 用它，且 `archive/specs/2026-06-02-metadata-model-consolidation` 显示它本就在被 `supersedes` 边取代。死/被取代的旧件 → 走 `obsolete` 排水。
- **保留 `supersedes`（关系边）= 纯溯源标注，不是归档钉扣边**（修正前一版的内部矛盾）：写在**新** docs frontmatter 上、指回它取代的旧件，仅供溯源/grep。**关键**：它**不进** `--archivable` 钉扣集（钉扣边只有 `implements:` / `superseded_by`，见 `flightdeck_index.py:358`）——否则新件 active 永远指着旧件、旧件就**永远排不掉**。旧件的死亡由它自己翻 `obsolete` 独立驱动，**与这条边无关**。旧件排进 archive 后，`supersedes` 指向 `archive/…` 是**合法历史指针**，无需维护其活性。**区分**：`superseded`（状态值，删）vs `supersedes`（溯源标注，留）。
- **`obsolete` = knowledge 版的 `done`**（关键对称，写进 model-architecture）：不是"堆在活跃区的原地墓碑"，而是**"已死·待归档"的排水触发态**——正如 workflow 的 `done`。
  - workflow：`idea → active → done →`（仪式排进 archive）
  - knowledge：`active/stale → obsolete →`（仪式排进 archive）
  - **preflight + landing 排空 `obsolete`**（与排空 `done` 同一套搬运逻辑）：检测到 `obsolete` 工件 → 提醒/排进 `archive/`。活跃区只留 `active`/`stale`，`obsolete` 只是排空前那一下。
  - **对称是精确的**：`obsolete`-未排空 ≡ workflow 的 **done-but-unlanded**（`spec-lifecycle.md:52`）——`done` 自己也可能滞留在源文件夹直到下次 landing 自动排干。所以"obsolete 会不会赖在活跃区"的答案与 `done` 一字不差：**会短暂滞留、靠下次仪式排干**，不是新问题。两者都是**用户断言的终态 + 仪式是唯一搬运者**。
- **归档文件冻结终态 status**：搬进 `archive/` 的文件保留它当时的 status（`done`/`obsolete`）作冻结历史；`flightdeck_lint.py` **已排除 `archive/`**（`line 292-296`：history 不受 current-state 规则约束），故"archive 里 status 该填啥"**无 lint 冲突**——填它死时那个值即可。
- **incident 回归 tripwire 随之搬家**：错误库的"根治退役 incident 当回归 tripwire"机制（`archive/specs/2026-06-05-incident-error-library-lifecycle`）原本靠 obsolete **原地** grep；现在 obsolete 被排进 archive，所以 **recurrence sweep 扩到也扫 `archive/incidents/`**，复发命中时**复活 = 从 archive 捞回翻 `active`**（原为原地翻回）。这是本 spec 对错误库子系统的唯一触动。

铁律统一：**活跃区只放活着（`active`）/ 发黄（`stale`）的；死的（`obsolete`）一律被仪式排进 `archive/`，不靠 status 标签长留原地。** 与 workflow 轴彻底对称。

### 4. 链路闭环（一张图）

```
设计稿命中判据 ─前置问(整个active期可补)─▶ graduate:true ─landing/preflight兜底─▶ 本体变身 docs(active,带 when_to_update)
                                                                                      │
        改动命中 when_to_update ──exit-ritual + preflight 双仪式自动──▶ status:stale + cockpit待复核行
                                                                                      │
                              钉进 frontmatter+INDEX ──任一仪式漏跑另一端兜──▶ 用户复核
                                                                                      │
                                          改新→翻回 active  /  确认死→obsolete ──仪式排空──▶ archive
```

## 实施面（落进 plan，不在本 spec 展开）

触及文件/模块：

- `skills/preflight/protocol.md`（status 枚举 `{active, stale, obsolete}`、lifecycle、graduate 接缝、obsolete=knowledge-done 排水、双仪式检测）
- `skills/preflight/exit-ritual.md` + preflight 仪式（when_to_update 检测两端、自动翻 stale、graduate 收尾 + 兜底、排空 obsolete）
- **stale 检测锚点的确切存储**（trailer / 小指针文件 / cockpit 字段三选一）——plan 选型并实现"退出仪式记录 ref + preflight diff anchor..HEAD + 推进 anchor"
- `skills/preflight/folder-semantics.md`、`skills/preflight/templates.md`（frontmatter 加 `when_to_update` + 好/坏示例、`graduate`、status 枚举）
- `skills/new`（创建时 graduate 前置问 + hint 字段）
- `skills/landing`（graduate 改写搬运、stale 浮现、排空 obsolete）
- `docs/model-architecture.md`、`docs/spec-lifecycle.md`（两轴 + graduate 两条路 + status 简化 + obsolete=done 对称 对齐）
- `scripts/flightdeck_index.py`（status 校验、INDEX 渲染、cockpit stale/obsolete 行、排空 obsolete 与排空 done 复用）
- `scripts/flightdeck_lint.py`（`KNOWLEDGE_STATUSES` 改 `{active, stale, obsolete}`、`when_to_update` 质量闸）
- 错误库回归 sweep（扩到扫 `archive/incidents/`、复活=un-archive）
- 对齐已记 incident `2026-06-07-workflow-has-no-superseded-status`（superseded 不是 workflow 状态；现 knowledge 侧也删 superseded 状态值、只留 supersedes 边——一并对齐措辞）

**迁移**：本 deck 实测 **0 个 live `obsolete`/`superseded` knowledge 文件**（grep 命中全在 `archive/` 或散文），迁移近乎 trivial。`flightdeck_lint.py` 已排除 `archive/`（`line 292-296`），归档文件不受新枚举约束。**用户自己的 deck** 若有 live `superseded` knowledge → 实施迁移文档要给一条规则（翻 `obsolete` 排空 / 或翻 `active`，逐件判断，非机械转换）。

## 前提与边界

- **单活跃会话前提（显式声明）**：本设计假定**同一时刻只有一个 AI 会话**在跑该 deck 的 preflight/exit-ritual。多会话并发改 frontmatter 的冲突协调**不在范围内**（单用户、顺序使用）。若未来要多开，需另立 spec。
- **archive 仍是冷存、不是活路由输入**：obsolete 排进 archive 后，sweep 偶尔 grep `archive/incidents/`、`supersedes` 偶尔指向 archive——这些是**按需 grep 的冷查**，archive 仍整体排除出路由；只有**显式复活**才把一个文件提升出 archive。冷存被偶尔扫 ≠ 活数据库。

## 明确不做（YAGNI）

- 不加人类新手专用门 / 架构总览特殊槽（需要时它自然是一条普通 graduate 的 docs）。
- 不加完工时兜底**识别**（无 hint 就不沉淀；但 graduate 转换本身在 preflight 有兜底）。
- 不留 graduate 的 archive 副本 / 不加 `source_spec` 溯源边（用户在 A/B/C 里已选"无溯源边"）。
- 不做 stale 优先级/去重/静默期（规模 YAGNI）。
- 不处理并发/多 agent（见上"单活跃会话前提"）。
- 不引向量库/DB/sidecar——保持 markdown + git + 仪式范式。

## 验收

**结构可断言（now，可脚本化）**：
1. `flightdeck_lint.py`：knowledge `status: superseded` 报非法；`status` 只接受 `{active, stale, obsolete}`；缺/空/过泛 `when_to_update` 被 flag。
2. graduate:true 的 done spec 跑 landing 后：`docs/` 下出现改写文档、源 `specs/` 文件已移走、无 archive 双胞胎、**新 doc 带齐 `when_to_read`/`applies_to`/`when_to_update`**（内容改写质量是判断，脚本只断言结构与字段齐全）。再跑一次 landing/preflight 不重复改写（幂等键=源文件已不在 `specs/`）。
3. 一个 `obsolete` knowledge 工件跑 preflight/landing 后被排进 `archive/`（与 `done` 排空同逻辑）。
4. 不跑 landing 直接进下一会话：preflight 扫到 `stale` docs 并提示；preflight 比对改动也能新翻 `stale`（双仪式兜底）。
5. 错误库 recurrence sweep 能命中 `archive/incidents/` 下的退役 incident 并复活。

**行为级（延后到 `external-memory-borrowings #7` 恢复回归测试）**：
- "AI 主动问是否 graduate"、"改动命中 when_to_update 语义判断" 这类依赖语义/交互的点，无法现在脚本化断言；按既定决策，**待恢复模型稳定后**用 #7 的行为级恢复回归测试固化，本 spec 不强行造测试。
