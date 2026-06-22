<div align="center">

# ✈️ flightdeck

**An operational protocol for AI-assisted engineering sessions.**

[![Version: 3.0.0-alpha.5](https://img.shields.io/badge/version-3.0.0--alpha.5-orange?style=flat-square)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-tested-success?style=flat-square)](adapters/claude/README.md)
[![AGENTS.md](https://img.shields.io/badge/emits-AGENTS.md-blueviolet?style=flat-square)](https://agents.md)

🇨🇳 [中文 README](README.zh.md) · 🇬🇧 English

</div>

---

> [!WARNING]
> **`3.0.0-alpha.5` — pre-release for early testers.** 3.0 is a **breaking** release and the new format baseline: decks created by 2.x are **not** auto-migrated — start fresh with `/flightdeck:launch` and hand-copy what's still relevant from your old `cockpit.md`. Format and behavior may still change before the final 3.0.0; don't rely on it for production projects yet. Feedback is the whole point — [issues](https://github.com/Yuelioi/flightdeck/issues) welcome.

> Your AI assistant forgets everything between chats. **flightdeck** is a directory convention plus a skill that gives it operational continuity across sessions — so the next session knows what you were doing, why, and what to do next.

## ✨ 3.0 highlights

- **Auto-landing — real increments persist themselves.** When a turn produces something worth keeping, there's no wrap-up command to remember: new knowledge soft-lands (classified + indexed); a finished item triggers a full landing (archive + local commit) on its own. Every execution turn ends with a one-line soft-landing banner — `[Saved]` when something persisted, `[No change]` when nothing did (an honest "nothing to save, board current") — so the signal is always there. `/flightdeck:landing` remains as the explicit wrap-up.
- **See the banner, close the window — nothing is lost.** The soft-landing banner ends every execution turn with a "you can close now" line, signalling the recovery payload (cockpit + INDEX + persisted artifacts) is on disk. From there, killing the chat is safe: the next `/flightdeck:preflight` resumes from a true picture, not a stale one.

## TL;DR

```text
/plugin marketplace add Yuelioi/flightdeck
/plugin install flightdeck@flightdeck-marketplace
```

Run `/flightdeck:preflight` at the start of a session — the session-entry takeover. In an existing project it reads `flightdeck/cockpit.md`, glances at `git status`, and reports where you left off. In a fresh one (no `cockpit.md`) it points you to `/flightdeck:launch`, which bootstraps a deck after a quick doctor check (one `git init` prompt if there's no repo). Nothing loads on its own; you invoke it.

## What it is

A `flightdeck/` directory your AI reads and writes by convention:

```
flightdeck/
├── cockpit.md          # must-read entry — Active focus / Next / Hanging Tasks
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

## In Progress

<!-- AUTO:inprogress -->
- specs/2026-05-26-stripe-hardening.md — active
<!-- /AUTO -->

## Next

1. Reproduce the duplicate-event bug from incidents/stripe-idempotency.md (Case 3).
2. Decide: idempotency key in DB vs Redis.

## Hanging Tasks

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

On a brand-new project (no `cockpit.md`) preflight points you to `/flightdeck:launch`, which runs a quick **doctor check** (git repo + a script runtime) then copies the scaffold — a missing repo gets a single `git init? [y/N]` offer; no interview, no `AGENTS.md` questions. Fill `Active focus` / `## Next` in `cockpit.md` when you start; `/flightdeck:emit-agents-md` is optional, anytime.

**Session end** — when a turn produced a real increment, flightdeck lands it at end-of-turn on its own. State-only progress → a silent **checkpoint** (board stays true); new knowledge → a **soft-landing** that classifies it (bug → `incidents/`, procedure → `checklists/`, one-off → discard) and prints 「已保存」 — the visible signal it's safe to close; a finished item → a **full landing** (refresh `cockpit.md`, archive, local commit). A small turn with no increment lands nothing. Run `/flightdeck:landing` to force the full wrap-up explicitly. The next session — even a different AI or developer — picks up exactly here.

### Commands

| Command | Purpose |
| --- | --- |
| `/flightdeck:launch` | **First-time deck creation** — doctor-checks git + a runtime (one `git init` prompt if no repo), then copies the scaffold and seeds `cockpit.md`. Refuses if a deck already exists. |
| `/flightdeck:preflight` | **Session-entry takeover** — reads `cockpit.md`, glances at git, reports the next item. Deckless → points to `/flightdeck:launch`. |
| `/flightdeck:new` | Author a deck artifact (spec/plan/incident/checklist/reference/doc) — stamps frontmatter + naming, regenerates INDEX/cockpit. Use instead of hand-writing. |
| `/flightdeck:landing` | Session wrap — classify new knowledge, update cockpit, commit. |
| `/flightdeck:walkaround` | Integrity audit — protocol-drift detection. |
| `/flightdeck:conform` | Format an old deck to the current canonical shape — script prunes non-schema frontmatter + stamps rules + adds missing sections, then the AI reshapes `cockpit.md`/`rules.md` and fills semantic fields. Dry-run first (`--check`). |
| `/flightdeck:emit-agents-md` | Regenerate `AGENTS.md` from `cockpit.md`. |
| `/flightdeck:sync` | Refresh this deck's vendored shared-knowledge files against their master deck — the master owns each file's shared region; a content fingerprint detects drift and a mechanical splice replaces it (no AI merge), keeping the project-specific section. `promote <path>` lifts a new local file up to the master; `--fanout` pushes a master edit to every consumer. |

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

### Rules
# behavioral rules the AI maintains from your natural-language requests; omit = defaults
```

`version` is the only structured field. Everything else is **inferred, defaulted, or skill judgment**:

- **git** — inferred from a `.git` directory.
- **AGENTS.md** regeneration — inferred from an `AGENTS.md` file being present.
- **scripts** — inferred from a `uv`/`python` runtime being reachable (else the markdown fallback).
- **rituals** — all five self-invoke; **`status`** auto-advances idea→active→done but **never archives** (archiving is `landing`'s cross-reference-aware judgment); **`commit`** is local-auto, **push asks**.

To change a behavior, **just tell the AI a persistent preference in plain language** — "ask before committing", "this deck doesn't use git", "don't auto-start specs" — and it appends a free-prose rule under `### Rules` (noting source + date) and honors it above the default. There's no magic-string toggle catalog to memorize: the AI authors and reads its own rules.

## Shared knowledge across projects

Some procedures and reference docs aren't project-specific — a commit-message checklist, a comment-style guide — and you want one canonical copy across every deck you run. flightdeck handles this with **vendored shared-knowledge**: a checklist or doc lives in a **master deck** and is copied into each consuming deck, refreshed automatically on session entry (or on demand).

- **Master deck** — fixed at `~/.flightdeck`. Want it elsewhere? Make that path a symlink, or a directory junction on Windows (`mklink /J %USERPROFILE%\.flightdeck <target>`).
- **Vendored copy** — carries `synced: true` in its frontmatter and mirrors the master's relative path. A `<!-- flightdeck:project-specific -->` marker splits the file: everything above is the **shared region** (master-owned), everything below is your deck's **project section** (yours, never touched).
- **Single writer** — the master is the sole writer of the shared region; a consumer never edits it. Staleness is a content fingerprint over that region, so a sync is a mechanical text splice — the AI reads nothing and spends no tokens.
- **Auto-refresh on entry** — `/flightdeck:preflight` runs that same mechanical pull before it reads the deck, so a project self-heals to the latest shared knowledge on its next session. You rarely sync by hand.
- **`/flightdeck:sync`** — the explicit on-demand run: pulls any stale file's shared region from the master, keeping your project section and frontmatter verbatim.
- **`/flightdeck:sync promote <path>`** — lifts a *new* locally-authored file up to the master (the only consumer→master path; there is no shared-region back-flow), registering this deck as a consumer.
- **`/flightdeck:sync --fanout`** — optional: after editing a master file, push it to every registered consumer at once instead of letting each pick it up on its next entry.

Only `checklists/` and `docs/` participate. A deck with no vendored files never touches the master and works standalone.

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
