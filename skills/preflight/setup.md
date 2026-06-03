# Flightdeck first-time setup

Run by `preflight` Branch-0 when **no `flightdeck/cockpit.md`** exists. Creates the deck, then stops — the next `/preflight` takes the read path.

1. **git check** — does the deck root (cwd) contain `.git`? If **no**: tell the user "no git here — flightdeck still works, but staleness/history fall back to `landed/HISTORY.md`", and **offer `git init`? (y/N)**. Non-blocking either way.
2. **Confirm**: "Create a flightdeck deck here? (full layout + 3-file contract)" — wait for yes.
3. **Interview (2 Q)** — gather *before* creating: "Active focus — current main thread (5–15 words)?" and "First 'next session' item — one concrete action?"
4. **Create the deck — copy the scaffold verbatim + seed the cockpit.**
   - **Fast path** (preferred when a Python runtime is reachable — no House Rule needed, `rules.md` doesn't exist yet): run the bundled initializer against the current dir, e.g. `uv run <flightdeck-pkg>/scripts/flightdeck_init.py . --name <project> --user <user> --date <today> --focus "<answer 1>" --next "<answer 2>"`. It copies `scaffolds/full/flightdeck/` into `./flightdeck/` (every folder + each `INDEX.md` + the **commented** `rules.md` + `cockpit.md` + `landed/HISTORY.md`) and seeds the cockpit in one deterministic step. Being a verbatim copy it **cannot re-author or drop the `rules.md` comments** — which hand-copying does. Refuses if a deck already exists.
   - **Fallback** (no runtime): copy by hand from `../../scaffolds/full/flightdeck/` into `./flightdeck/` — **copy, do NOT re-author** (this is what preserves the `rules.md` comments) — then substitute today's date / `<user>` / the two interview answers into `cockpit.md` (`<ACTIVE_FOCUS …>` / `<FIRST_NEXT_ITEM …>`).
   - Either way: the scaffold `rules.md` `version` should equal `MIGRATION.md` `current` — bump it if the scaffold is behind.
5. **AGENTS.md** — ask "Generate `AGENTS.md` (cross-tool bridge from cockpit)? (Y/n)". If yes, run `/flightdeck:emit-agents-md`. (Opt-in; creating it now bootstraps it — matches the 3.0 emit-on-presence rule.)
6. **Then STOP** — the next `/preflight` takes the read path.
