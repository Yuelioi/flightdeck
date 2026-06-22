---
status: active
summary: Two-phase lifecycle replacing the checkpoint/soft-landing/full-landing split: stage (auto every turn-end -- knowledge persisted as pending-review, done marked but not archived, board converged, auto local commit) and land (manual valve -- archive + flip pending-review knowledge live; push still asks).
last_updated: 2026-06-22
graduate: true
---

# Stage/land lifecycle -- replace the soft/full-landing split

## 动机（要解决的痛）

当前生命周期是三层包含：`checkpoint ⊂ soft-landing ⊂ full-landing`。两个真问题：

1. **soft vs full 的二分本身是罪魁祸首。** 它俩被框成「同一件事的轻重版」（轻 land / 重 land），所以每个回合收尾都要判「这算 soft 还是 full」——判断负担 + 困惑。
2. **board 收敛只挂在 full-landing。** Key Context 的 drain/graduate、Pending Review 老化逐条提示、active 线程整理，协议明文「runs at landing ... not at the mechanical checkpoint」。于是纯 soft-land 流里 **board 只进不出**：active spec/plan、Pending Review、Key Context 一路累加没人 drain → 「越堆越吵」；中途断了再进来面对的是一堆没整理的 board → 主观「怕丢」（其实知识每回合已落盘、文件在盘上不丢，丢的是「整理」）。

三个被否的修补方向（留痕，避免重走）：
- **超阈值自动 landing**：计数器需跨 turn 持久状态，flightdeck 刻意不存（无 startup hook / 无 turn-id）。
- **turn-end 复用 `git status` changed-file 数当 watermark**：信噪比太低——cockpit 每 checkpoint 改、各 INDEX AUTO 区每回合被 hook regen、plan `## Progress` 每 task 动，再加日常改 plan/加 spec，`flightdeck/` 下轻松 ≥5 changed files 全是正常 churn，nudge 每回合亮 = 狼来了。（这也解释了原 signal 2 为何只在入口、once per entry：它隐含依赖「入口那刻的 changed count 反映跨 session 真积压」。）
- **cockpit 加新字段放积压任务**：积压的「任务」已有家（plan `## Progress` + cockpit `## In Progress`），新字段是重复存储 + 撞 80 行 cap / de-scope 红线。

## 模型：stage + land（两段，性质不同，不再是轻重之分）

取消 `checkpoint` / `soft-landing` / `full-landing` 三层，换成**暂存 vs 提交**两段：

### ① stage（自动，每次对话结束，无条件、无阈值、无判断）

对话一结束，把这次产生的**一切**冲到同一个暂存口（the staging area）：

- **知识** → 总结落盘，进「**待翻牌**」（pending review，未经用户确认生效）。
- **完成的 plan / task** → 标 `status: done`，但**不下沉 archive**，停在原地（`done` 是「已 stage、囤在阀门前」的**正常常态**，不是待清理的残留）。
- **board 收敛** → Key Context drain、Pending Review 整理一并在此做（不再独属 land）。
- **commit（local）** → 自动发生，带 `Flightdeck-Sync:` trailer（stale-detection 锚）。理由：历史靠 git 追踪、local commit 默认本就自动、撤回无风险、噪音不痛。
- **不做**：archive、push。

「所有东西只能流到这个暂存口，到此为止。」stage 没有「轻/重」之分——它是对话结束的**固定动作**，消除「我该 soft 还是 full」的判断。

### ② land（手动，阀门 = `/flightdeck:landing`）

只有用户主动开阀门，暂存口的东西才真正「排出去」：

- **done 下沉 archive**（Land Routine：move + rewrite relation edges + 删 INDEX 行）。
- **待翻牌知识翻牌生效**（sign-off）。
- **push**：仍手动 ask（rules.md 红线不变）。

land 保留 `/flightdeck:landing` 命令名，语义收窄为「真正落地归档」。

### 命名（发布面英文）

- 下放 = **stage**（动词/名词；the staging area = 暂存口）。
- 开阀门 = **land**（保留 `/flightdeck:landing`）。
- 待确认知识沿用 **pending review**。
- `stage` ↔ `land` 直觉即「暂存 → 落地」，且 staging 是软件界熟词（git staging area），零歧义。

## 关键决策（已与用户敲定）

| 决策 | 取值 | 理由 |
|---|---|---|
| commit 归属 | **stage 侧，每回合自动** | git 追踪历史、默认自动、撤回无风险、不痛；从「区分 soft/full 的标志」降级成 stage 的一部分，反帮消除二分 |
| push 归属 | 仍手动 ask | rules.md 红线不变 |
| archive 归属 | **land 侧（阀门）** | archive 是「真正从活跃区移走」，要用户确认 |
| `done` flip | **不再自动 archive**（取消 signal 1 自动 landing） | done 是 staged 常态，囤在阀门前 |
| 知识落盘 | stage 时即落盘，进 pending review | 不丢；翻牌（生效确认）留给 land |

## staging area 在 cockpit 的呈现（推荐设计）

痛点「越堆越吵」的解药是**统一囤积口、不散漏**：把「已 stage 未 land」的东西聚到一处可见，而不是散在 cockpit 各字段 + 各 INDEX。

推荐：cockpit 增设一个 **AUTO 派生视图**（类比 `## In Progress` 是 active 投影），名暂定 `## Staged (awaiting land)`，从三类**派生**（非新真相源）：
- `done`-not-archived 的 workflow artifact；
- pending-review 的知识 artifact；
- 待 sign-off 项（原 Pending Review 并入）。

派生 = 不增真相源、可由脚本 regen、可随 land 自动清空。这样 cockpit 行数不因囤积无限涨（land 一次清一次），且「断了再进来」看到的是一个**整理过的暂存清单**而非散乱 board。

## 受影响的协议面（清单，逐行改法留给 plan）

- `skills/preflight/exit-ritual.md`：三层模型 → stage/land 两段；signal 1/2/3 体系重构；accumulator-drain 从「仅 landing」下放到 stage；soft-landing banner → stage banner。
- `skills/preflight/protocol.md`：Act-report-close loop、Land-readiness、status⟂location、Land Routine 触发时机。
- `skills/landing/SKILL.md`：landing = 阀门（archive + 翻牌），砍掉 commit（移到 stage）；Modes 段重写。
- `skills/status/SKILL.md`：`done` flip 不再触发自动 landing。
- `skills/walkaround/SKILL.md`：**done-but-unlanded 语义翻转**——从「异常，催 land」→「阀门前正常囤积，不催」（见下）。
- `skills/preflight/SKILL.md`：入口 land-readiness 报告语义随之变。
- cockpit 模板（`scaffolds/full`）+ `scripts/flightdeck_index.*`：新 `## Staged` AUTO 投影。
- `templates.md`：cockpit 字段说明。

## walkaround 语义翻转

现状 walkaround 把 `done`-but-unlanded 当 INFO「提醒你去 land」。新模型下 `done`-not-archived 是 stage 的**正常输出**，不该催。翻转为：walkaround 只在 staging area **异常**时报（如 pending-review 知识与已 archive 矛盾、staging 派生与真相源不一致），不再把「done 没归档」当债。

## 迁移（现有 deck）

本仓即首个 dogfood 对象。现有 deck 无 `## Staged` section、可能有 done-but-unlanded 残留——首次按新模型 stage 时由脚本补 section + 聚合。无需向后兼容分支（de-scope 红线：不引入兼容/迁移机制层）；旧 deck 跑新脚本即自然补齐，旧 `soft-landing`/`full-landing` 术语在散文里一次性替换。

## Design tradeoffs

- **为何 stage/land 优于 soft/full**：soft/full 是「同一动作的两个强度」，强迫每回合选强度；stage/land 是「两个不同性质的阶段」（暂存 vs 提交），对话结束**永远** stage、提交**永远**手动 land——判断负担归零。
- **代价：commit 变多**。每回合自动 commit → git 历史更碎。用户已明确接受（撤回无风险、不痛、要 git 追踪）。`Flightdeck-Sync` trailer 仍只认最新，stale-detection 不受影响。
- **代价：active 区会囤 done**。done 不自动归档 → 活跃文件夹累积 done 项。由 `## Staged` 视图聚合可见 + land 一次清空兜住；walkaround 不再视为债。
- **保留的旧机制**：Land Routine（搬档 + edge 重写）原样复用，只是触发点从「signal 1 自动 / 显式 landing」收窄为「仅显式 land」。knowledge 分类启发式（incidents/docs/...）不变。

## Open questions（plan 阶段敲定的实现细节）

1. `## Staged` 到底是新 AUTO section，还是复用/重命名现有 `## Pending Review` + 让 done 项靠 INDEX 自然显示？（倾向新 AUTO 派生 section，但需确认不撞 80 行 cap。）
2. 「待翻牌」是否需要知识 artifact 的新 `status` 值（如 `pending`），还是纯靠 cockpit staging 视图 + 现有 `active` 表达？（倾向后者，零新 status。）
3. signal 2 / signal 3 在新模型下保留还是删除？（stage 无条件每回合跑 → signal 3 的「知识增量才 soft-land」判断可能整个消失；signal 2 入口提示是否还需要。）
4. 自动每回合 commit 与现有 turn-end hook（只焊 AUTO 区）的关系——commit 该由 AI 在 stage 动作里做，还是也welded 进 hook？（commit 是 judgment-adjacent，倾向 AI 做。）
