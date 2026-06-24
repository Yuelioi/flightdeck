# AI-native redesign: less structure, more trust

> flightdeck 自身的彻底重设探索,**不取代当前 3.0**——3.0 继续运行,本 spec 探索「纯 AI 形态」。设计经多轮 + 外审已锤定,本文件 = **单一决策记录**(演化史见 git log);剩下的是 authoring(协议正文)+ 迁移执行,非设计抉择。

## 动机:一个根,三个痛

当前 flightdeck「笨重」。三个痛同一个根 —— **结构太多**,其中大半是「不信任 AI」加的脚手架:

1. **流程复杂** —— 9 个 skill(preflight/stage/landing/status/walkaround/conform/sync/new/emit-agents-md)+ idea→active→done→archive→graduate→promotion 长生命周期。
2. **改了难迁移** —— 动 flightdeck 自身格式/规则,所有现存 deck + 脚本 + skill 散文连锁更新。
3. **AI 写冗余** —— 内容自膨胀、重述(protocol 自称 SSOT 33 次,却到处复制)。

**方向:少结构 · 多信任 AI。** 砍「不挣钱」的结构(为拷贝/同步/校验/迁移付的机器),留「挣钱」的(裁剪知识面、token 经济、消化层级)。

## 不可碰的内核(红线)

- **跨会话上下文零损失**(de-scope baseline):从「机械」(AUTO 区/hook/确定性恢复)迁到「信任」(AI 每轮忠实重写 cockpit.md + commit)。
- **token 经济(选择性加载)**:靠「多个小文件 + 只开相关」保住,不靠合并文件。

## 贯穿原理

**拷贝/派生副本是漂移、同步、维护的根。** 砍掉为「拷贝/同步/校验/迁移」付的机器,保留需求本身,靠「**单一真相源 + AI 直读判断 + 挣得起的那点结构**」替代。每个 scale 顾虑(token、母库、100 选 10、半成品、superpowers、多级知识库、incident)修法都回到这条。

---

## 形态

> **仍是插件。** skills + 协议正文(微核心 + 深层)全部定死在插件里、随版本 ship —— 这点同 3.0,不变。变的只是**数据**怎么放:项目热层(repo)+ `~/.flightdeck` 冷层(只存未定/过期/通用)。**`~/.flightdeck` 不是协议的家。**

### 两动词

- **`preflight`(手动 · 进场闸 · 招牌)**:你跑 `/flightdeck:preflight` → 载入微核心协议 + 读 `cockpit.md`/`rules.md`/`uses.md` + 惰性走树(`ls` + grep)。默认只载 `cockpit.md`,其余按需。**不注入、不自动触发**:只想看一眼别的就别跑,零打扰;**不跑 = 没启用 flightdeck**。
- **`persist`(自动 · turn-end)**:零丢失的写侧。重写 `cockpit.md` + 就地写知识 + `git commit` 项目 repo;gated on 实际 deck 改动(无改动 = no-op)。一个 work effort「做完」= 挪出 `work/` 进冷存储,项目 git log 记下它离开。

**非对称 = 保护你的自动、打扰你的按需。** persist 自动护着你(前提:本会话先跑过 preflight 把协议载进上下文 —— 没跑过的会话没有「turn-end 要 persist」这条指令,不自动落盘,这正是「只看一眼」的免打扰场景)。**手动命令 = 2**:`preflight`(进场)+ `walkaround`(审计,按需);其余(stage/landing/status/new…)全折进自动 turn-end,无命令。

### 文件结构

```
插件(随版本 ship,同 3.0)          ← 协议 + skills 定死在这,不进用户文件夹
└── skills/preflight/                 微核心(SKILL 正文)+ 深层 protocol.md

~/.flightdeck/                 母库 = 冷层(普通目录,不版本化)—— 只存「未定/过期/通用」数据
├── knowledge/                 跨项目通用知识(按域;经 uses 订阅)
└── projects/<x>/               冷存储:archive/(过期 = done)+ ideas/(未定)

<project>/flightdeck/           项目 deck(在项目 git repo 内 = 热层,每轮 commit)
├── cockpit.md                  now/仪表盘 —— 恢复载荷,每轮重写,小
├── rules.md                    项目约定(House Rules)—— 单文件,进场常读,稳定
├── uses.md                     订阅清单 —— 每行一条全局相对路径
├── work/                       在飞多步工作(在飞的 spec+plan)
│   ├── <effort-a>/  design.md  plan.md     ← superpowers 产出原样放
│   └── <effort-b>.md                       ← 轻量 effort 单文件
└── knowledge/                  持久知识 —— 按领域嵌套,类型 = 标题行(# doc / # ⚠ trap / # X checklist)
    ├── sync/   how-it-works.md  ⚠ drift-trap.md  checklist.md
    └── git/    commits.md  comments.md
```

无 frontmatter schema · 无常驻 `INDEX.md` · 无 status 机 · 无自动 stale flip · 无 cockpit AUTO 区 · 无 conform/version/runtime/agents_md · 无 sync 子系统 · 无大部分脚本 · 项目内无 `archive/`(冷的搬母库)。

**只保留两个项目目录:`work/`(在飞,按生命周期)+ `knowledge/`(持久,按领域)。** 3.0 的 `specs/plans/incidents/checklists/docs/references` 六分被这两个吸收 —— `work/` 收在飞的 spec+plan,`knowledge/` 收剩下全部持久内容。

### cockpit.md = now / 仪表盘

free-form,每轮重写,**小**:列「在飞 effort」(一效一行,指向 `work/<x>`)+ 标「当前焦点 + 下一步」+「悬而未决」。它是索引 + 此刻,**不装下所有工作**,只随活动量涨、不随知识总量涨。**砍掉所有 AUTO 派生区**(cockpit.md 即真相,无投影副本 → 无漂移,turn-end welding hook 一并蒸发)。

旧 cockpit ~10 字段去向:

| 旧 cockpit 字段 | 去向 |
|---|---|
| `Updated`(日期·人·Stage) | 时间/人 → git 已知;**Stage(生命周期阶段)** 留进 cockpit.md(恢复要) |
| `Focus` | → cockpit.md「当前焦点」 |
| `Pointers`(配置→rules.md…) | 删:定位归协议微核心 + 走树(rules.md 仍在,但 preflight 进场直接读,不需指针) |
| `## In Progress`(AUTO,派生 status:active) | → cockpit.md「在飞 effort」一效一行(**手写,非 AUTO**) |
| `## Staged (awaiting land)`(AUTO) | **删**:无 stage/land 两段、无 archive 阀;done 直接 persist 挪母库 |
| `## Next` | → cockpit.md「下一步」 |
| `## Key Context` | → cockpit.md free-form(活的)或就近放 `work/<effort>` |
| `## Pending Review` / `## Hanging Tasks` | → cockpit.md「悬而未决」一行(无 verify 字段;下次碰到再复核) |
| `## Note on dogfooding`(项目专属) | → `rules.md`(项目约定 = House Rules) |

### work/ = 在飞工作(+ superpowers 集成,硬约束)

- 每个在飞努力 = 一个**文件**(轻量)或一个**文件夹**(多产物)。无 frontmatter、无 status、无 INDEX。在 `work/` = active,挪出去 = done。
- **superpowers 咬合**:`work/<effort>/` 原样装 `design.md`(brainstorming)+ `plan.md`(writing-plans);`- [ ]` 复选框**归 executing-plans 管,flightdeck 不碰**。
- **集成税归零**:新设计无 required frontmatter → superpowers 产出不必过 `/flightdeck:new` re-stamp,直接落 `work/`。brainstorming 默认路径用「用户偏好覆盖」改指 `flightdeck/work/<effort>/`。
- 分工:**superpowers = 写一个 effort 的引擎;flightdeck = 跨会话记忆 + 知识层的薄壳。**

### knowledge/ = 持久知识(按领域,不按类型)

替掉 3.0 的 `docs/ + incidents/ + checklists/ + references/` 四个类型文件夹。**按领域嵌套**,一个文件「是什么」由**标题行**说,不由文件夹说(路由细节在路由头,见下「轻量路由头」):

| 标题行 | 是什么(原对应) |
|---|---|
| `# <title>` | 设计/原理/架构(原 `docs/`) |
| `# ⚠ <title>` | 踩过的坑(原 `incidents/`) |
| `# <X> checklist` | 照办手册/runbook(原 `checklists/`) |
| `# <title>`(SUMMARY 注来源) | 外部导入(原 `references/`) |

**为什么按域不按类型**:新路由 = grep 文件名/首行/body + 走树,**类型文件夹对路由没用了**;真正值钱的是**共置** —— 搞 sync 时 `knowledge/sync/` 里设计、坑、checklist 全在一处,不用在三个类型文件夹间来回翻。「它是 doc/坑/checklist」是文件的**标题行属性**,不是文件夹种类。

- **trap(原 incident)不建机器**(无 fingerprint、无复发计数):撞坑 → 按 **scope** 写一条 `# ⚠ <title>` 的 trap(本项目专属 → 项目 `knowledge/<域>/`;通用教训 → 母库 `~/.flightdeck/knowledge/<域>/`);复发 = 再撞时 grep 到既有 trap → 读了不重写;补救稳定 → 判断结晶成同域的 checklist。**位置编码 scope(项目/通用),不是次数** —— scope 稳定,次数不稳(母库不版本化,计数无处存)。
- 跨域的过程 checklist(commits/comments/release)= 放对应域(如 `knowledge/git/commits.md`),通用的经 `~/.flightdeck/knowledge/` + `uses.md` 订阅。

> 注意 `knowledge/`(持久知识,路由型,撞匹配任务才拉)与 `rules.md`(项目约定 = House Rules,**always-on**,进场常读)分开 —— always-on 的约定靠路由会漏,得进场就在;不进每轮重写的 cockpit.md(约定稳定,不该跟着漂)。

### uses.md = 跨项目引用订阅(替 vendoring)

纯列表:每行一条 `~/.flightdeck/` 下相对路径;目录条 = 订阅整棵子树;`#` 注释;无 YAML(例:`knowledge/git/commits.md` / `knowledge/auth/`)。preflight 读它 → 这些全局文件/目录并入路由树(同本地 `knowledge/`)。

- **同 relpath 冲突 = 本地整文件 shadow 全局(replace,不 merge)** → 确定性、零维护、两次 preflight 同结果;要扩展就自己读两边。不引入运行时合并(那会把 sync 漂移换成合并漂移)。
- 全局文件失踪/改名:preflight 出一行软警告,不 fail。
- 改全局 → 下次 preflight 读到新版(无 sync 子系统;要可移植/可 ship 时,vendoring 作为「引用快照成拷贝」按需加回)。

### 零 YAML → 轻量路由头(deck-wide 零 schema)

保 YAML frontmatter 的理由只剩路由 + 过期,两样都能被更轻的约定替代 → **零 YAML**,改用纯散文的**路由头**:文件开头几行带标签的散文,`---` 收尾(读到第一个 `---` 即止 = 便宜发现);`---` 以下是自由正文。

```
# <title>          (坑 = # ⚠ <title>;checklist = # <X> checklist)
SUMMARY: <一行,这是什么>
READ WHEN:         (何时读 / 路由进来的触发)
- <situation / keywords>
RECHECK WHEN: <它跟着什么变,变了回来复核;无则省>   ← 选填
---
<自由正文>
```

- **三标签封顶**:`SUMMARY`(必)· `READ WHEN`(必)· `RECHECK WHEN`(选)。克制,不再加。类型在标题行(`⚠` = 坑,`checklist` = 手册),不占字段。
- **读路由** = grep 文件名 + 路由头(尤其 `READ WHEN`)+ `ls` 走树。
- **维护路由** = 改了某物 → grep `RECHECK WHEN` 命中的文件回来复核(接住本项目反复栽的「改 X 忘改镜像文档」:incident `outer-ring-docs-drift`)。`RECHECK WHEN` 是软提示、触发「再判断」,不是 auto-stale flip。
- **新鲜度** = mtime(走树 `ls -l` 白嫖)+ body 自判「可能旧 → 验/改/删」+ `RECHECK WHEN` 条件;无机械 stale flip。
  - 为何 mtime 不走 git:① 母库不版本化,那儿没 git 可问,mtime 是唯一信号 → 一套机制管两层;② 路由已 `ls` 走树,mtime 顺路白嫖;③ 新鲜度只是软提示,不需 git 级精度。**坑**:mtime 在 clone/checkout/cp 后重置 —— 热层还有 `git log` 兜底,**冷层(母库无 git)没有**;但单机为主 + 软提示 + body 兜底,不咬人。
- 砍掉 `applies_to`/`last_updated`/`status`(化进路由头散文 / mtime / 位置;老 `when_to_update` → `RECHECK WHEN` 保留)。**大赢**:无 schema → 痛点 #2(改了难迁移)基本蒸发,迁移 = 剥 YAML + 合出路由头。**代价**:grep 无 tag,同义词可能漏(赌:域文件夹 + 走树 + 读头兜得住)。

### 位置即状态

**热(在项目)= 活;冷(挪进 `~/.flightdeck`)= 过期/暂存。** 无 status 字段:`work/` 里有 = 在飞,挪出去 = done(进母库 archive);idea 直接落母库 ideas。**位置只编码 active/done 两态**;blocked/reviewing/waiting/deferred 等细粒度状态走 cockpit「悬而未决」散文(或 effort 内注),不靠文件夹 —— 它们是「此刻」信息,本就归 cockpit。**knowledge 不套生命周期** —— `knowledge/` 常驻,present = 有效 / 删除 = 死,本就无状态;知识不「完成」只「失效被删」(obsolete 知识 = 删,不 drain archive,因为知识不是 done 是 wrong)。

### 写门

只写「**会改你以后怎么做**、或**以后要再查**的」。skip:一次性日志 / build 只是过了 / 探索没结论 / 重跑没新增。(完整例子留深层协议。)

### 协议两层(都定死在插件里 · 不重叠 → 零漂移)

**协议随插件 ship、定死在 skill 里,不进用户文件夹**(同 3.0 的 `skills/preflight/protocol.md`)。两层只是「常载 vs 按需」之分,dogfood 惰加载原理(= preflight 读 cockpit 再走树 的同构):

- **微核心(~1 页,常要)**:`preflight` 进场一跑即载入上下文。**「载入」≠「注入」**:载入 = 跑 skill 时机制把 SKILL 正文读进上下文(同今天 `/flightdeck:preflight` 读 protocol.md 那套);「不注入」= 不在会话开头自动塞、要你显式跑。故**不进 `CLAUDE.md`、不进 `~/.flightdeck`**(贴进用户文件 = 一份要手维护、会漂移的副本,撞贯穿原理)。内容 = 两动词 + 文件结构 + 不变量(位置=状态 · 路由头 · 写门 · 热层每轮 commit)+ 一句「深层见插件协议文件」。英文初稿见附录。
- **深层(按需读)**:插件里的深层协议文件(如 `skills/preflight/protocol.md`),AI 要细节时才读 —— write-gate 例子 · incident scope+结晶规则 · uses shadow · vendoring · 派生目录。

### 冷热两层 + 零丢失边界

- **热层 = 项目 repo(git,persist 每轮 commit)**:`cockpit.md` + `rules.md` + `uses.md` + `work/` + `knowledge/`。
- **冷层 = 母库 `~/.flightdeck/`(普通目录,不版本化)**:`knowledge/`(通用)+ `projects/<x>/{archive,ideas}`。连带出局:git/undo 载体、多 agent 并发、hook 强制 commit —— 单机用户为主,undo 场景 99% 不存在。
- **零丢失只覆盖恢复载荷** = 热层全部,**且限「用 flightdeck 的会话」**(persist 照协议做要先跑过 preflight 载入协议)。冷存储(归档/idea/通用知识)从来不是恢复载荷,显式排除、不版本化、尽力而为(错题大不了重记,归档 git 大半已有且极少翻)。
- **温度 = 版本化与否,≠ 活跃度**:全局 `knowledge/` 是冷存(无版本)但活查(经 uses 订阅)。git 是**项目 repo(热层)**的历史;归档进冷存储留着但不在 git,项目 git log 只记「它离开了」。

---

## 接受的取舍

- **【头号风险】机械自纠偏 → 约定 + AI 自觉,无自纠偏。** 砍掉的机械(schema/INDEX/sync/status 机/walkaround)会自动抓漂移;新形态把 stale/路由/复发/promote/uses/write-gate 全压到 AI 判断 + 约定,**没有机械自纠偏** —— AI 哪轮偷懒,质量静默退化。唯一的人工核查网 = `walkaround`(按需审计漂移)+ preflight 重读 + 人注意到;walkaround 部分兜这条,但仍是「信任 AI」的代价面。认,列头号风险(非已解决)。
- **零丢失** 从机械保证 → 信任 AI 维护 cockpit.md + commit,且收窄到「跑过 preflight 的会话」。
- **repo 自包含性丢失**(引用依赖机器 `~/.flightdeck`,冷存储也在母库);要可移植/可 ship 时 vendoring 按需加回。
- **冷层无版本、无 undo、不跨机器** —— 单机为主,只当万一兜底。
- **路由匹配靠散文 + grep,无 `applies_to` 精确路径表**(保留了手写 `READ WHEN` 触发,但匹配是散文级:赌 `READ WHEN` + 域文件夹 + 走树足以判断);incident 去重/回归检测从机械(指纹/archive 扫描)→ AI 读了再写 + 判断 + scope 落位。
- **跨项目本地覆盖 = replace 不 merge**(不引入运行时合并,免合并漂移)。
- **类型从文件夹降级成标题行标记**(checklist/doc/trap/reference 不再各占文件夹)—— 赢共置、输「一眼看类型分布」(靠 grep 首行补)。

---

## 迁移(3.0 → 新形态)

### 表 1 · 命令(skill)→ preflight + walkaround,其余自动/消失

**手动命令 = 2**:`preflight`(进场)+ `walkaround`(审计)。其余无命令 —— 要么折进自动 persist,要么没活可干:

| 原命令 | 去向 | 说明 |
|---|---|---|
| `preflight` | **留**(进场) | 载微核心协议 + 读 `cockpit.md`/`rules.md`/`uses.md` + 惰性走树;手动、不注入(不跑 = 没启用) |
| `walkaround` | **留**(审计) | 机械自纠偏没了,这是唯一的「信任但核查」网:人工扫 AI 漂移 —— cockpit↔现实、孤儿 `work/`、重复 trap、缺路由头、该归档没归档。只读、按需跑 |
| `stage`/`landing`/`status`/`new` | **折进自动 persist**(无命令) | turn-end 写知识 + 归档 done + 刷 cockpit + commit;无 status 字段要 stamp、无 frontmatter 要盖 |
| `conform`/`sync`/`emit-agents-md` | **消失**(无活可干) | 无 schema 可 conform · 通用知识直接读、无 vendoring 可 sync · 无 AUTO 区可 emit |

### 表 2 · 文件 / 目录

| 原 | 新 | 说明 |
|---|---|---|
| `cockpit.md` | `cockpit.md`(同名,原地重塑) | free-form、砍 AUTO 区 |
| `rules.md` · recorded-config | **删** | version/runtime/agents_md 全无 |
| `rules.md` · Project conventions / Rules | `rules.md`(保留,单文件) | House Rules + AI 维护偏好;进场常读、稳定 |
| `specs/`(active)· `plans/` | `work/<effort>/`(design.md/plan.md) | superpowers 产出原样放;`- [ ]` 归 executing-plans |
| `specs/`(idea 暂定) | 母库 `projects/<x>/ideas/` | idea 池,无日期前缀 |
| `specs/`(done)· `archive/` | 母库 `projects/<x>/archive/` | 冷的全搬母库 |
| `checklists/`·`docs/`·`incidents/`·`references/` | `knowledge/<域>/` | 按域共置,类型 = 标题行(`# …` / `# ⚠ …`) |
| 通用(跨项目)知识 | 母库 `~/.flightdeck/knowledge/` | 经 `uses.md` 订阅 |
| 各 `INDEX.md` · 所有 frontmatter | **删** | grep + 走树 + 路由头替 |

### 表 3 · 状态 / 位置 / 过期 / 暂定

| 原概念 | 新形态怎么表达 |
|---|---|
| `idea`(暂定/未启动) | 母库 `projects/<x>/ideas/`(冷,不占项目视野) |
| `active`(在飞) | 项目里有就是活:`work/`(在飞 effort)、`knowledge/`(活知识) |
| `done`(完成) | 挪出 `work/` → 母库 `projects/<x>/archive/`;位置 = 完成,无字段 |
| `stale`(过期) | 无字段;AI 看 mtime + body 自判「可能旧 → 验/改/删」 |
| `obsolete`(知识死) | 删(git 留底)或挪母库冷存;无 tombstone |
| 嵌套知识域 | `knowledge/<域>/<子域>/…` 任意嵌套,文件夹树 = 层级 = 索引 |
| incident 复发计数 | **无计数**:按 scope 定居(本项目→项目 `knowledge/`,通用→母库 `knowledge/`);复发 = grep 到既有 trap 不重写;补救稳定结晶成同域 checklist |

### 迁移脚本形态(一次性,跑完即弃)

- **机械(脚本)**:批量 `mv`/`rm` —— `specs`(active)+`plans`→`work/`、`checklists`+`docs`+`incidents`+`references`→`knowledge/<域>/`、archive+done+idea+通用→母库、删所有 `INDEX.md`、剥所有 frontmatter。
- **语义(AI 一趟)**:① 每个知识文件**合成路由头**(`# <title>` + `SUMMARY` + `READ WHEN`←旧 title/when_to_read;`RECHECK WHEN`←旧 when_to_update;incident 标题加 `⚠`),`---` 收尾;② 按领域归拢进 `knowledge/<域>/`;③ `cockpit.md` 原地重塑(In Progress/Focus/Next 搬进;Staged/AUTO 区丢;Pending/Hanging → 「悬而未决」)。
- **纪律**:破坏性(mv/rm)→ 先 `--check` 干跑列清单 + 迁移前留一个 git commit,跑完人工扫一眼。3.0 布局消失后脚本无用。

---

## 剩纯执行(设计已定,非设计抉择)

- **深层协议 authoring**:插件深层协议文件(如 `skills/preflight/protocol.md`)+ 微核心定稿(英文发布面)+ 与今天 ~169K 散文对照查漏 + 润色。
- **迁移脚本**:形态已定(见上),剩写脚本 + 跑(等新形态实体存在后才有意义)。
- **派生目录**:无数字阈值、不落盘 —— preflight 走树时 AI 判断「`ls` + 文件名不足以路由」就跑 `derive-listing <area>`(grep 每文件首行,打印一次性目录到上下文),transient、不存文件 → 零维护、零漂移。
- **产品化(doc-first 薄产品,细节缓)**:命令面 = 2(preflight + walkaround)→ 产品 ≈「协议正文(由 `preflight` 技能按需载,不贴 CLAUDE.md)+ 按需 vendoring 快照」;scripts/scaffold-as-code 随零 schema·无 INDEX·无 sync 一并砍光。**缓 + 新开的口**:非 Claude 工具(Codex/Cursor/Gemini)如何提供 `preflight` 等价入口 —— 它们的常载文件是 `AGENTS.md`/`GEMINI.md`/`.mdc`,而本设计不往那贴协议;留待产品化阶段。

---

## 附录:协议微核心初稿(英文,发布面)

> ~1 页微核心英文初稿,由 `preflight` 一跑载入上下文(不贴进用户 CLAUDE.md)。同时是「~1 页真能装下全部决定吗」的自检。深层(`skills/preflight/protocol.md`)另拟。

```markdown
## flightdeck (micro-core)

Two verbs:
- **preflight** (on request — you run `/flightdeck:preflight`): load this
  protocol, read `flightdeck/cockpit.md`, `rules.md` and `uses.md`, then walk the tree
  (`ls` + grep) for whatever the task needs. Default load = cockpit.md only;
  everything else is lazy. Nothing is injected and it never auto-fires — if you
  never run preflight this session, flightdeck isn't engaged (nothing
  auto-persists), and just looking around costs nothing.
- **persist** (automatic, turn end): rewrite `cockpit.md`, write knowledge in place,
  `git commit` the project repo. A **work** effort is done when you move it
  out of `work/` into the cold store; the project's git log records that it
  left.

Plus one audit command — **walkaround** (on request): sweep the deck for drift
(cockpit vs reality, orphaned work, duplicate traps, missing routing headers). It
is the only trust-but-verify net; nothing mechanical self-corrects.

Layout:
    <project>/flightdeck/            warm tier — git-tracked, committed each turn
      cockpit.md   now — in-flight efforts · focus + next · open questions
                 (rewritten each turn, kept small)
      rules.md   project house rules — single file, read on preflight, stable
      uses.md    one global path per line that this project subscribes to
      work/      in-flight multi-step efforts (one file or one folder each)
      knowledge/ persistent — nested by domain; type via first line
    ~/.flightdeck/                   cold tier — plain global dir, NOT git
      knowledge/                     cross-project knowledge (consulted via uses)
      projects/<x>/                  this project's cold store: archive/ + ideas/

Invariants:
- **Location is state.** In the project = live; moved into `~/.flightdeck` = cold
  (done/parked). No status field: in `work/` = active, moved out = done.
  Knowledge (`knowledge/`) is *resident*, not work: present = valid, deleted =
  dead; it has no lifecycle.
- **Routing header** (the one lightweight convention — no YAML schema). Every
  file opens with a header ended by `---`: a title (`# <title>`; pitfall `# ⚠
  <title>`; checklist `# <X> checklist`), then `SUMMARY:` (one line), `READ
  WHEN:` (when to route here), and optional `RECHECK WHEN:` (what it tracks —
  re-verify when that changes). Below `---` is free-form body. Routing reads
  only the header (cheap); freshness = mtime (`ls -l`, free while walking) +
  body + RECHECK WHEN; `git log` is the warm-tier fallback when mtime resets.
- **Write gate.** Record only what will change how you act later, or that you
  will look up again. Skip: one-off logs; a build that merely passed;
  exploration that concluded nothing; a re-run that added nothing.
- **Zero-loss covers the recovery payload** (cockpit.md + rules.md + work + knowledge —
  all warm, all in git): persist commits the project repo every turn, and
  `cockpit.md` must answer what you're doing / where you are / next step / open
  questions. The cold store is kept but unversioned — out of the guarantee.

Depth (read on demand): the plugin's deep protocol file (e.g.
`skills/preflight/protocol.md`) — write-gate examples, incident
scope+crystallize rule, uses shadowing, vendoring, derived-listing.
```
