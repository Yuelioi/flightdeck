---
status: active
when_to_read: 想理解一次工作会话从 preflight 进入、执行、到 landing 收尾或中途关停/遇重大决策的各种走向时
applies_to: [preflight, landing, walkaround, checkpoint, status, session, hanging-tasks]
last_updated: 2026-06-07
summary: 一次会话的走向——preflight 只读接管→执行→（任务边界 checkpoint / 重大决策 brainstorm / 阻塞记 hanging）→done 触发 landing 收尾→下次 preflight 干净接手；看板恒在盘上、commit 是独立轴
---

# 一个对话的走向

## 一句话

一次会话沿一条主干走：**preflight 只读接管 → 执行 → done 触发 landing 收尾 → 下次 preflight 干净接手**。主干上有三个岔口——任务边界做 **checkpoint**、遇重大决策走 **brainstorm**、没做完的活记进 **Hanging Tasks**。撑起全程的两条不变量是：**看板恒在盘上**（随时关掉、下次干净接手，不靠 git）、**commit 是独立刻意的轴**（不留噪音 commit）。这正是 flightdeck 的核心卖点——上下文不丢。

## 主干（一张图）

```
  [进入]                [执行]                                  [接缝]            [收尾]
  preflight  ──go──▶    干 ## Next                  ──批准/签收──▶  done    ──▶   landing      ──▶  下次 preflight
  只读接管             改 spec/plan、写代码、跑测试            status:done      回合末 debounce 跑一次     干净接手（闭环）
  读 INDEX/cockpit       │                                                    分类知识·建议status
  报下一步、停           │                                                    重生成变动 INDEX
  （不创建/不审计）      ├── 任务边界 ──▶ checkpoint（两处写盘，不 commit）   回写 cockpit
                        │                cockpit ## Next + plan current: 指针    recurrence sweep + 晋升闸
                        ├── 重大决策 ──▶ brainstorm（不自由发挥）            本地 commit（push 问）
                        ├── 没做完/阻塞 ▶ 记 cockpit ## Hanging Tasks         归档 done（Land Routine）
                        │                （阻塞干净退出，下次 preflight 先解决）
                        └── 回合末有知识增量 ▶ soft-landing（不 commit·不归档）
                                             知识+状态落盘 → 输出 💾 上下文已保存
                                             纯状态增量 → checkpoint 静默；无增量 → 沉默
```

## 主干逐段

1. **进入 —— preflight（只读接管）。** 读 `rules.md` / `INDEX.md` / `cockpit.md`，报"Next"item，**停**。它**不创建 deck**（那是 launch）、**不审计**（那是 walkaround）、不改 cockpit。可能附**被动 note**：git/layout 漂移、或"≥5 个未 land 改动 → 考虑 landing"。无 deck → 指向 `/flightdeck:launch` 并停。**四家宿主**的入场 hook 都把 AI 开场第 0 turn 拉进这个接手态（注入 bootstrap 强制令 + cockpit 锚点；Claude/Codex/Gemini 经 `SessionStart` 注入 `additionalContext`、Cursor 经 `.cursor/rules/flightdeck-context.mdc` 规则文件），不需用户手敲 `/flightdeck:preflight`。（注入已在 Claude live 实证，Codex/Gemini/Cursor **待 Phase 0 实证**；未生效的宿主退到 `@`-include 地板 / 手动入场，内容一致。）

2. **执行 —— 你说 "go"。** AI 干 `## Next`：改 `specs/`/`plans/`、写代码、跑测试。一个 spec 自身怎么从 idea 走到 done，见 [spec-lifecycle.md](spec-lifecycle.md)。

3. **接缝 —— done。** `active → done` 的触发源是**你断言的批准/签收**——AI 不自评完成、不靠 smoke-check 判定。到 `done` 即把棒交给 landing。**done 只翻 status，不归档**。

4. **收尾 —— landing（full mode）。** 在**回合结束前** debounce 跑一次（把本回合所有 `done` 聚到同一次 landing）：① 分类本会话新知识（incident/checklist/spec/plan/doc/references，或不写）② 建议 status、bump `last_updated` ③ 重生成**有改动**文件夹的 INDEX + root ④ 回写 cockpit（`Last updated`/`## In Progress`/`## Next`）⑤ recurrence sweep + 晋升闸 ⑥ 本地 commit（**push 问**）⑦ 归档 `done`（Land Routine：算 land set → 普通 `mv` 搬进 `archive/`（绝不 `git mv`）→ 改关系边 → 删 INDEX 行）。落地记录就是 `archive/` 里的文件本身 + `git log`，**不另记流水账**。

5. **闭环 —— 下次 preflight 干净接手。** 看板已在盘上，下个会话进 preflight 就接着 `## Next` 走。

## 三个岔口

- **任务边界 → checkpoint（轻量看板同步）。** 一个 plan-task **完成**时 AI **自调**（trivial 编辑不触发，避免噪音）：只做**两处写盘**——刷新 cockpit `## Next` + 推进 plan 的 `## Progress` `current:` 指针。**不** commit、**不**归档、**不**重生成 INDEX、**不** bump `Last updated`。它是 landing 的**严格子集**，专为"中途随时关掉、下次 preflight 无损接手"。

- **重大决策 → brainstorm。** 真正模糊的分类、或够分量的设计决策，**先和你 brainstorm**，不自由发挥。90% 的收尾决策是显然的，直接分类；只有真歧义才进 brainstorm（默认就 brainstorm 摩擦太高 → 被跳过 → 知识丢失）。

- **没做完 / 阻塞 → Hanging Tasks。** 有未决阻塞项时**不能干净退出**：要么当场解决，要么显式记进 cockpit `## Hanging Tasks`（`- [ ] <阻塞项>`，**手维护**，AI 不自动派生）。下次 preflight 入口就会看到并**先解决它**。

- **会话结尾自动落盘 → soft-landing。** 每个回合结束时若检测到**知识增量**（信号 3），AI 自动触发 **soft-landing**：把知识与状态落盘，**不** commit、**不**归档、**不**重生成 INDEX，并输出 `💾 上下文已保存` 标记告诉用户可以安全关闭。纯状态增量（无新知识）→ checkpoint 静默；完全无增量 → 沉默。意义：长会话干完活、用户离开，上下文不因会话中断而丢失，且用户**看得到**「已保存」信号。**四家宿主**的机械看板（`## In Progress` + 各 `INDEX.md` 的 AUTO 区）另由 **turn-end hook 每回合结尾静默重生**（Claude/Codex `Stop`、Cursor `stop`、Gemini `AfterAgent`；幂等、不 commit/不归档），所以机械看板永不漂；判断性看板（`## Next`/`Active focus`/plan `current:`）+ 知识落盘仍由 agent（soft-landing/checkpoint）做。（Claude 已实证，其余**待 Phase 0**。）

## 可能发生 vs 可能不发生（分叉）

| 情形 | 结果 |
|---|---|
| 产出了新知识 | landing 分类落盘（incident / checklist / spec / plan / doc / references）|
| **没**产出知识 | 只在 `Active focus` 变了时更 cockpit，其余不写（写门很严，flightdeck 不是会话日志）|
| `done` 但仍被某 `active` 用 `implements:` 指着 | **done-but-unlanded**——留在源文件夹**不搬**，下次 landing 重扫、入边清空才归档（drain 不积累）|
| 中途直接关掉对话（没到 done）| 靠 **checkpoint 写在盘上的看板**，下次 preflight 接手；未写盘的进度才会丢 |
| landing 中途失败 | **不回滚 `done`**——文件停在 done-but-unlanded，下次 landing 扫到它 |
| 一长会话只埋头干、从不翻 status | 中途**不**催（YAGNI）；若回合末有知识增量，end-of-turn soft-landing 落盘（见下行）；纯状态增量 → checkpoint；否则沉默，下次入口才提示 |
| 长会话干完活、用户离开，有新知识 | end-of-turn 自动 soft-landing 落盘 + 打「已保存」标记，可安全关闭 |

## 两条贯穿全程的轴（为什么"上下文不丢"）

- **看板恒在盘上，不靠 git。** "随时关掉再开、上下文不丢"骑在**文件落盘**上——preflight 读的是*文件*，与 commit 状态无关。所以 checkpoint 每个任务都同步看板（便宜、不 commit）。四家宿主上，机械 AUTO 区还额外由 turn-end hook 每回合焊死（Claude 已实证，其余待 Phase 0），进一步保证"随时关掉、下次干净接手"。
- **commit 是独立、刻意的轴。** commit 只在 landing / 里程碑发生，避免一串噪音 commit。本仓库约定更强：**只本地 commit，绝不 push**。

> 出处：`skills/preflight/exit-ritual.md`（decision tree / checkpoint / Land Routine / land-readiness）、`skills/preflight/protocol.md` § Lifecycle、`skills/preflight/SKILL.md`（preflight 清单）。相关：[spec-lifecycle.md](spec-lifecycle.md)（artifact 级流向）。
