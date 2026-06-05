---
status: active
when_to_read: 改 flightdeck 数据模型 / 文件夹分类 / 状态语义前
applies_to: [skills/preflight/protocol.md, skills/preflight/folder-semantics.md, scripts/flightdeck_index.py]
last_updated: 2026-06-05
summary: flightdeck 数据模型怎么运作——status⟂location 两条正交轴、文件夹按 kind 分类（自撰/导入 × 一次性/常驻）、命名铁律、确定性归档判据
---

# flightdeck 数据模型架构

讲清 flightdeck 的数据模型**怎么运作**（不是怎么操作）。维护 `protocol.md` / `folder-semantics.md` / `flightdeck_index.py` 前先读这篇，避免把「状态」「位置」「类型」三个范畴重新搅成一团——历史上 2.0 的状态机就是这么崩的。

## 两条正交轴：status ⟂ location

模型最核心的设计是把两个**互相独立**的轴拆开。历史上「done = 已归档」的误判，根因就是把它们画了等号。

- **status**（状态）∈ `{idea, active, done, scrapped}`（workflow）/ `{active, obsolete, superseded}`（knowledge）——*工件走到哪一步*。它是 frontmatter 里**显式写下**的值。
- **location**（位置）∈ `{源文件夹, archive/}`——*它还在不在活跃区*。它是**派生的、不是 frontmatter 字段**（由「是否在 `archive/` 下」算出），但是**一等概念**：它驱动**路由**（`archive/` 整个排除出路由图）和**归档判断**（landing 决定 done 工件是否落 archive）。

一句话：**status 说「哪一步」，location 说「在不在活跃区」，而 landing 是唯一的搬运者。**

由此 `done` 工件有两个合法位置：**done-but-unlanded**（仍在 `specs/`，因为还有 active 工件引用它）与 **done-and-archived**（已搬进 `archive/`）。三条硬不变量：`archived`/`landed` **永不是状态值**（没有文件写 `status: landed`）；**只有 landing 的 Land Routine 能把东西搬进 `archive/`**；AI 永不手写归档标签、也永不在没真跑 landing 时宣称已归档。

## 文件夹 = kind：自撰/导入 × 一次性/常驻

**文件夹就是类型**——所以工件 frontmatter 不带 type 字段，放进哪个文件夹就决定了它是什么 kind。六个工件文件夹沿两个维度铺开：

|  | 一次性（drain，完成后排进 archive） | 常驻（accumulate，永不因完成而归档） |
| --- | --- | --- |
| **自撰** | `specs/`（设计/想法）、`plans/`（实施计划） | `incidents/`（错题本）、`checklists/`（要*执行*的流程/规范）、`docs/`（要*读懂*的解释性知识） |
| **导入** | —— | `references/`（外部材料：竞品代码 / RFC / 文章） |

三个 knowledge 文件夹的边界要分清：`checklists/` = 你**执行**的过程；`docs/` = 你**读来理解**系统的解释性知识；`references/` = **外部导入**的材料。最常见的错误是把常青参考资料塞进 `specs/`——spec 是「打算实现然后归档的设计」，常青资源属于 knowledge 文件夹。

`archive/` 不在上表里：它**不是一个 kind**，是 location 轴落到磁盘上的样子。它按需镜像源文件夹（`archive/specs/`、`archive/plans/`…），工件搬进去仍保留自己的 kind，只是退出了活跃区。所以脚本的 `FOLDER_ORDER` 里没有 `archive`，root INDEX 也不为它出行。

**drain vs accumulate** 是「一次性/常驻」这条轴的深层理由：workflow 一旦 `done` 就排进 `archive/`，活跃集容量有界，扁平 + INDEX 日期排序就够；knowledge 常驻且只增长（永不因完成而归档），所以需要按 area 嵌套来在规模下保持可导航。这也解释了为什么 `specs/`/`plans/` 严禁子文件夹、而 `incidents/`/`checklists/`/`docs/`/`references/` 可按 area 嵌套成 INDEX-of-INDEXes。

## 命名铁律：隐喻 vs 主流

数据模型里的文件夹名**一律用主流词**，不让航空隐喻渗进去要先懂隐喻才能猜「东西该放哪」。3.0 把仅剩的两个隐喻名改主流：`charts/ → references/`、`landed/ → archive/`。状态值（`idea/active/done/scrapped`、`active/obsolete/superseded`）本就是主流词，不改。

产品名 `flightdeck/` 与纯交互入口 `cockpit.md` 是**保留的隐喻**——它们是品牌/界面，不是数据模型分类，不受铁律约束。区分原则：**会影响「东西放哪」判断的名字必须主流；纯品牌/界面名可保留隐喻。**

## 确定性归档判据

`done` 工件何时能落 `archive/`，是一条**确定性结构判据**，不靠 AI 读散文链接拍脑袋：

> 一个 `done` 工件可归档 **当且仅当 没有任何 `active` 工件经结构化边指向它**。

结构化边只有两种：`active` plan 的 `implements:` 指向 done spec；`active` knowledge 的 `superseded_by` 指向它替换的那个。`flightdeck_index.py --archivable` 把「可归档 done 集」算成**可复现的事实**（同输入→同结论）；散文里的 markdown 链接只给人看，**不进判据**。被某条 active 入边指着 → 留在 done-but-unlanded。

由此「整簇完成才一起 land」不再是手写注释里的约定，而是模型内化的能力：只要还有 active 工件引用簇里的 done spec，整簇就自动留在原地；引用一解除，下次 landing 自动把它扫进 archive。**Drain, don't accumulate**——每次 landing 重扫**全部** done-in-place（不止本会话），入边清空的自动排空，永不滞留。
