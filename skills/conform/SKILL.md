---
name: conform
description: Conform a flightdeck deck to the current canonical schema — a script does the mechanical pass (delete non-schema frontmatter fields, stamp rules recorded-config, append missing cockpit/rules sections) and prints a worklist; then the AI reshapes cockpit.md/rules.md to the template and fills the missing semantic fields. Like gofmt for a deck, not a migration framework. Triggered by /flightdeck:conform.
---

# Flightdeck Conform — format a deck to the canonical shape

flightdeck's format evolves (cockpit field renames, recorded-config fields, retired toggles).
An **old deck does not follow along on its own**: a deck created before alpha.4 may still use
`**Last updated**` / `**Active focus**` labels, lack `## Key Context` / `## Pending Review`, and
carry a `rules.md` with no `runtime` / `agents_md`. This skill conforms it — adding what's missing,
deleting what's not in the schema. It is **a strict formatter, not an upgrade guide**: there is no
"old → new" migration table; the canonical template is the only source of truth.

Two passes: a deterministic **script pass** (the machine shapes frontmatter + section skeletons)
and a judgment **AI pass** (you reshape the two root files and fill semantic fields the script
cannot author). Mantra: **the script shapes, the AI fills meaning, `archive/` and stray dirs are left alone.**

## When to use

- A deck whose `cockpit.md` / `rules.md` use pre-alpha.4 labels or are missing canonical sections.
- After retiring a frontmatter field (e.g. `portable`) once its replacement is in place — the formatter
  deletes any field outside a kind's legal set, so **make sure the successor is live first**
  (`portable` → only after `synced` / the shared-knowledge master has taken over that file's
  distribution; the formatter does not judge ordering for you).
- Any time you want a deck snapped back to the current shape. `/flightdeck:walkaround` only *reports*
  field-structure drift (Audit 16); this skill is the *fix*.

## Irreversibility — dry-run first

The script deletes non-schema fields with **no registry, no history, no undo file**. A non-git deck has
no rollback. **Default to `--check` first**, read the planned changes, and only then apply. On a git
deck, confirm the working tree is clean so the apply is a reviewable diff.

## Pass 1 — the script (mechanical, deterministic)

Run the conform script — call form per the recorded `runtime` ([protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order)); e.g. with `runtime: uv`:

```
# dry-run: print planned changes + the AI worklist, write nothing (exit 1 if not conformant)
uv run <flightdeck-pkg>/scripts/flightdeck_conform.py <deck> --check

# apply: prune + stamp + append sections, then print the missing-required worklist
uv run <flightdeck-pkg>/scripts/flightdeck_conform.py <deck>
```

`--runtime <uv|python|node>` overrides the stamped runtime (default: probe `uv` > `python` > `node`).
Node twin: `node <flightdeck-pkg>/scripts/flightdeck_conform.js <deck> [--check]` (byte-identical).

What the script does, and **only** this:

- **Frontmatter delete** — across every in-scope file, drop any field not in that kind's legal set
  (`portable`, retired toggles, typos → gone; legal optionals like `note` / `supersedes` / `synced` → kept).
- **rules.md recorded-config stamp** — add `version: 3.0`, `runtime: <detected>`, `agents_md: off`
  only when absent; existing values are never overwritten.
- **cockpit.md / rules.md section skeletons** — **append-only**: add any missing canonical section with
  a `- (none)` placeholder (`## In Progress` gets the `<!-- AUTO:inprogress -->` markers). It never
  deletes or relabels a section — that is the AI pass.
- **Worklist** — print `<relpath>\t<missing-required-field>` for every required semantic field still
  absent, for the AI pass to author.

**Scope:** `cockpit.md`, `rules.md`, and non-archive `.md` under `specs/ plans/ incidents/ checklists/ docs/`.
**Excluded and untouched:** `archive/` (frozen history), `references/` (imported, hand-maintained —
decks vendor whole upstream repos there), and any stray folder.

## Pass 2 — the AI (judgment)

The script cannot invent meaning. After it runs, you:

1. **Reshape `cockpit.md` + `rules.md` to the canonical template** ([templates § cockpit.md](../preflight/templates.md#cockpitmd) / [§ rules.md](../preflight/templates.md#rulesmd)).
   Read each file fully and rewrite it to the template shape, **preserving values** — relabeling is
   rename-keep-value, not delete-and-refill:
   - `**Last updated**` → `Updated: <date> · <who> · Stage: <stage>` (infer `Stage` from context).
   - `**Active focus**` → `Focus: <label> → <link>`.
   - `**Pointers**` / a localized pointers label → `Pointers:`.
   - Delete any non-canonical section/field the script left in place (e.g. a hand-added `**Context**` block),
     folding its still-relevant content into the right canonical slot.
   - Drain the appended `- (none)` placeholders that you can now fill from the file's real state.
2. **Fill the worklist fields** — for each `<relpath>\t<field>` line, **read that one file** and author the
   missing required field (`when_to_read` / `applies_to` / `summary` / `status` / `last_updated`) from its
   content. Only the flagged files are read — not the whole deck.

After editing cockpit/rules, regenerate the AUTO regions if needed (`flightdeck_index <deck>`, call form
per the recorded `runtime`) so `## In Progress` and the INDEXes reflect the conformed frontmatter.

## Report

End with the unified banner ([protocol § Act-report-close loop](../preflight/protocol.md#act-report-close-loop)):

```
─── 🩹 conform ───
[Saved] script: <N fields dropped · M sections added · rules stamped>; AI: <K fields filled · cockpit/rules reshaped>
```

On a `--check`-only run (no apply), report the planned counts instead and state that nothing was written.

## Relationship to walkaround

`walkaround` is **audit-only** (it surfaces drift, never writes). This formatter is the **fix path** — an
independent action (script + AI), not a step embedded in walkaround. Audit 16 (cockpit field-structure
conformance) reports the drift; `/flightdeck:conform` resolves it in one pass.
