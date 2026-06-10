---
status: done
summary: 把每命令品牌图标 spec 逐落点落地：protocol.md 建权威字形表 → 7 命令各改运行时报告行加 emoji（launch🛠️/preflight🛫/walkaround🔍/status🔄/landing🛬/new✍️/emit🌉）→ 末轮一致性核对（字形↔表三列、scaffolds/脚本零改动 grep）+ 目标终端目视；纯 SKILL.md/protocol.md prose 编辑，无脚本/测试改动
last_updated: 2026-06-10
implements: archive/specs/2026-06-08-stage-brand-glyphs.md
---

# 每命令品牌图标——逐落点落地

> **For agentic workers:** REQUIRED SUB-SKILL: 用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐 task 实施。步骤用 `- [ ]` 复选框跟踪。

**Goal:** 给 7 个 flightdeck 命令各配一枚彩色 emoji 品牌图标，只改各 skill 运行时主报告/完成行；字形映射表落 `skills/preflight/protocol.md` 作文档级单一真相源。

**Architecture:** 纯 prose 编辑——改 `skills/<cmd>/SKILL.md` 的报告行 + 在 `protocol.md` 增一节权威表。无自动化测试（横幅是模型 prose，非脚本 stdout），故每 task 用 `rg` 字面核对替代单元测试，末轮加目标终端人眼目视。`scaffolds/` / `templates.md` / `scripts/`（含 `tests/`）一律不碰。

**Tech Stack:** Markdown（SKILL.md / protocol.md）；`rg`（ripgrep）做字面核对；`git`（本地 commit，**绝不 push**）。

**字形权威表（每 task 以此为准）：**

| 命令 | 图标 | codepoint |
|---|---|---|
| launch | 🛠️ | U+1F6E0 FE0F |
| preflight | 🛫 | U+1F6EB |
| walkaround | 🔍 | U+1F50D |
| new | ✍️ | U+270D FE0F |
| status | 🔄 | U+1F504 |
| landing | 🛬 | U+1F6EC |
| emit-agents-md | 🌉 | U+1F309 |

**通用约定：** 提交信息用**中文**、**不带 emoji 字符**（规避 Windows git 参数编码坑——用命令名描述）；每 task 一个本地 commit，绝不 push；`rg` 找不到串时再 `Read` 该文件按内容定位（行号仅提示、会漂移）。

---

### Task 1: protocol.md —— 建权威字形表（单一真相源，先行）

**Files:**
- Modify: `skills/preflight/protocol.md`（新增一节 `## Brand glyphs (per command)`）

- [ ] **Step 1: 定位插入点**

Read `skills/preflight/protocol.md`，找到末尾的最后一个 `## ` 顶级小节（约定/folder-map 类内容之后）。新节作为**新的顶级 `## ` 小节**追加在其后。

- [ ] **Step 2: 写入新节**（完整内容如下，原样写入）

```markdown
## Brand glyphs (per command)

每个 flightdeck 命令在其**运行时主报告/完成行**带一枚品牌 emoji（仅报告行，不进 deck 文件、不进 scaffolds）。这是**文档级单一真相源**——各 skill 硬编码自己那枚，新增命令照此表配字形。`✈️`（U+2708 + FE0F）保留作项目 wordmark（README 标题），**不**作命令字形。

| 命令 | 图标 | codepoint | 语义 |
|---|---|---|---|
| launch | 🛠️ | U+1F6E0 FE0F | 造甲板 / 首次建机 |
| preflight | 🛫 | U+1F6EB | 起飞前就绪 |
| walkaround | 🔍 | U+1F50D | 绕机巡检 / 审计 |
| new | ✍️ | U+270D FE0F | 新建工件 |
| status | 🔄 | U+1F504 | 状态流转 |
| landing | 🛬 | U+1F6EC | 着陆归档 |
| emit-agents-md | 🌉 | U+1F309 | 跨工具桥 |

效力边界：被动文档约定，无程序强制——改某命令字形须人工同步本表（preflight 不自动校验）。
```

- [ ] **Step 3: 核对**

Run: `rg -F "## Brand glyphs (per command)" skills/preflight/protocol.md`
Expected: 命中 1 行。再 `rg -c "U+1F6EB|U+1F6EC|U+1F50D|U+270D|U+1F504|U+1F6E0|U+1F309" skills/preflight/protocol.md` 应为 7（七枚 codepoint 各一）。

- [ ] **Step 4: Commit**

```bash
git add skills/preflight/protocol.md
git commit -m "feat(protocol): 增 per-command 品牌字形权威表（单一真相源）"
```

---

### Task 2: launch —— 报告行 🛠️（裸 ✈ U+2708 → 🛠️）

**Files:**
- Modify: `skills/launch/SKILL.md`（Final report 行，约 :29）

- [ ] **Step 1: 改字形**

把 Final report 行开头的**裸 `✈`（U+2708，无 FE0F）**替换为 `🛠️`：

- old: `> ✈ Deck created at \`flightdeck/\` (full layout, version \`<v>\`).`
- new: `> 🛠️ Deck created at \`flightdeck/\` (full layout, version \`<v>\`).`

（只换行首那一个字形，行内其余不动。）

- [ ] **Step 2: 核对**

Run: `rg -F "🛠️ Deck created at" skills/launch/SKILL.md`
Expected: 命中 1 行。
Run: `rg -F "✈ Deck created" skills/launch/SKILL.md`
Expected: **无命中**（旧裸 ✈ 已从报告行清除）。README 的 `✈️` wordmark 不在本文件、不受影响。

- [ ] **Step 3: Commit**

```bash
git add skills/launch/SKILL.md
git commit -m "feat(skill): launch 报告行换品牌图标（build，取代旧裸 ✈）"
```

---

### Task 3: preflight —— 报告行 🛫（2 处同串）

**Files:**
- Modify: `skills/preflight/SKILL.md`（散文收尾句约 :69 + Output format 块末行约 :98）

- [ ] **Step 1: 加前缀（两处一并）**

把字符串 `Preflight complete (read-only)` 的**两处**出现都前缀 `🛫 `：

- old（散文 :69）：`... hand off: "Preflight complete (read-only). Say 'go' to execute item #1."`
  new：`... hand off: "🛫 Preflight complete (read-only). Say 'go' to execute item #1."`
- old（Output 块 :98）：`Preflight complete (read-only). → Say "go" to execute item #1.`
  new：`🛫 Preflight complete (read-only). → Say "go" to execute item #1.`

实现：对 `Preflight complete (read-only)` 做 replace_all → `🛫 Preflight complete (read-only)`（仅这两处出现，无其他）。

- [ ] **Step 2: 核对**

Run: `rg -F "🛫 Preflight complete (read-only)" skills/preflight/SKILL.md`
Expected: 命中 **2 行**。
Run: `rg -F "Preflight complete (read-only)" skills/preflight/SKILL.md | rg -v "🛫"`
Expected: **无命中**（没有漏网的未加前缀版本）。

- [ ] **Step 3: Commit**

```bash
git add skills/preflight/SKILL.md
git commit -m "feat(skill): preflight 完成行加品牌图标（takeoff）"
```

---

### Task 4: walkaround —— 报告标题 🔍（findings + clean 两版同串）

**Files:**
- Modify: `skills/walkaround/SKILL.md`（Output format 报告标题，约 :190 findings 版 + :210 clean 版）

- [ ] **Step 1: 标题加图标（两处一并）**

把报告标题 `=== /flightdeck:walkaround report ===` 的**两处**出现都改为 `=== 🔍 /flightdeck:walkaround report ===`。`✅ Clean.` 那行**不动**。

实现：对 `=== /flightdeck:walkaround report ===` 做 replace_all → `=== 🔍 /flightdeck:walkaround report ===`（仅这两处）。

- [ ] **Step 2: 核对**

Run: `rg -F "=== 🔍 /flightdeck:walkaround report ===" skills/walkaround/SKILL.md`
Expected: 命中 **2 行**。
Run: `rg -F "=== /flightdeck:walkaround report ===" skills/walkaround/SKILL.md | rg -v "🔍"`
Expected: **无命中**。

- [ ] **Step 3: Commit**

```bash
git add skills/walkaround/SKILL.md
git commit -m "feat(skill): walkaround 报告标题加品牌图标（inspect）"
```

---

### Task 5: status —— 流转确认 print 🔄（2 条 done print）

**Files:**
- Modify: `skills/status/SKILL.md`（Step 6 的两条 done print，约 :74 / :75）

> **落地更正（对 spec）**：status **无** formal 的 active-flip 打印行（Step 5a 只 regen cockpit，不打用户可见行）。故 🔄 只挂这 **2 条 done print**，**不**新发明 active-flip 行（与"不过度造约定"一致）。spec 验证项把 status 触点视为这 2 条即可。

- [ ] **Step 1: 两条 print 内加前缀**

- old（:74）：`then print: \`[判定: <理由>; 待验证: <怎么验>; done + verify]\``
  new：`then print: \`🔄 [判定: <理由>; 待验证: <怎么验>; done + verify]\``
- old（:75）：`print: \`[判定: <理由>; 无需验证; done]\``
  new：`print: \`🔄 [判定: <理由>; 无需验证; done]\``

即把每个 print 反引号内的 `[判定` 前加 `🔄 `。

- [ ] **Step 2: 核对**

Run: `rg -F "🔄 [判定" skills/status/SKILL.md`
Expected: 命中 **2 行**。
Run: `rg -F "print: \`[判定" skills/status/SKILL.md`
Expected: **无命中**（两条 print 都已加前缀；注意匹配反引号后紧跟 `[判定` 的未加前缀残留）。

- [ ] **Step 3: Commit**

```bash
git add skills/status/SKILL.md
git commit -m "feat(skill): status 流转确认 print 加品牌图标（transition）"
```

---

### Task 6: landing —— 着陆横幅 🛬（顶部新增 + soft-land marker）

**Files:**
- Modify: `skills/landing/SKILL.md`（Output format 块顶部约 :80 + modes 表 soft-land marker :21）

- [ ] **Step 1a: Output format 块顶部新增横幅行**

在 Output format 代码块的**第一行内容**前插入 `🛬 已着陆`：

- old: `Hanging tasks: none / [resolved X / blocking on Y]`
- new:
  ```
  🛬 已着陆
  Hanging tasks: none / [resolved X / blocking on Y]
  ```

（即 `🛬 已着陆` 成为该报告块的首行横幅；属**新增文本**，spec 已诚实标注。）

- [ ] **Step 1b: soft-land marker 加图标**

modes 表里 soft-landing 列的 `「已保存」marker` 改为带图标：

- old: `+ 「已保存」marker`
- new: `+ 🛬 已保存 marker`

- [ ] **Step 2: 核对**

Run: `rg -F "🛬 已着陆" skills/landing/SKILL.md`
Expected: 命中 1 行（顶部横幅）。
Run: `rg -F "🛬 已保存 marker" skills/landing/SKILL.md`
Expected: 命中 1 行（soft-land marker）。
Run: `rg -F "「已保存」marker" skills/landing/SKILL.md`
Expected: **无命中**（旧无图标 marker 已替换）。

- [ ] **Step 3: Commit**

```bash
git add skills/landing/SKILL.md
git commit -m "feat(skill): landing 报告顶部横幅 + soft-land marker 加品牌图标（landing）"
```

---

### Task 7: new —— 新增报告约定行 ✍️

**Files:**
- Modify: `skills/new/SKILL.md`（新增 `## Report (one line)` 小节，插在 `## Relationship to landing` 之前）

> new 当前仅有 "It prints the created path"、**无报告横幅**；本 task 新增一行报告约定（spec 已诚实标注为"+1 约定行"，顺带补上 new 缺失的输出指引）。脚本的 `created … at …` 是 Bash 工具结果（过程性 stdout），用户看到的报告由模型这一行承载，不另复述。

- [ ] **Step 1: 插入新节**

在 `## Relationship to landing` 这一行**之前**插入：

```markdown
## Report (one line)

壳建好、正文写入后，给用户一行报告：

> ✍️ 已建 <kind>: <path>

这一行带图标的确认**就是** new 的用户可见报告——不要再单独复述脚本的 `created … at …` 原始 stdout。

```

- [ ] **Step 2: 核对**

Run: `rg -F "## Report (one line)" skills/new/SKILL.md`
Expected: 命中 1 行。
Run: `rg -F "✍️ 已建 <kind>: <path>" skills/new/SKILL.md`
Expected: 命中 1 行。

- [ ] **Step 3: Commit**

```bash
git add skills/new/SKILL.md
git commit -m "feat(skill): new 增报告约定行加品牌图标（authoring）"
```

---

### Task 8: emit-agents-md —— 报告首行 🌉

**Files:**
- Modify: `skills/emit-agents-md/SKILL.md`（Step 6 Report 块首行，约 :106）

- [ ] **Step 1: 首行加前缀**

- old: `AGENTS.md regenerated.`
- new: `🌉 AGENTS.md regenerated.`

- [ ] **Step 2: 核对**

Run: `rg -F "🌉 AGENTS.md regenerated." skills/emit-agents-md/SKILL.md`
Expected: 命中 1 行。
Run: `rg -F "AGENTS.md regenerated." skills/emit-agents-md/SKILL.md | rg -v "🌉"`
Expected: **无命中**。

- [ ] **Step 3: Commit**

```bash
git add skills/emit-agents-md/SKILL.md
git commit -m "feat(skill): emit-agents-md 报告首行加品牌图标（bridge）"
```

---

### Task 9: 末轮一致性 + 范围 + 目视核验（needs-verify 门）

**Files:**
- 只读核验，无文件改动（除可能的 spec/plan 状态由 `/flightdeck:status` 翻转）。

- [ ] **Step 1: 七枚字形各就各位**

Run（逐命令核对字形存在于其 SKILL.md 报告行）：
```
rg -F "🛠️ Deck created at" skills/launch/SKILL.md
rg -F "🛫 Preflight complete (read-only)" skills/preflight/SKILL.md
rg -F "=== 🔍 /flightdeck:walkaround report ===" skills/walkaround/SKILL.md
rg -F "🔄 [判定" skills/status/SKILL.md
rg -F "🛬 已着陆" skills/landing/SKILL.md
rg -F "✍️ 已建" skills/new/SKILL.md
rg -F "🌉 AGENTS.md regenerated." skills/emit-agents-md/SKILL.md
```
Expected: 每条均有命中（preflight 2 行、walkaround 2 行、status 2 行，其余各 1 行）。

- [ ] **Step 2: protocol.md 表 ↔ 实际用字三列一致**

人工对照 `## Brand glyphs (per command)` 表的（命令名 + emoji + codepoint）与上一步七处实际用字，逐枚一致（非仅比 emoji）。

- [ ] **Step 3: 范围零越界**

Run: `git diff --name-only main...HEAD -- scaffolds/ flightdeck/ skills/preflight/templates.md scripts/`
Expected: **仅** `skills/preflight/protocol.md` + 本轮的 spec/plan 工件（`flightdeck/...`）；**不含** `scaffolds/`、`templates.md`、`scripts/`（含 `tests/`）任何改动。
Run: `git diff --name-only main...HEAD -- skills/` 应只列出 8 个文件：`protocol.md` + 7 个 `SKILL.md`。
再人工扫一遍 `scripts/tests/` 有无**部分匹配/正则**断言依赖横幅 prose（预扫结论：命中仅测试方法名，非 prose 断言——复核一次确认）。

- [ ] **Step 4: 目标终端人眼目视（manual，一次性）**

在 Claude Code 终端实跑（或贴出）各报告行，目视确认七枚 emoji 渲染正常——**尤其带 FE0F 变体选择符的 🛠️ / ✍️**（不显示成豆腐块/缺字）。这是 manual 验收项，不保证任意终端。

- [ ] **Step 5: 收口**

七项核验全过后，本 plan 与 spec 即可经 `/flightdeck:status` 翻 `done`（needs-verify：随 `verify: 七处字形已目视、protocol 表三列一致、范围零越界` 字段携带），再由 `/flightdeck:landing` 归档。**status/landing 翻转与归档不在本 plan 手动做**——交仪式。

---

## Self-Review（写完即对 spec 核一遍）

- **Spec 覆盖**：spec §2 落点表 7 命令 → Task 2–8 逐一对应；§3 单一真相源 → Task 1；§4 范围边界 → Task 9 Step 3；§验证 4 项 → Task 9 Step 1–4。无遗漏。
- **占位符**：无 TBD/TODO；每个 edit 给了精确 old→new 串与 rg 核对命令。
- **一致性**：七枚字形（emoji + codepoint）在权威表、各 task、Task 9 核验三处一致；status 的"无 active-flip print"落地更正已写明，与 spec 对齐说明在 Task 5。
