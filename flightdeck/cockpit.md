# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-24 · 月离

Focus: **把 AI-native 重设 cutover 到真产品**(本会话从「探索草稿」推进到「真切」)。本 deck 自身已迁到新形态(两目录 work/+knowledge/、free-form cockpit、零 INDEX/YAML)。

## In flight (work/)

- **ai-native-redesign/** — 重设的全部草稿真相源:`micro-core.md`(协议微核心,已接进 live `skills/preflight/SKILL.md`)、`protocol.md`(深层协议,已接进 live `skills/preflight/protocol.md`)、`coverage-check.md`(3.0→新形态 33 类 disposition,零孤儿)、`skills-draft/`(preflight/walkaround 草稿,已接 live)。
- **2026-06-23-ai-native-redesign.md** — 重设设计单一可信源(决策记录)。
- **2026-06-22-stage-land-lifecycle.md** — 旧 stage/land 生命周期设计(active,其 plan 已 done 进冷 archive)。

## Next

**cutover 收尾(剩余,按序)**:
1. **知识路由头语义趟**:`knowledge/` 下 ~18 个文件迁移时被剥了 frontmatter,只剩 `# 标题`,缺 `SUMMARY`/`READ WHEN` 路由头 + 未按域归拢。逐个补路由头(`# title`/`# ⚠ title`/`# X checklist` + `SUMMARY:` + `READ WHEN:`,`RECHECK WHEN:`←旧 when_to_update)并按域归进 `knowledge/<域>/`。walkaround 第 4 审计(缺路由头)现在会全亮。
2. **repo 清理(新形态零脚本/零 hook)**:删死脚本 `flightdeck_{index,conform,new,lint,init,lib}` + 其 tests(新 skill 零脚本依赖;留 `migrate`(throwaway 跑完可删)、`build_stamp`/`bump_version` 发版用);删 `hooks/`(新形态不注入、无机械 board-sync)+ `skills/_shared/bootstrap.md`;`skills/launch` 改成新形态(零脚本建 deck:cockpit/rules/uses/work/knowledge)或并入 preflight 的「无 deck」分支。
3. **外环文档**:README/README.zh/CHANGELOG/MIGRATION/AGENTS.md/GEMINI.md/`docs/`/`scaffolds/full` 全是 3.0 描述,需改新形态(incident `outer-ring-docs-drift` 警的就是这条)。
4. **plan #1 verify**(人读):micro-core/protocol/coverage-check + 两 SKILL 英文散文 tone+sense —— 你来读。

## Open questions / 悬而未决

- **迁移器 nested-folder 局限**(已手工绕过,未加固——脚本 throwaway):`flightdeck_migrate.py` 只 glob 源文件夹顶层 `*.md`,没递归;真 deck 的 `references/`(外部知识子树)+ `archive/`(嵌套 incidents/plans/specs)漏搬,本次手工归位:archive 子树→冷 store;references 是**自带 .git 的外部克隆**(3.0 里就未跟踪),挪进**冷 `~/.flightdeck/knowledge/references/`**(跨项目外部参考,不 vendor 进项目 git)。flat fixture 测试没覆盖嵌套——若日后还要用此脚本得加 `**/*.md` 递归 + 子树目的地决策 + 跳过 embedded git repo。
- **发布面**:cutover 全在 feature 分支 `feat/launch-recorded-config`、**未发版**;3.0 仍是 marketplace 上已 ship 的,直到显式 bump+release(rules:push 需你批准)。
- **冷 store** 已落 `~/.flightdeck/projects/flightdeck/`(archive=旧 done 的 specs/plans/incidents + 本会话 done 的 plan #1/plan3;不版本化,git 历史兜底)。

## House pointers

配置 → rules.md · 约定/偏好 → 项目根 CLAUDE.md · 知识 → knowledge/<域> · 冷/归档/idea → ~/.flightdeck

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench — `knowledge/` here documents **maintaining the flightdeck tool**, not using it elsewhere. Users running flightdeck in their own projects see their own deck, not this one.
