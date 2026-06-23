# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-24 · 月离

Focus: **把 AI-native 重设 cutover 到真产品**(本会话从「探索草稿」推进到「真切」)。本 deck 自身已迁到新形态(两目录 work/+knowledge/、free-form cockpit、零 INDEX/YAML)。

## In flight (work/)

- **ai-native-redesign/** — 草稿已全部 graduate 进 live `skills/`,**退役**(单一来源,免漂移);只留 `coverage-check.md`(3.0→新形态 33 类 disposition 映射记录)。真相源 = live `skills/preflight/{SKILL,protocol}.md` + `skills/walkaround/SKILL.md`。
- **2026-06-23-ai-native-redesign.md** — 重设设计单一可信源(决策记录)。
- **2026-06-22-stage-land-lifecycle.md** — 旧 stage/land 生命周期设计(active,其 plan 已 done 进冷 archive)。

## Next

**cutover 收尾(剩余,按序)**:
1. ✓ **知识路由头语义趟(完成)**:`knowledge/` 21 文件**分流**——9 个活的(4 trap + 4 checklist + external-memory-borrowings)补了路由头(`# /# ⚠ /# X checklist` + SUMMARY + READ WHEN[+RECHECK],值取自旧 frontmatter);**12 个记 3.0 已删机械的(conform/sync/index/hooks/recorded-config/status 生命周期/cockpit AUTO/…)判过时,归冷** `~/.flightdeck/projects/flightdeck/archive/3.0-knowledge/`(项目 git 历史也留)。derive-listing recipe 已 dogfood 跑通。
2. ✓ **repo 清理(完成,上轮)**:死脚本/hooks/_shared 已删,launch 改零脚本。
3. **外环文档(剩)**:README/README.zh/CHANGELOG/MIGRATION/AGENTS.md/GEMINI.md/`scaffolds/full` 全是 3.0 描述,需改新形态(`outer-ring-docs-drift` trap 警的就是这条)。root `AGENTS.md` 现是孤儿(emit-agents-md 已删)。
4. **plan #1 verify**(人读):新 skills 英文散文 tone+sense —— 你来读。

## External review triage (tmp/ds·claude·gpt — reference only; they lacked walkaround / current state)

- **第1轮修**:① preflight cockpit-first · ② launch 去 `Updated:`+固定区块改 free-form · ③ 退役重复草稿 · ④ protocol 补 §Persist · ⑤ §Incidents trap 澄清 · ⑥ derive-listing 标明=约定/动作。
- **第2轮修(含 walkaround)**:⑦ §Persist 空提交矛盾澄清(板动了→commit;啥没变→不 commit;非 git→无 commit 无 zero-loss)· ⑧ preflight banner 去残留 `[Stage]`(新形态无 Stage 字段)· ⑨ derive-listing recipe 改 fenced + `AREA` 占位(免尖括号渲染歧义)+ 注明 READ WHEN 尽量单行 · ⑩ walkaround 补 **uses 健康检查**(死订阅/shadow/vendor 残留)+ 点明它是「读 prose 的判断网」非字段匹配。
- **误报(两轮都报,有据驳)**:rg 反引号语法错——`cat -A` 证源文件第 98 行 `… '^(…)' <area>/` **铁无反引号**,是他们那侧尖括号渲染被吃;walkaround「悬空」(第1轮没给他们看,第2轮给了)。
- **by-design 取舍(不改,spec 已认)**:每轮 commit 噪音史(zero-loss 的代价,可后 squash)· `present=valid` 二元(RECHECK WHEN+mtime+body 兜)· **整系统依赖 AI 记住协议**——这正是 spec 列的头号风险(无机械自纠偏),walkaround 是兜底网,非 bug。

## Open questions

- **迁移器 nested-folder 局限**(已手工绕过,未加固——脚本 throwaway):`flightdeck_migrate.py` 只 glob 源文件夹顶层 `*.md`,没递归;真 deck 的 `references/`(外部知识子树)+ `archive/`(嵌套 incidents/plans/specs)漏搬,本次手工归位:archive 子树→冷 store;references 是**自带 .git 的外部克隆**(3.0 里就未跟踪),挪进**冷 `~/.flightdeck/knowledge/references/`**(跨项目外部参考,不 vendor 进项目 git)。flat fixture 测试没覆盖嵌套——若日后还要用此脚本得加 `**/*.md` 递归 + 子树目的地决策 + 跳过 embedded git repo。
- **发布面**:cutover 全在 feature 分支 `feat/launch-recorded-config`、**未发版**;3.0 仍是 marketplace 上已 ship 的,直到显式 bump+release(rules:push 需你批准)。
- **冷 store** 已落 `~/.flightdeck/projects/flightdeck/`(archive=旧 done 的 specs/plans/incidents + 本会话 done 的 plan #1/plan3;不版本化,git 历史兜底)。

## House pointers

配置 → rules.md · 约定/偏好 → 项目根 CLAUDE.md · 知识 → knowledge/<域> · 冷/归档/idea → ~/.flightdeck

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench — `knowledge/` here documents **maintaining the flightdeck tool**, not using it elsewhere. Users running flightdeck in their own projects see their own deck, not this one.
