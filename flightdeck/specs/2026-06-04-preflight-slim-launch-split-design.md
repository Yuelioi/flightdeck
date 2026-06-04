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
- `preflight` 的 Branch-0 **不再创建 deck**，改为**重定向**：检测到无 `flightdeck/cockpit.md` → 报一行「此目录无 flightdeck deck —— 运行 `/flightdeck:launch` 创建」然后 STOP。不做任何拷贝、不读 repo。
- `setup.md` 文件删除（内容已迁入 `skills/launch/SKILL.md`）。

> **为何拆**：初始化与接管是互斥路径，硬塞进 Branch-0 让「单一入口」这句话名不副实——deckless 时 preflight 干的根本不是 preflight 的活。拆开后两个命令各自语义自洽：`launch` = 一次性建 deck，`preflight` = 每次开工接管。`launch`（发射/放飞）取航空常用词，与 operational 仪式（preflight/walkaround/landing）的调性区分开，凸显其一次性奠基性质。

### B. `preflight` 瘦成纯接管

**保留的步骤（精简后的 preflight 全流程）：**

1. **Gate** — model-invocation 自调用门（不变）。
2. **Branch-0（重定向）** — 无 `cockpit.md` → 指向 `/flightdeck:launch` + STOP（见 A）。
3. **读 `rules.md`** — autonomy gate 解析 + git 推断（deck root 有无 `.git`）+ `disabled_folders`。便宜，保留。
4. **读 `INDEX.md` + `cockpit.md`** — reconcile 基线：`Last updated` / `Active focus` / `## 进行中` AUTO 区 / `## 下一步`。报 `## 下一步` item #1。
5. **catalog 预热（精简）** — 读 `checklists/INDEX.md` + `incidents/INDEX.md`，列出**文件 + when_to_read 两列**（去掉 applies_to / status 列）。目的是会话开场「知道手头有哪些路由知识可查」，属于**接管**语义，不是检查。`charts/` 仍不进 catalog（同现状）。
6. **git 被动一行提示（降级）** — 跑一条 `git status` / `git branch --show-current`（可与其它信号合并成一条命令），**仅在明显不对时**附一行 `⚠ 分支/cockpit 看着不对，跑 /flightdeck:walkaround`；否则不出声。**不再走 step 5 现有的「Resolve which?」阻塞式互动**。
7. **报告 + STOP** — 报 item #1，「Say go to execute」。Land-readiness（≥5 未 land）提示保留为最后一行（便宜、入口语义）。
8. **下一步为空时的 fallback** — surface active plans / active specs / idea pool（不变）。

**从 preflight 删除（walkaround 已覆盖的纯重复）：**

- **结构性迁移探测**（现 step 2 的 model-v4 结构信号探测 + 版本比对的迁移 offer）→ walkaround Audit 10 已做。preflight 不再探测/offer 迁移。
  - **保留**：`version` 兼容性静默 bump（`< current` 但不在 `layout_need_update` → 静默 bump 到 `current`）——这是 step 3 现有的「唯一允许的静默 stamp」，便宜、非交互，留在读 rules.md 那步。结构性（需交互）的迁移 offer 才删。
- **catalog 状态体检**（现 step 7）→ walkaround Audit 1。
- **cockpit `## 进行中` 漂移检查** → walkaround Audit 13。
- **阻塞式 git reconcile 互动**（现 step 5 的「Resolve which?」分支）→ 降级为 B-6 的被动一行。

### C. 配套改动

- **插件清单注册新命令**：`.claude-plugin/` / `.codex-plugin/` / `.cursor-plugin/` / `gemini-extension.json` 加 `launch` 命令条目（与现有 4 命令同构）。
- **交叉引用改写**：`protocol.md` / `MIGRATION.md` / `README` / `CHANGELOG.md` 中凡引用 preflight「Branch-0 首次创建 / setup.md」之处，改指向 `/flightdeck:launch`。`MIGRATION.md` 不需要新增 deck 迁移段（这是工具内部行为变化，不改 deck 数据结构）。
- **SKILL.md description**：preflight 的 description（去掉「Initializes flightdeck when absent」一句，改为「无 deck 时指向 launch」）；新增 launch 的 description。

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

## 实现顺序（交给 writing-plans 细化）

1. 新建 `skills/launch/SKILL.md`（搬 setup.md 内容 + 终态报告）。
2. preflight Branch-0 改重定向；删 setup.md；删 preflight 的迁移探测/catalog 体检/阻塞 reconcile；catalog 降两列；git 降被动一行。
3. 4 个插件清单注册 launch；改 description。
4. 交叉引用改写（protocol/MIGRATION/README/CHANGELOG）。
5. 测试 + dogfood 验证。
