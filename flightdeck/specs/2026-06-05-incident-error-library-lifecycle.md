---
status: active
summary: 错误库生命周期完善(方向C之Spec1)：生=正文加可grep的 ## Signature 块(symptom/error_type/where/trigger)+分节标准化；用=recurrence sweep 加确定性签名指纹精确匹配去重(脚本算,AI只管模糊层)；死=resolved_by + status:obsolete 从活跃路由退出(物理删/归档交 scrapped-disposition 统一定)。Signature 放正文+退役缩集→省token；B(两层manifest)留作超大deck未来升级备注
last_updated: 2026-06-05
---

# incident 错误库生命周期——Signature + 签名去重 + 退役

> 来源：2026-06-05 会话，从"怎么让技术文档让 AI 快速定位"讨论收敛而来。原方向 **C**
> 拆成两个 spec，本条是 **Spec 1（错误库生命周期）**；Spec 2（一致性守卫推广：
> 索引↔内容 / 文档↔代码漂移测试）单独走一轮。

## Problem

flightdeck 的 incident 已有 `recurrences` + 三条 promotion gate + `when_to_read/applies_to`
路由，骨架完整，但错误库的"生→用→死"链路有三处缺口：

1. **生（命中率）**：症状只在正文自由叙述（且分节不统一——powershell 那条用
   `**Symptom**`/`**Root cause**`，新建的用 `## 现象/根因/修法`）。AI 下次拿着真实报错
   （如 `KeyError: 'summary'`）去找时，没有稳定、可 grep 的症状锚点。
2. **用（去重）**：recurrence sweep 全靠 AI 比 `applies_to`/根因。明显同错也走 AI 判断
   （耗 token），且签名不规范时易**过度分裂**（同根因反复建新条，复发计数永远到不了
   升级阈值）或**过度合并**（不同根因并成一条）。
3. **死（新陈代谢）**：**完全没有退役机制**。promote 后"Incident kept as the record"永久
   留存，根因已被守卫测试根治的 incident 仍占活跃路由（占 token + 噪声）。

## Goals / 非目标

- 目标：在不增加每会话路由 token 的前提下，提命中率（生）、降去重成本与误判（用）、
  让错误库有新陈代谢（死）。三者服务"完善 / 合理 / 省token"。
- 非目标：① 两层 manifest 路由（方向 B）——留作"超大 deck"未来升级，本 spec 只写备注，
  不实现；② 退役工件的**物理处置**（删 vs 移 archive）——与 [scrapped-artifact-disposition](scrapped-artifact-disposition.md)
  同源，交那条 idea 统一定，本 spec 只负责"退出路由"。

## 核心原则（化解"完善↔省token"矛盾）

> preflight 每会话只加载**路由面**（各 INDEX 行，frontmatter 派生），**不加载正文**。
> 所以：提命中的结构放**正文**（grep / 按需读才触及，常驻零成本）；省 token 做在**路由面
> + 退役**上。两者不打架。

## 生 —— Signature + 正文标准化

incident 正文顶部加一个可 grep 的 `## Signature` 块（**正文，非 frontmatter**），其余分节固化：

```
---
status: active
when_to_read: <场景/动作触发器>
applies_to: [<tag>, ...]
recurrences: 1
resolved_by:                 # 空=未根治；填 commit/test = 退役依据（见「死」）
last_updated: YYYY-MM-DD
---
# <标题，含症状关键词>

## Signature
- symptom: `<报错原文 / 可观测症状>`   # 可 grep —— 命门；key:value 行（脚本要解析）
- error_type: <异常类型/错误码 或 —>
- where: <函数/文件/子系统>
- trigger: <什么动作/场景引发>

## 症状/复现   ## 根因   ## 修法   ## Cases（每复发一行：日期 + 一句）
```

- `symptom` 放 AI 实际会看到的字符串（报错原文/异常类名），别写抽象叙事标题。允许多行
  （堆栈 trace 用缩进或 `|`）——`symptom` 是**人读/grep 锚点**，指纹是从它**计算**出来的
  （见「用」），两个职责分离：作者只写 `symptom`，不手写指纹。
- **`error_type: —` 是一等情形，不是退化**：UI 错位 / 性能退化 / 死锁 / 数据错误等非异常型
  问题没有天然 error_type，此时 incident 自然退化成 `symptom + where`，预期如此。
- **Signature 是硬 schema，只有这 4 个键**（symptom / error_type / where / trigger），它**只为
  grep + 指纹**而存在，**不是通用元数据筐**。新增字段（severity/owner/component/introduced_by…）
  需另开 spec——立此边界，防 Signature 长成"正文里的隐藏版 frontmatter"。
- **Cases**：建 incident 时即写第一行（与 `recurrences: 1` 对应，故 Case 行数 == recurrences）；
  高频条目正文会膨胀，故**只保留最近 N 行 + 总计数**（压缩，N 由 plan 定），AI 打开时不无限长。
- 配套：protocol 增一条**命中路径**——"遇到报错，先把原文 grep 进 `incidents/` 看是否已知"。
- 旧 incident 不强制回填，新建/复发触及时补 `## Signature`（渐进迁移）。

## 用 —— 签名指纹精确匹配去重（C1）

**确定性脚本匹配**作为兜底前置层：

- 脚本读各 incident 的 `## Signature`，对 `symptom`（归一化）+ `error_type` + `where` 算**指纹**。
- 新错误：**指纹精确命中 → 确定性判"同一条"**，脚本直接指给 AI（零 AI 判断、零 token、
  零误判）→ append Case + `recurrences +1`。
- **无精确命中 → 落回 AI 模糊层**（applies_to/语义）。模糊层三出口：确认同一条 / 确认新建 /
  **不确定 → 问用户**（保持当前 false-positive guard，不新增行为）。

**触发时机（关键）**：主触发点是 **AI 准备建 incident 之前**——先 grep/`--match-signature`
查，命中就 append Case 而非新建文件（dedup 的价值在**防**重复，不是事后补救）。**landing 的
recurrence sweep 是兜底**，捞会话中漏查直接建出来的重复。

**确定性层的覆盖边界（诚实声明，别高估）**：
- 只覆盖**同症状同错误**。`KeyError('summary')` vs `Missing field summary` vs `summary not
  found` 根因相同但症状不同 → **指纹命不中，必走 AI 模糊层**。"确定性去重"不等于覆盖大多数。
- `where` 在代码重构时不稳定（`parser.py→loader.py` / `ParseSummary→BuildSummary` 会换指纹，
  同一历史问题被拆成新条）→ 已知局限：指纹以 **symptom + error_type 为主、where 为次/tiebreak**；
  重构导致的拆分由模糊层/人工重新关联。plan 阶段定权重。
- **缺 `## Signature` 的旧 incident**：脚本跳过确定性层，直接走 AI 模糊层（双轨共存，不报错）。

**归一化规则的约束（spec 级，不给完整正则——那是 plan/实现）**：
- 归一化**单独成函数 + 配测试套件 + lint**；脚本**保留原始 `symptom`** 供人工审计。
- 去易变 token：路径（Win/Linux）/行号/时间戳/hex/UUID/数据库主键/JSON path。
- **不得过度归一化**：语义不同的键**不可**并指纹——`KeyError: 'summary'` ≠ `KeyError: 'title'`。
  测试套件须覆盖这类"必须区分"与"必须归并（如 `0x7f3a→0x…`）"的对照样例。
- 落点：`flightdeck_index.py` 加可被 landing/创建前调用的辅助（如 `--match-signature`），**不进
  preflight**；解析正文 `## Signature`（landing/创建时读文件本就允许，不碰路由面）。

## 死 —— 退役机制

- 根因被永久修复（如加了守卫测试）→ 填 `resolved_by` + 翻 `status: obsolete`。
  - **`resolved_by` 格式**：一个**引用**——commit SHA 或 测试 id/路径（如
    `test_flightdeck_index.py::CockpitProjectionRobustnessTest`）。单一约定，便于后续自动化。
  - **退役是一次刻意动作（人/审批 gated，同 done/scrapped）**：填 `resolved_by` + 翻 `obsolete`
    是**同一个有意动作**；landing **不**因 `resolved_by` 非空就自动翻 `obsolete`（避免误退役）。
- **`obsolete` 从活跃路由退出**。**现状（已核实）**：`regen_folder_index` 对 knowledge 文件夹
  列出全部状态，scrapped 排除是 specs 专属——**obsolete 当前不被排除**。故"加排除"是本 spec
  的确定改动（preflight catalog + folder INDEX 活跃区均排除 obsolete），token 账那行据此成立。
- **语义**：此处 `obsolete` = "根因已根治、退出活跃路由、保留作历史记录"，**不是"过时无价值"**。
  复用 obsolete 是为模型一致性（knowledge 状态固定 active/obsolete/superseded，**不新增状态**）；
  命名与含义的落差是已知点，是否改名交 [scrapped-artifact-disposition](scrapped-artifact-disposition.md) 一并定。
- **回归处理（闭环）**：`obsolete` 的 incident 若签名再次精确命中（回滚/新变化致同症状重现）→
  **复活**：翻回 `active`、清空 `resolved_by`、`recurrences` 继续累加、Cases 注明"回归，原根治失效"。
  （不另设"验证期"缓冲——回归复活已提供安全网，YAGNI。）
- 物理删/归档：见非目标②，交 [scrapped-artifact-disposition](scrapped-artifact-disposition.md) 统一。

## token 账（验证"省token"）

| 改动 | 作用域 | token 影响 |
|---|---|---|
| Signature 放正文 | 每会话路由 | 不变（preflight 不读正文）|
| 退役 obsolete 出路由 | 每会话路由 | 负（路由集随时间缩小）|
| 脚本去重（明显同错不走 AI）| landing/建前 | 负（少一次 AI 判断）|
| 脚本去重防过度分裂 | 长期 | 负（库不因重复条目膨胀）|

净效果：每会话路由面持平或缩小；landing/长期 token 下降；命中率与信噪比都升。

## 影响面（待 plan 细化）

- 数据/约定：incident 模板（templates.md）、protocol（命中路径 + 退役语义）、folder-semantics。
- 脚本：`flightdeck_index.py`（签名指纹 + 匹配；obsolete 出路由的 INDEX/计数处理）、可能 lint。
- skill：landing（recurrence sweep 接脚本匹配 + 退役判定）、preflight（catalog 排除 obsolete）、
  `/flightdeck:new`（incident 模板带 `## Signature`/`resolved_by`）。
- 测试：签名归一化 + 指纹匹配、obsolete 出路由、模板一致性。

## 未来升级备注（方向 B，不实现）

deck 真的巨大、路由读取成为瓶颈时，可把路由拆两层：preflight 只读超薄 manifest
（文件 + 一句触发器），完整 INDEX（含 signature/applies_to）按需才读。代价是多一个生成
文件 = 多一处漂移面 + 改 4 skill，当前规模 YAGNI。

## 评审纪要（2026-06-05，3 份外部 AI 评审）

3 份评审（claude/gpt/ds，不了解项目现状，供参考）。已采纳并入上文的：

- **归一化只有举例无规范**（三家共识）→ 「用」加约束（单函数+测试套件+保留原文+"必须区分/必须归并"对照样例）；完整正则留 plan/实现，不进 spec（altitude）。
- **symptom 一字段两职责**（gpt）→ 「生」明确 symptom=人读/grep、指纹=从它计算，作者不手写指纹。
- **同根因不同症状指纹命不中**（gpt）→ 「用」加覆盖边界诚实声明。
- **where 重构不稳定**（gpt）→ 「用」列为已知局限，指纹以 symptom+error_type 为主。
- **dedup 在 landing 太晚**（claude/gpt）→ 「用」改主触发点=建 incident 前，landing 兜底。
- **缺 Signature 的旧条怎么办**（gpt/claude）→ 「用」明确跳过确定性层走模糊层。
- **模糊层"不确定"出口悬空**（claude）→ 「用」补三出口。
- **resolved_by 语义/时机不清**（claude/gpt）→ 「死」定格式（commit SHA/test id）+ 退役=刻意动作、不自动。
- **回归（obsolete 后重现）无路径**（ds/gpt）→ 「死」加回归复活闭环。
- **obsolete 出路由"核实"悬空**（claude/ds）→ 已核实现状=未排除，断言"加排除"为本 spec 改动。
- **Signature 沦为第二套 frontmatter**（gpt）→ 「生」立硬边界=只 4 键。
- **error_type 常缺**（gpt）→ 「生」声明 `—`/symptom-only 为一等情形。
- **Cases 无限增长**（gpt）→ 「生」加压缩（最近 N + 计数）+ 首行建时即写。
- **token 表 脚本去重行混作用域**（claude）→ 拆表加"作用域"列。

**未采纳（项目现状）**：gpt 建议新增 `resolved/historical` 状态——flightdeck knowledge 状态固定
active/obsolete/superseded（一致性，不新增状态）；保留 obsolete + 定义其义，改名问题交
scrapped-disposition。gpt"验证期缓冲"——以回归复活替代，YAGNI。
