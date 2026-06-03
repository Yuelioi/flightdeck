---
status: active
summary: 把 flightdeck 的机械层（INDEX 重生 / walkaround lint / AGENTS emit / 对账）脚本化以降 token，模型只留判断；单语言 Python stdlib + markdown fallback（官方双轨）+ rules `scripts:` 开关；先拿 INDEX-regen 做 PoC 量收益
---

# 机械层脚本化（scriptable mechanical layer）

## 目标

flightdeck 本质上一半是 **linter + generator**：walkaround 审计、landing 重生 INDEX、emit-agents、status/计数对账——这些机械活现在全由模型逐字做，token 随 deck 规模线性涨。把**机械层下放给确定性脚本、模型只留判断层**，目标是降 token + 拿到可测性，且**不破坏 flightdeck 的纯 markdown / 工具无关身份**。

## 调研定论（2026-06-03，三 agent：本地已装 skill + Anthropic 官方 doc skills + 生态/标准文档）

每条带证据。来源链接见末尾。

1. **多语言端口 = 没人干，劝退。** 跨官方/标准/本地，找不到把**同一操作**做成多语言的例子；真实做法是**按任务分语言**（py 数据、node 生成），从不重复同一个活。标准文档明确推荐单语言 + 锁版本防漂移。→ flightdeck **单语言**。
2. **Fallback 是官方钦定双轨。** Anthropic best-practices 把每个工作流写成 "with code" + "without code" 两份；without-code 的 validator 就是"一个 markdown，模型靠读+比对执行"。→ **markdown 协议 = fallback，脚本 = 加速器**，不是妥协。flightdeck 现有 prose 就是 "without code" 那份。
3. **分界线（行业通则，且更严）：脚本算事实、模型做判断。** docx skill 明文：编辑/判断"**Do NOT write Python scripts，用 Edit 工具**"。脚本=纯机械只读/生成，判断永不进脚本。
4. **何时脚本化：proven-by-repetition。** skill-creator 法则——模型每次跑都在重造同一个 helper，就固化进 `scripts/`。→ flightdeck 指向 **walkaround（每次重做的 linter）+ landing INDEX 重生（每次重算的 generator）**。
5. **依赖：纯 Python stdlib、零安装**（绕开"prose 声明 + 按需 pip"的主流麻烦）；调用 `python scripts/x.py`。
6. **rules `scripts:` 开关——因"无跨工具标准"才更该自定义。** 原生开关全工具私有（Codex `[[skills.config]]`、Claude `userConfig`），互不通用；flightdeck 自定义、由 markdown 层读，是唯一跨四工具的办法。

## 决定

- **语言**：Python，纯 stdlib，零依赖单文件。
- **形态**：单 CLI 多子命令 `flightdeck.py <cmd>`（`regen-index` / `lint` / `emit-agents` …），单文件单测试套件单版本。
- **版本钉死**：脚本编码了 layout 结构/status 合法值，须与 deck `version`（对 `MIGRATION.md current`）匹配；不符则脚本拒跑、退化手动。防旧脚本糟蹋新 deck。
- **fallback**：每个子命令对应的 markdown 慢路径保留（= 今天的行为，任何工具可跑）。
- **rules.md 配置**：
  - `scripts: auto`（默认）— 探测可用 runtime（探到就钉进 rules，如 `scripts: python3`），无则退化手动。
  - `scripts: off` — 强制手动（信任/审计敏感场景；markdown skill 自动跑代码是高信任动作，必须给逃生口）。
  - `scripts: <runtime|path>` — 钉死解释器（解 `py` vs `python3` 歧义）。
  - 首次 opt-in 提示，既是信任闸也是可发现性。

## 红线（尤其 Windows）

- 官方 doc skills 全 **POSIX-only、零 Windows 处理**（LD_PRELOAD、`~/.config` 硬路径、grep/nohup/kill、裸 `python`）。flightdeck 用户 Windows-first → **脚本里不碰 shell/bash，纯 Python**，无官方先例可抄。
- **脚本执行跨工具支持**：Claude ✅ / Cursor ✅ / **Codex 存疑**（默认 instruction-only）/ **Gemini 没确认** → fallback 必须留。
- **token 收益方向对但全网无实测数字**（只有"输出才进上下文、省 codegen"定性论证）→ flightdeck 自己量。

## 操作清单（script 还是 model）

| 操作 | 归属 | 性质 | 备注 |
|---|---|---|---|
| INDEX 重生（folder AUTO 块 + root 计数） | **script** | generator | **PoC 首选**：最机械、每会话必跑、deck 自身即 golden fixture |
| walkaround 全量审计（Audit 1–10） | **script** | linter | 最大 token 收益，但面广，PoC 之后 |
| emit-agents-md 标记间重生 | **script** | generator | 文本变换 |
| status 合法性 / 计数对账 | **script** | check | 只读吐 JSON |
| git reconcile 信号采集 | **script**（采集）/ model（判断） | 半 | 采 branch/status/stash/log，判等留模型 |
| 知识分类（bug→incident…） | **model** | 判断 | 永不脚本 |
| routing trigger 匹配当前任务 | **model** | 判断 | 脚本只抽 frontmatter，匹配留模型 |
| migration 决策/改写 | **model** | 判断 | 交互+判断，不脚本 |

## 顺序

- INDEX-regen 与 [preflight-tri-review-triage](preflight-tri-review-triage.md) 的 A1/A2 重构**正交**（INDEX 格式独立于 migration/status-audit），可**现在就做**，不会被重构掉。
- walkaround / 涉 preflight 范围的脚本，等 triage 的范围重构（A1 拆 migration 等）落定再上，避免"脚本化一坨又重构掉"。

## PoC 计划（→ 开始干）

1. TDD：以 flightdeck 自身 deck 为 golden fixture（本会话已保持 INDEX 与文件同步），写 `regen-index` 子命令重生**应等于**当前 INDEX 文件。
2. 纯 Python stdlib；解析各文件夹 frontmatter（status + 各文件夹特有字段：checklists/incidents 的 when_to_read/applies_to、debriefs 的 reviewed、specs/plans/sketches 的 summary）。
3. 跑通后**量 token/工作量差**（对比模型手动重生），用数据决定是否铺开 walkaround 等。

## PoC 结果（2026-06-03，已建 + 已落地）

`scripts/flightdeck_index.py`（纯 Python stdlib，~100 行）+ `scripts/tests/`（unittest，**10 测试**，TDD 全程红→绿）。子命令式 CLI：
- `python scripts/flightdeck_index.py <deck>` —— 从 frontmatter 重生所有 folder INDEX + root INDEX。
- `python scripts/flightdeck_index.py <deck> --check` —— 只读，报漂移，有漂移 exit 1（适合 CI / walkaround）。

**决策已锁**：
- **行序 = 文件名字母序**（canonical）。pre-script 的手工 append 序无法从文件系统复现 → incidents/debriefs 本已符合；specs/plans/sketches 首次重生被重排（已发生，见下）。
- **charts/ folder INDEX 手维护**（外部 import，无 frontmatter），脚本不重生；仅其 root 行按 entry 数派生。
- **row 真相源 = frontmatter**：summary 类取 `summary`，knowledge 类取 `when_to_read`+`applies_to`，debriefs 取 `reviewed`+`last_updated`（与 [incidents/index-row-summary-delimiter](../incidents/index-row-summary-delimiter.md) 确认的"rows are regenerated, not parsed"一致）。

**实证价值**：`--check` 当场在 flightdeck 自身 deck 抓出 **4 个文件夹漂移**（specs / plans / checklists / sketches）——INDEX 行的 summary/applies_to 早已偏离源 frontmatter（典型：`version-bump` 的 applies_to 在 INDEX 是 `[release,version,…]`，frontmatter 是 `[.claude-plugin,…]`）。已 `regenerate` 修复，复查 clean。证明手维护 INDEX 会静默漂移。

**token 实测论点**（与调研一致，verified 架构性）：脚本读 ~13 个文件全在 bash 子进程内，**不进模型上下文**；模型只见调用 + 一行输出（`regenerated: specs, plans, checklists, sketches`）。即**模型上下文成本 ≈ 常数，与 deck 规模无关**；手动重生则随 artifact 数线性涨（每个改动文件的 frontmatter + 每个 INDEX 都要进上下文 + 重排重算）。未给精确数字（手动路径未实跑），但"输出才进上下文"已坐实。

## 剩余（rollout，未做 → 待决定）

1. **接进 skill 契约**：landing / walkaround / status SKILL.md 加"脚本可用则 `python scripts/flightdeck_index.py <deck>`，否则按现有 prose 手动重生（fallback 双轨）"。
2. **rules.md `scripts:` 开关** + 首次 opt-in 提示（schema 见上）。
3. **版本钉死 guard**：脚本读 deck `version` 对 `MIGRATION.md current`，不符则拒跑、退化手动。
4. **walkaround 整体脚本化**（lint 子命令）—— 最大 token 收益，等 [preflight-tri-review-triage](preflight-tri-review-triage.md) 的范围重构落定再上。

## Open / flags

- 语言终定 Python（已决），但"有 node 没 py"的机器暂不覆盖（YAGNI，等需求）。
- Codex/Gemini 是否真能执行 `scripts/` 未经一手确认 → 全靠 fallback 兜底。
- 各文件夹 INDEX 行 schema 需从现有 INDEX + `templates.md` 精确抽取（PoC 第一步）。

## 来源

- Anthropic Agent Skills overview / best-practices / engineering blog（双轨、progressive disclosure、脚本只进输出）
- Claude Code plugins reference（`bin/` vs `scripts/` vs `hooks`、userConfig、信任门）
- agentskills.io 标准 + skill-creator（单语言锁版本、proven-by-repetition）
- Codex / Cursor / Gemini skills docs（跨工具执行支持差异）
