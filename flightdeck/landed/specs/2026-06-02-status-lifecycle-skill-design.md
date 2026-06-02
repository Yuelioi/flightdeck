---
status: done
---

# 新增第 5 仪式 `flightdeck:status` —— 状态生命周期自动翻转

**日期**：2026-06-02
**来源**：YHFish 用户实战诉求 —— "很多 spec 做完了状态还挂 awaiting-review；正常不是该在任务开始/执行/结束自动更新状态吗？skill 应该加生命周期自动化。"
**状态**：设计定稿（双层配置 + 三方 review 修正已并入），待实现。
**依赖**：[soft-config-model-invocation](2026-06-02-soft-config-model-invocation-design.md)（**已落地** 2026-06-02：`model_invocable` 软门栓替换 `disable-model-invocation` 硬开关）。

> **定稿记录**：
> - **v1 → v2（设计对话 + GPT review）**：三争议点拍板 —— `done`+land 支持但下放 `status_auto`；`start→active` 也软配置；配置形态 = opt-in list（核心转换始终自动）。GPT 三处措辞（`status_auto` 语义 / done 与 land 解耦 / land 例程 DRY）并入。
> - **v3（Claude + DeepSeek + GPT 三方 review）**：补 11 项实现前收口 —— artifact 选定置信规则、`pending→awaiting-review` 直跳、`description` 候选草稿、来源区分具体规则、land 例程抽取为公共锚点、INDEX 更新策略、rules.md 缺失 fallback、手动调用绕过门栓、sketches/幂等边界并入状态机、preflight 感知 done-but-unlanded、验证/toggle 表措辞。

---

## 背景 / 真实现状盘点（别在误解上造方案）

诱因是 YHFish 用户感觉"很多 spec 做完了还 awaiting-review、像 flightdeck 的 bug"。实地盘点后，**现状和这个感觉有出入**，记录下来免得照错的前提设计：

- YHFish 的 `landed/` 里已有 ~75 spec + ~65 plan 规规矩矩落地——"做完 → landed" 这条纪律一直在跑，**没有大面积烂尾**。
- 当时真·awaiting-review 的 spec 只有 2 个，其中一个是"代码完成但真机 smoke 待验"——**这个状态是对的**，本就该停在 awaiting-review 等验，不是 drift。
- 真正的轻微 drift 在 plans/：两个 plan 代码完成了却还挂 `active`，没跟着翻 awaiting-review。

**根因不是"flightdeck 坏了"，是它本来就没这设计**：

- 状态变更**只在用户手敲 `/flightdeck:landing` 时、由模型"建议"、用户"确认"后**才发生（landing SKILL.md step 3a 原文：AI *may suggest* the next status，applied only after the user confirms）。`preflight` 是纯只读。
- plugin 里**零 hook、零脚本**（`plugin.json` 只声明 `skills/`）。
- 所以只要某次没跑 landing、或 landing 时模型没顺手翻 plan 状态，就留 drift。

**为什么"自动"只能靠 skill、不能靠脚本**：用户想要的"开始/执行/结束自动翻状态"里，"开始执行某 spec"是个**语义事件**。确定性脚本（hook）只看得到工具调用和提示词，**看不到意图**，没法可靠判断"这个 spec 现在开始做了"。所以真正能落地的"自动"只有靠 **skill**（提示模型在该翻的节点翻状态）。`soft-config-model-invocation` spec 的 §未来可选 已分析并否决了 SessionStart hook 注入方案，理由同源——本 spec 不走 hook。

---

## 依赖：`soft-config-model-invocation`（已落地）

本 skill 要能**被模型自调**（自动触发是它的全部价值）。`soft-config-model-invocation` spec 已于 2026-06-02 落地，提供两层机制：

1. **去掉 frontmatter 硬开关**（平台层放行）；
2. **rules.md `model_invocable: []` 软门栓**（per-project opt-in，默认全关 = 现状不变）。

本 skill 直接复用这套：自己**不带** `disable-model-invocation`，自己用 `model_invocable` gate 守住（见下 §配置 第 1 层）。来源区分的**具体规则**见 §配置。

---

## 方案

### 定位

新增第 5 个仪式 skill：`skills/status/SKILL.md`。在 `preflight / walkaround / landing / emit-agents-md` 之外，它是**唯一"高频、轻量、可自调"**的 skill（其余四个低频、重操作、仪式化）：

- **只**改单个 artifact 的 frontmatter `status` + 它在所属 folder INDEX 的那一行（+ 必要时根 INDEX 该 folder 计数）。`land` 启用时**额外**移文件进 `landed/`（确认门控，见状态机）。
- **不**动 cockpit（状态可见性本就活在 folder INDEX，不在 cockpit——遵循现有协议）、**不** commit、**不**跑 length check / AGENTS.md regen。
- 与 landing 互补，不是替代：见下「与 landing 的关系」。

### Artifact 选定 —— 置信规则（本设计最脆弱处，三方 review 共识 #1）

所有自动翻转都建立在"status 知道在更新**谁**"之上。上下文里常同时有多个 artifact（如 spec A + plan B），用户一句"实现这个"可能指向任一。**翻错对象比漏翻危险得多**：漏翻可由 landing/preflight 兜底恢复；翻错难被发现，且 forward-only 也救不了。故定一条硬规则：

**按优先级唯一定位目标 artifact：**
1. 本回合**正在写入/编辑**的那个 flightdeck artifact；
2. 当前**正在执行**的 plan（executing-plans 上下文绑定的 artifact）；
3. 本会话**最近创建**且无歧义的 artifact；
4. **以上都无法唯一确定 → 不自动翻**（静默跳过，可留一句提示让用户手动）。

> **原则（写进 SKILL.md）**：*If the target artifact cannot be identified with high confidence, status MUST NOT perform an automatic transition.* 两害相权：自动漏翻可恢复，自动翻错难发现。

### 触发契约（`description` 决定平台何时自调）

model-invocable。`description` 编码四个生命周期时机。**核心两跳始终自动；两个争议跳由 `status_auto` 软配置 opt-in**（见 §配置 第 2 层）。每个触发都先过上面的 artifact 置信规则：

| # | 时机（模型在做什么） | 锚点（实现可靠性） | 目标状态 | 类别 |
|---|---|---|---|---|
| 1 | 往 `flightdeck/{specs,plans,sketches,…}` **写入新 artifact** | **确定事件**（写文件，非语义猜测）——最可靠 | `pending`（sketches→`active`） | **核心·始终自动** |
| 2 | 绑定 artifact 的活**完成、准备 commit** | 语义判断，但锚定在"**用户要求 git commit 前的那一推理瞬间、且上下文有在执行的 plan/spec**"；awaiting-review 低风险 + landing 兜底，故仍入核心 | `awaiting-review` | **核心·始终自动** |
| 3 | **开始执行**某 flightdeck plan（进 executing-plans / 动手实现） | 最软语义（"现在算开始了吗"模糊）——故 opt-in | 该 artifact `active` | **可选**·`status_auto:[start]` |
| 4 | 用户 **review 通过 / 签字**（approved / lgtm / ship it 之类） | 依赖用户明确语句；**仅当 `status_auto` 含 `land` 时才响应**（否则交 landing，避免"开了 review 没人理"的困惑） | `done` →（确认后）land | **可选**·`status_auto:[land]` |

### `description` 候选草稿（成败关键，先给实现者一版校验靶子）

> Use to keep a flightdeck artifact's lifecycle status fresh and its folder INDEX row in sync. Identify the target artifact with **high confidence** (currently-edited file → current executing-plan → most-recent unambiguous creation); if none is unambiguous, do nothing.
> **Always-auto** (when self-invoked and `status` ∈ rules.md `model_invocable`): (1) right after **writing a new file** into `flightdeck/{specs,plans,sketches,…}` → set `pending` (sketches → `active`); (2) in the **reasoning moment just before a user-requested commit** that finishes a plan/spec's work → set `awaiting-review`.
> **Opt-in** (only if the member is in rules.md `status_auto`): `start` → when **beginning execution** of a plan, set `active`; `land` → when the **user approves/signs off**, set `done`, then ask before archiving.
> **Never** fires on ordinary edits (typo/wording fixes), and never does `start`/`land` moments unless opted in. Forward-only: never downgrades a status.

实现时按真实平台触发表现再打磨此文本（见落地清单）。

### 状态机（forward-only，含直跳 / sketches / 幂等边界）

- 规范推进链：`pending → active → awaiting-review → done`。允许**跳过中间态直跳**：因 `active` 默认不自动设，`finish` 触发时常是 `pending → awaiting-review` **直跳**——**合法**（不要求必经 `active`）。
- **核心两跳**（create 落 `pending`、finish 落 `awaiting-review`）**始终静默自动**，不受 `status_auto` 控制。
- **`start → active`**：仅当 `status_auto` 含 `start` 时自动；否则不碰。
- **`done` 与 land 解耦**（review 共识）。仅当 `status_auto` 含 `land` 时 status 才介入收尾，分两步：
  1. **`set done`——自动**。"review 通过"是用户已断言的**事实**，`done` 跟着落定，不单独要确认。
  2. **`land`（移文件进 `landed/` 镜像结构、删 folder INDEX 行、改根计数）——破坏性操作，必须停下确认**。
  - **拒绝 land 确认 → artifact 停在 `done` 但未归档（done-but-unlanded），状态不回退**；后续 preflight/landing 拾起归档（见落地清单 preflight 依赖）。固定措辞：**done is automatic; land remains confirmation-gated.**
- **sketches 例外**：sketches 合法状态通常只有 `active / scrapped`（见协议），故 create 落 `active` 而非 `pending`；sketches 不参与 `awaiting-review/done` 链。
- **只前进不后退（幂等）**：目标 == 当前 或 比当前更靠后 → **no-op**，绝不静默降级。边界例：用户先手动把新文件设成 `active`/`done`，create→pending 触发时 → no-op（不降级、不报错）。保证可重复触发安全。
- `blocked` / `scrapped` 仍是**显式人工**动作，本 skill 不自动碰。

### INDEX 同步（明确策略，避开脆弱的计数算术）

翻完 frontmatter，**复用 landing 的"单 folder AUTO 区重生"逻辑**（不做整库、不做易错的 +1/−1 行内计数算术）：

1. **全量重生受影响 folder 的 `INDEX.md` `<!-- AUTO -->` 区**——folder 内文件通常很少，重生廉价且确定。
2. 从重生后的 folder INDEX **重算根 `flightdeck/INDEX.md` 里该 folder 那一行的计数**。其它 folder 行不动。

理由：drift 的**症状**正是 INDEX 过期（preflight/外部读 INDEX 当真相）。状态变了不同步 INDEX，等于没治本。重生整 folder 区比"定向改两个计数"更不易错。

---

## 配置（两层软门栓，正交，不合并）

两个维度回答**不同**问题，分两个 rules.md 键，**不要合并**：

### 第 1 层：`model_invocable` —— 模型能不能自调 status

复用已落地的 soft-config 机制：

- SKILL.md **不带** `disable-model-invocation`；**Step 0 gate** 读 rules.md。
- **来源区分具体规则**（不再空引用）：判定"用户手敲 `/flightdeck:status`" vs "模型经 Skill 工具自调"，沿用四仪式已落地的同一 gate —— 关键信号是**用户 slash 会注入 `<command-name>/flightdeck:status</command-name>` 标记，模型自调没有**（Claude Code = 正式版）；平台不暴露该信号时**退化版**：`status` 不在 `model_invocable` 即按手动处理、提示用户手敲。具体见 `skills/*/SKILL.md` 已落地的 `## Step 0 — model-invocation gate` 正文，status 原样复用，不另造。
- **gate 只拦自调**：用户手敲 `/flightdeck:status` **绕过** `model_invocable` 门栓（门栓只约束模型自调）。
- 默认 / 缺失：`model_invocable: []`（或 **无 rules.md** 视同空）→ status 默认不自调。要用：`model_invocable: [status]`（可与 landing 等并列）。

### 第 2 层：`status_auto` —— status 被调用后，允许哪些**可选**转换

```yaml
# rules.md
status_auto: []
# no optional transitions enabled
# core transitions (create→pending, finish→awaiting-review) remain automatic
```

- **opt-in list，核心转换始终开**。`create→pending` / `finish→awaiting-review` **不属于** `status_auto`，永远自动。`status_auto: []` = 「不启用任何**可选**转换」，**不是**「只启用可靠转换」。
- 合法成员：`start`（开 `start→active`）、`land`（开 `done`+land 收尾：done 自动 / land 确认门控）。
- 例：`status_auto: [start, land]` = 全自动（land 仍逐次确认）。
- **不再细化**：成员只到 `start` / `land` 粒度，**不**引入 `start_after_first_edit` 或把 `create/finish/review` 也列进来的子开关（防 per-transition 蔓延）。

> 这是 rules.md 闭合 toggle 集的**第 6 个键**（前五：`git` / `emit_agents_md` / `disabled_folders` / `disabled_gates` / `model_invocable`）。schema 表（含**描述文字**）/ 模板 / 协议列举 / folder-semantics 需同步（见落地清单）。

### 默认与缺失安全（fallback）

- **无 `rules.md`**：两键视同空 —— status 仅可手动调用，且只执行核心两跳；而核心两跳只在模型自调时才自动，手动调用本就由用户显式驱动，故**无 rules.md ≈ 不自动发生任何事**，符合安全默认。Step 0 gate 描述须含"**rules 文件不存在 → 假设两键均为空**"。
- 写了 rules.md 但缺这两个键：同样视同 `[]`。
- 开箱（含旧项目升级）**所有现存项目行为不变**。

---

## 与 landing 的关系（互补 + 单一 land 例程，单一真相）

互补，不重复：

- `status` 在**中途**把状态保持新鲜；landing 的 step 3a 退化成**末尾兜底安全网**（状态多半已新鲜 → 近 no-op）。
- **land 例程 —— 一份实现、一个真相、两个调用方**（review 共识，硬契约）：

  > **The land procedure has a single implementation and a single source of truth. `status` and `landing` are merely two invocation paths.**
  > ✅ `status` MUST call the same land routine used by `landing`.　❌ NOT "status performs landing".

  落地时**把 land 过程从 landing/exit-ritual 抽成一个可被两技能引用的命名锚点/片段**（见落地清单 #2），否则"同一例程"半年后必漂移。

---

## 落地清单（给实现者，soft-config spec 已落地）

1. **新建 `skills/status/SKILL.md`**：
   - 不带 `disable-model-invocation`；**Step 0 `model_invocable` gate**（复用四仪式已落地正文：来源区分 + 手动绕过 + rules 缺失视空）。
   - **artifact 置信规则**（优先级 4 步 + "不确定不翻"原则）写在 description 之后、各触发之前。
   - `description` 用上面的**候选草稿**起步，按平台真实触发表现打磨（成败关键）。
   - 读 `status_auto`：核心两跳无条件；`start` / `land` 按列表 opt-in。
   - forward-only 状态机（含 `pending→awaiting-review` 直跳、sketches 例外、幂等 no-op 边界）。
   - INDEX：单 folder AUTO 区重生 + 重算根该 folder 计数（不做行内 +1/−1）。
   - `done` 自动 / **land 停下确认**；land **调用抽取出的公共 land 例程**；拒绝确认 → 停在 done-but-unlanded。
2. **抽取公共 land 例程（DRY 真相）**：把"移入 `landed/` 镜像、删 folder INDEX 行、改根计数、提示 commit"从 landing/`skills/preflight/exit-ritual.md` 抽成单一命名锚点（如 `exit-ritual.md` 内 `## Land Routine` 锚点，或独立 `skills/preflight/_land-artifact.md` 片段），landing 与 status **都引用它**。spec/SKILL 里写死该锚点路径，杜绝两份实现。
3. **rules.md 第 6 键 `status_auto`**：
   - `skills/preflight/templates.md § rules.md`：模板加 `status_auto: []` 行；toggle **表加行（含描述文字）**；「闭合 X 键」计数 5→6。
   - `skills/preflight/protocol.md` toggle 列举、`folder-semantics.md` toggle 列举：加 `status_auto`。
   - `scaffolds/full/flightdeck/rules.md`：加 `status_auto: []` + 注释。
   - `model_invocable` 合法值文档补 `status`；`protocol.md` 仪式列举 / scenario-trigger 表加 `status`。
4. **preflight 感知 done-but-unlanded（依赖检查）**：preflight 现有 fallback 已对"`done` 但未 land 的 plan → 提议 land 它"。确认/补齐这条对 **specs 等其它 folder** 同样覆盖；若 status 启用 land 后会产出 done-but-unlanded，preflight 必须能浮出它。这是 preflight 的一处措辞核对/小改，列为 dependency。
5. README / README.zh 增"第 5 仪式 `status`"说明 + 生命周期自动翻转章节（含两层配置示例 + description 触发表）。
6. 跨平台 adapter（gemini / codex / cursor）：同 soft-config，gate 正文共享在 SKILL.md；adapter README 注 `status` 同走 model_invocable 门栓。
7. 安装生效提醒：源仓库改完，用户侧 plugin cache 副本需重装/同步才生效。

---

## 验证

- **门栓（第 1 层）**：rules.md 不设 `status`（或 `model_invocable: []`，或**无 rules.md**）→ 模型自调被 gate 拦、提示手动；手敲 `/flightdeck:status` 不被拦。行为等价改动前。
- **artifact 置信**：上下文同时有 spec A + plan B、指代不唯一 → **不自动翻**（不翻错对象）。
- **核心两跳（无条件）**，设 `model_invocable: [status]`、`status_auto` 缺省或 `[]`：
  - 往 `flightdeck/specs` 写新 spec → 自动 `pending`（sketches → `active`）+ 该 folder INDEX 区重生 + 根计数重算，无需确认。
  - 活完成、准备 commit → 自动 `awaiting-review`（含 `pending→awaiting-review` 直跳），无需确认。
  - 开始执行其 plan → **不**自动 `active`（`start` 未开）。
  - 用户说 approved → **`done` 和 land 均不触发**，artifact 停在 `awaiting-review`，留给 landing（措辞统一，避免"只是 land 没动"的歧义）。
- **`status_auto: [start]`**：开始执行 plan → 自动 `active`。
- **`status_auto: [land]`**：
  - 用户 approved → **自动 `set done`**（无需确认）→ **停下问 land 确认**。
  - 确认 → 走**公共 land 例程**移 `landed/` + INDEX/根计数。
  - **拒绝 land → 停在 `done` 但未归档**，状态**不**回退；preflight 后续浮出并提议 land。
- **幂等**：已是 `awaiting-review`/`done` 再触发更早目标 → no-op，**不降级、不报错**。
- 触发后 cockpit `Last updated` **未**被 bump。
- 跨平台：逐 adapter 确认 `status` 经 model_invocable 门栓生效。
