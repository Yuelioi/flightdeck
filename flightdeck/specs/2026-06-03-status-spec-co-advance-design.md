---
status: pending
summary: status 只推进正在执行的工件，spec 会停在 pending 而其 plan 已 done；提议 plan 翻 done/awaiting-review 时 confirm-gated 地 offer 推进其 implements 的 spec，或交由 landing 对账。由 sketch 提升
last_updated: 2026-06-03
related: [landed/specs/2026-06-03-rules-simplification-design.md]
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
