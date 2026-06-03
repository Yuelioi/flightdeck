---
status: pending
summary: preflight 静默 bump 版本时新的 autonomy/commit 默认对升级者不可见；提议在静默 bump 的那一回合打一行一次性提示，指向对应 MIGRATION 段。由 sketch 提升
last_updated: 2026-06-03
related: [landed/specs/2026-06-03-rules-simplification-design.md]
---

# preflight 静默 bump 既有 deck 时给一行升级提示

> 由 sketch `preflight-upgrade-nudge` 提升（2026-06-03）。dogfood 在 flightdeck 自身 deck 上确认。

## Problem

当 `preflight` 静默地把既有 deck 的 `version` 往上 bump（如 2.2 → 2.3，无 layout 变更、走 silent-bump 分支）时，deck 在用户视角下没有任何可见变化：新的 autonomy / commit 默认只通过 first-time-setup 随**新建** deck 出厂。升级者看到的是「version 变了，行为没变」，永远不会得知新开关的存在。

> 3.0 升级本身是 `layout_need_update` 里的**非静默**迁移（会主动询问），所以这个缺口主要影响未来 3.0 → 3.x 的静默 bump，而非 3.0 发布本身。

## Proposed design

在 preflight Step 2 的 silent-bump 分支：当发生一次静默 bump，打**一行**提示——例如 `deck bumped X → Y; 新的 autonomy / commit 默认是 opt-in — 见 MIGRATION X→Y`。

- 仅在发生 bump 的那一回合打印，不是每次进场都打。
- 低成本，闭合可发现性缺口。

## Open questions

- 提示文案是否引用 `MIGRATION.md` 的具体段落锚点？
- 与 walkaround 的「有 N 条已确认迁移注释可清理」提示是否合并到同一处。
