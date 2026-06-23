# 外圈人类文档随协议变更静默漂移

## Signature
- symptom: README/docs/.github 等人类叙事文档描述的结构或机制在 skills/ 协议里已不存在（如 debriefs/、根 INDEX.md、sketches/、`## Next session`、checklist→rules 晋升级）
- error_type: —
- where: README.md / README.zh.md / docs/*.md / .github/PULL_REQUEST_TEMPLATE/
- trigger: 协议变更（文件夹模型、仪式语义）落地后只清扫 skills/，未扫外圈

## 症状/复现

3.0 大改（drop-root-index、debriefs 移除、sketches 并入 specs idea 池、status⟂location）落地并完成 skills/ 失实清扫后，外圈文档仍大面积保留 2.x 叙述：README 目录树含根 INDEX/sketches/debriefs、cockpit 示例用 `## Next session`；docs/philosophy 写「晋升到 checklists 再到 rules」（晋升门只有一级）；docs/comparison 称「incidents/checklists 携带 MDC frontmatter 供 Cursor 互操作」（实为 MDC *启发*的 when_to_read/applies_to，互操作走 adapter 的 .mdc）；.github 验证模板 S5 仍考核存入 debriefs/。用户连续两轮人工抓出。

## 根因

失实清扫的 spec 把范围圈定为 `skills/` 12 个文件——协议（AI 面）有清扫仪式，外圈（人类面）没有任何机制把它挂进协议变更的影响面：外圈文档不带 `applies_to`、不进 walkaround 审计、也不在 landing 的 stale 检测路径上，于是协议每动一次，外圈就静默漂移一格。点状修补（只改被指出的那一处）会漏同文件其他段落——本档案 Case 2 即「修 mermaid 旧名时漏掉同一张图里的根 INDEX/sketches/debriefs 节点」。

## 修法

协议语义/文件夹模型/仪式行为变更落地时，清扫范围默认含外圈：README 中英 + docs/*.md + .github 模板 + adapters/*.md（CHANGELOG/TEST_PLAN/archive 是历史记录，不改）。手法用「关键词全仓 grep + 逐句对照权威源（protocol/folder-semantics/exit-ritual/templates）」，不点状修补。本档案 `applies_to` 即外圈清单，landing 的 stale 检测可借此挂钩。

## Cases
- 2026-06-11 首次：用户指出 README 仍宣传 debriefs/ 与根 INDEX.md（实际 sketches/ 也已并入 specs）。
- 2026-06-11 Case 2：用户追问「docs 是不是也没看清就写了」——逐句复核 docs/ 三篇，再出三处失实（晋升两级、MDC frontmatter 互操作、peer reviews before merge）+ architecture 漏 turn-end hook。
