---
status: active
graduate: true
summary: Shift flightdeck from inference/fallback to recorded settings + required runtime/git: structured settings in rules.md frontmatter (runtime, agents_md) read directly at runtime, free-prose ### Rules kept for the long tail (commits, start, nudge…); force git + a runtime (uv/python/node), delete no-git branches and hand-written fallbacks across the skills; launch records resolved values zero-prompt and prints a non-blocking pick-list. Ships in the 3.0.0-alpha train (no minor/major bump until stable).
last_updated: 2026-06-19
---

# Launch-recorded config & single-path

## 1. 原则与动机

一句话:**把「运行时推断 / 处处兜底」换成「launch 一次性记录 / 强制的单条线」。**

判据(贯穿全 spec,且**只**针对**机械 / 环境双路**):每一处「脚本路 vs 手写兜底」「git vs no-git」「每会话探测运行时」都是 AI **每次加载 skill 都要读 + 推理**的死代码。原则——**机械双路塌成单条线;逐项 / 逐任务的真·判断不在此列**(知识分类、needs-verify、archivable、`## Next`-空兜底——见 §3.4,它们记不进配置,本就是 scope 外的「没办法」)。

Token 论证(收紧、不超词):flightdeck 的 SKILL.md 被调用时整份注入上下文;运行时脚本则跑在**子进程、其文件读取从不进上下文**。所以「script fast-path + 手写 markdown 兜底」的双写里,**手写兜底那段散文每次加载都被读入,无论用没用到**——删它(靠强制 runtime)去掉的是这部分常驻成本;no-git 分支同理。本 spec **不声称**具体削减量(无基准计数)、也不号称"唯一解"(精简表述同样省 token)——收益方向明确即可。

产品定位的诚实交代:强制 git + runtime 把首次体验从「launch 必成功」变成「环境不齐先修再来」。这是**有意的取舍**(见 §4 拒绝路径),不掩饰。

## 2. 配置形态(hybrid)

记录式配置进 **`rules.md` 的 frontmatter**(与 `version` 同级),`### Rules` 自由散文留在正文。**把配置放 frontmatter 是有意选择**:`rules.md` 既有 frontmatter,**直接复用脚本现成的 `parse_frontmatter`**(真·复用,零新解析逻辑),且天然避免「正文 H2 块与 `### Rules` 散文误读」的风险(这是上一稿被反复挑的点)。

```
---
version: 3.0
runtime: uv        # uv | python | node — which interpreter the skills invoke
agents_md: off     # auto | off — landing reads this, never probes for an AGENTS.md file
---

### Rules          # free prose, the long tail — arbitrary unanticipated prefs
- ask before committing (you, 2026-06-19)
- commit msg always cites the ticket id (you, 2026-06-19)
```

- **晋升判据(谁进 frontmatter)——单一、可证伪**:**当且仅当**该 knob 否则需要「**每会话探测某个外部事实**」→ 升结构化字段(runtime 直读、不再探)。
  - `runtime` ✅ 否则每会话探 `uv/python/node`。
  - `agents_md` ✅ 否则每次 landing 探 `AGENTS.md` 文件是否存在。
  - `commits` / `start` / soft-landing 降级 / nudge-on-done ❌ **不探测任何外部事实**——只是一次设定的偏好 → 全留 `### Rules` 散文。(commits 据此判据**不比 start/nudge 更该升字段**,三家评审一致;故归 Rules。)
- **`git` 不进配置**:它是**安装前置**——launch 缺 git 直接拒、运行期恒成立,记成字段是永不变的静态标签 =「配置不是配置」。git 的"设置"就是 launch 那道门。
- **`### Rules` = 散文逃生口**:接字段化不了的任意偏好(commits、ping 频道、特定目录先问…),AI 读一遍照做;保留它是为了不退回 3.0 砍掉的 magic-string toggle catalog。
- **稳态优先级(永久,不只迁移期)**:frontmatter 结构化字段对**其管辖的 key** 永久高于 `### Rules` 散文——若散文与某字段冲突(如散文写 "always use python" 但 `runtime: node`),**字段胜**;协议 Rule resolution order 据此补一句。散文只对**没有对应字段**的偏好有效。
- Settings 记的是**解析出的值(探测或默认),不号称"用户显式决策"**——`runtime` 来自探测、`agents_md` 来自默认,用户随后可改。
- `version` 不再是 `rules.md` frontmatter 唯一的结构化字段 → 改 `skills/preflight/templates.md` 对应那条断言。

## 3. 三个强制(把双路塌成单路)

### 3.1 git 强制

flightdeck **要求 git**。删除贯穿各 skill 的 no-git 分支:

- `skills/preflight/SKILL.md` step 1/4(git 推断、no-git 跳过)
- `skills/landing/SKILL.md` step 0(no-git → `mv` 退路)、step 11(no-git 跳 commit)
- `skills/preflight/exit-ritual.md`(`no-git overrides all`、anchor 兜底、signal 2 的 no-git 禁用)
- `skills/status/SKILL.md`、`skills/emit-agents-md/SKILL.md` 的 no-git 旁支
- `skills/preflight/folder-semantics.md`(「A no-git deck loses nothing…」整段)
- `skills/preflight/protocol.md`(Rule resolution order 里的 git 推断条目)
- `scaffolds/full/flightdeck/rules.md`(注释里的 "this deck doesn't use git" 示例)

**被砍到的用例(真实代价、不是稻草人)**:故意把 deck gitignore 的用户;deck 放临时目录 / 导出包 / 共享文件夹;**CI 里跑 flightdeck 做自动化文档生成、不需 commit** 的场景。alpha 期接受此代价、不再为它保留 no-git 分支或 `--no-git` 标志(那正是要消的双路);若稳定后确有需求再单独评估。出路:`git init` 或留在前一 alpha。

### 3.2 runtime 强制(uv / python / node)

flightdeck 要求**至少一个受支持运行时**:`uv`、`python`、或 `node`。删除所有「无 runtime → 手写 markdown 兜底」双写:

- `skills/preflight/exit-ritual.md` § INDEX regeneration / § Script fast path(整段手写重建散文)
- `skills/status/SKILL.md` step 5 / 5a 的 fast-path + always-valid fallback
- `skills/landing/SKILL.md` step 3 的 hand fallback
- `skills/new/SKILL.md` 的 Fast path / no-runtime fallback 二分
- `skills/launch/SKILL.md` 的 Fast path / Fallback 二分
- `skills/walkaround/SKILL.md` 机械审计的「optional fast path」措辞 → 直接是脚本

INDEX / cockpit 重建、artifact stamp、机械审计**只剩脚本一条线**。INDEX row 格式真相源 = 脚本代码;`templates.md` 仍保留 row **示例**供人读,但不再作为「手动重建步骤」。

### 3.3 runtime 多实现(支持面代价)

为支持 node-only 用户,**用户可见的运行时脚本各加一份 Node 移植**,与 Python 版行为等价:

| 脚本 | Python | Node | 说明 |
|---|---|---|---|
| `flightdeck_index` | `.py` | `.js`(新增) | 热路径:INDEX/cockpit regen、`--check`/`--archivable`/`--sync-status`/`--verify-pending`、consumer 注册表 |
| `flightdeck_init` | `.py` | `.js`(新增) | launch 落 scaffold + stamp |
| `flightdeck_lint` | `.py` | `.js`(新增) | walkaround 机械审计 |
| `flightdeck_new` | `.py` | `.js`(新增) | artifact 壳 |
| `bump_version` | `.py` | —(保留 Python) | maintainer/dogfood 发版工具,**用户 skill 从不调用**——node-only 用户永不需要它 |

**脚本依赖前提(已核实)**:四个生产脚本**仅用标准库**(`argparse/hashlib/json/os/re/subprocess/collections/pathlib`,无第三方)。故 Node 版以**内置模块对等**实现(`crypto/JSON/fs/path/RegExp/child_process/Map`)、**零 npm 依赖**;唯一无直接 stdlib 对应的目录遍历(Python `pathlib.glob`)用 **`fs.globSync`(Node ≥ 下限,§8 定)或手写递归**。

**Parity 防线(必须,否则双实现必漂——与本仓 i18n 漂移同类痛)**:目标是**行为等价**,以**钉死非确定性的 fixture 做字节对拍**验证——
- fixture **固定一切非确定输入**:`--date`/`--user` 走入参(脚本已支持)、不读 wall-clock、不含随机 stamp;version/时间戳类字段在对拍里 mock 或排除。
- 两版**钉死归一规则**堵隐性漂移(评审点名的高风险面):排序按 **Unicode 码点**(显式规避 Node `sort()` 默认 UTF-16 与 Python 码点序在非 BMP 上的差异)、换行恒 `LF`、文本 UTF-8 **NFC**、**日期/时间格式固定(同一 `YYYY-MM-DD`、无时区漂移)**、JSON 键序稳定且无多余空白。
- `scripts/tests/` 加 golden-output 对拍(覆盖 index regen、`--check`、`--archivable`、`--sync-status` 等所有子命令),**逐字 diff 必须为空**;CI / 发版门挂上。**此 parity 契约是 spec 级约束**(不是 plan 才定的验收)。

skill 按 frontmatter 的 `runtime` 字段决定调用形:`uv run …` / `python …` / `node …`。

### 3.4 不动:逐项 / 逐任务判断(「真没办法」的例外)

这些**留作判断**,不塌成配置——记不进字段,且本就是 §1 原则的 scope 外(原则只针对**机械 / 环境双路**,不消真·推理):

- **needs-verify 分类**(`exit-ritual` § Self-asserting done):某任务是否「机械执行且误判不易察觉」——逐任务。
- **知识分类 / 路由**:新知识进哪个 folder、incident↔checklist 提升、spec graduate——逐件。
- **landing 的 archivable / 交叉引用判断**。
- **preflight `## Next` 为空的兜底搜索**:板子真可能空。

## 4. launch 行为(仍零提示)

launch 维持「运行一次 = 同意创建、零提问」的 3.0 内核,只多两件确定性动作:

1. **探测面收窄为「仅 git 存在性 + runtime 检测」**(优先级 `uv` > `python` > `node`——Python 是参考实现、Node 是移植,故默认优先参考实现;记录的是探测结果,**用户可在 frontmatter 改**,如 node 项目改 `runtime: node`)。改写现 `skills/launch/SKILL.md`「You MUST NOT inspect the repo」铁律为「**仅允许 git 与 runtime 这类纯环境探测,项目内容一概不碰**」(用"仅允许这些"而非"恰好两次"——日后若加 deno 探测不必改规范)。
2. **任一缺失 → 拒绝并提示**(与 deck-already-exists 同类硬拒;git 的"设置"即此门):
   - 无 git → `⚠ flightdeck requires git — run \`git init\`, then re-run launch.`
   - 无 runtime → `⚠ flightdeck needs a script runtime — install uv (recommended), python, or node, then re-run launch.`
3. **零提示写入 frontmatter**:`runtime: <detected>`、`agents_md: off`(新 deck definitionally 无 `AGENTS.md`——这是**平默认、非探测**)。直接落,**不问**。
4. **建完打印非阻塞 pick-list**:**纯打印、零回应、不阻塞**——这不是提问(不挡执行、不等输入)。文案对副作用**透明**:

```
🛠️ Deck created at flightdeck/ (full layout, v<V>).  git ✓ · runtime uv ✓
Recorded settings — defaults are safe; change by editing rules.md frontmatter
or just telling me (I append a rule / edit the field):
  • runtime   uv      (detected; say "use node" to switch)
  • agents_md off      (landing won't touch AGENTS.md; /flightdeck:emit-agents-md
                        creates it AND flips this to auto — a permanent change)
  • commits   auto      (default; say "ask before committing" → I add a ### Rules entry)
→ Run /flightdeck:preflight to start.
```

> 注:pick-list 里「say "use node"」「say "ask before committing"」是**告知后续可用的自然语言途径**(下一回合你说了,AI 才据此改字段 / 加散文规则)——launch **本回合**不等这句话、不阻塞,故「零提示」内核未破。

## 5. 字段化语义(runtime 直读处)

- **`agents_md`(`auto|off`)**:`landing` 读字段——**不再探 `AGENTS.md` 文件是否存在**。`off` = 不自动重生;`auto` = landing 总重生。`/flightdeck:emit-agents-md` 是**一次原子动作**:创建/重生文件 **并**把字段翻 `auto`(首次 bootstrap 即记录"今后自动维护"的意图,无先后依赖)。
  - **这是兼容性破坏、不只是实现重构**:语义从"看文件现实"变成"看记录意图"。**有意的、可接受的 UX 锐边**:用户手删 `AGENTS.md` 但字段仍 `auto` → 下次 landing 重生(忽略了"删文件"这个直觉停止信号)。**对齐手段**:字段在 pick-list / frontmatter 里可见,改 `agents_md`(或重跑 emit-agents-md)即对齐——**不**引入"再探文件"的旁路(那正是要消的推断)。代价记在此,稳定前不为它回退到文件探测。
- **`runtime`(`uv|python|node`)**:所有调脚本的 skill 读它拼调用形,不再每会话探测。
  - **记录的 runtime 失效**(用户卸载 / 换机)——这是可预见操作、非意外崩溃,故定清行为:**任何需要脚本的步骤**(landing/status/new/walkaround 的 regen、launch 的 init)**硬失败并中止该操作**,报 `⚠ recorded runtime '<x>' not found — update rules.md (runtime:) or reinstall`;**preflight 只读**仍照常报板,但附一行 `⚠ recorded runtime broken`。**不**静默回落到每会话重探(那会复活被删的推断)。这是"硬失败替代旧软回落"的取舍——换单条线、用户摩擦集中在一次性修复。

## 6. 版本

**留在 `3.0.0-alpha` 列车——下一增量 `3.0.0-alpha.4`,不升 minor/major。** 本仓采 Wails 式长 alpha(参 `Wails v3.0.0-alpha2.104`):用户宣布稳定前,破坏性改动一律并入当前 alpha、只递增 `alpha.N`(`rules.md`:未发布前所有新工作并入当前版本)。走 `checklists/version-bump.md`(5 manifest + CHANGELOG),版本号 `3.0.0-alpha.4`;`MIGRATION.md` `current` 不动(仍 `3.0` = format baseline,正式迁移段留待稳定版——`descope-baseline` 的「migration 起于 3.0 之后首个结构化 release」指**稳定之后**,现触发未到)。

> Rationale(非规范):三家外部评审按纯语义化版本指此为 major(4.0,因删 no-git/no-runtime 支持)。记此张力——alpha 阶段 semver 的 major/minor 边界尚未启用,故不适用;首个稳定版号待宣布稳定时定。

**alpha 期无迁移机制**:现仅本 dogfood 一个 deck(git-backed、有 runtime)。实现时**手改本仓 `rules.md`**——加 `runtime`/`agents_md` frontmatter 字段、把现有 commit/git 相关散文按 §2 稳态优先级就地理顺。**不是自动迁移脚本、不自动删用户散文**(评审正确指出:自动识别+删散文风险高于价值);单 deck 手做即可。

## 7. 影响面 + 分相提示

面铺得广(近乎每个 skill + 脚本层 + scaffold + 模板),但主张单一、改动多为**机械删减**。plan 阶段建议分相:

1. **相一 · 配置模型 + git 强制** — frontmatter 字段 schema + 解析接入、`templates.md`/`protocol.md` 断言(含稳态优先级)、删 no-git 分支、scaffold rules.md。
2. **相二 · runtime 强制 + 多实现** — 删手写兜底散文、Node 移植 4 脚本、parity 对拍 + 归一契约(spec 级)、launch 探测收窄 + 拒绝路径。
3. **相三 · 字段化语义** — `agents_md`/`runtime` 字段读取接入 landing/status/emit-agents-md;runtime 失效硬失败路径。
4. **相四 · 发版** — 手理本仓 rules.md、`version-bump.md` 走 `3.0.0-alpha.4`。

> spec 级约束(必须满足才算实现对)= §3.3 的 parity 契约 + §2 的晋升判据/稳态优先级 + §5 的失效行为。各相**怎么算完成**的逐项验收清单由 plan 给出。

## 8. 待定 / 留给 plan

- Node 移植的运行时下限(`fs.globSync` 需 Node ≥ 22;低于则手写递归——plan 定取舍)。
- frontmatter 新字段的校验(非法值如 `runtime: foo` 怎么报)与 `parse_frontmatter` 接入点 —— plan 定。
- pick-list 文案最终措辞(发布面英文)—— 实现时定。
