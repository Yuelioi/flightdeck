---
status: active
summary: 少结构·多信任 AI 重设:砍流程/迁移/冗余三痛,resume+persist 两动词,behave/know/now 三层软知识,引用订阅替 vendoring,位置替状态+冷存储进母库(不版本化)+frontmatter 全砍(零 schema,首行自述替路由)。设计进行中
last_updated: 2026-06-23
---

# AI-native redesign: less structure, more trust

> 状态:**设计进行中**(brainstorm 草案,边锤边填)。这是 flightdeck 自身的一次彻底重设方向探索,不取代当前 3.0;3.0 继续运行,本 spec 探索「纯 AI 形态」。

## ⏸ 最新方向(2026-06-23,边锤边填)

> 用户拍板(原话):**「使用新的目录结构,但保留旧版本的 frontmatter,不过删减大部分生命周期。」** + 续锤:**「位置替状态——冷的进母库,项目只剩热的;母库不版本化,单机为主,undo 基本不要。」**

这是对下文早期草案的**修正,以此为准**(下文「无 frontmatter schema / when_to_read 降级成首行 / 砍派生目录」等早期判断被本节覆盖):

- **目录结构 = 新的**:`state.md` + `uses.md` + `work/` + `behave/`(域嵌套)+ `know/`(按域共置、坑带 ⚠)。沿用下文。
- **frontmatter = 全砍(deck-wide 无 schema)**:这是对 pivot「保留旧版 frontmatter」的**反转**——auto-stale 一砍,保 frontmatter 只剩路由价值,而路由由**首行自述 + grep** 替代。knowledge 不带 frontmatter;`when_to_read` 降级成首行散文,`applies_to`/`last_updated`/`when_to_update`/`status` 全砍。详第 6 条。
- **生命周期 = 砍大部分**:status 机 · idea→active→done→archive→graduate→promotion 链 · stage/land 两段 · conform/迁移 · sync 子系统 —— 全砍,只留最小(知识能写/能读 + AI 自判新鲜度)。

### 本周期锤定(2026-06-23,6 条)

1. **砍常驻 INDEX → grep + 走树。** resume 默认只读 `state.md`;任务起时 grep 文件头 `applies_to`/`when_to_read` + `ls` 走树按需开篇。成本 ∝ 命中,守住 token 红线;无派生副本 = 无漂移。超大 area 才脚本派生一行目录(YAGNI 逃生口)。
2. **全砍 status 机 → 位置替状态。** 文件「在不在项目里」= 活不活。`work/` 里有 = active,挪走 = done;knowledge 同理。status 字段消失,生命周期长链随之拆掉。
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

## 已定的设计

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
自由格式,每轮重写,**小**:列「在飞 effort」(一效一行,指向 `work/<x>`)+ 标「当前焦点 + 下一步」。它是索引 + 此刻,**不装下所有工作**。只随活动量涨,不随知识总量涨。

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

### 7. 零丢失 = 单真相 + git 兜底(砍 AUTO 区/hook)
- 今天 AUTO 区/hook/确定性恢复都是**防 cockpit 与现实漂移**;漂移需要两份拷贝。**新设计 state.md 是唯一真相,无投影副本 → 无可漂移之物**,机械同步失去存在理由。
- 零丢失靠三层:① 单一真相 + 每轮重写;② **git 兜底**(persist 每轮 commit,漏了可从 diff/commit msg 补);③ 一条 behave 约定「state 答得出 在做什么/到哪/下一步/悬而未决」。
- **这是 trust 最吃重最险处**:hook 本无活可干;若想留一丝机械兜底,可退化成「每轮强制 commit」。**(留/不留 = 用户选,待定。)**

### 8. 极简协议放哪
放项目 **`CLAUDE.md`/`AGENTS.md`**(每会话必载、最稳,也是今天引导 AI 的方式)。全局通用部分可同时作 `~/.flightdeck/behave/flightdeck.md` 供订阅。

---

## 接受的取舍
- 零丢失:机械保证 → 信任 AI 维护 state + commit。**红线只保热层**(项目 repo 每轮 commit);冷层尽力而为。
- repo 自包含性丢失(引用依赖机器 `~/.flightdeck`,且冷存储也在母库);要可移植/可 ship 时,vendoring 作为「引用快照成拷贝」按需加回。
- **冷层(归档/idea 池/first-seen incident)无版本、无 undo、不跨机器** —— 单机为主,错题可重记、归档 git 大半已有且极少翻,只当万一兜底。
- 语义路由比手写 `when_to_read` 略粗(赌:AI 看自描述文件名 + 走树足以判断)。
- incident 去重/回归检测从机械(指纹/archive 扫描)→ AI 读了再写 + 判断 + 位置阶梯(母库↔项目)。

## 还要锤(未定)
- **从 3.0 deck 一次性迁到新形态**(讽刺但必要,但因零 schema 大大简化):specs/plans→work、各 knowledge 文件夹→behave/know(按域)+ 机械剥 frontmatter 合并出首行、冷的(归档/idea 池/first-seen incident)搬母库、cockpit→state、sync 拆解。
- **派生目录**约定(首行自述格式已定;剩「何时触发」的阈值)。
- **产品化**——**方向已锁:doc-first 薄产品**(细节缓)。依据:resume/persist 是协议驱动的**自动行为**(非 slash command),手动阀又基本砍光 → **命令面蒸发** → 产品 ≈「**协议正文** + **每工具安装知识**(Claude→`CLAUDE.md` / Codex→`AGENTS.md` / Cursor→`.cursor/rules/*.mdc` / Gemini→`GEMINI.md`)+ **按需 vendoring 快照**」。scripts/scaffold-as-code 随零 schema·无 INDEX·无 sync 一并砍光。**缓**:具体留几个手动阀、要不要 setup helper、adapter 打包形态——等协议正文 + 迁移稳定再定(那时才看得清该留什么阀)。
- **极简协议正文 authoring**(形态已定=两层,见上「协议正文形态」)——把今天 ~169K 字符压成微核心(~1 页进 `CLAUDE.md`)+ 深层(`behave/flightdeck.md`)。**发布面 = 英文**。

> 已消解(2026-06-23 本周期):INDEX 去留、status 机边界、自动 stale 范围、**frontmatter 字段表(→ 零 schema)**、git/undo 载体、零丢失机械兜底、多 agent 并发 —— 见上「本周期锤定」。

## 原理自洽性自检
每个 scale 顾虑(母库、100 选 10、多半成品、superpowers、多级知识库、incident/checklist)修法都落回贯穿原理。「少结构」≠「零结构」——留**挣得起**的(订阅清单、work/ 一效一档、behave/know 两层、文件夹树)、砍**不挣钱**的(维护机器/派生副本/同步/迁移/校验)。
