# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-25 · 月离 · +dogfood finding: persist knowledge 子动作没心跳(p-downloader 实战;已修发布面+外圈+knowledge)

Focus: **把 AI-native 重设 cutover 到真产品**(本会话从「探索草稿」推进到「真切」)。本 deck 自身已迁到新形态(两目录 work/+knowledge/、free-form cockpit、零 INDEX/YAML)。

## In flight

- **ai-native-redesign/** — 重设 effort,设计 + 验证**共置一个 folder**(spec 推荐结构):`design.md`(重设决策单一可信源)+ `coverage-check.md`(3.0→新形态 disposition 映射)。草稿已 graduate 进 live `skills/`;真相源 = live `skills/preflight/{SKILL,protocol}.md` + `skills/walkaround/SKILL.md`。
- **2026-06-22-stage-land-lifecycle.md** — 旧 stage/land 生命周期设计(轻量单文件 effort;其 plan 已 done 进冷 archive)。

## Next

**cutover 收尾(剩余,按序)**:
1. ✓ **知识路由头语义趟(完成)** + **格式钉死(本会话)**:9 个活的补了路由头、12 个 3.0 机械的归冷。本会话补:routing-header 空行布局钉进 micro-core 的 canonical 范例(`---` 前空行 load-bearing——否则末行 + `---` 被解析成 setext H2、终止符渲染时消失)+ walkaround #4 加一眼;10 个 knowledge 文件格式修对;**markdownlint 判 off-design 弃用**(机械 linter 违背新形态「零脚手架」命题,dogfood 应与真产品一致走协议+walkaround,不养调过的 lint config)。
2. ✓ **repo 清理(完成)**:死脚本/hooks/_shared 已删,launch 改零脚本。
3. **外环清理(本会话基本扫完)**:scaffolds 退役删 · README×2 全重写 · install.ps1/sh 去 `-Scaffold` · 全 manifest(plugin.json×3 描述/去死 `./hooks/` 引用)· GEMINI.md 修 `@`-include(4 死文件→SKILL+protocol)· adapters×4 重写到 3 verbs(去 7 死 skill、"no-gate as of 3.0"、companion 文件、2.x `incident-reports/`)· `.github` PR 模板重写到新形态 · MIGRATION.md 重写(英文)· **删** AGENTS.md(孤儿)/ TEST_PLAN.md(3.0)/ `docs/`(architecture+philosophy+README)/ flightdeck_migrate.py(+test,throwaway)· CLAUDE.md+rules.md 去 scaffolds 例子 · build_stamp 去 scaffolds+AGENTS.md input。**剩**:CHANGELOG.md(历史,发版时补条目);版本号 gated 未动(3.0.0-alpha.5)。
4. **plan #1 verify**(人读):新 skills 英文散文 tone —— 你来读(本会话又加了 README×2 发布面英文,一并可读)。

## Review triage

- **第1轮修**:① preflight cockpit-first · ② launch 去 `Updated:`+固定区块改 free-form · ③ 退役重复草稿 · ④ protocol 补 §Persist · ⑤ §Incidents trap 澄清 · ⑥ derive-listing 标明=约定/动作。
- **第2轮修(含 walkaround)**:⑦ §Persist 空提交矛盾澄清(板动了→commit;啥没变→不 commit;非 git→无 commit 无 zero-loss)· ⑧ preflight banner 去残留 `[Stage]`(新形态无 Stage 字段)· ⑨ derive-listing recipe 改 fenced + `AREA` 占位(免尖括号渲染歧义)+ 注明 READ WHEN 尽量单行 · ⑩ walkaround 补 **uses 健康检查**(死订阅/shadow/vendor 残留)+ 点明它是「读 prose 的判断网」非字段匹配。
- **误报(两轮都报,有据驳)**:rg 反引号语法错——`cat -A` 证源文件第 98 行 `… '^(…)' <area>/` **铁无反引号**,是他们那侧尖括号渲染被吃;walkaround「悬空」(第1轮没给他们看,第2轮给了)。
- **by-design 取舍(不改,spec 已认)**:每轮 commit 噪音史(zero-loss 的代价,可后 squash)· `present=valid` 二元(RECHECK WHEN+mtime+body 兜)· **整系统依赖 AI 记住协议**——这正是 spec 列的头号风险(无机械自纠偏),walkaround 是兜底网,非 bug。

## Open questions

- **迁移器 nested-folder 局限**(已手工绕过,未加固——脚本 throwaway):`flightdeck_migrate.py` 只 glob 源文件夹顶层 `*.md`,没递归;真 deck 的 `references/`(外部知识子树)+ `archive/`(嵌套 incidents/plans/specs)漏搬,本次手工归位:archive 子树→冷 store;references 是**自带 .git 的外部克隆**(3.0 里就未跟踪),挪进**冷 `~/.flightdeck/knowledge/references/`**(跨项目外部参考,不 vendor 进项目 git)。flat fixture 测试没覆盖嵌套——若日后还要用此脚本得加 `**/*.md` 递归 + 子树目的地决策 + 跳过 embedded git repo。
- **发布面**:cutover 全在 feature 分支 `feat/launch-recorded-config`、**未发版**;3.0 仍是 marketplace 上已 ship 的,直到显式 bump+release(rules:push 需你批准)。**版本号 gated**:新形态 README/plugin.json 描述已换,但 version 字符串仍留 `3.0.0-alpha.5`——发版时你 bump(可能 4.0,install 脚本旧注释提过)。- **冷 store** 已落 `~/.flightdeck/projects/flightdeck/`(archive=旧 done 的 specs/plans/incidents + 本会话 done 的 plan #1/plan3;不版本化,git 历史兜底)。
- **母库 `~/.flightdeck` 已迁新形态(本会话)**:删 3.0 master-deck 骨架(`cockpit.md`/`rules.md` + `checklists/docs/incidents/plans/specs/references` 空壳 INDEX);3 个跨项目 checklist(comments/commits/subagent-guide)转路由头进 `knowledge/`(平铺);`skills/writing-claude-md` 挪进 `knowledge/` 当参考(保留 skill 格式,无路由头=browseable)。现 master = `knowledge/` + `projects/`。**knock-on**:其它项目(nuxtblog/aep-parser)若要订阅这些共享知识,得在各自 `uses.md` 写新路径 `knowledge/<file>`——原 `checklists/<file>` 路径已没;且那些项目本身还是 3.0,各自迁移另算。
- **冷层模型(本会话定稿)**:① `projects/<x>` → **flattened 全路径 slug**(`E--projects-tools-flightdeck`,防同名碰撞,同 Claude Code `~/.claude/projects/`);母库已改名。② **references 不进协议**:协议冷存只定义 `archive/ + ideas/`,外部参考料放哪是用户的事(协议不 mandate);flightdeck 自己那 4 个克隆从母库挪回 **repo 根 `references/` + gitignore**(实时可看、不提交;3 个带自己 .git,所以必须 gitignore)。skill/README 措辞同步:micro-core layout、protocol `## Cold tier`(slug 编码 + 「references 非协议槽、用户自定」一句)、walkaround/fallback `<x>`→`<slug>`。`knowledge/` 现只剩真·通用(comments/commits/subagent-guide/writing-claude-md)。

## Dogfood findings (from real-world use)

- **跨工作流 cockpit 陈旧**(2026-06-24,用户带回外项目)→ `knowledge/sibling-workflow-leaves-cockpit-stale.md`。一整场会话跑别的工作流(SDD/executing-plans)、没跑 preflight → flightdeck 没 engage → turn-end persist 不存在 → cockpit 哑掉烂在旧焦点;**工作没丢**(git+SDD 账本),丢的是恢复载荷时效性;re-entry 的 preflight **drift 检测兜住了**(报焦点对不上)。是 spec 头号风险(无机械自纠偏)的尖锐子型。
  **已加固(发布面协议)**:protocol.md § Persist 触发钉成 milestone 粒度 + 点名跨工作流;SKILL.md 微核 persist 行同步;SKILL.md 第4步 passive git note 扩到「最近提交 vs focus」(强化 re-entry 网)。改不了的:没跑 preflight 的会话读不到协议——加固后保证 = engaged 不再 lag + re-entry 更可靠报警,非「绝对不陈旧」。
  **+ landing 确认行**:persist 收尾打一行 `─── 🛬 landing ───`(cockpit ✓ · +N knowledge · commit sha),配 preflight 的 🛫,补上「看不见 persist 有没有发生」的盲点。明钉「landing 只是确认名、非命令/仪式,无 `/landing`」防 AI 误以为旧命令回归。

- **spec 落 `docs/` 而非 `work/`**(2026-06-25,用户带回 p-downloader 新项目)→ 根因 **不是内容缺失,是层级**:effort 产物归 `work/<effort>/` 的指引只在 **read-on-demand 的 `protocol.md` § Work efforts**;preflight 只加载 micro-core,brainstorming 会话很可能从没加载 protocol.md → 信号不在上下文 → 跟着 spec-generator 硬编码的 `docs/` 走。
  **已修(发布面,内嵌插件本体)**:① `SKILL.md` micro-core 的 `work/` layout 行抬出明确归属(`spec/design/plan` 归 `work/<effort>/`,非 side `docs/` tree)——**载重那处**,把信号从「按需层」提到「始终加载层」;② `protocol.md` § Work efforts 补**工具无关**的撞车处理一句(spec-generator 默认落别处→收进 work/;成品/参考 docs 仍可留 docs/)。narrow scope:只管活跃 effort 产物,不禁 docs/。
  **否决项**:不改 seed/初始文件(用户:别给每个新项目塞默认,内嵌本体即可);不绑死 superpowers(用户:可能用别的 spec 生成器,发布面须工具无关)。**遗留**:§ Work efforts line 66-67 旧的 `superpowers' writing-plans` 点名未动,待定是否一并去耦合。

- **persist knowledge 子动作没心跳**(2026-06-25,用户带回 p-downloader 实战报告 `flightdeck-field-report.md`)→ `knowledge/persist-knowledge-scan-no-heartbeat.md`。engaged 长跑(SDD 15 任务)cockpit 每 cycle 满分,但 `knowledge/` **零文件**——抓到的 channel deadlock / event-emit race / UTF-8 截断类 class-bug 全留在 gitignored `.superpowers/sdd/progress.md`,+47 个 scratch 没清;人工点名才补。根因:persist 三子动作只有 cockpit 有逐回合 forcing function,knowledge-write 没心跳 → 拖延 → 永不;写入门控其实在抓到 bug 那刻就已满足。spec 头号风险(无机械自纠偏)的又一尖锐子型,与 sibling-workflow 同源(那个 cockpit 跨工作流陈旧,这个 knowledge 子动作没心跳)。
  **本会话续修(上场中断的修复)+ 收尾(发布面协议)**:① `SKILL.md` 微核 persist 重排有序三步,**scan-for-knowledge 提为第一步**(forcing,当场写不拖到收尾);② `protocol.md` § Knowledge 改「scan first, every turn」+ landing 行钉死知识计数(含 0)= 可见心电平线;③ walkaround #7 加「知识平线 + 孤儿 scratch」检查;④ **外圈续扫**(本会话):README 中英(亮点+会话结束+verb 表)+ adapters/claude persist 叙述从被动「writes knowledge in place」改主动「scans … and writes」+ scan-first 排序(走 outer-ring-docs-drift 全圈规则;codex/gemini/cursor 不枚举子动作,未动)。**否决项**:不在 seed/`rules.md` 塞默认 landing checklist(用户既定:别给新项目塞默认);external-scratch 清理走 walkaround 不进 persist 核心 scope(对应 field report 建议 4 与建议 3 的边界)。**改不了的**:仍靠 AI 记得扫——把「忘了扫」从沉默变显形,非物理强制。

## House pointers

配置 → rules.md · 约定/偏好 → 项目根 CLAUDE.md · 知识 → knowledge/<域> · 冷/归档/idea → ~/.flightdeck

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench — `knowledge/` here documents **maintaining the flightdeck tool**, not using it elsewhere. Users running flightdeck in their own projects see their own deck, not this one.
