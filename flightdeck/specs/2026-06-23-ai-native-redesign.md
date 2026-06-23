---
status: active
summary: 少结构·多信任 AI 重设:砍流程/迁移/冗余三痛,resume+persist 两动词,behave/know/now 三层软知识,引用订阅替 vendoring。设计进行中
last_updated: 2026-06-23
---

# AI-native redesign: less structure, more trust

> 状态:**设计进行中**(brainstorm 草案,边锤边填)。这是 flightdeck 自身的一次彻底重设方向探索,不取代当前 3.0;3.0 继续运行,本 spec 探索「纯 AI 形态」。

## 动机:一个根,三个痛

当前 flightdeck「笨重」。三个痛被确认为**同一个根:结构太多**——其中大半是「不信任 AI」加的脚手架:

1. **流程复杂** —— 8 个 skill(preflight/stage/land/status/walkaround/conform/sync/new/emit-agents-md)+ idea→active→done→archive→graduate→promotion 长生命周期。
2. **改了难迁移** —— 动 flightdeck 自身格式/规则,所有现存 deck + 脚本 + skill 散文连锁更新(incident `validator-canonical-section-list-skew` 即此类活样本)。
3. **AI 写冗余** —— 内容自膨胀、重述(protocol 自称 SSOT 33 次,却到处复制)。

**方向:少结构 · 多信任 AI。** 砍掉「不挣钱」的结构(为拷贝/同步/校验/迁移付的机器),保留「挣钱」的结构(裁剪知识面、token 经济)。

## 不可碰的内核(红线)

- **跨会话上下文零损失**(de-scope baseline)。保证从「机械」(AUTO 区/hook/确定性恢复)迁到「信任」(AI 每轮忠实重写 state + commit)——更多信任、更少机械确定性,与「多信任 AI」一致,但是真实取舍。
- **token 经济(选择性加载)** —— 头一版「一个 knowledge.md」是错的(整篇加载,token 随积累涨)。token 经济靠「**多个小文件 + 只开相关**」保住,不靠合并文件。

## 已定的设计

### 1. 两个动词替八个 skill
- **resume**(原 preflight)—— 读 state,报下一步。
- **persist**(原 stage/land/status/new/conform/sync/walkaround/emit-agents-md)—— 轮末把 state 改新 + 知识就地增改,一个写动作。无 stage→land 两段、无 status 机、无 archive 搬迁、无 graduate/promotion 闸、无 INDEX 重生、无 conform。「做完的」= AI 从 state 删掉;历史在 git。

### 2. state:一份小活文档
- `state.md`,自由格式,AI 每轮重写,装下恢复所需一切(在做什么/到哪/下一步/关键上下文/悬而未决)。无固定小节、无 AUTO 区、无 schema。替掉 cockpit + INDEX + status 板 + staged 视图。

### 3. 知识按「怎么用」分三层(不是按内容类型四分)
旧四分(incident/checklist/doc/reference)混了「改变 AI 怎么用」(留)与「喂维护机器」(砍)。保留的区分只有一条——**遵守 vs 查阅**:

| 层 | 是什么 | 谁落进来 | 怎么用 |
|---|---|---|---|
| **behave** | 做匹配任务要照办的约定/手册 | `commits.md` `comments.md` | 做事前主动遵守(rules 的条件版) |
| **know** | 系统怎么运作/为何这么设计/**以前的坑** | 架构 docs、决策、incident 错题 | 要懂/要避坑时查 |
| **now** | 当前在哪 | = `state.md` | 每会话恢复 |

- 三层全是**软的**:自由格式、AI 维护、无 frontmatter schema、无 INDEX、无 status 机。「区分」是 AI 写在内容里的一句自述,维护成本 0。
- **路由**(砍了 frontmatter+INDEX 后):文件名 + 功能文件夹 + 每篇首行自述;真到列目录都嫌大,再让脚本**派生**一行目录(派生=零维护)。YAGNI。
- **incident**:避坑**价值**留(并入 know),fingerprint/recurrence/promotion **机器**砍。自我改进闭环(复发坑→硬化成 behave 约定)靠 **AI 判断**存活,无计数器/闸门。

### 4. 跨项目共享:引用订阅,不 vendor
- 旧「母库」降格成**全局 deck `~/.flightdeck/`**(同 behave/know 结构)。
- 项目不拷贝;放一份**小订阅清单**,引用它实际用的那 N 个全局文件(解决「100 选 10」:那 90 个不进项目视野)。
- **引用 ≠ 拷贝 → 整个 sync 子系统蒸发**:`synced:` / 边界锚 / 指纹 / `--sync-pull` / `--fanout` / `consumers` 全砍。改全局 = 下次读到新版,自动传播。本地同名文件覆盖/扩展全局(AI 合并,不在文件内 splice)。

## 接受的取舍
- 零丢失:机械保证 → 信任 AI 维护 state + commit。
- repo 自包含性丢失(引用依赖机器的 `~/.flightdeck`);要可移植/可 ship 时,vendoring 作为「引用快照成拷贝」的可选操作按需加回。
- 语义路由比手写 `when_to_read` 略粗(赌:AI 看一列自描述文件名足以判断)。

## 还要锤(未定)
- **零丢失怎么不靠 AUTO 区还保住**(下一段)。
- **git 历史 / undo 载体**:git-as-blob 还是 append 日志,未钉。
- **检索细节**:派生目录何时才需要;首行自述的约定。
- **多 agent 并发**(当前协议假设单会话)。
- **从 3.0 deck 迁到新形态**的一次性迁移(讽刺但必要)。
- AI 读的那份**极简「协议」**(替掉今天 ~169K 字符散文)长什么样。
- **产品化**决定(缓议:adapters/scaffold/发布面/迁移层去留)。

## 原理自洽性自检
用户每抛一个「那 X 怎么办」(token、母库、100 选 10),答案都是同一形状:**砍掉为「拷贝/同步/校验/迁移」付的机器,保留需求本身,靠「单一副本 + AI 直读判断 + 挣钱的那点结构」替代。** 这反向印证主线自洽。「少结构」≠「零结构」——留**挣得起**的结构(订阅清单、功能三层、小文件粒度),砍**不挣钱**的(维护机器)。
