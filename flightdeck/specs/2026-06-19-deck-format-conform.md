---
status: active
graduate: true
summary: A strict deck formatter that conforms every active file to its canonical schema/template: a script deletes non-schema frontmatter fields across all files and adds missing section skeletons + drops non-standard sections on the two root files (cockpit.md/rules.md), then the AI fills semantic fields (when_to_read/applies_to/summary/Focus/Stage) by reading the file; excludes archive/ and stray folders; no migration registry, no history kept.
last_updated: 2026-06-19
---

# Deck format conform (strict formatter)

## 1. 动机

flightdeck 格式一直在演进(cockpit 字段重命名、recorded-config 字段加入、退役 toggle…)。**老 deck 不会自动跟上**:隔壁 `organizations/nuxtblog` 就是 alpha.3 之前建的——cockpit 还用 `**Last updated**` / `**Active focus**` 老字段名、缺 `## Key Context` / `## Pending Review`、rules 缺 `runtime` / `agents_md`。用户不想重装,也不想维护一份「升级指南」。

判据:**不要显式升级指南,只要一个对标模板的 strict formatter**——把 deck 文件捏成当前 canonical 形,缺的补、多的删。像 `gofmt`,不是迁移框架。

## 2. 范围

**作用面 = 活跃 deck 文件**:

- 根 2 文件 `cockpit.md` + `rules.md`(**细致档**:frontmatter + section 结构都管)。
- 标准 folder 的非 archive 文件:`specs/` `plans/` `incidents/` `checklists/` `docs/` `references/`(含合法 area 嵌套)——这些**只管 frontmatter**。

**排除(不碰、不审、不扫)**:

- `archive/` —— 冻结历史。
- 杂目录 / 不在标准 folder 模型里的文件夹 —— 不是 conform 的范围(顶多 walkaround 出 stray 提示,formatter 不动)。

## 3. 五类处理

| 类 | 对象 | 谁做 | 动作 |
|---|---|---|---|
| **缺的** | 任意 in-scope 文件 | 脚本 | 补缺的 schema 字段空骨架 / 默认值 |
| **多的** | 全文件 frontmatter | 脚本 | 删不在该 kind 合法字段集的字段 |
| **细致** | 根 `cockpit.md` + `rules.md` | AI | 读全文对标模板重塑(标签 / section / 缺字段,**值保留**) |
| **AI 填义** | 脚本标记的空语义字段 | AI | 读该文件补 `when_to_read` / `applies_to` / `summary` 等 |
| **不碰** | `archive/` + 杂目录 | — | 免管 |

口诀:**脚本做形,AI 填义,archive 与杂目录免管。**

## 4. 两趟

### 4.1 脚本趟(机械、确定性)

- **frontmatter 删多余**:每个文件按其 kind 的**合法字段集**(required + 全部 optional)过滤,集外字段删。合法集真相源 = `protocol.md § Frontmatter field reference` + `templates.md` 各 kind schema,**不新造**。
  - 合法可选字段(`note` / `implements` / `supersedes` / `related` / `graduate` / `verify` / `when_to_update` / `skip_when` / `recurrences` / `resolved_by` / `synced` …)保留;`portable`、退役 toggle(`git` / `emit_agents_md` / `disabled_folders`)、拼错字段 → 删。
- **rules.md frontmatter**:缺 `runtime` → doctor 探测(`uv` > `python` > `node`)填;缺 `agents_md` → 默认 `off`;`version` 缺 → 当前基线 `3.0`。
- **输出清单**:每个文件「删完后还缺哪些 required 语义字段」→ 交给 AI 趟。
- **不登记、不留历史、不写 undo 文件。**

### 4.2 AI 趟(判断)

脚本造不出有意义的语义值,这部分 AI 读文件后补:

- **cockpit.md + rules.md(细致档)**:AI 读全文,对标 `templates.md` 把两文件重塑成 canonical 形——补缺 section(`## Key Context` / `## Pending Review` → `- (none)`;rules 缺的 `## House rules` / `### Project conventions` / `### Rules` 骨架)、删非标 section、把老标签归一到 canonical(`**Last updated**` → `Updated` + 补 `Stage`、`**Active focus**` → `Focus`、`**指针**` → `Pointers`)、推断填 `Stage`。**归一是改名保值,不是删了重填**;AI 直接照模板重写,不需要「旧→新」登记表(模板就是真相)。
- **其它文件的空必填字段**:脚本清单里「缺 `when_to_read` / `applies_to` / `summary`」的文件,AI **读那一个文件**总结后补写。

> cockpit/rules 本就要 AI 全读;其它文件只在脚本标了缺必填时才触发 AI 读那一个文件补——不无差别全读。

## 5. 不变量 / 取舍

- **无登记表、无历史、无 undo**:不维护「旧字段 → 新字段」迁移表(cockpit 标签归一靠 AI 对模板重塑,不靠表);删了不留备份。
- **不可逆**:非 git 的 deck(如 `nuxtblog` org 根 `flightdeck/ 不在版本控制`)删了无 git 回滚——有意接受。
- **删的前提由用户控时机**:formatter 见非 schema 即删、不判语义。退役一个仍在干活的字段(如 `portable` 还在做母版分发),用户须**先让接管者就位再删**:`portable` → 先让 `synced` / 母库([shared-knowledge-sync](../docs/shared-knowledge-sync.md))接管这两份 checklist 的分发,再跑 formatter 删 `portable`。formatter 不替用户判断顺序。

## 6. 与 walkaround 的关系

walkaround 是 **audit-only**(只浮现 drift、从不写)。本 formatter 是**修复路**,与 walkaround 的 invariant 不冲突——它是独立动作(脚本 + AI),不是 walkaround 内嵌的 fix。现有 **Audit 16**(cockpit 字段结构 conformance)从「INFO 提示 + 手动修」让位给「formatter 一键对标」。

## 7. 待定 / 留给 plan

- **承载形式**:独立 `/flightdeck:conform` 命令 · walkaround 报告后的可选 fix 步 · 还是 landing 顺带?(倾向独立命令——职责干净、可单独跑。)
- **脚本落点 + parity**:复用 `flightdeck_lint`(已读全 frontmatter)加 `--conform` 子命令,还是新脚本?py / js 双实现 + byte-parity(沿用 alpha.4 契约)。
- **合法字段集编码**:从 protocol / templates 抽成脚本里的 per-kind set(单一真相源,防与文档漂移);怎么防漂移要 plan 定。
- **cockpit/rules canonical 骨架**:section 列表 + 占位文案 + 老标签归一表(收窄成 cockpit 头部固定几个标签,不是通用迁移表)。
- **AI 趟与脚本趟的接口**:脚本输出「缺必填字段」清单格式;AI 据此逐文件补。
- **dry-run / 预览**:非 git deck 不可逆,是否默认先出 diff 预览再写(尤其删 section/字段那种)。
