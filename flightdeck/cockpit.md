# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-04 by 月离 (本会话：设计+实现两特性并入 3.0——**preflight 瘦身 + 拆 `/flightdeck:launch`**〔preflight 改纯接管、Branch-0 重定向、setup→launch、删重复检查、doc-sweep〕与 **`/flightdeck:new` 撰写入口**〔`flightdeck_new.py`+12 测试、SKILL 撰写契约、protocol/emit 发现钩子、README/adapters〕；79 tests 绿、deck lint+`--check` clean。两者均待 reload 后交互 dogfood)
**Active focus**: flightdeck 3.0 收尾——model-v4 + scriptable lint + **preflight 瘦身/launch 拆分** + **`/flightdeck:new` 撰写入口** 均实施完成；剩发布前 reload 后交互 dogfood 验证 + AGENTS emit + 发布 → 合并 main。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-03-incident-recurrence-autocount-design.md](specs/2026-06-03-incident-recurrence-autocount-design.md) — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
- [2026-06-03-model-v4-folder-state-cockpit-design.md](specs/2026-06-03-model-v4-folder-state-cockpit-design.md) — flightdeck 模型 v4——folder 7→5（sketches 并入 specs、删 debriefs）、workflow 状态 6→4（idea/active/done/scrapped）、cockpit 由 AI 全自动驱动（进行中区 AUTO 派生 + 下一步自动维护），并入 3.0
- [2026-06-04-command-simplify-scriptable-version-design.md](specs/2026-06-04-command-simplify-scriptable-version-design.md) — 自治面收敛到底(真删 self-invoke/disabled_folders/run-scripts(转推断)/status:auto-land 开关，换好默认+推断+判断) + 智能 landing(智能归档替 auto-land) + commit 翻默认(本地自调/push 先问，override 保留) + 版本/布局判定脚本化(verdict 源自 MIGRATION frontmatter) + 版本职责单一归属(preflight 只读上报/landing 只读守卫/walkaround 唯一写) + preflight 删 Branch-0；并入 3.0
- [2026-06-04-new-artifact-authoring-convention-design.md](specs/2026-06-04-new-artifact-authoring-convention-design.md) — 撰写新 deck 工件每次交"推导税"（按-kind frontmatter / 命名 dateless-vs-dated / 记得 regen——位置实践中已可靠落对 flightdeck/specs/，不是痛点）。选定方向 B：新增 /flightdeck:new skill 包 flightdeck_new.py，确定性盖按-kind frontmatter + 命名 + 落目录 + regen，覆盖全部工件种类，shell-first 交接；SKILL=权威撰写契约文档面（含方向 A）。发现靠常驻指针（protocol 节 + emit-agents-md 模板行 + skill description）——目的是让 agent 用入口而非手搓，不防 docs/。并入 3.0
- [2026-06-04-preflight-slim-launch-split-design.md](specs/2026-06-04-preflight-slim-launch-split-design.md) — preflight 太重（兼管初始化/检查/接管）——拆出 `/flightdeck:launch` 接管首次创建 deck，preflight 瘦成纯接管（读 cockpit/INDEX → 报下一步 + 精简 catalog 预热 + 被动一行 git 提示），删掉与 walkaround 重复的检查（结构性迁移探测/catalog 状态体检/cockpit 漂移/阻塞式 reconcile）。并入 3.0
- [2026-06-05-model-coherence-mainstream-naming-design.md](specs/2026-06-05-model-coherence-mainstream-naming-design.md) — 彻底理清 flightdeck 生命周期+文件夹模型并立主流命名铁律——status⟂location正交(landed非状态/done≠归档)、done翻转 end-of-turn 防抖接力landing(方案A出厂默认/push先问)、归档判据确定性结构边(脚本可算/不靠AI正文)、航空名只留指令与仪式、数据模型全主流(charts→references、landed→archive、新增docs/)、knowledge可嵌套撑大型项目、status自动翻转收成唯一权威表；并入3.0
- [2026-06-03-model-v4-rollout.md](plans/2026-06-03-model-v4-rollout.md) — model-v4 分 6 phase 实施——数据模型真相源 → flightdeck_index 扩展(+测试) → 4 skill 行为 → scaffolds/emit/MIGRATION → dogfood 迁移本仓库 → 验证收尾；并入 3.0
- [2026-06-04-command-simplify-scriptable-version-rollout.md](plans/2026-06-04-command-simplify-scriptable-version-rollout.md) — 实施 spec：脚本层(layout_verdict + format_row 健壮性, TDD) → 5 skill 改(删 Gate / 智能 landing / commit 默认 / verdict 接线) → protocol + scaffold 模板 → MIGRATION + dogfood rules → 验证(pytest / --check / walkaround / reload dogfood) + 发布提醒
- [2026-06-04-new-artifact-entrypoint.md](plans/2026-06-04-new-artifact-entrypoint.md) — 实现 /flightdeck:new + flightdeck_new.py——TDD 建脚本（kind→folder 常量表、按-kind frontmatter、命名 dateless/dated、参数校验报错、调 flightdeck_index regen + status-aware stdout），再建 skills/new/SKILL.md（fast path + 权威撰写契约 fallback），接发现钩子（protocol 节 + emit 模板行 + description），验证 + dogfood，最后文档 + 发布提醒
- [2026-06-04-preflight-slim-launch-split.md](plans/2026-06-04-preflight-slim-launch-split.md) — 实现 preflight 瘦身 + 拆出 /flightdeck:launch——新建 launch skill（搬 setup.md）、重写 preflight（重定向 Branch-0 / 删重复检查 / 2 列 catalog / 被动 git 表 / 版本 bump 优先级）、删 setup.md、改两条 description、交叉引用 doc-sweep；验证靠现有 pytest + index --check + dogfood + walkaround。清单自动发现无需注册，CHANGELOG 留发布时写
- [2026-06-05-model-coherence-rollout.md](plans/2026-06-05-model-coherence-rollout.md) — 实施模型理清 spec：脚本层(改名 charts→references/landed→archive、认 docs、knowledge 嵌套 INDEX-of-INDEXes、可归档 done 集、scrapped 分组、旧名结构信号, TDD) → lint/init/new → 模型文档(protocol/folder-semantics/templates/exit-ritual) → 4 skill 行为(status/landing/preflight/walkaround) → scaffold+MIGRATION+README → dogfood 迁移本仓库 + 全套验证 + 发布提醒
<!-- /AUTO -->

## 下一步

- 发布前交互 dogfood（reload 后）：① model-v4（preflight 读新 cockpit / status idea→active 带动 `## 进行中` / landing 写两区）；② preflight 瘦身（deckless → `/flightdeck:launch` 重定向、slim 接管 2 列 catalog + 被动 git 提示、无阻塞 reconcile）；③ `/flightdeck:new`（建各 kind 壳 + 发现钩子是否真让 brainstorming/agent 交接而非手搓）。
- dogfood 通过后：preflight-slim / new-artifact 的 spec+plan 翻 `done`；重跑 `/flightdeck:emit-agents-md` 消 AGENTS.md drift。
- 发布 3.0：version-bump + CHANGELOG（写 `/flightdeck:launch`、`/flightdeck:new` 两条 + preflight deckless 行为变更）+ marketplace + tag + 合并 → main（见 [checklists/version-bump.md](checklists/version-bump.md)）。
- （可选）记一条 `flightdeck_index.format_row` 对缺-`summary` workflow 文件 KeyError 的健壮性缺口（reload 后可用 `/flightdeck:new` 自举 dogfood）。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
