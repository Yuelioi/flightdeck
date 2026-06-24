# ⚠ a sibling workflow leaves the cockpit stale

SUMMARY: A session driven by another workflow (SDD / executing-plans) that never runs preflight leaves flightdeck disengaged — turn-end persist never applies, so the cockpit silently rots while real work proceeds (tracked in git + the other ledger), and the divergence only surfaces on the next re-entry.
READ WHEN: a session does substantial work under another workflow (SDD, executing-plans, subagent-driven) without running /flightdeck:preflight; or re-entry preflight shows cockpit focus diverging from recent commits / branch.
RECHECK WHEN: the "persist only applies once preflight loaded the protocol this session" rule, or the preflight drift check, changes in skills/preflight/{SKILL,protocol}.md.

---

## Signature

- symptom: `重开项目跑 preflight,cockpit focus 写的是 effort A,但最近 5 条提交 + 当前分支全是 effort B —— 三者对不上。做 B 的那场会话结束时没更新 cockpit。`
- error_type: stale-recovery-payload (not lost work)
- where: 任何把 flightdeck 和另一套执行工作流(SDD `.superpowers/sdd/`、executing-plans、subagent-driven)混用的项目
- trigger: 一整场会话在别的工作流节奏里干活,**从没跑 `/flightdeck:preflight`**

## 症状 / 复现

某项目里 detect-click 特性走 SDD 工作流完成(spec → 3 plans → 实现,5 条提交,进度记
`.superpowers/sdd/progress.md`)。该会话整场在 SDD 节奏里,没跑 preflight。会话结束时
cockpit 仍停在上一焦点(`focus: MCP`,`## In flight` 没列 detect-click)。下次重开项目跑
preflight,drift 检测命中:cockpit focus(MCP) vs 最近提交(detect-click) vs 分支
对不上。

关键区分:**工作没丢**——git 提交链 + SDD 账本都在,可完整恢复。丢的是 **cockpit 这个
恢复载荷的时效性**,导致 re-entry 时焦点指向错的 effort。

## 根因

不是 persist 坏了,是 flightdeck **opt-in、不 auto-fire** 的本质后果。micro-core 硬约束:

> Turn-end persist ... only applies once preflight has loaded the protocol this session.
> ... if you never run preflight this session, flightdeck isn't engaged — nothing auto-persists.

会话整场跑别的工作流、没 engage flightdeck → turn-end persist 这条**根本不存在** → 没人
改 cockpit。两套系统(SDD 账本 / flightdeck cockpit)并行,cockpit 是哑的。这是 spec 头号
风险(无机械自纠偏,全系统依赖 AI 记得跑协议)的一个更尖锐子型:**跨工作流陈旧**。

## 兜底网起作用了(别误判为纯 bug)

re-entry 的 preflight **drift 检测命中并报了**:"分支/最近提交指向 B,cockpit focus 写
A,三者对不上,确认焦点"。也就是 cockpit 烂了但 re-entry 把它兜住,没让用户被错焦点带跑
——这是 walkaround/preflight 这层 trust-but-verify 网按设计干活。代价:用户得**手动确认
一次焦点**,而非开箱即用。零损失(工作层)守住,时效性(载荷层)靠网补。

## 修法 / 自检

- 混用别的执行工作流时,**收尾仍要 engage flightdeck 跑一次 persist**:把 cockpit 的
  focus / `## In flight` 同步到这场真正干的 effort,哪怕工作本身记在别的账本里。
- 别指望 cockpit 反映"会话外"做的事——flightdeck 对自己仪式外的工作是瞎的(by design)。
- re-entry 看到 drift 警告 = 网在干活,不是 bug;按提示确认焦点即可。

## 已加固(2026-06-24,发布面协议)

能改的改了,改不了的说清楚:

- **engaged 会话**:`protocol.md` § Persist 把触发从模糊的「turn end」钉成 **milestone
  粒度**——每做完一批任务/里程碑就刷 cockpit,判据「现在关对话光靠 cockpit 能恢复、不用
  翻 git」;并点名跨工作流(executing-plans/SDD/subagent)那套账本不是 cockpit。
  `SKILL.md` 微核 persist 行同步。
- **re-entry 网**:`SKILL.md` 第4步 passive git note 从只比「分支 vs focus」扩到也看
  「最近几条提交 vs focus」(`git log --oneline -5`)——这是唯一能兜住「上场没 persist」
  的机制(本 case 正是靠它)。
- **改不了的**:没跑 preflight 的会话物理上读不到 protocol.md。彻底堵死只能靠 startup
  hook(flightdeck 故意不要)或用户混用时也跑一次 preflight。加固后真实保证 = engaged
  不再 lag + re-entry 更可靠报警,不是「绝对不会陈旧」。

## Cases

- 2026-06-24 首次(用户带回外项目 dogfood:detect-click SDD 会话没跑 preflight,cockpit
  停在 MCP 焦点;重开项目 preflight drift 检测兜住)
