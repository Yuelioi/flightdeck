---
status: done
summary: scrapped 状态退役——否决 workflow 工件＝直接删文件(git 留史+commit body 记原因)，取消 scrapped status 值与 ### 已否决 墓碑分组，一并消灭"计数≠可见行"+"文档↔代码漂移"两 bug。落地：STATUS_ORDER/WORKFLOW_STATUSES 去 scrapped、folder_summary/_specs_grouped_body/layout_verdict 去特例、6 skill+MIGRATION/CHANGELOG 对齐、lint 标遗留 scrapped 为 illegal、连带删过时 docs/lifecycle.md
last_updated: 2026-06-06
---

# scrapped 工件归宿重定 + 修计数/文档不一致

> 起因（2026-06-05 dogfood）：审核 idea 池时质疑「作废工件留 specs/ 不是污染吗」，
> 顺藤摸出现状 scrapped 处置的张力 + 两处代码/文档不一致。

## Problem

scrapped（已否决的 workflow 工件）现状处置自相矛盾、且像污染：

1. **留 specs/ 当墓碑**：`flightdeck_index.py` 把 scrapped 列在 specs/INDEX 的
   `### 已否决（scrapped）` 分组（`regen_folder_index`，且两测试断言），文件不删不归档。
2. **Land Routine 从不归档 scrapped**（exit-ritual：only done lands），所以它永远滞留 specs/。
3. 设计理由：`archive/` 语义 = **完成并落地**的工作，塞进否决物会污染「archive 里都做成了」
   的含义。代价 = specs/ 堆死设计。

## 两处已确认不一致（顺手修）

- **计数 ≠ 可见行**：`folder_summary`（specs）**排除** scrapped 计数（`:108`），但
  `regen_folder_index` **列出** scrapped（`### 已否决`）。→ 有 scrapped 时 root 计数 < 可见
  INDEX 行数，破坏 `folder_summary` 注释自称的「count 应 = 可见行数」不变式。
- **文档 ↔ 代码漂移**：`folder_summary`/`regen_*` 多处 docstring 与 exit-ritual/landing SKILL
  写「scrapped never appears / skips scrapped」，与代码实际的 `### 已否决` 分组**矛盾**
  （与 2026-06-05 修的 SKILL.md kind 表漂移同类——文档面滞后脚本面）。

## 候选方向（下次定）

1. **直接删（倾向）**：scrapped = 删文件，历史靠 `git log`。符合「果断删减 / history-logs-are-junk」
   一贯偏好；specs/ 只留活设计；archive/ 语义纯净。代价：放弃理由若只在正文，删后要翻 git。
   → 可在删前要求一行 `scrapped_reason` 落 commit body。
2. **归档到 archive/（带标记）**：移 archive/，但加 `status: scrapped` 区分，archive/ 不再纯 done。
3. **维持墓碑**：保留 `### 已否决`，但修计数（把 scrapped 计入可见行）+ 对齐文档。最小改动、
   但没解决「specs/ 堆死设计」的根本质疑。

## 决策点

- 选方向后，scrapped 语义需在 protocol / folder-semantics / status SKILL / Land Routine / lint
  + `flightdeck_index.py`（`folder_summary` / `regen_folder_index` / `archivable_done`）一致落地。
- 无论选哪个，先修「计数≠可见行」+ 文档漂移（独立的小 bug，不必等大方向）。

## 决策与落地（2026-06-06）

选 **方向 1（彻底删 + 取消 status 值）**——最果断、消灭俩 bug、无死结构（符合 [[prefers-decisive-deletion]] / [[history-logs-are-junk]]）。否决一个 workflow 工件＝**直接删文件**（仅用户显式指示；git log 留史 + commit body 记一行原因）。不再有 `scrapped` status 值、`### 已否决` 分组、墓碑。

落地清单：
- **代码**：`STATUS_ORDER` / lint `WORKFLOW_STATUSES` 去 `scrapped`；`folder_summary` 去 specs-scrapped 排除特例；`_specs_grouped_body` 去 `### 已否决` 分组；`layout_verdict` 去 scrapped-免-summary 特例；`flightdeck_new.py --status` choices 去 scrapped。
- **测试**：删 4 个 scrapped 专测（分组/计数排除/missing-summary/own-group）、改 `STATUS_ORDER` 断言、新增「遗留 `status: scrapped` 被 lint 标 illegal WARNING」。137 tests 绿。
- **两 bug 自动消灭**：移除 scrapped 渲染特例后，「计数≠可见行」与「文档↔代码漂移」矛盾不复存在。
- **文档一致**：protocol / folder-semantics / templates / status SKILL / walkaround SKILL / landing SKILL / exit-ritual 共 ~30 处对齐；MIGRATION（status 6→3、遗留 scrapped 迁移即删）；CHANGELOG（撤未发布的「scrapped 单列」Added、改记「scrapped 退役」）。
- **连带清理**：删过时的 `docs/lifecycle.md`（2.0 废弃模型 sketch/pending/awaiting-review/landed/debriefs，且与 model-architecture/protocol 重复），并移除 3 处 README 对它的引用。
