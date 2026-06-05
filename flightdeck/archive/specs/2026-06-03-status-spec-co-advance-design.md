---
status: done
summary: plan 全部 done 但其 implements 的 spec 滞后 active；交由 landing 对账（脚本 spec_advance_candidates + CLI --advance-candidates）confirm-gated offer 推进 spec→done，绝不自动碰第二工件，确认后同轮进 archivable 一起归档
last_updated: 2026-06-06
related: [archive/specs/2026-06-03-rules-simplification-design.md]
---

# `status` 推进 plan 但不带动其 spec

> 由 sketch `status-spec-lags-plan` 提升（2026-06-03）。dogfood 2.3 期间反复观察到，已在本次归档这批 spec 时再次撞上。

## Problem

`status` 技能精确只作用于一个工件（被编辑 / 正在执行的那个）。完成或推进一个 `plans/` 工件，从不会推进它 `implements:` 的 `specs/` 工件。结果：一个 spec 可以在它的 plan 跑完整个 `active → awaiting-review → done` 期间一直停在 `pending`；co-land 簇在 Land Routine 能干净归档前，需要一次手动把 spec → `done` 的 nudge。

## Proposed design

候选增强（落在 `status` 技能的 target 解析，Step 2）：当把一个 plan 翻成 `done` / `awaiting-review` 时，**offer**（confirm-gated）推进它 `implements:` 的 spec。

铁律：绝不自动翻第二个工件——那会违反「一次一工件、高置信」原则。提示由用户拍板。

**备选**：不在 `status` 里做，改由 `landing` 在归档时对账——把一个 spec 的状态与其已 `done` 的 plan 核对，提示是否一并推进。

## Open questions

- 放在 `status`（即时、贴近翻转点）还是 `landing`（集中对账、避免每次翻转都问）？
- 若 plan 有多个 `implements:` 目标，offer 是否逐个确认？
- 与 incident-recurrence-autocount / scriptable-lint 的 landing 自动化如何分工，避免重复 offer。

## 决策与落地（2026-06-06）

选 **landing 对账**（非 status 即时）。理由：保住 status「单工件、高置信、绝不碰第二工件」铁律的纯粹性；复用 landing 已有的 `implements:` 边图（与 `--archivable` 同源）；集中对账不打断高频 status；与全自动流契合（status 每次翻转都问会打断）。

落地：
- **脚本** `flightdeck_index.py`：新增 `spec_advance_candidates(deck)` —— active spec 且其 `implements:` 它的 plan **全部 `done`**（≥1 done、无 active/idea plan 仍指向它）；确定性、只读、复用 implements 边。加 CLI `--advance-candidates`（同 `--archivable` 模式）。
- **landing SKILL** Step 3a：算 `--archivable` 前先跑 `--advance-candidates`，逐候选 **confirm-gated** offer 推进 spec→done（用户判断设计是否真落地，绝不自动）；确认后 spec 进**同轮** archivable 集，spec+plan 簇一起归档。
- **测试**：7 个 `SpecAdvanceCandidatesTest`（全 done→候选 / 仍有 active plan→否 / done spec→否 / 无 plan→否 / 仅 idea plan→否 / 多 done plan 去重 / implements 指向不存在 spec 忽略）。

**回答 open questions**：① 放 landing；② 候选判定按「该 spec 的全部 implements plan 都 done」聚合，offer 以 spec 为单位（不逐 plan 问）；③ 走 `implements:` 边，与 recurrence sweep（incident 签名）/ archivable（done 归档）正交，无重复 offer。
