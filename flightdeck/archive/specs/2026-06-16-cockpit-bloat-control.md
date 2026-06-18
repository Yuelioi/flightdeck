---
status: done
summary: cockpit 膨胀治理（v2 重订）：现存的字段纪律（Active focus 一行 / Last updated ≤200 / Key Context literal + accumulator-drain）只是散文,landing 无任何环节在出场时检查它们——补「逐字段密度检查 + 门控 trim」抓「行少字密」,加 active 计数非阻塞提示。原 v1 的「排空冗余散文」「野章节守卫」已被 Pending Review 转正 + Accumulator-drain discipline 吸收,本版剔除。
last_updated: 2026-06-19
---

# Cockpit bloat control: 出场密度检查 + active 计数提示（v2 重订）

> 3.0 alpha 打磨。**已启动 · 2026-06-19 按现实重订**(原 v1 立论被后续提交覆盖,见下「已被现实吸收」)。

## 背景 / 动机(仍成立的内核)

用户观察:cockpit.md 有时会变得很大。cockpit 是恢复载荷的仪表盘,胖了既费 token(每次 landing/preflight 都读)又稀释了真正该看的下一步。

诊断(本仓 dogfood 实测:行少却字密)——膨胀**不在行数,在密度**:手维护的散文字段(`Active focus`、`Last updated` 括号、`Key Context` 条目)会从「粗线条」累积成叙述/changelog。现有的「80 行」长度检查是**行数**判据,**抓不到「行少字密」**。

**关键洞察(本版核心):** 治这个膨胀所需的**纪律已经全部写进了 `exit-ritual.md`**(`Active focus` 一行 / `Last updated` ≤~200 字 / `Key Context` 只放 literal + accumulator-drain)。缺的不是规则,是**出场时没有任何环节去检查这些规则被没被违反**——纪律是散文,landing 的 Length check 只数 80 行,放行了一切「行少字密」。

## 已被现实吸收(原 v1 的两条立论作废)

2026-06-16 之后的提交把 v1 的部分靶子直接消解,故剔除:

1. **`## Pending Review` 已转正为规范字段**(提交 `a9bb9eb`,`exit-ritual.md` §Cockpit update / §「the standing awaiting-review home」)。v1 的**组件 C.1「野章节守卫」**拿它当主要靶子立论——前提已不成立,**删除**。(残余形态「守卫规范字段集之外的章节」价值过低,一并不做。)
2. **`exit-ritual.md` Accumulator-drain discipline** 已明令:landing 时 `Key Context` 必须 clear「目标已 archive/graduate、下次会话不需要」的条目、shrink 过长条目。这正是 v1 的**组件 A「着陆排空冗余散文」**要的效果——已作为 landing 判断步存在,**删除组件 A**(不再单列;其精神并入下方密度检查的 `Key Context` 一项)。
3. **walkaround Audit 14** 已非阻塞浮出 `Key Context` stale/散文化/超长(INFO)。审计侧已覆盖,本版不再加 walkaround 项。

## 决策(v2 — 只剩两条,均为「补检查 / 补提示」,不新增机制)

### 组件 B(留 · 本版核心)— landing 出场「逐字段密度检查 + 门控 trim」

在 `exit-ritual.md` §Length check(landing Step 4 出场前)把现有「>80 行 → trim」升级为**行数 + 逐字段密度双判据**,逐字段软上限直接复用已写死的纪律:

- `Active focus` ≤ 一行 / ~200 字
- `Last updated` 括号 ≤ ~200 字
- `Key Context` / `Pending Review` 每条 ≤ 一短行 literal,且无「目标已归档仍滞留」条目(后者复用 Accumulator-drain 判据)
- 任一超限 → **提议精简(门控)**:把还活着的设计细节挪去对应 `specs/` 条目再删 cockpit 散文。**门控**因为「哪些细节还活着、该挪哪」是判断活,要用户点头。≤ 限即 no-op(幂等)。

与 80 行检查**并列**:80 行抓「条目堆积」,密度检查抓「行少字密」,两个判据互补。

### 组件 C.2(留)— active 计数非阻塞提示

`## In Progress` AUTO 列表的 active 项 > ~5 → preflight / landing 给一条**非阻塞**提示「N 条 active 线程,考虑关停/搁置部分」。只提醒、不删——根因是开太多线程,治理在行为不在 cockpit。落 `skills/preflight/SKILL.md` + `skills/landing/SKILL.md`(或其 exit-ritual 出场段)。

## 非目标(YAGNI)

- **不**给 cockpit 加硬字符总预算 / 自动截断——会误伤恢复载荷,违「上下文不丢」红线。密度检查只「提议」,删动作门控。
- **不**新增 walkaround 审计项——Audit 14 已覆盖 Key Context 卫生;Pending Review 已是规范字段无需守卫。
- **不**改 `## In Progress` 的 AUTO 机制——它已自排空、工作正常;C.2 只读它的计数。
- **不**把密度上限做成结构化字段或脚本硬校验——上限是软判据,留 AI 在 landing 判断(脚本只算 INDEX 的确定性事实,不做判断)。

## 落地面

- `skills/preflight/exit-ritual.md` —— **真相源**:§Length check 升级为行数+逐字段密度双判据(组件 B);出场段加 C.2 active 计数提示。
- `skills/landing/SKILL.md` —— Step 4 引用上述检查(checklist 面,不重述真相)。
- `skills/preflight/SKILL.md` —— C.2 active 计数提示在 preflight 报告侧的对应措辞。
- (不再触 `skills/walkaround/SKILL.md`:Audit 14 已覆盖。)

## 验证

- 用本 spec 把**当前** dogfood cockpit 过一遍密度检查:collapse 超长 `Active focus` / `Last updated`、shrink `Key Context` 滞留条目,看是否触发门控提议。
- `uv run pytest scripts/tests/`(若密度检查落到脚本侧辅助则加测试;纯措辞改无脚本测试)。
- 归 3.0 alpha;`wc -m flightdeck/cockpit.md` 作 token 代理看净降。

## 沿革

- **v1(2026-06-16)**:三组件 A(着陆排空冗余散文)/ B(密度检查)/ C(C.1 野章节守卫 + C.2 active 计数)。未实现。
- **v2(2026-06-19)**:按已落地现实重订。A 被 Accumulator-drain discipline 吸收、C.1 因 Pending Review 转正作废,均剔除;只剩 B(密度检查,核心)+ C.2(active 计数)。
