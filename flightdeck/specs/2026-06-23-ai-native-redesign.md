---
status: active
summary: 少结构·多信任 AI 重设:砍流程/迁移/冗余三痛,resume+persist 两动词,behave/know/now 三层软知识,引用订阅替 vendoring,位置替状态+冷存储进母库(不版本化)+frontmatter 全砍(零 schema,首行自述替路由)。设计进行中
last_updated: 2026-06-23
---

# AI-native redesign: less structure, more trust

> 状态:**设计进行中**(brainstorm 草案,边锤边填)。这是 flightdeck 自身的一次彻底重设方向探索,不取代当前 3.0;3.0 继续运行,本 spec 探索「纯 AI 形态」。

## ⏸ 最新方向(2026-06-23,边锤边填)

> 用户拍板(原话):**「使用新的目录结构,但保留旧版本的 frontmatter,不过删减大部分生命周期。」** + 续锤:**「位置替状态——冷的进母库,项目只剩热的;母库不版本化,单机为主,undo 基本不要。」**

这是对下文早期草案的**修正,以此为准**。早期草案经 pivot、再经本周期 6 条迭代(frontmatter 一度被 pivot 保留、又被锤定 #6 反转回全砍)——**最终态一律以「本周期锤定」+「变动指南」为准**,下文 §0–8 是更早的推演底稿。

- **目录结构 = 新的**:`state.md` + `uses.md` + `work/` + `behave/`(域嵌套)+ `know/`(按域共置、坑带 ⚠)。沿用下文。
- **frontmatter = 全砍(deck-wide 无 schema)**:这是对 pivot「保留旧版 frontmatter」的**反转**——auto-stale 一砍,保 frontmatter 只剩路由价值,而路由由**首行自述 + grep** 替代。knowledge 不带 frontmatter;`when_to_read` 降级成首行散文,`applies_to`/`last_updated`/`when_to_update`/`status` 全砍。详第 6 条。
- **生命周期 = 砍大部分**:status 机 · idea→active→done→archive→graduate→promotion 链 · stage/land 两段 · conform/迁移 · sync 子系统 —— 全砍,只留最小(知识能写/能读 + AI 自判新鲜度)。

### 本周期锤定(2026-06-23,6 条)

1. **砍常驻 INDEX → grep + 走树。** resume 默认只读 `state.md`;任务起时 grep **文件名 + 首行自述 + body**(无 frontmatter 可 grep,见第 6 条)+ `ls` 走树按需开篇。成本 ∝ 命中,守住 token 红线;无派生副本 = 无漂移。超大 area 才脚本派生一行目录(YAGNI 逃生口)。
2. **全砍 status 机 → 位置替状态(仅 work)。** `work/` 里有 = active,挪走 = done。status 字段消失,生命周期长链随之拆掉。(**knowledge 不套此规** —— 常驻,present=有效/删除=死,见第二轮锤定 #3。)
3. **冷存储全进母库。** 项目 `flightdeck/` 只剩热的(state/uses/work/behave/know);`~/.flightdeck/` 持 `know/`(跨项目 + first-seen incident 暂存池)+ `projects/<x>/`(本项目归档 + idea 池)。
   - **incident 晋升阶梯(位置即复发计数)**:第一次撞 → 进母库 `know/`(还不知是否本项目专属,先 park 跨项目池);再撞 → 检索母库被提醒;**第三次 → 回项目**(证明本项目复发,落本地)。替掉 `recurrences` 计数器 + promotion gate;补救稳定后结晶进 `behave`。
4. **母库不版本化。** `~/.flightdeck/` 是普通全局目录,不进 git。**零丢失红线只覆盖热层**(项目 repo,persist 每轮 commit);冷层无损兜底、不做硬保证(错题大不了重记、归档 git 大半已有且极少翻)。连带出局:**git/undo 载体、多 agent 并发、hook 强制 commit**——单机用户为主,undo 场景 99% 不存在。
5. **自动 stale 全砍。** 无机械 stale flip;`last_updated`/`when_to_update` 只是 AI 加载时读的提示,当场自判「可能过期、验一下」。persist 不再做路径交集。
6. **frontmatter 全砍 → 零 schema(deck-wide)。** 第 5 条砍掉 auto-stale 后,保 frontmatter 的理由只剩路由,而路由可由首行自述 + grep 替代 → 整个新 deck **零 frontmatter**。
   - **约定**:每个 knowledge 文件首行 = `# <标题> — <何时读>`;trap 文件首行 `⚠ trap: …`;body 自带领域关键词。
   - **路由** = grep 文件名 + 首行 + body;**新鲜度** = AI 看**文件系统 mtime**(走树 `ls -l` 时顺带,不走 git)+ body 自判。`when_to_read`→首行散文,`applies_to`/`last_updated`/`when_to_update`/`status` 全砍。
     - **为何 mtime 不走 git**:① 母库不版本化 → 那儿没 git 可问,mtime 是唯一信号 → **一套机制管两层**;② 路由已是 `ls` 走树,mtime 顺路白嫖,省每文件 `git log`;③ 新鲜度只是软提示,不需 git 级精度。**坑**:mtime 在 clone/checkout/cp/同步后重置——但单机为主 + 软提示 + body 兜底,不咬人。
   - **大赢**:无 schema → 痛点 #2(改了难迁移)基本蒸发;迁移 = 机械剥 frontmatter + 合并出首行。
   - **承重约定**:首行自述必须紧致(它是唯一路由锚)→ 这条进 `behave`。**代价**:grep 无 tag,同义词可能漏(赌:域文件夹 + AI 走树 + 读首行兜得住)。

### 协议正文形态(2026-06-23,已定形)

两层,**dogfood 惰加载原理**(= resume 读 state 再走树 的同构),两层**不重叠** → 零漂移:

- **微核心(~1 页,进 `CLAUDE.md` 每会话常载)**:两动词(resume/persist)· 文件结构图 · 不变量(位置=状态 · 首行自述 · 写门 · 热层每轮 commit)· 一句「深层见 `behave/flightdeck.md`」。
- **深层(`~/.flightdeck/behave/flightdeck.md`,按需读)**:write-gate skip 清单细节 · incident 母库↔项目阶梯 · uses 订阅+本地覆盖合并 · vendoring · 派生目录逃生口。

骨架 7 节:① 一句话+两动词 ② 文件结构 ③ 位置即状态 ④ 知识约定(首行/⚠trap/按域;grep+走树;mtime+body 判新鲜)⑤ 写门 ⑥ 零丢失 ⑦ edge。**①–③ + ⑥精要 → 核心;④–⑤细节 + ⑦ → 深层。** 剩:authoring(英文发布面)。

### 第二轮锤定(2026-06-23 · 回应外审,关掉最后开口)

外审(ds/claude/gpt)收敛出几个我上轮误标「已定」的真开口——撤回「设计层已无悬而未决」,逐个锤死:

1. **uses.md 格式 + 合并 = 纯列表 + 本地全替(不 merge)。**
   - 格式:每行一条 `~/.flightdeck/` 下的相对路径;目录条 = 订阅整棵子树;`#` 注释;无 YAML。例:`behave/commits.md` / `know/auth/`。
   - resume 读 uses.md → 这些全局文件/目录并入路由树(同本地 know/behave)。
   - **同 relpath 冲突 = 本地整文件 shadow 全局(replace,不 merge)。** 砍掉「AI 合并/扩展」——那正是外审戳的「又造两个来源 + 运行时合并 = 漂移没消除」。要扩展就自己读两边,但**文件级规则是本地覆盖** → 确定性、零维护、两次 resume 同结果。
   - 全局文件失踪/改名:resume 出一行软警告,不 fail。

2. **incident 阶梯砍计数,改「按 scope 定居 + grep 去重 + 判断结晶」。**
   - 外审对:三次回项目 = 没用字段的状态机,母库不版本化 → 计数无处存、跨机器重置。
   - 新规:撞坑 → 写 `⚠ trap:`,**按 scope 落位**(本项目专属 → 项目 `know/<域>/`;通用教训 → 全局 `know/`;AI 写时判)。复发 = 再撞 grep 到既有 trap → **读了不重写**;补救稳定 → 判断结晶进 `behave/`。
   - **无计数、无「第三次」。** 位置编码 **scope(项目/通用)**,不是次数——scope 稳定,次数不稳。

3. **「位置即状态」收窄到 *work*,不套知识。**
   - gpt 对:work 靠在不在 `work/` 表 active/done 成立;know/behave **常驻**,「在项目里 ≠ 活」。
   - 精确版:**work = 位置即状态(active/done);knowledge = 常驻(present=有效 / 删除=死),本就无状态。** 知识不「完成」只「失效被删」;obsolete 知识 = 删(不 drain archive——知识不是 done 是 wrong)。

4. **write-gate 洞补死(我草稿 bug)。** 砍宽到没边的「informs a decision」;微核心给**完整可操作**门:正面 =「只写**会改你以后怎么做**、或**以后要再查**的」;skip 短清单进核心(一次性日志 / build 只是过了 / 探索没结论 / 重跑没新增),完整例子留深层。

5. **「Git is the history」措辞改(我草稿 bug)。** done 挪进**不版本化**母库,archive 不在 git 里。改:git 是**项目 repo(热层)**的历史;归档进冷存储**留着但不在 git**,项目 git log 只记「它离开了」。

6. **零丢失红线 = 精确化,不松绑。** 红线保的「上下文」一直 = **恢复载荷**(resume 续上所需:state + work + 项目 know/behave,全热层、全在项目 git、每轮 commit)。冷存储(归档/idea/通用 trap)**从来不是恢复载荷**,丢了不影响 resume。故:**恢复载荷零丢失完整保住;冷存储 = 留存但不版本化,显式排除在零丢失外。**

**头号风险(记入取舍,不当已解决)**:gpt 戳的本质 —— 砍机械(schema/INDEX/sync/status 机/walkaround)的同时,把 stale/路由/复发/promote/uses/write-gate 全压到 **AI 判断 + 约定**;而**机械自纠偏(walkaround 抓漂移),约定+判断不会**。AI 哪轮偷懒 → 质量静默退化,兜底只有 preflight/resume 重读 + 人注意到。这是「机械保证→信任 AI」赌注的代价面,**认,列头号风险**。

**术语统一**:① **母库**只指整棵 `~/.flightdeck/`;其子目录叫**冷存储 `projects/<x>/`**(免「母库套母库」)。② behave/know 出现处标**全局/项目**限定。③ **温度 = 版本化与否**:热层 = 项目 repo(git);冷层 = 全局 deck(无 git)。全局 behave/know 是**冷存(无版本)但活查(经 uses 订阅)**——温度 ≠ 活跃度。

## 动机:一个根,三个痛

当前 flightdeck「笨重」。三个痛被确认为**同一个根:结构太多**——其中大半是「不信任 AI」加的脚手架:

1. **流程复杂** —— 8 个 skill(preflight/stage/land/status/walkaround/conform/sync/new/emit-agents-md)+ idea→active→done→archive→graduate→promotion 长生命周期。
2. **改了难迁移** —— 动 flightdeck 自身格式/规则,所有现存 deck + 脚本 + skill 散文连锁更新(incident `validator-canonical-section-list-skew` 即此类活样本)。
3. **AI 写冗余** —— 内容自膨胀、重述(protocol 自称 SSOT 33 次,却到处复制)。

**方向:少结构 · 多信任 AI。** 砍「不挣钱」的结构(为拷贝/同步/校验/迁移付的机器),留「挣钱」的结构(裁剪知识面、token 经济、消化层级)。

## 不可碰的内核(红线)

- **跨会话上下文零损失**(de-scope baseline)。保证从「机械」(AUTO 区/hook/确定性恢复)迁到「信任」(AI 每轮忠实重写 state + commit)——真实取舍,与「多信任 AI」一致。
- **token 经济(选择性加载)** —— 靠「多个小文件 + 只开相关」保住,不靠合并文件。

## 贯穿原理(每个 scale 顾虑都落回它)

**拷贝/派生副本是漂移、同步、维护的根。** 砍掉为「拷贝/同步/校验/迁移」付的机器,保留需求本身,靠**「单一真相源 + AI 直读判断 + 挣得起的那点结构」**替代。每次抛来一个顾虑(token、母库、100 选 10、多半成品、superpowers、多级知识库、incident),修法都回到这条。

---

## 已定的设计(§0–8 = 历史推演底稿)

> ⚠ **§0–8 是更早的推演底稿,部分已被「本周期锤定」+「第二轮锤定」+「变动指南」覆盖**(incident 阶梯计数、knowledge 套位置即状态、母库术语等)。**终稿真相一律以上方那三节为准**;此处只读流程脉络,勿当现行规范引用。定档时这些会被收敛/删除。

### 0. 文件结构(全貌)

```
~/.flightdeck/                 全局母库(普通目录,不版本化)
├── behave/                     跨项目约定(obey)
│   ├── commits.md  comments.md ...
│   └── flightdeck.md           ← 极简协议本身
├── know/                       跨项目知识(consult)+ first-seen incident 暂存池
└── projects/<x>/               每项目冷存储:归档 + idea 池(冷的全搬这)

<project>/flightdeck/           项目 deck(在项目 git repo 内)
├── state.md                    now/仪表盘 —— 唯一恢复载荷,每轮重写
├── uses.md                     订阅清单 —— 引用全局那 N 个
├── work/                       在飞的多步工作(替 specs+plans)
│   ├── <effort-a>/  design.md  plan.md     ← superpowers 产出原样放
│   └── <effort-b>.md                       ← 轻量 effort 单文件
├── behave/                     项目专属约定
└── know/                       项目专属知识(树状嵌套,含按域共置的坑)
```

无 `specs/plans/incidents/checklists/docs/references` 六分 · 无常驻 `INDEX.md` · **无 frontmatter schema(deck-wide)**——首行自述(`# <标题> — <何时读>`)+ 文件名 + 内容 grep 替路由,文件系统 mtime(走树 `ls` 顺带)替 `last_updated` · 项目内无 `archive/`(冷的搬母库)· 无 status 机 · 无自动 stale flip · 无 cockpit AUTO 区 · 无 conform/version/runtime/agents_md · 无 sync 子系统 · 无大部分脚本。

### 1. 两个动词替八个 skill
- **resume**(原 preflight):读 `state.md`(+ 解析 `uses.md`),按需走树开相关篇。默认**只载 state.md**,其余惰性。
- **persist**(原 stage/land/status/new/conform/sync/walkaround/emit):重写 `state.md` + 知识就地增改 + `git commit`。「做完」= 从 work/state 删掉,历史在 git。

### 2. state.md = now / 仪表盘
自由格式,每轮重写,**小**:列「在飞 effort」(一效一行,指向 `work/<x>`)+ 标「当前焦点 + 下一步」+「悬而未决」。它是索引 + 此刻,**不装下所有工作**。只随活动量涨,不随知识总量涨。

#### 旧 cockpit ~10 字段 → state.md(本次分析)
state.md 把旧 cockpit 塌缩成 **3 样 free-form**,并**砍掉所有 AUTO 派生区**(state 即真相,无投影副本 → 无漂移,turn-end welding hook 一并蒸发):

| 旧 cockpit 字段 | 去向 |
|---|---|
| `Updated`(日期·人·Stage) | 时间/人 → git 已知;**Stage(生命周期阶段)** 留进 state(恢复要) |
| `Focus` | → state「当前焦点」 |
| `Pointers`(配置→rules.md…) | 删(rules.md 没了);定位归协议微核心 |
| `## In Progress`(AUTO,派生 status:active) | → state「在飞 effort」一效一行(**手写,非 AUTO**) |
| `## Staged (awaiting land)`(AUTO) | **删**:无 stage/land 两段、无 archive 阀;done 直接 persist 挪母库 |
| `## Next` | → state「下一步」 |
| `## Key Context` | → state free-form(活的)或就近放 `work/<effort>` |
| `## Pending Review`(待复核 / verify 债) | → state「悬而未决」一行(无 verify 字段;下次碰到再复核) |
| `## Hanging Tasks`(阻塞) | → state「悬而未决」一行 |
| `## Note on dogfooding`(项目专属) | → `behave/`(项目约定) |

**净结果**:state.md = 在飞 effort 列表 + 焦点/下一步 + 悬而未决,**外加 git 给的时间线**。旧的两个 AUTO 区(In Progress / Staged)消失——没有派生副本可同步,也就没有 hook 要 weld。

### 3. work/ = 在飞工作(+ superpowers 集成,硬约束)
- 每个在飞努力 = 一个**文件**(轻量)或一个**文件夹**(多产物)。无 frontmatter、无 status、无 INDEX。
- **superpowers 咬合**:`work/<effort>/` 原样装 `design.md`(brainstorming)+ `plan.md`(writing-plans);`- [ ]` 复选框**归 executing-plans 管,flightdeck 不碰**。
- **集成税归零**:新设计无 required frontmatter → superpowers 产出**不必过 `/flightdeck:new` re-stamp**,直接落 `work/`。brainstorming 默认路径用「用户偏好覆盖」改指 `flightdeck/work/<effort>/`。
- 分工:**superpowers = 写一个 effort 的引擎;flightdeck = 跨会话记忆 + 知识层的薄壳。**

### 4. behave / know = 软知识两层
按「怎么用」分,不按内容类型分:

| 层 | 是什么 | 谁落进来 |
|---|---|---|
| **behave**(照办) | 做匹配任务要遵守的约定/手册/runbook | **checklist**(commits/comments/release)· rules 偏好 |
| **know**(查阅) | 系统怎么运作/为何这么设计/**踩过的坑** | 架构、决策、**incident** |

- **checklist → behave**,**incident → know**。
- **incident 按域共置,不建 silo**:`know/auth/oauth-flow.md` 旁边就是 `know/auth/oauth-trap.md`;「它是坑」= 首行 `⚠ trap:` 标记,不是文件夹类型。讲解与坑同域同查,就放一起。
- incident 机器(fingerprint/recurrence/promotion/archive 扫描)→ **AI 读了再写(就地补,不重复)+ 判断复发 + 复用域内可见**。补救稳定后结晶进 behave(旧 promotion 链,靠判断)。

### 5. 知识导航 = 走文件夹树(砍 per-area INDEX)
- `know/`(及需要时 `behave/`)**按 area 任意嵌套**。**文件夹树就是层级 + 索引。**
- 导航 = 惰性走树:`ls` 顶层 area → 钻相关 → 开相关篇。token ∝ 你要的那条枝,不是整库。
- **砍 per-area `INDEX.md`**:它只是「这 area 有哪些文件」的派生拷贝(= 漂移+维护)。`ls` 文件系统本身就是永远准确的查询。
- **大项目反而更省**:今天 preflight 读遍所有 INDEX(成本 ∝ 知识总量);新设计默认只载 state.md、按需走树(成本 ∝ 当前任务)。
- **逃生口(YAGNI)**:极大单 area 连文件名都判不出时,脚本**派生**一行目录(从首行自述抽,派生=零维护)。只在真不够时上。

### 6. 跨项目 = 引用订阅(不 vendor)
- 旧「母库」→ **全局 deck `~/.flightdeck/`**(同 behave/know)。
- 项目放 `uses.md` 引用它实际用的那 N 个全局文件(解决「100 选 10」:那 90 个不进视野)。
- **引用 ≠ 拷贝 → 整个 sync 子系统蒸发**(`synced`/边界锚/指纹/`--sync-pull`/`--fanout`/`consumers` 全砍)。改全局 = 下次读到新版,自动传播。本地同名文件覆盖/扩展全局(AI 合并,不在文件内 splice)。

### 7. 零丢失 = 单真相 + git 兜底(热层;砍 AUTO 区/hook)
- 今天 AUTO 区/hook/确定性恢复都是**防 cockpit 与现实漂移**;漂移需要两份拷贝。**新设计 state.md 是唯一真相,无投影副本 → 无可漂移之物**,机械同步失去存在理由。
- 零丢失靠三层:① 单一真相 + 每轮重写;② **git 兜底**(persist 每轮 commit,漏了可从 diff/commit msg 补)——**只覆盖热层**(项目 repo);③ 一条 behave 约定「state 答得出 在做什么/到哪/下一步/悬而未决」。
- **机械兜底(hook→强制 commit)留不留 → 已定(本周期):砍。** 母库不版本化、git/undo 出局(单机为主,undo 99% 不存在);零丢失只靠上面三层,冷层(母库)无 git 兜底、尽力而为。

### 8. 极简协议放哪
放项目 **`CLAUDE.md`/`AGENTS.md`**(每会话必载、最稳,也是今天引导 AI 的方式)。全局通用部分可同时作 `~/.flightdeck/behave/flightdeck.md` 供订阅。

---

## 接受的取舍
- **【头号风险】机械自纠偏 → 约定+AI 自觉无自纠偏。** 砍掉的机械(schema/INDEX/sync/status 机/walkaround)会自动抓漂移;新形态把 stale/路由/复发/promote/uses/write-gate 全压到 AI 判断 + 约定,**没有自纠偏兜底**——AI 哪轮偷懒,质量静默退化,只靠 preflight/resume 重读 + 人注意到。这是「机械保证→信任 AI」的代价面,认。
- 零丢失:机械保证 → 信任 AI 维护 state + commit。**保的是恢复载荷**(state+work+项目 know/behave,全热层、全在 git、每轮 commit);冷存储(归档/idea/通用 trap)不是恢复载荷,显式排除、不版本化、尽力而为。
- 跨项目本地覆盖 = **本地整文件 shadow 全局(replace,不 merge)**;要扩展自己读两边。不引入运行时合并(那会把 sync 漂移换成合并漂移)。
- repo 自包含性丢失(引用依赖机器 `~/.flightdeck`,且冷存储也在母库);要可移植/可 ship 时,vendoring 作为「引用快照成拷贝」按需加回。
- **冷层(归档/idea 池/first-seen incident)无版本、无 undo、不跨机器** —— 单机为主,错题可重记、归档 git 大半已有且极少翻,只当万一兜底。
- 语义路由比手写 `when_to_read` 略粗(赌:AI 看自描述文件名 + 走树足以判断)。
- incident 去重/回归检测从机械(指纹/archive 扫描)→ AI 读了再写 + 判断 + 位置阶梯(母库↔项目)。

## 变动指南(3.0 → 新形态映射表)

### 表 1 · 命令(skill)
| 原命令 | 去向 | 说明 |
|---|---|---|
| `preflight` | → **resume**(自动,无命令) | 进场读 `state.md` + 惰性走树 |
| `stage`(turn-end) | → **persist**(自动,无命令) | 收尾重写 state + 就地写知识 + commit |
| `landing` | **并入 persist** | 「做完」时 persist 把 work 挪母库;归档说人话,无独立阀 |
| `status` | **砍** | 位置即状态,无 status 字段/转换 |
| `walkaround` | **砍** | 无 schema/INDEX/status 可审;无派生副本=无一致性可查 |
| `conform` | **砍** | 无 schema 可 conform |
| `sync` | **砍** | `uses.md` 引用订阅替 vendoring;改全局下次读到新版 |
| `new` | **砍** | 无 frontmatter 要 stamp;新知识=写带首行的 md |
| `emit-agents-md` | **砍** | 协议正文 install 时入 `CLAUDE.md`/`AGENTS.md`;无 AUTO 区可 emit |

**剩下命令数 = 0**(resume/persist 是自动行为,非 slash command)。

### 表 2 · 文件 / 目录
| 原 | 新 | 说明 |
|---|---|---|
| `cockpit.md` | `state.md` | now/仪表盘,每轮重写,小,只随活动量涨 |
| `rules.md` · recorded-config | **删** | version/runtime/agents_md 全无 |
| `rules.md` · Project conventions | `behave/` | 项目约定 |
| `rules.md` · Rules(AI 维护偏好) | `behave/` 或 CLAUDE.md 微核心 | |
| `specs/`(active) | `work/<effort>/design.md` | superpowers 产出原样放 |
| `specs/`(idea 暂定) | 母库 `projects/<x>/ideas/` | idea 池,无日期前缀 |
| `specs/`(done) | 母库 `projects/<x>/archive/` | |
| `plans/` | `work/<effort>/plan.md` | `- [ ]` 归 executing-plans |
| `checklists/` | `behave/` | 照办层(怎么做 X) |
| `docs/` | `know/` | 查阅层(怎么运作/为何) |
| `references/`(外部导入) | `know/` 或 `uses.md` 订阅全局 | |
| `incidents/` | `know/<域>/`,首行 `⚠ trap:` | 按域共置,不建 silo |
| `archive/` | 母库 `projects/<x>/archive/` | 冷的全搬母库 |
| 各 `INDEX.md` | **删** | grep + 走树替 |
| 所有 frontmatter | **删** | 零 schema;路由靠首行自述 |

### 表 3 · 状态 / 位置 / 嵌套 / 过期 / 暂定
| 原概念 | 新形态怎么表达 |
|---|---|
| `idea`(暂定/未启动) | 母库 `projects/<x>/ideas/`(冷,不占项目视野) |
| `active`(在飞) | 项目里有就是活:`work/`、`know/`/`behave/`(活知识) |
| `done`(完成) | 挪出 `work/` → 母库 `projects/<x>/archive/`。位置=完成,无字段 |
| `stale`(过期) | 无字段;AI 看 mtime + body 自判「可能旧 → 验/改/删」 |
| `obsolete`(知识死) | 删(git 留底)或挪母库冷存;无 tombstone |
| 嵌套知识域 | `know/<域>/<子域>/…` 任意嵌套,文件夹树=层级=索引;`behave/` 同理 |
| incident 复发计数 | 位置阶梯:first-seen→母库 `know/`;复发→检索母库;第三次→回项目 |
| incident 退休/晋升 | 补救稳定 → 结晶进 `behave/`(旧 promotion 链,靠判断) |

### 迁移脚本形态(一次性,分工同 conform)
- **机械(脚本)**:按三表批量 `mv`/`rm` —— specs/plans→`work/`、checklists→`behave/`、docs/incidents→`know/<域>/`、archive+done+idea→母库、删所有 `INDEX.md`、剥所有 frontmatter。
- **语义(AI 一趟)**:① 每个知识文件**合成首行** `# <title> — <when_to_read>`(从旧 frontmatter title+when_to_read 拼,AI 润);② `cockpit.md`→`state.md` 重塑(In Progress/Focus/Next 搬进;Staged/AUTO 区丢;Pending/Hanging→「悬而未决」)。
- **纪律**:破坏性(mv/rm)→ 先 `--check` 干跑列清单 + 迁移前留一个 git commit,跑完人工扫一眼。**一次性,跑完即弃**(3.0 布局消失后脚本无用)。

## 待执行(设计已定,非设计抉择)
- **从 3.0 deck 一次性迁到新形态**:映射表 + **脚本形态已定**(见上「迁移脚本形态」);剩**写脚本 + 跑**(等新形态实体存在后才有意义)。
- ~~**派生目录触发阈值**~~ **已定**:无数字阈值、不落盘。它是 resume **走树时的按需读工具**——AI 判断「`ls` + 文件名不足以路由」时跑 `derive-listing <area>`(grep 每文件首行,打印一次性目录到上下文),**transient,不存文件** → 零维护、零漂移。触发 = AI 判断,不是计数。
- **产品化**——**方向已锁:doc-first 薄产品**(细节缓)。依据:resume/persist 是协议驱动的**自动行为**(非 slash command),手动阀又基本砍光 → **命令面蒸发** → 产品 ≈「**协议正文** + **每工具安装知识**(Claude→`CLAUDE.md` / Codex→`AGENTS.md` / Cursor→`.cursor/rules/*.mdc` / Gemini→`GEMINI.md`)+ **按需 vendoring 快照**」。scripts/scaffold-as-code 随零 schema·无 INDEX·无 sync 一并砍光。**缓**:具体留几个手动阀、要不要 setup helper、adapter 打包形态——等协议正文 + 迁移稳定再定(那时才看得清该留什么阀)。
- **极简协议正文 authoring**(形态已定=两层)——**微核心英文初稿已草拟**(见下「协议微核心初稿」);剩:深层(`behave/flightdeck.md`)authoring + 与今天 ~169K 散文对照查漏 + 定稿润色。**发布面 = 英文**。

> 已消解(2026-06-23):INDEX 去留、status 机边界、自动 stale 范围、frontmatter(→ 零 schema)、git/undo 载体、零丢失机械兜底、多 agent 并发、新鲜度载体(→ mtime)、产品形态(→ doc-first)、协议形态(→ 两层)、派生目录阈值、迁移脚本形态;**第二轮**再关:uses 格式+合并、incident 阶梯、位置即状态对知识、write-gate 洞、Git-is-history、零丢失措辞 —— 见各节。剩开的:深层协议 authoring 的具体措辞 + 产品化细节(缓)+ 头号风险(认了、非待决)。

## 提议:协议微核心初稿(英文,进 `CLAUDE.md`)

> 这是 ~1 页微核心的英文初稿(发布面 = 英文)。它同时是「~1 页真能装下全部决定吗」的自检——下稿通过即证明骨架自洽。深层 `behave/flightdeck.md` 另拟。

```markdown
## flightdeck (micro-core)

Two automatic verbs:
- **resume** (session start): read `flightdeck/state.md` and `uses.md`; then
  walk the tree (`ls` + grep) for whatever the task needs. Default load =
  state.md only; everything else is lazy.
- **persist** (turn end): rewrite `state.md`, write knowledge in place,
  `git commit` the project repo. A **work** effort is done when you move it
  out of `work/` into the cold store; the project's git log records that it
  left.

Layout:
    <project>/flightdeck/            warm tier — git-tracked, committed each turn
      state.md   now — in-flight efforts · focus + next · open questions
                 (rewritten each turn, kept small)
      uses.md    one global path per line that this project subscribes to
      work/      in-flight multi-step efforts (one file or one folder each)
      behave/    conventions to obey on matching tasks
      know/      knowledge to consult (nested by domain)
    ~/.flightdeck/                   cold tier — plain global dir, NOT git
      behave/                        cross-project conventions (consulted via uses)
      know/                          cross-project knowledge; general traps live here
      projects/<x>/                  this project's cold store: archive/ + ideas/

Invariants:
- **Location is state — for work only.** In `work/` = active; moved to the cold
  store = done. There is no status field. Knowledge (`behave/` `know/`) is
  *resident*, not work: present = valid, deleted = dead; it has no status.
- **First-line self-description** (the one lightweight convention — no YAML
  schema). Every knowledge file opens with `# <title> — <when to read>`; a
  pitfall opens with `⚠ trap: …`. Routing = grep filename / first line / body +
  walk the tree. Freshness = glance at the file's mtime (`ls -l`, free while
  walking) plus the body, and judge; in the warm tier `git log` is the precise
  fallback when mtime looks reset.
- **Write gate.** Record only what will change how you act later, or that you
  will look up again. Skip: one-off logs; a build that merely passed;
  exploration that concluded nothing; a re-run that added nothing.
- **Zero-loss covers the recovery payload** (state + work + project know/behave —
  all warm, all in git): persist commits the project repo every turn, and
  `state.md` must answer what you're doing / where you are / next step / open
  questions. The cold store is kept but unversioned — out of the guarantee.

Depth (read on demand): `~/.flightdeck/behave/flightdeck.md` — write-gate
examples, incident scope+crystallize rule, uses shadowing, vendoring,
derived-listing.
```

## 原理自洽性自检
每个 scale 顾虑(母库、100 选 10、多半成品、superpowers、多级知识库、incident/checklist)修法都落回贯穿原理。「少结构」≠「零结构」——留**挣得起**的(订阅清单、work/ 一效一档、behave/know 两层、文件夹树)、砍**不挣钱**的(维护机器/派生副本/同步/迁移/校验)。
