---
name: sync
description: Use when explicitly syncing this deck's vendored shared-knowledge files (a checklist/doc carrying `synced: true`) against their master deck — a mechanical, zero-AI text splice replaces each stale file's master-owned shared region while preserving the consumer-owned project section + routing frontmatter, surfaces drift it can't resolve, and `promote <path>` lifts a locally authored file up to the master. Triggered by `/flightdeck:sync`.
---

# Flightdeck Sync — vendored shared-knowledge refresh

The master deck is the single source of truth for the **shared region** of every vendored file; this ritual refreshes the vendored copies in a consumer deck against the master. The model is **section-single-writer + mechanical pull**: a boundary marker splits each file into a master-owned shared region and a consumer-owned project section, staleness is a content fingerprint over the shared region, and the pull is a script-side text splice — **zero AI tokens**. `flightdeck_index.py --sync-status` computes the facts; `--sync-pull` applies the splice.

## The boundary marker

Each vendored file may carry the literal marker line:

```
<!-- flightdeck:project-specific -->
```

- **Above the marker** (frontmatter-stripped body) = the **shared region**, owned by the master, replaced wholesale on every pull.
- **The marker and everything below it** = the **project section**, owned by the consumer, **never pulled and never pushed**.
- **Frontmatter** (routing: `when_to_read` / `applies_to`, plus `synced: true`) stays consumer-local and is never overwritten.
- **No marker** → the whole body is the shared region (a pure-shared file); the master's own files carry no marker.

Staleness ignores frontmatter, per-line trailing whitespace, and trailing blank lines: only the normalized shared region is fingerprinted.

## Master resolution

Fixed convention: the master root = `~/.flightdeck` (the script's `_resolve_master_root`, no argument). If it is a directory, use it; otherwise `master-missing` — each file gracefully skips and is reported (vendored files are self-contained and still usable). **Escape hatch**: to keep the master elsewhere, make `~/.flightdeck` a symlink pointing to it; on Windows without admin rights use a directory junction `mklink /J %USERPROFILE%\.flightdeck <target>` (`is_dir()` follows both).

## Modes

Call form per the deck's recorded `runtime` (e.g. `uv run scripts/flightdeck_index.py <deck> …`).

### A. Pull / re-sync (bare `/flightdeck:sync`)

1. Run `flightdeck_index.py <deck> --sync-pull` → it applies the mechanical splice to every `stale` file, printing `pulled<TAB>relpath` per file: the shared region is replaced with the master's body, while frontmatter + marker + project section are kept verbatim. **No AI merge.**
2. States (from `--sync-status`):
   - `stale` → pulled (shared region replaced).
   - `in-sync` → skipped (fingerprint already matches).
   - `dangling` → the master source is gone; not pulled. Report and ask the user: delete the local copy / keep / re-point.
   - `master-missing` → `~/.flightdeck` absent; report once, no-op.
3. **Irreversibility** (non-git deck): run `--sync-pull --check` first (prints `would-pull<TAB>relpath`, writes nothing, exit 1 if any stale), review, then apply. A git deck's pull is reversible via git, so apply directly.
4. regen INDEX: `flightdeck_index.py <deck>`.
5. Emit the banner.

### B. First vendoring (`/flightdeck:sync <master-relpath>`)

1. Resolve the master root; read the master file at `<master-relpath>`.
2. Copy the whole file (frontmatter + body) into the consumer deck at the **same relpath** (master `checklists/commits.md` → deck `checklists/commits.md`).
3. Stamp `synced: true` into its frontmatter, and **strip the master's `consumers` key** (master-store-only, not for consumer copies).
4. Localize routing as needed (the project may change `when_to_read` / `applies_to`); any project-specific additions go below a `<!-- flightdeck:project-specific -->` marker.
5. regen INDEX.
6. Register the consumer: against the master, run `flightdeck_index.py <master-root> --register-consumer <this-deck-abspath> <master-relpath>` (idempotent; on failure warn only, do not roll back the landed vendor).

### C. Promote (`/flightdeck:sync promote <consumer-relpath>`)

Lift a **locally authored** file (no `synced`) up to the master once it has become general enough to share — the AI judges the generality (the only AI step in sync).
1. Confirm the file is genuinely project-agnostic.
2. Copy its **body** (the shared region, above any marker) to the master at the **same relpath**; the master's `last_updated` takes that file's value.
3. Stamp `synced: true` onto the local file (it becomes a vendored consumer from now on) and run `--register-consumer <this-deck> <relpath>` against the master.
4. If the master already has a file of that relpath → **stop and ask** (that's a conflict, not a promote).
5. regen both the **master** and this deck's INDEX.

There is **no back-flow**: the shared region is master-authoritative, so a consumer never pushes shared edits up. Local edits to a shared region are simply overwritten on the next pull — keep anything project-local below the marker.

### D. Fan-out (`/flightdeck:sync --fanout`)

Push master changes to every registered consumer in one command — a pure-script loop:
1. `flightdeck_index.py <master-root> --list-consumers` → the set of reachable consumer decks (empty → no-op, report "registry is empty").
2. For each, run `flightdeck_index.py <deck> --sync-pull` (mechanical splice; preserves that deck's project section + frontmatter). Pass each deck path as an explicit argument; do not change cwd.
3. **Failure isolation**: a single deck's failure (permissions / lock / corruption / missing directory) is recorded once; continue with the rest.
4. (Optional) run `--prune-consumers` to clear decks confirmed gone.

`--fanout` is this skill's orchestration over the script primitives (`--sync-pull` + register/list/prune), **not a script flag**.

## Don't do

- Don't touch files without `synced: true` (locally authored — unless you are promoting one).
- Don't overwrite frontmatter, and don't touch anything at or below the `<!-- flightdeck:project-specific -->` marker (project-private).
- Don't hand-merge a shared region — the pull is a mechanical splice. If a consumer's shared region drifted, the pull overwrites it (master is authority); move anything worth keeping below the marker first.
- There is no `locally-ahead` / back-flow — only `promote` lifts a (new) file up, and only its shared body.
- A missing master is not a hard failure — graceful no-op.

## Report

Unified banner at the end (prose first, then the banner, one per turn):

```
─── 🔄 sync ───
[Synced]  N pulled · M in-sync · D dangling
[Master]  <resolved master root>   (or "master-missing — ~/.flightdeck absent / not a directory, skipped")
```

(In `--fanout` mode, additionally one line per deck `<deck>: pulled N / in-sync / skipped / error <reason>` + a total.)
