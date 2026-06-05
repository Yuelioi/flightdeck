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

- `symptom` 放 AI 实际会看到的字符串（报错原文/异常类名），别写抽象叙事标题。
- 配套：protocol 增一条**命中路径**——"遇到报错，先把原文 grep 进 `incidents/` 看是否已知"。
- 旧 incident 不强制回填，新建/复发触及时补 `## Signature`（渐进迁移）。

## 用 —— 签名指纹精确匹配去重（C1）

recurrence sweep 前置一层**确定性脚本匹配**：

- 脚本读各 incident 的 `## Signature`，对 `symptom`（归一化：去路径/行号/时间戳/hex/随机 id）
  + `error_type` + `where` 算**指纹**（短 hash 或规范串）。
- 新错误：**指纹精确命中 → 确定性判"同一条"**，脚本直接指给 AI（零 AI 判断、零 token、
  零误判）→ append Case + `recurrences +1`。
- **无精确命中 → 落回 AI 模糊层**（applies_to/语义，仍需用户确认，false-positive guard 不变）。
- 落点：`flightdeck_index.py` 加辅助（如 `--match-signature <symptom>` 或一个可被 landing 调用的
  函数），**landing 时跑，不进 preflight**。脚本解析正文 `## Signature` 块（landing 操作读文件
  本就允许，不影响 preflight 路由面）。

## 死 —— 退役机制

- 根因被永久修复（如加了守卫测试）→ 填 `resolved_by: <commit/test 引用>` + 翻
  `status: obsolete`（复用现有 knowledge 状态 active/obsolete/superseded，**不新增状态**）。
- **`obsolete` 从活跃路由退出**：preflight catalog + folder INDEX 的活跃区**排除 obsolete**
  （需核实现状是否已排除；若没有，纳入本 spec 改动）。
- 物理删/归档：见非目标②，交 [scrapped-artifact-disposition](scrapped-artifact-disposition.md) 统一。

## token 账（验证"省token"）

| 改动 | 每会话路由 token |
|---|---|
| Signature 放正文 | 不变（preflight 不读正文）|
| 退役 obsolete 出路由 | 负（路由集随时间缩小）|
| 脚本去重 | landing 省（明显同错不走 AI）+ 防过度分裂导致库膨胀 |

净效果：路由面持平或缩小，命中率与信噪比都升。

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
