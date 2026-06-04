---
status: idea
summary: flightdeck 只有"管理既有工件"的仪式，没有"撰写新工件"的入口——撰写发生在外部 skill（如 brainstorming），而约定（位置在 commits.md、frontmatter 在 templates.md、INDEX/cockpit 归属在协议正文）分散无单一权威源、且不在撰写开始时被加载，导致 agent 每次"现翻"重推。修法方向：把"撰写新工件的位置+frontmatter"集中成单一权威且写时被指向的源 / 或加轻量 new-artifact 入口盖 frontmatter+落目录 / 或在 preflight 把"产出 spec/plan→一律写 flightdeck/<folder>/、用此 frontmatter、绝不写 docs/"作常驻覆盖注入
last_updated: 2026-06-04
---

# 撰写新 deck 工件的约定无单一权威源，导致每次"现翻"

> 由真实会话（2026-06-04，preflight 瘦身设计）暴露：用 brainstorming/writing-plans 产出 spec/plan 时，agent 不得不读 `templates.md`、翻现有 spec、翻 `commits.md` 才能拼出"放哪 + frontmatter 长啥样 + 谁更新 INDEX/cockpit"。本该被遵守的约定，变成每次重新推导。供 flightdeck 取舍。

## 现象

每次让 agent 产出 deck 工件（spec / plan / 设计文档），它都得"现翻"——读 `templates.md`、翻现有 spec、翻 `commits.md`——才能拼出"放哪 + frontmatter 长啥样 + 谁更新 INDEX/cockpit"。本该遵守的项目约定，变成每次重新推导。

## 根因（结构性，不是用户配置缺失）

1. **flightdeck 只有"管理既有工件"的仪式**（`preflight` / `landing` / `walkaround` / `emit-agents-md`），**没有"创建/撰写新工件"的入口**。撰写动作发生在外部 skill（如第三方 `brainstorming`）里。
2. **撰写 skill 不知道 flightdeck 的约定。** `brainstorming` 默认把 spec 写到 `docs/superpowers/specs/`、用它自己的 frontmatter，对 `flightdeck/specs/` 和 `templates.md` 一无所知。它只留了句"用户偏好可覆盖默认位置"，但没规定这个覆盖该从哪读。
3. **约定本身是分散的**：spec 位置在 `commits.md`、frontmatter 在 `templates.md`、INDEX/cockpit 归属在协议正文——没有一个"撰写 deck 工件时该遵守的格式"的**单一权威来源**，可供撰写 skill 在动笔时被指过去。

**结果**：撰写 skill 与 deck 存储约定之间的交接面是**未定义的**，只能靠 agent 临时人肉对账 =「现翻」。

## 修法方向（治本，供取舍）

- **A. 单一权威源** —— 让 flightdeck 把"撰写新工件的位置 + frontmatter 模板"集中成单一权威、且在撰写开始时会被加载/指向的来源。
- **B. new-artifact 入口** —— 提供一个轻量 `new-artifact` 入口/命令，由它负责盖正确的 frontmatter + 落正确目录；外部撰写 skill 撰写完**交接给它**而不是自己编路径。
- **C. 常驻覆盖注入** —— 在 `preflight` / 协议里把"任何 skill 产出 spec/plan/设计 → 一律写 `flightdeck/<folder>/`、用此 frontmatter、绝不写 `docs/`"作为常驻覆盖注入上下文，让 agent 不必重新推导。

**核心**：把"`brainstorming` 默认值的覆盖"上升到**协议层**、变成**权威且被加载**的规则，而不是每次现推。

## 备注（评估时的几个钩子）

- B 与 flightdeck 现有"机械层脚本化"（`flightdeck_init.py` 盖 frontmatter+落目录）天然契合——new-artifact 可复用同一盖章逻辑。
- C 与 idea spec `preflight 静默 bump 提示`（`2026-06-03-preflight-silent-bump-nudge-design.md`）类似，都是"把隐性约定显式注入开场上下文"的思路。
- 注意别把 cockpit `## 进行中`（仅 active 投影）/ idea 不进 cockpit 等 model-v4 规则在新入口里重新实现一遍——应复用 `flightdeck_index.py` 的派生。
- AGENTS.md（emit）也是一个候选的"常驻注入"载体（C 方向）。
