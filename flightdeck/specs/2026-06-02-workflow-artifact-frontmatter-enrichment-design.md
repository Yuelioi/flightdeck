---
status: pending
---

# workflow 工件 frontmatter 富化：summary + last_updated + 关系边

**日期**：2026-06-02
**来源**：dogfood 中作者提出 —— (1) spec/plan 归档后摘要丢失，想看历史只剩文件名；(2) 缺更新时间，长命 spec 判断不出新旧；(3) 一个大 spec 常对多个 plan / 取代旧 spec，关系散落在正文，归档时不好快速查齐。
**状态**：pending（设计定稿，待开 plan 实现）
**关联**：[2026-06-02-version-in-rules-migration-detection-design.md](2026-06-02-version-in-rules-migration-detection-design.md)（动机不同，但改的是同一批文件 —— `templates.md` frontmatter、INDEX 生成、walkaround；实现时同一 pass 落地，省得两遍动 `templates.md`）

---

## 1. 问题

workflow 类工件(`sketches/`/`specs/`/`plans/`)的 frontmatter 现在只有 `status`(+ plan 的可选 `implements`)。三个缺口：

1. **摘要落地即丢。** 一行摘要现在只活在 `INDEX.md` 的 AUTO 行里，而 Land Routine 第 2 步 landing 时会把该行从 INDEX 删除 → 归档进 `landed/` 的工件没有摘要，只剩文件名 + HISTORY 一句话。看历史时无从快速辨认。
2. **无更新时间。** 知识类工件(incidents/checklists/charts)本就必带 `last_updated`，workflow 类反而没有 → 被多轮修订的长命 spec(spec-evolution-markers 针对的场景)判断不出 staleness。
3. **关系散落正文。** 一个 spec 常对多个 plan、或取代/修订旧 spec。plan→spec 已有 `implements:`；但 **spec↔spec**(取代/关联)只是正文散文，不可结构化查询，归档时查齐成本高。

## 2. 设计

### 2.1 `summary`：权威源进 frontmatter，INDEX 行从它派生

- spec/plan/sketch frontmatter 加 `summary: <一行摘要>`。
- `INDEX.md` 的 AUTO 行**改为从各文件的 `summary` 派生**(INDEX 生成本就读 frontmatter 的 `status`，现在顺带读 `summary`)。
- 效果：活跃期不重复(INDEX 行是生成物，符合"Link, don't copy")；归档后摘要随文件进 `landed/` 不丢。

### 2.2 `last_updated`：与知识类统一

- 加 `last_updated: YYYY-MM-DD`，字段名复用知识类工件的同名字段。
- 内容实质变化时 bump(typo 不算)；与 git 修改时间重叠是已知的，但知识类明知有 git 仍带它(不翻 git、移进 landed 后也能一眼看新旧)—— 此处一致，非冗余。

### 2.3 关系边：纯 YAML 路径，不引 Obsidian `[[ ]]`

- 保留 `implements:`(plan→spec，已存在)。
- 新增 **`supersedes: <path>`**(取代旧工件，正向边，挂在新工件上)。可选回填 **`superseded_by: <path>`** 到被取代的旧工件以便从旧文件正向发现。
- 需要更泛关联时加 **`related: [<path>, ...]`** 列表。
- 取值一律**相对路径**(相对 flightdeck 根)，非 wikilink。

**已决：不引入 Obsidian `[[wikilink]]` 双链。** 两条理由：
1. `[[ ]]` 只在 Obsidian 渲染成链接，GitHub / 多数 markdown 查看器里是字面量 → 破坏 flightdeck "tool-agnostic 纯 markdown、哪都能渲染"的核心赌注。已有跨引用约定是正文标准 markdown 链接 `[hook](path)`(walkaround Audit 7 查死链)。
2. `[[ ]]` 的真正价值是自动反向链接面板，flightdeck 运行时(AI + git + grep)没有该面板 —— 反向链接在这里靠 grep/派生实现。

**双向靠派生，不手维护两头。** 只存正向边(`implements` / `supersedes` / `related`)；反向(如"某 spec 的所有 plan"、"谁取代了我")用一条 `grep` 从 frontmatter 算出 —— **只读 frontmatter、不读正文**，这正是降 token 的点。手存双向 = 改一边忘一边就烂(与 INDEX 派生同哲学)。

> 注意：workflow 状态字里没有 `superseded`(那是知识类的 status 值)。spec↔spec 的取代关系**用边字段表达，与 status 无关** —— 被取代的旧 spec 仍是 `done`/`scrapped` 并归档，靠 `supersedes`/`superseded_by` 边连起来。

## 3. 落地细节

- **不设 hard-required。** 否则 walkaround Audit 1/2 会把现存所有 spec/plan 报 CRITICAL。`summary`/`last_updated` 设为**推荐**;关系边按需。这次顺手**回填**现有 spec/plan(总共没几个)。
- walkaround 可加**软检查**(缺 `summary`/`last_updated` → INFO 级提示),不升 WARNING/CRITICAL,避免对存量噪声。

## 4. blast radius

- `skills/preflight/templates.md` —— spec/sketch、plan 两个 frontmatter 模板加 `summary` + `last_updated`(+ 关系边说明);per-folder INDEX 模板的行格式说明改为"从 `summary` 派生"。
- INDEX 生成逻辑(`landing` / `status` / `walkaround` 中重生成 AUTO 区处)—— 读 frontmatter 时一并取 `summary`。
- `skills/walkaround/SKILL.md` —— Audit 2 范围说明(workflow 不强制这些字段);可选 Audit：缺 `summary`/`last_updated` 报 INFO;Audit 3 `superseded_by` 概念扩到 spec(边而非 status)。
- `skills/preflight/protocol.md` —— 数据模型 / frontmatter 字段表同步。
- `scaffolds/**` —— 示例工件(如有)补字段。

## 5. 非目标

- 不动知识类工件的 frontmatter(它们已有 `when_to_read`/`applies_to`/`last_updated`)。
- 不引入任何 Obsidian / 工具专属语法(见 §2.3)。
- 不把关系边设成 hard-required，不阻断现有 deck。
