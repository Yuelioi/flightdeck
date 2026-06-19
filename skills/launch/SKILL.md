---
name: launch
description: Use when explicitly creating a flightdeck deck for the first time in a project that has none — copies the full-layout scaffold and seeds cockpit.md (zero prompts), then stops. Refuses if cockpit.md already exists. Triggered by /flightdeck:launch.
---

# Flightdeck Launch — first-time deck creation

The **one-time** command that brings a flightdeck deck into existence. Run `/flightdeck:launch` in a project that has **no `flightdeck/cockpit.md`**. It creates the deck with **zero prompts** — running it *is* the consent to create one — then stops. From then on, every working session starts with `/flightdeck:preflight` (which takes the read path).

`launch` is the only flightdeck command that scaffolds. `preflight` no longer creates a deck — in a deckless project it just points here and stops.

**Probe only git-existence + a script runtime — never the project's content.** The only two things launch inspects are (1) whether a git repo exists and (2) which script runtime is available (`uv` > `python` > `node`). It MUST NOT read `package.json`, run `git ls-files`, open source files, or learn anything about *what* the project is — the scaffold is fixed and depends on none of it.

## Refuse if a deck already exists

If `flightdeck/cockpit.md` already exists, this project already has a deck → **refuse** and redirect: "Deck already exists (`flightdeck/cockpit.md`). Run `/flightdeck:preflight` to take over." The bundled `flightdeck_init.py` enforces the same predicate (`(deck / "cockpit.md").exists()` → `FileExistsError`), so the initializer refuses automatically; the redirect target is the same `cockpit.md` test preflight uses, so there is no half-init dead-end.

## Run this

1. **Probe git + a script runtime (the only inspection) — refuse hard if either is missing.**
   - **git** — is there a git repo (an ancestor `.git`)? If **not**, refuse and STOP: `⚠ flightdeck requires git — run \`git init\`, then re-run launch.`
   - **runtime** — silently try `uv --version` (preferred) → `python --version` → `node --version`, first hit wins. If **none** is found, refuse and STOP: `⚠ flightdeck needs a script runtime — install uv (recommended), python, or node, then re-run launch.`
   Don't announce the probes; only the refusals surface.
2. **Create the deck — run the initializer (verbatim scaffold copy).** Call form per the detected runtime ([protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order)): `uv run <flightdeck-pkg>/scripts/flightdeck_init.py . --user <user> --date <today>` (uv) / `python …/flightdeck_init.py …` / `node …/flightdeck_init.js …` — **no `--focus`/`--next`** (there is no interview). It copies `scaffolds/full/flightdeck/` into `./flightdeck/` (every folder + each `INDEX.md` + the **commented** `rules.md` + `cockpit.md`) and stamps name/date/user in one deterministic step. `Focus` / `## Next` ship as `(set me)` placeholders. The scaffold ships **no history-log file and no `archive/`** — flightdeck keeps no separate landing log (`archive/` is created on demand at first land; archived files + `git log` are the record). Being a verbatim copy it **cannot re-author or drop the `rules.md` comments** — which hand-copying does. Refuses if `cockpit.md` already exists.
3. **Stamp the runtime into `rules.md` frontmatter.** The scaffold ships `agents_md: off` but **no `runtime`** (it can't know which runtime you have). After init, write `runtime: <detected>` (`uv` | `python` | `node`) into the `rules.md` frontmatter — a single field write done by launch directly (the initializer does not stamp it). This is the recorded-config field every later ritual dispatches on ([protocol § Runtime dispatch](../preflight/protocol.md#rule-resolution-order)).
4. **STOP** — report one line (below, including the recorded runtime + that it can be changed by editing `rules.md` `runtime:`) and hand off. The next `/flightdeck:preflight` takes the read path.

## Final report (one line + optional hints)

> 🛠️ Deck created at `flightdeck/` (full layout, version `<v>`). Fill `Focus` / `## Next` in `cockpit.md` when you start — or just run `/flightdeck:preflight`.
> Tune behavior by telling the AI a persistent preference in plain language ("ask before committing", "don't auto-commit") — it appends a free-prose rule to `flightdeck/rules.md` → `### Rules`. There is no magic-string toggle catalog. Defaults are safe — local commit is reversible; push asks first.
> Optional, anytime: `/flightdeck:emit-agents-md` (cross-tool AGENTS.md bridge). Created it by mistake? Delete `flightdeck/`.

## Why zero prompts (3.0)

The git-init *offer*, the 2-question interview, and the AGENTS.md opt-in were all dropped to make first-run a **single deterministic copy** — the slow, chatty old flow was the complaint that drove this. git is now a hard **precondition** checked at launch (refuse if absent — no interactive offer, just `git init` then re-run), not something inferred later; the cockpit fields are placeholders the user fills when real work starts (or `landing` derives them); AGENTS.md stays opt-in via its own command.
