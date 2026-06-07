# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-07 by 月离 (write-gate-examples 实施完成并归档：protocol § Write gate 加 skip-list+✅/❌、exit-ritual 加独立 body 质量小节、refactor spec 加边界注记；spec+plan 已 done+landed。下一步转执行 hook-primary rollout。历史详 git log。)
**Active focus**: flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。**核心卖点=随时可关对话、下次 preflight 干净接手、上下文不丢**；载体 checkpoint + soft-landing + auto-land 执行层（注入入场 + Stop board-sync）+ HISTORY 移除/gitignored-deck 接缝 均已实施，待 resync 部署 + live 复验。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-06-auto-land-executor.md](specs/2026-06-06-auto-land-executor.md) — 给 auto-land 补执行层——把唯一能在回合结尾安全自动化的 board-sync(cockpit ## 进行中 + INDEX 的 AUTO 区)从"靠 agent 自觉"转成脚本真执行(Stop hook 每回合结尾静默重生);判断性看板(## 下一步/Active focus/plan 指针)+知识分类+done 归档仍归 agent,靠 session-start 注入常驻强制令拉到很高的 best-effort,诚实不膨胀;why-no-hooks 核心前提对 gating hook 仍成立、对 session-start 注入失效,据此改写为采纳可移植注入+被动同步 hook、拒绝 gating hook
- [2026-06-06-end-of-turn-soft-landing.md](specs/2026-06-06-end-of-turn-soft-landing.md) — end-of-turn 若有知识增量,自动跑 landing 的知识+状态落盘子集并输出「已保存」标记,让用户随时可安全关闭对话、上下文不丢;soft-landing 不 commit、不归档(commit/归档/晋升闸都是 full landing 的尾巴),landing 幂等重跑只补差集
- [2026-06-07-hook-primary-refactor.md](specs/2026-06-07-hook-primary-refactor.md) — 四家 hook 趋同后的大重构——给 Codex/Gemini 补真 hook、Cursor 补 stop（机制 A：每家一份小 config + 共享 session-start/stop/run-hook 脚本），四家吃满 SessionStart 注入 + Stop board-sync；删 why-no-hooks（理由已入 cross-host-hooks）；全 skill 文案以 hook 为主路径重写、删无-hook 双路径对冲与「仅 Claude 焊/Codex 退指令文件/未实证」措辞，保留知识分类归 agent + 一行环境降级地板；保行为紧致 protocol/templates/folder-semantics；收编 auto-land-executor + soft-landing + 2 rollout，取代部分标 superseded
- [2026-06-06-auto-land-executor-rollout.md](plans/2026-06-06-auto-land-executor-rollout.md) — 把 auto-land 执行层 spec 落地的逐文件实施——新增 hooks/（run-hook.cmd + session-start 注入 + stop 被动 board-sync + hooks.json/hooks-cursor.json）+ skills/_shared/bootstrap.md，接 Cursor/Gemini manifest，加 hook 测试；再做 Layer 3 文档改写（exit-ritual board-AUTO 移出 agent 顾虑、protocol/landing 同步、why-no-hooks 前提部分失效改写 + 新决策原则、session-flow 纳入注入入场 + Stop board-sync）
- [2026-06-06-soft-landing-rollout.md](plans/2026-06-06-soft-landing-rollout.md) — 把 end-of-turn soft-landing(知识落盘+「已保存」标记、不commit不归档、landing 幂等)铺进 exit-ritual/landing/protocol/status 4 个 skill + session-flow dogfood doc 的逐文件实施步骤
- [2026-06-07-hook-primary-refactor-rollout.md](plans/2026-06-07-hook-primary-refactor-rollout.md) — 把 hook-primary 大重构落地的逐文件实施：相位1 机制（Codex/Gemini config + Cursor stop + 脚本 project-dir/emit 四家泛化 + HOOK_DEBUG + 自动化脚本测试）→ 相位2 文案（删 why-no-hooks + 引用清理、bootstrap 三链路、exit-ritual board-AUTO 移出 agent、preflight/protocol/landing/status/session-flow hook-primary 重写、保行为紧致 diff 自检）→ 相位3 spec 收编（auto-land 标 superseded、两 rollout 并入）→ 相位4 每家 Phase0 live 实证门（resync 后新会话，未过停地板）
<!-- /AUTO -->

## 下一步

- **#1 ✅ write-gate-examples 完成**：spec+plan 已实施、done、归档（protocol § Write gate 加 skip-list+✅/❌、exit-ritual 加独立 body 质量小节、refactor spec 加边界注记锚点）。写门/分类启发/body 段已定稿，hook refactor Phase2 按锚点跳过。
- **#2 执行 hook rollout（当前·先行）**：spec + plan `2026-06-07-hook-primary-refactor[-rollout]` 已落、已过 3 轮评审硬化。= 执行 `plans/2026-06-07-hook-primary-refactor-rollout`——**相位1 机制接线（本会话可 TDD）** → 相位2 文案 → 相位3 收编 → **相位4 每家 Phase0 live 实证门（resync 后新会话，未过停地板）**。执行方式待用户选（subagent-driven / inline）。
- **并入说明**：原「resync / live 复验」+ auto-land 两个 rollout + soft-landing 的落地，均已**并入本 rollout**（相位4 = 各家 live 实证）；auto-land spec + 两 rollout 将在相位3 标 superseded，soft-landing spec 的 what 保留。
- **本轮新并入（外部记忆系统借鉴，用户拍板）**：① Cursor 注入改 `.cursor/rules/*.mdc` 规则文件为**主路径**（稳定加载>优雅加载，Task 1.7）；② cockpit `## 关键上下文` 槽（#2，Task 2.7）；③ 失败/弯路捕获入 incidents（#4，Task 2.8）。**单独 backlog**：#1 写门负例（纯 prompt 低风险）、#7 恢复回归测试（待恢复模型稳定再做，首个核心价值行为测试）。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
