# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-07 by 月离 (相位3 收编 commit 补全（ff7868e 漏的归档件内容半边补在 7b4fcc2）；`.gitignore` + 删 2 份 tri-review debrief + 清死链已提交（53505b6/9edb9d8），工作区干净。相位1–3 全 done，仅剩相位4 live 实证（resync 后新会话，做不了停地板）。历史详 git log。)
**Active focus**: flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。**核心卖点=随时可关对话、下次 preflight 干净接手、上下文不丢**；载体 checkpoint + soft-landing + auto-land 执行层（注入入场 + Stop board-sync）+ HISTORY 移除/gitignored-deck 接缝 均已实施，待 resync 部署 + live 复验。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-06-end-of-turn-soft-landing.md](specs/2026-06-06-end-of-turn-soft-landing.md) — end-of-turn 若有知识增量,自动跑 landing 的知识+状态落盘子集并输出「已保存」标记,让用户随时可安全关闭对话、上下文不丢;soft-landing 不 commit、不归档(commit/归档/晋升闸都是 full landing 的尾巴),landing 幂等重跑只补差集
- [2026-06-07-hook-primary-refactor.md](specs/2026-06-07-hook-primary-refactor.md) — 四家 hook 趋同后的大重构——给 Codex/Gemini 补真 hook、Cursor 补 stop（机制 A：每家一份小 config + 共享 session-start/stop/run-hook 脚本），四家吃满 SessionStart 注入 + Stop board-sync；删 why-no-hooks（理由已入 cross-host-hooks）；全 skill 文案以 hook 为主路径重写、删无-hook 双路径对冲与「仅 Claude 焊/Codex 退指令文件/未实证」措辞，保留知识分类归 agent + 一行环境降级地板；保行为紧致 protocol/templates/folder-semantics；收编 auto-land-executor + soft-landing + 2 rollout，取代部分标 superseded
- [2026-06-07-hook-primary-refactor-rollout.md](plans/2026-06-07-hook-primary-refactor-rollout.md) — 把 hook-primary 大重构落地的逐文件实施：相位1 机制（Codex/Gemini config + Cursor stop + 脚本 project-dir/emit 四家泛化 + HOOK_DEBUG + 自动化脚本测试）→ 相位2 文案（删 why-no-hooks + 引用清理、bootstrap 三链路、exit-ritual board-AUTO 移出 agent、preflight/protocol/landing/status/session-flow hook-primary 重写、保行为紧致 diff 自检）→ 相位3 spec 收编（auto-land 标 superseded、两 rollout 并入）→ 相位4 每家 Phase0 live 实证门（resync 后新会话，未过停地板）
<!-- /AUTO -->

## 下一步

- **#1 ✅ write-gate-examples 完成**：spec+plan 已实施、done、归档（protocol § Write gate 加 skip-list+✅/❌、exit-ritual 加独立 body 质量小节、refactor spec 加边界注记锚点）。写门/分类启发/body 段已定稿，hook refactor Phase2 按锚点跳过。
- **#2 执行 hook rollout（当前·先行）**：执行 `plans/2026-06-07-hook-primary-refactor-rollout`。**相位1 机制 ✅ + 相位2 文案 ✅ + 相位3 收编 ✅**（Task 全 commit，2.6 无可压跳过；163 测试绿；auto-land spec+rollout done+archive+supersedes、soft-landing-rollout 完成归档、soft-landing spec 保 active）。**仅剩相位4 = 每家 Phase0 live 实证门**：resync 进各宿主缓存后**新会话**手动跑（Claude/Codex/Gemini/Cursor 注入到达 + 回合末 board `--check` clean + 缺 deck/bash/python 静默）；过了才把该家"待 Phase 0 实证"措辞翻最终态。**本会话做不了（hook 只在 resync 后新会话触发）——停在此地板。**
- **相位3 模型坑（已记）**：plan 原写"标 status superseded"，但 workflow 无此状态 → incident `workflow-has-no-superseded-status`；正确=done+archive+新工件 supersedes 反向边，已照此执行。
- **本轮新并入（外部记忆系统借鉴，用户拍板）**：① Cursor 注入改 `.cursor/rules/*.mdc` 规则文件为**主路径**（稳定加载>优雅加载，Task 1.7）；② cockpit `## 关键上下文` 槽（#2，Task 2.7）；③ 失败/弯路捕获入 incidents（#4，Task 2.8）。**单独 backlog**：#1 写门负例（纯 prompt 低风险）、#7 恢复回归测试（待恢复模型稳定再做，首个核心价值行为测试）。

## 关键上下文

- **相位1–3 全 done**，仅剩**相位4 live 实证**（resync→新会话手动跑各家最小矩阵；见 plan Phase 4）。
- hook 文件：`hooks/{session-start,stop,_context.sh}` + `hooks/hooks-{codex,gemini,cursor}.json`；测试 `scripts/tests/test_hooks.py`（`uv run pytest scripts/tests/`，163 passed）；调试 `FLIGHTDECK_HOOK_DEBUG=1`。
- 全 skill 非-Claude hook 叙事标"待 Phase 0 实证"——相位4 过了才由各家收尾步翻最终态。
- `.gitignore`（cursor `.mdc` 投影忽略 + `.claude`）+ 删 2 份 tri-review debrief（含清死链）已提交（`53505b6`/`9edb9d8`）。工作区现干净。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
