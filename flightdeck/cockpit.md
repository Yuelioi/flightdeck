# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-26 · 月离 · 看板精简(砍过期流水账)+ 读头分层特性收尾

Focus: **AI-native 重设 cutover** —— 协议 / 外圈 / repo 清理基本完成,全在 feature 分支 `feat/launch-recorded-config`、**未发版**。本 deck 自身已是新形态(`work/` + `knowledge/`、free-form cockpit、零 INDEX/YAML)。

## In flight

- **work/ai-native-redesign/** —— 重设主 effort;`design.md`(决策单一真相源)+ `coverage-check.md`(3.0→新形态映射)。草稿已 graduate 进 live `skills/`;真相源 = `skills/preflight/{SKILL,operations,concepts}.md` + `skills/walkaround/SKILL.md`。发版后可归档。
- **work/2026-06-22-stage-land-lifecycle.md** —— 旧 stage/land 生命周期设计(轻量单文件;plan 已 done 进冷 archive)。
- **读头分层特性**(本会话,并入 redesign):扫头从「条件兜底」→ 入口默认「先地图后领土」+ 按 READ-WHEN 分层 + 标准档展示(In force / On call)+ 写头提权词表。已落协议(SKILL/operations/README)。曾同步过一次 alpha.4 缓存,**之后又改动 → 缓存现 stale**;待你说「同步」刷成终版,去外部 deck 新会话实测分层手感。

## Next

1. **plan #1 verify(人读)**:新 skills + README×2 英文散文 tone,你来读。
2. **发版(gated,需你批)**:CHANGELOG 补条目 + 版本号 bump(现 `3.0.0-alpha.5`,可能 4.0)+ `git push` —— 三者均需你显式批准(briefing rules)。

## Open questions

- **未发版**:cutover 全在 feature 分支,marketplace 仍是已 ship 的 3.0,直到你显式 bump + release。

## Recent dogfood findings(已修,详见 knowledge/)

[[sibling-workflow-leaves-cockpit-stale]] · [[persist-knowledge-scan-no-heartbeat]] · [[routing-headers-not-resident-at-entry]] · [[reference-project-names-leak-into-commits]] —— 均已落协议加固 + 写成 knowledge,narrative 不再占看板。

## House pointers

配置/约定 → briefing.md · 偏好 → 项目根 CLAUDE.md · 知识 → knowledge/<域> · 冷/归档/idea → ~/.flightdeck

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench — `knowledge/` here documents **maintaining the flightdeck tool**, not using it elsewhere. Users running flightdeck in their own projects see their own deck, not this one.
