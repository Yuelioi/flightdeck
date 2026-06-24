# Migration

This rewrite ships **no automatic migration machinery** — no schema, no version field,
no in-place upgrader, and no migrate/conform command. A deck from an older version is
not auto-upgraded. You migrate it once; two paths.

## In-place migration (keeps your structure)

No command does this — an AI session in the project (with the new plugin loaded) follows
these steps once. Everything is mechanical except the routing headers, which need a
judgement pass.

1. **Move folders.**
   - `specs/` (active) + `plans/` → `work/<effort>/` (one folder per effort, its design
     and plan together; a lightweight effort can be a single `work/<effort>.md`).
   - `checklists/` + `docs/` + `incidents/` + `references/` → `knowledge/<domain>/`,
     regrouped **by domain**, not by kind.
   - `specs/` (idea) → `~/.flightdeck/projects/<slug>/ideas/`.
   - `specs/` (done) + `archive/` → `~/.flightdeck/projects/<slug>/archive/`.
   - Delete the deck's kind-folder `INDEX.md` (specs/plans/checklists/docs/incidents/
     references). **Leave** an `INDEX.md` that belongs to an unrelated subsystem living
     inside the deck (e.g. a source or showcase tree) — it's not a routing index. Strip
     YAML frontmatter from the moved knowledge files.

   (`<slug>` = the project's absolute path with `/`, `\`, `:` replaced by `-` — see
   [protocol.md](skills/preflight/protocol.md) § Cold tier.)

2. **Add a routing header to each knowledge file** (the judgement pass). Replace the
   stripped frontmatter with a header ended by `---`:
   - title `# <title>` — a pitfall/incident → `# ⚠ <title>`; a checklist → `# <X> checklist`
   - `SUMMARY:` (one line) · `READ WHEN:` (← old `when_to_read`) · optional
     `RECHECK WHEN:` (← old `when_to_update`)

3. **Reshape `cockpit.md`** to the canonical skeleton: a `Focus:` line + `## In flight`
   (active `work/` efforts) + `## Next` + `## Open questions`. Drop the `Updated:` line,
   every AUTO region, and `## Staged`. `Pending Review` / `Hanging Tasks` fold into
   `## Open questions` prose.

4. **`rules.md`:** delete the recorded-config frontmatter (`version` / `runtime` /
   `agents_md`); keep the house rules. Also fix any `### Project conventions` text that
   names a now-removed structure (`INDEX`, `specs/`, kind-folders) — repoint it to the
   new shape (`knowledge/` routing headers, `work/`).

5. **Shared knowledge:** for each vendored `synced: true` file (`comments` / `commits` /
   `subagent-guide` / …), subscribe to its master path in `uses.md` (e.g.
   `knowledge/commits.md`) and delete the local copy. **If the local copy carries a
   project-specific addition** beyond the master's shared region (extra commit scopes,
   local conventions), fold that part into `rules.md` first — don't lose it.

6. **Commit** the reshaped deck, then run `/flightdeck:walkaround` to catch leftovers —
   missing routing headers, orphaned `work/`, cockpit-vs-reality drift.

> **Body cross-links go stale when files move.** `[[wikilink]]` / relative `[text](path)`
> references inside knowledge bodies that point at moved siblings will dangle. Routing
> greps headers — it never follows these — so they're not load-bearing; repoint the
> high-value ones, or accept the staleness and fix on next touch.

> **Extra root files are fine.** A deck may carry files beyond the skeleton (e.g. a custom
> `conventions.md`). The skeleton is a minimum, not a cap — keep them and fix any stale
> structure references inside, or fold their content into `rules.md`.

## Start fresh (simpler, loses structure)

Delete the old deck, run `/flightdeck:launch`, then hand-copy your old `cockpit.md`
content and the knowledge files you still want (give each a routing header).

---

If a future release changes the deck format, concrete version-to-version steps will be
recorded here.
