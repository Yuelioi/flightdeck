---
state: pending
---

# v1.0 = Flightdeck rebrand + board.md decomposition

**Date**: 2026-05-28
**Origin**: brainstorm from [升级执导.md](../../升级执导.md) proposal + critical review against actual workshop structure
**Status**: design — awaiting dogfood-week completion (~2026-06-02) before implementation
**Applies to**: workshop-project meta-evolution; supersedes the v1.0 scope row in [specs/2026-05-25-v0.6-to-v1.0-roadmap.md](2026-05-25-v0.6-to-v1.0-roadmap.md)
**Relates to**: [specs/2026-05-23-v1.0-release-gate.md](2026-05-23-v1.0-release-gate.md) — release-gate criteria will need amendment under new names

## Goal

Reframe the project from `workshop` to `flightdeck`, replacing a generic "maker space" identity with an "operational protocol for AI-assisted engineering" identity, and use the same breaking-change window to decompose the overloaded `board.md` into three files separated by **when you read what**.

Two motivations bundle into one v1.0 release:
1. **Naming precision**: the aviation framing — preflight / checklists / blackbox / debrief — is structurally accurate, not decorative. `workshop` undersells the operational discipline the project actually encodes.
2. **board.md is overloaded**: it carries 8 responsibilities ranging from "must read every session" to "almost never read", forcing a 300-line ceiling to fight growth pressure. The rename is the cheapest moment to split it.

## Why now

- **Pre-1.0 = the breaking-change window** ([roadmap principle 1](2026-05-25-v0.6-to-v1.0-roadmap.md)). Post-1.0 is additive only.
- **User base = 1** (maintainer). Migration cost is bounded.
- **Dogfood week ends ~2026-06-02**. v1.0 scope was always defined as "ship as-roadmapped / scope-adjust / defer" — adjusting to bundle the rebrand is within the roadmap's allowance.

## Out of scope (deferred to v1.1+)

These were in the original proposal but rejected from v1.0 to keep scope contained:

- `briefing/` folder for domain context — useful but no urgent gap; revisit when a real project has nowhere to put its term glossary.
- `blackbox/` folder for raw session log — needs new hook plumbing; not worth the cost without a clear retrieval use case.
- `crew-handover/` folder for operator transitions — board.md `Next session` already covers ~80% of this need.
- `experiments/` folder for long-running probes — already listed as a future-expansion slot; revisit when first real need appears.
- Automated migration skill (`/flightdeck:migrate-from-workshop`) — user base = 1 makes this premature engineering; a written `MIGRATION.md` is sufficient.

## Decisions

### Folder renames

| workshop | flightdeck | reason |
| --- | --- | --- |
| `specs/` | `specs/` (unchanged) | cross-domain term, no aviation equivalent improves it |
| `plans/` | `flight-plans/` | direct, accurate |
| `playbooks/` | `checklists/` | aviation's literal term for "procedure you follow step by step" |
| `scars/` | `incident-reports/` | more professional; `scars` was already metaphorical |
| `reference/` | `charts/` | aeronautical charts = pilot's reference materials |
| `sketches/` | `sketches/` (unchanged) | cross-domain term, no aviation equivalent improves it |
| `critiques/` | `safety-reviews/` | aviation peer review = safety review |
| `wip/` | `kneeboard/` | flight-deck device pilots use for *exactly* this: session-scoped scratch notes / temporary reminders. Strongest semantic match in the entire table. |
| `*/finish/` | `landed/*/` | promoted to top-level umbrella; eliminates the "active folder shadowing its own archive" inelegance. `landed` doubles as aviation term and metaphor for "completed work" |

### board.md decomposition

`board.md` splits into three files, separated by read-time:

```
flightdeck/
├── cockpit.md       # ≤80 lines. Must-read every session entry.
│                    #   - Last updated
│                    #   - Active focus
│                    #   - Next session
│                    #   - Hanging tasks
│
├── manifest.md      # On-demand. Read only when picking up flagged artifacts.
│                    #   - In flight (table of artifacts with divergent state)
│                    #   - Blockers
│
└── logbook.md       # Rarely read. For retrospective / release-notes use.
                     #   - Recently finished (FIFO cap 5)
                     #   - Deferred
```

**cockpit.md is intentionally ephemeral and operational. It is NOT a project archive.** The old `board.md` carried both "current flight condition" and "project dashboard" semantics — that bundling is what produced the 300-line ceiling pressure. Everything historical or contextual moves to `logbook.md` or out of cockpit entirely. If something feels permanent or referential, it does not belong in cockpit.

The 80-line ceiling is not arbitrary aesthetics — it is **cognitive-load engineering** for the human + AI both reading cockpit on every session start. Treat the ceiling as a load-bearing design constraint, not a style guide.

Authority order update — replaces the current `Project agent rules > board.md > active plans/ > active specs/ > playbooks/ > scars/ > archived` chain. The three new files are **peers** (they describe different facets: cockpit = what to do, manifest = what's open, logbook = what happened), so they share one rung:

```
Project agent rules > cockpit.md (≡ manifest.md ≡ logbook.md) > active flight-plans/ > active specs/ > checklists/ > incident-reports/ > landed/
```

In practice, only `cockpit.md` carries authority over operational state. `manifest.md` is an index of state divergences. `logbook.md` is immutable-ish history. The peer grouping reflects that they don't compete with each other.

Hygiene rule changes:
- cockpit.md hard ceiling: **80 lines** (down from 300). Forced by stripping out the historical/contextual sections.
- manifest.md / logbook.md: no hard ceiling. Their content is structurally bounded (FIFO cap on `Recently finished`, state-divergence-only on `In flight`).
- The `Last updated` bump trigger moves to cockpit.md.

### Command renames

| workshop | flightdeck | reason |
| --- | --- | --- |
| `/workshop:session-enter` | `/flightdeck:preflight` | strongest aviation mapping — preflight is the literal checklist before flight |
| `/workshop:session-exit` | `/flightdeck:landing` | symmetric to preflight; "landing" + "kneeboard cleanup" reads naturally |
| `/workshop:doctor` | `/flightdeck:walkaround` | pilot's pre-flight external aircraft inspection. Semantically precise vs `doctor` (which conflates medical diagnosis with structural check) |
| `/workshop:emit-agents-md` | `/flightdeck:emit-agents-md` | AGENTS.md is a cross-platform standard; the function name stays standard |

### Repo identity

- Rename `Yuelioi/workshop` → `Yuelioi/flightdeck` on GitHub.
- Plugin marketplace identifier updates accordingly.
- GitHub's automatic redirect covers historical links; CHANGELOG.md notes the rename explicitly.

### Skill module rename

- `skills/workshop-workflow/` → `skills/flightdeck-workflow/`
- SKILL.md frontmatter (`name:`, `description:`) updated.
- Internal cross-links in SKILL.md / folder-semantics.md / templates.md / exit-ritual.md all rewritten.

### Scaffold rename

- `scaffolds/full/workshop/` → `scaffolds/full/flightdeck/`
- `scaffolds/minimal/workshop/` → `scaffolds/minimal/flightdeck/`
- Inner files reflect the new folder structure (cockpit.md instead of board.md, etc.)

### AGENTS.md emission

`/flightdeck:emit-agents-md` outputs paths using new names (`flightdeck/cockpit.md`, `flightdeck/flight-plans/`, ...). Users with pre-existing AGENTS.md regenerated under workshop must re-emit after upgrade. No backward-compat shim — the user base doesn't justify it.

### Cross-platform manifests

- Claude Code manifest: rewritten for flightdeck. Status remains `tested`.
- Codex CLI / Cursor / Gemini CLI manifests: rewritten for flightdeck. Status remains `manifest in place, behavior untested` (same as v0.8). Community PR template ([.github/PULL_REQUEST_TEMPLATE/manifest-verification.md](../../.github/PULL_REQUEST_TEMPLATE/manifest-verification.md)) is rewritten to reference flightdeck.

## Release strategy

Single-shot to v1.0. No transitional v0.9.

- **v0.8.x — current**: continue dogfood week through 2026-06-02. Any dogfood findings that warrant protocol changes get folded into the v1.0 scope.
- **v0.9 — skipped.** v0.9 transitional was originally proposed as a migration-prep release, but with user base = 1 it earns no place.
- **v1.0 — flightdeck**: single commit (or tight commit series) that:
  1. Renames all folders / commands / skill modules / scaffolds.
  2. Splits the maintainer's own `workshop/board.md` into `flightdeck/cockpit.md` + `manifest.md` + `logbook.md`.
  3. Rewrites SKILL.md, folder-semantics.md, templates.md, exit-ritual.md, README.md, README.zh.md, AGENTS.md, CLAUDE.md (if present), CHANGELOG.md.
  4. Renames the GitHub repo.
  5. Updates plugin marketplace manifests across all 4 platforms.
  6. Writes [MIGRATION.md](../../MIGRATION.md) — a self-note documenting "what I did, in case I forget what I changed".

## Migration plan

For the maintainer (the only user). Step list lives in MIGRATION.md after the v1.0 release ships. The doc serves as memory aid, not a wide-audience migration guide.

For any future user landing on flightdeck after the rename: README documents the workshop-era predecessor and links to MIGRATION.md as historical context. Users coming from `Yuelioi/workshop` install commands hit GitHub's auto-redirect and end up reading the renamed README, which explains the change.

## Design warning — metaphor lock-in

Once renamed to flightdeck, every future concept added to the project will face the silent pressure of "is there an aviation word for this?". That pressure produces the cosplay outcome — reject it.

The metaphor stays:
- operational
- procedural
- reliability-focused
- professional

The metaphor does NOT become:
- aviation roleplay
- sci-fi theming
- meme interfaces
- gamified agent cosplay

Strength comes from high-reliability systems engineering, not aesthetics. If a future rename or new term is "cute but unclear" (e.g., `/stuck → /request-vector` from the original proposal), reject it.

Two folders (`specs/`, `sketches/`) intentionally keep neutral names because no aviation equivalent improves them. Mixing neutral and themed names is acceptable — *forcing* every term into the metaphor produces the cosplay outcome the warning forbids.

### Governing principle

> **Semantic clarity outranks thematic consistency.**

This sentence is load-bearing. When any future naming decision triggers a conflict between "fits the metaphor" and "reads correctly", clarity wins by default. The whole project is an exercise in reliability-oriented language design — language that obscures more than it reveals violates the project's first commitment.

## Open questions

1. **Dogfood findings integration**: dogfood week ends ~2026-06-02. Findings may indicate protocol-level fixes that should bundle into v1.0. Re-read this spec on 2026-06-02 with dogfood signals in hand; amend `Decisions` section if anything material surfaces.
2. **README.zh.md treatment**: Chinese README currently mirrors the English one. After rename, full translation parity or English-first with Chinese summary? Defer decision to v1.0 prep work.
3. **CHANGELOG voice**: the v1.0 entry will be unusually large. Consider whether to write it as one paragraph or section it into "renames / decomposition / repo / migration".
4. **`manifest.md` naming overload**: `manifest` is overloaded in software (package manifest, cargo manifest, deployment manifest), reducing semantic distinctiveness vs `kneeboard` or `cockpit`. The current definition is closer to "divergence tracker" or "open-state registry". Acceptable for v1.0 — flag for review if naming friction surfaces during dogfood under flightdeck.

## Authority

When sources disagree about a path:
- This spec wins until v1.0 ships.
- After v1.0 ships, this spec moves to `landed/specs/` and loses to current state per [authority order](../../skills/workshop-workflow/SKILL.md).
