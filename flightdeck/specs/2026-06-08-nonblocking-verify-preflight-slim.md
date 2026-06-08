---
status: active
summary: 验证由阻塞门降为非阻塞标记——复用 stale（拓宽为 待复核：疑似过期 或 新产出未验证），AI 可自断 done(未验证) 照常归档清看板、验证欠债经 cockpit 待验证行在 preflight 浮出、可逆复活；并 preflight 输出瘦身（folder INDEX 仍读只显计数 + docs 载入上下文不刷屏）——兑现随时关不丢上下文
last_updated: 2026-06-08
---

# 验证降为非阻塞标记（复用 stale）+ preflight 瘦身

## 背景 / 要解决的问题

`skills/preflight/exit-ritual.md:246` 的 **needs-verify 门**规定：soft-landing 只能给「纯执行、无需验证」的任务自动翻 `done`；凡是 AI/脚本机械执行、误判不易察觉的（开 PR、部署、改 `protocol.md`/`rules.md`、改 frontmatter/脚本契约……）→ **AI 不许自断 `done`**。

后果（本会话亲历）：`specs/2026-06-07-hook-primary-refactor.md` + 其 rollout plan 卡在「相位4 各家 live 实证」——而 live 实证本会话根本做不了（hook 只在 resync 后新会话触发）。于是两件永远 `active`，堆在 cockpit `## 进行中` 下不来。这直接产生四个问题：

1. **看板堆积一堆「待验证」**（用户：完全没必要，应直接归档）。
2. **docs 加载**：其他项目反映 preflight 没加载 docs；docs 是关键摘要，应进上下文（注：3.0 源码 `skills/preflight/SKILL.md:27` 其实已读 `docs/INDEX.md`，详见 D）。
3. **智能 landing 卡死**：一旦「要验证」就不肯软着陆 → 当次产出无法干净落地 → **违背核心亮点「随时关对话、下次 preflight 干净接手、上下文不丢」**。
4. **preflight 输出太啰嗦**：整张 when_to_read/用途表刷屏，用户只想要「docs N条 / checklist N条」计数。

## 核心原则（为什么这么改）

**验证 = 非阻塞标记，不是落地门。** 安全性不靠「挡住落地」，靠「每次 preflight 把验证欠债浮出来」——**可见性 > 阻塞**，且可逆。

这条恰恰是 flightdeck 自己 3.0 的「**可逆=自动 / 外发=先问**」原则。needs-verify 门的理由（`exit-ritual.md:251`）写的就是「误判很便宜——`done` 只是一个 frontmatter 字段，用户能翻回来」；而归档进 `archive/` 同样可逆（`mv` 回来即可，文件没删）。既然「翻 done」可逆到可以自动，「归档」也可逆，那么「未验证就死锁在 active」反而自相矛盾。本 spec 消除这个矛盾。

## 设计

### A. 验证降为非阻塞标记（复用 stale）— 解 ①③

**改 needs-verify 门**（`exit-ritual.md:244–251`）：AI **可以**自断 `done`，但对 needs-verify 的活打上「未验证」标记，而不是拒绝落地。

**「未验证」复用现有 `stale`，不新增状态、不迁移**：
- `stale` 的 status token 不变（知识三态仍是 `active / stale / obsolete`）。只**拓宽含义**：
  - 旧：`stale` = 疑似过期·待复核。
  - 新：`stale` = **待复核：疑似过期 _或_ 新产出未验证**。两者机制本就同构——非阻塞、可逆、不预先问、浮出待人复核。
- **知识件（checklist / docs / incident）**：本会话新产出但没实证过 → 落 `status: stale`（而非 `active`），留在原文件夹（仍进 catalog、仍可路由），挂「待复核」。验证/复核通过 → 翻回 `active`。
- **工作流件（specs / plans）**：状态集**仍是 `idea / active / done`**（不破 model-v4 三态）。substantively 完成即可 `done`，照常按 `--archivable` 归档、**清空 `## 进行中`**。要验证的事**不是一个状态**、而是一条**下一步动作**，由 B 的 cockpit「待验证」行承载（而非给工作流加第 4 个状态）。

**判定行**（保持可审计）：
- needs-verify → `[判定: <理由>; 待验证: <怎么验>; done(未验证)]`
- no-verify → `[判定: <理由>; 无需验证; done]`（不变）

> 不对称是**有原则的**：知识件是参考材料 → 留在文件夹、`status: stale` 个体可寻、随时复核；工作流件是任务 → 工件归档、把「去验证 X」留成 cockpit 待办。

### B. preflight 浮出「待验证」— 兑现「随时关不丢上下文」

**复用现有 stale→cockpit「待复核」浮出口**（`skills/landing/SKILL.md:39` 的 3c：stale 渲染为 `⚠ 待复核: <file>`，落在 `## 下一步` 下或 `## 待复核` 小节）。**不新增 cockpit section**。

- 工作流 `done(未验证)` 的验证欠债，写进**这同一个待复核/待验证行**，例如：
  `待验证: archive/specs/2026-06-07-hook-primary-refactor.md — 相位4 各家 live 实证`
- preflight 本就在 step 2 读 cockpit（含 `## 关键上下文`）；它读到这条 → 下次进场即接手验证。
- 验证失败 → 从 `archive/` 复活：沿用现成的「回归复活」机械（`mv` 回原文件夹 + 翻状态），不新造路径。

### C. preflight 输出瘦身 — 解 ④

**把「读」和「展示」拆开**（`skills/preflight/SKILL.md:25–31` 的 catalog warm-up + 输出格式）：
- **照旧读** folder INDEX 进上下文（路由 priming 不变，避免 AI 进场不知有啥）；
- **但用户可见输出只给计数**：`docs N · checklist N · incident N`，**不再回显整张 when_to_read / 用途 / applies_to 表**；
- when_to_read 在**任务命中触发时按需再读**（exit-ritual 本就这么规定，execution-time 读单文件）。
- preflight 输出保留：cockpit 对账行 + git/version 一行注（step 4，已是非阻塞）+ **「待验证」清单**（来自 B）+ next item。

### D. docs 加载/展示拆分 — 解 ②

- docs **保持载入上下文**（3.0 `SKILL.md:27` 已读 `docs/INDEX.md` 顶层，满足「关键摘要应加载」），但**展示归 C 只给计数**（`docs N条`），逐条用途 / 正文按需读。
- 「其他项目说没加载」无法从本仓库远程核查；设计上 3.0 已读 docs/INDEX。**待用户指明是哪个项目再单独排**——大概率是那 deck 没有 `docs/` 文件夹、或插件缓存未 resync 到 3.0。本 spec 不把它当代码缺陷处理，除非排查后确有 bug。

## 影响的文件（粗粒度；逐文件改动留给 plan）

- `skills/preflight/exit-ritual.md` — needs-verify 门重写（A）；待验证浮出口扩用（B）。
- `skills/preflight/protocol.md` — `done` 语义补「needs-verify 可自断为 done(未验证)」；`stale` 含义拓宽；落「验证非阻塞」原则。
- `skills/preflight/templates.md` — `stale` 定义文案（待复核 = 过期 _或_ 未验证）；cockpit 模板的「待复核/待验证」行说明。
- `skills/landing/SKILL.md` — 3a/3c 串起 `done(未验证)` + 待验证行；明确 soft-landing 不再被「要验证」挡住。
- `skills/status/SKILL.md` — `done` 翻转允许「未验证」分支与判定行。
- `skills/preflight/SKILL.md` — 输出瘦身（C）；docs 计数（D）；待验证清单。
- `scripts/flightdeck_index.py`（+ `scripts/tests/`） — 待确认：待验证行渲染 / stale 计数是否需脚本支持（plan 阶段定；能纯文案就纯文案）。
- **首个适用对象** = cockpit 现存的 hook spec+plan：本 spec 落地后，它俩 `done(未验证)` + 归档，`## 进行中` 清空，preflight 浮出「待验证: 相位4 各家 live 实证」。

## 不做 / 边界（YAGNI）

- **不**新增第 4 个工作流状态（保 `idea/active/done`）。
- **不**另造新的 cockpit 概念/section——验证欠债走 3c **既有**的「待复核」浮出（`## 下一步` 行内，或 3c 已允许的 `## 待复核` 小节），不发明新结构。
- **不**改 `stale` 的 status token、**不**触发迁移（仅拓宽含义，纯文案）。
- **不**动「外发先问」：deploy / 开 PR / 发邮件 **该不该由 AI 去做**是另一层（不变）；本 spec 只管「做完但没亲验」的**标记与落地**，不放宽 AI 去执行外发动作的权限。
- **不** eager-load docs 正文（仍按需）。

## 验收

- hook spec+plan 不必等相位4，即可 `done(未验证)` + 归档；`## 进行中` 清空；preflight 浮出 `待验证: … 相位4 各家 live 实证`。
- preflight 用户可见输出 = 计数 + 对账 + 待验证 + next item，无整张路由表刷屏。
- 新写 checklist/doc 未实证 → 落 `stale`；preflight 列「待复核」；验证后翻 `active`。
- 「随时关对话」可在任意点落地：当次产出（知识 stale / 工作流 done未验证）全部持久化 + 浮出，下次 preflight 干净接手。

> **自指注脚**：本 spec 的实现本身就是「改了治理文案、需 resync 后新会话 live 实证」的典型 needs-verify 活——它会是自己这套「done(未验证) + 待验证浮出」设计的第一个用户。
