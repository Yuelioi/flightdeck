---
status: done
summary: 按 load 频率降 skill token + 治流程过长：常驻 SKILL 优先、dedup-to-canonical / defer-to-companion / script-owns / summarize；不改行为、保双轨 fallback。第一批已落（SKILL 瘦身 + 5 漂移修），余下分批
last_updated: 2026-06-03
---

# Skill token reduction（+ 流程过长治理）

## Problem

skill 文本 ~130KB ≈ ~32k token；每次调用进上下文。很多内容是逐步 prose、跨文件重复、或脚本已接管的机械步骤。叠加"流程过长"（preflight 每次都加载一生只跑一次的建档分支等）。

## Approach

**按 load 频率定优先级**（关键洞察）：`preflight/SKILL.md` 常驻（每会话）> protocol/exit-ritual（常被拉取）> templates/folder-semantics（按需，优先级反而低）。

**手法**：dedup → 单一 canonical + 指针；defer → 搬进按需 companion；script-owns → 机械步骤缩成 gist + 指脚本；summarize → 逐步 prose 压成要点。**铁律**：不改行为；双轨 fallback（无 runtime 仍可手动）原文保留、仅去重复/justification。

来源：2026-06-03 四 agent 并行审 9 个 skill 文件 + 跨文件去重审。

## Done（第一批，已提交）

- **preflight SKILL.md 158→127**：first-time-setup 搬进 `setup.md`（只首次无 deck 时加载）。**每会话**省，最高价值。`4463f89`/`d9b1aa8`。
- **5 个跨文件漂移 bug 全修**：sketch last_updated 对齐、"main token saving" 双标注、两个同名 Authority order → "Override authority" vs "Source-of-truth precedence"（+ 修错链）、4-trigger 计数（exit-ritual Step4 收成指针）。
- **流程**：A2 —— preflight step 7 status 审计收窄到"已加载文件夹"（修"扫不动没读的文件夹"）。
- **去重**：folder-semantics INDEX-Rules 三重复述 → 指针、删冗余 Naming 表；protocol behavioral-override 段 5-bullet → 2 句（去"穿针"）。

## Done（第二批，2026-06-03）

- **Tier 2 真重复折叠**：templates status-flow 图（6 行 verbatim）→ 指针 protocol §Status；protocol Core-principle 与 Write-gate 的"write strictly"重句 → 合并到 write-gate canonical。（核查发现批 1 已清掉多数高频 fat；其余"6×/5×"多为独立加载 skill 的简短本地引用或已是指针，保留——删了那些 skill 就跑不起来。）
- **exit-ritual 内部去重**：决策树 Step 2 的 (a)–(i) 由逐条展开压成单行 + 指针「## Classification heuristics」（详情归专节）；Step 3 INDEX-scope 收成 gist + 指针；Step 3a status 箭头 → 指针 protocol §Status。**决策树 ~58→25 行**，不改行为。
- **A3 git reconcile 降 heuristic**：SKILL Step 4/5 由"Mismatch handling"逐条改为"fuzzy 启发式信号——只报明确背离、不猜等价"，~12→4 行、降误报。

## 结论 / 余项处置（2026-06-03，评估后定）

值得做的减重批 1+2 已落。剩余按证据定案：

- **A1 拆 migration —— 关闭（moot）**：「重的嵌套迁移树」已不存在——批 1 把 SKILL Step 2 压成一段指针，迁移重步骤本在 `MIGRATION.md`（仅迁移时加载），protocol §Migration 仅 ~10 行检测逻辑。再抽第三个 companion 只会**碎片化**（检测/步骤分两处），不减负。当前结构（检测在 protocol、步骤在 MIGRATION.md）已是 A1 想要的形态。
- **A4 拆 protocol —— 关闭（不划算）**：`protocol.md#anchor` 引用图（grep 全仓）显示高频锚点 `#rule-resolution-order`(×13)、`#frontmatter-field-reference`(×4)、`#status`、`#source-of-truth` 是**紧耦合核心、必须同处**；可独立外迁的只有 §Migration（=A1，已关）。4 路拆分 = 为接近零的常驻收益换 ~20 个跨 10 文件 anchor 断裂风险。
- **templates.md `### Rules` —— 低 ROI，留**：load-on-demand 低频；body 块是 paste-able 价值所在；`### Rules` 是校验规则+少量语义重述混排，逐段抠收益微、易伤可读。已取最清晰一处（status-flow 图→指针）。
- **walkaround 压缩 —— 改归 [scriptable-mechanical-layer](2026-06-03-scriptable-mechanical-layer-design.md)**：前置是 `flightdeck_index.py` 加 `lint` 子命令（验 status 合法值 + dangling-link/anchor 检查）。不属本 spec，归那份。

## QA（2026-06-03）

- **anchor/link 一致性全仓校验**（131 md）：发现并修 1 处**既存** dangling link——exit-ritual「See also」指 `SKILL.md#common-mistakes`，实际该节在 `protocol.md`。已修。
- **脚本测试** `scripts/tests/`：24 passed。
- **INDEX `--check`**：clean。

## 量级

不改行为估计可砍 ~400-500 行；常驻 SKILL + 高频 protocol/exit-ritual 的每会话省最多（已优先拿下）。

## Related

- [scriptable-mechanical-layer](2026-06-03-scriptable-mechanical-layer-design.md)（脚本接管机械层 → prose 可缩；walkaround lint 是其 Phase 3）
- [preflight-tri-review-remediation](2026-06-03-preflight-tri-review-remediation.md)（A1/A2/A3 流程项的来源；三方审核整改总账）
