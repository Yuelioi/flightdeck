---
status: active
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

## Remaining（分批，按价值/频率）

- **templates.md（按需、优先级低）**：~210 行 body 模板 + 各 "### Rules" 段重述 protocol 字段语义 → 压成指针（body 模板保 paste-able 不动）。
- **walkaround**：审计压缩 —— **前置**：`flightdeck_index.py` 目前只验 INDEX↔frontmatter 行一致、**不验 status 合法值**；要压 Audit 1/2/3 得先给脚本加 `lint` 子命令（= [scriptable-mechanical-layer](2026-06-03-scriptable-mechanical-layer-design.md) Phase 3）。**阻塞**。
- **流程（结构性，较大）**：A1 拆 migration 成「仅版本不符时加载的 companion」（轻路径，不加新命令）；A4 拆 protocol.md（**最低 ROI / 最高 anchor 改动风险**，待评估）。

## 量级

不改行为估计可砍 ~400-500 行；常驻 SKILL + 高频 protocol/exit-ritual 的每会话省最多（已优先拿下）。

## Related

- [scriptable-mechanical-layer](2026-06-03-scriptable-mechanical-layer-design.md)（脚本接管机械层 → prose 可缩；walkaround lint 是其 Phase 3）
- [preflight-tri-review-remediation](2026-06-03-preflight-tri-review-remediation.md)（A1/A2/A3 流程项的来源；三方审核整改总账）
