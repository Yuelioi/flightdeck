# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-06 by 月离 (删 HISTORY 流水账 + 修 gitignored-deck 的 git-mode 接缝：land move 改普通 mv、git 判定加 check-ignore、cockpit `Last updated` 收紧；新 incident `gitignored-deck-git-mode-seam`。143 测试通过。)
**Active focus**: flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。**核心卖点=随时可关对话、下次 preflight 干净接手、上下文不丢**；载体 checkpoint + soft-landing + 本轮 HISTORY 移除/gitignored-deck 接缝 已实施，待 resync 部署 + live 复验。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-06-end-of-turn-soft-landing.md](specs/2026-06-06-end-of-turn-soft-landing.md) — end-of-turn 若有知识增量,自动跑 landing 的知识+状态落盘子集并输出「已保存」标记,让用户随时可安全关闭对话、上下文不丢;soft-landing 不 commit、不归档(commit/归档/晋升闸都是 full landing 的尾巴),landing 幂等重跑只补差集
- [2026-06-06-soft-landing-rollout.md](plans/2026-06-06-soft-landing-rollout.md) — 把 end-of-turn soft-landing(知识落盘+「已保存」标记、不commit不归档、landing 幂等)铺进 exit-ritual/landing/protocol/status 4 个 skill + session-flow dogfood doc 的逐文件实施步骤
<!-- /AUTO -->

## 下一步

- **resync + reload**：把两批 skill 改动同步进 plugin 缓存重载——① soft-landing（exit-ritual/landing/protocol/status + checkpoint/`folder-semantics`）② 本轮 HISTORY 移除 + gitignored-deck git-mode 接缝（protocol/exit-ritual/landing/launch/templates/folder-semantics/init/scaffold）——让二者对下个会话 live 生效。
- **live 复验**：① soft-landing（end-of-turn 知识增量→自动落盘+标记、纯状态→checkpoint 静默、无增量沉默）+ checkpoint 子路径；② 在一个**真·gitignored deck** 上跑 landing，确认不写 HISTORY、用 `mv` 不报 `not under version control`、INDEX 一次到位。通过 → 批准 `specs/2026-06-06-end-of-turn-soft-landing` + `plans/2026-06-06-soft-landing-rollout` done → 归档。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
