---
status: done
summary: 彻底理清 flightdeck 生命周期+文件夹模型并立主流命名铁律——status⟂location正交(landed非状态/done≠归档)、done翻转 end-of-turn 防抖接力landing(方案A出厂默认/push先问)、归档判据确定性结构边(脚本可算/不靠AI正文)、航空名只留指令与仪式、数据模型全主流(charts→references、landed→archive、新增docs/)、knowledge可嵌套撑大型项目、status自动翻转收成唯一权威表；并入3.0
last_updated: 2026-06-05
---

# flightdeck 模型理清 + 主流命名铁律

## 心智模型（先拿简版）

flightdeck 模型 = **两条正交轴 + 一张翻转表 + 一处接缝**：

1. **文件夹 = kind，frontmatter = 状态**；kind 按两轴分：**自撰 vs 导入**、**一次性(workflow) vs 常驻(knowledge)**。
2. **status（做到哪一步） ⟂ location（在不在活跃区）**：`done` 不等于已归档；只有 `landing` 仪式搬运到 `archive/`。
3. **`done` 是唯一接缝**：到 done 就把控制权交给 `landing` 收尾；其余翻转都是 `status` 的轻量活。
4. **命名铁律**：航空隐喻只留指令/仪式/cockpit；文件夹、状态、字段一律主流词。

下面是完整推导。

## 背景 / 动机

两个观察触发本设计：

1. **「标 landed 但不跑 landing」的幽灵态**：AI 判定任务完成后，会口头宣称 landed（甚至写非法的 `status: landed`），却不真跑 `/flightdeck:landing` 的机械步骤（INDEX 重生、搬移、cockpit 重算、commit）。结果状态漂移：标着 landed，机械上没落地。
2. **整套生命周期 + 文件夹模型让人觉得绕**：`done`/`landed`/`landing` 关系不清、status 自动翻转规则散在多个 skill、status 与 landing 职责边界模糊、文件夹分类（尤其 `charts/` 这种航空隐喻烂名）让「东西该放哪」经常拿不准。
3. **真空**：当前没有任何文件夹装「本项目自撰的、常驻的技术资料」（架构/理念/子系统参考）。`checklists/` 是过程性、`charts/` 是外部导入，都不对口；散在 repo 根 `docs/` 的文件 preflight 也不读。大型项目尤其需要这一层且需分层。

根因诊断：

- **概念缺陷**：`protocol.md` 把 `done` 写成「complete, archived to landed/」——把「状态」和「位置」画了等号，喂出 AI 的「done = 已 landed」误判。
- **行为缺陷**：`status` 翻到 `done` 时默认只发一句 nudge、不真跑 landing；而「auto-run landing」虽在文里写了，Rule resolution order 里根本没有这个触发的定义，是悬空引用。全自动 AI 拿到「done + 没人执行的提示」就自己脑补 landed。
- **命名缺陷**：航空隐喻渗进数据模型（`charts/`、`landed/`），让本该一眼可懂的文件夹要先懂隐喻才能猜。

本设计对整个模型做一次彻底理清，并立下命名铁律。**全部并入未发布的 3.0。**

## 设计铁律：航空隐喻只留给交互面

> **航空隐喻只留给「交互面」——斜杠指令与仪式**（`flightdeck` / `cockpit` / `preflight` / `walkaround` / `landing` / `launch`，含每会话必读的 `cockpit.md` 仪表盘）。**数据模型——文件夹、状态、字段——一律用主流、普通开发者一眼能猜中的名字**。新人不懂航空隐喻也能猜出每个文件夹/状态干嘛。

应用结论：数据文件夹里两个航空隐喻名改主流——`charts/ → references/`、`landed/ → archive/`；状态值（`idea/active/done/scrapped`、`active/obsolete/superseded`）已全是主流词，**不改名**，唯一要修的是概念层（`landed` 不是状态）。`flightdeck/` 根目录是产品名保留；`cockpit.md` 归交互面保留。

## ① 核心概念修复：status 与 location 是两条正交轴

done/landed/landing 之所以绕，是三个不同范畴被混成一团：`done` 是**状态**（frontmatter 值），`landed/` 是**位置**（归档文件夹），`landing` 是**仪式**（收尾命令）。

理清后——**状态 ⟂ 位置，彼此独立**：

- **status** ∈ `{idea, active, done, scrapped}` —— 工件做到哪一步。
- **location** ∈ `{源文件夹, archive/}` —— 还在不在活跃区。**派生，不是 frontmatter 字段**。
- 一个 `done` 工件有两种合法位置：**done-but-unlanded**（仍在 `specs/`，因为有 `active` 工件还引用它）或 **done-and-archived**（已进 `archive/`）。
- **`landed`/`archived` 永远不是 status 值**，没有任何文件写 `status: landed`。
- **只有 landing ritual 的 Land Routine 能往 `archive/` 搬东西**；status 永不归档，AI 永不手写归档标签。

**location 是一等概念，只是不是 frontmatter 字段**：它由「在不在 `archive/`」派生，但驱动两件核心事——路由（`archive/` 整个排除在 routing graph 外）与归档判断（landing 据此判断该不该搬）。文档须点明这一点，免得读者以为 location 不重要。

一句话：**status 说「做到哪一步」，location 说「在不在活跃区」，landing 是唯一搬运工。**

落地动作：改写 `protocol.md` 原「`done` = complete, archived to landed/」一行为「`done` = 工作完成；**留在源文件夹直到 landing ritual 把它归档进 `archive/`**（done ≠ archived）」，并在 protocol Status 节 + status「Don't do」+ landing red-flags 加显式不变量：`archived` 不是状态值；除 landing Land Routine 外任何东西都不准进 `archive/`；AI 永不手写归档标签或在没跑 landing 时宣称已归档。

## ② status 自动翻转的唯一权威表

把散在 `status`/`protocol`/`exit-ritual` 的翻转规则收成**一张权威表**（放 protocol），其余文件只指向它、不再各自重述。

workflow 状态链：`idea → active → done`；`任意 → scrapped`。

| 触发时刻 | 翻转 | 谁做 | 自动？ |
|---|---|---|---|
| 写下新 spec/plan 进 `specs/`·`plans/`（仅捕获、未动手） | →`idea` | status | **总是自动** |
| 写下新 spec/plan 且**已在动手做**它 | **直接 →`active`**（合法直跳，跳过 idea） | status | **总是自动** |
| 开始动手做一个已存在的 idea | `idea→active`（+加 `YYYY-MM-DD-` 前缀 + 重生 cockpit `## 进行中`） | status | 默认自动（House Rule `status: don't auto start` 可关） |
| 用户批准 / 签收 | `active→done` | status/landing 接缝（见 ③） | **总是自动**（只翻 done，**不归档**） |
| 人工判定某方向被否决 | `任意→scrapped` | **仅用户显式指令**（自然语言或斜杠命令） | **永不自动**（AI 不得自行推断） |

铁规：

- **只进不退、幂等**：目标 ≤ 当前则 no-op。
- **`idea` 无日期前缀**，`idea→active` 是**唯一**改名点，且**幂等**——若文件名已含 `^\d{4}-\d{2}-\d{2}-` 前缀则不再加（同日不同 `<topic>` 本就不撞，无需冲突后缀方案）。
- **`scrapped` 只能由用户显式指令触发**（说「废掉这个」或 `/flightdeck:status`），AI 永不自行判定。`scrapped` 工件**留在源文件夹原地**、**不归档进 `archive/`**；在 INDEX 里**单列 `### 已否决（scrapped）` 分组**（与待启动池隔开、不污染它，但**仍可见**——若整个排除出 INDEX，routing 靠 INDEX，AI 反而看不到被否决的方向、失去"避免重提"的本意），由人手删。
- **`done` 的触发源 = 用户批准/签收**（对话里断言完成 或 `/flightdeck:status`），是**已断言的事实**，AI 不自评完成、不靠 smoke-check 判定。
- 每次翻转 bump `last_updated`（裸 `idea` 除外）。

知识类（`incidents/` `checklists/` `docs/` `references/`）状态 = `active / obsolete / superseded`，**无自动翻转**，由人设 obsolete/superseded（带 `superseded_by`）。

## ③ status / landing 职责接缝 + 自动真着陆（方案 A，防抖）

两仪式的**干净分工**：

- **status** = 轻 · 单工件 · 高频。只翻一个工件的 `status` + 它的 INDEX 行 + cockpit `## 进行中`。**不 commit、不归档、不 regen AGENTS、不长度检查**。主战场 `idea→active`。
- **landing** = 批 · 收尾 · 低频。分类新知识、重生改动文件夹的 INDEX、cockpit 全量更新、smoke-check、regen AGENTS、commit，**外加归档判断（Land Routine：把 `done` 工件搬进 `archive/`，带交叉引用判断）**。

**接缝 = `done` 翻转**（整套理清的关键咬合点）：

- `idea→active` 是轻活，status 自己干完。
- **`→done` = 「完成」时刻 = landing 的触发点**。**方案 A：done 翻转默认接力 landing**，不再只 nudge。status 本身仍不 commit/不归档，只是认出完成、把控制权交给 landing。

**防抖批处理（关键细化）**：done 翻转**不立即**逐个跑 landing，而是标记「欠一次 landing」，在 **AI 结束本轮、把控制权交还用户之前**（end-of-turn —— 一个**可判定事件**，不是"自然停顿点"那种实现不了的语义）跑一次 landing，把本轮内的多个 done 聚合进**同一次** landing；显式 `/flightdeck:landing` 也是触发点。这样既保留 A 的自治（不靠用户响应 nudge），又消除「连做 4 个工件 → 4 次 commit/regen」的浪费，也让 `done` 不再是「每个都触发重型仪式」。各 adapter 一律按 end-of-turn 实现，不各自解释。

**归档判据（确定性、可脚本计算）**：归档是**结构变更**，不能靠 AI 读正文得出"两次可能不同"的结论，故判据是**确定性结构边**：一个 `done` 工件**当且仅当没有任何 `active` 工件用结构化边指向它**时，归档进 `archive/`。边与方向严格定义——`implements:`（active plan → done spec：plan 指向它所实施的 spec）、`superseded_by`（active knowledge → 它取代的 knowledge）。`flightdeck_index.py` 把"可归档 done 集"算成**事实输出**（同输入同结论、可复现）；正文 markdown 链接**仅供人读、不进判据**（删掉之前的"读正文链接做 AI 判断"）。被 active 入边指向 → 留作 done-but-unlanded。

**排空，不积累**：**每次 landing 重新扫描全部 `done`-in-place 工件**（不止本会话新产生的），把入边已解除、现在可归档的一并搬走——故 done-but-unlanded **自动排空、不会无限滞留**；仍被指向的，由 walkaround 以 INFO 列出（带**阻挡它的 active 工件名**，而非含糊"原因"），重判由每次 landing 自动承担。

**失败路径**：landing 中途失败（如 INDEX 重生报错）→ 工件**停在 `done`、位置不变**（即 done-but-unlanded），**绝不回滚 status 到 active**（done 是已断言的事实，回滚会丢失真相）；报错让用户/下次 landing 接手。注意：**`done` 断言的是"用户对工件的批准"，不是"系统检查通过"**——故「已 done 但随后 landing 的 smoke-check 失败」是**合法、预期**的状态（工件已获批、收尾遇阻），两件事正交，landing 报错而 done 不回滚。

**心智模型**：status 管「做到哪一步」的日常保鲜；一旦到 `done` 就交棒给 landing 收尾＋决定归不归档。`done` 是唯一会触发重型仪式的状态，且经防抖聚合成一次。

**自治 / 可逆性**（默认贴「全自动 + 好默认」）：

- 防抖接力 landing 是**出厂默认**（可逆→自动，符合 3.0「可逆自动 / 外发先问」）；landing 内部仍**本地 commit 自动、push 先问**。
- 降级逃生口：House Rule `landing: nudge on done, don't auto-run`（仿 `commit: ask`，存于 `rules.md` 的 `### Autonomy overrides` 段），并在 protocol 标准短语表 + Rule resolution order 补上这条 landing 自动触发的定义（消除现有悬空引用）。
- **迁移窗口安全**：landing **已有 layout guard**——deck 结构落后（仍是旧名 `landed/`/`charts/`）时 landing **直接 STOP、点向先迁移**，不会在新旧结构间混写。故自动接力在未迁移 deck 上不会产生 `archive/`+`landed/` 并存的脏态。

效果：「标 landed 但不跑 landing」的非法中间态彻底消失——到 `done` 要么（防抖后）自动跑真 landing（→`archive/`），要么被 ritual 诚实标成 done-but-unlanded（walkaround 可见），不存在第三种幽灵态。

## ④ 文件夹分类 + 新增 docs/ + 主流命名全景

### docs/ 装什么 / 跟邻居怎么分

`docs/` = **自撰、常驻、解释性**的本项目技术资料——讲「系统怎么运作、为什么这么设计」：架构、设计理据、子系统概览、模块参考、生命周期/理念。

四条边界：

| 对比 | 区别 | 一句话判据 |
|---|---|---|
| `docs/` vs `checklists/` | 解释性 vs 过程性 | docs 是你**读懂**的；checklist 是你**执行**的 |
| `docs/` vs `references/` | 自撰 vs 外部导入 | docs 是**我们写**的；references 是**外面来**的 |
| `docs/` vs `specs/` | 常驻 vs 一次性 | spec 是「打算建造然后归档」的设计意图(有 idea/active/done)；doc 是「描述已建成系统」的常驻参考，不随完工归档 |

**混合型裁决判据**（如 `release-process.md` 既像步骤又像知识）：看**主要用法**——你主要是**逐步执行它** → `checklists/`；主要是**读它理解系统** → `docs/`。若一份文件真兼具且都重，**拆成两份**（步骤进 checklists、原理进 docs，互链）。默认偏「执行」入 checklists。

**docs/ vs archive/spec 的真相归属**（避免双份真相）：沿用 protocol 既有 source-of-truth 优先级——**归档件输给当前活跃态**，故 `docs/`（活跃 knowledge）**权威高于** `archive/` 里被归档的 spec。一个特性发布后，它的 spec 落进 `archive/`（历史），而「它最终怎么运作」的持久知识**毕业进 `docs/`**（当前真相）。**不追踪"毕业来源"**（不加 `source_spec`/`graduated_from` 字段——毕业是人的编辑动作，非被跟踪的边）。

二者**本就该分叉**：`archive/spec` 是**冻结的历史快照**，`docs/` 是**演进中的当前真相**——这不是"知识漂移"，而是"历史 ≠ 现状"的预期；要追源用 git 历史或正文自述即可，不设追源字段。

文件命名：`<topic>.md`（无日期前缀，常驻参考，同 checklists/incidents）。frontmatter 用知识类那套（`status: active/obsolete/superseded` + `when_to_read` + `applies_to` + `last_updated` + `summary`），以便被路由预热。

### 撑大型项目：按轴嵌套

**嵌套规则按轴划**（非任意特例）：

- **knowledge 文件夹可按 area 嵌套**（`incidents/` `checklists/` `docs/` `references/`）：`<folder>/<area>/` 带 `<folder>/<area>/INDEX.md`。子目录只能是**同一 kind 内的组织分区**，**绝不是另一种 kind**——避免重新引出「子文件夹是什么 kind」的老问题。
- **workflow 文件夹严格扁平**（`specs/` `plans/`）。理由是**容量有界**（不是历史选择）：workflow 一次性、`done` 后流向 `archive/`，活跃集天然不累积——扁平 + INDEX 日期排序即够；真要按 feature 分组，用 **INDEX 手区分组**（非子目录）。knowledge 则**常驻、只增不归档**，会无界膨胀，才需按 area 嵌套。即"排空 vs 累积"的推导。
- **嵌套深度不人为设限**：每一级目录都带自己的 `INDEX.md`，**INDEX-of-INDEXes 逐级串联**。
- **INDEX-of-INDEXes 路由**（撑规模的关键）：顶层 `<folder>/INDEX.md` 列各 area，**每行带一句用途描述 + `last_updated`**（不只 area 名）；每个 area 的 `INDEX.md` 列该 area 内容。
- **preflight 只读顶层 INDEX**：它是 **catalog 预热（know-what-exists）**——读 INDEX 的 markdown 行（含每 area 的一句用途 + 每条 `summary`），**不读正文、不做 RAG/embedding**，正文按需用 Read 下钻。这是**刻意的按需路由**（与 checklists/incidents 一致，从不预载正文）：preflight 让 AI **知道存在什么、何时该去读**，而非把知识正文塞进上下文。`last_updated` 让它优先点出近期改动的 area。大型项目也不撑爆 preflight。
- **修原始痛点**：把 `docs/` 加进 preflight catalog 预热（现仅热 checklists/INDEX + incidents/INDEX）。

### 应用主流铁律后的完整分类全景

```
flightdeck/                  [产品名·保留]
├── cockpit.md               [交互面·航空名保留]   rules.md   INDEX.md
│
├── specs/        设计&想法        workflow(idea/active/done/scrapped)   自撰·一次性·扁平
├── plans/        实施计划          workflow                              自撰·一次性·扁平
├── incidents/    bug 复盘          knowledge(active/obsolete/superseded) 自撰·常驻·可嵌套
├── checklists/   过程/规范(执行)   knowledge                             自撰·常驻·可嵌套
├── docs/         技术资料(读懂) ★  knowledge                             自撰·常驻·可嵌套
├── references/   外部导入(旧charts)knowledge                             导入·常驻·可嵌套
│
└── archive/      归档(旧landed) + HISTORY.md        location(非 kind)
```

**两条正交轴，整套模型这么记**：

- **自撰 vs 导入**：只有 `references/` 是导入；其余都是自撰。
- **一次性 vs 常驻**：`specs/`·`plans/` 是一次性 workflow（带 idea/active/done，建完归档，扁平）；`incidents/`·`checklists/`·`docs/`·`references/` 是常驻 knowledge（active/obsolete/superseded，长期查阅，可嵌套）。
- **嵌套 = knowledge 可、workflow 不可**。
- **`archive/` 是一级结构容器**（镜像源 kind、有 `HISTORY.md`、landing/index/migration 专门处理它），但它**不是一种 kind**——不回答"这是什么工件"（工件保留自己的 kind），只回答"在不在活跃区"。强调"非 kind"是为正交轴清晰，不代表它不重要。

## 连带改动面（细节留给实施计划）

- **scaffold/launch**：建 `docs/` + `docs/INDEX.md`；把 scaffold 里 `charts/`→`references/`、`landed/`→`archive/`。
- **`flightdeck_index.py`**：认 `references/`/`archive/`/`docs/`；knowledge 文件夹的 INDEX-of-INDEXes 生成（顶层 area 行带一句用途 + `last_updated`）；root INDEX 加 docs/ 行；`archive/HISTORY.md` 路径；`specs/INDEX` 增 `### 已否决（scrapped）` 分组；**新增"可归档 done 集"计算**（无 `active` 入边 `implements:`/`superseded_by` 指向的 `done` 工件 → 确定性事实输出，供 landing 归档；可加 `--archivable` 或函数）。
- **preflight**：catalog 预热加 `docs/INDEX.md`（顶层）；land-readiness/版本路径里的 `landed/` 字样改 `archive/`。
- **landing**：分类启发式加 docs/ 分支；Land Routine 目标改 `archive/`，归档**用 flightdeck_index 的确定性"可归档 done 集"（不读正文判断）**；**每次扫全部 done-in-place 排空**；**end-of-turn 防抖聚合**多个 done 成一次；补 `landing: nudge on done, don't auto-run` 降级与默认接力定义；写明兼容窗口内 layout guard 使自动归档暂停的后果。
- **status**：done 翻转在 **end-of-turn** 接力一次 landing；「Don't do」加「不手写归档标签」。
- **walkaround**：审计认 `docs/`（含嵌套 INDEX-of-INDEXes）+ 新文件夹名；列出 done-but-unlanded（INFO，带**阻挡它的 active 工件名**）；旧 `charts/`/`landed/` 存在 → `structural-behind`，缺 `docs/` → INFO 补建。**不对称的理由**：旧名存在会让 preflight 读错路径 / INDEX 生成出错（影响功能正确性，故 structural-behind）；缺新文件夹只是功能未启用（故 INFO）。
- **`MIGRATION.md`**：写 3.0 改名迁移条目（`charts/→references/`、`landed/→archive/`、新增 `docs/`），进 `layout_need_update`；verdict 据此对老 deck 报 `structural-behind`。
- **protocol / folder-semantics / templates / exit-ritual / README / 各 adapter**：全面对齐主流铁律、正交轴模型、权威翻转表、接缝定义、docs/ 语义与按轴嵌套规则。
- **本 dogfood 仓库自身**：把 repo 根现有散装 `docs/`（architecture/philosophy/comparison/lifecycle/README）迁入 `flightdeck/docs/` 并配 INDEX（验证新文件夹 + 路由真生效）。

## 迁移（老 deck）

`charts/→references/`、`landed/→archive/` 是结构性改名，需 author-confirmed 迁移（walkaround 提供，永不静默）。`MIGRATION.md` 列出搬移步骤；`docs/` 为纯新增（不触发已存在 deck 的迁移失败，缺它由 walkaround 作 INFO/补建）。3.x 内对老名做**兼容读取窗口**（读但提示迁移），4.0 移除。迁移期写行为由 landing 的 layout guard 兜底：结构落后 deck 上 landing **STOP 让先迁移**，不混写新旧结构。

**已知后果（须写明）**：兼容窗口内，未迁移 deck 上 done 接力 landing 会撞 layout guard → 报「先迁移」而非归档，故**自动归档/bookkeeping 在迁移前实质暂停**，done 工件留原地直到用户迁移——这是安全设计的**已知代价、非 bug**。文档须明说，免得用户以为"自动 landing 坏了"。

## 非目标 / YAGNI

- 不改状态值集合（已主流）；不改仪式名（航空名是交互面，保留）。
- 不给 `specs/`/`plans/` 开子目录（workflow 严格扁平；嵌套仅 knowledge）。
- 不引入 `location` frontmatter 字段（location 是派生的，由「在不在 `archive/`」决定）。
- **不新建反向引用索引字段**（`depends_on`/`refers_to` 等）——归档的交叉引用判断靠 AI 读现有边（`implements:`/`superseded_by`/正文链接），符合 flightdeck 判断驱动 + 最小 frontmatter。
- **不加 `source_spec`/`graduated_from` 字段**追踪 docs"毕业来源"——毕业是人的编辑动作，靠 source-of-truth 优先级（docs 活跃 > archive 归档）解决真相归属即可。
- 不为 `idea→active` 改名做 `-2/-3` 冲突后缀方案（不同 topic 不撞，YAGNI）。
- 不做 docs/ 的全文索引/搜索（INDEX-of-INDEXes 已够路由）。
- 不把 preflight 变成知识正文预载器——它只 know-what-exists，正文按需 Read（拒绝"preflight 应 surface 知识内容"的要求）。
- 归档判据**不含 AI 正文判断**——只认确定性结构边（`implements:`/`superseded_by`），保证同输入同结论。
- **不为消除"两个完成态"而砍掉 location 轴**：done-but-unlanded 与 done-and-archived 是**同一 status 的两个 location**，由一行确定性规则决定、且归档件移出视线；location 轴在"既不误 archive 被引用件、又要归档已完成件"的需求下**不可约减**——砍了它，要么 done 永不归档（archive/ 失去意义），要么破坏交叉引用安全。只能把它的认知成本压到最小（确定性 + 不可见）。

## 验收

- protocol 里 `done` 不再等于 archived；status⟂location 有单一权威表述、location 标为一等派生概念；自动翻转一张表（含直跳 active、scrapped 仅人工）、接缝一处定义、landing 自动触发在 Rule resolution order 有定义（无悬空引用）。
- 新建 deck 的 scaffold = 主流分类（`references/`/`archive/`/`docs/`，无 `charts/`/`landed/`）。
- `flightdeck_index.py` 对含嵌套 knowledge 文件夹的 deck 正确生成 INDEX-of-INDEXes；pytest 全绿；`flightdeck_index.py --check` clean。
- 老 deck 跑 walkaround 报 `structural-behind` 并能按 MIGRATION 完成改名迁移；缺 `docs/` 报 INFO。
- 本仓库 `docs/` 迁入 `flightdeck/docs/` 后，preflight 能在 catalog 预热里报出技术资料 area。
- reload 后交互 dogfood：连做多个 done 在 **end-of-turn 聚合成一次** landing；`flightdeck_index` 能算出"可归档 done 集"（确定性、同输入同结论）；landing 每次扫**全部** done-in-place、排空已解除入边的；无「标 landed 不跑 landing」幽灵态。
