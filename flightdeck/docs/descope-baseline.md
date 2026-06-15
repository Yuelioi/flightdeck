---
status: active
when_to_read: 改 preflight/landing/walkaround 的职责边界、考虑给 deck 加向后兼容/迁移/校验机制、或往热路径加散文之前
applies_to: [skills/preflight/SKILL.md, skills/landing/SKILL.md, skills/walkaround/SKILL.md, skills/preflight/protocol.md, skills/_shared/bootstrap.md, scripts/flightdeck_index.py, scaffolds/full]
when_to_update: 3.0→3.1 真正引入格式变更/迁移时、校验归宿从 walkaround 迁移时、或热/冷路径预算政策调整时
last_updated: 2026-06-16
---

# 3.0 de-scope 基线：职责边界·无向后兼容·预算铁律

flightdeck 3.0 是**格式基线第 0 版**。本篇记录这一版**蓄意的设计边界**——哪些机制被刻意排除、校验归谁、热/冷路径如何分工。不变约束：核心卖点「随时可关、下次干净接手、上下文不丢」零损失——真正神圣的只有 cockpit + INDEX 的恢复载荷。

## 无向后兼容子系统（阶段性）

3.0 的格式**就是**格式。flightdeck 不为任何「老 deck」做检测/迁移/版本校验——没有 layout verdict、没有 MIGRATION 迁移逻辑、没有 legacy 路径探测。`flightdeck_index.py` 不含 `layout_verdict` / `version_mismatch` 等函数，也无 `--verdict` 子命令。

**这是阶段性策略，非永恒教条**：一旦 3.0 被真实使用，3.1 立刻就有「老 deck」，届时**再就地建 3.0→3.1 迁移**（为真实存在的旧格式而建，不预先投机）。`rules.md` 保留极简 `version: 3.0` 单行戳——这是**蓄意留下的 3.1 迁移识别锚点**，不是 verdict 输入。后续执行者勿把「无向后兼容」误读成长期原则。

**保留、勿误伤**：`scripts/bump_version.py` + `checklists/version-bump.md` 是**发布管线**（bump 工具版本号 / CHANGELOG / 各 host manifest），与 deck 校验正交；`verify` 待验证标记、`match_signature` 签名指纹都留。

## 校验单一归宿 = walkaround

「校验」（跨版本兼容验证 **+** 本版内结构完整性审查：INDEX↔folder、孤儿 plan、死链、status 合法性、cockpit `## In Progress` AUTO 一致、stray 文件、AGENTS.md drift）**只许活在按需跑的 walkaround**。

- **preflight = 纯读 + 报告，零写入**：读 cockpit + INDEX + folder INDEX（只显计数）+ `--verify-pending` 扫描 + 报下一步。不翻 stale、不 advance 锚点、不做补偿检查。
- **landing = 核心仪式**：分类知识、重生成变动 INDEX、回写 cockpit、堵 hanging task、轻量 smoke、本地 commit（push 先问）。**保留** `applies_to` 路径重叠触发的 stale 保鲜翻转（判为知识保鲜，非版本校验），收敛为 landing 退场单仪式。
- **walkaround = 唯一校验之家**（按需跑）：只审不修，浮出漂移 → 修复路径 = 确定性 regen（landing 或 `flightdeck_index.py <deck>`），不在 walkaround 内改。

> `verify` 待验证标记**不算校验**（工件级，留）。**描述**校验可写在 protocol 等冷路径供阅读；**执行**校验只在 walkaround——二者不冲突。

**stale 翻转是机械的、不读 doc 全文**：触发 = `--changed-since-anchor` 的变更路径 ∩ 知识件 `applies_to` 中的路径条目（含 `/` 者，前缀匹配；纯词标签只做路由），确定性比对。`when_to_update` 是给人看的**理由**，非运行时求值的条件表达式。stale 是**非阻塞元数据**——黄灯提醒，不进恢复载荷 / 排序 / 过滤；「从不 landing」至多漏一个黄灯软信号，漏它 ≠ 上下文损失（「上下文不丢」指 cockpit+INDEX 恢复载荷，不含 stale 信号）。

## 假定 deck 良构（不防御性检查）

`/launch` 从 `scaffolds/full/` 整包复制，合法 deck 必带齐文件/文件夹。preflight + landing **不做 within-deck 存在性检查**；文件缺了 = 用户责任，由 walkaround 审查或自然报错暴露（自然报错 = 缺前提，**不算校验**）。唯一例外：preflight 顶层一句「这目录没有 deck → 跑 `/flightdeck:launch`」——这是**入场前置 / onboarding**（答「此处是否 flightdeck 语境」），非被删的 within-deck 防御。

## 热/冷路径预算铁律（防再膨胀）

永远/经常载入的表面（注入 directive、每个 `SKILL.md`）只放**最小祈使式清单**；解释 / 边角 / why / edge-case 一律下沉到按需读的冷路径（`protocol.md` 等）。冷路径文件**同样设字符上限**——否则砍掉的散文只是从热路径流到冷路径。cockpit 的 `## Next` / `## Key Context` 设**软上限**（= 触发复核的警戒线，**非**自动截断；与「cockpit 语义神圣不动」不冲突——后者指角色/结构不变，前者只是膨胀预警），防被砍内容回灌让成本反弹。

## incidents：吸纳即退役

incident 教训一旦**吸纳进权威 skill/protocol 本体**（设计上防再犯）即退役：过时的删，活的翻 `obsolete` 退出 AUTO 路由、留盘可 grep 防回归。吸纳形式二分：

- **可设计防范**——坑能被结构性消除（脚本守卫 / scaffold 修正 / 确定性判据）→ 改设计 + 退役。
- **仅可警示**的环境/工具 gotcha（无法从设计上根除）→ 把警示放进该命令**必经路径**会被读到的权威件。「会被读到」的客观判据：(a) 热路径技能的祈使必经步，或 (b) 对应命令必读的 protocol 章节——塞进没人翻的 appendix **不算**。为遵热路径预算，warn-only 教训默认落冷路径 protocol 对应章节。

既不可设计防范、又无合适必经落点的 gotcha → **不退役，留作活跃 incident**（预期少数）。

## 治理取舍（明示）

3.0 **接受完整性问题的发现延迟**，以此换热路径成本下降。**良构性由工具链（`flightdeck_index.py`）+ walkaround 保证，不由运行时（preflight/landing）保证**。代价：长期不跑 walkaround，结构漂移 / 孤儿 / 死链会滞留——这是**自觉取舍，非疏漏**。

## 自治交互边界（act-report-close loop）

3.0 把「AI 操作」定为：**可逆 deck 动作无确认门、自动执行**；外发 / 不可逆（push / 发布 / 调外部服务）**仍先问**——「可逆=自动、外发=先问」是不可关的内置红线，不再是开关。散落的 per-action 确认门删除（promotion / advance / status-apply / retire），代之以**一个统一「翻回」通道**（撤销最近一个着陆单元，从 git + 看板推导，跨会话可恢复）。

- **统一输出格式**：所有 flow 回合 = 先正文 → 末尾一个标准 banner（`─── <icon> <flow> ───`），恒在最后、一回合一个；执行回合无增量也出 `[No change]`（替代旧 print-nothing 静默；纯对话不出）。
- **零损失的范围**（防过度承诺）：「随时可关、恢复零损失」**专指恢复载荷 = cockpit + INDEX + 已落盘工件**，**不含未落盘的对话推理**；长 brainstorm 靠「边定边落」缩小丢失面。
- **preflight 纯读零写不变**：恢复（读 cockpit+INDEX）与「翻回」（用户主动触发、可读 git）是两个不同操作，前者只读看板。
- **配置面 AI-authored**（ai-authored-config spec）：删人工 magic-string 开关目录 + resolution-order 匹配机器；`rules.md` `### Autonomy overrides`→`### Rules` 由 AI 按用户自然话落盘自由文规则，授权序 `CLAUDE.md > deck ### Rules > 默认`；保留 `version:3.0` + 环境推断（git/emit）+ 内置默认。

完整运行契约（可逆判据表 / banner 字段 / 翻回 / 阶段派生 / 生命周期恢复）的**单一真相源**是 `skills/preflight/protocol.md` § Act-report-close loop；本节只记 de-scope 边界。设计稿 `specs/`（archive 后）`2026-06-16-act-report-close-loop`。
