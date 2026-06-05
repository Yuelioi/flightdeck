---
status: done
---

# 把仪式入口的「硬禁自调」下放成 rules.md 软门栓 + 软配置面盘点

**日期**：2026-06-02
**来源**：YHFish 用户实战诉求 —— rules.md User Rules 写了「长任务结束自动 landing」，但 `/flightdeck:landing` 带 `disable-model-invocation: true`，模型根本调不进，规则无法兑现。
**状态**：pending（设计已敲定，待在 flightdeck 项目开新对话实现）

---

## 背景 / 动机

四个仪式入口 skill —— `landing` / `preflight` / `walkaround` / `emit-agents-md` —— frontmatter 都带 `disable-model-invocation: true`。语义：只能用户手敲 `/flightdeck:<x>`，模型不能经 Skill 工具自调。作者本意是「这些会改 cockpit/INDEX、甚至 commit，要用户显式拍板」。

**问题**：这是个**全局硬开关**，且与真实诉求冲突 ——

- 有用户在 `rules.md` 写「长任务结束自动 landing」，但硬开关让模型永远调不到 landing，规则成空文。
- 想自调的项目和想手动的项目，**无法各自决定** —— 硬开关一刀切。

**方向**：把这个**加载期硬开关**下放成 **per-project 运行期软门栓**（rules.md），契合 flightdeck 已有的 toggle 哲学（`git` / `emit_agents_md` / `disabled_folders` / `disabled_gates`）。默认保持「需手动」，项目按需 opt-in。

---

## 核心机制（实现者必读，别在误解上造方案）

为什么**不能**纯靠 rules.md、也不能靠 hook 注入解决 —— 两个东西在不同层级：

| | `disable-model-invocation` | `rules.md` |
|---|---|---|
| 是什么 | skill 的**静态 frontmatter** | flightdeck per-project 配置文件 |
| 谁读、何时 | **平台**在**加载 skill 时**读 | **skill 自己**在**执行第一步**读 |
| 作用 | 决定 Skill 工具**暴不暴露**该 skill | skill 跑起来后改它**怎么跑** |

**先有鸡蛋问题**：`disable-model-invocation: true` 挡在最前，模型连 skill 都进不去，**到不了读 rules.md 那一步**。所以：

- 纯 rules.md 开关 → **做不到**（运行期配置管不到加载期 frontmatter）。
- SessionStart hook 注入「本项目允许自调」文本 → **也没用**。hook 注入的是上下文文本，Skill 工具仍拒绝被禁用的 skill。
- **去掉 frontmatter 是模型能自调的唯一前提**，任何注入/配置都替代不了它。

结论：方案必须是**两层配合**——平台层放行（去 frontmatter）+ skill 自己用 rules.md 软门栓守住。

---

## 方案

### 第 1 层：去掉 frontmatter 硬开关（必做）

删掉 `landing` / `preflight` / `walkaround` / `emit-agents-md` 四个 `SKILL.md` 的 `disable-model-invocation: true`。平台层放模型进来。

⚠️ 这是**全局**改动（影响该 skill 在所有项目）。靠第 2 层默认值保证**其它项目行为不变**。

### 第 2 层：rules.md 软门栓（per-project 阀门）

rules.md 新增一个 list 键：

```yaml
model_invocable: []   # 默认 [] = 全部仍需手动 /flightdeck:<x>；
                       # 列进来的仪式才允许模型自调，e.g. [landing]
```

四个仪式的 **Step 0（本来就在读 rules.md）** 各加一道 gate：

> 读 rules.md。若本仪式名**不在** `model_invocable` 里、且本次是**模型自调**（非用户显式 `/` 触发）→ 立即停，报：「`<仪式>` 仅限手动 `/flightdeck:<仪式>`；要允许模型自调，在 rules.md 设 `model_invocable: [<仪式>]`」。在列表里 → 正常跑。

> 实现注意：skill 难以可靠区分「用户敲 /」还是「模型自调」。务实做法 = gate 只在「自调」路径生效。若平台不暴露调用来源，可退化为：**列在 `model_invocable` 才允许进入仪式主体，否则一律提示手动** —— 用户敲 / 时若没开也会被提示，体验略糙但安全。实现时先查平台是否能区分来源（Claude Code / Gemini / Codex 各异），不能区分就用退化版并在 README 注明。

### 默认与安全

- `model_invocable` 默认 `[]` → **现状不变**：去了 frontmatter 但软门栓默认全关，等价于「仍需手动」。
- 纯 opt-in：项目想让模型自调哪个仪式，就把它列进 rules.md。

### 跨平台适配（调研项）

`disable-model-invocation` 是 Claude Code 的字段。flightdeck 还有 `adapters/`、`gemini-extension.json`、`.codex-plugin/`、`.cursor-plugin/`。实现前**逐平台核**各自的「禁模型自调」等价机制（Gemini `activate_skill`、Codex 等），软门栓 gate 写在 skill 正文（跨平台共享），平台层各自去硬开关。

---

## 顺带：软配置面盘点（用户要的「更多软配置」）

借这次把 rules.md 的 toggle 面补齐。候选（**本 spec 只落地 `model_invocable`，其余列为 backlog，按 YAGNI 等真实需求**）：

| 候选键 | 现状（写死在哪） | 建议默认 | 价值 |
|---|---|---|---|
| `model_invocable` | 4×`SKILL.md` frontmatter | `[]` | **本 spec 主项** |
| `cockpit_max_lines` | `80`，散在 landing/exit-ritual/folder-semantics/protocol/templates 多处 | `80` | 大项目想放宽 cockpit 长度 |
| `staleness_days` | `~14`，preflight staleness 检查 | `14` | 低频项目不想被频繁报「cockpit 陈旧」 |
| (扩展) `disabled_gates` | 已有键，已知 `debrief-disposition` / `frontmatter-required` | `[]` | 把更多硬步骤命名成可关 gate |

**明确不下放**：

- **Layout 版本（`1.2`）** —— 这是**协议契约/迁移基线**，不是 per-project 偏好。下放会让不同项目对「什么是合法 deck」产生分歧，破坏迁移检测。保持写死。

> 盘点原则：rules.md 软配置只收**真正因项目而异的偏好/策略**；协议结构性契约（layout、AUTO 区机制、reachability 规则、四 toggle 的语义本身）不进 rules.md。

---

## 未来可选（暂不做，记录理由）

**SessionStart hook 注入 rules.md 到上下文** —— 设想：会话一开始就把开关状态注入，让模型在普通对话轮也知道「本项目允许自调 landing」从而主动择机自调。

**暂不做的理由**（用户实战推翻）：rules.md 本来就是每个仪式 **Step 0 的第一读**，不存在「靠注入省一次读」的空间。唯一边际价值是「**非仪式的普通对话轮**模型也知道开关」，价值很弱，不值当为此引入一个 per-project hook + settings.json 配置负担。等真出现「模型老忘记该自调」的实际痛点再议。

---

## 验证

- 4×`SKILL.md` frontmatter 去掉 `disable-model-invocation` 后，Skill 工具能列出/调用这些 skill（不再报 `disable-model-invocation` 错）。
- rules.md 不设 `model_invocable`（或设 `[]`）→ 模型自调仪式被 gate 拦、提示手动；行为等价于改动前。
- rules.md 设 `model_invocable: [landing]` → 模型可自调 landing；其余三仪式仍被拦。
- `templates.md § rules.md` 的 schema 表 + README 的 toggle 说明同步更新。
- 跨平台：逐 adapter 确认等价开关已去 + 软门栓 gate 生效。

---

## 落地清单（给实现者）

1. 删 4×`skills/<x>/SKILL.md` frontmatter 的 `disable-model-invocation: true`。
2. 4 仪式 Step 0 加 `model_invocable` gate（先查平台能否区分调用来源，定正式版 / 退化版）。
3. `skills/preflight/templates.md § rules.md` schema 表加 `model_invocable` 行；`protocol.md` / `folder-semantics.md` 的 toggle 列举同步。
4. README / README.zh 把「Every command carries `disable-model-invocation: true`」一句改写成新机制说明。
5. 跨平台 adapter 核查（gemini / codex / cursor）。
6. （backlog，按需）`cockpit_max_lines` / `staleness_days` 同法下放。
7. 安装生效提醒：源仓库改完，用户侧的 **plugin cache 副本**需重装/同步才生效（marketplace 安装路径）。
