# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-06 by 月离 (本会话：**落成 checkpoint 特性并归档**——子代理驱动逐 task 实现 5 处 skill 改（exit-ritual canonical 定义 + landing Modes + plan `## Progress current:` 指针 + templates/folder-semantics/protocol 收口），双重评审通过、跨文件一致、`current:` 指针经 index 复跑实证为 body-only（脚本零改动）。spec+plan 已 done→archive。评审拦下一条 shipped-skill 死链 → 落 incident。)
**Active focus**: flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。**核心卖点=随时可关对话、下次 preflight 干净接手、上下文不丢**；其载体 checkpoint 特性已落成归档，待 resync 部署 + live 复验。

## 进行中

<!-- AUTO:inprogress -->

<!-- /AUTO -->

## 下一步

- **resync + reload**：把本会话改的 5 处 skill（含 checkpoint + 早先 `folder-semantics.md`）同步进 plugin 缓存并重载，让 checkpoint 对下个会话 live 生效；之后 live 复验 checkpoint 子路径与「知识规模化组织」那节文档指南。
- 选下一个 3.0 完善点（specs/ 现已清空，按需 `/flightdeck:new` 起新 idea）。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
