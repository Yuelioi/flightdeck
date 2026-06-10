# How it compares

flightdeck sits **on top of** [AGENTS.md](https://agents.md), not against it, and adds a lifecycle + write discipline that raw memory tools don't have.

| | flightdeck | [AGENTS.md](https://agents.md) | Cline Memory Bank | OpenSpec | Cursor MDC | Letta Code |
| --- | --- | --- | --- | --- | --- | --- |
| Static project rules | via emit | ✅ native | — | — | ✅ | — |
| Session-to-session continuity | ✅ | — | ✅ | — | — | ✅ |
| Lifecycle model (folder=kind · status · archive) | ✅ | — | — | ✅ | — | — |
| Strict write gate (anti junk-drawer) | ✅ | — | — | — | — | — |
| Incident / lesson tracking (root-cause) | ✅ | — | — | — | — | — |
| External review disposition | ✅ | — | — | — | — | — |
| INDEX-first token saving | ✅ | — | — | — | — | — |
| Single explicit entry (`/preflight`) | ✅ | — | — | — | — | — |
| Tool-agnostic (markdown + filesystem) | ✅ | ✅ | partial | ✅ | Cursor-only | — |

- **AGENTS.md** — the wire format for static rules. flightdeck **emits into** it, doesn't compete with it.
- **Cline Memory Bank** — raw memory persistence; flightdeck adds lifecycle + write discipline.
- **OpenSpec** — the closest sibling for spec evolution; flightdeck adopts its `ADDED:` / `MODIFIED:` / `REMOVED:` markers.
- **Cursor MDC** — a path-scoped frontmatter tag; flightdeck carries MDC frontmatter on incidents / checklists for Cursor interop.
- **Letta Code** — a skill-library promotion pattern; flightdeck adopts the gate-based incident → checklist promotion.

flightdeck is **opinionated**: write gate before storage, lifecycle before memory, peer reviews before merge. If only static project rules are what you need, **AGENTS.md alone is enough** — flightdeck is for the cases that need continuity and discipline on top.
