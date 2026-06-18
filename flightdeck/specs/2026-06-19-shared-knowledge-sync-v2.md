---
status: active
graduate: true
summary: 母库解析塌成固定约定 ~/.flightdeck（symlink/junction 逃生口）；synced_from 去别名改 synced 标记；母库加 consumers 注册表（拷贝时剔除）+ 脚本自动维护 + /flightdeck:sync --fanout 真扇出到全下游。
last_updated: 2026-06-19
---

# shared-knowledge-sync v2: 母库解析简化 + 双向可发现

v1（已 land，`archive/specs/2026-06-18-shared-knowledge-sync.md`）的母库解析过度配置、字段冗余、且只有消费端单向可见。v2 把三处一并修掉。

## 动机

- env var + 指针文件 + CLAUDE.md 回退的三层解析，对一个**要发给别人用的工具**是过度设计——家目录固定约定（如 `~/.gitconfig`、`~/.ssh`）零配置、不用每机设 env、不用往每 repo 塞 gitignored 指针。
- `synced_from` 存母库相对路径作「别名」，但消费端相对路径**从来恒等于**母库相对路径（B 模式本就是同路径拷贝），别名能力无人使用。
- 改了母库，**无从知道哪几个项目消费了该文件**——缺母库→消费者的反向可发现，扇出靠人肉记忆。

## Part 1 — 母库解析固定为 `~/.flightdeck`

**契约**：母库根恒为 `Path.home() / ".flightdeck"`。是目录则用；否则 `master-missing`，每文件优雅跳过并报告（vendored 文件自洽，照常可用）。**逃生口 = 符号链接**：母库想放别处（如 `E:\projects\agent\flightdeck`），把 `~/.flightdeck` 做成指向它的符号链接，`is_dir()` 自动跟随。**Windows 无管理员权限**时用**目录联接**（`mklink /J %USERPROFILE%\.flightdeck <target>`，junction 不需管理员 / Developer Mode），`is_dir()` 同样跟随；企业策略禁 symlink 时这是首选。

删除：`_resolve_master_root` 的 `deck` 入参、`rules.md` 的 `shared_master` frontmatter、env 展开（`os.path.expandvars`）、gitignored `<deck>/.shared-master` 指针、CLAUDE.md 资产库回退。三层塌成一条。

落地（仓库外，plan 单列、动前再确认）：母库内容物理移到 `C:\Users\yl\.flightdeck`；四账户同步的全局 CLAUDE.md「跨项目资产库」措辞同步（四份须逐字一致）。

## Part 2 — `synced_from` → `synced`（去别名）

消费端相对路径恒等于母库相对路径，故不存路径，字段塌成布尔标记 **`synced: true`**。`sync_status` 用消费文件**自身 relpath** 去母库找源（`master_root / <consumer relpath>`）。全仓 `synced_from` 引用改 `synced`。

**关键不变量（v2 显式声明）**：`消费端 relpath == 母库 relpath`。整个 `synced` 模型依赖它——它要求消费 deck 的共享文件目录结构镜像母库（母库 `checklists/commits.md` ↔ 消费 deck `checklists/commits.md`）。v1 的 B 模式同路径拷贝已隐含此约束，v2 把它提为协议不变量，并由 **walkaround sync Audit 校验**：发现某 `synced: true` 文件在母库无同 relpath 源 → 报 `dangling`（而非静默 master-missing）。「vendor 到不同位置 / scaffold 重定位 / 手工迁移」会破坏该不变量，属**协议禁止**，不提供兼容。

## Part 3 — 母库 `consumers` 注册表 + `--fanout`

**字段**：母库每个共享文件 frontmatter 加 `consumers: [<消费 deck 绝对路径>, ...]`，**母库专属元数据**。

**vendor 时的 frontmatter 变换（精确定义，消歧）**：vendor（B 模式 / promote）拷贝母库文件到消费端时，拷正文 + frontmatter，但**滤掉 `consumers` 键**，并写入 `synced: true`。即消费副本 frontmatter = 母库 frontmatter − `consumers` + `synced: true`。`synced: true` 的写入只发生在 **vendor 路径**。

**pull 刷新（`upstream-changed`）不碰 frontmatter**：只用母库正文替换消费端共享正文，逐字保留消费端整个 frontmatter（其本就无 `consumers`、已有 `synced: true`）+ `## 项目覆盖` 段。故 `consumers` 既不外泄、也不需在 pull 路径重写 `synced`。若消费端被人为加了 `consumers` 键 → walkaround 报为非法字段（消费端不该有）。

**脚本维护（`flightdeck_index.py` 新 flag，全部对「母库」操作）**：
- `--register-consumer <deck> <relpath>`：把规范化的 `<deck>` 绝对路径加进母库文件 `<relpath>` 的 `consumers`（去重幂等、排序写回）。**契约**：`<relpath>` 必须解析到母库内**已存在的文件**（非目录、非缺失），否则报错且**不阻断主 sync**（注册失败只警告，vendor 本身已成功）。sync skill 在 B 模式 vendor / push promote 成功后调用一次。
- `--list-consumers`：读全母库共享文件的 `consumers`，**并集去重（规范化主键）+ 排序**成 deck 集合，**纯读**——本机当前不可达的目录在本次结果里**跳过但不写回母库**（避免网络盘暂离线 / 外接盘未挂载 / symlink 暂不可达被误判永久删除）。
- `--prune-consumers`：**唯一**会从母库 `consumers` 删条目的动作，显式调用。保守判定：仅当目录的**父目录 `is_dir()` 为真**、且该 deck 路径既 `exists()` 为假**又** `os.path.lexists()` 为假时才剔除——`lexists` 这层专防「symlink 入口还在、只是目标临时不可达」被误删（区别于「整个盘不可达」「目录真没了」）。
- 三者读/写某母库文件 frontmatter 遇**权限 / 锁 / 解析错** → 警告并**跳过该文件**，不中断整体（与 fanout 的失败隔离一致）。

**扇出**：母库端 `/flightdeck:sync --fanout`：
1. 跑 `--list-consumers` 拿下游 deck 集合（空 → no-op，报「注册表为空」；首次部署属正常）。
2. **串行**遍历，对每个下游 deck 在本会话内执行正常 pull 合并流——`--sync-status` 算该 deck 的 `upstream-changed`，AI 做正文替换、逐字保 `## 项目覆盖`、frontmatter 不动。每个 deck 路径作**显式入参**传给脚本与 pull 流，**不切换 cwd**（脚本本就吃 deck 路径参数，无需改工作目录）。
3. **失败隔离 best-effort**：单个 deck 失败（权限 / 锁 / 损坏 / 目录缺席）记一条、**继续**其余；不中断扇出。
4. 汇总 banner：逐 deck 一行 `<deck>: pulled N / in-sync / skipped / error <因>`，末尾总计；有 error 时整体非零状态。

「真扇出」= 一次会话动多个项目目录里的 deck，影响面大但符合本工具 AI 全自动驱动定位（半扇出仅列清单的方案已否决）。`_resolve_master_root` 与 fanout **不耦合**：解析恒指 `~/.flightdeck`（无 deck 参）；fanout 三个 flag 把母库根作普通入参枚举 `consumers`，逐消费 deck 的 pull 再各自把消费 deck 路径作入参——没有任何一处让解析逻辑重新依赖 deck 上下文。

**首次部署 / v1 迁移（两条路径非冗余、是「以后」与「这一次」）**：
- **自然填充（以后）**：v2 起，任何 deck 经 B 模式 / promote 落地共享文件时，sync skill **当场自动** `--register-consumer`——这是长期机制，post-v2 无漏注册缺口。
- **一次性迁移（这一次）**：v1 在 `consumers` 字段存在前就已 vendor 的文件登记不到。**唯一**这样的存量 = 本仓的 `checklists/comments.md`、`checklists/commits.md`。迁移由 **AI 在 plan 执行时跑**两行 `--register-consumer <本仓 flightdeck deck 绝对路径> checklists/comments.md|commits.md`（绝对路径 = 本仓 `flightdeck/` deck 路径，AI 已知）。这是**plan 的显式一步 + 验收项**，不是可选。
- **漏注册缺口有界**：缺口仅存在于「pre-v2 已 vendor 的文件」这一有限集合（即上面两份）；迁移做完即闭合，此后自然填充保证不再产生新缺口。故不另做「发现未注册消费者」机制（母库本就无从发现未登记者，YAGNI）。

**注销 / 剪枝路径（v2 显式）**：
- 消费 deck 整个删除 / 移走 → `--prune-consumers` 在父目录可达时剔除。
- 消费 deck 仍在、但删了某 vendored 副本 → 该 deck 仍在 `consumers`，下次 fanout 对它 pull 时发现无对应 `synced` 文件、no-op（轻微残留，不阻塞）；不主动追删（YAGNI）。
- 母库文件 rename / move → 视为**手动操作 = 删旧 + 新 vendor**：旧 relpath 的消费副本变 `dangling`（消费端处理），旧 `consumers` 条目随旧文件删除一并消失。v2 不提供 rename 自动迁移。

## 状态语义与变更检测（消歧）

**`master-missing` vs `dangling` 按作用域互斥，先判根：**
1. 母库根 `~/.flightdeck` 不存在 / 非目录 → 整 deck 走 **`master-missing`**（deck 级，所有 `synced` 文件一次性优雅跳过、报一次）。
2. 母库根在，但本文件的 `master_root / <relpath>` **不是可读文件**（中间目录缺失 / relpath 指向目录 / 文件变目录等类型错配 / 源被删）→ 该文件 **`dangling`**（文件级）。即「根级缺失=master-missing，文件级缺失=dangling」，二者不重叠。

**变更检测不变（无 hash）**：沿用 v1「谁新谁赢，比 `last_updated`」，**无 source_hash**。去掉 `synced_from` 不影响检测——源仅靠 relpath 定位、新旧仍比 `last_updated`；vendor 不写也不需任何 hash 字段。

**`dangling` 修复路径**（沿用 v1 sync 既有交互）：报告后问用户——删本地副本 / 保留 / 转本地原创（去掉 `synced` 标记，从此不再随母库）。

**master 不是自己的消费者**：`consumers` 只登记**异于 `~/.flightdeck` 的**消费 deck；位于母库根自身的 deck 即母库，绝不登记为自身消费者（防同路径自我覆盖）。

**`consumers` 绝对路径规范化**：写入 / 去重 / 比对前一律 `Path(p).resolve()`（吸收 `C:\`↔`c:\`、尾斜杠、`.`/`..`、symlink 归一）；规范化后的字符串即去重主键。

## 改动面

| 面 | 文件 | 改动 |
|---|---|---|
| 脚本 | `scripts/flightdeck_index.py` | `_resolve_master_root` 重写（固定约定、去 `deck` 参）；**全部调用点同步去入参**（含 `sync_status` 及任何 pull 路径调用），用自身 relpath 找源；新增三个母库 primitive flag `--register-consumer` / `--list-consumers`（纯读）/ `--prune-consumers`（唯一剔除，含 `lexists` 守卫）——`--fanout` 本身是 **skill 编排**（跑 `--list-consumers` 再循环 pull），非脚本 flag；消费路径 `resolve().as_posix()` 规范化去重；`consumers` 以**单行 JSON 数组**存 frontmatter（兼容现 `parse_frontmatter` 标量行解析）；vendor 写入路径滤 `consumers` 键 + 写 `synced: true`；`synced_from`→`synced` |
| sync skill | `skills/sync/SKILL.md` | 母库解析节改一句；B 模式 stamp `synced: true` 且滤 `consumers`；vendor/promote 后调 `--register-consumer`；新 §扇出（串行/失败隔离/banner 状态行）；banner master-missing 文案去 env 字样 |
| 配置面 | `flightdeck/rules.md`、`scaffolds/full/flightdeck/rules.md` | 删 `shared_master` frontmatter |
| 配置面 | `.gitignore` | 删 `.shared-master` 条目 |
| 协议/文档 | `skills/preflight/protocol.md`、`skills/preflight/templates.md`、`skills/walkaround/SKILL.md` | `shared_master`/`.shared-master`/`synced_from`/env 解析处改措辞；walkaround sync Audit：校验 `relpath` 不变量（`synced` 文件母库无同 relpath 源 → `dangling`）+ 消费端非法 `consumers` 键 |
| 测试 | `scripts/tests/test_flightdeck_index.py` | `_resolve_master_root` 改 mock `Path.home()`；删 env/指针用例；新增 register/list-consumers(纯读不写回)/prune(保守)/vendor 滤 consumers/synced 用例 |
| 迁移 | （命令，无文件）| plan 显式一步：对本仓 `flightdeck/` deck 跑 `--register-consumer` ×2（`comments.md`/`commits.md`），闭合 v1 存量缺口 |
| 文档尾 | `CHANGELOG.md`、`flightdeck/cockpit.md` Key Context | 折进 3.0 alpha 现有条目；**旧 `shared_master`/env/`synced_from`/`.shared-master` 描述一律删除、不留 deprecated**（alpha 未发 + 项目「果断删减」）|
| 仓库外 ⚠ | `C:\Users\yl\.flightdeck`、四账户全局 CLAUDE.md | 移母库 + 措辞同步（plan 单列，动前确认）；四份**逐字一致**按全局 CLAUDE.md §多账户同步既有流程（推平 + 核对 hash）核验 |

**不动**：`archive/` 下历史 spec/plan。

## 边界与已接受的限制（非目标）

- **跨 OS 共享母库**：`consumers` 存绝对机器路径；母库设计为**每机一份**（`~/.flightdeck` 或本机符号链接），不支持把同一母库经共享存储跨 Windows/Linux 访问后做路径匹配。非目标。
- **并发 sync 会话的 frontmatter 原子读改写**：`--register-consumer` / `--prune-consumers` 是读-改-写。本工具**单用户串行**使用，不做文件锁 / 冲突合并；同时手工编辑母库 + 跑注册的丢写风险由「别并发」规避。
- **`relpath` 不变量**：见 Part 2——破坏镜像结构属协议禁止，不提供兼容路径。
- **注册表内嵌 frontmatter（非集中索引）**：`consumers` 存在每个共享文件 frontmatter 里，fanout/list/prune 须遍历全母库读 frontmatter。共享文件量级很小（个位数），可接受；若将来规模逼人要改集中索引，那是**另起一份 spec** 的协议变更，本 v2 不预留。
- **fanout 为 deck 粒度广播**：`consumers` 虽是「文件→消费者」，但 fanout 并集成 deck 集合后对每个 deck 整体 pull（deck A 只消费 `comments.md`，母库改 `commits.md` 也会进 A 跑一次 `--sync-status`）。下游 deck 数小，多余扫描成本可忽略；per-file 精度只用于「谁消费此文件」的信息查询，不用于收窄 fanout。
- **`synced: true` 的可观察性**：不再像 v1 `synced_from` 携带来源串。但来源**唯一可推导**——母库固定 `~/.flightdeck`、relpath 恒等于消费端自身路径，故源恒为 `~/.flightdeck/<同 relpath>`；v1 的 `synced_from` 因恒等本就不含额外信息。判定可接受，不为「人眼可读来源」保留冗余字段。

## 验收

- `uv run pytest scripts/tests/` 全绿。
- 端到端 pull/fanout：母库（或 `~/.flightdeck` 符号链接）改一份共享文件 → `/flightdeck:sync --fanout` 命中已注册消费 deck 并刷新；B 模式 vendor 后该母库文件 `consumers` 多出该 deck，**消费副本无 `consumers` 键、无路径别名（只 `synced: true`）**；母库缺席时优雅 `master-missing`。
- dangling / 删除：删母库某共享文件后，消费端 `--sync-status` 报 `dangling`（按 v1 处理）；`--prune-consumers` 在父目录可达时剔除已不存在的消费 deck，盘不可达时**不误删**。
- 注册表健壮性：`--list-consumers` 对暂不可达目录只跳过不写回；空注册表 `--fanout` = no-op 且明确报「注册表为空」；单下游失败时其余 deck 仍完成、banner 区分 pulled/in-sync/skipped/error。
- 幂等：连续 `--register-consumer` 同 deck N 次（含 `C:\`↔`c:\`/尾斜杠变体）→ `consumers` 不重复增长（规范化主键去重）。
- 迁移闭合：plan 执行后，母库 `comments.md`/`commits.md` 的 `consumers` 均含本仓 deck；`--fanout` 能命中本仓。
- 仓库外：四份全局 CLAUDE.md 经 §多账户同步流程核对 hash 一致。
