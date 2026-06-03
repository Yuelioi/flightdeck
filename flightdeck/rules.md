---
version: 3.0
disabled_folders: []
---

## House rules

### Project conventions

Dogfood：本项目用自身验证 flightdeck 的 status 仪式与软配置面。
所有 `applies_to` 必须指向 flightdeck 项目路径（`skills/`、`scaffolds/`、`adapters/` 等），不得用 `general`。

### Autonomy overrides

<!-- migrated from model_invocable:[status] — preflight/landing/walkaround/emit-agents-md were omitted (manual); status stays self-invocable (default). status_auto:[start,land] / commit_mode:confirm / git / emit were all at 3.0 defaults, so dropped. -->
preflight: don't self-invoke; I run it manually.
landing: don't self-invoke; I run it manually.
walkaround: don't self-invoke; I run it manually.
emit-agents-md: don't self-invoke; I run it manually.
run scripts with python3.
