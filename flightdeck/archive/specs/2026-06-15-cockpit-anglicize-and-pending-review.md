---
status: done
summary: cockpit 段名全英文化（进行中/下一步/关键上下文→In Progress/Next/Key Context）+ 新增 Pending Review 段 + 给累积段(Pending Review·Key Context)立逐条排水纪律；破坏性 deck 格式变更，alpha 期推进
last_updated: 2026-06-16
---

# Cockpit model: anglicize headers + Pending Review section + accumulator-drain rules

## 背景 / 动机（alpha 反馈）

来自 YHFish dogfood 的现场信号：标准 cockpit 模型（`进行中`/`下一步`/`关键上下文`/`Hanging tasks`）少了两类「家」，用户在现场**手工补**了 `## 待复核` + `## 待验证` 两段——最强的设计缺口证据。同时 `关键上下文` 只有整体约束（80 行硬顶 / 只放 literals），**没有逐条生命周期规则**，会无限累积成垃圾抽屉。

两个病根其实是一个：**cockpit 里会「累积」的非-AUTO 段都缺排水（drain）规则**。本 spec 一并解决，并顺手把公开发布的 cockpit 模板从中英混排收成全英文（deck 是公开 GitHub 文档，模板应专业）。

## 决策（已与用户拍板）

1. **`Pending Review` 作为独立常驻段**（非并入 verify / Hanging Tasks）。
2. **改工具本体**：scaffold + templates + landing 协议 + 全部接线，所有未来 deck 受益；本仓 dogfood 同步。
3. **全量英文化**：段名 + lint regex + index emit 串 + 各 skill 散文 + hooks + 测试 + 外圈文档。
4. **走 spec → plan → 执行**（本文件即 spec）。

## Part 1 — cockpit 段名英文化

段名映射（cockpit 段）：

| 现（中文） | 改（English） | 备注 |
|---|---|---|
| `进行中` | `In Progress` | AUTO 段；锚 `<!-- AUTO:inprogress -->` 不变（脚本靠锚不靠段名） |
| `下一步` | `Next` | cockpit anchor / hooks 提取这段 |
| `关键上下文` | `Key Context` | |
| `待审核`（新） | `Pending Review` | 见 Part 2 |
| `Hanging tasks` | `Hanging Tasks` | 仅规范大小写 |

**段序**（拍板预览）：`In Progress → Next → Key Context → Pending Review → Hanging Tasks`。

script-emit 串（specs INDEX 分组头，`flightdeck_index.py`）一并英文化：

| 现 | 改 |
|---|---|
| `### 待启动（idea）` | `### Backlog (idea)` |
| `### 进行中·完成（active·done）` | `### Active · Done` |

**结构英文、内容用户语言**：只英文化段名/结构串；用户写在段下的内容仍是其工作语言（本仓 dogfood 内容继续中文）。

## Part 2 — `Pending Review` 段 + 累积段排水纪律

### `Pending Review` 语义

- **是什么**：AI 自认完成、等用户拍板过目的产出队列。契合「AI 全自动驱动 + 用户定期回看」用法。
- **行格式**：`- [<artifact/topic>] <一行：干了什么 · 怎么看/怎么验>`
- **drain（清理时机）**：用户拍板，或下次 landing 经用户确认 → **删行**；空 → `- (none)`。
- **与邻段区别**：Hanging Tasks **阻塞** landing；Pending Review **不阻塞**（可带着 land）。verify 是**客观**（跑测试/构建）；Pending Review 是**主观**（人过目拍板）。
- **不强制、非 AUTO**：与 Key Context / Hanging Tasks 同级——lint **不**硬性要求此段（lint critical 只保 `In Progress` + AUTO 锚 + `Next`）；agent 判断维护，非脚本生成。

### 累积段排水纪律（本 spec 核心新增）

通则：**凡 cockpit 里会累积的非-AUTO 段，必须有 drain 条件**，否则退化为垃圾抽屉。

- **Pending Review**：drain 见上。
- **Key Context 逐条规则**：
  - **清理 when**：该 literal 指向的目标已归档 / 已落进 `docs/` / 下一会话不再需要 → 删该条。
  - **收缩 when**：单条过长 → 压成一行指针（链接 + hook）；多条同源 → 合并。
  - 整体仍 **80 行硬顶**（沿用既有）。
- **执行时机 = landing**：landing 本就按判断重写 cockpit，drain 是判断步，归 landing。checkpoint 轻量、不强制 drain。
- **walkaround**：加一条**非阻塞 INFO**（Key Context 疑似 stale 或单段超长），不阻塞、不改「校验只在 walkaround、判断在 landing」的既有边界。

## 落点 / 爆炸半径（≈28 文件 / 189 处）

1. **模板/脚手架**：`scaffolds/full/flightdeck/cockpit.md`；`skills/preflight/templates.md`（§cockpit + 各引用）。
2. **脚本**：`flightdeck_lint.py`（header regex L65-68，critical 校验）；`flightdeck_index.py`（specs 分组 emit 串 L233/235 + docstring 引用）；`flightdeck_new.py`（print 串 L149）。
3. **skills 散文**：landing · status · walkaround · preflight(SKILL/protocol/exit-ritual/folder-semantics) · emit-agents-md · launch · new · `_shared/bootstrap.md`。
4. **hooks**：`hooks/stop` · `hooks/_context.sh`（提取 `## 下一步` 锚）。
5. **测试**：`test_flightdeck_lint.py` · `test_flightdeck_index.py` · `test_hooks.py`（硬编码中文 header 串同步改）。
6. **外圈文档**：`README.md` · `README.zh.md` · `AGENTS.md` · `CHANGELOG.md` · `docs/architecture.md` · `TEST_PLAN.md` · `.github/PULL_REQUEST_TEMPLATE/manifest-verification.md`。`README.zh.md` 散文可留中文解释，但引用的段名用新英文名。

## 破坏性变更处置

- 现存中文-header deck 会过不了新 lint（critical）——**破坏性格式变更**。alpha 期明确允许（cockpit anchor：「alpha 期间仍可破坏性调整」）。
- **无双语 compat lint**（违反 de-scope「无向后兼容」）。
- 本仓 dogfood cockpit 同步英文 header（内容仍中文）。
- YHFish 等用户自有 deck 由用户自迁；3.1 再建就地迁移（de-scope：无向后兼容，3.1 in-place migration）。
- **AGENTS.md**：emit-agents-md 从 cockpit 取 `进行中`/`下一步`，改名后 emit 逻辑同步改；本仓 `AGENTS.md` 重新 emit。

## 待定（请你 review 时拍）

- **英文名**：`In Progress` / `Next` / `Key Context` / `Pending Review`。若想要别的（`Next Step` / `Resume Context` / `Awaiting Review` …）此处定。
- **graduate**：本 spec 是「本次变更的设计稿」，cockpit 模型契约的常驻家在 `templates.md`/`protocol.md`（本变更会更新它们），spec 落地后归档——故**倾向不 graduate**。若你要留作常驻参考再标。

## 执行中发现 / 决策修订（2026-06-15）

**既有 `待复核` 概念碰撞**：flightdeck 早有 `待复核` = knowledge `stale` 状态注脚（疑似过期/新产出未验证）；`exit-ritual.md` 已指引把 `待复核: <file>` 浮到 cockpit「`## 下一步` 下或专门 `## 待复核` 子段（如果有）」。YHFish 手工加的 `## 待复核` 即 follow 此指引——与本 spec 的 `Pending Review` 高度重叠。决策：

- **`Pending Review` = 「等你过目」的统一常驻家**：收 AI 产出待拍板 + 既有 stale-knowledge 浮出的 `待复核` 项；把原模糊归宿（下一步下/可选子段）收成一个明确的家。`exit-ritual` 的 stale 浮出改指向 `## Pending Review`。
- **`verify:` / `⚠未验证`（客观跑测）保持独立**，不并入。
- **`stale=待复核` 状态注脚保持中文、不动**——属知识状态语义，不在「cockpit 段名英文化」范围（翻译整份 templates.md 中文注释超纲）。

## 验证

- 改完跑 `uv run pytest scripts/tests/`。注意本机 `test_hooks.py` 17 失败 = WSL bash 遮蔽 Git Bash 的环境噪音（非回归，见 incidents/wsl-bash-shadows-git-bash-in-tests）。
- `wc -m` 作 token 代理，确认英文化未显著膨胀热路径。
