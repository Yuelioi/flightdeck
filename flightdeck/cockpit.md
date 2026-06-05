# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-06 by 月离 (本会话：①探讨大型项目 docs 组织 → `folder-semantics.md` 加「知识规模化组织」节（四形态/golden-path/横切列/map 生成+核对/防漂移 + 3 条 anti-pattern，**build 输入**）；②探讨并**放弃** preset-library 预设库（收益低/维护要为通用性背书/用户心智负担大——见 memory）；③**锁定核心卖点=可恢复上下文**（随时可关对话、下次 preflight 干净接手、上下文不丢），落成 `execution-checkpoint` spec（idea，停机位）。改了 build input（folder-semantics）→ resync+reload 后 live 复验。)
**Active focus**: flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。**核心卖点锁定=随时可关对话、下次 preflight 干净接手、上下文不丢**；围绕它设计 `execution-checkpoint`（plan/task 边界看板同步）。specs/ 现 1 idea。

## 进行中

<!-- AUTO:inprogress -->

<!-- /AUTO -->

## 下一步

- `execution-checkpoint`（idea，停机位）已成型——决定：flip→active 走 writing-plans，或先聊定 plan 开口（形态＝landing 子路径 vs 文档化 self-invoke 行为、checkpoint 提不提交）。
- 本会话改了 `folder-semantics.md`（build 输入）→ resync + reload 后 live 复验那节文档指南。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
