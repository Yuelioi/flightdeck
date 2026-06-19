---
name: sync
description: Use when explicitly syncing this deck's vendored shared-knowledge files (a checklist/doc carrying `synced: true`) against their master deck — pulls upstream-changed bodies, preserves the reserved project-specific section + routing frontmatter, surfaces drift it can't auto-resolve, and `push <path>` reverse-adds a local file up to the master (promote / backflow). Triggered by `/flightdeck:sync`.
---

# Flightdeck Sync — vendored shared-knowledge refresh

The master deck is the single source of truth for shared knowledge; this ritual refreshes the vendored copies in a consumer deck against the master. **Newer wins** (compare `last_updated`, no hash). The AI does the merge; `flightdeck_index.py --sync-status` computes the facts.

## Master resolution

Fixed convention: the master root = `~/.flightdeck` (i.e. the script's `_resolve_master_root`, no argument). If it is a directory, use it; otherwise `master-missing` — each file gracefully skips and is reported (vendored files are self-contained and still usable). **Escape hatch**: to keep the master elsewhere, make `~/.flightdeck` a symlink pointing to it; on Windows without admin rights use a directory junction `mklink /J %USERPROFILE%\.flightdeck <target>` (`is_dir()` follows both).

## Modes (pull: A full / B first-vendor; push: C reverse)

### A. Re-sync everything (bare `/flightdeck:sync`)

1. Run `flightdeck_index.py <deck> --sync-status` → one `state<TAB>relpath` line per vendored file.
2. Handle by state:
   - `upstream-changed` → open the master source + project copy: **replace the shared body with the master's; preserve the project's `## Project-specific` section verbatim + the entire frontmatter; stamp `last_updated` to the master's.** Never touch `when_to_read` / `applies_to`.
   - `in-sync` → skip.
   - `locally-ahead` → skip + report one line "this project's copy is newer than the master, you may want to back-flow" (MVP: report only, no auto back-flow).
   - `dangling` → report (master source deleted), ask the user: delete the local copy / keep / re-point.
   - `master-missing` → report once, skip all (no master on this machine).
3. regen INDEX: `flightdeck_index.py <deck>`.
4. Emit the banner.

### B. First vendoring (`/flightdeck:sync <master-relpath>`)

1. Resolve the master root; read the master file at `<master-relpath>`.
2. Copy the whole file (frontmatter + body) into the consumer deck at the **same relpath** (master `checklists/commits.md` → deck `checklists/commits.md`).
3. Stamp `synced: true` into its frontmatter, and **strip the master's `consumers` key** (master-store-only, not for consumer copies).
4. Localize routing as needed (the project may change `when_to_read` / `applies_to`); project-specific additions go in a separate `## Project-specific` section.
5. regen INDEX.
6. Register the consumer: against the master, run `flightdeck_index.py <master-root> --register-consumer <this-deck-abspath> <master-relpath>` (idempotent; on failure warn only, do not roll back the landed vendor).

### C. Reverse: push back to the master (`/flightdeck:sync push <consumer-relpath>`)

Push a consumer-deck file up to the master (lifting the earlier "one-way, no back-flow" MVP boundary). Two cases:

- **promote (locally authored, no `synced`)**: written inside the project and now general enough → copy its **body** to the master at the **same relpath**, the master's `last_updated` takes that file's value; then **stamp `synced: true`** onto the local file (it becomes a vendored consumer from now on), and likewise run `--register-consumer <this-deck> <relpath>` against the master. If the master already has a file of the same name → **stop and ask** (that's a conflict / back-flow, not a promote).
- **back-flow (already vendored, `locally-ahead`)**: push the file's **shared body** up to the master source, stamp the master's `last_updated` to the consumer's → both in-sync.
- **The `## Project-specific` section is never pushed up** (project-private, not for the master); only the shared body is pushed.
- Wrap-up: regen both the **master** and this deck's INDEX.

### D. Fan-out: push master changes to all downstream (`/flightdeck:sync --fanout`)

From the master side, fan out changes to every registered consumer deck in one command:
1. `flightdeck_index.py <master-root> --list-consumers` → get the set of reachable consumer decks (empty → no-op, report "registry is empty").
2. Iterate **serially**, running the normal pull (§A) on each downstream deck: `--sync-status` computes that deck's `upstream-changed`, replace the body, preserve `## Project-specific` verbatim, leave frontmatter untouched. Pass each deck path as an explicit argument; do not change cwd.
3. **Failure isolation**: a single deck's failure (permissions / lock / corruption / missing directory) is recorded once; continue with the rest.
4. (Optional) run `--prune-consumers` to clear decks confirmed gone.

`--fanout` is this skill's orchestration, **not a script flag**; the script provides only the three primitives register/list/prune.

## The `## Project-specific` convention

A vendored file's project-specific additions go under a reserved heading section (`## Project-specific`, or this deck's-language equivalent). sync **never overwrites** anything under that section. **Above** it (the shared body) is owned by the master and refreshed on `upstream-changed`.

## Don't do

- Don't touch files without `synced: true` (locally authored).
- Don't overwrite frontmatter, and don't overwrite the `## Project-specific` section.
- `locally-ahead` does **not** auto back-flow — back-flow goes through an explicit `/flightdeck:sync push` (to avoid pushing local experiments up to the master).
- promote / back-flow both **push only the shared body, never the `## Project-specific` section** (project-private).
- A missing master is not a hard failure — graceful no-op.

## Report

Unified banner at the end (prose first, then the banner, one per turn):

```
─── 🔄 sync ───
[Synced]  N pulled · M in-sync · K locally-ahead · D dangling
[Master]  <resolved master root>   (or "master-missing — ~/.flightdeck absent / not a directory, skipped")
```

(In `--fanout` mode, additionally one line per deck `<deck>: pulled N / in-sync / skipped / error <reason>` + a total.)
