---
status: done
summary: 删人工开关目录（7 个 magic-string toggle）+ resolution-order 教学机器；rules.md 从「人手填语法」改为「用户自然话→AI 落盘规则」，保留 version:3.0 戳 + Project conventions；AI 读 rule 高于默认执行，化解删开关后『别人没逃生舱』
last_updated: 2026-06-16
---

# AI-authored config: remove human toggle surface, AI-managed rules.md

> Spec 2 / 2（配套 `2026-06-16-act-report-close-loop`，已 land）。本篇＝铁律第一根「纯 AI 操作」的配置面。**已启动。**

## 背景 / 动机

flightdeck 现有 7 个人工 opt-out 开关（`rules.md` `### Autonomy overrides` 的 magic-string）+ 一整套教人怎么设的 `Rule resolution order` 机器（protocol 表、templates 表、各 skill 的 `Overrides:` 分支）。纯 AI 全自动用法下：

- **人根本不编辑这些**——本仓 dogfood 的 `### Autonomy overrides` 段是空的，用户一个都没用。
- 这套词汇表 + 教学散文压在热/冷路径预算上，却服务一个不存在的「人来调旋钮」场景。

但开关背后的**行为能力**（如「commit 前先问」「这个 deck 不走 git」）对别的用户/工作流仍有合法价值——直接删能力会让 flightdeck 作为「发给别人的工具」失去灵活性。

**解法：删人工配置面，不删配置能力。** 入口从「人编辑 magic-string 语法」翻成「用户自然话说 → AI 落盘成 rule」。AI 既是规则作者又是读者，规则可用自由文，不需固定词汇表。

## 决策（已拍板）

1. **删开关目录 + resolution-order 教学机器**（散文 / 表 / 分支）。
2. **rules.md 改作者**：保留文件 + `version: 3.0` 戳 + `### Project conventions`；`### Autonomy overrides` 段从「人填 magic-string」变「AI 按用户自然话写自由文规则」。
3. **保留语义**：AI 读到 deck 规则 → 高于默认执行；无规则 → 好默认 + 环境推断 + 判断。授权链简化为 **CLAUDE.md（项目）> deck 规则 > flightdeck 默认**。
4. **环境推断保留**（git 探测、emit-AGENTS.md「有才 regen」）——它们是推断不是开关，只撤人工 override 旋钮。

## Part 1 — 删人工开关目录

撤掉作为**人类词汇表**的 7 个 magic-string：`commit: ask` · `don't auto-commit; leave changes for me / CI` · `landing: nudge on done, don't auto-run` · `landing: don't soft-land at end-of-turn` · `status: don't auto start` · `this deck doesn't use git` · `has AGENTS.md but don't auto-regen`。

连带删：`protocol.md` 的 Rule resolution order 表 + override-authority 详表（保留一行精简授权序）；`templates.md` 的 House-Rules 开关表；各 skill 里 `Overrides: …` 针对这些串的分支散文。

## Part 2 — rules.md AI-authored

- rules.md 仍必备，**保留 `version: 3.0`**（3.1 迁移锚点，神圣）+ `### Project conventions`。
- **`### Rules` 段**（原 `### Autonomy overrides`）语义：**用户提持久行为变更 → AI 用自然话追加一条 + 注明来源/日期**，并即刻遵守。例：用户「以后 commit 前先问我」→ AI 写 `- commit 前先问我（用户 2026-06-16）`，后续 commit 即先问。
- skills 加识别：`以后 / 每次 / always / never` 类持久指令 → 落 rules.md（对齐 harness 自身 update-config / memory 模式）。
- 写规则发生在正常 turn/landing（非 preflight，**保 preflight 纯读零写**）；这条写动作本身是 Spec 1 的「可逆-自动 + 报告」覆盖的一个动作。

## 落点 / 爆炸半径（初估）

`skills/preflight/protocol.md`（删 resolution-order）· `skills/preflight/templates.md` + `scaffolds/full/flightdeck/rules.md`（重写 rules.md 模板）· `status`/`landing`/`preflight`/`emit-agents-md`/`walkaround` 的 `Overrides:` 分支 · 测试（删开关用例 / 改授权链断言）· 外圈 README/AGENTS/CHANGELOG/architecture · 知识归宿写进 `docs/descope-baseline.md`。

## 红线 / 不动项

rules.md `version: 3.0` 戳保留 · 环境推断（git / emit）保留 · preflight 纯读零写 · CLAUDE.md 仍是最高项目层。

## 已定（启动时拍板）

- **段名 `### Autonomy overrides` → `### Rules`**：不再是「override 开关」，而是 AI 按用户自然话维护的行为规则；保留 `### Project conventions`（deck 约定）与 `### Rules`（行为规则）两段。
- **偏好归宿**：deck-specific 行为 → deck 本地 `rules.md`（跨 host 可移植、preflight 已读）；cross-project 偏好 → 用户的 `CLAUDE.md`（最高项目层）。不进 harness memory（非 deck 可移植）。
- **graduate：否**（契约家在 templates/protocol）。

## 验证

`uv run pytest scripts/tests/`；`wc -m` 确认删开关后热/冷路径字符数下降。
