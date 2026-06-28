# ⚠ persist's knowledge scan has no heartbeat

SUMMARY: In an engaged run persist rewrites cockpit + commits reliably, but silently drops the knowledge-write sub-action across the whole session — only the cockpit is re-surfaced as a next action each turn, so the learning rots in a gitignored sibling-workflow scratch file and never crystallizes.
READ WHEN: a long engaged run produced zero (or far too few) knowledge files despite catching bugs / making decisions / hitting traps; or deciding whether a persist sub-action or the landing line needs more turn-to-turn visibility.
RECHECK WHEN: persist's sub-action set, its ordering, or the landing-line format changes in skills/preflight/SKILL.md or skills/preflight/operations.md; or walkaround's checks change.

---

## Signature

- symptom: `一整场 engaged 会话（跑了 preflight、persist 在生效）逐回合 commit + 重写 cockpit 全对，但 knowledge/ 一个文件没多；抓到的 bug/race/决策全留在 SDD 的 gitignored progress 笔记里，没进恢复载荷。`
- error_type: dropped-sub-action（不是 stale-payload，git 里也没丢工作）
- where: 任何 engaged 长跑会话，尤其与 SDD / executing-plans 混用（scratch 笔记吸走了本该 crystallize 的知识）
- trigger: persist 三子动作里只有 cockpit 被逐回合重新当成「下一步」surfaced；knowledge-write 没有逐回合 forcing function

## 症状 / 复现

p-downloader 实战：SDD 驱动 15 个任务（3 个站点提取器 + 下载引擎 + CLI），`3.0.0-alpha.4`，跑了
preflight 所以 persist 在生效。cockpit 每个 cycle 都刷、每 cycle 一个 bookkeeping commit——这部分**满
分**，任何时刻 cockpit 单独就能答「在干嘛 / 到哪 / 下一步 / open questions」。但全程结束：

- **knowledge/ 零文件**，尽管这趟抓到 channel deadlock、event-emit race、UTF-8/rune 截断类 bug（两
  次）+ 攒了每站点提取情报——全是教科书级「记下来会改变以后行为」。最肥的 pitfall 日志反而躺在
  **gitignored** 的 `.superpowers/sdd/progress.md`，即恢复载荷之外。
- **47 个用过的 scratch 文件**留在 skill 工作目录没清。

直到人工点名，才补写 3 个 knowledge + 清 scratch——而「人工点名」正是这份报告要消灭的东西。

## 根因

persist 有三子动作（rewrite cockpit / write knowledge / commit），但只有**一个 forcing function，且只
指向 cockpit**。于是形成注意力梯度：

- **cockpit** 每回合被 loop 当成「交还给你的东西」重新 derive + 重写 → 高可见 → 高遵守。
- **knowledge-write** 在 spec 里是平级子动作，但**没有任何东西逐回合重新 surface 它**。AI 自圆其说
  「这学习还 in-flight，等稳定了再 crystallize」——恰恰错：写入门控（「以后会不会改变我的行为 / 再
  查一次」）在抓到 bug / 学到 INTEL 的**那一刻就已满足**。低可见 → 拖延 → 永不。
- **cleanup** 根本不在 persist scope 内：location-is-state 只管 `work/` 进冷存，不管 skill 自己在 deck
  外建的 scratch dir，也不管 harness 的 task board。没人 own → 烂着。

一句话：**cockpit 有心跳，knowledge 和 cleanup 没有。** 这是 flightdeck 头号风险（无机械自纠偏、全系统靠
AI 记得跑协议）的又一尖锐子型，与 `sibling-workflow-leaves-cockpit-stale` 同源——那个是 cockpit 跨
工作流陈旧，这个是 knowledge 子动作没心跳。

## 修法 / 已加固（2026-06-25，发布面协议）

给没心跳的子动作装心跳——哪怕只是 landing 行里一句诚实的计数：

- **scan 提为强制步**：`SKILL.md` 微核把 persist 重排成有序步骤，**第一步 = 每回合扫一遍知识**（过写
  入门控就**当场**写进 `knowledge/<域>/`，不拖到 effort 收尾）；`operations.md` 的 Persist 展开段说明
  「scan first, every turn, forcing step」，并点明「拖延的知识就是那条进了 gitignored scratch、永不毕业
  的学习」。「没东西够格」是合法结果，但必须**靠扫描、刻意**抵达。
- **landing 行钉死知识计数（含 0）**：`cockpit ✓ · knowledge: 0 · commit <sha>`——一串
  `knowledge: 0` 跨回合就是可见的**心电平线**，而非沉默；省掉这段则遗漏隐形（heartbeat that shows the
  flatline）。
- **walkaround 知识平线检查**：近 20 条提交像在修 bug / 做决策 / 踩坑，而 `knowledge/` 同期零增
  → 报（⚠）平线。默认只查 flightdeck 管辖域：项目 `flightdeck/`、项目 cold store、已订阅的
  mother-store knowledge。`.superpowers/…`、`tmp/` 这类 sibling workflow scratch 不再默认扫；只有
  cockpit / topic index / briefing / knowledge 明确指向时，才检查被引用的具体路径并提出清理。
- **外圈同步**：README 中英 + adapters 把 persist 叙述从被动「writes knowledge in place」改成主动
  「scans for new knowledge and writes it」+ scan-first 排序（走 `outer-ring-docs-drift` 的全圈清扫规则）。
- **否决项**：不在 launch seed / scaffold 塞默认 landing checklist（用户既定取舍：别给每个新项目塞默认，内
  嵌本体即可）。external-scratch 的清理走 walkaround，不进 persist 核心 scope。
- **改不了的**：整系统仍依赖 AI 记得扫——forcing step + 可见计数把「忘了扫」从沉默变成显形，不是物理
  强制。

## Cases

- 2026-06-25 首次（用户带回 p-downloader 实战报告 `flightdeck-field-report.md`：engaged 长跑，cockpit
  满分但 `knowledge/` 零文件 + 47 个 scratch 没清；人工点名才补）
