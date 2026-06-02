---
git: true                  # false → 跳过 git 对账/commit
emit_agents_md: true       # false → emit-agents-md 不输出
disabled_folders: []       # 关掉的文件夹（不建议/不审计）
disabled_gates: []         # 关掉的 gate
model_invocable: [status]  # 允许模型自调的仪式；这里开 status（landing/preflight/walkaround/emit 仍手动）
status_auto: [start, land] # status 的可选转换：start→active、done+land（land 仍逐次确认）
---

## House rules

Dogfood：本项目用自身验证 flightdeck 2.1 的 `status` 仪式与软配置面。
所有 `applies_to:` 必须指向 flightdeck 项目路径（`skills/`、`scaffolds/`、`adapters/` 等），不得用 `general`。
