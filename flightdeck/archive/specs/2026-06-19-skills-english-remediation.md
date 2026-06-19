---
status: done
summary: 实测 skills/ 有 184 处中文漂移（10 文件），违反 rules.md 发布面英文红线。已止血：CLAUDE.md 强化对比 + version-bump 硬发版门。本 spec = 一次性翻译整顿：把 10 个 skill 文件翻成纯英文。scope 只管 ship 面（skills/scaffolds/templates/README/banner/字段标签），项目内 CLAUDE.md / flightdeck dogfood deck / 用户 deck 全不管。结构坑：中文 heading 被别处锚链（改名连带改链）、中文约定名 ## 评审纪要 多处引用（统一英文名+更新全部引用）。翻译只动语言不动语义。
last_updated: 2026-06-19
---

# skills/ 纯英文整顿（发布面 i18n 止血 + 翻译）

> 3.0 alpha 打磨。一次性 remediation（不 graduate——耐用规则已在 `rules.md`，本 spec 是清账）。

## 背景 / 动机

实测 `rg -lP '\p{Han}' skills scaffolds`：`scaffolds/` 干净，`skills/` **10 个文件、184 处中文**，是近几轮工作（cockpit-bloat-control / AI 化精简 / shared-knowledge-sync）一路把中文散文漏进 ship 面的累积漂移。违反 `rules.md` `### Project conventions` 的「发布面一律英文（国际化）」红线。

**根因**：CLAUDE.md 只说「用中文和我沟通」，AI 一边对话中文、一边手滑把中文带进 skill 编辑。且规则只是散文、无机械检查——和 cockpit-bloat-control 的核心洞察同构（「纪律是散文，没环节查它被没被违反」），所以 184 处才能堆出来。

**已止血（本 spec 前置，已落）**：
- `CLAUDE.md` 强化「对话中文 / 发布面英文」对比 + 点名根因。
- `checklists/version-bump.md` 加硬发版门 `rg -lP '\p{Han}' skills scaffolds` 必须为空 + Verification 项。

本 spec = 把存量 184 处翻干净，让发版门转绿。

## Scope（红线只管 ship 面 — 用户「其他无所谓」的钉死）

**必须纯英文**（ship 给所有用户）：`skills/` · `scaffolds/` · `templates` · `README.md` · banner · 字段标签（散文 / heading / anchor / 示例全英文）。

**不管语言**（项目内部 / 用户私有）：
- 本仓 `CLAUDE.md`（dogfood 仓的沟通偏好，中文）。
- `flightdeck/` dogfood deck 内容（`specs/` `incidents/` `checklists/` `docs/` 等，中文 OK——它们是「维护 flightdeck 工具」的记录，不随产品 ship）。
- `README.zh.md`（本就是中文翻译版）。
- 用户自己项目的 deck（随用户语言）。

判据：**会不会 ship 进插件包给别的项目用** → 会则英文，不会则随意。

## 待翻译清单（10 文件，实测计数）

| 文件 | 中文行数 | 备注 |
|---|---|---|
| `skills/sync/SKILL.md` | 42 | 整篇基本中文 |
| `skills/preflight/protocol.md` | 35 | 含被锚链的中文 heading（见结构坑） |
| `skills/preflight/templates.md` | 32 | |
| `skills/preflight/exit-ritual.md` | 29 | cockpit 两 spec 会先重写其大段（见落地序） |
| `skills/walkaround/SKILL.md` | 27 | 整篇 audit 中文 |
| `skills/landing/SKILL.md` | 6 | |
| `skills/new/SKILL.md` | 5 | |
| `skills/status/SKILL.md` | 3 | 含 `## 评审纪要` 引用 + 中文锚链 |
| `skills/preflight/folder-semantics.md` | 3 | 定义 `## 评审纪要` 约定名 |
| `skills/preflight/SKILL.md` | 2 | 英文夹中文小注（如「(零写入)」） |

## 结构坑（不能盲扫，须原子处理）

1. **中文 heading + 别处锚链**：`protocol.md` 有 `§ 验证非阻塞`（`#验证非阻塞-non-blocking-verification`）等中文标题；`status/SKILL.md` / `exit-ritual.md` 用中文锚点引它。**改 heading 名必须同一改全部 anchor**，否则 walkaround Audit 7 断链。流程：先 grep 出所有指向该中文 anchor 的链接 → heading 改英文 → 链接同步改 → Audit 7 复验零断链。
2. **中文约定名 `## 评审纪要`**：`folder-semantics.md` 定义、多个 skill（exit-ritual / landing 等）引用「fold disposition into the reviewed spec's `## 评审纪要`」。**统一改英文名**（提议 `## Review notes`）→ 更新定义处 + 全部引用处。注意：这是 ship 面的*约定名*，但它指导的是*用户 deck 里的 section*——deck 内容随用户语言，故约定名英文、用户实际写中文 section 也行；skill 散文里的示例用英文名。
3. **英文夹中文小注**：如 `(零写入)`、`status附加标记`、`verify: <一行怎么验>`——就地译，别漏。

## 翻译原则

- **只动语言、不动语义**：逐文件翻译，行为/契约/结构零改动。不趁机重构（重构走 cockpit 两 spec）。
- **术语一致**：建一张小术语表（如 退场=exit / 着陆=landing / 出场=on-exit / 字面量=literal / 门控=gated / 排空=drain / 逼问=prompt-to-resolve / 漂移=drift …），全 skills 统一，避免同词多译。
- **每文件翻完即 `rg -P '\p{Han}' <file>` 自验零残留**；全部翻完 `rg -lP '\p{Han}' skills scaffolds` 必须空。

## 落地序（关键——本 spec 在今天 3 个 spec 里**最后**执行）

cockpit 两 spec（field-redesign → accumulator）会**先重写** `exit-ritual.md` / `protocol.md` / `templates.md` 的大段（且按 CLAUDE.md 已强化的规则，新内容直接写英文）。所以本 i18n 整顿**放最后**，只需清扫那两 spec **没动到的剩余中文**——最小化返工（别去翻 cockpit spec 即将重写的段落）。

执行序：`field-redesign` → `accumulator-convergence` → **本 spec（i18n）**。

## 验证

- `rg -lP '\p{Han}' skills scaffolds` 返回空（= version-bump 发版门转绿）。
- `/flightdeck:walkaround` Audit 7 零断链（中文 heading 改名后 anchor 全部解析）。
- 抽读 sync / walkaround（翻得最多的两篇）确认英文通顺、语义未漂。
- `uv run pytest scripts/tests/`（纯文案翻译，预期不动测试；若某测试 assert 了中文串则同步改）。

## 非目标（YAGNI）

- **不**翻 `flightdeck/` dogfood deck / 本仓 `CLAUDE.md` / `README.zh.md` / 用户 deck（scope 外）。
- **不**借翻译重构 skill 行为/结构（只换语言）。
- **不**新增机械 lint 到 shipped `flightdeck_lint.py`（「skills 英文」是 dogfood-repo 专属，不是通用 deck 规则；守卫住在 version-bump 发版门 + 可选 repo CI，不进 ship 的 walkaround/lint）。

## 沿革

- 用户发现 walkaround/sync 用中文 → 扫出全 skills 184 处漂移 → 拍板：写整顿 spec + 「skills 必须纯英文、项目内 CLAUDE/flightdeck deck 无所谓」。
- 前置止血（CLAUDE.md 强化 + version-bump 硬门）已落；本 spec 清存量。
- 与今天另两 spec（cockpit field-redesign / accumulator）独立，但**排最后**执行以蹭其英文重写、省返工。
