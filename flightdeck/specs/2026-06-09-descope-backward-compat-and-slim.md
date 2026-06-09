---
status: active
summary: 3.0 定为格式基线第0版：砍掉整个向后兼容/迁移/版本校验子系统（layout verdict/MIGRATION 迁移/legacy 路径全删，3.1 再就地建迁移）；校验只许活在按需跑的 walkaround，preflight 退化纯读零写、landing 仅核心仪式；assume 良构 deck 不做防御性存在检查；incidents 教训吸纳进权威件后退役清理；热/冷路径预算铁律防再膨胀——根治 preflight 固定成本，上下文不丢零损失
last_updated: 2026-06-09
graduate: true
---

# flightdeck 3.0 大瘦身 / de-scope

## 一句话

3.0 定为格式基线**第 0 版**：**砍掉整个向后兼容/迁移/版本校验子系统**；**校验只许活在按需跑的 walkaround**，preflight + landing 退化为纯核心动作；assume 良构 deck、不做防御性存在检查；incidents 教训吸纳进权威件后退役清理；热/冷路径散文按预算瘦身。目标——大幅压低**每会话固定成本**与**单次 /preflight 成本**，且「上下文不丢 / 干净接手」**零损失**。

## 背景 / 动机

flightdeck 的核心卖点是「随时可关对话、下次 preflight 干净接手、上下文不丢」。但系统在迭代中长出了大量**散文 + 防御逻辑 + 向后兼容机制**，token 成本失控：一次 `/flightdeck:preflight` 实测吃 ~9k token，且每个会话开局还有固定注入成本。

实测成本分布（字符数 → token 代理，deck 中文为主 ~1.5–2 字符/token）：

- **永远在场（每会话注入）**：takeover directive + cockpit 锚点 ≈ 7k 字符 ≈ 3–4k token。
- **跑 /preflight 时**：`preflight/SKILL.md` 正文 = 13.5k 字符 ≈ 5–7k token（单笔最大头，且是给 AI 看的操作手册散文，**不是**用户数据）；cockpit + 6 个 INDEX 读取 = 11.2k 字符 ≈ ~5k token（这才是「可恢复上下文」真载荷）；外加 step 4a stale 检查逼读的 2 个 doc 全文。
- **按需才载入但巨大**：`protocol.md` 53.5k 字符、`exit-ritual.md` 44k、`walkaround/SKILL.md` 233 行。

关键洞察：**最大且最安全可砍的是 skill 正文散文 + 防御/兼容机制**，砍它们**完全不伤**「上下文不丢」——真正神圣的只有 cockpit + INDEX 那 ~5k 恢复载荷。

de-scope 比单纯压缩散文更狠也更对：flightdeck **尚未发布、世上没有任何老版本 deck**，却背着一整套伺候老 deck 的迁移/校验机制——这是为不存在的兼容负担背死重。

## 政策与原则（本 spec 立的规矩）

1. **无向后兼容（3.0 = 第 0 版，阶段性）**：3.0 的格式**就是**格式，到此为止。不为任何「老 deck」做检测/迁移/校验。等 3.1 真改格式时，**再就地建 3.0→3.1 迁移**（届时为真实存在的旧格式而建，不预先投机）。**这是阶段性策略，非永恒教条**——一旦 3.0 被真实使用，3.1 立刻就有「老 deck」；保留 `version: 3.0` 戳正是**蓄意留下的 3.1 迁移识别锚点**（最小元数据，让未来迁移认出起点）。后续执行者勿把「无向后兼容」误读成长期原则。
2. **校验单一归宿 = walkaround**：一切「校验」只许活在 walkaround（按需才跑、不压热路径）。**preflight + landing 一点校验都不沾**。「校验」= 跨版本兼容验证 **+** 本版内结构完整性审查（INDEX↔folder、孤儿、死链、status 合法性）。**不**含 `verify` 待验证标记（工件级，留）。（**描述**校验可写在 protocol 等冷路径文档供阅读；**执行**校验只在 walkaround——二者不冲突。）
3. **热路径只放祈使清单**：永远/经常载入的表面（注入 directive、每个 `SKILL.md`）只放最小祈使式清单；解释 / 边角 / why / edge-case 一律下沉到**按需读**的 `protocol.md` 等冷路径文件。
4. **假定 deck 良构**：`/launch` 从 `scaffolds/full/` 整包复制，合法 deck 必带齐文件/文件夹。preflight + landing **不做 within-deck 防御性存在检查**；文件缺了 = 用户责任，由 walkaround 或自然报错暴露。
5. **错题本吸纳即退役**：incident 的教训一旦**吸纳进权威 skill/protocol 本体**（设计上防再犯），该 incident 即退役（过时的删、活的翻 `obsolete` 退出路由、留盘可 grep 防回归）。

**治理取舍（明示，回应评审）**：3.0 **接受完整性问题的发现延迟**，以此换热路径成本下降。**良构性由工具链（`flightdeck_index.py`）+ walkaround 保证，不由运行时（preflight/landing）保证**；运行时读到缺失文件时**自然报错**——这**不算「校验」**（校验 = 主动完整性审查，只在 walkaround；自然报错只是缺前提）。walkaround **只审不修**：浮出漂移（如 `## 进行中` AUTO 不一致），**修复路径 = 确定性 regen**（landing 或 `flightdeck_index.py <deck>`），不在 walkaround 内改。代价：长期不跑 walkaround，结构漂移/孤儿/死链会滞留——这是**自觉取舍，非疏漏**。

## 第 1 节：砍掉向后兼容子系统

**删**（实测删除面）：

- `scripts/flightdeck_index.py`：`layout_verdict` / `_classify_version` / `_structural_signal` / `_vtuple` / `_migration_layout` / `version_mismatch` 全套函数 + `--verdict` 子命令（约 180 行，第 333–516 区段）。
- legacy 路径探测（`charts→references` / `landed→archive` 重命名识别）、pre-3.0 key「读-忽略」处理 —— 全删（没有老 deck）。
- `walkaround/SKILL.md` 中的 migration 审查 / layout-version 审查 / version-bump 提示（实测 20 处 verdict/migration refs）。
- `preflight/protocol.md`（19 处）、`preflight/SKILL.md`（step 1 verdict + step 4 version note）、`templates.md`（MIGRATION 模板段）中的 verdict/version 散文。
- `MIGRATION.md` 的 verdict/迁移逻辑角色。

**保留（这些**不是** deck 校验，勿误伤）**：

- `scripts/bump_version.py` + `checklists/version-bump.md` = **发布管线**（发 3.0 时 bump 工具版本号 / CHANGELOG / 各 host manifest），与 deck 校验正交，留。
- `rules.md` 的 `version:` + `MIGRATION.md` → 降为**极简单行版本戳**（`version: 3.0`，给未来 3.1 迁移认起点），删掉所有读它做 verdict 的逻辑。
- `verify` 待验证标记（工件级）、`match_signature` / 签名指纹（incident 回归检测）—— 都留。

## 第 2 节：命令职责重划 —— 校验只在 walkaround

- **preflight = 纯读 + 报告（零写入）**。删 step 1 verdict、step 4 version note、**整块 step 4a 补偿检查**（stale 补偿 / graduate 补偿 / obsolete 提醒——正是逼 AI 读 doc 全文的元凶）。放弃「唯一允许的写」，preflight 不再翻 stale、不再 advance 锚点。preflight 收敛为：读 cockpit + INDEX + folder INDEX（只显计数）+ `--verify-pending` 扫描 + 报下一步。**这一刀直接根治 ~9k。**
- **landing = 核心仪式**：分类知识、重生成变动 INDEX、回写 cockpit、堵 hanging task、轻量 smoke、本地 commit（push 先问）。不碰 version / verdict / migration。**保留** landing 的 `when_to_update → stale` 知识保鲜翻转——判定其为「知识保鲜」非「版本校验」，且每回合 Stop hook 跑，是退场仪式的自然位置。stale 翻转由双仪式收敛为**单仪式**（只在 landing 退场翻；preflight 入场半边删除）。**关键澄清——stale 翻转是机械的、不读 doc 全文**：其触发是**路径重叠**——`--changed-since-anchor` 的变更路径 ∩ 该知识件声明的源路径（`applies_to`），确定性比对，**不读 doc 全文**；`when_to_update` 是给人看的**理由**，非运行时求值的条件表达式。preflight 旧 step 4a 之所以贵，正是它误把这个「路径机械比对」做成了「读全文语义判断该不该 stale」——本 spec 删的是那个**误用**，不是保鲜本身；因此 landing 接手 stale **不会**继承 4a 的膨胀。**收敛路径**：stale 主翻转 = landing（每回合 soft-land 退场）；walkaround 按需兜底重扫（**审/重算，非例行仪式**）。**边界**：`stale` 是**非阻塞元数据，不参与恢复载荷计算**——黄灯提醒而已，不进排序/优先级/过滤；故退化案例「从不 landing」至多漏一个黄灯软信号，**漏它 ≠ 上下文损失**（「上下文不丢」指 cockpit+INDEX 恢复载荷，不含 stale 信号）。
- **walkaround = 唯一校验之家**（按需跑）：保留本版内完整性审查（INDEX↔folder 一致、孤儿 plan、死链、status 合法性、cockpit `## 进行中` AUTO 一致、stray 文件、AGENTS.md drift、done-but-unlanded INFO 等），**删掉**其中的 migration / verdict / legacy / version 部分。存在性/一致性检查在 walkaround 是**有意的审查职责**，不是防御性兜底。233 行预计大幅瘦。

## 第 3 节：incidents 吸纳 → 退役 → 清理

逐条 triage（实施时在 plan 内逐文件判定）：

- **过时**（讲的是本 spec 已删除的机制，如 verdict/migration/legacy 相关）→ **直接删**。
- **活 gotcha**（如 `windows-python-stub-board-sync-noop` / `powershell-herestring-in-bash-tool` / `git-add-partial-stages-renamed-modified-file` / `scaffold-ships-verbatim` / `skill-prose-links-into-dogfood-deck` / `index-row-summary-delimiter` 等）→ 教训**吸纳进权威 skill/protocol 本体**（让坑从设计上不可能再犯）→ 该 incident 翻 `obsolete` → landing 排进 `archive/`（退出 AUTO 路由、留盘可 grep 防回归）。

**吸纳形式分两类（triage 判据，回应「纯环境 gotcha 怎么吸纳」）**：

- **可设计防范**——坑能被结构性消除（脚本加守卫 / scaffold 修正 / 确定性判据）→ 改设计 + 退役。
- **仅可警示**的环境/工具 gotcha（如 `powershell-herestring-in-bash-tool` / `git-add-partial-stages-renamed-modified-file`，无法从设计上根除）→ 吸纳形式 = 把警示放进**该命令必经路径**上会被读到的权威件。**「会被读到」的客观判据**（否则不算吸纳完成，回应评审）：(a) 热路径技能的**祈使必经步**，或 (b) **对应命令必读的 protocol 章节**——塞进没人翻的 appendix **不算**。为遵 原则 3（热路径只放最小祈使清单），warn-only 教训**默认落冷路径 protocol 对应章节**；仅当它在某命令的祈使必经步上，才以**一行祈使**进热路径。退役合法性 = 警示已落到上述位置 → 翻 `obsolete`（留盘 grep 防回归）。**若某 gotcha 既不可设计防范、又无合适必经落点 → 不退役，留作活跃 incident**（预期少数，不与「大幅收缩」矛盾）。

结果：活跃 incidents 从当前 **9 条**大幅收缩，preflight 每次读的 incident INDEX 行数骤降。（正式采纳外部反馈：root-fixed incident 翻 `obsolete` 退出 AUTO 路由。）

## 第 4 节：热/冷预算铁律（防再膨胀）

**铁律**：永远/经常载入的表面只放最小祈使式清单；解释/边角/why 下沉到按需读的冷路径。

**初定预算（可调，实施时校准）**：

- 注入 directive ≤ ~25 行。
- cockpit 锚点只投影 `## 下一步` + `## 关键上下文`（不投全 `Active focus` 长段）。
- `preflight/SKILL.md` ≤ ~40 行（纯读+报告，自然就短）。
- 其余各 `SKILL.md` 各定行数上限（实施时定）。

每相位报 before/after 字符数（token 代理，`wc -m`）。

**冷路径也设预算**（回应「冷路径无预算会回流再膨胀」）：`protocol.md` / `exit-ritual.md` / `walkaround/SKILL.md` 等冷路径文件同样设字符上限（plan 定具体数值）——否则被砍的散文只是从热路径流到冷路径。**恢复载荷设软上限**：cockpit 的 `## 下一步` / `## 关键上下文` 设软上限，**防被砍内容回灌进 cockpit/INDEX 让成本反弹**（cockpit 神圣 = 语义不动，**不等于**可无限增长）。**软上限 = 触发复核的警戒线**（超 → 提示精简），**非自动截断**——与「语义不动」不冲突（后者指角色/结构不变，前者只是膨胀预警）。

## 第 5 节：假定 deck 良构（不防御性检查）

- **preflight + landing 不做 within-deck 存在性检查**：删 `rules.md "if present"`、`folder-missing 当空`兜底、malformed-file verdict 处理等一切「万一不在」的防御分支。
- **保留** preflight 顶层一句「这目录没有 deck → 去跑 `/flightdeck:launch`」：这是**入场前置**（答「此处是否 flightdeck 语境、有无 deck 可读」），**不是被删的 within-deck 完整性防御**；onboarding 性质，成本 <1 行。其余 within-deck 检查全删。
- walkaround 的存在性/一致性检查作为**审查职责**保留。

## 非目标（这轮不做）

- 不动 cockpit + INDEX 的恢复载荷语义（那是「上下文不丢」的真核，神圣）。
- 不**公开发布** 3.0（完善优先，避免迁移债）。注：「格式基线 / 第 0 版」是**内部设计冻结**（dogfood + 未来 3.1 起点），与「暂不公开发布」不冲突——基线是设计决定，发布是公开动作。
- 不重写 hook 机制（仅按预算压注入 directive 文案）。
- 不碰 `verify` 非阻塞验证特性（工件级，正交）。
- 不预建 3.0→3.1 迁移（等真有 3.1 格式变更再就地建）。

## 微决策落定（已与用户确认）

1. 留极简 `version: 3.0` 单行戳（给 3.1 认起点），删所有读它做 verdict 的逻辑。✅
2. 留发布管线（`bump_version.py` + `version-bump.md`），与 deck 校验正交。✅
3. landing 的 stale 保鲜翻转判为「非校验」，留 landing；删 preflight 入场补偿半边 → stale 单仪式。✅
4. preflight 彻底只读、零写入（放弃唯一允许的写）。✅
5. 留 preflight 顶层 deckless→/launch 一行；其余 within-deck 检查全删。✅

## 实施大纲（交 plan 细化，分相位）

- **相位 1**：删向后兼容子系统——`flightdeck_index.py` 删 verdict/version 函数 + `--verdict` 子命令（TDD：删测试同步）；删 legacy/pre-3.0 处理；`MIGRATION.md`/`rules.md` 降极简版本戳。
- **相位 2**：命令职责重划——preflight 收敛纯读零写（删 step 1/4/4a）；landing 剥离 version/verdict，保留 stale 单仪式；walkaround 删 migration 审查、聚焦本版内完整性。
- **相位 3**：incidents 吸纳-退役——逐条 triage，活 gotcha 吸纳进权威件后翻 `obsolete`，过时的删；landing 排空。
- **相位 4**：热/冷预算扫尾——按预算压注入 directive、cockpit 锚点投影、各 SKILL.md；下沉冷路径细节。
- 每相位：脚本测试绿 + `flightdeck_index.py <deck>`（lint/INDEX）clean + 报 before/after token。

## 验收

**基线（2026-06-09 实测，作验收对照）**：`/flightdeck:preflight` 单次 ≈ **9k token**；`preflight/SKILL.md` **13.5k 字符**；注入 directive + cockpit 锚点 ≈ **7k 字符**；活跃 incidents **9** 条。**测量法**：`wc -m` 字符数作 token 代理（近似——tokenizer 因模型有 ±差异，故验收以**数量级**「下降一半」为准，对该差异稳健），记录每相位 before/after。

- `/flightdeck:preflight` 单次成本较 ≈9k 基线下降**一半量级**（砍 SKILL.md 散文 + step 4a doc 读 + verdict 步）。
- 每会话固定注入成本（directive + cockpit 锚点）较 ≈7k 字符基线下降。
- 全脚本测试绿；`flightdeck_index.py` 全 deck regen / lint clean。
- **行为恢复验收（验业务能力，非字段存在）**：模拟「关闭会话 → 新开会话跑 preflight」，恢复出的工作上下文**足以继续执行 cockpit 指向的下一步**（针对有**非空下一步**的 deck 状态测）——验「能接着干」而非「两个 section 存在」，避免有人砍掉半个 INDEX 仍误过。**失败信号 = 此测不过（客观，即回滚触发条件）**。完整恢复回归自动化测试 = backlog #7（待恢复模型稳定后做；本 spec 至少手测此路径）。
- 向后兼容**逻辑**清零：grep `verdict` / `migrat` / `layout_verdict` / `compatible-behind` 在 skills 热路径 + 已删函数处不再出现。grep 是 sanity-check **非硬门**——发布管线、极简版本戳、历史/测试数据里的合法字面提及不算失败。
- 活跃 incidents 从 9 条显著收缩，无教训在退役时丢失（吸纳进权威件 + 留盘 grep 可验）。

**回滚**：四相位**各自独立 commit**，任一相位若**行为恢复验收失败**（恢复质量回退）即 `git revert` 该相位、重审设计。失败信号 = 行为恢复验收不过，而非主观判断。

## 外部评审纪要（ds / claude / gpt，2026-06-09，仅供参考）

三份外部 AI 评审（不了解项目现状，技术过滤后处置如下）：

**已采纳（折进上文对应节）**：
- *收敛缺口*（三家共提：删 preflight stale 补偿后，若从不 landing 则 stale 永不翻）→ §2 补 stale 机械化澄清 + 收敛路径（soft-land 每回合翻 + walkaround 兜底）+ 退化案例至多漏黄灯软信号。
- *landing 是否继承 4a 膨胀*（claude）→ §2 澄清 stale 翻转只比对 `when_to_update` 一行、不读全文，4a 贵在误用。
- *缺量化基线*（三家）→ 验收补实测基线（9k / 13.5k / 9 条）+ `wc -m` 测量法。
- *吸纳形式对纯环境 gotcha 不清*（claude）→ §3 补吸纳二分类（可设计防范 / 仅可警示）+ 退役合法性判据。
- *无向后兼容是阶段性非永恒 + 3.1 迁移入口*（gpt）→ §1 补阶段性框定 + version 戳 = 蓄意迁移锚点。
- *冷路径无预算 / 恢复载荷可回灌*（gpt）→ §4 补冷路径预算 + cockpit 软上限。
- *行为验收 vs 结构代理*（claude / gpt）→ 验收改行为恢复测试，接 backlog #7。
- *grep 误伤 / 缺回滚*（gpt）→ 验收软化 grep 为逻辑清零 + 补每相位独立 commit 可回滚。

**未采纳（评审缺项目语境）**：
- *graduate:true 与 active「矛盾」*（ds）→ 误解 graduate 语义：它是 active 期可随时设的标记（landing 时改写进 docs），非「已定型」。
- *原则2「校验唯一归宿」与原则5「吸纳进权威本体」冲突*（ds）→ 范畴错误：吸纳的是**教训/警示**，非校验逻辑。
- *存在性检查被连同兼容逻辑误删*（gpt）→ 实为**迁移**到 walkaround（审查职责），非删除；热路径不背损坏检测是用户拍板的取舍。
- *未发布系统 token 验收无效*（ds）→ dogfood：系统正用于自身，成本真实可测。
- *verify-pending「零写入」存疑*（ds）→ verify-pending 是无状态重导出（每次从盘上 `verify:` 字段重算），不写标记。
- *「排空」措辞不可执行*（ds）→ flightdeck 既有术语（drain done/obsolete 进 archive）。

**留给 plan**：各 incident 吸纳的具体落点文件、受影响测试清单、各 SKILL.md / 冷路径预算的具体数值——由 plan 逐条 triage 定。

### 第二轮（ds / gpt 复评，2026-06-09）

gpt 复评结论：「已从激进删减提案变成逻辑自洽、可实施、可回滚的 de-scope spec」，剩余为治理边界/措辞。**已采纳**：① 治理取舍明示（接受发现延迟换热路径成本、良构由工具链+walkaround 保证非运行时）→ 新增「治理取舍」段；② 行为验收改「验能否继续执行下一步」非字段存在 → 验收节；③ `stale` 非阻塞元数据边界（不参与恢复载荷/排序/过滤）→ §2；④ 吸纳完成客观判据（必经路径，非 appendix）+ warn-only 默认落冷路径以遵原则 3 → §3；⑤ 软上限=警戒线非截断、char-proxy 近似按数量级验收 → §4/验收。**ds 增补采纳**：stale 触发为路径重叠（非 `when_to_update` 条件求值）→ §2；deckless=入场前置非 within-deck 防御 → §5；原则 1 标题加「阶段性」；描述校验 vs 执行校验 → 原则 2；「不公开发布」≠ 否定内部格式基线 → 非目标。**仍驳回**：graduate:true 与 active「冲突」（ds 三复仍误解——graduate 是 active 期可随时设的标记、landing 才把本体改写进 docs，spec 在 specs/ 标记它正是为了被 graduate）；dogfood≠发布故验收无效（当前 dogfood 成本真实可测，正是优化标的）。
