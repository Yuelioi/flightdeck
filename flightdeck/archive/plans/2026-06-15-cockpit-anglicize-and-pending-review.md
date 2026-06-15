---
status: done
summary: 按 spec 落地：脚本+测试原子核(lint/index/new/hooks)先行 → scaffold/templates 模型 → skills 散文 → 外圈文档 → dogfood 同步+verify → landing
last_updated: 2026-06-16
implements: specs/2026-06-15-cockpit-anglicize-and-pending-review.md
---

# Execute: anglicize cockpit headers + Pending Review + drain rules

设计见 [spec](../specs/2026-06-15-cockpit-anglicize-and-pending-review.md)。**字符串契约**（全程一致）：
`进行中→In Progress` · `下一步→Next` · `关键上下文→Key Context` · `Hanging tasks→Hanging Tasks` · 新 `Pending Review`；
specs INDEX 分组头 `### 待启动（idea）→### Backlog (idea)` · `### 进行中·完成（active·done）→### Active · Done`；
AUTO 锚 `<!-- AUTO:inprogress -->` **不变**。段序 `In Progress → Next → Key Context → Pending Review → Hanging Tasks`。

## Progress

current: Task 6 — landing（待用户拍板 待复核↔Pending Review 决策 + 英文名后执行）  [Task 1-5 done: 全 28 文件改完, lint/index/160 测试绿, dogfood+AGENTS 同步]

## Tasks

### Task 1 — 脚本 + 测试原子核（必须同改，否则中途红）

- `scripts/flightdeck_lint.py` L65-68：header regex `进行中→In Progress`、`下一步→Next`。
- `scripts/flightdeck_index.py`：specs 分组 emit 串（L233/235）+ docstring 引用（L192-194/242 等）改英文。
- `scripts/flightdeck_new.py` L149：print 串 `## 进行中→## In Progress`。
- `hooks/_context.sh` + `hooks/stop`：`## 下一步` 锚提取 → `## Next`。
- `scripts/tests/test_flightdeck_lint.py`、`test_flightdeck_index.py`、`test_hooks.py`：fixture/断言里硬编码的中文 header 串同步改。
- **关口**：`uv run pytest scripts/tests/` 绿（`test_hooks.py` 17 失败=WSL 环境噪音，非回归，按既有 incident 判）。

### Task 2 — scaffold + templates（模型契约）

- `scaffolds/full/flightdeck/cockpit.md`：段名英文化 + 新增 `## Pending Review`（`- (none)`），段序如上。
- `skills/preflight/templates.md` §cockpit：模板块改英文段名 + 新增 Pending Review；Rules 增两条——(a) Pending Review 语义/drain（拍板或 landing 确认即删行、非阻塞、主观 vs verify 客观）；(b) 累积段排水通则 + Key Context 逐条「清理 when / 收缩 when」+ 沿用 80 行硬顶。

### Task 3 — skills 散文（引用段名 + 新增行为）

- 纯改名：`status/SKILL.md` · `preflight/SKILL.md`+`protocol.md`+`exit-ritual.md`+`folder-semantics.md` · `launch/SKILL.md` · `new/SKILL.md` · `_shared/bootstrap.md`。
- 改名 + 加行为：
  - `landing/SKILL.md`：drain 步（landing 时清理 Key Context stale 条 + 确认/drain Pending Review）。
  - `walkaround/SKILL.md`：非阻塞 INFO（Key Context 疑似 stale / 单段超长），不阻塞、不动「校验在 walkaround / 判断在 landing」边界。
  - `emit-agents-md/SKILL.md`：从 cockpit 取段的 emit 逻辑改用新英文段名。

### Task 4 — 外圈文档

- `README.md` · `README.zh.md`（散文留中文，引用段名用新英文）· `docs/architecture.md` · `TEST_PLAN.md` · `.github/PULL_REQUEST_TEMPLATE/manifest-verification.md`。
- `CHANGELOG.md`：加一条破坏性变更条目（段名英文化 + Pending Review + drain 规则）。

### Task 5 — dogfood 同步 + verify

- 本仓 `flightdeck/cockpit.md`：段名英文化（内容仍中文）+ 加 `## Pending Review`。
- 重新 emit 本仓 `AGENTS.md`（`/flightdeck:emit-agents-md`）。
- `uv run scripts/flightdeck_lint.py flightdeck`（或等价）→ 绿；`uv run pytest scripts/tests/` → 绿（按既有噪音判）。
- `wc -m` 抽查热路径未显著膨胀。

### Task 6 — landing

- `/flightdeck:landing`：更新 cockpit `Next`/`Active focus`，归档 spec/plan（done 后），本地 commit（**不 push**）。
