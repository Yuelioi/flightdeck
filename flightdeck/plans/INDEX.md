# plans/ — INDEX

<!-- AUTO:plans -->
- [2026-06-03-model-v4-rollout.md](2026-06-03-model-v4-rollout.md) — active — model-v4 分 6 phase 实施——数据模型真相源 → flightdeck_index 扩展(+测试) → 4 skill 行为 → scaffolds/emit/MIGRATION → dogfood 迁移本仓库 → 验证收尾；并入 3.0
- [2026-06-03-scriptable-mechanical-layer-rollout.md](2026-06-03-scriptable-mechanical-layer-rollout.md) — done — 机械层脚本化 rollout —— INDEX-regen 接进 landing/walkaround/status 双轨 + rules scripts 开关 + 版本 guard + walkaround lint 子命令；3 phase 全完成（lint=flightdeck_lint.py，Audit 1/4/5/7/8）
- [2026-06-04-new-artifact-entrypoint.md](2026-06-04-new-artifact-entrypoint.md) — active — 实现 /flightdeck:new + flightdeck_new.py——TDD 建脚本（kind→folder 常量表、按-kind frontmatter、命名 dateless/dated、参数校验报错、调 flightdeck_index regen + status-aware stdout），再建 skills/new/SKILL.md（fast path + 权威撰写契约 fallback），接发现钩子（protocol 节 + emit 模板行 + description），验证 + dogfood，最后文档 + 发布提醒
- [2026-06-04-preflight-slim-launch-split.md](2026-06-04-preflight-slim-launch-split.md) — active — 实现 preflight 瘦身 + 拆出 /flightdeck:launch——新建 launch skill（搬 setup.md）、重写 preflight（重定向 Branch-0 / 删重复检查 / 2 列 catalog / 被动 git 表 / 版本 bump 优先级）、删 setup.md、改两条 description、交叉引用 doc-sweep；验证靠现有 pytest + index --check + dogfood + walkaround。清单自动发现无需注册，CHANGELOG 留发布时写
<!-- /AUTO -->
