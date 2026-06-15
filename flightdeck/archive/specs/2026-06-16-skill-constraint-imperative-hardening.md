---
status: done
verify: 下次任一新会话走 /flightdeck:new，确认 AI 直接建壳→写正文、无「先参考 INDEX/旧 spec」前戏（红旗护栏行为效力）
summary: Skill 约束措辞硬化：一条原则——硬约束用强命令式大写 MUST/NEVER/DO NOT。① new/SKILL.md 加红旗式反模式块拦「调 new 前预读兄弟 spec/INDEX 对格式」（已观察 3+ 次，用户嫌不专业）+ _shared/bootstrap.md 一行通则覆盖同类权威 skill；② 把 5 处核心安全不变量（emit 保留手写区/walkaround 只审不修/preflight 零写入/status 不擅自弃稿/launch 不探仓）从软措辞升强命令式。代码库本已大量用强词，只补这几处载荷重却软的。
last_updated: 2026-06-16
---

# Skill constraint hardening: strong-imperative register + no pre-read red-flag

> 3.0 alpha 打磨。**已启动。**

> **一条贯穿原则**：flightdeck skill 里的硬约束/护栏/反模式，一律用**强命令式 + 大写否定**（`MUST` / `NEVER` / `DO NOT`），不用软叙述。依据：强命令 + 显式否定显著提升指令遵从（本生态 `using-superpowers` 全程如此）；软叙述拦不住行为反射。本 spec 既**新增**一处护栏（pre-read 红旗，组件 A/B），又**硬化**已有的若干软措辞核心不变量（组件 C）。

## 背景 / 动机

用户已**三次以上**观察到：AI 在调用 `/flightdeck:new`（及同类权威 authoring skill）之前，先去 Read `specs/INDEX.md` 或翻已归档的旧 spec，理由是「参考写法 / 对格式」。用户明确反感：**「显得很不专业」**。

这正是 `/flightdeck:new` 要消灭的手工推导。skill 已自陈是「artifact 形状的唯一权威」——frontmatter、命名、放哪个文件夹、自动 regen INDEX/cockpit 全由脚本盖戳。调它前还去「对格式」是纯多余仪式，既费 token/轮次，又向用户暴露了「这工具好像得手工对齐」的错误印象。

**根因**：`new/SKILL.md` 写了「use this instead of hand-deriving location/frontmatter/naming」，但**没有一条显式反模式禁止「预读兄弟 artifact 对格式/对风格」这个反射**。AI 的通用训练习惯（「创建前先看现有例子」）就钻这个空子。光靠正向叙述（「用这个就行」）拦不住——本生态已验证：**红旗式自检表（Red Flags）才拦得住理性化借口**（见 `using-superpowers` skill 的 Red Flags 表）。

## 决策（已拍板 — 新增护栏 A/B + 硬化已有不变量 C）

### 组件 A — `new/SKILL.md` 加红旗式反模式块（新增护栏，主修）

在 `skills/new/SKILL.md` 显眼位置（顶部 intro 之后）加一个 **Don't / Red Flags** 块，照搬 using-superpowers 的「念头 → 现实」两列表写法，把预读反射标成 STOP 信号。至少覆盖：

| 念头 | 现实 |
|---|---|
| 「先看看别的 spec 怎么写的」 | 脚本盖戳 frontmatter/命名/位置——你只供 body。预读=多余仪式。 |
| 「读下 INDEX 对齐格式」 | INDEX 由脚本 regen，不用你手对。 |
| 「翻归档 spec 学 house style」 | body 散文风格随手写即可；没有需要预先对齐的固定模板。 |

**唯一合法的预读**要写明并保留：
- 你要编码进 body 的**内容**（通常已在手——来自 brainstorming / 当前任务）。
- **incident 去重**：建 incident 前 grep 错误文本 / `--match-signature` 查是否已有同签名（这是 incident 契约已要求的，不在禁止之列）。

**措辞要求（硬性）**：红旗块与下方组件 B 的通则一律用**强命令式 + 大写否定**——`MUST` / `NEVER` / `DO NOT`，不用软叙述（"prefer not to" / "try to avoid" 拦不住行为反射）。落地面 `new/SKILL.md` / `_shared/bootstrap.md` 是**发布面=英文**，故直接用英文大写命令式（与 `using-superpowers` 的 `ABSOLUTELY MUST` / `You MUST` / `DO NOT` 同register）。依据：强命令 + 显式否定显著提升指令遵从——本 spec 的核心论点正是「软叙述无效，红旗 + 硬命令才拦得住」。

### 组件 B — `_shared/bootstrap.md` 加一行通则（覆盖同类）

在 `skills/_shared/bootstrap.md` 加一行通则，把约束从「仅 new」抬到「任何权威 skill」。同样用强命令式（英文发布面），意译如：

> **When a skill OWNS a shape or ritual, DO NOT re-derive it.** When a skill declares itself the authority for a product shape or flow (`new` for artifact shape, `landing` for the landing ritual, `status` for status transitions), you MUST NOT pre-read sibling files to "match format / learn style / verify naming" before invoking it — that is exactly what the skill does for you. Supply only the input it asks for.

这样 `landing` / `status` 等若出现同类反射也被一句话兜住，无需每个 skill 各写一遍。

### 组件 C — 硬化 5 处软措辞的核心安全不变量（措辞硬化）

审计全部 skill 后的结论：**代码库已大量用强命令式**（`DO NOT WRITE` 写门、`NEVER push without asking`、`status MUST NOT perform an automatic transition` 等都在用）。只有少数**载荷重、尤其不可逆/数据丢失**的核心不变量仍用软措辞，升级这 5 处即可。**不**把满篇小写 `never/don't` 全大写——滥用稀释 caps。发布面=英文，直接英文大写命令式。

**Tier 1（不可逆/数据丢失/核心契约）：**

1. **`emit-agents-md` Don't-do** —— `Don't read or modify content OUTSIDE the fenced markers` → `NEVER read or modify content outside the markers — your edits would clobber the user's hand-authored AGENTS.md`。理由：会覆盖用户手写内容（数据丢失）；同文件 Step 2 已是 `MUST be preserved verbatim`，Don't-do 须对齐强度。
2. **`walkaround`** —— `Don't auto-fix` → `walkaround MUST NOT modify any file. NEVER auto-fix.`。理由：walkaround 写文件即破坏「只审不修」只读审计契约（核心不变量）。
3. **`preflight` Step 5 + Don't-do** —— `Do not...start execution` / `Don't create a deck` 等 → 把零写入抬成 `preflight MUST NOT write anything — all writes belong to landing/walkaround`，执行/建 deck 的禁止用 `MUST NOT` / `NEVER`。理由：read-only 零写入是 preflight 整个契约。

**Tier 2（已有近义强词兜底，顺手统一）：**

4. **`status` Step 4** —— 小写 `the AI must not unilaterally abandon work` → `the AI MUST NOT unilaterally abandon work`（对齐旁边已加粗的 `Never delete...without explicit user instruction`）。
5. **`launch`** —— 加粗 `Do not inspect the repo` → `MUST NOT inspect the repo`（determinism 不变量）。

**不动**（已够强）：`exit-ritual` 的 `DO NOT WRITE` / `NEVER push`、`new` 的 `Never auto-append -design`、`status MUST NOT perform an automatic transition` 等。

## 非目标（YAGNI）

- **不**提升为 protocol 级全局原则 / 不在每个 skill 各复制一份红旗表——一处红旗（new）+ 一行通则（bootstrap）足够；过度铺面违反精简哲学。
- **不**加任何脚本层强制（如 hook 拦截 Read）——这是 AI 行为纪律问题，靠显式反模式自检解决，不值得机制成本。
- **不**把全库小写 `never/don't` 一律大写——只升级组件 C 列的 5 处载荷重不变量，避免稀释 caps。
- 不改任何 skill 的实际功能/契约——只硬化措辞 + 补 pre-read 护栏。

## 落地面

- `skills/new/SKILL.md` —— 组件 A 红旗反模式块。
- `skills/_shared/bootstrap.md` —— 组件 B 一行通则。
- `skills/emit-agents-md/SKILL.md` —— 组件 C.1。
- `skills/walkaround/SKILL.md` —— 组件 C.2。
- `skills/preflight/SKILL.md` —— 组件 C.3。
- `skills/status/SKILL.md` —— 组件 C.4。
- `skills/launch/SKILL.md` —— 组件 C.5。

## 验证

- 读改后的 `new/SKILL.md`：红旗块在 intro 后、合法预读例外（含 incident 去重）写明。
- 读改后的 5 个组件 C 文件：每处核心不变量已用 `MUST`/`NEVER`/`DO NOT`；未殃及无关小写 never/don't。
- 行为验证：下次任一新会话走 `/flightdeck:new`，应直接建壳→写正文，无「让我先参考 INDEX/旧 spec」前戏。
- 记忆 `dont-preread-siblings-with-authoritative-skill` + `constraints-use-strong-imperatives` 已存（feedback 类，cross-session 兜底）。
