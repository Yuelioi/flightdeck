---
status: done
---

# 布局版本号驱动的迁移检测

**日期**：2026-06-01
**一句话定位**：用 cockpit 里一行 `**Layout**: 1.2` 取代"到处数旧文件名"的存在性检测——健康 deck 静默放行，旧 deck 仍先问后迁，未来迁移只比数字。

## 1. 动机

现在 flightdeck 检测"该不该迁移"靠的是**硬编码一串 1.x 遗留文件名的存在性**（`manifest.md` / `logbook.md` / `kneeboard/` / `flight-plans/` / `incident-reports/` / `safety-reviews/`），而且这串清单**复制在两处**：

- `skills/preflight/SKILL.md` 第 1 步 —— **硬停**：命中就停下整个 ritual，必须先迁移。
- `skills/walkaround/SKILL.md` Audit 10 —— **WARNING**：非阻塞审计项。

两个毛病：

1. **每次改布局都要手工同步多处清单**——将来 1.2→1.3 又重命名某目录，得去每个 skill 里再加一行旧标记。
2. **健康 deck 也要无条件跑一遍 6 项存在性检查**——纯属噪音 / 浪费。

引入一个**布局版本号**（layout version）：写在每个 deck 的 cockpit 里，入口 skill 读它、与当前 schema 比对。

## 2. 核心机制

### 2.1 版本号的家 —— cockpit 散文头加一行

`cockpit.md` 现在用散文头（`**Last updated**` / `**Active focus**`），**没有 YAML frontmatter**。顺着这个风格，在头部加一行：

```
**Layout**: 1.2
```

- 叫 **Layout**（布局版本），不叫 version——避免跟工具 `VERSION`（`1.2.0`，工具语义版本）和工件版本撞名。
- 选 cockpit 的理由：它**必有**、且每个入口 skill **最先读**；散文行零成本、可 grep、不引入新文件、不引入 frontmatter 新格式。
- **不放 `rules.md`**：rules.md 是可选的、可缺失的，缺文件时就读不到版本号。

> "当前 schema = 1.2" 这个常量写在 skill 文本里（skill 随工具版本一起发布、本就每版会改）。未来发 1.3，改动 = MIGRATION.md 加一段映射 + skill 里把"当前"从 1.2 改 1.3，**不再往清单塞旧文件名**。

### 2.2 preflight 第 1 步 —— 三岔

```
读 cockpit 的 Layout：
 ├─ == 1.2（当前）         → 静默继续，不报告               ← 新增的安静路径
 ├─ 存在但 < 1.2（如 1.1） → "检测到 Layout 1.1 — 迁移到 1.2？"
 │                            按 MIGRATION.md，先问后迁，未决不往下走
 └─ 缺失（老 deck 没这字段）→ 回退到现存 6 项存在性检查：
        ├─ 命中 manifest.md 等任一 → 是 1.x，同上「先问后迁」
        └─ 全无                  → 版本号发明前的干净 deck，
                                   offer 补写 **Layout: 1.2**，然后继续
```

**关键不变量**：

- **「缺号」绝不静默跳过**。缺版本号正是真·老 deck 最典型的特征（版本号字段是 1.2 才有的），所以它必须**回退到存在性检查**，而不是放行——否则最该被迁移的那批 deck 会被静默吞掉。
- **`never-migrate-silently` 完整保留**：检测到旧版只是把提示从"手动数文件"换成"版本号驱动"，仍等用户点头；补写 Layout 戳也先 offer。

### 2.3 walkaround Audit 10 —— 版本感知

读 Layout：

- `< 1.2`，或（缺号 **且** 命中旧标记）→ **WARNING legacy**，指向 MIGRATION.md。
- 缺号 **且** 无旧标记 → **INFO**："没有 Layout 戳，建议补 `**Layout**: 1.2`"。
- `== 1.2` → 通过，不报告。

## 3. 冻结清单（去重的取舍）

那 6 项遗留文件名清单**就此冻结**——版本号驱动后它再也不会被扩展（未来迁移只比数字）。因此 preflight / walkaround 各留一份**内联副本**即可：已冻结的副本不会随时间腐化，无需抽到单一来源。

> 备选（未采纳，留作未来"更瘦"选项）：把 6 项抽到 MIGRATION.md 单一来源，两处只写"按 MIGRATION.md 列的旧标记检查"。代价是 AI 每次要多读一次 MIGRATION.md。当前因清单已冻结，内联更直接。

## 4. 范围

只动检测已存在的两处：`skills/preflight/SKILL.md`、`skills/walkaround/SKILL.md`。**自动加载的 `workflow` 不加这道**——它每次会话都跑，加硬停太重；1.x 拦截维持现状（仅 explicit 的 preflight 硬停 + walkaround WARNING）。

## 5. 受影响组件（供 plan）

- `skills/workflow/templates.md` § cockpit.md 模板 —— 加 `**Layout**: <ver>` 行 + 说明。
- `scaffolds/` 的 cockpit 模板 —— 新建 deck 一律带 `**Layout**: 1.2`（确保新 deck 永远命中"分支 2 静默"，不掉进缺号兜底）。
- 本项目自己的 `flightdeck/cockpit.md` —— 补 `**Layout**: 1.2`（dogfood）。
- `skills/preflight/SKILL.md` 第 1 步 —— 重写为 §2.2 三岔。
- `skills/walkaround/SKILL.md` Audit 10 —— 改为 §2.3 版本感知。
- `MIGRATION.md` —— 确认仍是 rename 映射的单一来源（未来按版本号分段）。
- 发布：CHANGELOG 记一条；是否算版本号 bump 由 version-bump 检查单定。

## 6. 待 plan 细化

- `**Layout**` 行在 cockpit 头里的确切位置（紧邻 `Active focus` 之后）。
- preflight 三岔的精确措辞 + 输出格式（命中各分支时报告什么）。
- "当前 schema 版本"常量在 preflight / walkaround 两处如何措辞一致。
- 补写 Layout 戳的 offer 文案（属结构性改动？还是元数据小改可轻量 offer）。
