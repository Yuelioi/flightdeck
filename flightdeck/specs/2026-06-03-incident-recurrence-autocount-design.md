---
status: active
summary: incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
last_updated: 2026-06-03
---

# Incident 复发计数 auto-count（Approach A）

## Problem

复发计数现在是**手记 prose**（本会话刚加的 `**Recurrences**:` body 头）+ 手动 `[Case N]`。后果：
- **漏计 → 晋级 gate 形同虚设**：here-string 错题的"3 次"是用户嘴报的，系统没追踪前 2 次。gate（≥3 次晋级 checklist）因此从不触发，同一错反复犯。
- **AI 在路由时看不见复发态**：count 埋在 body，preflight catalog 阶段（只读 INDEX，不开文件）无从知道"这条已 2/3、快晋级"。

面向 AI 的系统，计数应当**自动维护 + 结构化可见**，而不是靠人记。

## 非目标（守住 flightdeck 哲学 / 2.0 教训）

- **不加 status 生命周期值**（不要 `watching/gate-ready/promoted`）。status 仍 `active/obsolete/superseded`。"状态机塞进 status"正是 2.0 被废的方向（[[flightdeck-2.0-abandoned]]）。
- **不自动晋级**：晋级仍是 landing 提示 + 用户确认（误判闸门留在最有后果那步）。
- **status 不 gate INDEX**：所有 incident 都进 INDEX（图可达性——不在 INDEX = 对 AI 不存在）。"待晋升"也必须可见。
- **脚本不做判断**：计数=判断（"是不是同一条 incident？"），由 AI 在 landing 决定；脚本只**渲染** count 进 INDEX 行 + 校验，绝不自己 bump。

## 设计（Approach A）

### 1. `recurrences` 提为 frontmatter 字段

incidents frontmatter 新增 `recurrences: <int>`（默认 1）。**取代**本会话加的 `**Recurrences**:` body 头——理由：INDEX 行铁律是只从 frontmatter 生成、不读 body，要上 INDEX 就必须在 frontmatter。`[Case N]` 叙事块保留（每块带日期/上下文，是"≥2 distinct sessions"判据的来源）。

- 计数器 ≠ 状态机：它是个 int，无 transition、无 verb。
- 字段表（protocol canonical）加一行：`recurrences | incidents | optional(默认1) | INDEX gen + 晋级 gate 读 | landing/status auto-bump | walkaround 校验`。

### 2. 上 INDEX 行

`incidents/INDEX.md` 每行追加 `— recur: N`（N>1 时才显，=1 省略以免噪声）。preflight catalog 阶段不开文件即见复发态。`flightdeck_index.py` 的 incident 行生成读 `recurrences` frontmatter 渲染；`--check` 一并验。

### 3. landing「复发扫描」(exit-ritual Step 5a 扩展)

landing 时，对本会话产生的 bug/教训，**主动比对**现有 incidents 的 `applies_to`/root-cause：
- **明确同一条** → AI **自动** append `[Case N]`(带本会话日期) + `recurrences += 1`，**不再逐次问**（满足"应自动记录"）。这把 protocol 现行"Do NOT auto-increment，须用户确认每次"改为"明确匹配自动记，歧义才问"。
- **歧义/拿不准** → 按现状问用户（误判防护前移到模糊态）。

与已有的"Proactive incident resurfacing"(任务**开始**前提示相关 incident)对称：开始前提示、结束后记账。

### 4. 晋级 gate：触发逻辑不变、闸门不变

`recurrences ≥ 3` **且** `[Case N]` 跨 ≥2 distinct 日期(sessions) **且** remediation 稳定 → landing **提示**"晋级到 checklist？"，用户确认。auto-count 让这个 gate **终于会可靠触发**（这才是本 spec 的真正收益），但晋级本身**仍非自动**。

### 5. "待晋升 / 已晋级" = 派生，不是新 status

- **待晋升** = `recurrences ≥ 3` 且尚无 `Promoted:` 标记。
- **已晋级** = 有 `Promoted: → checklists/X` 标记（或 `status: superseded → project-rules`）。
- 两者从 count + 既有标记派生，INDEX 行的 `recur: N` 已让"快到阈值"可见。无需新 status 值。

### 6. walkaround 校验

`recurrences` 为 int ≥1；与 `[Case N]` 块数大致一致（count 应 = 1 + Case 块数，因首次不带 Case 号）；不一致报 INFO。归 [scriptable lint](2026-06-03-scriptable-mechanical-layer-design.md) 的 lint 子命令时一并脚本化。

## 迁移

把本会话刚建的 `incidents/powershell-herestring-in-bash-tool.md` 的 `**Recurrences**: 3 …` body 头迁成 frontmatter `recurrences: 3`（首条样例 + dogfood）。

## 改动面

protocol（字段表 + 复发 auto-count 小节 + 晋级 gate 措辞 + 去"never auto-increment"旧句）、templates（incident frontmatter 块 + body 去 `**Recurrences**` 头 + Rules）、exit-ritual（Step 5a 复发扫描）、`flightdeck_index.py`（incident 行渲染 `recur:` + 测试）、here-string incident（迁移）、walkaround（加校验项）。

## Related

- [[flightdeck-2.0-abandoned]] —— 不重蹈状态机覆辙
- [scriptable-mechanical-layer](2026-06-03-scriptable-mechanical-layer-design.md) —— recur 校验归其 lint
- [preflight-tri-review-remediation](../archive/specs/2026-06-03-preflight-tri-review-remediation.md) —— 错题本计数升级的延续
