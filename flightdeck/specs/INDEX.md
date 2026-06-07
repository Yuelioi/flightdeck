# specs/ — INDEX

<!-- AUTO:specs -->
### 进行中·完成（active·done）
- [2026-06-07-hook-primary-refactor.md](2026-06-07-hook-primary-refactor.md) — active — 四家 hook 趋同后的大重构——给 Codex/Gemini 补真 hook、Cursor 补 stop（机制 A：每家一份小 config + 共享 session-start/stop/run-hook 脚本），四家吃满 SessionStart 注入 + Stop board-sync；删 why-no-hooks（理由已入 cross-host-hooks）；全 skill 文案以 hook 为主路径重写、删无-hook 双路径对冲与「仅 Claude 焊/Codex 退指令文件/未实证」措辞，保留知识分类归 agent + 一行环境降级地板；保行为紧致 protocol/templates/folder-semantics；收编 auto-land-executor + soft-landing + 2 rollout，取代部分标 superseded
- [2026-06-06-end-of-turn-soft-landing.md](2026-06-06-end-of-turn-soft-landing.md) — active — end-of-turn 若有知识增量,自动跑 landing 的知识+状态落盘子集并输出「已保存」标记,让用户随时可安全关闭对话、上下文不丢;soft-landing 不 commit、不归档(commit/归档/晋升闸都是 full landing 的尾巴),landing 幂等重跑只补差集
<!-- /AUTO -->
