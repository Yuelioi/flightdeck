---
status: pending
---

# 新增第 5 仪式 `flightdeck:status` —— 状态生命周期自动翻转

**日期**：2026-06-02
**来源**：YHFish 用户实战诉求 —— "很多 spec 做完了状态还挂 awaiting-review；正常不是该在任务开始/执行/结束自动更新状态吗？skill 应该加生命周期自动化。"
**状态**：设计定稿（双层配置 + GPT review 三处措辞修正已并入），待实现。
**依赖**：[soft-config-model-invocation](2026-06-02-soft-config-model-invocation-design.md)（**已落地** 2026-06-02：`model_invocable` 软门栓替换 `disable-model-invocation` 硬开关）。

> **定稿记录（2026-06-02）**：经一轮设计对话 + GPT review，三个争议点已拍：
> 1. `done`+land **支持**，但下放成 rules.md 软配置；
> 2. `start→active` **也**软配置，不写死；
> 3. 配置形态 = opt-in list（`status_auto: []`，核心转换始终自动）。
> GPT review 三处措辞修正（`status_auto` 语义 / done 与 land 解耦 / land 例程 DRY）已并入正文。

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

本 skill 直接复用这套：自己**不带** `disable-model-invocation`，自己用 `model_invocable` gate 守住（见下 §配置 第 1 层）。

---

## 方案

### 定位

新增第 5 个仪式 skill：`skills/status/SKILL.md`。它是四仪式之外**唯一"高频、轻量、可自调"**的 skill：

- **只**改单个 artifact 的 frontmatter `status` + 它在所属 folder INDEX 的那一行（+ 必要时根 INDEX 计数）。`land` 启用时**额外**移文件进 `landed/`（确认门控，见状态机）。
- **不**动 cockpit（状态可见性本就活在 folder INDEX，不在 cockpit——遵循现有协议）、**不** commit、**不**跑 length check / AGENTS.md regen。
- 与 landing 互补，不是替代：见下「与 landing 的关系」。

### 触发契约（`description` 决定平台何时自调）

model-invocable。`description` 编码四个生命周期时机。**核心两跳始终自动；两个争议跳由 `status_auto` 软配置 opt-in**（见 §配置 第 2 层）：

| # | 时机（模型在做什么） | 目标状态 | 类别 | 应用方式 |
|---|---|---|---|---|
| 1 | 往 `flightdeck/{specs,plans,sketches,…}` **写入新 artifact** | `pending`（sketches 例外，见下） | **核心·始终自动** | 静默自动 |
| 2 | 绑定某 plan/spec 的活**完成/验证通过、准备 commit** | `awaiting-review` | **核心·始终自动** | 静默自动 |
| 3 | **开始执行**某 flightdeck plan（进 executing-plans / 开始动手实现该 plan 的活） | 该 artifact `active` | **可选**·`status_auto:[start]` | 启用后静默自动 |
| 4 | review 通过、要收尾 | `done` →（确认后）land 进 `landed/` | **可选**·`status_auto:[land]` | `done` 自动；**land 停下确认** |

- **sketches 例外**：sketches 的合法状态通常只有 `active / scrapped`（见协议），所以 create 时落 `active` 而非 `pending`。
- "绑定哪个 artifact" 靠**模型当前上下文**判定（它知道自己在执行 plan X / 这次 commit 实现的是 spec Y），不解析显式 link。

### 状态机（forward-only）

- 规范推进链：`pending → active → awaiting-review → done`。
- **核心两跳**（create 落定 `pending`、finish 落 `awaiting-review`）**始终静默自动**，不受 `status_auto` 控制。
- **`start → active`**：仅当 `status_auto` 含 `start` 时自动；否则不碰（`active` 不自动设，靠人工 / landing）。
- **`done` 与 land 解耦**（GPT review 修正）。仅当 `status_auto` 含 `land` 时，status 才介入收尾，且分两步：
  1. **`set done`——自动**。"review 通过"是用户已断言的**事实**，`done` 跟着落定，不为它单独要确认。
  2. **`land`（移文件进 `landed/`，镜像源结构如 `specs/foo.md → landed/specs/foo.md`，更新 INDEX/根计数）——破坏性操作，必须停下确认**。
  - **关键**：用户拒绝 land 确认 → artifact **停在 `done` 但未归档**（done-but-unlanded，preflight/landing 后续会拾起来归档），**绝不**因为 land 被拒就把状态退回去不设 `done`。避免"我同意 done、但暂不归档"被系统误解成"那就别 done"的歧义。
  - 文档措辞固定为：**done is automatic; land remains confirmation-gated.**
- **只前进不后退**：目标状态 == 当前 或 比当前更靠后 → **no-op**，绝不静默降级（保证幂等 / 可重复触发安全）。
- `blocked` / `scrapped` 仍是**显式人工**动作，本 skill 不自动碰。

### INDEX 同步

翻完 frontmatter，**同步**更新（复用 landing/walkaround 的"单文件定向更新"逻辑，不做整 folder 重生）：

- 该 folder `INDEX.md` 的 `<!-- AUTO -->` 区里这一行的状态字。
- 若某状态分类计数变了，刷新根 `flightdeck/INDEX.md` 该 folder 的计数。

理由：drift 的**症状**正是 INDEX 过期（preflight/外部读 INDEX 当真相）。状态变了不同步 INDEX，等于没治本。

---

## 配置（两层软门栓，正交，不合并）

两个维度回答**不同**问题，分两个 rules.md 键，**不要合并**：

### 第 1 层：`model_invocable` —— 模型能不能自调 status

复用已落地的 soft-config 机制：

- SKILL.md **不带** `disable-model-invocation`；**Step 0 gate** 读 rules.md：`status` **不在** `model_invocable` 且本次是模型自调 → 立即停，提示「`status` 仅限手动；要允许模型自调，在 rules.md 设 `model_invocable: [status]`」。
- 调用来源区分（"用户敲 /" vs "模型自调"）**沿用 soft-config 定的正式版 / 退化版策略**，不另造。
- 默认 `model_invocable: []` → status 默认不自调（自动翻转的全部价值要靠开它）。要用：`model_invocable: [status]`（可与 landing 等并列）。

### 第 2 层：`status_auto` —— status 被调用后，允许哪些**可选**转换

```yaml
# rules.md
status_auto: []
# no optional transitions enabled
# core transitions (create→pending, finish→awaiting-review) remain automatic
```

- **opt-in list，核心转换始终开**。`create→pending` / `finish→awaiting-review` **不属于** `status_auto`，永远自动。`status_auto: []` 表达的是「不启用任何**可选**转换」，**不是**「只启用可靠转换」（GPT review 修正：避免暗示核心两跳也在这个列表里）。
- 合法成员：
  - `start` → 开启 `start→active`。
  - `land` → 开启 `done`+land 收尾（done 自动 / land 确认门控，见状态机）。
- 例：`status_auto: [start, land]` = 全自动（land 仍逐次确认）。
- **不再细化**：成员只到 `start` / `land` 粒度，**不**引入 `start_after_first_edit` 之类的子开关（GPT review：防 per-transition 子开关蔓延）。

> 这是 rules.md 闭合 toggle 集的**第 6 个键**（前五：`git` / `emit_agents_md` / `disabled_folders` / `disabled_gates` / `model_invocable`）。schema / 模板 / 协议列举需同步（见落地清单）。

### 默认安全

开箱（不写这两个键）：status 不自调（`model_invocable: []`）；即便自调也只跑核心两跳（`status_auto: []`），`start→active` 与 `done`+land 全关。**所有现存项目行为不变**。

---

## 与 landing 的关系（互补 + 单一 land 例程）

互补，不重复：

- `status` 在**中途**把状态保持新鲜；landing 的 step 3a 退化成**末尾兜底安全网**（状态多半已新鲜 → 近 no-op）。
- **land 例程：一份实现，两个调用方（GPT review 契约）**。`status`（启用 `land` 时的中途就地闭环）和 `landing`（批量收尾）**复用同一套 land 过程**——即 exit-ritual 里那段 land 描述。spec 明确写：
  - ✅ **`status` MUST call the same land routine used by `landing`.**
  - ❌ 不是 "`status` performs landing"（各写一份）。
- 理由：防止半年后两条路径漂移（如 landing 维护 `landed/` INDEX、status 漏更某字段）。统一指向 exit-ritual 的 land 描述，单一真相。

---

## 已决定（原"作者额外考虑"6 条，逐条收口）

1. **`start→active` 可靠性最软** → **下放成 `status_auto:[start]`，默认关**。需要的项目自己开；`description` 仅在"明确开始执行某 plan"的节点触发；landing 兜底；forward-only no-op 让误触发无害。实测噪音大可直接从 rules.md 关掉，无需改码。
2. **过度触发 / 噪音** → `description` 限定在"**新建** artifact / **状态语义**变化节点"，非"任何编辑"；forward-only no-op 兜底。**`description` 措辞是成败关键**，实现时重点打磨。
3. **create 的 seam** → 触发点锚定"**写入 flightdeck 工作流文件夹**"这个动作本身，而非"brainstorming 结束"。直接写 `flightdeck/specs` 的项目即时 `pending`；先 `docs/` 后 land 的项目，在 land 入 `flightdeck/` 时落定。两种自洽。
4. **与"完成即 commit"纪律时序** → `finish→awaiting-review` 在**该 commit 前/同步**触发，commit 时状态已新鲜。SKILL.md 点明此时序锚点。
5. **不碰 cockpit** → 状态可见性活在 folder INDEX；本 skill 不 bump cockpit `Last updated`、不加 cockpit 段落（遵守现有协议 red flag）。
6. **`done`+land 归属** → **支持在 status 就地做，但 `status_auto:[land]` opt-in**；done 自动 / land 确认门控；**复用 landing 的同一 land 例程**（见上）。默认不开 = landing 仍是唯一 done+land 入口。

---

## 落地清单（给实现者，soft-config spec 已落地）

1. 新建 `skills/status/SKILL.md`：
   - 不带 `disable-model-invocation`；**Step 0 `model_invocable` gate**（沿用 soft-config 来源区分策略）。
   - `description` 精准编码四触发，限定新建/状态语义节点（见已决定 #2、#3）。
   - 读 `status_auto`：核心两跳无条件跑；`start` / `land` 按列表 opt-in。
   - forward-only 状态机；INDEX 单行同步 + 必要时根计数。
   - `done` 自动 / **land 停下确认**；land **调用 exit-ritual 的同一 land 例程**（不另写），拒绝确认 → 停在 done-but-unlanded。
2. **rules.md 第 6 键 `status_auto`**：
   - `skills/preflight/templates.md § rules.md`：模板加 `status_auto: []` 行 + toggle 表加行 +「闭合 X 键」计数 5→6。
   - `skills/preflight/protocol.md` toggle 列举、`folder-semantics.md` toggle 列举：加 `status_auto`。
   - `scaffolds/full/flightdeck/rules.md`：加 `status_auto: []` + 注释。
   - `model_invocable` 合法值文档补 `status`；`protocol.md` 仪式列举 / scenario-trigger 表加 `status`。
3. README / README.zh 增"第 5 仪式 `status`"说明 + 生命周期自动翻转章节（含两层配置示例）。
4. 跨平台 adapter（gemini / codex / cursor）：同 soft-config，gate 正文共享在 SKILL.md；adapter README 注 `status` 同走 model_invocable 门栓。
5. 安装生效提醒：源仓库改完，用户侧 plugin cache 副本需重装/同步才生效。

---

## 验证

- **门栓（第 1 层）**：rules.md 不设 `status`（或 `model_invocable: []`）→ 模型自调被 gate 拦、提示手动；行为等价改动前。
- **核心两跳（无条件）**，设 `model_invocable: [status]`、`status_auto` 缺省或 `[]`：
  - 往 `flightdeck/specs` 写新 spec → 自动 `pending`（sketches → `active`）+ 该 INDEX 行同步，无需确认。
  - 活完成、准备 commit → 自动 `awaiting-review`，无需确认。
  - 开始执行其 plan → **不**自动 `active`（`start` 未开）。
  - review 通过 → **不**自动 done+land（`land` 未开）；停在 awaiting-review，留给 landing。
- **`status_auto: [start]`**：开始执行 plan → 自动 `active`，无需确认。
- **`status_auto: [land]`**：
  - review 通过 → **自动 `set done`**（无需确认）→ **停下问 land 确认**。
  - 确认 → 移 `landed/` 镜像结构 + INDEX/根计数更新（**走 landing 同一 land 例程**）。
  - **拒绝 land 确认 → artifact 停在 `done` 但未归档**，状态**不**回退；后续 preflight/landing 拾起归档。
- **forward-only**：已是 `awaiting-review` 再触发 →  no-op，**不降级**。
- 触发后 cockpit `Last updated` **未**被 bump。
- 跨平台：逐 adapter 确认 `status` 经 model_invocable 门栓生效。
