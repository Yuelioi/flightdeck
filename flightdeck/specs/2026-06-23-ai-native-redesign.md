---
status: active
summary: 少结构·多信任 AI 重设:砍流程/迁移/冗余三痛,resume+persist 两动词,behave/know/now 三层软知识,引用订阅替 vendoring。设计进行中
last_updated: 2026-06-23
---

# AI-native redesign: less structure, more trust

> 状态:**设计进行中**(brainstorm 草案,边锤边填)。这是 flightdeck 自身的一次彻底重设方向探索,不取代当前 3.0;3.0 继续运行,本 spec 探索「纯 AI 形态」。

## ⏸ 最新方向(2026-06-23 本周期收尾,下周期继续)

> 用户拍板(原话):**「使用新的目录结构,但保留旧版本的 frontmatter,不过删减大部分生命周期。」**

这是对下文早期草案的**修正,以此为准**(下文「无 frontmatter schema / when_to_read 降级成首行 / 砍派生目录」等早期判断被本节覆盖):

- **目录结构 = 新的**:`state.md` + `uses.md` + `work/` + `behave/`(域嵌套)+ `know/`(按域共置、坑带 ⚠)。沿用下文。
- **frontmatter = 保留旧版**:`when_to_read` / `applies_to` / `when_to_update` / `status` 这套**留着**(不 de-schema 化、不降级成首行)→ 路由 + 自动 stale 的资产全保住(用户投资过的东西)。retrieval / stale 之前那两个待决问号,被「保留 frontmatter」一并消解。
- **生命周期 = 砍大部分**:idea→active→done→archive→graduate→promotion 链 · stage/land 两段 · status 机仪式 · conform/迁移 · sync 子系统 —— 过程税砍掉,只保留最小(知识能写/能读/能标 stale)。

**下周期要锤(本次未决):**
- frontmatter 留 ⇒ **INDEX 留不留?** 若留,改成「从 frontmatter 派生、零同步」而非手维护。
- **张力**:frontmatter(schema)在 = 「改了难迁移」痛仍在。用户选择为路由价值接受这点——下周期定**哪些字段必留、哪些可松**。
- **自动 stale**:frontmatter 既留,这台机器可一并留(它读 frontmatter)→ 确认范围。
- **「删减大部分生命周期」的精确边界**:哪些 status 转换 / 归档行为留、哪些砍(尤其 done/archive、graduate→docs、incident promotion)。
- 仍开:git/undo 载体 · 多 agent 并发 · 产品化去留 · 3.0→新形态一次性迁移 · 极简协议正文。

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
~/.flightdeck/                 全局 deck(原「母库」降格)
├── behave/                     跨项目约定(obey)
│   ├── commits.md  comments.md ...
│   └── flightdeck.md           ← 极简协议本身
└── know/                       跨项目知识(consult)

<project>/flightdeck/           项目 deck(在项目 git repo 内)
├── state.md                    now/仪表盘 —— 唯一恢复载荷,每轮重写
├── uses.md                     订阅清单 —— 引用全局那 N 个
├── work/                       在飞的多步工作(替 specs+plans)
│   ├── <effort-a>/  design.md  plan.md     ← superpowers 产出原样放
│   └── <effort-b>.md                       ← 轻量 effort 单文件
├── behave/                     项目专属约定
└── know/                       项目专属知识(树状嵌套,含按域共置的坑)
```

无 `specs/plans/incidents/checklists/docs/references` 六分 · 无 `INDEX.md` · 无 frontmatter schema · 无 `archive/` · 无 status 机 · 无 cockpit AUTO 区 · 无 conform/version/runtime/agents_md · 无 sync 子系统 · 无大部分脚本。

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
- 零丢失:机械保证 → 信任 AI 维护 state + commit。
- repo 自包含性丢失(引用依赖机器 `~/.flightdeck`);要可移植/可 ship 时,vendoring 作为「引用快照成拷贝」按需加回。
- 语义路由比手写 `when_to_read` 略粗(赌:AI 看自描述文件名 + 走树足以判断)。
- incident 去重/回归检测从机械(指纹/archive 扫描)→ AI 读了再写 + 判断。

## 还要锤(未定)
- **git 历史 / undo 载体**:git-as-blob 还是 append 日志;`persist` 每轮 commit 与 undo「截断尾」怎么咬合。
- **零丢失那一丝机械兜底**(hook→强制 commit)留不留。
- **从 3.0 deck 一次性迁到新形态**(讽刺但必要):specs/plans→work、各 knowledge 文件夹→behave/know(按域)、cockpit→state、sync 拆解。
- **派生目录**约定(首行自述格式;何时触发)。
- **多 agent 并发**(当前协议假设单会话)。
- **产品化**去留(缓议:adapters/scaffold/发布面/迁移层)。
- AI 读的那份**极简协议**正文(替今天 ~169K 字符散文)。

## 原理自洽性自检
每个 scale 顾虑(母库、100 选 10、多半成品、superpowers、多级知识库、incident/checklist)修法都落回贯穿原理。「少结构」≠「零结构」——留**挣得起**的(订阅清单、work/ 一效一档、behave/know 两层、文件夹树)、砍**不挣钱**的(维护机器/派生副本/同步/迁移/校验)。
