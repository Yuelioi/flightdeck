---
status: pending
---

# 新增第 5 仪式 `flightdeck:status` —— 状态生命周期自动翻转

**日期**：2026-06-02
**来源**：YHFish 用户实战诉求 —— "很多 spec 做完了状态还挂 awaiting-review；正常不是该在任务开始/执行/结束自动更新状态吗？skill 应该加生命周期自动化。"
**状态**：pending（设计已敲定，待在 flightdeck 项目开新对话讨论 + 实现）
**依赖**：[soft-config-model-invocation](2026-06-02-soft-config-model-invocation-design.md)（**必须先落地**，见下「依赖」）

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

## 依赖：先落地 `soft-config-model-invocation`

本 skill 要能**被模型自调**（自动触发是它的全部价值）。但当前四仪式都带 `disable-model-invocation: true`，平台层连 Skill 工具都不暴露它们。`soft-config-model-invocation` spec 已设计好两层机制：

1. **去掉 frontmatter 硬开关**（平台层放行）；
2. **rules.md `model_invocable: []` 软门栓**（per-project opt-in，默认全关 = 现状不变）。

本 skill 直接复用这套：自己**不带** `disable-model-invocation`，自己用 `model_invocable` gate 守住。所以**先实现那个 spec，再实现本 spec**；否则这个 skill 要么平台调不进（带硬开关），要么没 gate 可守（裸奔自调）。

---

## 方案

### 定位

新增第 5 个仪式 skill：`skills/status/SKILL.md`。它是四仪式之外**唯一"高频、轻量、可自调"**的 skill：

- **只**改单个 artifact 的 frontmatter `status` + 它在所属 folder INDEX 的那一行（+ 必要时根 INDEX 计数）。
- **不**动 cockpit（状态可见性本就活在 folder INDEX，不在 cockpit——遵循现有协议）、**不** commit、**不**跑 length check / AGENTS.md regen。
- 与 landing 互补，不是替代：见下「与 landing 的关系」。

### 触发契约（`description` 决定平台何时自调）

model-invocable。`description` 编码三个生命周期时机 + 一个收尾时机：

| # | 时机（模型在做什么） | 目标状态 | 应用方式 |
|---|---|---|---|
| 1 | 往 `flightdeck/{specs,plans,sketches,…}` **写入新 artifact** | `pending`（sketches 例外，见下） | 静默自动 |
| 2 | **开始执行**某 flightdeck plan（进 executing-plans / 开始动手实现该 plan 的活） | 该 artifact `active` | 静默自动 |
| 3 | 绑定某 plan/spec 的活**完成/验证通过、准备 commit** | `awaiting-review` | 静默自动 |
| 4 | review 通过、要收尾 | `done` + land 进 `landed/` | **停下等用户确认** |

- **sketches 例外**：sketches 的合法状态通常只有 `active / scrapped`（见协议），所以 create 时落 `active` 而非 `pending`。
- "绑定哪个 artifact" 靠**模型当前上下文**判定（它知道自己在执行 plan X / 这次 commit 实现的是 spec Y），不解析显式 link。

### 状态机（forward-only）

- 规范推进链：`pending → active → awaiting-review → done`。
- 前三跳（create 落定 / →active / →awaiting-review）**静默自动应用**。
- `done`（伴随移文件进 `landed/`，镜像源结构如 `specs/foo.md → landed/specs/foo.md`）**必须用户确认**——这是有移文件副作用的重操作。
- **只前进不后退**：目标状态 == 当前 或 比当前更靠后 → **no-op**，绝不静默降级（保证幂等 / 可重复触发安全）。
- `blocked` / `scrapped` 仍是**显式人工**动作，本 skill 不自动碰。

### INDEX 同步

翻完 frontmatter，**同步**更新（复用 landing/walkaround 的"单文件定向更新"逻辑，不做整 folder 重生）：

- 该 folder `INDEX.md` 的 `<!-- AUTO -->` 区里这一行的状态字。
- 若某状态分类计数变了，刷新根 `flightdeck/INDEX.md` 该 folder 的计数。

理由：drift 的**症状**正是 INDEX 过期（preflight/外部读 INDEX 当真相）。状态变了不同步 INDEX，等于没治本。

### 门栓（per-project opt-in，复用 soft-config spec 机制）

- SKILL.md **不带** `disable-model-invocation`（前提=soft-config spec 已落地，平台层放行）。
- **Step 0** 读 rules.md：若 `status` **不在** `model_invocable` 且本次是模型自调 → 立即停，报「`status` 仅限手动；要允许模型自调，在 rules.md 设 `model_invocable: [status]`」。在列表里 → 正常跑。
- 调用来源区分难题（"用户敲 /" vs "模型自调"）**与 soft-config spec 同款**，沿用它定的正式版 / 退化版策略，不另造。
- 默认 `model_invocable: []` → 本 skill 默认不自调，**所有现存项目行为不变**。项目想要：`model_invocable: [landing, status]`。

### 与 landing 的关系

互补，不重复：

- `status` 在**中途**把状态保持新鲜；landing 的 step 3a 退化成**末尾兜底安全网**（状态多半已新鲜 → 近 no-op）。
- `done` + land 两边都能做：`status` 让你**中途就地闭环**（确认后），landing 仍是**批量收尾**入口。两者复用同一 land 过程，不重复实现。

---

## 作者的额外考虑（讨论时重点看这几条）

记录我设计时的判断与隐忧，供你那边开对话时拍：

1. **全粒度里三跳的可靠性不均**。`finish → awaiting-review` 最稳，因为"准备 commit"是个**明确动作**，模型几乎一定路过。`create → pending` 次之（写文件也明确）。`start → active` **最软**——"现在算开始执行了吗"是模糊语义，模型不一定每次准确识别（边设计边写边改的活，active 和 pending 边界本就糊）。**结论**：照你的选择三跳全做，但别期待 `start→active` 像 finish 那样滴水不漏；landing 兜底对这跳尤其有用。如果实测 `start→active` 噪音大/经常误触，第一个该砍的就是它。

2. **过度触发 / 噪音风险**。一个 model-invocable 且"写 artifact 就该想到它"的 skill，可能在不必要的小编辑（改个错字、补一句话）时也被平台拉起来。缓解：①`description` 把触发限定在"**新建** artifact / **状态语义**变化的节点"，而非"任何编辑"；②forward-only no-op 让误触发基本无害（已在目标就啥也不干）。实现时 `description` 措辞要精准，这是成败关键。

3. **create 的"seam"问题**。superpowers brainstorming 默认把 spec 写到 `docs/superpowers/specs/`，不是 `flightdeck/specs/`；artifact 往往是 landing classification 时才落进 `flightdeck/<folder>/`。所以**触发点应锚定"写入 flightdeck 工作流文件夹"这个动作本身**（不管是谁、何时写进去的），而不是"brainstorming 结束"。在直接往 flightdeck/specs 写 spec 的项目（如 YHFish），create→pending 即时生效；在先 docs/ 后 land 的项目，create→pending 在 land 入 flightdeck/ 时落定。两种都自洽。

4. **与"完成即 commit"纪律的时序**。很多项目（含 YHFish CLAUDE.md）有"活完成立即 commit"铁律。`finish→awaiting-review` 应在**该 commit 前/同步**触发，让 commit 时状态已新鲜。建议在 SKILL.md 里点明这个时序锚点。

5. **不碰 cockpit `Last updated`**。状态可见性活在 folder INDEX，不在 cockpit；本 skill 不 bump cockpit、不加 cockpit 段落（遵循现有协议 red flag）。

6. **要不要把 `done`+land 完全交给 landing？** 本设计让 `status` 也能在确认后就地 done+land，好处是中途闭环。代价是 land 过程两处都引用（需保证 DRY，统一指向 exit-ritual 的 land 描述）。若觉得 done+land 只该在 landing 一处，可把 #4 砍成"只到 awaiting-review 为止，done 留给 landing"——这是个干净的缩范围选项。

---

## 落地清单（给实现者，假定 soft-config spec 已先落地）

1. 新建 `skills/status/SKILL.md`：不带 `disable-model-invocation`；`description` 精准编码三触发（限定新建/状态语义节点，见考虑 #2）；Step 0 `model_invocable` gate（沿用 soft-config 的来源区分策略）；forward-only 状态机；INDEX 单行同步；`done` 确认 + land（复用 exit-ritual land 过程）。
2. `skills/preflight/templates.md § rules.md` 的 `model_invocable` 合法值补 `status`；`skills/preflight/protocol.md` 的仪式列举 + scenario-trigger 表加 `status`；`folder-semantics.md` 如列举仪式同步。
3. README / README.zh 增"第 5 仪式 `status`"说明 + 生命周期自动翻转章节。
4. 跨平台 adapter（gemini / codex / cursor）：同 soft-config，平台层各自去硬开关 + 共享 gate 正文在 SKILL.md。
5. 安装生效提醒：源仓库改完，用户侧 plugin cache 副本需重装/同步才生效。

---

## 验证

- rules.md 不设 `status`（或 `[]`）→ 模型自调被 gate 拦、提示手动；行为等价改动前。
- 设 `model_invocable: [status]`：
  - 往 `flightdeck/specs` 写新 spec → 自动 `pending`（sketches → `active`）+ 该 INDEX 行同步，无需确认。
  - 开始执行其 plan → 该 plan 自动 `active`，无需确认。
  - 活完成、准备 commit → 自动 `awaiting-review`，无需确认。
  - 标 `done` → **停下问确认** → 确认后移 `landed/` 镜像结构 + INDEX/根计数更新。
- 已是 `awaiting-review` 再触发 → no-op，**不降级**。
- 触发后 cockpit `Last updated` **未**被 bump。
- 跨平台：逐 adapter 确认硬开关已去 + gate 生效。
