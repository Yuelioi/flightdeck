---
status: idea
summary: scrapped 现状=留 specs/「已否决」分组当墓碑、root 计数却排除它(→计数≠可见行)、Land Routine 不归档；多处 docstring/SKILL 说「scrapped never appears」与代码 ### 已否决 分组矛盾。重定 scrapped 处置(倾向直接删、git 留史，符合果断删减) vs archive vs 留墓碑，并修计数≠可见行 + 文档↔代码漂移
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
