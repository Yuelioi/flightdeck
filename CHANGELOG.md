# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0-alpha.4] — 2026-06-20

launch-recorded-config spec 落地（相 1/2/3）：把「运行时推断 / 处处兜底」换成「launch 一次性记录 / 强制的单条线」。**Breaking**：删 no-git 分支、删手写 markdown 兜底（强制 runtime）、`agents_md` 改读字段不再探文件。本版另并入两件独立工作（未发布前不另起版本）：`/flightdeck:conform`（deck 格式归一器）与 `/flightdeck:sync` 机械化重写（section-single-writer 懒拉）。

### Added
- **记录式配置进 `rules.md` frontmatter** — `runtime`（`uv|python|node`）+ `agents_md`（`auto|off`）与 `version` 同级，runtime 直读不再每会话探测；晋升判据单一可证伪（当且仅当否则需「每会话探测某个外部事实」才升结构化字段），其余偏好（commits / start / nudge…）留 `### Rules` 自由散文。稳态优先级：frontmatter 字段对其管辖 key 永久高于散文。
- **4 个用户可见脚本 Node 移植** — `flightdeck_index` / `flightdeck_init` / `flightdeck_lint` / `flightdeck_new` 各加 `.js`（内置模块对等、**零 npm 依赖**）支持 node-only 用户；`bump_version` 仅保留 Python（用户 skill 从不调用）。
- **Parity 字节对拍防线（spec 级约束）** — `scripts/tests/parity/` 金标 fixture + `test_parity*.py`（24 parity 测试），Python/Node 双实现逐字 diff 必须为空；钉死归一规则（Unicode 码点序、LF、UTF-8 NFC、固定日期格式、稳定 JSON 键序）堵隐性漂移。harness 顺带浮出并修了 Python 参考 3 个真 bug（lint stdout 未强制 UTF-8、`KNOWLEDGE_FOLDERS` 集合序非确定、`_collect_md` 未排序）。
- **`/flightdeck:conform` — deck 格式归一器**（设计 `docs/deck-format-conform.md`）— `scripts/flightdeck_conform.py`/`.js`（byte-parity，`ConformParity` 对拍）走查 deck，按 per-kind 合法字段集 check/apply 收敛 frontmatter（schema-delete 多余键）+ 补 cockpit/rules 缺失段 + stamp `rules.md` 的 `version`/`runtime`/`agents_md`；walkaround **Audit 16** 把 cockpit 字段结构漂移指向 `/flightdeck:conform`；`references/` 作 `IMPORTED_KIND` 排除出走查。
- **`/flightdeck:sync` 机械化（section-single-writer 懒拉）**（设计 `docs/shared-knowledge-sync.md`；`specs`/`plans` `2026-06-20-sync-mechanical-pull`）— 把带时间戳的 AI-merge sync 降级为纯机械模型：母库是 shared 内容唯一写者、consumer 不改 shared，`<!-- flightdeck:shared … -->` 边界锚 + shared-region 指纹定位；`flightdeck_index.py`/`.js` 加 `--sync-pull`（apply + `--check`）、node 端 byte-parity；sync skill 按机械模型重写。

### Changed
- **runtime 强制 → 机械路塌成单条线** — 删各 ritual「无 runtime → 手写 markdown 兜底」双写（exit-ritual / status / landing / new / launch / walkaround）；INDEX/cockpit regen、artifact stamp、机械审计只剩脚本一条线，skill 按 frontmatter `runtime` 拼调用形（`uv run` / `python` / `node`）。
- **launch doctor 体检 + git-init offer** — 探测面收窄为「仅 git 存在性 + runtime 检测」（优先级 `uv` > `python` > `node`），打 `🩺 flightdeck doctor` 体检表逐项正面/负面汇报；缺 repo 时问一句 `git init now? [y/N]`（`y` 帮建、`N` 停），git 没装 / 无 runtime 硬停提示安装；写 `runtime:` / `agents_md:` 并在建完回显记下的设置。（相对原 spec「零提示」有意回调一处 git 提示。）
- **protocol `Rule resolution order`** 加 Runtime dispatch 段；`templates.md` 改「`version` 是唯一结构化字段」断言为多字段。
- **发布面 i18n 收口** — `scripts/` 残留中文译为英文（发布面英文硬门 `rg -lP '\p{Han}' skills scaffolds`）。
- **`commits.md` / `comments.md` 退役 `portable`** — 改由 synced 母库分发（`/flightdeck:sync` vendoring，不再各项目重新播种）；`commits.md` `§通用` 补 shell 传参 + RM/MM 暂存扫描两条。
- **`bump_version.py` 接管 README 版本** — `set`/`--check` 现同步并校验中英 README 的版本徽标 + 警示 banner（只改锚定位点，prose 里的裸 semver 如「the final 3.0.0」不动），堵住「只升 manifest、README 徽标漂移」（本版前 README 徽标停在 `alpha.2` 直到 `alpha.4`）。

### Fixed
- **Node 默认日期 parity** — `.js` 脚本默认日期改用本地时间，与 Python 参考一致（原 UTC 破 byte-parity）。

### Breaking
- **删 no-git 支持** — 贯穿各 skill 的 no-git 分支全删（preflight / landing / status / emit-agents-md / exit-ritual / folder-semantics / protocol / scaffold）；flightdeck 现要求 git，缺 git → launch 直接拒绝提示 `git init`。CI 自动化 / gitignore deck / 临时目录等用例为有意取舍。
- **`agents_md` 改读字段** — `landing` 读 `agents_md` 字段决定是否重生 AGENTS.md，**不再探文件是否存在**；`/flightdeck:emit-agents-md` 变原子动作（建文件 **并**翻 `off→auto`）。语义从「看文件现实」变「看记录意图」——手删 AGENTS.md 但字段仍 `auto` → 下次 landing 重生（有意 UX 锐边，改字段即对齐）。
- **记录 runtime 失效硬失败** — 记录的 runtime 不存在（卸载 / 换机）时，任何需脚本的步骤硬失败中止并报 `⚠ recorded runtime '<x>' not found`，不静默回落每会话重探；preflight 只读仍报板 + 附一行 `⚠ recorded runtime broken`。

## [3.0.0-alpha.3] — 2026-06-19

cockpit 再设计（纯恢复载荷）+ skills 全英文。设计沉淀 `docs/cockpit-design.md`。**Breaking**：cockpit 字段重命名（`Active focus→Focus`、`Last updated→Updated`、加 `Pointers`），存量 deck 与依赖旧字段名的工具/emit 需同步。

### Added
- **cockpit 字段重设计**（`docs/cockpit-design.md`）— 纯恢复载荷原则（pointer-vs-record）：`Updated` 纯戳（无 changelog）、`Focus` 一行标签+链接（无目标/判据）、新 `Pointers` 薄导航行、`Next` 单步+进度移 plan `## Progress`；`In Progress` AUTO 渲染 summary 截断头部（≤80 字，`flightdeck_index.py` `_truncate_inprogress_summary`）。landing Length check 加「角色越界」判据；walkaround **Audit 16** 浮出 cockpit 字段结构/角色 conformance。
- **Key Context 中转暂存生命周期** — Key Context 不再永久驻留：referent 死即 drain（近确定性、自动 + 可 undo）、耐用条目 graduate 到 home-by-kind（`rules.md` / `docs/` / agent 指令文件）。`Pending Review` 加 aged-prompt：跨 ≥1 landing 未签收 → landing 逐条逼问（sign off / keep / drop），签收仍显式。
- **发布面英文硬门** — `checklists/version-bump.md` 加 pre-release gate：`rg -lP '\p{Han}' skills scaffolds` 必须为空，CI 式挡住中文漂回 ship 面。

### Changed
- **skills/ + scaffolds/ 全英文** — 翻译 10 个 skill 文件（散文 / heading / anchor / 示例）；中文约定名改 `## Review notes`、`## Project-specific`、`## Design tradeoffs` 等；中文 heading `验证非阻塞` 改名 `Non-blocking verification` + 全锚点同步（零断链）。`CLAUDE.md` 强化「对话中文 / 发布面英文」对比，点名漂移根因。
- **多 agent 中立** — override 权威序与「常驻 meta 家」去 CLAUDE.md 写死，统一为「项目的 agent 指令文件（`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`，按运行的 agent）」（protocol + templates 三处）。

### Breaking
- **cockpit 字段重命名**：`Active focus→Focus`、`Last updated→Updated`、新增 `Pointers` 行。`emit-agents-md` 改读 `Focus:`（非 `**Active focus**:`）；存量 deck 的旧字段名 + 依赖旧名的脚本/测试需同步（alpha 期允许破坏；3.1 再就地迁移）。

## [3.0.0-alpha.2] — 2026-06-19

cockpit 模型升级（alpha 反馈驱动）。**Breaking**：cockpit 段名全英文化，存量中文-header deck 过不了新 lint——alpha 期可破坏，本仓 dogfood 已同步；其它 deck 用 `/flightdeck:launch` 新建后搬运，或等 3.1 就地迁移。

### Added
- **`## Pending Review` cockpit 段** — AI 自认 done、等用户拍板过目的产出队列（非阻塞、主观，区别于 `verify` 客观）；既有 stale `待复核` 浮出项归入此段，审过即 drain。
- **累积段排水纪律** — 给 `Key Context` / `Pending Review` 立逐条 drain 规则（清理 when：目标已归档/已 graduate/下一会话不需要；收缩 when：长条压成一行指针、同源合并），landing 执行 drain、walkaround 出非阻塞 INFO（新增 Audit 14）。
- **cockpit 出场密度门控 + active 计数提示**（cockpit-bloat-control spec v2）— landing 出场 Length check 从「纯 80 行」升级为「行数 + 逐字段密度」双判据，抓「行少字密」散文膨胀（`Active focus` / `Last updated` ≤~200 字、`Key Context` / `Pending Review` 每条一行 literal），超限 → 门控 trim（非自动截断，守恢复载荷红线）；`## In Progress` active 项 >~5 → preflight/landing 非阻塞「考虑关停部分」提示。
- **`/flightdeck:sync` + 共享知识 vendoring**（shared-knowledge-sync spec + v2）— 跨项目共享 checklist/doc：母库为准、谁新谁赢（比 `last_updated`，无 hash）；vendored 文件标 `synced: true`（无路径别名，消费端 relpath 恒等于母库 relpath）；**母库根固定约定 `~/.flightdeck`**（想放别处用 symlink / `mklink /J` junction，`is_dir()` 跟随；缺席 → `master-missing` 优雅跳过）。下发（pull）+ 显式 `/flightdeck:sync push <路径>` 反向（promote 本地原创 / 回流 locally-ahead，`## 项目覆盖` 永不上推）。**双向可发现**：母库共享文件 frontmatter 带 `consumers`（母库专属，vendor 时剔除），脚本 `--register-consumer` / `--list-consumers`（纯读）/ `--prune-consumers`（保守剔除）维护；`/flightdeck:sync --fanout` 把母库改动串行扇出全下游。事实 = `flightdeck_index.py --sync-status`（`state<TAB>relpath`）+ walkaround Audit 15（relpath 不变量 → dangling、消费端非法 `consumers` 键）；仅 checklist/doc。
- **Act-report-close loop**（act-report-close-loop spec）— 所有 flow 统一末尾 banner（`─── <icon> <flow> ───`，先正文后 banner、一回合一个）；执行回合无增量也出 `[No change]`；统一「翻回 / undo」通道（撤最近着陆单元，跨会话从 git+看板推导）；全生命周期恢复 + 阶段派生。契约真相源 = `protocol § Act-report-close loop`。
- **AI-authored config**（ai-authored-config spec）— `rules.md` `### Autonomy overrides` → `### Rules`：行为偏好改由「用户自然话 → AI 落盘自由文规则」，删 7 个 magic-string 开关目录 + resolution-order 匹配机器。

### Changed
- **cockpit 段名英文化**：`进行中→In Progress`、`下一步→Next`、`关键上下文→Key Context`、`Hanging tasks→Hanging Tasks`；specs INDEX 分组头 `待启动（idea）→Backlog (idea)`、`进行中·完成（active·done）→Active · Done`；AGENTS.md emit 块同步英文。AUTO 锚 `<!-- AUTO:inprogress -->` 不变（脚本靠锚不靠段名）。结构英文、内容仍随用户工作语言。
- **可逆 deck 动作无前置确认门**：status flip / incident→checklist promotion / `--advance-candidates` / 归档 / retire 等可逆动作改为按判断自动执行 + banner 报告 + 可翻回；只有外发（push）仍先问。
- **退场契约**：soft-landing 的「已保存」marker → 统一 banner；「无增量静默」→ banner `[No change]` 一行（纯对话仍不出）。`README` 卖点「零损失」收窄为恢复载荷（cockpit+INDEX+已落盘工件），不含未落盘对话推理。

### Breaking
- cockpit 段名英文化＝破坏性 deck 格式变更：`flightdeck_lint.py` 的 cockpit 结构校验改认英文段名，存量中文-header deck 报 CRITICAL。无双语兼容层（de-scope：无向后兼容，3.1 再就地迁移）。
- **删 magic-string 开关目录**（`commit: ask` / `don't auto-commit` / `status: don't auto start` / `this deck doesn't use git` / `has AGENTS.md but don't auto-regen` 等）+ resolution-order lenient-substring 匹配机器：偏好改走 `### Rules` 自由文。依赖旧短语硬编码的 deck / 脚本 / 测试需改。
- **可逆动作不再先问** + **执行回合恒出 banner**（含无增量）：行为破坏性变更，alpha 期允许；不可逆（push）仍先问，安全面不降。

## [3.0.0-alpha.1] — 2026-06-11

3.0 的首个 **alpha 预发布**——邀请早期试用、收集反馈；正式 3.0.0 之前格式与行为仍可能再次破坏性调整，**不要在生产项目上依赖它**。

自治面收敛 + 主流命名铁律 + 确定性归档判据。**Breaking**：3.0 是新的格式基线（第 0 版），不自动迁移 2.x deck——建议用 `/flightdeck:launch` 新建 deck 后手工搬运 cockpit 内容，见 [MIGRATION.md](MIGRATION.md)。

### Added
- **`docs/` 文件夹** — 自撰常驻技术资料（区别于 `references/` 导入的外部材料）；knowledge 可按 area 嵌套形成 INDEX-of-INDEXes，撑大型项目。
- **incident 错误库生命周期** — 可 grep 的 `## Signature`（4 键放正文，preflight 不读 → 零路由 token）+ 确定性签名指纹去重（`--match-signature`，归一化剥易变 token、保语义键）+ obsolete 退役出路由（退出 INDEX/计数但留盘、仍进匹配）+ 回归复活（landing gated sweep 命中 obsolete 先确认再翻 active）。

### Changed
- **主流命名铁律**：`charts/` → `references/`，`landed/` → `archive/`。航空隐喻只留指令/仪式/cockpit，数据文件夹改主流名，降低首次读者认知摩擦。
- **status⟂location**：`done ≠ archived`。归档判据确定性：无 active 入边（`implements` / `superseded_by`），通过 `--archivable` 检查，才进 `archive/`；`done` 仅表示工作完成，不触发自动归档。
- **done 翻转 end-of-turn 防抖接力 landing**：出厂默认 `status` 将 `done` 检测到后，在当轮结束时自动接力触发 landing（push 先问）；House Rule `landing: nudge on done, don't auto-run` 可将行为降级为仅提示。
- **workflow status 收敛 + `scrapped` 退役**：workflow status 三值 `idea`/`active`/`done`。否决一个工件＝直接删文件（git log 留史、commit body 记一行原因），不再有 `scrapped` 状态值或 `### 已否决` 墓碑分组——消除"留 specs/ 当墓碑"与"计数排除/文档声称不可见"的自相矛盾。
- **git 判定识别"deck 被 gitignore"**：deck 是否走 git 改为"祖先有 `.git` **且** deck 未被 gitignore（`git check-ignore` 为空）"。把 `flightdeck/` 单独 gitignore（常见做法——deck 不进代码库历史）正确判为 deck-级 no-git，即便外层代码仓有 git；不再让 landing 在 git/no-git 间反复横跳。
- **land 搬迁永远用普通 `mv`，绝不 `git mv`**：`git mv` 在被 ignore 的 deck 上会 `fatal: not under version control` 失败、逼出脆弱的即兴补救；普通 `mv` 对被跟踪和 no-git 两种 deck 都成立（被跟踪时随后 commit 自识别 rename）。
- **`Last updated` 收紧为一行短句**：cockpit 的 `Last updated` 括注是"变了什么 + 下一步指针"的一行短语，不再是整段会话流水账（违反它自己"不是会话流水账"的规定、且每次 landing 都涨 token）。

### Removed
- **`archive/HISTORY.md` 落地流水账整条移除**（所有 git 模式）。落地记录＝`archive/` 里被搬进去的文件本身 + `git log`；no-git deck（如被 gitignore 的 `flightdeck/`）也一样靠 `archive/` 文件，不另写日志。最小契约从 3 文件回到 2 文件（`rules.md` + `cockpit.md`）；scaffold 不再预置 `archive/`（首次 land 时按需创建）；`init` 不再有 HISTORY 增删逻辑。

### Breaking
- `charts/` → `references/`，`landed/` → `archive/`：存量 deck 需重命名文件夹及更新内部路径引用。迁移指引见 [MIGRATION.md](MIGRATION.md)。

## [2.3.0] — 2026-06-03

Autonomy release: new decks ship full-auto, a `commit_mode` landing policy, and a more robust Land Routine. Additive and backward-compatible — existing decks keep their current behavior and `version` silently advances 2.2 → 2.3 on the next `preflight` (no migration).

### Added
- **`commit_mode` rules.md toggle** (`manual` / `confirm` / `auto`, default `confirm`) — controls landing's commit step independently of `git` and `model_invocable`: `manual` never commits, `confirm` asks (the pre-2.3 behavior), `auto` commits unprompted. Applies only when `git: true`. Removes the last manual checkpoint for a headless run.
- **Full-auto defaults for new decks** — scaffolds (`minimal` + `full`) and `preflight` first-time-setup now write `model_invocable: [preflight, landing, walkaround, emit-agents-md, status]` + `status_auto: [start, land]` + `commit_mode: confirm`, so a freshly created deck drives status/landing itself out of the box (commit stays the one confirm-gated step). The gate fallback is unchanged (absent / empty = manual), so existing and hand-made decks are unaffected.

### Changed
- **Land Routine rewritten to collect-then-migrate** — landing now builds the full old→`landed/` remap for the entire land set *before* moving, then rewrites `implements` / `supersedes` / `related` across the active tree **and** the moved set. Fixes dangling edges when co-landing a mutual-reference cluster (the old inbound-only pass missed intra-set edges).
- **Docs** — README / README.zh gain a Configuration section documenting the full `rules.md` surface + an autonomous-operation guide; Roadmap de-staled to 2.x; TEST_PLAN gains 2.1 / 2.2 points; the Claude adapter install/uninstall now lists the `status` skill.

### Migration
- Additive / opt-in — `layout_need_update` unchanged (stays `[2.2]`); no deck migration. `version` silently bumps 2.2 → 2.3 on next `preflight`. To adopt full-auto on an existing deck, add the keys to `flightdeck/rules.md` (or re-scaffold). Reinstall/sync the plugin-cache copy to load the updated skills. See [MIGRATION.md](MIGRATION.md).

## [2.2.0] — 2026-06-03

Metadata-model consolidation + workflow frontmatter enrichment, with the deck-conformance version relocated into a now-mandatory `rules.md`. **Existing decks need a one-time migration** — see [MIGRATION.md](MIGRATION.md) (2.1 → 2.2).

### Added
- **Workflow frontmatter enrichment** — sketches/specs/plans gain recommended `summary` + `last_updated` and optional `supersedes` / `related` edges. `summary` drives the INDEX row (rows now derive purely from frontmatter); `last_updated` is auto-bumped by `status`/`landing`; relation edges are forward-only (reverse is grep-derived). ([spec](flightdeck/archive/specs/2026-06-02-workflow-artifact-frontmatter-enrichment-design.md))
- **Canonical frontmatter field table** in `protocol.md` — single source of truth; `templates.md` / `folder-semantics.md` / `walkaround` defer to it instead of restating field semantics. ([spec](flightdeck/archive/specs/2026-06-02-metadata-model-consolidation-design.md))
- **walkaround Audits 11–12** — aggregated INFO for missing workflow `summary`/`last_updated`, plus dangling `supersedes`/`related` edge detection.

### Changed
- **`rules.md` is now mandatory** and carries the deck-conformance `version:` — part of the minimal 3-file contract (`rules.md` + `cockpit.md` + `landed/HISTORY.md`). `preflight`/`walkaround` compare it against `MIGRATION.md` (`current` + `layout_need_update`) to detect migrations. ([spec](flightdeck/archive/specs/2026-06-02-version-in-rules-migration-detection-design.md))
- **The `` `**Layout**` `` line is removed from `cockpit.md`** — the version now lives in `rules.md`; cockpit is pure focus.
- **INDEX rows derive from `summary`**, and `landing` rewrites inbound `supersedes`/`related` edges to the `landed/` prefix on archive.

## [2.1.0] — 2026-06-02

Soft-config gating + a new high-frequency status ritual. Additive and opt-in — `flightdeck/` Layout stays 1.2; default behavior is unchanged.

### Added
- **`model_invocable` rules.md toggle** — per-project soft gate replacing the global `disable-model-invocation` hard switch on the four entry skills. Default `[]` = all manual (identical to before); opt a ritual into model self-invocation with e.g. `model_invocable: [landing]`. ([spec](flightdeck/archive/specs/2026-06-02-soft-config-model-invocation-design.md))
- **5th ritual `/flightdeck:status`** — high-frequency, model-invocable lifecycle auto-flip of a single artifact's `status:` + its INDEX row (forward-only; never touches cockpit/commit). ([spec](flightdeck/archive/specs/2026-06-02-status-lifecycle-skill-design.md))
- **`status_auto` rules.md toggle** — opt-in list controlling which *optional* status transitions (`start`, `land`) the `status` skill auto-applies; core `create→pending` / `finish→awaiting-review` are always automatic.
- **rules.md key admission policy** — a 4-point gate in `protocol.md` governing when a new toggle may be added (anti-sprawl).

### Changed
- The four entry skills no longer carry `disable-model-invocation`; self-invocation is gated by `model_invocable` (default-off). The gate ships in the shared `SKILL.md` body, so it reaches every platform.
- **Land procedure extracted** into a single shared `## Land Routine` anchor in `exit-ritual.md`; `landing` and `status` are two invocation paths over one implementation.
- `preflight` now surfaces `done`-but-unlanded artifacts in any folder (not just plans).

### Migration
- Additive / opt-in — Layout stays 1.2; existing decks need no changes. To adopt the new automation, add the opt-in keys to `flightdeck/rules.md`. Reinstall/sync the plugin-cache copy so the new ritual loads. See [MIGRATION.md](MIGRATION.md).

## [2.0.0] — 2026-06-02

Entry-layer collapse: one explicit entry skill, no auto-load. (Unrelated to the abandoned work-items "2.0" line — this 2.0 is purely about the entry model; `flightdeck/` layout is unchanged at 1.2.)

### Removed
- **Auto-loaded `workflow` skill** and the **SessionStart hook** — flightdeck is now manual-only. `/flightdeck:workflow` no longer exists.

### Changed
- **`/flightdeck:preflight` is the single entry point** — it initializes `flightdeck/` when absent (no `cockpit.md`), otherwise reconciles + reports (unchanged read behavior). Protocol knowledge moved into `skills/preflight/` (`protocol.md` + relocated companions).
- **Empty-`Next session` fallback unified** (`specs/` + `plans/` + `sketches/`), fixing a prior workflow/preflight divergence.

### Migration
- `flightdeck/` decks need no changes — Layout stays 1.2. Run `/flightdeck:preflight` explicitly at session start. See [MIGRATION.md](MIGRATION.md).

## [1.3.0] — 2026-06-01

### Added
- **Layout version stamp** — cockpit headers carry `**Layout**: <ver>`; `preflight` and `walkaround` compare it against the current layout version instead of always scanning for legacy 1.x filenames. Healthy decks pass silently; unstamped decks fall back to the (now-frozen) legacy-marker check. Never migrates silently.

## [1.2.0] — 2026-06-01

Refinement of 1.1.x: explicit metadata, derived-index reads, folder renames, and a streamlined cockpit. This is deletion + clarity, not a new model — 1.1.x installs migrate with a straight folder rename and adding `status:` frontmatter. See [MIGRATION.md](MIGRATION.md).

### Added
- **Explicit `status:` frontmatter** (required on every artifact) — replaces location-implicit state. Each file now declares its own lifecycle state directly; folder location is no longer the source of truth.
- **Per-folder `INDEX.md`** + root **`flightdeck/INDEX.md`** derived index (file / status / one-line summary). Entry skills read INDEX first to orient without loading every artifact — saves tokens and speeds up preflight.
- **`plans/`** folder with optional **`implements:`** frontmatter pointing to the spec a plan executes.
- **`sketches/`** and **`specs/`** retained and clarified in the folder-choice decision table.
- **`debriefs/`** folder (replaces `safety-reviews/`) for post-incident retrospectives.

### Changed
- **Folder renames** (breaking for existing installs, one-line fix): `incident-reports/` → `incidents/`, `safety-reviews/` → `debriefs/`, `flight-plans/` → `plans/`. Canonical folder set is now `sketches/ specs/ plans/ incidents/ checklists/ charts/ debriefs/` + `landed/`.
- **Cockpit is pure focus** — `## Active focus` / `## Next session` / `## Hanging tasks` only. The artifact-list section is gone; artifact state is now tracked via `status:` frontmatter and INDEX, not a cockpit list.
- **`README` → `INDEX` naming** within conventions and scaffolds. Folder = kind (implicit) + explicit `status:` replaces the old README-as-index idea.
- **Conventions doc** and scaffold templates updated throughout for the new folder names and `status:` field.

### Removed
- `manifest.md` and `logbook.md` — replaced by INDEX reads and `git log`; session scratch lives in project-root `tmp/`.
- `kneeboard/` folder — removed; no replacement needed.

## [1.1.1] — 2026-05-30

Reliability + clarity hardening of the four entry skills, driven by multi-model review of each skill's instructions. No new capabilities — backward-compatible.

### Changed
- **preflight** — now reports the first "Next session" item and **stops** (read-only recon); executing it is the next turn, not folded into the entry ritual. Catalog reads tightened: `Glob` real paths (never guess filenames), frontmatter-only reads in one batch (never full-file / duplicate). Trimmed verbosity and the executor-facing `workflow` cross-link.
- **walkaround** — Audit 8 (AGENTS.md drift) replaces the unexecutable "mentally re-run the recipe" with a concrete field-by-field comparison; Audit 1 adds frontmatter *value* validation (ISO date / list shapes); Audit 3 strips `#fragment`s and verifies files only; the "report once" dedup between Audits 1/9/10 became an explicit skip condition; Audit 6 flags only on high confidence; stray-files no longer false-flag assets/structured-data; absent target folders report ✅ N/A.
- **landing** — the length check is now non-destructive (move overflow to logbook/manifest, confirm before removing) and fires right after step 3, not after commit; step 5's AGENTS.md trigger corrected (`In flight` lives in `manifest.md`, not cockpit); "no new knowledge is a valid outcome"; blocking hanging tasks pause the ritual; opaque `gate (g)` reference made self-contained.
- **emit-agents-md** — step 5 replaces the unexecutable "re-run Steps 1-4 / byte-identical" with a real structural self-check (no second write); dropped the `verbatim` vs link-rewrite contradiction; link rewriting explicitly covers `./` / `../`; "no markers" footer omission made intentional; background stats tagged as non-content.

### Added
- **`checklists/version-bump.md`** — flightdeck now dogfoods its own checklist convention for releases: the five manifests + CHANGELOG that must stay in sync, semver level guidance, and the tag/push step.

## [1.1.0] — 2026-05-30

### Added
- **Bundles** — a first-class concept for multi-file topics: a subfolder with a `README.md` contract (`bundle: true` + `reading_order` + routing frontmatter) plus detail leaves that inherit the README's routing and carry no routing fields of their own. One routing boundary per bundle (no nesting). See `skills/workflow/folder-semantics.md` and design `flightdeck/archive/specs/2026-05-30-bundles-and-routing-graph-design.md`.
- **Routing graph model** — folder-semantics now states flightdeck is graph-routed, not filesystem-routed: a file unreachable from any entry (cockpit / INDEX / manifest / bundle README) effectively does not exist. Custom folders/root files are allowed but must be reachable.
- **Folder-choice decision table** — sketches (idea) vs specs (design to implement) vs checklists (evergreen operational reference) vs charts (imported external material). `checklists/` re-described as authored operational reference; no `references/` folder.
- **Optional `skip_when` frontmatter** — negative routing ("when NOT to read this") for checklists / incident-reports / bundle READMEs.
- **Walkaround** — extended Audit 1 for bundle contracts (README required, leaves must not carry routing fields, `reading_order` match), plus new Audit 9 (orphan / unreachable files + INDEX prompt) and Audit 10 (stray files); 10 audits total.
- **preflight routing catalog** — `/flightdeck:preflight` now reads + parses the frontmatter of `checklists/` / `incident-reports/` flat files and bundle `README.md`s (recursively, excluding `landed/`) and prints a grouped catalog (`[Checklists]` / `[Incident reports]` / `[Bundles]` / `[Malformed bundles]`) with `when_to_read` + `applies_to` + `last_updated`, so routed triggers are in context at entry. Know-what-exists only (not read-all, not a `walkaround` substitute); leaves excluded; unparseable / missing-`when_to_read` / missing-`bundle:true` files surfaced with `⚠` markers rather than dropped. See `flightdeck/archive/specs/2026-05-30-preflight-routing-catalog-design.md`.

### Changed
- **`reading_order` is now a reachability edge** — folder-semantics, `SKILL.md`, and walkaround Audit 9 all treat a bundle README's `reading_order` entries as routing edges to its leaves. A leaf listed in `reading_order` is reachable even without a prose body link, so well-formed bundles no longer false-positive as orphans; a leaf *missing* from `reading_order` is an orphan. Resolves a contradiction between the bundle contract (leaf list in frontmatter) and the orphan audit (links-only reachability).
- **Always-loaded `SKILL.md` now carries the core routing semantics** — the folder-choice decision table, graph-routing/reachability rule, bundle contract, and optional `skip_when` field are summarized in `SKILL.md` (previously only in the on-demand `folder-semantics.md`). Ensures models that don't load the companion still obey the conventions, across all platforms (Claude/Codex/Cursor load `skills/workflow/` directly; `GEMINI.md` @-includes both files).

## [1.0.0] — 2026-05-28

**Project renamed from `workshop` to `flightdeck`.** Aviation framing for operational discipline, continuity, and reliability. Single breaking-change window — post-v1.0 is additive-only.

See [MIGRATION.md](MIGRATION.md) for upgrade steps. Design rationale: [flightdeck/archive/specs/2026-05-28-flightdeck-rebrand-design.md](flightdeck/archive/specs/2026-05-28-flightdeck-rebrand-design.md).

### Renamed

- **Project**: workshop → flightdeck (plugin name, marketplace identifier, repo URL, install commands)
- **Folders**: `plans/` → `flight-plans/`, `playbooks/` → `checklists/`, `scars/` → `incident-reports/`, `reference/` → `charts/`, `critiques/` → `safety-reviews/`, `wip/` → `kneeboard/`. `specs/` and `sketches/` retained (no aviation equivalent improves them).
- **Skill modules**: `workshop-workflow/` → `workflow/`, `session-enter/` → `preflight/`, `session-exit/` → `landing/`, `doctor/` → `walkaround/`. `emit-agents-md/` unchanged.
- **Slash commands**: `/workshop:workshop-workflow` → `/flightdeck:workflow`, `/workshop:session-enter` → `/flightdeck:preflight`, `/workshop:session-exit` → `/flightdeck:landing`, `/workshop:doctor` → `/flightdeck:walkaround`, `/workshop:emit-agents-md` → `/flightdeck:emit-agents-md`. (Main skill module renamed `flightdeck-workflow` → `workflow` to avoid the awkward `/flightdeck:flightdeck-workflow` slash form — clean reads as `/flightdeck:workflow`.)

### Decomposed

- **`board.md` split into three files** separated by read-time:
  - `cockpit.md` — must-read every session entry (Active focus, Next session, Hanging tasks). **80-line hard ceiling.**
  - `manifest.md` — on-demand (In flight artifacts, Blockers). No ceiling.
  - `logbook.md` — rarely read (Recently finished FIFO 5, Deferred). Append-mostly history.

### Restructured

- **`*/finish/` archive subdirs promoted to top-level `landed/` umbrella**. Now `landed/flight-plans/` and `landed/specs/`. Eliminates the "active folder shadowing its own archive" inelegance.

### Surfaced

- **Governing principle** lifted from rebrand spec into `workflow/SKILL.md` and `AGENTS.md`: **"Semantic clarity outranks thematic consistency."** The metaphor is a tool, not a theme. Resist metaphor lock-in on future concepts.

### Repository

- GitHub repo renamed `Yuelioi/workshop` → `Yuelioi/flightdeck`. Auto-redirect in place. Plugin marketplace identifier updated across all 4 platforms.
- VERSION: 0.8.1 → 1.0.0.

### Deferred to v1.1+

These were considered for v1.0 but punted to keep scope contained. Revisit when real usage demands each:

- `briefing/` (domain context / glossary)
- `blackbox/` (raw session-log persistence)
- `crew-handover/` (human ↔ human / cross-AI handoff)
- `experiments/` (long-running probes — already a `future expansion slot`)
- Automated migration skill (manual `MIGRATION.md` was sufficient for user base = 1)

## [0.8.1] — 2026-05-26

Patch release: README clarity + bootstrap UX + content cleanup. No protocol changes.

### Added

- **Bootstrap behavior in `workshop-workflow` skill**: when invoked in a project without `workshop/`, the skill now asks to create one, runs a short Active focus / Next session interview, and writes `workshop/board.md` directly. No more `install.sh --scaffold=minimal` round-trip required for Claude Code users.
- **Slash commands table** in README (EN + ZH) — all 5 commands listed with auto-load behavior and one-line purpose. Replaces the scattered "Force-invoke" + "Explicit slash commands (v0.5.0+)" sections.

### Changed

- **README "Day 1" section** simplified to `/workshop:workshop-workflow` flow. The clone + `install.sh` path remains documented as the fallback for non-Claude tools.
- **`workshop-workflow` skill** decoupled from `superpowers` plugin. Cross-references reframed as "Optional companions" — workshop is self-contained and accepts content from any source. Scenario triggers, exit-ritual heuristics, and folder-semantics no longer prescribe `superpowers:*` skills.
- **Trims**: SKILL.md dropped redundant prose Transitions table (Mermaid covers it), "Why semi-implicit" paragraph, "Backlog specs" edge case, "Proactive scar resurfacing" explanation. Common mistakes merged with Red flags. Net auto-load token cost down ~20%.
- **CHANGELOG** compressed: v0.3–v0.5 entries reduced to 1–2 lines each; "Known limitations" sections folded; per-commit citations dropped.
- **Archived plan** `workshop/plans/finish/2026-05-25-v0.6-cleanup.md` compressed from 789 → 39 lines (step-by-step Edit prescriptions removed; outcome summary retained).

### Fixed

- **README.md** had a duplicate `🇨🇳 中文用户` Chinese-link line inside the `## Install` section (original top-of-file placement + middle convenience link both rendered). Removed the duplicate.
- **`exit-ritual.md`** "Red flags" and "Common rationalizations" tables had significant overlap with `SKILL.md` Common mistakes; the two exit-ritual tables removed (one cross-link added instead).

## [0.8.0] — 2026-05-26

Lifecycle deepening. State-machine depth and protocol-drift surfacing — QoL polish landed before the v1.0 format freeze.

### Added

- **`/workshop:doctor` slash skill** (`skills/doctor/SKILL.md`) — audits a workshop for protocol drift across 8 categories: scars/playbooks frontmatter, stale wip, dangling internal references, orphan scars, board ↔ folder lifecycle mismatch, stale Blockers entries, Recently finished length, AGENTS.md regeneration drift. Severity: CRITICAL / WARNING / INFO. Never auto-fixes — surfaces drift; author decides.
- **OpenSpec-style spec evolution markers** (`ADDED:` / `MODIFIED:` / `REMOVED:`) — optional convention documented in `skills/workshop-workflow/templates.md` for long-lived backlog specs.
- **wip Pre-write checklist** in `skills/workshop-workflow/templates.md` — two-question hard gate before creating any new `wip/` file. Prose discipline, not programmatic enforcement.

### Changed

- **Scar promotion gate** is now multi-criterion: `[Case N] count ≥ 3` AND `≥ 2 distinct sessions` AND remediation pattern stable across cases. Two-stage path: first to `playbooks/`, then to project rules only if the playbook keeps getting ignored.
- **`Recently finished` auto-trim** is enforced, not advisory. `exit-ritual.md` wording tightened to "MUST enforce" / "not author-discretion".
- **session-exit Step 5** ("Check scar→playbook promotion gate (wrap-up)") added after the commit decision.

## [0.7.0] — 2026-05-26

Cross-tool reach. Workshop is portable beyond Claude Code — AGENTS.md emitter bridges to Codex CLI / Copilot / Cursor / Windsurf / Continue / Cody.

### Added

- **`/workshop:emit-agents-md` slash skill** (`skills/emit-agents-md/SKILL.md`) — regenerates `AGENTS.md` at repo root from `workshop/board.md` between fenced markers (`<!-- BEGIN: workshop -->` / `<!-- END: workshop -->`). Hand-authored content outside markers is preserved. Relative links from `board.md` get prefixed with `workshop/`.
- **`AGENTS.md` at repo root** — dogfood output of the emitter. Bridges to the cross-tool standard.
- **Optional Cursor MDC frontmatter fields** (`globs:` + `alwaysApply:`) on scar/playbook templates.
- **Capability × tool compatibility matrix** in `workshop/specs/2026-05-23-v1.0-release-gate.md`.
- **Community PR template** at `.github/PULL_REQUEST_TEMPLATE/manifest-verification.md`.
- **README "Why not just AGENTS.md?" section** (EN + ZH).

### Changed

- **`session-exit/SKILL.md`** gains step 5 (regenerate `AGENTS.md` if `board.md` changed); old Commit step becomes step 6.

### Known limitations

- Behavioral verification on Codex CLI / Cursor / Gemini CLI is out of scope; community PRs invited.
- `.codex-plugin/plugin.json` is functionally inert (Codex CLI has no plugin manifest format); workshop reaches Codex via emitted `AGENTS.md`.

## [0.6.0] — 2026-05-25

Internal consistency cut. No new user-facing features; deduplicates doctrine, hardens enforcement.

### Changed

- **De-duplicated `skills/session-exit/SKILL.md` against `exit-ritual.md`** — lifecycle table + (a)–(h) classification + `Last updated` triggers now live in one place; `session-exit/SKILL.md` is a thin entry-point.
- **Hard-fail on missing scars/playbooks frontmatter.** `when_to_read` + `applies_to` + `last_updated` are REQUIRED; workshop STOPs and reports missing fields instead of silent-skipping.
- **`wip/` TTL hard gate.** Wip files require `last_touched:` frontmatter; `session-enter` surfaces stale wip; `session-exit` BLOCKS until classified, deleted, or explicitly deferred with `defer_reason:`.

### Added

- **Mermaid lifecycle state diagram** in `skills/workshop-workflow/SKILL.md`.

### Migration from v0.5.x

- Add `when_to_read` + `applies_to` + `last_updated` to existing scars / playbooks (or delete the file). Otherwise v0.6+ STOPs and reports them.
- Add `last_touched:` to existing `wip/` files. Otherwise they count as stale and block session-exit.

## [0.5.0] — 2026-05-25

Two explicit slash-command skills exposing the workshop entry / exit rituals as one-command triggers: `/workshop:session-enter` (re-anchor mid-session) and `/workshop:session-exit` (clean wraps). Both `disable-model-invocation: true` — fire only on explicit slash.

## [0.4.0] — 2026-05-25

Dogfood refinements after 1 week of real use: `last_updated` frontmatter on scars/playbooks; proactive scar resurfacing when task overlaps with scar `applies_to` tags; per-review-point critique disposition tags; semi-implicit lifecycle (location = source of truth, frontmatter for divergent states); `Last updated` bump triggers pinned to 4 events.

## [0.3.0] — 2026-05-25

SessionStart hook auto-injects `workshop-workflow` when project has `workshop/`. Six-state lifecycle machine added. Board hygiene: 300-line hard ceiling, `Recently finished` capped at 5 (FIFO), per-entry summary ≤ 3 lines. Scars / playbooks require `when_to_read` + `applies_to` frontmatter.

## [0.2.0] — 2026-05-23

Multi-AI manifests: Claude Code plugin + self-hosted marketplace (tested); Codex CLI / Cursor / Gemini CLI manifests (untested). Chinese README mirror. Skill content made fully tool-neutral.

## [0.1.0] — 2026-05-23

Initial scaffold: `workshop-workflow` skill, adapters, scaffold templates, installers, RED-phase test plan.
