# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-24 · 月离

Focus: **把 AI-native 重设 cutover 到真产品**(本会话从「探索草稿」推进到「真切」)。本 deck 自身已迁到新形态(两目录 work/+knowledge/、free-form cockpit、零 INDEX/YAML)。

## In flight

- **ai-native-redesign/** — 草稿已全部 graduate 进 live `skills/`,**退役**(单一来源,免漂移);只留 `coverage-check.md`(3.0→新形态 33 类 disposition 映射记录)。真相源 = live `skills/preflight/{SKILL,protocol}.md` + `skills/walkaround/SKILL.md`。
- **2026-06-23-ai-native-redesign.md** — 重设设计单一可信源(决策记录)。
- **2026-06-22-stage-land-lifecycle.md** — 旧 stage/land 生命周期设计(active,其 plan 已 done 进冷 archive)。

## Next

**cutover 收尾(剩余,按序)**:
1. ✓ **知识路由头语义趟(完成)** + **格式钉死(本会话)**:9 个活的补了路由头、12 个 3.0 机械的归冷。本会话补:routing-header 空行布局钉进 micro-core 的 canonical 范例(`---` 前空行 load-bearing——否则末行 + `---` 被解析成 setext H2、终止符渲染时消失)+ walkaround #4 加一眼;10 个 knowledge 文件格式修对;**markdownlint 判 off-design 弃用**(机械 linter 违背新形态「零脚手架」命题,dogfood 应与真产品一致走协议+walkaround,不养调过的 lint config)。
2. ✓ **repo 清理(完成)**:死脚本/hooks/_shared 已删,launch 改零脚本。
3. **外环文档**:✓ 本会话扫了 `scaffolds/`(**退役删除**——新 launch 直接写文件、不再 copy,留着就是重复源/漂移面)+ README/README.zh(全重写到新形态,2 verbs+work/+knowledge+routing header+uses,删 INDEX/sync/landing/new/emit 等 3.0 描述)+ install.ps1/sh(去 `-Scaffold` + 修 docstring)+ plugin.json description + build_stamp.py(去 scaffolds input + 修 `checklists→knowledge` 路径)。**剩**:CHANGELOG / MIGRATION / AGENTS.md / GEMINI.md / `docs/`(architecture、philosophy)仍 3.0;root `AGENTS.md` 孤儿(emit-agents-md 已删)。
4. **plan #1 verify**(人读):新 skills 英文散文 tone —— 你来读(本会话又加了 README×2 发布面英文,一并可读)。

## Review triage

- **第1轮修**:① preflight cockpit-first · ② launch 去 `Updated:`+固定区块改 free-form · ③ 退役重复草稿 · ④ protocol 补 §Persist · ⑤ §Incidents trap 澄清 · ⑥ derive-listing 标明=约定/动作。
- **第2轮修(含 walkaround)**:⑦ §Persist 空提交矛盾澄清(板动了→commit;啥没变→不 commit;非 git→无 commit 无 zero-loss)· ⑧ preflight banner 去残留 `[Stage]`(新形态无 Stage 字段)· ⑨ derive-listing recipe 改 fenced + `AREA` 占位(免尖括号渲染歧义)+ 注明 READ WHEN 尽量单行 · ⑩ walkaround 补 **uses 健康检查**(死订阅/shadow/vendor 残留)+ 点明它是「读 prose 的判断网」非字段匹配。
- **误报(两轮都报,有据驳)**:rg 反引号语法错——`cat -A` 证源文件第 98 行 `… '^(…)' <area>/` **铁无反引号**,是他们那侧尖括号渲染被吃;walkaround「悬空」(第1轮没给他们看,第2轮给了)。
- **by-design 取舍(不改,spec 已认)**:每轮 commit 噪音史(zero-loss 的代价,可后 squash)· `present=valid` 二元(RECHECK WHEN+mtime+body 兜)· **整系统依赖 AI 记住协议**——这正是 spec 列的头号风险(无机械自纠偏),walkaround 是兜底网,非 bug。

## Open questions

- **迁移器 nested-folder 局限**(已手工绕过,未加固——脚本 throwaway):`flightdeck_migrate.py` 只 glob 源文件夹顶层 `*.md`,没递归;真 deck 的 `references/`(外部知识子树)+ `archive/`(嵌套 incidents/plans/specs)漏搬,本次手工归位:archive 子树→冷 store;references 是**自带 .git 的外部克隆**(3.0 里就未跟踪),挪进**冷 `~/.flightdeck/knowledge/references/`**(跨项目外部参考,不 vendor 进项目 git)。flat fixture 测试没覆盖嵌套——若日后还要用此脚本得加 `**/*.md` 递归 + 子树目的地决策 + 跳过 embedded git repo。
- **发布面**:cutover 全在 feature 分支 `feat/launch-recorded-config`、**未发版**;3.0 仍是 marketplace 上已 ship 的,直到显式 bump+release(rules:push 需你批准)。**版本号 gated**:新形态 README/plugin.json 描述已换,但 version 字符串仍留 `3.0.0-alpha.5`——发版时你 bump(可能 4.0,install 脚本旧注释提过)。
- **小清理待办**:`flightdeck/rules.md` 的 `### Project conventions` + 根 `CLAUDE.md` 的「发布面」清单仍把 `scaffolds/` 列为发布面例子——已删,become stale,下次顺手去掉。
- **冷 store** 已落 `~/.flightdeck/projects/flightdeck/`(archive=旧 done 的 specs/plans/incidents + 本会话 done 的 plan #1/plan3;不版本化,git 历史兜底)。

## House pointers

配置 → rules.md · 约定/偏好 → 项目根 CLAUDE.md · 知识 → knowledge/<域> · 冷/归档/idea → ~/.flightdeck

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench — `knowledge/` here documents **maintaining the flightdeck tool**, not using it elsewhere. Users running flightdeck in their own projects see their own deck, not this one.
