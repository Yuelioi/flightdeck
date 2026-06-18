---
version: 3.0
shared_master: $FLIGHTDECK_SHARED_MASTER
---

## House rules

### Project conventions

Dogfood：本项目用自身验证 flightdeck 的 status 仪式与软配置面。
所有 `applies_to` 必须指向 flightdeck 项目路径（`skills/`、`scaffolds/`、`adapters/` 等），不得用 `general`。

发布面（`skills/`、`scaffolds/`、`templates`、README、banner、字段标签）一律英文（国际化）；用户 deck 内容随用户语言。
未发布前，所有新工作并入当前版本（现 3.0 alpha），不另问并入哪个版本。
公开文档（README / deck）措辞专业、不过度宣称——卖点不得超出协议语义。

### Rules

- 本仓库只本地 commit，**绝不 `git push`**（即便用户批准提交也不推；推送由维护者手动执行）。
