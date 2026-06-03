# Lifecycle & execution flow

How a flightdeck session runs, and how a piece of work moves from idea to archive.

## Session flow

Every working session is bracketed by two rituals, with a lightweight one keeping state fresh in between:

```
session start ─▶ /flightdeck:preflight ─▶ … work … ─▶ /flightdeck:landing ─▶ session end
                 read cockpit, reconcile    status keeps    classify, refresh
                 git, report next item      state current   cockpit, commit
```

- **preflight** (entry) — reads `cockpit.md`, reconciles against `git status`, and reports the next item. On a brand-new project it runs first-time setup instead (copies the scaffold in one step — zero prompts). → [SKILL.md](../skills/preflight/SKILL.md)
- **status** (mid-session, automatic) — as work moves it keeps each artifact's `status:` current and its `INDEX.md` row in sync, so the next `preflight` reads truth. → [status/SKILL.md](../skills/status/SKILL.md)
- **landing** (exit) — classifies new knowledge into the right folder, refreshes `cockpit.md`, and commits. → [exit-ritual.md](../skills/preflight/exit-ritual.md)

By default the AI runs these itself when it judges the moment right; `commit` stays a confirm checkpoint. Nothing fires on session start and there's no background process.

## Artifact lifecycle

Work moves through folders by **kind**, and through `status` values **within**:

```
sketch ──promote──▶ spec ──break down──▶ plan ──(work)──▶ done ──land──▶ landed/
 idea                design               steps                          archive
```

The `status` field advances along:

```
pending ─▶ active ─▶ awaiting-review ─▶ done
            ▲  │
            └──┴─ blocked            any active state ─▶ scrapped
```

When an artifact reaches `done` (or `scrapped`), landing **archives** it into `landed/` — out of the active tree, kept as history. Knowledge artifacts (`incidents/` `checklists/` `charts/` `debriefs/`) use a simpler `active → obsolete | superseded` and usually stay in place.

Authoritative rules: [protocol.md](../skills/preflight/protocol.md).

## Where new knowledge goes

At landing, each new thing is routed by kind:

| You produced | Goes to |
| --- | --- |
| a bug + root cause | `incidents/` |
| a repeatable procedure (2nd time seen) | `checklists/` |
| a design decision | `specs/` |
| a multi-step task | `plans/` |
| external review feedback | `debriefs/` (with disposition) |
| imported external material | `charts/` |
| a rough idea | `sketches/` |
| a one-off / session byproduct | discarded (write gate) |

Full classification heuristics: [exit-ritual.md](../skills/preflight/exit-ritual.md).
