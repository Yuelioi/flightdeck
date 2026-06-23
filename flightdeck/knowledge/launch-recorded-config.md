# Launch-recorded config & single-path（现状）

> 落地于 v3.0.0-alpha.4（相 1/2/3）。原 spec graduate 至此；历史动机/评审张力见 git 历史与 CHANGELOG。

## 一句话

把「运行时推断 / 处处兜底」换成「launch 一次性记录 / 强制的单条线」。每一处「脚本路 vs 手写兜底」「git vs no-git」「每会话探运行时」都是 AI 每次加载 skill 都要读+推理的死代码——机械/环境双路塌成单条线（逐项/逐任务的真·判断不在此列）。

## 配置形态（hybrid）

记录式配置进 **`rules.md` 的 frontmatter**（与 `version` 同级），复用脚本现成的 `parse_frontmatter`；`### Rules` 自由散文留正文接长尾偏好。

```
---
version: 3.0
runtime: uv        # uv | python | node — skill 调脚本用哪个解释器
agents_md: off     # auto | off — landing 读它，从不探 AGENTS.md 文件
---
```

- **晋升判据（谁进 frontmatter）——单一、可证伪**：当且仅当该 knob 否则需要「每会话探测某个外部事实」→ 升结构化字段。`runtime`✅（否则每会话探 uv/python/node）、`agents_md`✅（否则每次 landing 探 AGENTS.md 是否存在）；`commits`/`start`/soft-landing 降级/nudge ❌（不探任何外部事实，只是一次设定的偏好）→ 全留 `### Rules` 散文。
- **`git` 不进配置**：它是安装前置——launch 缺 git 直接拒、运行期恒成立；git 的"设置"就是 launch 那道门。
- **稳态优先级（永久）**：frontmatter 结构化字段对其管辖的 key 永久高于 `### Rules` 散文（散文写 "always use python" 但 `runtime: node` → 字段胜）。散文只对没有对应字段的偏好有效。
- Settings 记的是**解析出的值**（探测或默认），不号称"用户显式决策"；用户随后可改。

## 三个强制（双路塌成单路）

1. **git 强制** — 删贯穿各 skill 的 no-git 分支（preflight / landing / status / emit-agents-md / exit-ritual / folder-semantics / protocol / scaffold）。被砍用例（gitignore deck、临时目录/导出包、CI 跑 flightdeck 不 commit）为有意取舍；出路 `git init`。
2. **runtime 强制（uv/python/node）** — 删所有「无 runtime → 手写 markdown 兜底」双写。INDEX/cockpit regen、artifact stamp、机械审计只剩脚本一条线；INDEX row 格式真相源 = 脚本代码，`templates.md` 仅留 row 示例供人读。skill 按 frontmatter `runtime` 拼调用形（`uv run` / `python` / `node`）。
3. **runtime 多实现** — 四个用户可见脚本（`flightdeck_index` / `flightdeck_init` / `flightdeck_lint` / `flightdeck_new`）各一份 **Node 移植**（内置模块对等、零 npm 依赖）支持 node-only 用户；`bump_version` 仅保留 Python（maintainer 发版工具，用户 skill 从不调用）。

### Parity 防线（spec 级约束）

双实现必漂——以钉死非确定性的 fixture 做**字节对拍**验证：`scripts/tests/parity/` 金标 fixture + `test_parity*.py`，Python/Node 逐字 diff 必须为空。归一规则堵隐性漂移：排序按 **Unicode 码点**（规避 Node `sort()` 默认 UTF-16 与 Python 码点序在非 BMP 的差异）、换行恒 LF、文本 UTF-8 NFC、固定日期格式、稳定 JSON 键序。

## launch 行为（doctor 体检 + 极简提示）

「运行一次=同意创建」内核不变；2 问 interview 与 AGENTS.md opt-in 仍砍掉。**唯一提示**是 git——这是相对原 spec「零提示」的一处有意回调（缺 repo 时与其硬拒不如直接帮你 init，更省事，且 launch 本就是建 deck 的同意）。

1. **doctor 体检**：探测面只「git 存在性 + runtime 检测」（优先级 `uv` > `python` > `node`），打 `🩺 flightdeck doctor` 体检表，**每项一行正面/负面汇报**。规则仍是「仅允许 git 与 runtime 这类纯环境探测，项目内容一概不碰」。
2. **按结果分支**：
   - 全绿 → 直接建。
   - **有 git 但无 repo** → 问一句 `Run \`git init\` now and continue? [y/N]`；`y` 帮你 init 再建，`N`/其它 → 停（`Skipped — flightdeck requires git ...`），不建 deck。
   - **git 没装** → 停，提示装 git（不能替你 init）。
   - **无 runtime** → 停，提示装 uv/python/node（不能替你装；非交互）。
   - 两者都缺 → 体检表两行都列后停（runtime 没法自动修，git offer 不弹）。
3. 写 `runtime: <detected>` + `agents_md: off`（新 deck definitionally 无 AGENTS.md——平默认、非探测）。
4. 建完汇报 deck-created + **回显记下的设置**（`runtime: <x>` · `agents_md: off`，告知可改），让用户看见到底记了什么。

## 字段化语义（runtime 直读处）

- **`agents_md`（`auto|off`）**：`landing` 读字段——**不再探 AGENTS.md 文件是否存在**。`off`=不自动重生；`auto`=landing 总重生。`/flightdeck:emit-agents-md` 是**一次原子动作**：建/重生文件 **并**把字段翻 `off→auto`（首次 bootstrap 即记录"今后自动维护"的意图）。这是兼容性破坏（语义从"看文件现实"变"看记录意图"）：手删 AGENTS.md 但字段仍 `auto` → 下次 landing 重生——有意的 UX 锐边，改字段（或重跑 emit-agents-md）即对齐，不引"再探文件"旁路。
- **`runtime`（`uv|python|node`）**：所有调脚本的 skill 读它拼调用形，不再每会话探测。**记录的 runtime 失效**（卸载/换机）是可预见操作：任何需脚本的步骤**硬失败并中止该操作**，报 `⚠ recorded runtime '<x>' not found — update rules.md (runtime:) or reinstall`；**preflight 只读**仍照常报板，但附一行 `⚠ recorded runtime broken`。不静默回落每会话重探。

## 不动:逐项/逐任务判断（scope 外的"真没办法"）

needs-verify 分类、知识分类/路由、landing 的 archivable/交叉引用判断、preflight `## Next`-空兜底——记不进字段，本就是原则的 scope 外（原则只针对机械/环境双路，不消真·推理）。

## 版本策略

留在 `3.0.0-alpha` 列车（Wails 式长 alpha）：稳定前破坏性改动一律并入当前 alpha、只递增 `alpha.N`。`MIGRATION.md` `current` 留 `3.0`（format baseline），正式迁移段待宣布稳定时再写。三家外部评审按纯 semver 指删 no-git/no-runtime 为 major——记此张力，但 alpha 阶段 major/minor 边界尚未启用。
