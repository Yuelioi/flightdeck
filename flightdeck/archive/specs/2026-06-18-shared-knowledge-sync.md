---
status: done
summary: 跨项目共享 checklist/doc 同步：母库唯一真相源、谁新谁赢（比既有 last_updated，无 hash）、文件加一行 synced_from 作血缘+勾选、母库根用 env 引用（$FLIGHTDECK_SHARED_MASTER）避免换机失效、AI 驱动只换共享正文保留 ## 项目覆盖段；MVP 单向不回流、仅 checklist/doc、不迁内容。
last_updated: 2026-06-19
verify: 下次真 vendor 一份共享文件跑 /flightdeck:sync，确认只换共享正文、保 ## 项目覆盖 段、把 last_updated 戳成母库的（--sync-status 已单测；端到端 AI 合并未实证——MVP 未迁内容）
---

# 跨项目共享知识同步（母库为准·谁新谁赢·一行 synced_from）

> 源起 / 完整上下文：`E:\projects\agent\flightdeck-shared-sync-PROPOSAL.md`（YHFish 会话成型的提案）。
> 本 spec 是对该提案 vet 源码 + 头脑风暴后的**收敛版**——比原提案更轻：砍掉 hash 与三态漂移表，改 last_updated 谁新谁赢，字段从三个降到一个。

## 1. 问题

用户多项目都用 flightdeck，其中一批**通用知识**跨项目共用（commit 风格、注释规范、UI/API 风格…）。一对矛盾：

- **不能漂移** —— 通用知识要有**单一真相源**，改一处各项目都能拿到最新，不能 N 份各自跑偏。
- **要 git 可见** —— 每个项目里这些知识得是**真文件、提交进该项目 git**（不能只是指向外部的软链/纯指针，否则 clone 出来看不到、CI 读不到）。

一句话：**「多项目把通用知识总结在一处 → 一句『同步』反哺多项目 → 不漂移 → 还要 git 可见」**。

## 2. 目标 / 非目标

**目标**：一份知识（checklist / doc）在一个**母库**维护，能下发（vendor）进任意项目 deck，下发产物是 git 可见的真文件，且能检测「母库更新了」并再同步。

**非目标（YAGNI 边界）**：
- 不做实时同步 / watch / daemon。同步是**显式触发**。
- 不做版本号 / 语义化版本 / 冲突自动合并 / 内容指纹（hash）。
- 不做双向回流（locally-modified 只报不回流，MVP）。
- 不碰 incidents / plans / specs（项目专属，从不共享）。
- 不迁现有内容（先做机制，`agent\skills\commits.md` / `comments.md` 暂留原地）。

## 3. 设计

核心模式 = **vendoring（带血缘下发）**，但靠 flightdeck 既有字段 + AI 驱动，不靠 hash 计算。

### 3.1 数据模型（字段与约定）

vendored 进来的文件（且仅这些）多一行 frontmatter：

```yaml
synced_from: checklists/commits.md   # 母库相对路径（相对母库根）
```

**`synced_from` 是纯可选字段，deck 里绝大多数文件没有它。** 缺省（无此字段）= 本地原创、不共享，sync 完全无视；**只有从母库 vendored 进来的文件才带它**。由此两条硬约束：`flightdeck_new.py` 不得要求它（正常建工件从不加），`flightdeck_lint.py` 不得因它缺失而报警（`parse_frontmatter` 对缺省字段天然返回 `None`）。**不设 present-but-empty 中间态**——有值=共享、无字段=不共享，不用空串。

带它的文件里，`synced_from` **一箭三雕**：① 血缘、git 可见（提案 §3.2 原本要的「参考路径」）；② sync 靠它找哪些文件要同步；③ **就是项目「我要这份共享文件」的勾选记录**——这点决定选它而非纯路径配对：纯路径配对要么全拉、要么另立清单，反而更重。

- **新鲜度锚点 = 既有 `last_updated` 字段**，不新增。比较两边日期判谁新。**无 hash、无 synced_hash、无 synced_at。**
- **项目专属内容写进正文一个约定标题段 `## 项目覆盖`**（复用全局 CLAUDE.md 播种 portable checklist 时已有的同名约定，**不另起 `## 本项目专属`**，免得两个名字）。sync 永不动这段，也不动 frontmatter。
- 发布面（shipped skill/docs）描述此约定时用**语言中性**措辞（"project-specific additions live under a reserved heading, e.g. `## 项目覆盖` / `## Project-specific`"）；用户 deck 内的实际标题随用户语言。

### 3.2 同步动作 `/flightdeck:sync`（AI 驱动）

扫消费 deck 所有带 `synced_from` 的文件，逐个读母库源 + 项目副本，比 `last_updated`：

| 情形 | 判定 | 动作 |
|---|---|---|
| 母库 `last_updated` > 项目 | upstream-changed | AI **刷新「共享正文」段**，保留 `## 项目覆盖` 段 + 整个 frontmatter，把项目 `last_updated` 戳成母库的 |
| 相等 | in-sync | 跳过 |
| 项目 > 母库 | locally-ahead | 跳过 + 报一句「这份比母库新，可能想回流母库」（MVP 不自动回流） |
| 母库源已删 | dangling | 报出来让用户定 |

- **首次下发**：用户说「把母库 commits.md 拉进来」→ AI **整文件拷贝**（frontmatter + 正文）+ 戳 `synced_from`。之后裸跑 `/flightdeck:sync` 即对所有带 `synced_from` 的文件再同步。
- **只换共享正文、不整文件覆盖**：因为 frontmatter 的 `when_to_read`/`applies_to` 是项目本地路由（`index.py` 据此建 INDEX 行），盖掉会破路由、也违反本仓「`applies_to` 须指项目路径」铁律。
- 收尾复用既有 `flightdeck_index.py` regen 受影响 INDEX（不新增 regen 逻辑）。

### 3.3 漂移可见性（walkaround，被动）

walkaround 扫带 `synced_from` 的文件：
- 母库已更新（upstream-changed）→ **INFO**「N 个共享文件可同步——跑 `/flightdeck:sync`」。
- 源已删（dangling）→ **WARN**。

只提示、不自动改。归入 walkaround 现有 AI 审计层即可。

### 3.4 可移植性：母库根用 env 引用（关键，换机器不失效）

会换机器失效的只有**母库绝对路径**；`synced_from` 是相对路径，跟 repo 走、没事。解法 = **绝对路径踢出 git，git 里只留引用，真值放每台机器各自的层**：

- **提交进 git（可移植）**：消费 deck 的 `rules.md` **frontmatter 加一个键**（不在正文另起 `### Shared` 段），**只引用环境变量名、不写真路径**：
  ```yaml
  ---
  version: 3.0
  shared_master: $FLIGHTDECK_SHARED_MASTER
  ---
  ```
  放 frontmatter 而非正文散行：既有 `parse_frontmatter` 直接能读、是结构化 config key、不往 House Rules 散文里掺配置。
- **每台机器各自（不进 git）**：环境变量 `FLIGHTDECK_SHARED_MASTER` = 该机器母库真路径（Win `E:\...\agent\flightdeck`、Mac/Linux `/.../agent/flightdeck` 各设各的），一次性。
- **换新机器流程**：clone repo（得到 `synced_from` + env 引用）→ 设一次 `FLIGHTDECK_SHARED_MASTER` → `/flightdeck:sync` 能解析。
- **AI 侧便利回退（Claude）**：env 未设时，AI 可回退去全局 CLAUDE.md 找母库根（该用户全局 CLAUDE.md 本就把 `E:\projects\agent\` 当跨项目资产库路由）。**发布给别人用的正式机制仍是 env 变量**（工具无关、跨 adapter 通用）；全局 CLAUDE.md 回退只是 Claude 侧便利。

两个由此自然成立、正印证「git 可见真文件」初衷：
1. 哪台机器没有母库（CI、无该私有资产库的协作者）→ env 没设 → sync **优雅 no-op**：「母库未配置/找不到，跳过同步」。
2. 下发文件本身是**自洽真文件**（已提交进 git），没母库照样读/用——sync 只是「需母库在场的可选刷新」，不是文件能否用的前提。

### 3.5 AI 驱动 vs 脚本（落点）

顺项目「事实进脚本、判断留模型」+「AI 全自动驱动」+ 低频：

- **算事实那半进脚本**：`flightdeck_index.py` 加一个**只读 `--sync-status` 扫描**（不是新脚本文件——是现有 index.py 的一个 flag，与 `--verify-pending`/`--changed-since-anchor` 同族）。扫所有带 `synced_from` 的文件，从 rules.md frontmatter `shared_master` 解析母库根 + 展开 env，比两边 `last_updated`，逐行吐 `状态<TAB>项目路径<TAB>母库相对路径`（状态：`upstream-changed` / `in-sync` / `locally-ahead` / `dangling` / `master-missing`）。纯只读、可单测。env 未设 → 吐 `master-missing`，全局 CLAUDE.md 回退留给 AI 那层。
- **判断那半留模型**：`/flightdeck:sync` = **一个新 skill**（与 preflight/landing/walkaround 并列），消费扫描输出，AI 干合并（刷共享正文、保 `## 项目覆盖` 段 + frontmatter、戳 `last_updated`）+ 首次下发。
- INDEX regen 仍复用 `flightdeck_index.py` 既有逻辑（创建/刷新后照常跑）。
- 漂移浮出（`upstream-changed` → INFO「可同步」、`dangling` → WARN）并进 **walkaround** 一条新 audit，消费同一个 `--sync-status` 扫描；`flightdeck_lint.py` 不动。

## 4. 范围（MVP）

- 只服务 **checklist / doc**；incidents/plans/specs 项目专属，不共享。
- **单向**：母库 → 项目；locally-ahead 只报不回流。
- **不迁内容**：先做机制，commits.md / comments.md 暂留原地。

## 5. 接受的代价 / 已知边界（用户已确认接受）

`last_updated` 是「谁记得改的日期」、不是内容指纹，由此：
1. 母库改正文**必须 bump 它的 `last_updated`** 才会传播——flightdeck 的 landing / `new.py` 本就会戳此字段，日常无额外负担。
2. **检测不出「项目偷改本地副本」**——母库一旦更新会**静默覆盖**项目对该文件正文的本地改动（`## 项目覆盖` 段除外，那段永远保留）。符合「母库唯一真相源、项目是消费者、本地不该改共享正文」。
3. `last_updated` 是日期粒度（YYYY-MM-DD）：母库与项目**同日**各改一次会判相等→跳过。低频场景可接受；真撞上由用户手动处理。

## 6. 待定 / 留给 plan

- `/flightdeck:sync` 的具体调用面：裸跑（再同步全部）/ 带母库相对路径（首次下发一份）/ 是否要 `--dry-run` 预览。
- rules.md frontmatter `shared_master` 键的精确命名 + 解析顺序（env → 全局 CLAUDE.md 回退）写进哪个 skill/protocol 文档。
- walkaround 那条 audit 的呈现文案（消费 `--sync-status`；机制已定 = walkaround audit + 只读扫描，不动 `flightdeck_lint.py`）。
- 发布面文档同步范围（README / adapters / TEST_PLAN）——见 incident `outer-ring-docs-drift`。
- 母库形态是否要 flightdeck 定义通用「shared-master deck」约定，还是就认一个 env 指向的 deck（MVP 倾向后者）。
