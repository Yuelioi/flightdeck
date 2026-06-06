# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-06 by 月离 (本会话：**设计并实施 soft-landing 特性**——end-of-turn 有知识增量→自动跑 landing 知识+状态落盘子集 +「💾 上下文已保存」标记，**不 commit、不归档**，landing 幂等重跑只补差集。brainstorm→spec→plan→子代理逐 task 改 4 skill（exit-ritual signal3/三档表/标记/自评done安全阀 · landing Modes 三档 · protocol House Rule+Lifecycle · status 划界）+ dogfood session-flow；两轮外部 AI 评审 disposition 折进 spec `## 评审纪要`，final 全局 review 的 4 Important fix。另立 2 篇 docs（spec-lifecycle / session-flow）。spec+plan **留 active** 待 resync+live 复验后批准 done。)
**Active focus**: flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。**核心卖点=随时可关对话、下次 preflight 干净接手、上下文不丢**；载体 checkpoint + **soft-landing** 已设计实施，待 resync 部署 + live 复验。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-06-end-of-turn-soft-landing.md](specs/2026-06-06-end-of-turn-soft-landing.md) — end-of-turn 若有知识增量,自动跑 landing 的知识+状态落盘子集并输出「已保存」标记,让用户随时可安全关闭对话、上下文不丢;soft-landing 不 commit、不归档(commit/归档/晋升闸都是 full landing 的尾巴),landing 幂等重跑只补差集
- [2026-06-06-soft-landing-rollout.md](plans/2026-06-06-soft-landing-rollout.md) — 把 end-of-turn soft-landing(知识落盘+「已保存」标记、不commit不归档、landing 幂等)铺进 exit-ritual/landing/protocol/status 4 个 skill + session-flow dogfood doc 的逐文件实施步骤
<!-- /AUTO -->

## 下一步

- **resync + reload**：把本会话改的 skill（soft-landing 的 exit-ritual/landing/protocol/status + 早先 checkpoint/`folder-semantics.md`）同步进 plugin 缓存并重载，让 soft-landing + checkpoint 对下个会话 live 生效。
- **live 复验 soft-landing**（end-of-turn 知识增量 → 自动落盘 +「已保存」标记、纯状态→checkpoint 静默、无增量沉默）+ checkpoint 子路径；复验通过 → 批准 `specs/2026-06-06-end-of-turn-soft-landing` + `plans/2026-06-06-soft-landing-rollout` done → 归档。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
