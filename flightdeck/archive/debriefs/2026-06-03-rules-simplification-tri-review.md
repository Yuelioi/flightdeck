---
status: active
reviewed: landed/specs/2026-06-03-rules-simplification-design.md
last_updated: 2026-06-03
---

# rules.md 简化 — 三方评审（Claude / DeepSeek / GPT）

**Date**: 2026-06-03
**Reviewer**: Claude · DeepSeek · GPT（三个外部模型独立评审）
**Reviewed**: [specs/2026-06-03-rules-simplification-design.md](../specs/2026-06-03-rules-simplification-design.md)

## Raw feedback

（摘录自 `debriefs/claude.txt` / `ds.txt` / `gpt.txt`；三份原始 txt 已合并入本文件并删除。）

### Claude
- 🔴 "prose 覆盖可靠性"被低估：把结构化 gate（model_invocable）换成自然语言解析、每个 skill 独立"认出"prose，是整个方案最薄弱点；`### 行为覆盖` 是"可选习惯"却被解析逻辑"依赖"——矛盾。建议升为必须的结构化小节，或保留 model_invocable 结构化形式只移进 House Rules 块。
- 🔴 "失去确定性 STOP"的兜底不完整：§8 的"逐一核对内层 confirm 门"没进 P1–P5；应列为 P2 前置条件。
- 🟡 git 推断边界：repo 内但不想走 git 的情形 + "House Rules 覆盖"的优先级/语法/读取时机没写清，需进 protocol。
- 🟡 signal 1 "刚"的定义模糊：哪个时间点触发？边沿触发在 stateless skill 怎么实现、幂等重跑会否重复？
- 🟡 emit 不对称（只有显式命令能 bootstrap AGENTS.md）需在 templates 明说。
- 🟢 §3 安全论证读起来像已确认的事实，应标"待验证"。
- 🟢 迁移表 `emit_agents_md:false` 那条有逻辑缺口（有 AGENTS.md 但不想被动）。
- 🟢 版本号同意 3.0。

### DeepSeek
- 总评：通过（有条件）。git/emit 推断 + 删 disabled_gates 零摩擦赞成；autonomy 三件套去结构化方向对，但 prose 识别是最大工程挑战。
- 需补：① 无 git 时 "repo root" 定义缺失（建议 deck root = 含 rules.md 的目录 / 最近 flightdeck/ 父目录，回退 cwd）；② House Rules 行为覆盖识别协议必须硬指定（固定句式 + 精确子串/正则，或允许 `### 行为覆盖` 内极简标记 `commit: auto`）；③ model_invocable 溶解前的内层确认门清单需显式列出；④ git 推断被 House Rules 覆盖的优先级要写死（先读覆盖、否则推断）。
- N=5 写死可接受，建议加一句未来可自适应以闭口。版本号支持 3.0、旧 key 兼容到下个 minor 后移除。

### GPT
- 把配置分三类：环境事实（git/emit）→推断；行为策略（commit/model_invocable/status_auto）→House Rules；功能禁用（disabled_folders）→结构化。分层对。
- git/emit 推断、删 disabled_gates、autonomy 三件套合并、House Rules 权威顺序、when-to-land：均"应该做"。
- 建议保留概念名 **Autonomy Policy**，House Rules 用 `### 项目约定` / `### 行为覆盖` 两小节（非强制解析，给稳定模式）。
- model_invocable 删除前必须做"独立确认门"审计表；缺确认且可改文件者不可删。
- 迁移生成的 prose 应带 `<!-- migrated from ... -->` 注释。
- 版本号 3.0；旧 schema 兼容读保持整个 3.x，4.0 删除。

## Disposition（每条一个标签）

1. **[adopt]** 内层 confirm 门审计升为 **P2 前置条件** + 显式清单（landing 移文件 / commit / migration 改写 / archive / status 副作用 / emit 覆盖写 / scaffold 改写）；缺门且可改文件的动作不得仅靠 House Rules 承接 — 写入 spec §3 + 实施分期。
2. **[adopt]** git 推断 vs House Rules 覆盖**执行顺序写死**：先读 House Rules 的 git 覆盖，有则用、跳过 `.git` 检测；否则推断 — 写入 spec §2 + protocol。
3. **[adopt]** 无 git 时 **deck root 定义**：含 `rules.md` 的目录（flightdeck/ 父目录），AGENTS.md 落该 root，回退 cwd — spec §2。
4. **[adopt]** signal 1 **边沿触发澄清**：提示就在 status 执行翻转的**同一次调用**里搭出；status 只在真翻转时动（否则 no-op），故"边沿"=翻转动作本身、无需存状态；幂等重跑遇已 done → no-op → 不再响 — spec §5。
5. **[adopt]** 迁移表缺口：`emit_agents_md:false` 且**有 AGENTS.md** → 译成 House Rule"有 AGENTS.md 但不要自动 regen"，不可直接丢 — spec §6。
6. **[adopt]** 版本号 **3.0**（schema 破坏，比 2.4 诚实）— spec §6/§8。
7. **[adopt]** 兼容旧 key **整个 3.x 保持读，4.0 删除**（取 GPT 的平滑路线，覆盖 DS 的"下个 minor 删"）— spec §6/§8。
8. **[adopt]** §3 安全论证标注 **"(待 P2 前核对确认)"** — spec §3。
9. **[adopt]** 迁移生成的 prose 带 `<!-- migrated from X -->` 来源注释 — spec §6。
10. **[adopt]** emit 不对称（只有显式命令能 bootstrap AGENTS.md）写进 templates.md — spec §2/§7。
11. **[adopt]** N=5 加一句闭口（小 deck 永不触发但紧迫性也低；未来可自适应，当前无必要）— spec §5。
12. **[adopt]** House Rules 行为覆盖**确定性识别 = 穿针版**（用户拍板）：迁移生成用**固定标准句式**（翻译表那几句为"标准措辞"），skill 对其**宽松子串匹配**；手写也认但推荐标准句。**非新增 YAML toggle**。同时修正 spec 的"可选 vs 依赖"矛盾。配合 GPT 的 `### 项目约定` / `### 行为覆盖` 两小节 + 概念名 Autonomy Policy — spec §4。
13. **[reject]** Claude 的备选"保留 model_invocable 结构化形式、移进 House Rules 块" / DS 的 `commit: auto` 极简标记 → 不采。理由：用户早先已否掉"在 prose 里重新长出配置"（option C 全量版）；穿针版（#12）已用"标准句式 + 宽松匹配"取得确定性而**不**引入结构化字段，足够。
14. **[defer]** 无 git 下 `landed/HISTORY.md` 维护规范（各 skill 改写格式）→ 不阻塞本设计，收进 spec §8 开放问题，writing-plans 阶段排期。

## Round 2 — 修订版复审

三方均"批准推进 writing-plans"；上轮补丁确认落地。新增点（摘录 `claude.txt`/`ds.txt`/`gpt.txt` 第二轮，原始 txt 已并入并删除）：

15. **[adopt]** 标准句匹配规则 / 词表**集中进 protocol.md 单一真相源**（命名 "Rule resolution order" + 标准句表），各 skill **引用**而非各自硬编码，防词表漂移（Claude/GPT）— spec §4。
16. **[adopt]** `### 行为覆盖` **标题字面量写死**于 protocol；skill 优先在该字面量段按标准句抓取（DS）— spec §4。
17. **[adopt]** 子串匹配**跳过 HTML 注释行**（防 `<!-- migrated from commit_mode:auto -->` 被误匹配）；可选 preflight 提示"有 N 条已确认迁移注释可清理"（Claude）— spec §4/§6。
18. **[adopt]** **P4 依赖 P3**（`### 行为覆盖` 结构/模板须先于迁移生成到位）（Claude）— spec 分期。
19. **[adopt]** §3 审计表改按**副作用维度**（写文件 / 删除 / 移动 / 已确认）而非 ritual 名；并写明**审计方法**（逐条在 scaffold/skill 代码找 write/move/delete，确认有无 confirm 分支）（GPT/Claude）— spec §3。
20. **[adopt]** scaffold 若审计无门，两出口：给 scaffold 加 confirm，或**局部保留 `model_invocable` 对该单一动作的结构化 gate**（既有字段子集，不算新 toggle）（DS）— spec §3。
21. **[adopt]** signal 2 作为 preflight **最后一行 / 单独 `## Land-readiness` 小节**，不插在主输出中间（Claude）— spec §5。
22. **[adopt]** deck root **回退 cwd 时附警告**，不静默（Claude）— spec §2。
23. **[adopt]** emit `false` 且**无** AGENTS.md → 静默丢弃是**预期行为**，实施卡注明"非遗漏 bug"（DS）— spec §6。
24. **[adopt]** no-git 关 signal 2 时留路标注释："未来可用 `landed/HISTORY.md` 修改时间/行数增长替代"（DS）— spec §5。
25. **[reject]** GPT 提议的 House Rules **内部冲突自动解析**（警告 + 最后匹配项生效）。**用户行内批注明确不同意（"应该用户负责"）**：House Rules 内部一致性是**用户责任**，设计**不**定自动解析语义；skill 至多被动提示明显矛盾，绝不静默择一。
26. **[adopt]** 迁移 `<!-- migrated from -->` 注释**实现时不得删**（溯源价值；重申 #9）（GPT）— spec §6 已含。
