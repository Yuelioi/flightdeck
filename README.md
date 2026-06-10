<div align="center">

# ✈️ flightdeck

**An operational protocol for AI-assisted engineering sessions.**

[![Version: 3.0.0-alpha.1](https://img.shields.io/badge/version-3.0.0--alpha.1-orange?style=flat-square)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-tested-success?style=flat-square)](adapters/claude/README.md)
[![AGENTS.md](https://img.shields.io/badge/emits-AGENTS.md-blueviolet?style=flat-square)](https://agents.md)

🇨🇳 [中文 README](README.zh.md) · 🇬🇧 English

</div>

---

> [!WARNING]
> **`3.0.0-alpha.1` — pre-release for early testers.** 3.0 is a **breaking** release and the new format baseline: decks created by 2.x are **not** auto-migrated — start fresh with `/flightdeck:launch` and hand-copy what's still relevant from your old `cockpit.md`. Format and behavior may still change before the final 3.0.0; don't rely on it for production projects yet. Feedback is the whole point — [issues](https://github.com/Yuelioi/flightdeck/issues) welcome.

> Your AI assistant forgets everything between chats. **flightdeck** is a directory convention plus a skill that gives it operational continuity across sessions — so the next session knows what you were doing, why, and what to do next.

## ✨ 3.0 highlights

- **Auto-landing — sessions persist themselves.** No wrap-up command to remember: a state-only turn silently checkpoints the board; a turn that produced real knowledge soft-lands it (classified + indexed) and ends with a visible 「已保存 (saved)」 marker; a finished item triggers a full landing (archive + local commit) on its own. `/flightdeck:landing` remains as the explicit wrap-up.
- **Close the conversation anytime — nothing is lost.** The board (`cockpit.md` + the active plan) is kept equal to actual progress at every task boundary, so killing the chat mid-work is safe by design: the next `/flightdeck:preflight` resumes from a true picture, not a stale one.

## TL;DR

```text
/plugin marketplace add Yuelioi/flightdeck
/plugin install flightdeck@flightdeck-marketplace
```

Run `/flightdeck:preflight` at the start of a session — the session-entry takeover. In an existing project it reads `flightdeck/cockpit.md`, glances at `git status`, and reports where you left off. In a fresh one (no `cockpit.md`) it points you to `/flightdeck:launch`, which bootstraps a deck in one step — zero prompts. Nothing loads on its own; you invoke it.

## What it is

A `flightdeck/` directory your AI reads and writes by convention:

```
flightdeck/
├── cockpit.md          # must-read entry — Active focus / 下一步 / Hanging tasks
├── rules.md            # project config — version + free-prose house rules
│
├── specs/              # scoped design documents (status: idea = the to-start pool)
├── plans/              # step-by-step implementation plans
├── incidents/          # lessons learned (root-cause, no "forgot")
├── checklists/         # repeatable procedures
├── docs/               # authored standing technical reference
├── references/         # imported external material (RFCs, competitor code)
└── archive/            # completed work, moved out of the active area
```

Each knowledge folder carries its own auto-regenerated `INDEX.md` (file · status · one-line summary) — there is no root-level INDEX.

### cockpit.md — the one must-read file

Read first every session, hard-capped at 80 lines:

```markdown
# Cockpit — payment-service

**Last updated**: 2026-05-28 by alice (shipped Stripe webhook refactor)
**Active focus**: stabilize Stripe webhook handler — failing edge cases in incidents/

## 进行中

<!-- AUTO:inprogress -->
- specs/2026-05-26-stripe-hardening.md — active
<!-- /AUTO -->

## 下一步

1. Reproduce the duplicate-event bug from incidents/stripe-idempotency.md (Case 3).
2. Decide: idempotency key in DB vs Redis.

## Hanging tasks

- (none)
```

No 500-line context dump — anything historical is one folder deeper, read from the folder `INDEX.md` files on demand.

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

You don't scaffold the deck by hand — run `/flightdeck:launch` once and it creates the deck.

## Usage

**Session start** — run `/flightdeck:preflight`. It:

1. Reads `flightdeck/cockpit.md`.
2. Glances at `git status` (branch / version) — a passive one-line note only when something looks off, never a blocking prompt.
3. Reports the next item — say "go" to execute.

On a brand-new project (no `cockpit.md`) preflight points you to `/flightdeck:launch`, which copies the scaffold in one deterministic step — **zero prompts** (no git / interview / `AGENTS.md` questions). Fill `Active focus` / `## 下一步` in `cockpit.md` when you start; `git init` and `/flightdeck:emit-agents-md` are optional, anytime.

**Session end** — usually nothing: flightdeck lands itself at end-of-turn. State-only progress → a silent **checkpoint** (board stays true); new knowledge → a **soft-landing** that classifies it (bug → `incidents/`, procedure → `checklists/`, one-off → discard) and prints 「已保存」 so you know it's safe to close; a finished item → a **full landing** (refresh `cockpit.md`, archive, local commit). Run `/flightdeck:landing` to force the full wrap-up explicitly. The next session — even a different AI or developer — picks up exactly here.

### Commands

| Command | Purpose |
| --- | --- |
| `/flightdeck:launch` | **First-time deck creation** — copies the scaffold, seeds `cockpit.md` (zero prompts). Refuses if a deck already exists. |
| `/flightdeck:preflight` | **Session-entry takeover** — reads `cockpit.md`, glances at git, reports the next item. Deckless → points to `/flightdeck:launch`. |
| `/flightdeck:new` | Author a deck artifact (spec/plan/incident/checklist/reference/doc) — stamps frontmatter + naming, regenerates INDEX/cockpit. Use instead of hand-writing. |
| `/flightdeck:landing` | Session wrap — classify new knowledge, update cockpit, commit. |
| `/flightdeck:walkaround` | Integrity audit — protocol-drift detection. |
| `/flightdeck:emit-agents-md` | Regenerate `AGENTS.md` from `cockpit.md`. |

Artifact `status` advances **automatically** (idea→active→done). All five rituals (`preflight` / `landing` / `walkaround` / `emit-agents-md` / `status`) may self-invoke; `landing` decides archiving by judgment (it keeps a `done` artifact in place while active work still references it). `commit` is **local-auto, push asks** (local commits are reversible; push is the gated checkpoint). `/flightdeck:launch` is an explicit one-time command (it creates a deck), not a session ritual. Nothing fires on session start; there's no background process.

### Routing — what triggers what

| What's happening | AI reads |
| --- | --- |
| session start / "what were we doing?" | `cockpit.md` |
| "why did the migration break?" | `incidents/` |
| "how do I run the tests?" | `checklists/` |
| "let's design X" | `specs/` |
| "break this into tasks" | `plans/` |

## Configuration

`flightdeck/rules.md` is the per-project control panel — mandatory (it carries the deck `version`):

```yaml
---
version: <release>       # the only structured field
---

## House rules

### Project conventions
# deck-local conventions, e.g. "specs in Chinese", "don't use references/"

### Autonomy overrides
# behavioral overrides; omit = defaults (local commit auto, push asks; rituals self-invoke)
```

`version` is the only structured field. Everything else is **inferred, defaulted, or skill judgment**:

- **git** — inferred from a `.git` directory.
- **AGENTS.md** regeneration — inferred from an `AGENTS.md` file being present.
- **scripts** — inferred from a `uv`/`python` runtime being reachable (else the markdown fallback).
- **rituals** — all five self-invoke; **`status`** auto-advances idea→active→done but **never archives** (archiving is `landing`'s cross-reference-aware judgment); **`commit`** is local-auto, **push asks**.

Override any of these with a one-line standard phrase under `### Autonomy overrides`:

- `commit: ask` (confirm before each local commit) · `don't auto-commit; leave changes for me / CI`
- `status: don't auto start` — don't auto-flip idea→active
- `this deck doesn't use git` · `has AGENTS.md but don't auto-regen`

## Why it exists

Most "AI memory" systems fail by saving everything — the signal drowns in a junk drawer. flightdeck does the opposite: a **strict write gate** (only what changes future decisions), a **folder=kind + status lifecycle** (work advances, then archives to `archive/`), **INDEX-first reads** (token-cheap on large projects), and a **landing ritual** that classifies new knowledge at session end. It's plain markdown — diff it in review, grep it from the terminal, and it survives a model upgrade or a switch between AI tools.

> ✨ Semantic clarity outranks thematic consistency — the aviation metaphor is used only where it sharpens intent, never as a theme.

## How it compares

flightdeck sits **on top of** [AGENTS.md](https://agents.md), not against it, and adds the lifecycle + write discipline that raw memory tools don't have:

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

3.0 is the format baseline (version 0) — it ships **no** automatic migration machinery, and decks created by 2.x are not auto-upgraded. Recommended path: create a fresh deck with `/flightdeck:launch`, then hand-copy your old `cockpit.md` content and any still-relevant artifacts. Starting from the first release after 3.0 that changes the deck structure, concrete migration steps will be written into [MIGRATION.md](MIGRATION.md) as needed.

</details>

## Documentation

**Guides** — go deeper in [`docs/`](docs/): [Architecture](docs/architecture.md) · [Design philosophy](docs/philosophy.md)

**Protocol reference** (canonical, AI-facing): [protocol.md](skills/preflight/protocol.md) · [folder semantics](skills/preflight/folder-semantics.md) · [templates](skills/preflight/templates.md) · [the landing ritual](skills/preflight/exit-ritual.md) · [MIGRATION.md](MIGRATION.md) · [CHANGELOG.md](CHANGELOG.md)

## Contributing

Skill changes follow a **RED-GREEN-REFACTOR** discipline — no edit without a failing test first ([TEST_PLAN.md](TEST_PLAN.md)). Highest-signal contributions: a transcript of an AI wriggling out of the protocol, or an end-to-end verification log for a Codex / Cursor / Gemini manifest ([template](.github/PULL_REQUEST_TEMPLATE/manifest-verification.md)).

## Roadmap

Optional folders (`briefing/`, `blackbox/`, `crew-handover/`, `experiments/`) · a "continuance" benchmark (hand an AI a mid-project deck, say "continue", measure recovery) · archive synthesis/compression · end-to-end verification of the untested adapters · an MCP server. Full history in [CHANGELOG.md](CHANGELOG.md).

## Acknowledgments

- [AGENTS.md](https://agents.md) — wire format
- [OpenSpec](https://github.com/openspec/openspec) — spec-evolution markers
- [Cursor MDC](https://docs.cursor.com) — path-scoped frontmatter
- [Letta Code](https://github.com/letta-ai/letta) — promotion-gate pattern
- [superpowers](https://github.com/anthropic-experimental/superpowers) — protocol style
- [Cline Memory Bank](https://docs.cline.bot) — the pattern that motivated the write gate

## License

[MIT](LICENSE) © 月离 (Yuelioi)

---

<div align="center">

If flightdeck saved you a context window, [star the repo](https://github.com/Yuelioi/flightdeck/stargazers).

</div>
