---
status: idea
summary: plan/task 边界自动看板同步（cockpit 下一步 + plan 进度落盘，commit 不强求），让用户随时可关对话、下次 preflight 干净接手、上下文不丢；轻量 checkpoint = 完整 landing 的子集
---

# 执行检查点：task 边界看板同步（随时可关、干净接手）

## 核心卖点

**用户随时可以关对话，下次 `/flightdeck:preflight` 干净接手、上下文不丢。**

长任务尤其受益：跑了很久、工作做完一段，用户不一定及时回来看；如果状态没落盘，用户一关对话再开，看到的是陈旧画面。

## 要解决的 gap

flightdeck 现在**只有完整 landing 一种状态落盘点**，且它只在**会话收尾**发生。plan 执行**中途没有任何看板更新**：

> 跑完 plan 的一个 task → 工作其实推进了 → 但 cockpit `## 下一步`、plan 文件的进度**还停在 task 开始前** → 用户一关对话再开 → preflight 读到陈旧 cockpit（进行中/下一步不对）→ 接手看到的是假象。

这就是"缓存问题"：**持久化的看板状态 < 实际进度**。

## 关键区分：看板同步 ≠ commit（两条轴）

"关了再开、上下文不变"靠的是**看板落盘，不是 git**：

- cockpit / plan 文件**在磁盘上**；preflight 读的是**文件**，与提没提交无关。
- 所以只要在 task 边界把**看板更新到真状态**（哪怕不 commit），下次 preflight 就看到真现状 → 上下文重建准确。
- commit 是**另一条轴**（历史 / durability），不必每个 task 都提（否则一堆噪声 commit）。

**这两条轴正交**：看板要随时是真的（便宜、每个 task 做、不提交）；commit 是 deliberate 的（收尾或里程碑才做）。

## 设计：checkpoint = 看板同步

| | 看板同步（checkpoint） | 完整 landing |
|---|---|---|
| 触发 | **每个 plan / plan-task 结束**，AI 自动 self-invoke | 会话收尾，deliberate |
| 动作 | 更新 cockpit `## 下一步` + plan 文件的 task 进度标记（**落盘即可**） | 看板同步 + 知识分类 + 归档判断 + smoke-check + **commit** |
| commit | **不强求**（看板讲清现状就够） | ✅ |
| 成本 | 极低、可频繁 | 重、deliberate |

**checkpoint 是 landing 的子集**：landing = checkpoint + 那几步收尾重活。

**落地在模型内、不破结构**：
- `## 进行中` 仍是 AUTO（plan 还 `active` 不变，无需动）。
- 只需在 task 边界**主动维护 `## 下一步`**（指向下一个 task）+ **plan 自己的 task 进度标记**。
- 无新配置项、无新文件夹、无新 frontmatter 字段。

## 触发判据

- **plan 或 plan-task 结束**时自动 checkpoint。
- 琐碎小改**不**触发（避免噪声）。
- 由 AI 判断 self-invoke——这是把"rituals self-invoke"的触发点从"**仅收尾**"扩到"**也含 task 边界**"，不是 harness 到点硬触发的 hook。

## 为什么不破 flightdeck 的规矩

- **契合"可逆=自动"出厂默认**：看板落盘可逆、便宜；本地 commit 也可逆（若 checkpoint 选择提交，仍在默认内，push 才先问）。
- **不破 `why-no-hooks`**：AI 主动 self-invoke，不是启动自动加载 / 到点触发的 hook。
- **不逆 3.0 删配置**：纯行为，不加任何开关 / 配置面。

## 落地形态（首要 plan 开口）

吸取 preset-library 的教训（砍了重机器）——**优先最轻形态**：

- **倾向**：checkpoint 不是新的用户 skill（用户不主动调用它，它是自动行为）。落成**文档化的 self-invoke 行为**，或在现有 `landing` skill 里加一条 **checkpoint 轻量路径**（"task 边界 → 只同步看板、不走收尾重活"）。
- **不做**：新的 `/flightdeck:checkpoint` 用户命令（除非真有手动触发需求）。

## 待 plan 细化的开口

- **形态**：文档化 self-invoke 行为 vs `landing` skill 的 checkpoint 子路径（倾向后者，复用其看板同步逻辑）。
- **plan 的 task 进度表示法**：plan 文件用 checkbox 勾，还是一个"当前 task"指针？preflight / cockpit `## 下一步` 怎么引它。
- **checkpoint 到底提不提交**：默认纯看板落盘不提交（用户"虽然没提交"的原话）；还是可逆→自动地顺手提交?需定默认，避免噪声 commit 与 durability 的取舍。
- **self-invoke 触发措辞**：在哪个 skill 的哪一步写明"task 结束 → checkpoint"。
- **与现有 landing 的代码/逻辑复用**：checkpoint 的看板同步应是 landing 看板同步那段的同一实现，避免两套漂移。
