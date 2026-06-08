# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-07 by 月离 (graduate + 知识保鲜 spec+plan 用户签收 done + landing 归档；实施=15 task subagent-driven 全绿（176 测试、lint/index/verdict clean）、final reviewer 3 处跟进已修、cache 已 resync（build_stamp current）。进行中现仅剩 hook-primary spec+rollout，卡相位4 live 实证。历史详 git log + archive/。)
**Active focus**: flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。**核心卖点=随时可关对话、下次 preflight 干净接手、上下文不丢**；载体 checkpoint + soft-landing + auto-land 执行层（注入入场 + Stop board-sync）+ HISTORY 移除/gitignored-deck 接缝 均已实施，待 resync 部署 + live 复验。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-07-hook-primary-refactor.md](specs/2026-06-07-hook-primary-refactor.md) — 四家 hook 趋同后的大重构——给 Codex/Gemini 补真 hook、Cursor 补 stop（机制 A：每家一份小 config + 共享 session-start/stop/run-hook 脚本），四家吃满 SessionStart 注入 + Stop board-sync；删 why-no-hooks（理由已入 cross-host-hooks）；全 skill 文案以 hook 为主路径重写、删无-hook 双路径对冲与「仅 Claude 焊/Codex 退指令文件/未实证」措辞，保留知识分类归 agent + 一行环境降级地板；保行为紧致 protocol/templates/folder-semantics；收编 auto-land-executor + soft-landing + 2 rollout，取代部分标 superseded
- [2026-06-08-nonblocking-verify-preflight-slim.md](specs/2026-06-08-nonblocking-verify-preflight-slim.md) — 验证由阻塞门降为非阻塞标记——复用 stale（拓宽为 待复核：疑似过期 或 新产出未验证），AI 可自断 done(未验证) 照常归档清看板、验证欠债经 cockpit 待验证行在 preflight 浮出、可逆复活；并 preflight 输出瘦身（folder INDEX 仍读只显计数 + docs 载入上下文不刷屏）——兑现随时关不丢上下文
- [2026-06-07-hook-primary-refactor-rollout.md](plans/2026-06-07-hook-primary-refactor-rollout.md) — 把 hook-primary 大重构落地的逐文件实施：相位1 机制（Codex/Gemini config + Cursor stop + 脚本 project-dir/emit 四家泛化 + HOOK_DEBUG + 自动化脚本测试）→ 相位2 文案（删 why-no-hooks + 引用清理、bootstrap 三链路、exit-ritual board-AUTO 移出 agent、preflight/protocol/landing/status/session-flow hook-primary 重写、保行为紧致 diff 自检）→ 相位3 spec 收编（auto-land 标 superseded、两 rollout 并入）→ 相位4 每家 Phase0 live 实证门（resync 后新会话，未过停地板）
<!-- /AUTO -->

## 下一步

- **✅ graduate + 知识保鲜 已实施+归档**（spec+plan 进 `archive/`）：knowledge status `{active, stale, obsolete}`、`obsolete`=knowledge 版 done 排水、`supersedes` 纯溯源非钉扣、`superseded`/`superseded_by` 退役；graduate（结构性设计稿 done 时本体变身常驻 docs）、`when_to_update`→`stale` 双仪式保鲜（锚点=git `Flightdeck-Sync:` trailer）。脚本：`archivable_obsolete` / `match_signature` 扩扫 archive / `audit_when_to_update` / stale ⚠ 渲染 / `last_anchor_ref`+`changed_since_anchor`。详见 archive 双件 + git log。cache 已 resync——**新会话**才吃到新 skill/脚本行为。
- **#2 执行 hook rollout（当前·先行）**：执行 `plans/2026-06-07-hook-primary-refactor-rollout`。**相位1 机制 ✅ + 相位2 文案 ✅ + 相位3 收编 ✅**（Task 全 commit，2.6 无可压跳过；163 测试绿；auto-land spec+rollout done+archive+supersedes、soft-landing spec+rollout 均 done+archive）。**仅剩相位4 = 每家 Phase0 live 实证门**：resync 进各宿主缓存后**新会话**手动跑（Claude/Codex/Gemini/Cursor 注入到达 + 回合末 board `--check` clean + 缺 deck/bash/python 静默）；过了才把该家"待 Phase 0 实证"措辞翻最终态。**本会话做不了（hook 只在 resync 后新会话触发）——停在此地板。**
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
