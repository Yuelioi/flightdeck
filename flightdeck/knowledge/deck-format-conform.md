# Deck format conform（strict formatter）· 现状

> 落地于 deck-format-conform plan（2026-06-20，7 任务）。原 spec graduate 至此；历史动机/张力见 git 历史。

## 一句话

flightdeck 格式一直演进（cockpit 字段重命名、recorded-config 字段、退役 toggle），**老 deck 不自动跟上**。不出「升级指南」，只给一个对标当前 canonical 模板的 **strict formatter**：缺的补、多的删，像 `gofmt`，不是迁移框架。

## 两趟：脚本做形，AI 填义

| 趟 | 谁 | 动作 |
|---|---|---|
| 脚本趟（确定性） | `flightdeck_conform.py` / `.js` | 删非 schema frontmatter · stamp rules 记录式配置 · 补 cockpit/rules 缺失 section（**append-only**）· 打印缺必填字段 worklist |
| AI 趟（判断） | `/flightdeck:conform` skill | 读全文重塑 cockpit/rules 到模板（标签归一、删非标 section，**值保留**）· 按 worklist 逐文件补 `when_to_read` / `applies_to` / `summary` 等 |

口诀：**脚本做形，AI 填义，`archive/` 与杂目录免管。**

## 作用域

- **根 2 文件** `cockpit.md` + `rules.md`：细致档——frontmatter + section 结构都管。
- **标准 folder 非 archive 文件**：`specs/` `plans/` `incidents/` `checklists/` `docs/`——只管 frontmatter。
- **排除、不碰**：
  - `archive/`——冻结历史。
  - `references/`——**IMPORTED_KIND**：与 `flightdeck_index` 同判据（`WALK_FOLDERS = FOLDER_KIND − IMPORTED_KINDS`）。decks 在此 vendoring 整个上游仓（如 ReMe / claude-mem），其 `.md` 的 frontmatter（`jupytext` / `kernelspec` / `name` / …）不是我们的，机械删会毁上游。**这是 plan 执行期定的取舍**（dry-run 实证）。
  - 杂目录 / 非标准 folder——不在范围（顶多 walkaround 出 stray 提示）。

## 脚本趟细节

- **frontmatter 删多余**：每文件按其 kind 的**合法字段集**（required + 全部 optional）过滤，集外字段删。合法集编码在脚本里（per-kind set），由 `test_flightdeck_conform.py` 的 drift-guard 测试钉死——改字段集必须改测试 = 有意编辑。真相源 = `protocol.md § Frontmatter field reference` + `templates.md` 各 kind schema，**不新造**。保留合法可选（`note`/`supersedes`/`synced`…）；删 `portable`、退役 toggle、拼错字段。
- **rules.md 记录式配置 stamp**：缺才补，已有值绝不覆盖——`version: 3.0`、`runtime: <探测 uv>python>node 或 --runtime>`、`agents_md: off`，按 canonical 顺序插在闭合 `---` 前。
- **cockpit/rules section 骨架**：**append-only**，缺的 canonical section 补 `- (none)` 占位（`## In Progress` 带 `<!-- AUTO:inprogress -->` markers）；**从不删/不重排** section——删非标 / 改标签是 AI 趟。
- **worklist**：`<relpath>\t<missing-required-field>`，sorted，交给 AI 趟。

## 两模式

- 默认 = apply + 写。
- `--check` = 干跑：打印计划改动 + worklist，写零，deck 非完全 conformant 时 exit 1（镜像 `flightdeck_index --check`）。

## 不变量 / 取舍

- **无登记表、无历史、无 undo**：删了不留备份；cockpit 标签归一靠 AI 对模板重塑，不靠「旧→新」迁移表。
- **不可逆 → dry-run 优先**：非 git deck 删了无回滚。skill 默认先 `--check` 看 diff 再 apply；git deck 先确认工作树干净使 apply 成可审 diff。
- **删的时机由用户控**：formatter 见非 schema 即删、不判语义。退役一个仍在干活的字段（如 `portable` 还在做母版分发），用户须**先让接管者就位再删**（`portable` → 先让 `synced` / shared-knowledge 母库接管分发）。formatter 不替用户判断顺序。

## 与 walkaround 的关系

walkaround 是 **audit-only**（只浮现 drift、从不写）。本 formatter 是**修复路**——独立动作（脚本 + AI），不是 walkaround 内嵌的 fix。**Audit 16**（cockpit 字段结构 conformance）报 drift，`/flightdeck:conform` 一趟修复。

## 落点 / parity

- 新脚本 `scripts/flightdeck_conform.py` + Node twin `.js`，byte-parity（codepoint sort、LF、`--runtime` 注入确定性），由 `test_parity.py::ConformParity` 钉死。脚本无 wall-clock 日期（故不受 [new-default-date-local-vs-utc](../incidents/new-default-date-local-vs-utc.md) 影响）。
- skill `skills/conform/SKILL.md`：编排两趟 + AI 重塑规则 + 不可逆/dry-run 注意 + `─── 🩹 conform ───` banner。
