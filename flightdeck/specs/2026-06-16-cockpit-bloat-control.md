---
status: active
summary: cockpit 膨胀治理：着陆归档时自动排空引用刚归档 artifact 的冗余散文（可逆，自动）；规范字段替换而非追加 + 逐字段密度检查（门控 trim）；walkaround 守卫野章节 + active 计数非阻塞提示。规范字段集本就精简，膨胀来自野章节与散文不排空。
last_updated: 2026-06-16
---

# Cockpit bloat control: land-tied prose sweep + field discipline

> 3.0 alpha 打磨。**已启动。**

## 背景 / 动机

用户观察：cockpit.md 有时会变得很大。担心点 = cockpit 是恢复载荷的仪表盘，胖了既费 token（每次 landing/preflight 都读）又稀释了真正该看的下一步。

诊断（基于本仓 dogfood cockpit 实测：35 行却 2021 字符）——膨胀**不在行数，在两条缝**：

1. **野章节**：当前 cockpit 那段最胖的 `## Pending Review` **根本不是规范字段**。exit-ritual §Cockpit update 钦定的字段只有：`Last updated` / `Active focus` / `## 进行中` / `## 下一步` / `## 关键上下文` / `Hanging tasks`。`## Pending Review` 是 dogfood 时手加的野章节，重复了 specs/plans + git 已记的东西。
2. **规范字段散文不排空 / 只追加**：
   - `## 进行中` 是 AUTO 投影（从 `status:active` spec/plan 生成），plan 归档后**自动消失**——结构上不膨胀。列表长的根因是**同时开太多 active 线程**（焦点流失信号），不是 cockpit 机制问题。
   - 手维护字段才是真凶：`Active focus` 从「一行粗线条」累积成「Spec 1（…）+ Spec 2（…）」的叙述；`Last updated` 括号从「≤200 字一句」塞成 changelog；引用已落地 artifact 的散文（如关键上下文里的字面量）在该 artifact 归档后没跟着排空。

**关键洞察**：规范字段集本来就是精简的。现有的「80 行」长度检查是**行数**判据，抓不到「行少字密」这种膨胀。已有的字段上限规则（`Last updated ≤200 字`、`Active focus` 一行）**存在但被违反**——问题在没有任何环节在 land 时检查它们、也没在 artifact 归档时排空对它的引用。

## 决策（已拍板 — 分层：可逆=自动 / 涉及删活上下文=门控）

三个组件。自动/门控边界严格沿 flightdeck 既有哲学切：排空「已被 archive 覆盖的冗余」是可逆且不丢恢复载荷 → 自动；挪「还活着的设计细节」是判断活 → 门控。

### 组件 A — 着陆时「冗余散文自动排空」（自动）

全量 landing 归档某 artifact X 后，在 cockpit board-sync（landing Step 8 / exit-ritual §Cockpit update）增加一步：
- **扫规范散文字段（`## 关键上下文` 及任何引用 X 的散文条目），排掉「主语是本次刚归档的 X」的条目。**
- 判据：AI 判断「这条是否已被 `archive/` 里的完整文件覆盖」。范围**严格限定在本次 landing 刚归档的 artifact 集**，因此无需逐条确认（有界、冗余、git 可逆）。
- 安全性（守红线）：完整载荷搬进了 `archive/`，排掉 cockpit 里的影子**不丢恢复载荷**。
- 幂等：再跑一次 landing，无新归档 → 无可排空项 → no-op。

### 组件 B — 规范字段「替换而非追加」纪律 + 逐字段密度检查（门控）

1. **纪律强化（exit-ritual §Cockpit update 措辞）**：把 `Active focus` / `Last updated` 明确写成**替换语义**——当其引用的 artifact 落地，**重写**成当前粗线条，而非追加「X done + Y done + Z done」。规则已部分存在（`Last updated 不是 session-activity log`、`Active focus 一行粗线条`），强化为「land 时主动 collapse」。
2. **密度检查升级（landing Step 8）**：现有「cockpit > 80 行 → 提议精简」是行数判据。补**逐字段软上限**，与 80 行检查并列：
   - `Active focus` ≤ 一行 / ~200 字
   - `Last updated` 括号 ≤ ~200 字
   - 其余散文字段每条 ≤ 一短段
   - 任一超限 → **提议精简（门控）**：把还活着的设计细节挪去对应 `specs/` 条目再删 cockpit 散文。门控因为「哪些细节还活着、该挪去哪」是判断活，要用户点头。

### 组件 C — 野章节守卫 + active 计数提示（小）

1. **walkaround 加审计项**：cockpit 出现规范字段集之外的章节（如 `## Pending Review`）→ 报 **INFO**「非规范 cockpit 章节，内容应归 specs/plans/INDEX 或删」。（walkaround 是只读审计，只报不改。）
2. **active 计数非阻塞提示**：`## 进行中` AUTO 列表的 active 项 > ~5 → preflight/landing 给一条**非阻塞**提示「N 条 active 线程，考虑关停/搁置部分」。只提醒、不删任何东西——因为根因是开太多线程，治理在行为不在 cockpit。

## 非目标（YAGNI）

- **不**给 cockpit 加硬字符总预算 / 自动截断——会误伤恢复载荷，违红线。密度检查只「提议」，删动作门控。
- **不**自动删野章节——A 只排空规范字段里对刚归档 artifact 的冗余引用；野章节由 walkaround 报、用户处置。
- **不**改 `## 进行中` 的 AUTO 机制——它已经自排空，工作正常。

## 落地面

- `skills/preflight/exit-ritual.md` —— 真相源：§Cockpit update 加组件 A 排空步 + 组件 B 替换语义/密度检查措辞。
- `skills/landing/SKILL.md` —— Step 8 引用组件 A/B（checklist 面，不重述真相）。
- `skills/walkaround/SKILL.md` —— 加组件 C.1 野章节审计项（INFO 级）。
- `skills/preflight/SKILL.md` + `skills/landing/SKILL.md` —— 组件 C.2 active 计数提示。
- 可能 `skills/preflight/protocol.md` —— 若需把「cockpit 规范字段集」显式钉成清单供 walkaround 引用。

## 验证

- 用本 spec 把**当前** dogfood cockpit 清一遍作首个验证：删 `## Pending Review`、collapse `Active focus` 成一行、瘦 `Last updated`。
- `uv run pytest scripts/tests/`（若密度检查/野章节审计落到脚本层则加测试）。
- 归 3.0 alpha；`wc -m flightdeck/cockpit.md` 作 token 代理看净降。
