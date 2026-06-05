# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-05 by 月离 (本会话：3.0 dogfood item#1 主体过——② preflight 瘦身全过、③ /flightdeck:new fast path 全过、① model-v4 读新 cockpit + active→进行中 投影确认。dogfood 揪出并**修了两缺陷**：A) `skills/new/SKILL.md` kind 表滞后脚本（`chart→references/`、补 `doc→docs/` 行+dateless 规则）+ 加 **SKILL↔脚本 kind 一致性守卫测试**；B) `regen_cockpit_inprogress` 缺 summary 抛 KeyError → 改 `.get` 防御 + 回归测试。新建 incident 记 B。**116 tests 绿**、lint/`--check` 干净。改了 build input → cache 已 stale（戳 `85cf206204ba`），下会话需 reload 才能 live 复验 fallback 修复。随后把 5 组实现完成的 spec+plan（preflight-slim / new-artifact / model-v4 / command-simplify / model-coherence）翻 `done`，连同 scriptable-mechanical-layer 共 **12 文件整簇 land 进 `archive/`**（边图 archivable、改 frontmatter+prose 跨引用），active 区收到只剩 incident-recurrence。  上会话：build-stamp 锚点 + why-no-hooks doc)
**Active focus**: flightdeck 3.0 收尾——所有核心工作（model-v4 / scriptable lint / preflight 瘦身+launch 拆分 / `/flightdeck:new`）已实施 + dogfood + land 归档完毕；**只剩发布**（version-bump + CHANGELOG + marketplace + tag + 合并 main），外加可选的 reload 后 live 复验。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-03-incident-recurrence-autocount-design.md](specs/2026-06-03-incident-recurrence-autocount-design.md) — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
- [2026-06-05-incident-error-library-lifecycle.md](specs/2026-06-05-incident-error-library-lifecycle.md) — 错误库生命周期完善(方向C之Spec1)：生=正文加可grep的 ## Signature 块(symptom/error_type/where/trigger)+分节标准化；用=recurrence sweep 加确定性签名指纹精确匹配去重(脚本算,AI只管模糊层)；死=resolved_by + status:obsolete 从活跃路由退出(物理删/归档交 scrapped-disposition 统一定)。Signature 放正文+退役缩集→省token；B(两层manifest)留作超大deck未来升级备注
<!-- /AUTO -->

## 下一步

- **发布 3.0**：version-bump + CHANGELOG（写 `/flightdeck:launch`、`/flightdeck:new` 两条 + preflight deckless 行为变更 + 本会话两 bugfix）+ marketplace + tag + 合并 → main（见 [checklists/version-bump.md](checklists/version-bump.md)）。
- （可选，非阻塞）sync+reload 后 live 复验：用修后 build 跑 `/flightdeck:new` 各 kind（重点 `doc` 恒-dateless、`chart→references/`）验 fallback 修复；并验 `incident-recurrence`（唯一留 active）的 dogfood 行为 + model-v4 残项（idea→active 实地翻转带动 `## 进行中`、landing 写两区）。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
