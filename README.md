<div align="center">

# ✈️ flightdeck

**An operational protocol for AI-assisted engineering sessions.**

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-tested-success?style=flat-square)](adapters/claude/README.md)
[![AGENTS.md](https://img.shields.io/badge/emits-AGENTS.md-blueviolet?style=flat-square)](https://agents.md)

🇨🇳 [中文 README](README.zh.md) · 🇬🇧 English

</div>

---

> Your AI assistant forgets everything between chats. **flightdeck** is a directory convention plus a skill that gives it operational continuity across sessions — so the next session knows what you were doing, why, and what to do next.

## TL;DR

```text
/plugin marketplace add Yuelioi/flightdeck
/plugin install flightdeck@flightdeck-marketplace
```

Run `/flightdeck:preflight` at the start of a session — the single entry point. In an existing project it reads `flightdeck/cockpit.md`, reconciles against `git status`, and reports where you left off. In a fresh one it bootstraps a deck from a short interview. Nothing loads on its own; you invoke it.

## What it is

A `flightdeck/` directory your AI reads and writes by convention:

```
flightdeck/
├── cockpit.md          # must-read entry — Active focus / Next session / Hanging tasks
├── rules.md            # project config — version + disabled_folders + house rules
├── INDEX.md            # global status summary across all folders
│
├── sketches/           # early ideas, scratchpad
├── specs/              # scoped design documents
├── plans/              # step-by-step implementation plans
├── incidents/          # lessons learned (root-cause, no "forgot")
├── checklists/         # repeatable procedures
├── charts/             # imported external material (RFCs, competitor code)
├── debriefs/           # external review feedback (raw + disposition)
└── landed/             # archive of completed work
```

### cockpit.md — the one must-read file

Read first every session, hard-capped at 80 lines:

```markdown
# Cockpit — payment-service

**Last updated**: 2026-05-28 by alice (shipped Stripe webhook refactor)
**Active focus**: stabilize Stripe webhook handler — failing edge cases in incidents/

## Next session

1. Reproduce the duplicate-event bug from incidents/stripe-idempotency.md (Case 3).
2. Decide: idempotency key in DB vs Redis.
3. Update plans/2026-05-26-stripe-hardening.md Phase 2 with the decision.

## Hanging tasks

- (none)
```

No 500-line context dump — anything historical is one folder deeper, read from `INDEX.md` on demand.

## Install

### Claude Code &nbsp;<sub>✅ tested</sub>

```text
/plugin marketplace add Yuelioi/flightdeck
/plugin install flightdeck@flightdeck-marketplace
```

Update: re-run `/plugin install`. Uninstall: `/plugin uninstall flightdeck`. No marketplace: `git clone` then `./install.sh` (or `.\install.ps1` on Windows).

### Other AI tools &nbsp;<sub>⚠️ manifests in place, untested</sub>

<details>
<summary><b>Codex CLI / Cursor / Gemini CLI</b></summary>

- **Codex CLI** — `/plugins` → search "flightdeck" → Install. See [adapters/codex/](adapters/codex/README.md).
- **Cursor** — `/add-plugin flightdeck` in Agent chat. See [adapters/cursor/](adapters/cursor/README.md).
- **Gemini CLI** — `gemini extensions install https://github.com/Yuelioi/flightdeck`. See [adapters/gemini/](adapters/gemini/README.md).

</details>

You don't scaffold the deck by hand — `/flightdeck:preflight` creates it on first run.

## Usage

**Session start** — run `/flightdeck:preflight`. It:

1. Reads `flightdeck/cockpit.md`.
2. Reconciles against `git status` (branch, uncommitted, stashes).
3. Reports the next item — say "go" to execute, or it surfaces a mismatch and asks.

On a brand-new project (no `cockpit.md`) it runs first-time setup instead: checks for git, creates the deck, a 2-question interview, asks about `AGENTS.md`, and offers a skippable guided tour.

**Session end** — run `/flightdeck:landing`. It classifies new knowledge (bug → `incidents/`, procedure → `checklists/`, one-off → discard), refreshes `cockpit.md`, and commits. The next session — even a different AI or developer — picks up exactly here.

### Commands

| Command | Purpose |
| --- | --- |
| `/flightdeck:preflight` | **The single entry point.** Creates the deck when absent; otherwise reconciles `cockpit.md` against git and reports the next item. |
| `/flightdeck:landing` | Session wrap — classify new knowledge, update cockpit, commit. |
| `/flightdeck:walkaround` | Integrity audit — protocol-drift detection. |
| `/flightdeck:emit-agents-md` | Regenerate `AGENTS.md` from `cockpit.md`. |

Artifact `status` advances **automatically** — you rarely type a command for it. By default the AI may self-invoke these rituals when it judges the moment right; nothing fires on session start, and there's no background process.

### Routing — what triggers what

| What's happening | AI reads |
| --- | --- |
| session start / "what were we doing?" | `cockpit.md` |
| "why did the migration break?" | `incidents/` |
| "how do I run the tests?" | `checklists/` |
| "let's design X" | `specs/` |
| "break this into tasks" | `plans/` |
| "here's review feedback" | `debriefs/` (with disposition) |

## Configuration

`flightdeck/rules.md` is the per-project control panel — mandatory (it carries the deck `version`):

```yaml
---
version: <release>
disabled_folders: []     # folders to treat as off — not suggested, not audited
---

## House rules

### Project conventions
# deck-local conventions, e.g. "specs in Chinese", "don't create sketches/"

### Autonomy overrides
# behavioral overrides; omit = full-auto defaults
```

Everything not pinned here is **inferred or defaulted**:

- **git** — inferred from a `.git` directory.
- **AGENTS.md** regeneration — inferred from an `AGENTS.md` file being present.
- **rituals** are self-invocable, **`status`** auto-advances, **`commit`** asks first (the one human checkpoint).

Override any of these with a one-line standard phrase under `### Autonomy overrides`:

- `commit without asking` — or `don't auto-commit; leave changes for me / CI`
- `landing: don't self-invoke; I run it manually`
- `this deck doesn't use git`

## Why it exists

Most "AI memory" systems fail by saving everything — the signal drowns in a junk drawer. flightdeck does the opposite: a **strict write gate** (only what changes future decisions), a **folder=kind + status lifecycle** (work advances, then archives to `landed/`), **INDEX-first reads** (token-cheap on large projects), and a **landing ritual** that classifies new knowledge at session end. It's plain markdown — diff it in review, grep it from the terminal, and it survives a model upgrade or a switch between AI tools.

> ✨ Semantic clarity outranks thematic consistency — the aviation metaphor is used only where it sharpens intent, never as a theme.

## Compatibility

| Tool | Status | Manifest |
| --- | --- | --- |
| Claude Code | ✅ tested | [`.claude-plugin/`](.claude-plugin/) |
| Codex CLI / App | ⚠️ untested | [`.codex-plugin/`](.codex-plugin/) |
| Cursor | ⚠️ untested | [`.cursor-plugin/`](.cursor-plugin/) |
| Gemini CLI | ⚠️ untested | [`gemini-extension.json`](gemini-extension.json) |

Skill content under [`skills/`](skills/) is **tool-agnostic markdown**; manifests are thin discovery pointers. "Untested" means the install works but no one has verified the AI follows the protocol end-to-end — **PRs with verification logs welcome**.

## FAQ

<details>
<summary><b>How is this different from just using AGENTS.md?</b></summary>

[AGENTS.md](https://agents.md) is the cross-tool standard for *static* project rules. flightdeck sits on top of it — `/flightdeck:emit-agents-md` writes a fenced block into `AGENTS.md` from `cockpit.md` — and adds what AGENTS.md doesn't: session-to-session continuity, a status lifecycle, a write gate against junk-drawer accumulation, and incident tracking. If you only need a static rules list, AGENTS.md alone is enough.

</details>

<details>
<summary><b>I have an older <code>flightdeck/</code> — how do I upgrade?</b></summary>

On entry, `/flightdeck:preflight` (and `walkaround`) read the deck `version` and offer a guided migration — never silent; you confirm before anything moves. See [MIGRATION.md](MIGRATION.md).

</details>

## Documentation

**Guides** — go deeper in [`docs/`](docs/): [Lifecycle & execution flow](docs/lifecycle.md) · [Architecture](docs/architecture.md) · [Design philosophy](docs/philosophy.md) · [How it compares](docs/comparison.md)

**Protocol reference** (canonical, AI-facing): [protocol.md](skills/preflight/protocol.md) · [folder semantics](skills/preflight/folder-semantics.md) · [templates](skills/preflight/templates.md) · [the landing ritual](skills/preflight/exit-ritual.md) · [MIGRATION.md](MIGRATION.md) · [CHANGELOG.md](CHANGELOG.md)

## Contributing

Skill changes follow a **RED-GREEN-REFACTOR** discipline — no edit without a failing test first ([TEST_PLAN.md](TEST_PLAN.md)). Highest-signal contributions: a transcript of an AI wriggling out of the protocol, or an end-to-end verification log for a Codex / Cursor / Gemini manifest ([template](.github/PULL_REQUEST_TEMPLATE/manifest-verification.md)).

## Roadmap

Optional folders (`briefing/`, `blackbox/`, `crew-handover/`, `experiments/`) · a "continuance" benchmark (hand an AI a mid-project deck, say "continue", measure recovery) · archive synthesis/compression · end-to-end verification of the untested adapters · an MCP server. Full history in [CHANGELOG.md](CHANGELOG.md).

## Acknowledgments

[AGENTS.md](https://agents.md) — wire format · [OpenSpec](https://github.com/openspec/openspec) — spec-evolution markers · [Cursor MDC](https://docs.cursor.com) — path-scoped frontmatter · [Letta Code](https://github.com/letta-ai/letta) — promotion-gate pattern · [superpowers](https://github.com/anthropic-experimental/superpowers) — protocol style · [Cline Memory Bank](https://docs.cline.bot) — the pattern that motivated the write gate.

## License

[MIT](LICENSE) © 月离 (Yuelioi)

---

<div align="center">

If flightdeck saved you a context window, [star the repo](https://github.com/Yuelioi/flightdeck/stargazers).

</div>
