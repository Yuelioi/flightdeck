---
status: active
summary: 结构性设计 spec 完工后本体变身常驻 docs；配 when_to_update→stale 失效信号防悄悄过期；knowledge status 砍成 {active, stale} 两档，死亡只靠 archive 承载
last_updated: 2026-06-07
---

# 设计稿 graduate + 知识保鲜（when_to_update / stale）

## 一句话

让**结构性/设计约束类**的 spec 完工后**本体变身成常驻 docs**（当前真相层），并给这层配一个**失效信号**（`when_to_update` → `stale`），使它不会悄悄过期；同时把 knowledge 的 status 轴砍成极简两档，与 workflow 轴彻底对称。

## 背景与动机

`spec-lifecycle.md` 第 6 步「graduate —— 知识沉淀进 docs/」已经描述了方向：特性上线后 spec 落进 `archive/`（冻结历史），而"它到底怎么运作"的耐久知识 graduate 进 `docs/`（当前真相）。但现状有两个缺口：

1. **graduate 是纯手工**——文档明说"没有 `source_spec` 字段追踪这次毕业（人手编辑）"。没有任何机制提醒/触发"这个 spec 该变成 docs"，依赖人记得手动搬。
2. **不分类型**——模型不区分"i18n 设计 / 错误码设计 / 插件系统"这种**结构性·大概率复用**的设计稿，和"修个 bug、加个一次性特性"这种用完即归档的 spec。前者本该沉淀，后者不该。

更深的风险：一旦让设计稿沉淀成常驻 docs，**docs 会悄悄撒谎**——i18n 改了、错误码体系重构了，但那份 docs 还停在旧真相上，新人/AI 读了反被误导。这比"没有文档"更糟。所以 graduate 必须配一个失效信号，否则就是在生产"自信的过期知识"。

**使用前提**：本仓库 99% 是用户自己用 / AI 用，核心消费者是 AI；目标是"AI 跑完 preflight 就掌握项目结构性设计的当前真相 + 哪些发黄了"。不为人类新手另设专门入口（见 § 明确不做）。

## 设计

### 1. Graduate 机制

**从宽前置标记（创建/规划时）**

- 触发判据（命中**任一**即可，从宽——把关的是用户那一下点头，AI 不怕误标）：
  - **约束后续开发**：定义了后续代码必须遵守的规范/契约/接口（错误码表、i18n key 规范、插件协议、UI 设计 token）——"立规矩"而非"做一件事"。
  - **大概率被反复参考**：将来会被反复打开查阅，而非做完即不再看。
- 触发点：`/flightdeck:new` 创建 spec 时，**或**在执行 plan 的过程中发现它符合。AI 主动问「标记为 graduate？」。
- 用户点头 → 在 spec frontmatter 打 **`graduate: true`**。把"要不要沉淀"的人类决策**前移到注意力还在这份设计上的时候**。

**完工时无脑收尾（landing）**

- landing 见 `graduate: true` 的 **done** spec → 把本体**改写成解释性 docs**（"当前真相"视角，不是逐字搬"我们当时决定了什么"），搬进 `docs/`，落 `docs/INDEX`。
- **一份工件**：graduate 的 spec **不留 archive 双胞胎**（区别于现有 spec-lifecycle 的"历史+真相两份"）。历史当垃圾堆，靠 git log 兜底，要清再清。
- **无 hint → 普通归档**：不沉淀、不二次识别、不兜底提议。漏标 = 用户责任（换取零心智负担——每次 landing 都兜底=持续噪音，不值）。

### 2. 知识保鲜：`when_to_update` + `stale`

**`when_to_update` 字段**

- graduate 出的 docs（及一般 knowledge 工件）frontmatter 加 **`when_to_update`**：一句"什么样的改动会让我失效"的触发条件。
- 与现有字段的区别（避免重复造轮子）：
  - `when_to_read` = "**读**它的时机"（要消费这知识时）——消费侧路由。
  - `when_to_update` = "什么样的改动让它**失效**"——预先写下的失效触发条件，与 `when_to_read` 对称（一个管"何时读"，一个管"何时这份知识自己成了被改的对象"）。
  - 例：插件系统 docs — `when_to_read`=写新插件前；`when_to_update`=改了插件加载协议/加了生命周期钩子时。

**exit-ritual 兜底检查 + 自动翻 `stale`**

- 在 **soft-landing / landing**（回合末退出仪式）：AI 本就在分类"这回合产生了什么新知识"，对称地加一问——"这回合的改动**命中了哪份 docs 的 `when_to_update`**？"（语义判断，与 landing 是 AI 一遍过同构）。
- 命中 → **自动翻 `status: stale`**（不先提议）。理由：翻 `stale` 是可逆、本地、纯警告（不删不改内容），且"docs 悄悄撒谎"是这特性最坏结局，**宁可多翻、错了一秒就能清**，比漏判一份骗人文档安全；先提议又会把"每回合心智负担"请回来。

**持久化抗漏（接 cockpit + INDEX）**

- 失效发现**不当转瞬即逝的提示**，而是**持久化状态**：钉进那份 docs 的 frontmatter（`status: stale`）+ `docs/INDEX`，并在 cockpit 浮一行待复核。
- 这样即使 landing 没跑（硬关对话），状态也钉在文件上，**下次 preflight 必然扫到**（preflight 本就预热 `docs/INDEX`，`stale` 行自然浮现）。解决"landing 不一定 100% 触发"。

**复核出口**

- 用户复核 → 改文档使其重新当前 → 翻回 `active`；或确认已死 → **archive**（位置移动，见 § 3）。

### 3. status 轴砍到底（对称化）

knowledge status 从 `{active, obsolete, superseded}` 砍成两档：

> **`active`（当前真相） / `stale`（疑似过期·待复核）**

- **删 `obsolete`**：它是"原地墓碑"——把死知识留在活跃文件夹只挂"我死了"的牌子，违反模型自己的 **"drain, don't accumulate"**。死/不相关的知识 → 直接 **archive**（或真垃圾就删），不需要状态值。
- **删 `superseded`（状态值）**：同理，被取代的旧 docs 也是死的 → 直接 archive。"被谁取代"的历史交给 commit message + 新件上的边。
- **保留 `supersedes`（关系边）**：写在**新** docs frontmatter 上、指回它取代的旧件。有真实功能——给确定性归档判据当结构边（知道何时能 archive 旧件）+ 溯源。**注意区分**：`superseded`（状态值，墓碑，删）vs `supersedes`（关系边，新件上，留）。
- 铁律统一：**活跃区只放活着（`active`）/ 发黄（`stale`）的；死的一律靠 location（`archive/`）承载，不靠 status 标签。** 与 workflow 轴（`done` → archive、rejected=直接删、无原地墓碑）彻底对称。

### 4. 链路闭环（一张图）

```
设计稿命中判据 ─前置问─▶ graduate:true ─landing─▶ 本体变身 docs(active, 带 when_to_update)
                                                          │
            改动命中 when_to_update ──exit-ritual自动──▶ status:stale + cockpit待复核行
                                                          │
                          钉进 frontmatter+INDEX(不依赖landing) ──next preflight必扫到──▶ 用户复核
                                                          │
                                          改新→翻回 active  /  确认死→archive(位置移动)
```

## 实施面（落进 plan，不在本 spec 展开）

触及文件/模块：

- `skills/preflight/protocol.md`（status 枚举、lifecycle、graduate 接缝）
- `skills/preflight/exit-ritual.md`（when_to_update 兜底检查 + 自动翻 stale）
- `skills/preflight/folder-semantics.md`、`skills/preflight/templates.md`（frontmatter 模板加 `when_to_update`、status 枚举）
- `skills/landing`、`skills/preflight` 文案（graduate 收尾、stale 浮现）
- `skills/new`（创建时 graduate 前置问 + hint 字段）
- `docs/model-architecture.md`、`docs/spec-lifecycle.md`（两轴 + graduate + status 简化对齐）
- `scripts/flightdeck_index.py`（status 校验改 `{active, stale}`、INDEX 渲染、cockpit stale 行）
- `scripts/flightdeck_lint.py`（status 合法值、`when_to_update`/`graduate` 字段校验）
- 对齐已记 incident `2026-06-07-workflow-has-no-superseded-status`（superseded 不是 workflow 状态；现在 knowledge 侧也删 superseded 状态值、只留 supersedes 边——一并对齐措辞）

迁移：现存 knowledge 工件若有 `status: obsolete` / `status: superseded` → 实施时按"archive 或翻 active"处理（dogfood deck 自身先扫一遍）。

## 明确不做（YAGNI）

- 不加人类新手专用门 / 架构总览特殊槽（需要时它自然是一条普通 graduate 的 docs，模型已支持）。
- 不加完工时兜底识别（无 hint 就不沉淀）。
- 不留 graduate 的 archive 副本。
- 不引向量库/DB/sidecar——保持 markdown + git + 仪式范式。

## 验收（用户视角）

1. 创建一个"约束后续开发"的 spec，AI 主动问是否 graduate；点头后 frontmatter 有 `graduate: true`。
2. 该 spec 翻 done 后跑 landing → docs/ 下出现一份改写后的解释性文档，无 archive 双胞胎。
3. 在 graduate 出的 docs 上写 `when_to_update`，随后某回合改动命中它 → 退出仪式自动把它翻 `stale` 并在 cockpit 浮一行。
4. 不跑 landing 直接进下一会话 → preflight 扫到 `stale` docs 并提示复核。
5. `flightdeck_lint.py` 对 `status: obsolete`/`superseded` 报非法；knowledge 只接受 `{active, stale}`。
