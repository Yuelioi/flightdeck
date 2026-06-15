---
name: launch
description: Use when explicitly creating a flightdeck deck for the first time in a project that has none — copies the full-layout scaffold and seeds cockpit.md (zero prompts), then stops. Refuses if cockpit.md already exists. Triggered by /flightdeck:launch.
---

# Flightdeck Launch — first-time deck creation

The **one-time** command that brings a flightdeck deck into existence. Run `/flightdeck:launch` in a project that has **no `flightdeck/cockpit.md`**. It creates the deck with **zero prompts** — running it *is* the consent to create one — then stops. From then on, every working session starts with `/flightdeck:preflight` (which takes the read path).

`launch` is the only flightdeck command that scaffolds. `preflight` no longer creates a deck — in a deckless project it just points here and stops.

**You MUST NOT inspect the repo** (no `ls`, no reading `package.json`, no `git ls-files`). The scaffold is fixed; nothing about it depends on the project's contents.

## Refuse if a deck already exists

If `flightdeck/cockpit.md` already exists, this project already has a deck → **refuse** and redirect: "Deck already exists (`flightdeck/cockpit.md`). Run `/flightdeck:preflight` to take over." The bundled `flightdeck_init.py` enforces the same predicate (`(deck / "cockpit.md").exists()` → `FileExistsError`), so the fast path refuses automatically; the redirect target is the same `cockpit.md` test preflight uses, so there is no half-init dead-end.

## Run this

1. **Detect a Python runtime** — silently try `uv --version` (preferred) or `python --version`. This is the only probe; don't announce it.
2. **Create the deck — copy the scaffold verbatim.**
   - **Fast path** (a runtime is reachable): run the bundled initializer against the current dir, e.g. `uv run <flightdeck-pkg>/scripts/flightdeck_init.py . --user <user> --date <today>` — **no `--focus`/`--next`** (there is no interview). It copies `scaffolds/full/flightdeck/` into `./flightdeck/` (every folder + each `INDEX.md` + the **commented** `rules.md` + `cockpit.md`) and stamps name/date/user in one deterministic step. `Active focus` / `## Next` ship as `(set me)` placeholders. The scaffold ships **no history-log file and no `archive/`** — flightdeck keeps no separate landing log (`archive/` is created on demand at first land; archived files + `git log` are the record). Being a verbatim copy it **cannot re-author or drop the `rules.md` comments** — which hand-copying does. Refuses if `cockpit.md` already exists.
   - **Fallback** (no runtime): copy by hand from `../../scaffolds/full/flightdeck/` into `./flightdeck/` — **copy, do NOT re-author** (this is what preserves the `rules.md` comments) — then substitute today's date / project name / `<user>` into `cockpit.md`, leaving the `<ACTIVE_FOCUS …>` / `<FIRST_NEXT_ITEM …>` placeholders as `(set me)`. The scaffold carries no history-log file and no `archive/` — nothing to delete.
3. **STOP** — report one line (below) and hand off. The next `/flightdeck:preflight` takes the read path.

## Final report (one line + optional hints)

> 🛠️ Deck created at `flightdeck/` (full layout, version `<v>`). Fill `Active focus` / `## Next` in `cockpit.md` when you start — or just run `/flightdeck:preflight`.
> Tune behavior by telling the AI a persistent preference in plain language ("ask before committing", "this deck doesn't use git") — it appends a free-prose rule to `flightdeck/rules.md` → `### Rules`. There is no magic-string toggle catalog. Defaults are safe — local commit is reversible; push asks first.
> Optional, anytime: `git init` (if you want history) · `/flightdeck:emit-agents-md` (cross-tool AGENTS.md bridge). Created it by mistake? Delete `flightdeck/`.

## Why zero prompts (3.0)

The git-init offer, the 2-question interview, and the AGENTS.md opt-in were all dropped to make first-run a **single deterministic copy** — the slow, chatty old flow was the complaint that drove this. git presence is simply *inferred* later on the read path (no prompt); the cockpit fields are placeholders the user fills when real work starts (or `landing` derives them); AGENTS.md stays opt-in via its own command.
