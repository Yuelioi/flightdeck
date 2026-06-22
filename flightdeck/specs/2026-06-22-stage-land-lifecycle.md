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

### ① stage（自动，每次对话结束；无 soft/full 强度判断、无阈值）

对话一结束，把这次产生的**一切**冲到同一个暂存口（the staging area）：

- **知识** → 总结落盘：**待复核**的标 `status: stale` + `verify:`（复用现状「新产生但未验证」分支），**确信**的直接 `active`（「知识即时可用」哲学不变）。待翻牌不是所有知识的默认态——是否待复核由 AI 在 stage 动作里判定。
- **完成的 plan / task** → 标 `status: done`，但**不下沉 archive**，停在原地（`done` 是「已 stage、囤在阀门前」的**正常常态**，不是待清理的残留）。
- **board 收敛** → Key Context drain、Pending Review 整理一并在此做（不再独属 land）。
- **commit（local）** → 自动发生，带 `Flightdeck-Sync:` trailer（stale-detection 锚）。理由：历史靠 git 追踪、local commit 默认本就自动、撤回无风险、噪音不痛。
- **不做**：archive、push。

「所有东西只能流到这个暂存口，到此为止。」

**执行主体分两半**（沿用现有 checkpoint 的机械/判断分工）：turn-end hook 只焊机械 AUTO 区（`## In Progress`、各 INDEX、新增 `## Staged`）；**知识分类、Key Context drain、commit 这些 judgment 步由 AI 在 stage 动作里做**。所以 stage 去掉的只是「soft 还是 full」这个**强度判断**——**不是「无判断」**：它仍含知识分类与 drain 的判断（与旧 soft-landing 同等、同风险——AI 回合被截断则这半不执行，但这是既有现实，非新模型引入）。

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
| 知识落盘 / 待翻牌 | **复用 `stale` + `verify`，不新增 status**：待复核的落 `stale`+`verify:`，确信的直接 `active` | 现状 `stale` 已含「新产生待复核」语义；land 翻牌 = 现有 `stale →(user-reviewed)→ active`；`verify` 即文件级落点 + 每 preflight 扫描 surface |

## staging area 在 cockpit 的呈现（推荐设计）

痛点「越堆越吵」的解药是**统一囤积口、不散漏**：把「已 stage 未 land」的东西聚到一处可见，而不是散在 cockpit 各字段 + 各 INDEX。

推荐：cockpit 增设一个 **AUTO 派生视图**（类比 `## In Progress` 是 active 投影），名暂定 `## Staged (awaiting land)`，从三类**派生**（非新真相源）：
- `done`-not-archived 的 workflow artifact；
- `stale`-with-`verify` 的知识 artifact（待复核 / 待翻牌）；
- 待 sign-off 项（原 Pending Review 并入）。

派生 = 不增真相源、由脚本 regen。**land 不「清空视图」**——它改的是真相源（archive `done` 文件、把 `stale` 知识翻成 `active`，即 user-reviewed 翻牌），下次 regen 时这些项自然从 `## Staged` 落出，与现在 archive 一个 spec 后它从 `## In Progress` 消失**完全同构**（无任何对视图的写操作）。所以「断了再进来」看到的是一个**整理过的暂存清单**而非散乱 board。

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
- **代价 + 诚实局限：active 区会囤 done，且积压是「集中 + 可见」而非「消除」**。done 不自动归档 → 活跃文件夹累积 done 项；释放（land）频率交给用户，**若用户长期不 land，`## Staged` 仍会增长**——只是从「散在 Pending Review / Key Context / 各 INDEX 的隐性堆积」变成「一个可见的囤积口」。这是**知情接受的取舍**：用户痛点是 soft/full 判断负担 + board 散乱看不住，新模型对前者归零、对后者用统一可见口替代散漏；它**不承诺**强制收敛（用户已否决自动触发 / 阈值）。代价是 land 成低频大操作 → 必须保证 `## Staged` 始终可见 + land 低摩擦，否则积压只是换个地方继续。
- **保留的旧机制**：Land Routine（搬档 + edge 重写）原样复用，只是触发点从「signal 1 自动 / 显式 landing」收窄为「仅显式 land」。knowledge 分类启发式（incidents/docs/...）不变。

## Open questions（plan 阶段敲定的实现细节）

1. `## Staged` 到底是新 AUTO section，还是复用/重命名现有 `## Pending Review` + 让 done 项靠 INDEX 自然显示？（倾向新 AUTO 派生 section，但需确认不撞 80 行 cap——见 Review notes「积压集中后可能成新 cap 压力点」。）
2. ~~待翻牌是否需新 `status`~~ **已决：复用现状 `stale` + `verify`，不新增 status**。stage 时待复核知识落 `stale`+`verify:`（「新产生但未验证」分支），land = 现有 `stale →(user-reviewed)→ active`。留给 plan：把 `stale`-with-`verify` 知识纳入 `## Staged` 视图聚合；明确「确信知识直接 `active` vs 待复核落 `stale`」由 AI 在 stage 动作里判定；确认现状 `verify`-pending 扫描与 `## Staged` 展示不重复 surface（择一或合流）。
3. **signal 体系整体重设计（强依赖，需一起敲定，不是逐条删）**：stage 无条件每回合化 → signal 3「知识增量才 soft-land」的判断**整个消失**；signal 1（done 自动 landing）取消；signal 2 需重新定位（从「入口催 land」→「入口报 staged 量，供用户决定是否开阀门」）。必须给出**替代的 readiness 概念**：land 纯手动后，readiness 退化为「staged 量的被动展示」，而非主动 nudge。
4. 每回合自动 commit 的执行 + 失败路径：commit 由 AI 在 stage 动作里做（judgment-adjacent，hook 只焊 AUTO）。**失败路径已被现有 fallback 兜底**——commit 没做成则知识仍在盘上（preflight 读文件不读 git，不丢）、`Flightdeck-Sync` 锚缺失则 stale-detection 回退 worktree diff（协议已有）；plan 阶段确认这条 fallback 在新模型下仍成立即可。
5. walkaround「异常」的可操作判定（plan）：`staged` 知识与已 archive 的比对键、staging 派生与真相源不一致的具体触发条件（脚本 bug / 手改 INDEX 未 regen），需给出判定规则，否则审计实现不了。

## Review notes

三方外部 AI（ds / claude / gpt，2026-06-22）审了本 spec。他们**不了解项目现状**，仅供参考；raw 文本留 `tmp/{ds,claude,gpt}.txt`，disposition 如下。

**采纳（已改本 spec）：**
- **待翻牌缺文件级落盘表示**（三方共咬）→ 先拟新增 `status: staged`，写 plan 时摸现状发现**现状 `stale`+`verify` 已覆盖**「新产生待复核 →(user 翻牌)→ active」，改为**复用 `stale`+`verify`、不新增 status**（决策表 + Open Q2）。`verify` 即三方要的「文件级落点」，且每 preflight 扫描 surface。
- **「无条件、无判断」措辞过度** → stage section 精确化为「无 soft/full 强度判断」，写明执行主体（hook 焊 AUTO、AI 做分类 / drain / commit）。
- **积压是转移而非消除**（gpt 核心论点）→ Design tradeoffs 补「集中 + 可见、非消除」的诚实局限条。
- **signal 2/3 强依赖、需替代 readiness 模型**（claude / gpt）→ Open Q3 升级为「signal 体系整体重设计」。

**澄清（措辞问题，非缺陷）：**
- `## Staged` 派生 vs「清空」写语义矛盾（ds）→ 已澄清：land 改真相源、视图随之自然收缩，与 `## In Progress` 同构，无对视图的写。
- commit 失败 / 迁移 done 二义（ds）→ 失败有 fallback 兜底（Open Q4）；迁移时旧 `done`-not-archived 统一当 staged、首次 land 清一次即可，无需区分历史语义。

**驳回（源于不了解现状）：**
- 「turn-end 边界不存在」（gpt / claude）→ 现状有 turn-end hook（Claude `Stop` / Codex / Gemini `AfterAgent`）；旧方案否的是 **mid-session** 计数器需 cross-call state，不是 turn-end 不存在。
- 「`## Staged` 与 INDEX done 重复暴露、会不同步」（ds）→ 与现有 `## In Progress`↔INDEX 同构，脚本同源 regen，无两个真相源。
- 「land 语义断裂」（ds）→ 显式 `/flightdeck:landing` 一向是「正式落地」（旧 full-landing），语义连续；新模型只去掉 soft-landing 这个**自动**变体。
