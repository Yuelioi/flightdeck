---
status: active
when_to_read: 规划或改动 flightdeck 跨项目共享知识 vendoring（母库解析 / synced 标记 / consumers 注册表 / fanout）前
applies_to: [scripts/flightdeck_index.py, skills/sync/SKILL.md, skills/preflight/protocol.md, skills/preflight/templates.md, skills/walkaround/SKILL.md, scaffolds/full/flightdeck/rules.md]
when_to_update: 母库解析路径、synced/consumers 字段语义、register/list/prune 契约、或 fanout 行为发生变化时
last_updated: 2026-06-19
summary: 共享知识 vendoring 的当前真相：母库固定 ~/.flightdeck、synced 标记 + relpath 不变量、consumers 注册表 + fanout 双向可发现。
---

# 共享知识 sync（shared-knowledge-sync，当前真相 v2）

跨项目把母库（master deck）里的 checklist/doc 副本（vendored）刷新到消费 deck。母库是唯一真相源，**谁新谁赢**（比 `last_updated`，**无 hash / 无 source_hash**）。AI 干语义合并，`flightdeck_index.py` 算事实。仅 checklist/doc。v1 设计见 `archive/specs/2026-06-18-shared-knowledge-sync.md`、v2 演进见 `archive/specs/2026-06-19-shared-knowledge-sync-v2.md`。

## 母库解析（固定约定）

母库根**恒为 `~/.flightdeck`**（`_resolve_master_root()`，无入参）。是目录则用；否则 `master-missing`，每文件优雅跳过（vendored 文件自洽，照常可用）。**逃生口**：母库想放别处，把 `~/.flightdeck` 做成符号链接；Windows 无管理员权限用目录联接 `mklink /J %USERPROFILE%\.flightdeck <target>`（`is_dir()` 两者都跟随）。无 env var、无指针文件、无 CLAUDE.md 回退。

## `synced` 标记 + relpath 不变量

vendored 文件 frontmatter 标 **`synced: true`**（布尔标记，不存路径）。**关键不变量：消费端 relpath == 母库 relpath**——`sync_status` 用消费文件自身 relpath 去 `~/.flightdeck/<同 relpath>` 找源。它要求消费 deck 的共享文件目录结构镜像母库。「vendor 到不同位置 / scaffold 重定位 / 手工迁移」破坏此不变量，属**协议禁止**，不提供兼容。

## `consumers` 注册表（母库→消费者反向可发现）

母库每个共享文件 frontmatter 带 `consumers: [...]`，**单行 JSON 数组**（兼容 `parse_frontmatter` 标量行解析），存消费 deck 绝对路径，**母库专属**——vendor 拷到消费端时剔除（消费副本 = 母库 frontmatter − `consumers` + `synced: true`）。消费端**不该**出现 `consumers` 键（walkaround 直读 frontmatter 判非法 WARNING）。路径以 `Path(p).resolve().as_posix()` 规范化作去重主键。

脚本三个母库 primitive flag（位置参 = 母库根）：
- `--register-consumer <deck> <relpath>`：把 deck 加进母库文件 `<relpath>` 的 `consumers`（幂等、排序写回）。`<relpath>` 须是母库已存在**文件**，否则报错且**不阻断主 sync**。sync skill 在 B 模式 vendor / promote 成功后调用。
- `--list-consumers`：全母库 `consumers` 并集去重 + 排序，**纯读**——本机暂不可达目录跳过但**不写回**（防网络盘/外接盘/symlink 暂离线被误删）。
- `--prune-consumers`：**唯一**剔除动作。保守判定：仅当父目录 `is_dir()` 为真、且 deck 既 `exists()` 又 `os.path.lexists()` 皆假才删（`lexists` 守卫 symlink 目标临时不可达）。
- 三者读母库 frontmatter 遇权限/锁/解析错（含 `UnicodeDecodeError`，它是 `ValueError` 非 `OSError`）→ 警告跳过该文件，不中断。

## `--fanout`（母库改动推全下游）

`/flightdeck:sync --fanout` 是 **sync skill 编排，非脚本 flag**：① `--list-consumers` 拿可达下游 deck（空 → no-op）；② **串行**对每个 deck 跑正常 pull（各自 `--sync-status` 算 upstream-changed、正文替换、逐字保 `## 项目覆盖`、frontmatter 不动），deck 路径作显式入参、不切 cwd；③ **失败隔离 best-effort**，单 deck 失败记一条继续其余；④ 汇总 banner 逐 deck 状态行。`_resolve_master_root` 恒指 home、与 fanout 不耦合（fanout 三 flag 把母库根作普通入参）。

## 状态语义（消歧）

按作用域互斥、先判根：① 母库根 `~/.flightdeck` 不存在/非目录 → 整 deck **`master-missing`**（deck 级，一次性跳过）；② 母库根在但 `~/.flightdeck/<relpath>` 不是可读文件（中间目录缺失 / relpath 指向目录 / 类型错配 / 源被删）→ 该文件 **`dangling`**（文件级）。`dangling` 修复 = sync 既有交互（删本地副本 / 保留 / 转本地原创即去 `synced`）。`upstream-changed` / `in-sync` / `locally-ahead` 按 `last_updated` 比。`--sync-status` 输出 `state<TAB>relpath`。

## 已接受的限制（非目标）

- **跨 OS 共享母库**：`consumers` 存绝对机器路径，母库设计为每机一份（`~/.flightdeck` 或本机符号链接），不支持同一母库经共享存储跨 OS 路径匹配。
- **并发原子写**：register/prune 是读-改-写，本工具单用户串行，不做锁/冲突合并。
- **注册表内嵌 frontmatter**：非集中索引；fanout/list/prune 遍历全母库读 frontmatter（文件量小可接受）。规模逼人改集中索引 = 另起 spec。
- **fanout 为 deck 粒度广播**：per-file `consumers` 信息仅用于「谁消费此文件」查询，不用于收窄 fanout。

## 落地状态（本仓 dogfood）

母库已物理移到 `C:\Users\yl\.flightdeck`；本仓 `checklists/comments.md`、`commits.md` 已迁到 `synced: true` 并对母库补注册（`--list-consumers` 命中本仓）；两文件当前 `in-sync`。
