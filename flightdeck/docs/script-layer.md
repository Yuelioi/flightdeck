---
status: active
when_to_read: 改 flightdeck_index.py 或脚本层行为前
applies_to: [scripts/flightdeck_index.py, scripts/flightdeck_lint.py]
last_updated: 2026-06-10
summary: 脚本层（flightdeck_index.py / flightdeck_lint.py）的职责——确定性 INDEX 再生、archivable_done/obsolete、knowledge 嵌套 INDEX-of-INDEXes；以及 model/judgment 与 script/facts 的分工
---

# flightdeck 脚本层

讲清 `scripts/` 这层**怎么运作**、它和模型层（skill 文档 + AI 判断）怎么分工。改 `flightdeck_index.py` / `flightdeck_lint.py` 前先读，避免把本属于「判断」的逻辑塞进脚本、或反过来让 AI 去手算本该确定性的事实。

## 分工铁律：script 算 facts，model 留 judgment

脚本层只做一件事：**从 deck 文件计算确定性事实**（同输入→同输出，无需上下文、无需判断）。所有需要权衡、解读、与用户确认的，留在模型层（skill 文档驱动 AI）。

| 属于 script（facts） | 属于 model（judgment） |
| --- | --- |
| 从 frontmatter **重生** INDEX 的 AUTO 区 | 新知识该归哪个 kind 的分类 |
| `archivable_done` / `archivable_obsolete`（可归档集） | 状态该不该往前翻、要不要 land |
| INDEX↔folder drift 检测 | AGENTS.md 语义漂移、stray 文件可达性 |

这条线是脚本层全部设计的总纲：脚本吐一行 JSON / 一行确定性结论，AI 据此判断。脚本在子进程跑、读文件不进上下文，模型只见结论——这是 token 经济性的来源。

## flightdeck_index.py — INDEX 再生引擎

纯 stdlib（`uv run` 没东西要装）。核心是**从 frontmatter 重生、绝不解析旧行**——所以 summary 里含 ` — `（行分隔符）也不会把再生搞乱。几个职责：

- **确定性 INDEX 再生**：每个工件文件夹的 `<!-- AUTO:<kind> -->` 区按 kind 渲染行（`SUMMARY_KINDS` = specs/plans 出 summary 行；`KNOWLEDGE_KINDS` = checklists/incidents/docs 出 when_to_read + applies_to 行；`references` 是手维护的导入，不进自动再生）。`FOLDER_ORDER` 派生 `REGEN_FOLDERS`，决定哪些文件夹被再生及顺序——注意它 **不含 `archive`**（archive 是 location 不是 kind）。无 root INDEX：deck 不带顶层索引（3.0 de-scope），preflight 直接读 cockpit + 各 folder INDEX。
- **specs/ 特殊分组**：idea 文件无日期前缀，混进 dated 的 active/done 会乱序，所以 AUTO 区**按 status 分组**（`### Backlog (idea)` / `### Active · Done`）。（3.0 无 scrapped 状态——rejected spec 直接删，不留墓碑分组。）
- **cockpit `## In Progress` 派生**：从每个 `status: active` 的 spec/plan 派生（specs 后 plans，各按文件名）——cockpit 因此是活跃集的**状态投影**，工件 active 当且仅当它在 cockpit。
- **knowledge 嵌套 INDEX-of-INDEXes**：`NESTABLE_KINDS`（incidents/checklists/docs/references）有子目录时，顶层 INDEX 退化成每个 area 一行（purpose + last_updated 取自 area/INDEX.md frontmatter），preflight 只读顶层、按需下钻。
- **可归档集 + drift + stale 锚点**：`--archivable` 吐确定性可归档集（done 无 active 入边 / obsolete knowledge）；`--check` 报 INDEX↔folder drift 不写盘；`--verify-pending` 吐待验证清单；`--changed-since-anchor` 吐自 `Flightdeck-Sync:` 锚点以来的变更路径（landing 退场单仪式据此机械翻 stale）。

## flightdeck_lint.py — 机械子集审计

`walkaround` 整套审计里，**无歧义、可机械判定**的那部分下沉到这里（status 合法性 / orphan plan / INDEX↔folder drift〔复用 `flightdeck_index.index_drift`〕/ dangling ref / stray file 子集），吐 `{"findings":[…]}` JSON，有 CRITICAL/WARNING 时 exit≠0。需要可达性整体推理、知识分类等**判断项**仍留模型——这正是上面那条分工线在 lint 侧的落点：lint 抓确定能抓的，剩下交给 walkaround 的 AI 判断。

> 3.0 = 格式基线第 0 版：脚本层**无 layout verdict / 版本守卫 / 迁移检测**（整套向后兼容子系统已删）。`MIGRATION.md` 只剩 `current` 戳；迁移机制等 3.1 真改格式时按需就地建。
