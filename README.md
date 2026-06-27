<div align="center">

# ✈️ flightdeck

**An operational protocol for AI-assisted engineering sessions.**

[![Version: 3.0.0-alpha.5](https://img.shields.io/badge/version-3.0.0--alpha.5-orange?style=flat-square)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-tested-success?style=flat-square)](adapters/claude/README.md)

🇨🇳 [中文 README](README.zh.md) · 🇬🇧 English

</div>

---

> [!WARNING]
> **Pre-release for early testers.** This is the AI-native rewrite of flightdeck — fewer moving parts, no schema, no scripts. Format and behavior may still change; don't rely on it for production projects yet. Decks created by older versions are **not** auto-migrated: start fresh with `/flightdeck:launch` and hand-copy what's still relevant from your old `cockpit.md`. Feedback is the whole point — [issues](https://github.com/Yuelioi/flightdeck/issues) welcome.

> Your AI assistant forgets everything between chats. **flightdeck** is a directory convention plus a skill that gives it operational continuity across sessions — so the next session knows what you were doing, why, and what to do next.

## ✨ Highlights

- **Zero-loss by default — the recovery payload commits itself.** At the end of any turn that did real work, flightdeck **persists** automatically: it scans for new knowledge worth keeping and writes it to `knowledge/`, rewrites the active topic `context.md` / `progress.md`, rewrites `cockpit.md`, and commits the repo. There's no wrap-up command to remember. Close the window whenever you like — the next `/flightdeck:preflight` resumes from a true picture, not a stale one.
- **No schema, no scripts, no INDEX.** The whole thing is plain markdown and two conventions: **location is state** (a folder in the project is live; moved out is done) and a one-line **routing header** on each knowledge file. Nothing to migrate, nothing to keep in sync, nothing that breaks on a model upgrade.

## TL;DR

```text
/plugin marketplace add Yuelioi/flightdeck
/plugin install flightdeck@flightdeck-marketplace
```

Run `/flightdeck:preflight` at the start of a session — the session-entry takeover. In an existing project it reads `flightdeck/cockpit.md`, the active topic `context.md`, glances at `git status`, and reports where you left off. In a fresh one (no `cockpit.md`) it points you to `/flightdeck:launch`, which seeds a deck. Nothing loads on its own; you invoke it.

## What it is

A `flightdeck/` directory your AI reads and writes by convention — a **warm tier** that lives in your repo and is committed every turn, plus a **cold tier** in a plain global dir for things that are done or parked:

```
your-project/
└── flightdeck/            # warm tier — git-tracked, committed every turn
    ├── cockpit.md         # project index (Focus / In flight / Next / Open questions)
    ├── briefing.md        # stable, human-owned — ## Conventions (house rules) + ## Subscriptions
    ├── work/              # topic packages: context.md + design.md + plan.md + progress.md
    └── knowledge/         # routed future-behavior knowledge, nested by domain

~/.flightdeck/             # cold tier — a plain global dir, NOT git
├── knowledge/             # genuinely cross-project knowledge (subscribed via briefing's ## Subscriptions)
└── projects/<slug>/       # one project's cold store: archive/ + ideas/
                           # <slug> = the project's abs path, separators → - (collision-proof)
```

There is no `INDEX.md`, no YAML frontmatter, and no status field. **Location is state**: a `work/` effort is active; moving it to `~/.flightdeck/projects/<name>/archive/` marks it done. Knowledge is resident — present means valid, deleted means dead. Nuanced states (blocked, waiting, reviewing) live in cockpit prose, not in a folder or a field.

### cockpit.md — the project index

Read first every session. It stays small on purpose — it points at the active topic package instead of carrying the topic notebook:

```markdown
# Cockpit — payment-service

Focus: stabilize the Stripe webhook handler — failing edge cases under knowledge/stripe/

## In flight

- work/webhook-idempotency/ — read `context.md` first; deciding DB vs Redis key

## Next

Continue `work/webhook-idempotency/context.md` → next action.

## Open questions

- Is the duplicate caused by Stripe retries or our own re-enqueue? (unverified)
```

No 500-line context dump. Topic detail lives in `work/<topic>/context.md` / `design.md` / `plan.md`; reusable future behavior lives in `knowledge/`, found on demand by walking the tree and grepping routing headers.

### work/&lt;topic&gt;/ — the topic package

Each active effort is a folder with stable entry files:

```text
work/<topic>/
  context.md    # topic recovery payload: state, next, blockers, key facts
  design.md     # why, approach, tradeoffs, settled decisions
  plan.md       # current main execution plan
  progress.md   # compressed progress summary, not a log
  plans/        # optional alternate or superseded plans
```

Preflight reads the active `context.md` after cockpit. Execution reads `plan.md`; design questions read `design.md`. `progress.md` is rewritten as a summary so the next session can continue without replaying the chat.

### The routing header — the one convention

Every knowledge file opens with a small header, ended by a `---`:

```markdown
# <title>          (# ⚠ <title> for a pitfall · # <X> checklist for a procedure)

SUMMARY: <one line — what this file holds>
READ WHEN: <when routing here is the right move>

---

<free-form body>
```

Routing reads only the header (cheap). The title glyph encodes the kind, so there's no `kind` field and no folder-per-kind — knowledge nests by **domain** instead, and the folder tree is the index.

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

You don't build the deck by hand — run `/flightdeck:launch` once and it writes the skeleton directly.

## Usage

**Session start** — run `/flightdeck:preflight`. It:

1. Loads the protocol and reads `flightdeck/cockpit.md` (plus `briefing.md`).
2. Scans the routing-header map (cheap one-liners), then loads bodies on demand — ranked by each header's `READ WHEN:`, so binding conventions stay foregrounded and reactive traps wait for their symptom.
3. Glances at `git status` — a passive one-line note only when something looks off, never a blocking prompt.
4. Reports the next item — say "go" to execute.

On a brand-new project (no `cockpit.md`) preflight points you to `/flightdeck:launch`, which seeds the skeleton after a quick check (one `git init` offer if there's no repo — the zero-loss guarantee needs git).

**Session end** — nothing to remember. When a turn produced a real increment, flightdeck **persists** on its own: scans what the turn produced for anything that passes the write gate and writes it to `knowledge/`, rewrites `cockpit.md` to reflect now, and makes one local commit. A pure-conversation turn that changed nothing commits nothing. The next session — even a different AI or developer — picks up exactly here.

### Commands

| Command | Purpose |
| --- | --- |
| `/flightdeck:preflight` | **Session-entry takeover** — loads the protocol, reads `briefing.md`, `cockpit.md`, and the active topic `context.md`, walks the tree for what's needed, reports the next item. Nothing auto-fires; not running it means flightdeck isn't engaged. |
| `/flightdeck:launch` | **First-time deck creation** — seeds the skeleton (`cockpit.md` + `briefing.md` + `work/` + `knowledge/`). One `git init` offer if there's no repo. Refuses if a deck already exists. |
| `/flightdeck:walkaround` | **Integrity audit and repair** — an on-demand sweep for drift the new form has no mechanism to self-correct (cockpit vs reality, malformed topic packages, orphaned work, duplicate traps, missing routing headers). Fixes mechanical issues and proposes lossy ones. |

**persist** is the fourth verb, but it's not a command — it runs automatically at the end of any execution turn (scan for knowledge, rewrite cockpit, commit). `commit` is **local-auto, push asks** (local commits are reversible; push is the gated checkpoint). Nothing fires on session start; there's no background process.

### Routing — what triggers what

| What's happening | AI reads |
| --- | --- |
| session start / "what were we doing?" | `cockpit.md` |
| an in-flight multi-step effort | `work/<topic>/context.md` first, then `plan.md` / `design.md` on demand |
| "why did the migration break?" | a `# ⚠` trap under `knowledge/<domain>/` |
| "how do I run the tests?" | a `# … checklist` under `knowledge/<domain>/` |

## Configuration

`flightdeck/briefing.md` is the per-project control panel — a single, stable, human-owned file read on entry. No frontmatter, no structured fields; two sections:

```markdown
## Conventions
deck-local conventions + behavioral rules the AI maintains from your natural-language
requests, e.g. "publishing surface is English", "ask before committing". Omit = defaults.

## Subscriptions
one ~/.flightdeck-relative path per line — shared knowledge this deck pulls in; empty = none
```

Everything is **inferred or skill judgment** — git from a `.git` directory, the rest from the protocol. To change a behavior, **just tell the AI a persistent preference in plain language** — "ask before committing", "don't auto-start work" — and it appends a free-prose rule under `## Conventions` (noting source + date) and honors it above the default. There's no magic-string toggle catalog to memorize.

## Shared knowledge across projects

Some procedures and reference docs aren't project-specific — a commit-message checklist, a comment-style guide — and you want one copy across every deck you run. flightdeck handles this with the **`## Subscriptions`** list in `briefing.md`:

- **Subscriptions** — one `~/.flightdeck`-relative path per line. A directory entry subscribes its whole subtree. On entry, preflight folds the subscribed global files into the routing tree alongside local `knowledge/`.
- **Cold tier as the shared store** — global knowledge lives in `~/.flightdeck/knowledge/`. Want it elsewhere? Make that path a symlink, or a directory junction on Windows (`mklink /J %USERPROFILE%\.flightdeck <target>`).
- **Local shadows global** — if a project has its own file at the same relative path, the local one wins entirely (replace, not merge) — deterministic, zero-maintenance.
- **Vendoring (opt-in)** — when you need the repo self-contained, snapshot a subscribed global file into the repo as a frozen copy and drop the subscription. The default is a live subscription, no copy.

A deck with an empty `## Subscriptions` never touches the global store and works standalone.

## Why it exists

Most "AI memory" systems fail by saving everything — the signal drowns in a junk drawer. flightdeck does the opposite: a **strict write gate** (only what changes a future decision, or that you'll look up again), **location-as-state** (work is live in the project, done when it's moved to the cold store), a one-line **routing header** so knowledge is found without a full-context dump, and a **zero-loss recovery payload** (`cockpit.md` + `briefing.md` + `work/` + `knowledge/`) committed every turn. It's plain markdown — diff it in review, grep it from the terminal, and it survives a model upgrade or a switch between AI tools.

> ✨ Semantic clarity outranks thematic consistency — the aviation metaphor is used only where it sharpens intent, never as a theme.

## How it compares

flightdeck is complementary to [AGENTS.md](https://agents.md) — keep an `AGENTS.md` for static rules and let flightdeck handle the session-to-session lifecycle that raw memory tools don't have:

| | flightdeck | [AGENTS.md](https://agents.md) | Cline Memory Bank | OpenSpec | Cursor MDC | Letta Code |
| --- | --- | --- | --- | --- | --- | --- |
| Static project rules | use AGENTS.md | ✅ native | — | — | ✅ | — |
| Session-to-session continuity | ✅ | — | ✅ | — | — | ✅ |
| Location-as-state lifecycle (work ↔ cold store) | ✅ | — | — | ✅ | — | — |
| Strict write gate (anti junk-drawer) | ✅ | — | — | — | — | — |
| Pitfall / lesson tracking (root-cause) | ✅ | — | — | — | — | — |
| Lazy routing (grep headers, no full dump) | ✅ | — | — | — | — | — |
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

[AGENTS.md](https://agents.md) is the cross-tool standard for *static* project rules — load every session, rarely changes. flightdeck is the *dynamic* layer on top: session-to-session continuity, a write gate against junk-drawer accumulation, and pitfall tracking. They compose — keep your `AGENTS.md` and add a `flightdeck/` deck. If you only need a static rules list, AGENTS.md alone is enough.

</details>

<details>
<summary><b>I have an older <code>flightdeck/</code> — how do I upgrade?</b></summary>

This rewrite ships **no** automatic migration machinery. To bring an older deck current, run `/flightdeck:walkaround` — it repairs the deck to the current shape (and migrates old-form structure: `INDEX.md`, frontmatter, kind-folders), preserving your content. Or start fresh with `/flightdeck:launch` and hand-copy the `cockpit.md` content and knowledge files you still want (give each a routing header).

</details>

## Documentation

**Protocol reference** (canonical, AI-facing): the micro-core in [skills/preflight/SKILL.md](skills/preflight/SKILL.md) loads on entry; the on-demand detail is in [concepts.md](skills/preflight/concepts.md) (definitions) + [operations.md](skills/preflight/operations.md) (procedures). History in [CHANGELOG.md](CHANGELOG.md).

## Contributing

Highest-signal contributions: a transcript of an AI drifting from the protocol (the failure mode the whole design guards against), or an end-to-end verification log for a Codex / Cursor / Gemini manifest ([template](.github/PULL_REQUEST_TEMPLATE/manifest-verification.md)).

## Roadmap

A "continuance" benchmark (hand an AI a mid-project deck, say "continue", measure recovery) · cold-store synthesis / compression · end-to-end verification of the untested adapters · an MCP server. Full history in [CHANGELOG.md](CHANGELOG.md).

## Acknowledgments

- [AGENTS.md](https://agents.md) — plain-markdown convention
- [superpowers](https://github.com/anthropic-experimental/superpowers) — protocol / skill style
- [Cline Memory Bank](https://docs.cline.bot) — the pattern that motivated the write gate

## License

[MIT](LICENSE) © 月离 (Yuelioi)

---

<div align="center">

If flightdeck saved you a context window, [star the repo](https://github.com/Yuelioi/flightdeck/stargazers).

</div>
