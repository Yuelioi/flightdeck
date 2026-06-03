# Flightdeck first-time setup

Run by `preflight` Branch-0 when **no `flightdeck/cockpit.md`** exists. Creates the deck with **zero prompts** — running `/flightdeck:preflight` in a deckless directory *is* the consent to create one — then stops. The next `/preflight` takes the read path.

**Do not inspect the repo** (no `ls`, no reading `package.json`, no `git ls-files`). The scaffold is fixed; nothing about it depends on the project's contents.

1. **Detect a Python runtime** — silently try `uv --version` (preferred) or `python --version`. This is the only probe; don't announce it.
2. **Create the deck — copy the scaffold verbatim.**
   - **Fast path** (a runtime is reachable): run the bundled initializer against the current dir, e.g. `uv run <flightdeck-pkg>/scripts/flightdeck_init.py . --user <user> --date <today>` — **no `--focus`/`--next`** (there is no interview). It copies `scaffolds/full/flightdeck/` into `./flightdeck/` (every folder + each `INDEX.md` + the **commented** `rules.md` + `cockpit.md`) and stamps name/date/user in one deterministic step. `Active focus` / `## 下一步` ship as `(set me)` placeholders. It also **silently removes `landed/HISTORY.md` when the deck root has `.git`** — that file is the no-git history substrate (`git log` is the history otherwise), so a git project never gets the dead file. Being a verbatim copy it **cannot re-author or drop the `rules.md` comments** — which hand-copying does. Refuses if a deck already exists.
   - **Fallback** (no runtime): copy by hand from `../../scaffolds/full/flightdeck/` into `./flightdeck/` — **copy, do NOT re-author** (this is what preserves the `rules.md` comments) — then substitute today's date / project name / `<user>` into `cockpit.md`, leaving the `<ACTIVE_FOCUS …>` / `<FIRST_NEXT_ITEM …>` placeholders as `(set me)`. **If the deck root has `.git`, delete the copied `landed/HISTORY.md`** (git log is the history); keep it only for a no-git deck.
   - Either way: the scaffold `rules.md` `version` should equal `MIGRATION.md` `current` — bump it if the scaffold is behind.
3. **STOP** — report one line (below) and hand off. The next `/preflight` takes the read path.

## Final report (one line + optional hints)

> ✈ Deck created at `flightdeck/` (full layout, version `<v>`). Fill `Active focus` / `## 下一步` in `cockpit.md` when you start — or just run `/flightdeck:preflight` again.
> Tune autonomy in `flightdeck/rules.md` → `### Autonomy overrides` (a commented catalog is there: auto-landing, auto-commit, no-git, run-scripts…). Defaults are safe — `landing` is manual; nothing archives or commits without you.
> Optional, anytime: `git init` (if you want history) · `/flightdeck:emit-agents-md` (cross-tool AGENTS.md bridge). Created it by mistake? Delete `flightdeck/`.

## Why zero prompts (3.0)

The git-init offer, the 2-question interview, and the AGENTS.md opt-in were all dropped to make first-run a **single deterministic copy** — the slow, chatty old flow was the complaint that drove this. git presence is simply *inferred* later on the read path (no prompt); the cockpit fields are placeholders the user fills when real work starts (or `landing` derives them); AGENTS.md stays opt-in via its own command.
