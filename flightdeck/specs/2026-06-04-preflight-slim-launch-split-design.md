---
status: active
summary: preflight 太重（兼管初始化/检查/接管）——拆出 `/flightdeck:launch` 接管首次创建 deck，preflight 瘦成纯接管（读 cockpit/INDEX → 报下一步 + 精简 catalog 预热 + 被动一行 git 提示），删掉与 walkaround 重复的检查（结构性迁移探测/catalog 状态体检/cockpit 漂移/阻塞式 reconcile）。并入 3.0
last_updated: 2026-06-04
related: [specs/2026-06-03-model-v4-folder-state-cockpit-design.md, specs/2026-06-03-scriptable-mechanical-layer-design.md]
---

# preflight 瘦身 + 拆出 `/flightdeck:launch`（并入 3.0）

## Problem

`/flightdeck:preflight` 是 flightdeck 的单一入口，但它在一个 skill 里同时背了三件性质不同的活：

1. **初始化** — Branch-0：无 `cockpit.md` → 加载 `setup.md` → 探测 runtime、拷贝 scaffold、创建 deck。
2. **检查** — step 2 结构性迁移探测、step 4–5 git 对账、step 6 catalog 装载、step 7 catalog 状态体检。
3. **正常接管** — 读 `INDEX.md`/`cockpit.md` → 报 `## 下一步` item #1（+ 空时 fallback）。

「初始化」与「正常接管」是互斥的两条路径，却挤在同一个 Branch-0 分叉里；「检查」这部分则与 `walkaround` 的审计**大面积重复**：

| preflight 步骤 | walkaround 对应审计 | 关系 |
|---|---|---|
| step 2 结构性迁移探测 | Audit 10 版本/迁移探测 | 完全重复 |
| step 7 catalog 状态体检 | Audit 1 status validity（且 walkaround 是全局的） | 完全重复 |
| step 5 cockpit「进行中」漂移 | Audit 13 进行中 AUTO 一致性 | 完全重复 |

结果是 preflight 这个「每次开工都跑」的入口被审计逻辑撑得很重，而审计本该是 `walkaround` 这个「按需深查」命令的职责。**第一性判断：每次开工的入口应当只回答「我在哪、接下来干什么」，深度完整性审计交给专门的 `walkaround`；首次建 deck 是一次性奠基事件，不该和每次接管挤在一个入口。**

## 目标终态

- **`/flightdeck:launch`**（新命令）独占「首次创建 deck」。
- **`preflight`** 瘦成纯接管：读 cockpit/INDEX → 报下一步，外加两项**便宜且确属入口语义**的保留物（catalog 预热、被动 git 提示）。
- 与 `walkaround` 重复的检查从 preflight **删除**（不是搬移——walkaround 已经在做）。
- 全部并入 **3.0**（尚未发布，继续在 `flightdeck-3.0-rules-simplification` 分支）。

## 设计

### A. 新命令 `/flightdeck:launch`（首次创建 deck）

- 现 `skills/preflight/setup.md` 的内容（探测 Python runtime → `flightdeck_init.py` 或手工拷贝 scaffold → STOP）整体搬成新 skill `skills/launch/SKILL.md`。**行为逐字不变**：零提问、确定性拷贝、git 项目静默删 `landed/HISTORY.md`、scaffold `version` 对齐 `MIGRATION.md` `current`、deck 已存在则拒绝。
- 终态报告（现 setup.md 的「Final report」三行）原样搬入。
- `preflight` 的 Branch-0 **不再创建 deck**，改为**重定向**：检测到无 `flightdeck/cockpit.md` → 报一行「此目录无 flightdeck deck —— 运行 `/flightdeck:launch` 创建」然后 STOP。
- **谓词对齐（防死胡同）**：launch 的拒绝条件与 preflight 的重定向条件**必须同用 `cockpit.md` 是否存在**这一个谓词。`flightdeck_init.py:33` 现已是 `(deck/"cockpit.md").exists()` → 二者天然互补：cockpit.md 在 → launch 拒绝、preflight 接管；cockpit.md 缺 → preflight 重定向、launch 继续建。半初始化（`flightdeck/` 目录在但无 cockpit.md）**不是死胡同**——preflight 重定向 → launch 因 cockpit 缺失而继续补建。（plan 期校验：`flightdeck_init.py` 在已存在部分文件的目录上的拷贝健壮性。）
- **deckless 即停（护栏）**：无 cockpit.md 时 preflight **只做重定向 + STOP**，不读 `rules.md`、不读 repo、不跑 git、不探测 migration。Branch-0 先于 Gate 与读 rules.md 执行，杜绝职责再膨胀。
- `setup.md` 文件删除（内容已迁入 `skills/launch/SKILL.md`）。

> **为何拆**：初始化与接管是互斥路径，硬塞进 Branch-0 让「单一入口」这句话名不副实——deckless 时 preflight 干的根本不是 preflight 的活。拆开后两个命令各自语义自洽：`launch` = 一次性建 deck，`preflight` = 每次开工接管。`launch`（发射/放飞）取航空常用词，与 operational 仪式（preflight/walkaround/landing）的调性区分开，凸显其一次性奠基性质。

### B. `preflight` 瘦成纯接管

**保留的步骤（精简后的 preflight 全流程）：**

1. **Gate** — model-invocation 自调用门（不变）。
2. **Branch-0（重定向）** — 无 `cockpit.md` → 指向 `/flightdeck:launch` + STOP（见 A）。
3. **读 `rules.md`** — autonomy gate 解析 + git 推断（deck root 有无 `.git`）+ `disabled_folders`。便宜，保留。
4. **读 `INDEX.md` + `cockpit.md`** — reconcile 基线：`Last updated` / `Active focus` / `## 进行中` AUTO 区 / `## 下一步`。报 `## 下一步` item #1。
5. **catalog 预热（精简）** — 读 `checklists/INDEX.md` + `incidents/INDEX.md`，列出**文件 + when_to_read 两列**（去掉 applies_to / status 列）。目的是会话开场「知道手头有哪些路由知识可查」，属于**接管**语义，不是检查。`charts/` 仍不进 catalog（同现状）。表尾加一行脚注 `(状态/合法性审计见 /flightdeck:walkaround)`，把「这些是否仍有效」的认知锚明确指向 walkaround，避免用户把 obsolete/superseded 项误当可用。
   - 为何只留 when_to_read：它是 trigger prose（「在 X 之前读」），对 AI 消费者直接够用；`applies_to` 标签与 `status` 仍在 INDEX 文件里，触发匹配时按需读，不必每次开场全列。
6. **git 被动一行提示（降级）** — 跑一条命令汇总信号（`git status --short` + `git branch --show-current`），**按下表判定**，仅在命中时附**被动一行**、绝不走阻塞式「Resolve which?」互动：

   | 信号 | 判定 | 提示文案 |
   |---|---|---|
   | A. 当前 branch 与 cockpit `Active focus` 提取的 branch token 明显不符 | 触发 | `⚠ git 状态异常（分支与 Active focus 不符），继续前先核对` |
   | B. detached HEAD | 触发 | `⚠ git 状态异常（detached HEAD），继续前先核对` |
   | uncommitted changes / ahead-behind / 多个 stash | **不触发** | （留给用户日常感知，preflight 不出声） |

   **git 异常的文案是「继续前先核对」，不导向 walkaround**——walkaround 是只读文件审计，不读 live git 状态，导过去无意义（评审采纳点）。导向 walkaround 的只有「版本结构落后」一类（见下「版本 bump 优先级」）。
7. **报告 + STOP** — 报 item #1，「Say go to execute」。Land-readiness（≥5 未 land）提示保留为最后一行（便宜、入口语义）。
8. **下一步为空时的 fallback** — 数据源是 folder INDEX 的行（这些行携带 `status`），不是文件时间排序、不是另跑体检。按序：`plans/INDEX.md` 的 `active` 行 → `specs/INDEX.md` 的 `active` 行 → `specs/INDEX.md` `待启动（idea）` 组，呈现候选请用户选，绝不自动开始（同现状，仅明确数据源）。

**从 preflight 删除（walkaround 已覆盖的纯重复）：**

- **结构性迁移探测**（现 step 2 的 model-v4 结构信号探测 + 版本比对的迁移 offer）→ walkaround Audit 10 已做。preflight 不再探测/offer 迁移。

**版本 bump 优先级（两套信号不冲突，评审采纳点）：** preflight 读 `version` 后按 `MIGRATION.md` frontmatter（`current` + `layout_need_update`）分两支，二者互斥——

  - **兼容落后**（`version < current` **且**不在 `layout_need_update`）→ **静默 bump 到 `current`，不出任何提示**。这是协议唯一允许的静默 stamp，留在读 rules.md 那步。
  - **结构落后**（`version <` 某个 `layout_need_update` 条目）→ **不 bump**，附被动一行 `ℹ deck 版本结构落后，跑 /flightdeck:walkaround 看迁移`。结构迁移的执行仍归 walkaround Audit 10。
  - preflight 与 walkaround **读同一份 `MIGRATION.md` 列表**，故判定一致，不会出现 preflight 误 bump 一个其实需迁移的 deck。
  - 取舍：bump 成功不另发 informational 提示（保持静默），避免每次开场噪声。
- **catalog 状态体检**（现 step 7）→ walkaround Audit 1。
- **cockpit `## 进行中` 漂移检查** → walkaround Audit 13。
- **阻塞式 git reconcile 互动**（现 step 5 的「Resolve which?」分支）→ 降级为 B-6 的被动一行。

### C. 配套改动

- **插件清单注册新命令**：`.claude-plugin/` / `.codex-plugin/` / `.cursor-plugin/` / `gemini-extension.json` 加 `launch` 命令条目（与现有 4 命令同构）。
- **交叉引用改写**：`protocol.md` / `MIGRATION.md` / `README` / `CHANGELOG.md` 中凡引用 preflight「Branch-0 首次创建 / setup.md」之处，改指向 `/flightdeck:launch`。`MIGRATION.md` 不需要新增 deck 迁移段（不改 deck 数据结构）。
- **CHANGELOG 用户行为变更条目**：preflight 行为变了（deckless 不再自动建 deck、不再阻塞式 reconcile），CHANGELOG 须把「原 Branch-0 自动初始化 → 现需显式 `/flightdeck:launch`」作为一条**显式用户行为变更**写出，附一行过渡说明（首次在空目录跑 preflight 会看到重定向提示，不再静默建 deck）。否则用户首遇 deckless 重定向会困惑。
- **SKILL.md description（定稿，影响 AI 路由）**：
  - preflight：`Use when explicitly invoking the flightdeck entry ritual — reads INDEX/cockpit and reports the next step, warms the routing catalog, and gives a passive note on obvious git/version misalignment. No deck (no cockpit.md) → points to /flightdeck:launch and stops. Triggered by /flightdeck:preflight.`
  - launch：`Use when explicitly creating a flightdeck deck for the first time in a project that has none — copies the full-layout scaffold and seeds cockpit.md (zero prompts), then stops. Refuses if cockpit.md already exists. Triggered by /flightdeck:launch.`

### D. 不做（YAGNI / 边界）

- **不**把 git 对账「搬」进 walkaround——walkaround 是只读文件审计，不碰 live git 状态，接不住；git 入口信号降级留在 preflight 即可。
- **不**改 `walkaround` 的任何 Audit——它已经覆盖删掉的那些检查，无需新增。
- **不**改 deck 数据结构 / scaffold 内容（launch 的拷贝行为与现 setup.md 完全一致）。
- **不**引入新的 deck 迁移（无结构变化）。

## 影响 / 风险

- **routing 预热不丢**：用户最初的顾虑（preflight 不读就不了解项目知识）——catalog 读取保留，只是列得更紧凑；合法性审计移走不影响「知道有什么」。
- **git 历史不受影响**：删的是 live-state 对账的阻塞互动，不是读 git 历史；项目历史照旧按需 `git log` / `landed/` 查。
- **迁移探测前移到 walkaround**：未迁移 deck 在 preflight 不再被自动 offer 迁移。缓解：preflight 的被动一行提示在 `version` 明显落后时附「跑 walkaround」，且 walkaround Audit 10 仍是权威探测点。可接受（迁移是低频结构事件）。
- **dogfood**：本仓库 deck 已是 3.0/model-v4，改完后跑 `/flightdeck:preflight`（重定向不触发，因有 cockpit）与一次 deckless 验证 `/flightdeck:launch`。

## 验证

- 现有测试套件（`test_flightdeck_init` 等）：launch 复用 `flightdeck_init.py`，初始化测试应仍绿；新增/改名命令的注册测试。
- 手工 dogfood：① 在本仓库跑精简后的 preflight，确认只读+报下一步+catalog 两列+无阻塞互动；② 在一个临时空目录跑 `/flightdeck:launch` 建 deck；③ 在该空目录（无 cockpit）跑 `/flightdeck:preflight` 确认重定向到 launch。
- `/flightdeck:walkaround` 对本仓库 deck 仍干净（确认删检查没在 preflight 留悬空引用）。
- **隐式消费者核查**：catalog 去掉 `applies_to`/`status` 两列前，确认无其它 skill/脚本依赖 preflight *输出* 的这两列（它们仍在 INDEX 文件中，按需读不受影响）——预期无消费者，但 plan 期 grep 确认。

## 实现顺序（交给 writing-plans 细化）

1. 新建 `skills/launch/SKILL.md`（搬 setup.md 内容 + 终态报告）。
2. preflight Branch-0 改重定向；删 setup.md；删 preflight 的迁移探测/catalog 体检/阻塞 reconcile；catalog 降两列；git 降被动一行。
3. 4 个插件清单注册 launch；改 description。
4. 交叉引用改写（protocol/MIGRATION/README/CHANGELOG）。
5. 测试 + dogfood 验证。

## 评审纪要

2026-06-04 三份外部 AI review（`tmp/{claude,ds,gpt}.txt`，作者不了解项目现状，仅供参考）。逐条裁决：

**采纳：**
- git 被动提示给最小触发表，且 git 状态异常文案不导向 walkaround（walkaround 不读 live git）→ 改「继续前先核对」（ds#2/gpt#2/gpt）。
- version 静默 bump 与 walkaround 提示的优先级讲清：兼容落后→静默 bump 不提示；结构落后→不 bump、提示 walkaround；二者读同一份 MIGRATION 列表（claude#2/gpt/ds#7）。
- deckless 即停、什么都不读，作为显式护栏；Branch-0 先于 Gate/读 rules（gpt）。
- catalog 表尾加脚注指向 walkaround 做状态审计（ds#5）。
- 定稿 preflight/launch 两条 description（claude#4/ds#4）。
- fallback 明确数据源为 folder INDEX 行 + 顺序（ds#3）。
- CHANGELOG 写一条显式用户行为变更 + 过渡说明（ds#6）。
- plan 期核查无隐式消费者依赖被删的 catalog 列（gpt 中风险）。

**拒绝 / 误判：**
- ds#1「launch 拒绝 vs preflight 重定向不一致→死胡同」=**误判**：`flightdeck_init.py:33` 拒绝条件已是 `cockpit.md` 存在，与重定向同谓词，天然互补。已转为 A 节「谓词对齐」显式声明。
- catalog 保 3 列（留 applies_to）：**维持 2 列**——when_to_read 是 trigger prose，对 AI 消费者够用；applies_to/status 仍在 INDEX 文件按需读。
- gpt「bump 成功发 informational 提示」：**不采**——静默 bump 保持静默，避免开场噪声。
