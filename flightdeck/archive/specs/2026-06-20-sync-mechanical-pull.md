---
status: done
summary: 把带时间戳的 AI-merge sync 降级为纯机械模型：母库是 shared 内容唯一写者、consumer 不改 shared，flightdeck:project-specific 锚切分 shared/项目段，脚本现算现比内容指纹判过期，进项目时纯脚本懒拉替换 shared 段；日常 sync AI 零参与（成本按活跃项目而非总项目数增长）；删 back-flow，promote 仍 AI 判断
last_updated: 2026-06-20
note: 机械 sync 模型契约已 graduate 进 docs/shared-knowledge-sync.md（就地更新现有 doc，非新建同名 doc）；本 spec 留档备查完整设计 rationale
---

# Sync: mechanical section-single-writer pull

## 1. 动机：两个病灶

现有 shared-knowledge-sync（v2，`docs/shared-knowledge-sync.md`）用 `last_updated` 时间戳做合并键、AI 逐仓 merge。两个病灶：

1. **时间戳做合并键 = last-write-wins，探测不了并发分叉。** 母库 6.18、项目 A 6.19、项目 B 6.20，A/B 各自改了 shared body。谁 push 母库就变谁，另一个 pull 时自己的改动被静默覆盖。时间戳新 ≠ 内容对，只能排序、不能合并。
2. **AI 逐仓 merge = token 黑洞。** fanout 对每个 consumer 跑一次 AI pull；项目越多，token 越烧。而那个 merge 其实是机械的（在边界处切开、换上半截、留下半截）。

判据：**把 sync 彻底降级成机械同步** —— 单写者消除合并、脚本消除 token。项目数增长 = 零 token 增长。

## 2. 模型：分区单写者（section-single-writer）

每个 vendored 文件分两区，各**只有一个写者**：

| 区 | 写者 | 同步方向 |
|---|---|---|
| **shared 段**（边界锚以上） | **母库唯一** | 母库 → consumer（pull，机械覆盖） |
| **`## 项目覆盖` 段**（边界锚以下） | **consumer 唯一** | 永不离开 consumer（永不上推） |

- consumer **永不改 shared 段** → shared 内容不可能分叉 → 合并问题从根上消失。
- 改共享规则 = **去母库改**（如本会话直接编辑 `~/.flightdeck/checklists/commits.md`）。
- 唯一的 consumer→母库 路径 = **promote**（把项目内新写的、够通用的文件升上母库；母库还没有 → 无冲突）。promote 仍 **AI 判断**通用性（显式、低频）。
- **砍掉 back-flow**（在项目里改 shared body 再 push 上去）—— 这正是 v2 的分叉之源。

## 3. 边界锚：机械可切

shared / 项目段的分界用**固定锚注释**：

```
<!-- flightdeck:project-specific -->
```

- 锚**以上** = shared（母库管）；锚**以下** = 项目私有（pull 永不碰）。
- 用固定锚而非匹配本地化标题（`## Project-specific` / `## 项目覆盖`）：标题文字仍可本地化给人看，但脚本切分**语言无关、一刀准**。
- 文件**没有锚** = 纯 shared（整个 body 都是 shared 段，无项目覆盖）。母库文件通常如此。
- frontmatter **不属于任何区**：`when_to_read` / `applies_to` 是 consumer 可本地化的路由，pull 永不碰（沿用 v2 现状）。
- **「锚以上」= 整个 body**（标题 + 导语 + 通用各节），不只是某个 `## 通用` 节。consumer 要项目私货**只能放锚以下**或 frontmatter 路由；导语也不许本地化（会被覆盖）。

**worked example（`commits.md`，回答"有两段是否还要 AI"——不要）：**

```
frontmatter                          ← consumer 可本地化路由（pull 不碰）
# Commits Playbook + 依据             ┐
## 通用 (项目无关)  §1–7              ├─ shared 段（母库 body = 一模一样）
<!-- flightdeck:project-specific -->  ← 固定锚（迁移时插一行）
## 项目覆盖 (本仓库专属)              ← 项目私有（pull 不碰）
```

pull 一刀：`indexOf(锚)` → 锚以上整段用母库 body 覆盖 → 锚以下原样留 → frontmatter 不动。纯文本 splice，**项目覆盖空与否都一样切，AI 一个字不读**。现在"感觉要 AI"只因事实边界是本地化标题 `## 项目覆盖`（匹配脆）；固定锚把"AI 看哪是哪"降成"脚本 `indexOf`"。

## 4. 同步键：现算现比内容指纹（无状态）

**判过期 = 比 shared 段内容,不比时间戳。**

```
shared_fp(text) = fingerprint( normalize( strip_frontmatter(text) 锚以上部分 ) )
in-sync  ⟺  shared_fp(consumer) == shared_fp(master)
```

- **fingerprint** = 复用 `flightdeck_lib` 现成的 `sha1(utf8(x)).slice(0,12)`（incident 签名同一函数，py/js byte-parity 已测）。
- **normalize**（否则平凡差异假报过期）：复用现成 byte-parity 归一 —— 换行 → LF、UTF-8 NFC、行尾空白 + 段末多余空行剥除。
- **无存储状态**：母库本地可读、文件几 KB，进项目时脚本现读现算现比。跟现有 `sync_status` 同风格（只是键从时间戳换成指纹）。
- **时间戳彻底退出 shared 同步**（§1 病灶 1 从根消除）。
- 注：母库本地、比对在脚本层，**AI 不读内容 → 零 token**；现算 vs 存指纹只差"算的时机"，无状态版零维护，选它。

## 5. 传播：进项目懒拉，纯脚本

- 进项目时（见 §6 时机）脚本对该项目的每个 vendored 文件跑一次 `shared_fp` 比对；`stale` 的就用母库 shared 段**机械替换**（切锚、换上半截、留项目段、frontmatter 不动）。
- 成本按**活跃项目**算 —— 一个从不打开的项目就让它陈旧，下次用时自愈。不访问死仓、不烧 token。
- **fanout（母库主动推全部）降级为可选手动** + 同一个纯脚本：需要"现在就推全部已注册 consumer"时再用（复用 `register/list/prune-consumers` 原语）。
- **AI 全程零参与**（日常 pull/fanout 纯脚本）；AI 只在 **promote** 出场。

## 6. 与 zero-write 的调和（关键）

preflight 读路由目录（含 shared 文件）进上下文 → 刷新必须在 preflight 读**之前** → 入口处必有一次"读前的写"。但**不打破 zero-write，而是精确化它**：

> zero-write 真正的意思一直是 **「preflight 不做判断性看板写入」**（不 bump `Updated`、不 regen INDEX、不建 artifact、不翻 status）。一次确定性、无冲突、可报告、可回滚的 vendored 输入刷新**不是那种写** —— 它是"读前先 `git pull`"，由独立机械层干，**与已存在的 turn-end INDEX hook 同范畴**。

守边界三条线：

1. **刷新不是 preflight 的步骤** —— 是 preflight **之前**的独立命名机械动作。preflight checklist 与其「MUST NOT write」原样为真。入口序列 = `[机械刷新] → [只读 preflight]`。
2. **刷新只碰 vendored shared 段 body** —— 绝不碰 cockpit / INDEX / status / artifact。
3. **透明 + 可逆有闸**：git deck 自动 + 报告（git 兜底）；非 git deck 先 **diff 再问**（不可逆，同 conform 的非-git 纪律）。

**逃生口（deck `### Rules`）**：默认 git→进场自动刷新+报告、非 git→检测+问；一条 deck rule 可降级成"只检测、入口永不自动写"，给想要"纯读入口"的用户。机制同现有"`### Rules` 覆盖默认"。

**优化**：刷新也挂一份到 **turn-end hook** —— 热项目每回合末顺手拉、一直新；入口刷新只为**冷重入**兜底（很久没碰、期间母库变了）。

## 7. 整改面

| 落点 | 改动 |
|---|---|
| `flightdeck_index.py` / `.js` | `sync_status` 键 时间戳 → `shared_fp`；新增机械 pull（切锚替换 shared）；保留 `register/list/prune-consumers`、`--fanout` 原语。py/js byte-parity。 |
| `skills/sync/SKILL.md` | 删 back-flow（§C locally-ahead push）；pull/fanout 改"脚本机械、AI 零参与"；promote 保留 AI 判断；新增边界锚约定。 |
| `skills/preflight/*` | 入口加机械刷新前步（git 自动+报 / 非 git diff+问）；精确化 zero-write 表述为"无判断性看板写入"。 |
| 边界锚约定 | `templates.md` / `protocol.md` 记 `<!-- flightdeck:project-specific -->` 与 shared/项目分区语义。 |
| 迁移 | 给现有 vendored 文件（`commits.md` / `comments.md`，本仓 + 母库）插边界锚。 |

## 8. 不变量 / 非目标

- **不变量**：日常 sync AI 零参与（成本按活跃项目算）；shared 内容母库单写、永不分叉；frontmatter 路由 consumer 可本地化、pull 永不碰；非 git deck 刷新不可逆 → 必先 diff+问。
- **非目标**：远程母库 / 网络同步（母库固定 `~/.flightdeck` 本地，escape 用 symlink/junction）；shared 段的双向/对等同步；promote 的自动化（保持显式 AI 判断）。
- **graduate**：本 spec 定义 sync 模型契约（分区单写、边界锚、指纹键），done 后 graduate → 更新 `docs/shared-knowledge-sync.md`（v2 设计现状真相源）。
