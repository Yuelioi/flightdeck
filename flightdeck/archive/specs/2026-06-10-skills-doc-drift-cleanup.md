---
status: done
last_updated: 2026-06-11
summary: 新模型全量 review skills/ 发现 6 组失实/矛盾：root INDEX 残留引用、hook 相位4 已实证但仍标 pending、preflight 补偿路径残留违反纯读零写、version/walkaround 权责矛盾、pre-3.0 向后兼容文案残留违反 descope 基线、new 的 kind 清单与 chart 命名不一致；另 3 项设计层疑点（applies_to tags vs paths、landing SKILL 超重、断锚点）
---

# skills 文档失实清扫

2026-06-10 用新模型（Fable 5）全量重读 `skills/` 12 个文件 + 对照 `flightdeck/docs/descope-baseline.md` 的 review 发现。分两档：A = 确定失实/自相矛盾（直接改）；B = 设计层疑点（需用户决策）。

## A. 确定失实（应改）

### A1. root INDEX 残留引用（drop-root-index 已 land，scaffold/dogfood 均无此文件）

- `skills/status/SKILL.md:53` — "Recompute … the root `flightdeck/INDEX.md` count line" 是死指令
- `skills/preflight/protocol.md:215` — 整段描述 root INDEX 存在（"sub-folder directory + global status summary"）
- `skills/preflight/protocol.md:235` — "Reachability entries: cockpit.md / INDEX.md / rules.md" 入口集合应去掉 root INDEX（folder INDEX 才是入口）
- `skills/preflight/folder-semantics.md` — 布局图含 `├── INDEX.md  # Root index…` 行；Routing model 段同样列 INDEX.md 为入口
- `skills/landing/SKILL.md:50,53` — smoke-check 把根 `INDEX.md` 列为合法 entry file；现在根 INDEX 反而该算 stray

### A2. hook 相位4 已 live 实证（2026-06-10 签收）但仍标 pending

- `skills/landing/SKILL.md:27` — "live-verified on Claude, others pending Phase 0"
- `skills/preflight/exit-ritual.md:395` — "Codex/Gemini/Cursor are pending Phase 0 live verification"
- `skills/preflight/protocol.md:326` — 同句
- 处置：按果断删减——直接删 hedge（四家已实证），不留"已验证"赘述

### A3. preflight 补偿路径残留（违反 descope「preflight 纯读零写、不做补偿检查」）

- `skills/preflight/protocol.md:266-268` — stale detection "dual-ritual (landing=primary, preflight=read-only compensating)" 整段
- `skills/preflight/protocol.md:332` — graduate "preflight is the compensating path (catches landing-not-run windows)"
- `skills/preflight/exit-ritual.md:75` — "Preflight is the compensating path if landing didn't run"
- `skills/landing/SKILL.md:37` — 同句
- `protocol.md` 字段表 `when_to_update` 行 — "exit-ritual + preflight stale detection"
- 事实基准：preflight SKILL 本体已无 stale/graduate 步骤；exit-ritual:78 "preflight 入场不再翻 stale" 才是对的

### A4. version / walkaround 权责矛盾

- 真相（walkaround SKILL Don't-do + descope 基线）："version 是 launch 写入的静态戳，walkaround 不读、不写、不 bump"
- 与之矛盾的残留：
  - `protocol.md:17` "walkaround is the sole writer"
  - `protocol.md` 字段表 version 行 "Written by: launch (init) / walkaround only (bump + migrate)；walkaround: Audit 10"（Audit 10 现在是 summary/last_updated 聚合，编号也错）
  - `protocol.md` Ritual responsibilities 表 walkaround 行 "version bump/migrate only (sole version writer)"
  - `templates.md:13` "(walkaround reads/writes this)" 及 Rules 段 "walkaround is the only command that reads and writes version"
  - `folder-semantics.md` "walkaround CRITICAL if rules.md/version missing" — 13 个 audit 里并无此项检查

### A5. pre-3.0 向后兼容文案残留（违反 descope「无向后兼容子系统」；3.0 未发布、不存在真实老 deck）

- `protocol.md:24` "read but ignored through 3.x and removed at 4.0 … walkaround offers any structural migration"
- `protocol.md:34` "(Pre-3.0 structured keys … read between steps 1 and 2 — honored for 3.x compatibility)"
- `protocol.md` 字段表末行（7 个 pre-3.0 keys 的 compat 行）
- `templates.md` Rules 段 "Compatibility: pre-3.0 keys read but ignored…"
- `walkaround` Audit 6 "pre-3.0 遗留 superseded 可容忍"、Audit 1 退役旧值列表中的 pre-3.0 值（后者可留作非法值校验，措辞去 compat 化）
- 标准-phrase 表 "legacy `commit without asking` phrase still matches"（`protocol.md:54`）同属此类

### A6. kind 清单 / `chart` 命名不一致

- `skills/new/SKILL.md` kind 表含 6 种（含 `doc`），但 `protocol.md` § Authoring 与 `emit-agents-md` 模板块写 "(spec / plan / incident / checklist / chart)" 漏 `doc`
- `emit-agents-md` 模板句 "Don't hand-write deck artifacts or place them under `docs/`" 与 `new` 的 `doc` kind 直接矛盾——且这句会写进每个用户的 AGENTS.md
- kind 名 `chart` 违反 naming iron-rule（charts/→references/ 已主流化）；候选：kind 改名 `reference`（脚本 `flightdeck_new.py` 同步）

## B. 设计层疑点（需决策）

### B1. `applies_to` 双重语义：tags（路由）vs paths（stale 检测）

- `templates.md` 教短标签（"`[parser, recursion]` beats `[code-quality]`"）；`exit-ritual` Step 3c 的 stale 翻转用「变更路径 ∩ `applies_to` 声明的源路径」集合交集
- 标签永远不会与文件路径相交 → 按模板写 tags 的 deck，stale 检测静默失效（dogfood deck 是因 House Rule 强制 applies_to=路径才能工作）
- 候选：明文规定 applies_to 可混装 tags+paths、交集只对 path-like 条目生效；或路由/保鲜拆成两个字段

### B2. landing SKILL.md 超重（自称 thin entry-point，实际 ~113 行）

- Step 3a 单段 400+ 词；Recurrence sweep wiring 与 exit-ritual Step 5a 双份近重复；step 0 的 git 推断全文与 protocol/templates 三处重复
- 违反热/冷预算铁律（SKILL.md=最小祈使清单，解释下沉冷路径）；候选：压成清单+指针，正文归 exit-ritual

### A7. flightdeck_new.py 知识件日期前缀与文档矛盾（执行中追加发现）

- 脚本 `DATELESS = {"doc"}`，给 incident/checklist/reference 都加了 `YYYY-MM-DD-` 前缀；而 folder-semantics/templates 明文「知识件一律 `<topic>.md` 无日期」（反模式表专门点名 `2026-05-23-bug.md`），存量 incidents 也全是无日期
- 处置：`DATELESS = KNOWLEDGE`，测试先行改断言（incident/reference 均 dateless）

### B3. 零散小项

- `exit-ritual.md:393` 锚点断链：`../landing/SKILL.md#modes--full-vs-checkpoint`，landing 实际标题已是 "Modes — full · soft-landing · checkpoint"
- `preflight/SKILL.md` step 1 git 推断简写 "Infer git from deck root `.git`" 漏 gitignore 检查，与 protocol 完整定义不一致
- `landing/SKILL.md` 步骤编号顺序 3 → 3b → 3c → 3z → 3a 反直觉（3z 排在 3a 前），可读性问题

## 处置纪要（2026-06-10）

- **已修**：A1–A7 全部 + B3 前两项（断锚点、preflight git 推断措辞）。A6 采用 kind 改名 `reference`（含 `flightdeck_new.py` + 契约测试 + README 双语 + emit 模板句重写）；A7 顺带修正 `DATELESS = KNOWLEDGE`。emit 模板那句改为「Don't hand-write deck artifacts or hand-derive their paths」，与 doc kind 不再矛盾。
- **顺带修**：`test_flightdeck_lint.py::test_main_exits_zero_when_clean` 测试隔离缺陷（deck 直接建在 `%TEMP%` 根、`main()` 默认 `repo_root=deck.parent` 扫到共享 Temp 的杂散 md）——deck 嵌套一层隔离；cockpit 与 `checklists/commits.md` 两条真断链（后者指向已归档 incident，改指 archive 路径）。
- **B1 定案（第二轮）**：`applies_to` 允许混装「路由标签 + 源路径」——含 `/` 的条目=源路径、参与 stale 检测（前缀匹配变更路径）；纯词条目只做路由；要保鲜至少放一条路径条目。最小成文化、不加新字段。落点：protocol 字段表 + § Stale detection、exit-ritual Step 3c、templates 两处 frontmatter 注释 + incident rules、deck `docs/descope-baseline.md`。
- **B2 完成（第二轮）**：`landing/SKILL.md` 整体重写——113 行压至约 75 行，细则全部指针化归 exit-ritual；步骤 0–11 顺序编号（B3 第三项的 3z/3a 乱序随之消失）；保住外部引用的两个标题锚点（`#modes--full--soft-landing--checkpoint`、`#recurrence-sweep-wiring`）；exit-ritual/protocol 两处按编号引用 board-sync 的句子改按名引用，防再漂移。
- **环境记录**：`test_hooks.py` 17 个失败 = 本机 PATH 把 bash 解析到 WSL（System32），见 [incidents/wsl-bash-shadows-git-bash-in-tests.md](../incidents/wsl-bash-shadows-git-bash-in-tests.md)；其余 138 测试全绿、`--check` clean。
