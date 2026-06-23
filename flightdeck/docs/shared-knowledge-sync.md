---
status: active
when_to_read: 规划或改动 flightdeck 跨项目共享知识 vendoring（母库解析 / synced 标记 / 边界锚 / 指纹判过期 / consumers 注册表 / fanout）前
applies_to: [scripts/flightdeck_index.py, scripts/flightdeck_index.js, skills/sync/SKILL.md, skills/preflight/protocol.md, skills/preflight/templates.md, skills/walkaround/SKILL.md, scaffolds/full/flightdeck/rules.md]
when_to_update: 母库解析路径、synced 语义、边界锚约定、指纹判过期算法、register/list/prune 契约、或 fanout 行为发生变化时
last_updated: 2026-06-23
summary: 共享知识 vendoring 的当前真相：分区单写者（母库唯一写 shared 段）、`<!-- flightdeck:project-specific -->` 边界锚切分（**可 vendor 的母库文件自带锚 + stub**，用户永不手写锚）、shared 段内容指纹判过期（现算现比、无存储 hash）、纯脚本机械 pull（AI 零参与）、安全网 `marker-missing`（synced + 无锚 + 漂移 → 不 pull、报 WARN）、删 back-flow（仅 promote 上提新文件、并 re-stamp 锚）、consumers 注册表 + fanout。
---

# 共享知识 sync（shared-knowledge-sync，当前真相）

跨项目把母库（master deck）里的 checklist/doc 副本（vendored）刷新到消费 deck。模型 = **分区单写者 + 机械懒拉**：母库是 shared 段唯一写者，判过期 = **shared 段内容指纹**（不比时间戳），pull 是脚本端纯文本 splice —— **AI 零参与、零 token**。`flightdeck_index.py --sync-status` 算事实，`--sync-pull` 应用 splice。仅 checklist/doc。

演进史：v1（`archive/specs/2026-06-18-shared-knowledge-sync.md`）、v2（`archive/specs/2026-06-19-shared-knowledge-sync-v2.md`）均用 `last_updated`「谁新谁赢」+ AI 语义合并 + back-flow，**已废**；现行机械模型见 `archive/specs/2026-06-20-sync-mechanical-pull.md`。

## 分区单写者（section-single-writer）

每个 vendored 文件分两区，各只有一个写者：

| 区 | 写者 | 同步方向 |
|---|---|---|
| **shared 段**（边界锚以上的整个 body：标题 + 导语 + 通用各节） | **母库唯一** | 母库 → consumer（pull，机械覆盖） |
| **项目段**（边界锚以下，本地化标题如 `## 项目覆盖`） | **consumer 唯一** | 永不离开 consumer（永不上推） |

consumer **永不改 shared 段** → shared 内容不可能并发分叉 → 合并问题从根上消失。改共享规则 = **去母库改**（直接编辑 `~/.flightdeck/<relpath>`）再 fanout。

## 边界锚（机械可切，语言无关）

shared / 项目段的分界用固定锚注释：

```
<!-- flightdeck:project-specific -->
```

- 锚**以上** = shared（母库管，pull 覆盖）；锚**以下** = 项目私有（pull 永不碰）。
- 用固定锚而非匹配本地化标题：标题文字仍可本地化给人看，脚本切分靠 `indexOf(锚)`，**语言无关、一刀准**。
- **可 vendor 的母库 shared 文件自带锚 + stub**（翻转旧约定「母库文件通常无锚」）：母库文件以
  canonical 结尾收尾，锚随整文件拷到 consumer，**用户永不需手写锚**。canonical 形 = 锚 + 可见
  `## Project overrides` + 一行斜体注；stub 在锚**以下**故不进 shared 指纹（只作首次 vendor 的种子，
  之后永不比对），consumer 可本地化其标题/正文。纯内部、不打算 vendor 的母库文件仍可无锚。
- 文件**没有锚** = 整个 body 当 shared。对纯 shared 文件合法；但对 `synced` 文件，若它**同时已漂移**，
  pull 会覆盖整个 body → 报 `marker-missing`（见状态语义），不再当普通 `stale`。
- 导语也算 shared，**不许本地化**（会被覆盖）；项目私货只能放锚以下，或放 frontmatter 路由。

## 判过期：现算现比内容指纹（无状态）

**判过期 = 比 shared 段内容，不比时间戳。**

```
shared_fp(text) = sha1_12( normalize( strip_frontmatter(text) 锚以上部分 ) )
in-sync  ⟺  shared_fp(consumer) == shared_fp(master)     否则 stale
```

- **fingerprint** = 复用 `flightdeck_lib` 的 `sha1(utf8(x))[:12]`（与 incident 签名同一函数，py/js byte-parity 已测）。
- **normalize**：换行 → LF、UTF-8 NFC、行尾空白 + 段末多余空行剥除（否则平凡差异假报过期）。
- **无存储状态**：不存 `source_hash`、不比 `last_updated`。母库本地、文件几 KB，进项目时脚本现读现算现比。
- 因母库是 shared 段唯一权威，**任何指纹差异 = consumer stale**（无方向判定，无 `locally-ahead`）。
- 比对全在脚本层 → **AI 不读内容、零 token**。

## 母库解析（固定约定）

母库根**恒为 `~/.flightdeck`**（`_resolve_master_root()`，无入参）。是目录则用；否则 `master-missing`，每文件优雅跳过（vendored 文件自洽，照常可用）。**逃生口**：母库想放别处，把 `~/.flightdeck` 做成符号链接；Windows 无管理员权限用目录联接 `mklink /J %USERPROFILE%\.flightdeck <target>`（`is_dir()` 两者都跟随）。无 env var、无指针文件、无 CLAUDE.md 回退。

## `synced` 标记 + relpath 不变量

vendored 文件 frontmatter 标 **`synced: true`**（布尔标记，不存路径）。**关键不变量：消费端 relpath == 母库 relpath**——`sync_status` 用消费文件自身 relpath 去 `~/.flightdeck/<同 relpath>` 找源。它要求消费 deck 的共享文件目录结构镜像母库。「vendor 到不同位置 / scaffold 重定位 / 手工迁移」破坏此不变量，属**协议禁止**，不提供兼容。frontmatter（`when_to_read` / `applies_to`）是 consumer 可本地化的路由，pull 永不碰。

## `consumers` 注册表（母库→消费者反向可发现）

母库每个共享文件 frontmatter 带 `consumers: [...]`，**单行 JSON 数组**（兼容 `parse_frontmatter` 标量行解析），存消费 deck 绝对路径，**母库专属**——vendor 拷到消费端时剔除（消费副本 = 母库 frontmatter − `consumers` + `synced: true`）。消费端**不该**出现 `consumers` 键（walkaround 直读 frontmatter 判非法 WARNING）。路径以 `Path(p).resolve().as_posix()` 规范化作去重主键。

脚本三个母库 primitive flag（位置参 = 母库根）：
- `--register-consumer <deck> <relpath>`：把 deck 加进母库文件 `<relpath>` 的 `consumers`（幂等、排序写回）。`<relpath>` 须是母库已存在**文件**，否则报错且**不阻断主 sync**。sync skill 在 B 模式 vendor / promote 成功后调用。
- `--list-consumers`：全母库 `consumers` 并集去重 + 排序，**纯读**——本机暂不可达目录跳过但**不写回**（防网络盘/外接盘/symlink 暂离线被误删）。
- `--prune-consumers`：**唯一**剔除动作。保守判定：仅当父目录 `is_dir()` 为真、且 deck 既 `exists()` 又 `os.path.lexists()` 皆假才删（`lexists` 守卫 symlink 目标临时不可达）。
- 三者读母库 frontmatter 遇权限/锁/解析错（含 `UnicodeDecodeError`，它是 `ValueError` 非 `OSError`）→ 警告跳过该文件，不中断。

## 模式（sync skill 编排）

- **A. pull / re-sync**（`/flightdeck:sync`）：`--sync-pull` 对每个 `stale` 文件机械 splice（切锚、母库 body 换上半截、项目段 + frontmatter 逐字留），`in-sync` 跳过、`marker-missing` **跳过**（无锚 + 漂移，整 body pull 会吞本地补充 → 报 WARN 让用户先补锚）、`dangling` 报告问。git deck 直接应用（git 可逆）；非 git deck 先 `--sync-pull --check`（`would-pull<TAB>relpath`，零写）再应用。
- **B. 首次 vendoring**（`/flightdeck:sync <master-relpath>`）：拷母库整文件到同 relpath、stamp `synced: true`、剔 `consumers` 键、按需本地化路由、`--register-consumer`。
- **C. promote**（`/flightdeck:sync promote <relpath>`）：把**本地新写、够通用**的文件（无 `synced`）的 shared body 上提到母库同 relpath（母库已有该 relpath → 停下问，是冲突非 promote），**并给母库副本补 canonical 锚+stub**（让 promote 出的文件遵守 vendorable-master 约定、把锚继续传下去），随后 stamp `synced: true` + `--register-consumer`。这是**唯一的 consumer→母库 路径，也是 sync 里唯一的 AI 步**（判通用性，显式、低频）。
- **D. fanout**（`/flightdeck:sync --fanout`）：**sync skill 编排、非脚本 flag**——`--list-consumers` 拿可达下游 deck（空 → no-op），**串行**逐个跑 `--sync-pull`（deck 路径作显式入参、不切 cwd），**失败隔离 best-effort**（单 deck 失败记一条继续其余），汇总 banner 逐 deck 状态行。

**无 back-flow**：shared 段母库权威，consumer 绝不把 shared 改动推上去；本地改 shared 段会在下次 pull 被机械覆盖 —— 要留的内容放边界锚以下。

## 状态语义（消歧）

按作用域互斥、先判根：① 母库根 `~/.flightdeck` 不存在/非目录 → 整 deck **`master-missing`**（deck 级，一次性跳过）；② 母库根在但 `~/.flightdeck/<relpath>` 不是可读文件（中间目录缺失 / relpath 指向目录 / 类型错配 / 源被删）→ 该文件 **`dangling`**（文件级；修复 = 删本地副本 / 保留 / 转本地原创即去 `synced`）；③ 指纹相等 → **`in-sync`**；④ 指纹不等且**有锚** → **`stale`**（锚护住项目段，机械 pull 安全）；⑤ 指纹不等且**无锚** → **`marker-missing`**（整 body 被当 shared，pull 会覆盖、吞掉无锚的本地补充——安全网：`--sync-pull` 沿 `state != "stale"` 过滤**自动跳过**它，walkaround/sync 报 WARN，提示先补锚再拉）。无方向、无 `locally-ahead`，母库永远权威。`--sync-status` 输出 `state<TAB>relpath`。

## 与 zero-write 的调和

入口刷新（preflight 读路由目录前先机械拉一次）**不破 zero-write，而是精确化它**：zero-write 真义 = preflight 不做**判断性看板写入**（不 bump `Updated` / 不 regen INDEX / 不翻 status / 不建 artifact）。一次确定性、可报告、可回滚的 vendored 输入刷新是「读前先 `git pull`」，由 preflight **之前**的独立机械层干，与已存在的 turn-end INDEX hook 同范畴。git deck 自动 + 报告；非 git deck 先 diff 再问（同 conform 的非-git 纪律）。一条 deck `### Rules` 可把它降级为「只检测、入口永不自动写」。

## 已接受的限制（非目标）

- **跨 OS 共享母库**：`consumers` 存绝对机器路径，母库设计为每机一份（`~/.flightdeck` 或本机符号链接），不支持同一母库经共享存储跨 OS 路径匹配。
- **并发原子写**：register/prune 是读-改-写，本工具单用户串行，不做锁/冲突合并。
- **注册表内嵌 frontmatter**：非集中索引；fanout/list/prune 遍历全母库读 frontmatter（文件量小可接受）。规模逼人改集中索引 = 另起 spec。
- **fanout 为 deck 粒度广播**：per-file `consumers` 信息仅用于「谁消费此文件」查询，不用于收窄 fanout。

## 落地状态（本仓 dogfood）

母库已物理在 `C:\Users\yl\.flightdeck`；本仓 `checklists/comments.md`、`commits.md` 已 `synced: true` 并对母库补注册（`--list-consumers` 命中本仓），当前 `in-sync`（shared 段指纹相等）。
