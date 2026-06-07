# plans/ — INDEX

<!-- AUTO:plans -->
- [2026-06-06-auto-land-executor-rollout.md](2026-06-06-auto-land-executor-rollout.md) — active — 把 auto-land 执行层 spec 落地的逐文件实施——新增 hooks/（run-hook.cmd + session-start 注入 + stop 被动 board-sync + hooks.json/hooks-cursor.json）+ skills/_shared/bootstrap.md，接 Cursor/Gemini manifest，加 hook 测试；再做 Layer 3 文档改写（exit-ritual board-AUTO 移出 agent 顾虑、protocol/landing 同步、why-no-hooks 前提部分失效改写 + 新决策原则、session-flow 纳入注入入场 + Stop board-sync）
- [2026-06-06-soft-landing-rollout.md](2026-06-06-soft-landing-rollout.md) — active — 把 end-of-turn soft-landing(知识落盘+「已保存」标记、不commit不归档、landing 幂等)铺进 exit-ritual/landing/protocol/status 4 个 skill + session-flow dogfood doc 的逐文件实施步骤
- [2026-06-07-hook-primary-refactor-rollout.md](2026-06-07-hook-primary-refactor-rollout.md) — active — 把 hook-primary 大重构落地的逐文件实施：相位1 机制（Codex/Gemini config + Cursor stop + 脚本 project-dir/emit 四家泛化 + HOOK_DEBUG + 自动化脚本测试）→ 相位2 文案（删 why-no-hooks + 引用清理、bootstrap 三链路、exit-ritual board-AUTO 移出 agent、preflight/protocol/landing/status/session-flow hook-primary 重写、保行为紧致 diff 自检）→ 相位3 spec 收编（auto-land 标 superseded、两 rollout 并入）→ 相位4 每家 Phase0 live 实证门（resync 后新会话，未过停地板）
<!-- /AUTO -->
