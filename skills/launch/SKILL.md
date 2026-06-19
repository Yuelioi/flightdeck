---
name: launch
description: Use when explicitly creating a flightdeck deck for the first time in a project that has none — runs a doctor check (git + a script runtime), offers to `git init` once if there's no repo, then copies the full-layout scaffold and seeds cockpit.md. Refuses if cockpit.md already exists. Triggered by /flightdeck:launch.
---

# Flightdeck Launch — first-time deck creation

The **one-time** command that brings a flightdeck deck into existence. Run `/flightdeck:launch` in a project that has **no `flightdeck/cockpit.md`**. It runs a short **doctor check** (git repo + a script runtime), offers a single `git init` if there's no repo, then copies the scaffold and stops — running it *is* the consent to create a deck. From then on, every working session starts with `/flightdeck:preflight` (which takes the read path).

`launch` is the only flightdeck command that scaffolds. `preflight` no longer creates a deck — in a deckless project it just points here and stops.

**The doctor probes only git-existence + a script runtime — never the project's content.** The only two things launch inspects are (1) whether a git repo exists and (2) which script runtime is available (`uv` > `python` > `node`). It MUST NOT read `package.json`, run `git ls-files`, open source files, or learn anything about *what* the project is — the scaffold is fixed and depends on none of it.

## Refuse if a deck already exists

If `flightdeck/cockpit.md` already exists, this project already has a deck → **refuse** and redirect: "Deck already exists (`flightdeck/cockpit.md`). Run `/flightdeck:preflight` to take over." The bundled `flightdeck_init.py` enforces the same predicate (`(deck / "cockpit.md").exists()` → `FileExistsError`), so the initializer refuses automatically; the redirect target is the same `cockpit.md` test preflight uses, so there is no half-init dead-end.

## Run this

1. **Doctor check — probe git + a script runtime, print a `🩺 flightdeck doctor` block (one line per check), then branch.** This is the only inspection.
   - **git** — `✓ repo detected` (an ancestor `.git` exists) · `✗ no repo here` (git installed, but no repo) · `✗ git not installed` (no `git` binary).
   - **runtime** — try `uv --version` (preferred) → `python --version` → `node --version`, first hit wins: `✓ <uv|python|node>  (used for all script calls)` · `✗ none found`.

   Branch on the result:
   - **all green** → continue to step 2.
   - **`✗ no repo here`** (git installed, no repo) → ask once: `Run \`git init\` now and continue? [y/N]`.
     - **y** → run `git init` in the project root, then continue to step 2.
     - **N / anything else** → STOP, no deck: `Skipped — flightdeck requires git. Run \`git init\` yourself, then re-run launch.`
   - **`✗ git not installed`** → STOP (nothing to offer — can't init without the binary): `Install git, then re-run launch.`
   - **`✗ none found`** (no runtime) → STOP (can't auto-install; non-interactive): `Install uv (recommended), python, or node, then re-run launch.`
   - **both git-repo and runtime missing** → list both lines, then STOP — the runtime can't be auto-fixed, so the `git init` offer does **not** fire.
2. **Create the deck — run the initializer (verbatim scaffold copy).** Call form per the detected runtime ([protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order)): `uv run <flightdeck-pkg>/scripts/flightdeck_init.py . --user <user> --date <today>` (uv) / `python …/flightdeck_init.py …` / `node …/flightdeck_init.js …` — **no `--focus`/`--next`** (there is no interview). It copies `scaffolds/full/flightdeck/` into `./flightdeck/` (every folder + each `INDEX.md` + the **commented** `rules.md` + `cockpit.md`) and stamps name/date/user in one deterministic step. `Focus` / `## Next` ship as `(set me)` placeholders. The scaffold ships **no history-log file and no `archive/`** — flightdeck keeps no separate landing log (`archive/` is created on demand at first land; archived files + `git log` are the record). Being a verbatim copy it **cannot re-author or drop the `rules.md` comments** — which hand-copying does. Refuses if `cockpit.md` already exists.
3. **Stamp the runtime into `rules.md` frontmatter.** The scaffold ships `agents_md: off` but **no `runtime`** (it can't know which runtime you have). After init, write `runtime: <detected>` (`uv` | `python` | `node`) into the `rules.md` frontmatter — a single field write done by launch directly (the initializer does not stamp it). This is the recorded-config field every later ritual dispatches on ([protocol § Runtime dispatch](../preflight/protocol.md#rule-resolution-order)).
4. **STOP** — report the deck-created result + the recorded settings (below), then hand off. The next `/flightdeck:preflight` takes the read path.

## Final report (deck-created result + recorded settings)

> ✓ all checks pass — creating deck…
> 🛠️ Deck created at `flightdeck/` (full layout, version `<v>`).
> &nbsp;&nbsp;&nbsp;`runtime: <uv|python|node>` · `agents_md: off` — recorded in `rules.md`; change anytime by editing the frontmatter or just telling me.
> &nbsp;&nbsp;&nbsp;Fill `Focus` / `## Next` in `cockpit.md` when you start — or just run `/flightdeck:preflight`.
> Tune behavior in plain language ("ask before committing", "don't auto-commit") — I append a free-prose rule to `rules.md` → `### Rules`. There is no magic-string toggle catalog. Defaults are safe — local commit is reversible; push asks first.
> Optional, anytime: `/flightdeck:emit-agents-md` (cross-tool AGENTS.md bridge). Created it by mistake? Delete `flightdeck/`.

## Why minimal prompts (3.0)

The 2-question interview and the AGENTS.md opt-in stay dropped — first-run is still near-silent, not the slow chatty old flow. The **one** prompt is git: an absent repo gets a single `git init now? [y/N]` offer rather than a hard refuse, because running launch is already consent to create a deck and a deck **needs** git — so offering to init it is the least-friction path, not a return to the interview. `git not installed` and `no runtime` stay hard stops: there is nothing to offer (you must install first). The cockpit fields are placeholders the user fills when real work starts (or `landing` derives them); AGENTS.md stays opt-in via its own command.
