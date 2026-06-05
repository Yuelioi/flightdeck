# flightdeck — Documentation

The [README](../README.md) is the 2-minute quick start. These pages are for going deeper.

> **What's canonical:** the AI-facing protocol the skill actually executes lives in [`skills/preflight/`](../skills/preflight/) and is the source of truth. These docs are the **human narrative** — they explain and link, they don't redefine.

## Guides

- **[Architecture](architecture.md)** — how flightdeck, your AI, and `AGENTS.md` fit together.
- **[Design philosophy](philosophy.md)** — why a write gate, why the lifecycle, why the 80-line ceiling, why aviation.
- **[How it compares](comparison.md)** — vs AGENTS.md, Cline Memory Bank, OpenSpec, Cursor MDC, Letta Code.

## Reference (canonical, AI-facing)

- [protocol.md](../skills/preflight/protocol.md) — data model · authority order · routing · write gate · Rule resolution order
- [folder-semantics.md](../skills/preflight/folder-semantics.md) — what each folder holds
- [templates.md](../skills/preflight/templates.md) — per-file frontmatter + templates
- [exit-ritual.md](../skills/preflight/exit-ritual.md) — the landing ritual
- [MIGRATION.md](../MIGRATION.md) · [CHANGELOG.md](../CHANGELOG.md) — version upgrades · history
