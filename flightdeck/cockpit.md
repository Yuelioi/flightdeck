# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-06 by 月离 (落地 auto-land 执行层 spec+plan：新增 `hooks/`（run-hook.cmd polyglot + session-start 注入 + stop 被动 board-sync + hooks.json/hooks-cursor.json）+ `skills/_shared/bootstrap.md`，接 Cursor/Gemini manifest；Layer 3 改写 exit-ritual/protocol/landing/why-no-hooks/session-flow。149 测试通过、index --check clean、lint clean。)
**Active focus**: flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。**核心卖点=随时可关对话、下次 preflight 干净接手、上下文不丢**；载体 checkpoint + soft-landing + auto-land 执行层（注入入场 + Stop board-sync）+ HISTORY 移除/gitignored-deck 接缝 均已实施，待 resync 部署 + live 复验。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-06-auto-land-executor.md](specs/2026-06-06-auto-land-executor.md) — 给 auto-land 补执行层——把唯一能在回合结尾安全自动化的 board-sync(cockpit ## 进行中 + INDEX 的 AUTO 区)从"靠 agent 自觉"转成脚本真执行(Stop hook 每回合结尾静默重生);判断性看板(## 下一步/Active focus/plan 指针)+知识分类+done 归档仍归 agent,靠 session-start 注入常驻强制令拉到很高的 best-effort,诚实不膨胀;why-no-hooks 核心前提对 gating hook 仍成立、对 session-start 注入失效,据此改写为采纳可移植注入+被动同步 hook、拒绝 gating hook
- [2026-06-06-end-of-turn-soft-landing.md](specs/2026-06-06-end-of-turn-soft-landing.md) — end-of-turn 若有知识增量,自动跑 landing 的知识+状态落盘子集并输出「已保存」标记,让用户随时可安全关闭对话、上下文不丢;soft-landing 不 commit、不归档(commit/归档/晋升闸都是 full landing 的尾巴),landing 幂等重跑只补差集
- [2026-06-06-auto-land-executor-rollout.md](plans/2026-06-06-auto-land-executor-rollout.md) — 把 auto-land 执行层 spec 落地的逐文件实施——新增 hooks/（run-hook.cmd + session-start 注入 + stop 被动 board-sync + hooks.json/hooks-cursor.json）+ skills/_shared/bootstrap.md，接 Cursor/Gemini manifest，加 hook 测试；再做 Layer 3 文档改写（exit-ritual board-AUTO 移出 agent 顾虑、protocol/landing 同步、why-no-hooks 前提部分失效改写 + 新决策原则、session-flow 纳入注入入场 + Stop board-sync）
- [2026-06-06-soft-landing-rollout.md](plans/2026-06-06-soft-landing-rollout.md) — 把 end-of-turn soft-landing(知识落盘+「已保存」标记、不commit不归档、landing 幂等)铺进 exit-ritual/landing/protocol/status 4 个 skill + session-flow dogfood doc 的逐文件实施步骤
<!-- /AUTO -->

## 下一步

- **resync + reload**：把三批改动同步进 plugin 缓存重载——① soft-landing（exit-ritual/landing/protocol/status + checkpoint/`folder-semantics`）② HISTORY 移除 + gitignored-deck git-mode 接缝 ③ **auto-land 执行层（新 `hooks/` + `skills/_shared/bootstrap.md` + Cursor/Gemini manifest + Layer 3 改写）**——让三者对下个会话 live 生效。**注意**：hooks 只在 resync 后的**新会话**才真正触发（本会话内只是落了文件）。
- **live 复验**：① auto-land——开场是否自动进入 preflight 接手态（无需手敲）、回合末 `flightdeck_index.py flightdeck --check` 是否恒 clean（Stop hook 焊死 board AUTO）、无 deck/无 bash/无 python 是否静默降级；② soft-landing + checkpoint 子路径；③ 真·gitignored deck 上跑 landing（不写 HISTORY、`mv` 不报错、INDEX 一次到位）。通过 → 批准 `specs/2026-06-06-auto-land-executor` + `2026-06-06-end-of-turn-soft-landing` + 两个 rollout plan done → 归档。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
