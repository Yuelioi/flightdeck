---
status: done
summary: 抓 markdown 多行 Edit 的"静默结构丢失"（标题/区块被替换跨度吞掉，link/anchor 检查抓不到）；把结构检查并进 scriptable lint。动机=本会话 cockpit `## Next session` 标题被 reorder Edit 误删
last_updated: 2026-06-06
---

# 结构性 Edit 守卫（structural-edit guard）

> 本 spec 同时**就是**这条 bug 的记录（不另开 incident，避免"同一事实两处"反模式）。

## Problem / 动机（本会话真实 case）

reorder cockpit `## Next session` 列表时，一个多行 `Edit` 的 `old_string` **跨进了 `## Next session` 标题**，`new_string` 只重排了条目却**没把标题补回** → 标题被静默删除，items 裸挂在 `Active focus` 下。两轮后我手动 re-read cockpit 才发现。

**为什么没被自动抓到**：本会话新建的 anchor/link 校验器只查 `[..](x.md#anchor)` 是否解析——**缺失的标题不是坏链接**，所以它静默漏过。`flightdeck_index.py` 只重生 AUTO 块，也不管标题。**没有任何机械检查覆盖"该在的结构块不见了"。**

## Root cause（wrong process）

多行 Edit 的 `old_string` 一旦跨越结构边界（标题、`## Section`、fenced block 边界），`new_string` 必须显式保留这些边界——但没有任何检查强制/验证这点，全靠人记得 re-read。可复发：本项目做大量多行 Edit。

## 候选方案（下个对话定）

1. **lint 里加"结构清单"校验**（推荐，归 [scriptable lint](2026-06-03-scriptable-mechanical-layer-design.md) Phase 3）：对已知文件类型断言必备结构块——`cockpit.md` 必有 `## Next session` / `## Hanging tasks`；skill `SKILL.md` 必有 frontmatter `name`/`description`；等。缺失 → 报错。轻量、确定性、脚本可做。
2. **anchor-checker PoC 升级**：现有 ~40 行 Python 顺带扫"标题集相对上次提交是否少了"（git diff 维度）——但需要 git 基线、较脆。
3. **纯纪律**：协议里写"跨结构边界的 Edit 后必 re-read"——便宜但不可靠（正是这次失效的东西）。

倾向 **方案 1**：与 lint 子命令天然同源（dangling-ref / status 合法性 / stray-file 已在其 scope），加一条"必备结构块"断言即可。

## 设计（已定 2026-06-06）

选 **方案 1**，scope 收敛为**只 `cockpit.md`**（最对症 bug、低误报；其余 deck 文件结构由 AUTO / index-drift 间接守）。`flightdeck_lint.py` 新增一个 audit，沿用现有 5 个 audit 的 `_finding` 模式，不动其它脚本。

- **常量** `REQUIRED_SECTIONS = {"cockpit.md": [...]}`（dict 便于将来扩展，现仅 cockpit）。
- **必备块**（按权威模板，对所有 deck 通用——排除 dogfood 专有的 `## Note on dogfooding`）：
  - `## 进行中` 标题 **+ `<!-- AUTO:inprogress -->` … `<!-- /AUTO -->` 锚点对**（regen 契约，最该守）
  - `## 下一步`
  - `## Hanging tasks`
- **`audit_required_structure(deck)`**：cockpit.md 不存在 → 跳过（不崩，deckless 由别处管）；缺任一必备块 → `_finding("required-structure", "CRITICAL", cockpit, …)`（CRITICAL = blocking，与 dangling-ref 同级，因缺块会让 landing/status 的 regen 损坏）。
- **匹配**：行首正则 `^## 进行中\s*$`（multiline、容尾随空格）；AUTO 锚点对各自存在性单独断言。
- **接入** `lint()`；severity 进现有 blocking 聚合。

> 旧候选里"skill `SKILL.md` 必有 name/description"**不纳入**——lint 跑在 deck 上、不扫 repo 的 `skills/`，且 SKILL 契约归工具自测（`SkillContractConsistencyTest` 一类）。

## Related

- [scriptable-mechanical-layer](2026-06-03-scriptable-mechanical-layer-design.md) —— lint 子命令是实现归属
- [token-reduction](2026-06-03-token-reduction-design.md) —— anchor-checker PoC 来源（同批 QA 发现 dangling link）
