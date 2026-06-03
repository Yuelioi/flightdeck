---
status: active
reviewed: specs/2026-06-02-workflow-artifact-frontmatter-enrichment-design.md
last_updated: 2026-06-02
---

# workflow frontmatter enrichment — 三方 AI review (claude / ds / gpt)

**Date**: 2026-06-02
**Reviewer**: Claude · DeepSeek(ds) · GPT —— 三方独立审同一份 spec
**Reviewed**: [specs/2026-06-02-workflow-artifact-frontmatter-enrichment-design.md](../specs/2026-06-02-workflow-artifact-frontmatter-enrichment-design.md)

## Raw feedback

（下为三份原始 drop 的忠实浓缩；原始无后缀文件 `claude`/`ds`/`gpt` 已折叠进本 debrief 后删除。）

### Claude
1. `summary` 权威源有实践漏洞：人工维护会滞后，INDEX 忠实反映过期摘要，反比"人写 INDEX 行"更难发现 drift → 把 `summary` 与 `last_updated` 绑同一 bump 触发点。
2. `superseded_by` 回填违反自己"不手维护两头"原则 → 砍掉,只留 `supersedes`,反向 grep 派生。
3. `related` 语义边界没定义,兜底桶 → 给操作性定义或暂不引入。
4. blast radius 漏了 `status` 技能:它也写 INDEX 行,若 INDEX 改为从 `summary` 派生,status 的 INDEX 写入须从一开始就读 `summary`。
5. walkaround "Audit 3 扩到 spec" 语焉不详；若砍 `superseded_by` 此条可删。
6. 措辞:§3 "总共没几个" 随意且易过期 → 删量化。
结论:核心设计合理;必须处理 #2(矛盾)与 #4(实现顺序依赖)。

### DeepSeek (ds)
1. 同 claude #2:"只存正向" vs "可选回填 superseded_by" 矛盾 → 路径A彻底砍 / 路径B定义为只读自动派生缓存(不可手编);不自动化则暂不引入。立即收口。
2. `last_updated` 更新责任完全缺失 → 必须指定自动锚点(status 翻状态 / landing 归档),否则沦为 git log 低效副本。
3. `summary` 格式约束缺位:自由文本含 `|`/`[`/`]`/换行会破坏 INDEX 生成 → 约束单行纯文本 + 转义兜底。
4. 关系边路径在 landed 后稳定性未讨论:`supersedes: specs/old.md` 在 old 归档后断 → 方案A(landing 自动改路径,小规模可行) / 方案B(接受断裂 + walkaround 软检查)。建议至少明确立场。
5. blast radius 缺具体改动点(所有重建 INDEX 的代码点)。
6. 微妙场景:active spec 被 active spec supersedes,旧 spec 状态是否自动翻?设计选择不自动碰 status(只前进不后退),正确,建议补进验证场景。
结论:#1、#2 是进实现前必须解决的逻辑缺口,其余建议性。

### GPT
APPROVE。做:`summary`/`last_updated`/`supersedes`/`related`(补 workflow 数据模型,长期收益高)。
Required change: **remove `superseded_by`**(唯一要砍的;`supersedes` 已够,反向 grep 派生,否则必出现"哪个是真相")。
Recommended: 明确 `last_updated` 归属(手动 vs 自动 bump);倾向自动 bump(机械信息,纯手动半年后必腐化)。`summary` 强烈推荐、`last_updated` 直接自动维护。blast radius "workflow 不强制这些字段" 是对的,否则 walkaround 瞬间炸历史库。

## Disposition（每点一个 tag）

1. **[adopt]** 砍 `superseded_by`(三方一致 required) —— 只留 `supersedes` 正向边,反向 `grep supersedes:` 派生。已改 §2.3。
2. **[adopt]** `last_updated` 自动 bump(ds #2 / gpt / claude #1) —— 锚点 `status` 翻状态 + `landing` 归档;模型自调 status 时由 status 负责写。已改 §2.2。**用户确认:自动 bump（推荐项）。**
3. **[adopt]** `summary`+`last_updated` 绑同一「实质变化」触发点防 drift(claude #1)。已改 §2.1/§2.2。
4. **[adopt]** `summary` 单行纯文本格式约束 + INDEX `|` 转义兜底(ds #3)。已改 §2.1。
5. **[adopt]** 关系边路径稳定性:landing 归档时自动改写指向被归档文件的 `supersedes`/`related` 为 `landed/` 前缀(ds #4)。已改 §2.3 + §4。**用户确认:landing 自动改路径（推荐项）。**
6. **[adopt]** `related` 保留 + 加操作性定义(claude #3 / gpt):非取代非实现的弱关联(共同前提/影响面)。已改 §2.3。**用户确认:保留 + 定义（推荐项）。**
7. **[adopt]** blast radius 补 `status` 技能实现顺序:其 INDEX 单行写入须从一开始读 `summary`,不回头改(claude #4 / ds #5)。已改 §4。
8. **[adopt]** 砍 walkaround "Audit 3 扩到 spec",改为可选断边软检查 INFO(claude #5,随 #1 砍 superseded_by 而失效)。已改 §4。
9. **[adopt]** 验证场景:active spec 被 active spec supersedes 时不自动翻旧 spec status(ds #6)。已补 §2.3 注意块。
10. **[adopt]** 删 §3 "总共没几个" 量化措辞,改"实现时一并回填"(claude #6)。已改 §3。
11. **[reject]** ds #1 路径B(`superseded_by` 作只读自动派生缓存) —— 与 #1 决定一致选路径A(彻底砍),不引入缓存字段,避免任何持久化反向边。理由:flightdeck 规模下 grep 派生足够,缓存只增不减复杂度。
