## House rules

### Project conventions

Dogfood：本项目用自身验证 flightdeck 的 status 仪式与软配置面。
所有 `applies_to` 必须指向 flightdeck 项目路径（`skills/`、`scaffolds/`、`adapters/` 等），不得用 `general`。

发布面（`skills/`、`templates`、README、banner、字段标签）一律英文（国际化）；用户 deck 内容随用户语言。
未发布前，所有新工作并入当前版本（现 3.0 alpha），不另问并入哪个版本。
公开文档（README / deck）措辞专业、不过度宣称——卖点不得超出协议语义。

de-scope 红线：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。详 `docs/descope-baseline.md`。
测试/度量：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。`test_hooks.py` 在 WSL bash 遮蔽 Git Bash 时失败 = 环境噪音（见 incidents/wsl-bash-shadows-git-bash-in-tests.md）。

### Rules

- 本仓库默认只本地 commit；**`git push` 需用户显式批准**——AI 不主动推送，用户明确说「push」时方可执行（首例：v3.0.0-alpha.2 发版，2026-06-19）。
