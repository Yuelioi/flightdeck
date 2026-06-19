---
name: emit-agents-md
description: Use when explicitly invoking the flightdeck AGENTS.md emitter — regenerates `AGENTS.md` at repo root from `flightdeck/cockpit.md` between fenced markers, preserving any hand-authored content outside the markers. Triggered by `/flightdeck:emit-agents-md`.
---

# Flightdeck AGENTS.md Emitter

User-triggered regeneration of `AGENTS.md` at repo root from the current state of `flightdeck/cockpit.md`. Use after `cockpit.md` changes (e.g., at landing) so non-Claude AI tools (Codex CLI, Copilot, Cursor, Windsurf, Continue, Cody, etc.) reading `AGENTS.md` see fresh project state.

## Why this exists

*(Background rationale — do not copy any of this section into AGENTS.md.)*

AGENTS.md is the cross-tool standard for project-level AI instructions, stewarded by the Agentic AI Foundation under the Linux Foundation; ~60k+ repos adopted by mid-2026 with measurable 28.6% runtime / 16.6% token wins. Flightdeck tracks the same information (current focus, next actions, hanging tasks) in `flightdeck/cockpit.md`. The emitter is the bridge: flightdeck authors maintain this file, and AI tools that don't speak flightdeck natively read the auto-regenerated `AGENTS.md`.

## Run this checklist

### Step 0: Apply `flightdeck/rules.md` toggles

This is the **explicit** emitter — it **always** creates/regenerates `AGENTS.md` (the bootstrap path; the "auto-regen only if `AGENTS.md` already exists" rule applies to *landing*'s call, not to this command). Under no-git, still emit (AGENTS.md is not git-dependent) but skip the working-tree-clean warning in "Don't do". A deck `### Rules` entry that opts out of auto-regen only suppresses the *automatic* landing-time regen — never this explicit command.

### Step 1: Read `flightdeck/cockpit.md`

Use Read on `flightdeck/cockpit.md`. Extract these fields (content copied as-is — the only transformation is the relative-link prefixing applied per-block in Step 3):

- The `Focus:` line value (one coarse label + a spec/plan link).
- All bullet items inside the `## In Progress` AUTO region (between `<!-- AUTO:inprogress -->` and `<!-- /AUTO -->`). This is the machine-derived active set — copy the rows verbatim; do not re-derive or reorder. Empty region → no items.
- The `## Next` body — the single next concrete action (free prose, usually one line; may itself contain a markdown link).
- All bullet items under `## Hanging Tasks` whose content is not literally `(none)`.

Extract only these fields; ignore all other cockpit sections.

### Step 2: Read current `AGENTS.md` at repo root (if present)

Use Read on `AGENTS.md` at the project root.

- **File exists with flightdeck markers** (`<!-- BEGIN: flightdeck -->` and `<!-- END: flightdeck -->`): note the content BEFORE the BEGIN marker and AFTER the END marker — both blocks of hand-authored prose MUST be preserved verbatim.
- **File exists without flightdeck markers**: the entire file is hand-authored. You will add the flightdeck block at the top (above all existing content) and leave the rest untouched.
- **File does not exist**: you will create it with the flightdeck block + a footer comment inviting hand-authored additions below.

### Step 3: Construct the new flightdeck block

The block to insert between markers (or as the whole new file body if AGENTS.md was missing):

```
<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

<Focus value, verbatim from cockpit.md>

## In Progress

<Bullet list copied from cockpit.md `## In Progress` AUTO region, verbatim.
 Else (empty region): single line "None.">

## Next

<The `## Next` body copied from cockpit.md, verbatim.
 Else (empty / placeholder): single line "None.">

## Hanging Tasks

<If cockpit has hanging tasks: bullet list copied verbatim.
 Else: single line "None.">

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

To author a new deck artifact (spec / plan / incident / checklist / reference / doc), run `/flightdeck:new` — it stamps the correct frontmatter + naming and regenerates INDEX/cockpit. Don't hand-write deck artifacts or hand-derive their paths.

<!-- END: flightdeck -->
```

**Relative-link rewrite (applies to every copied block — `## In Progress`, `## Next`, `## Hanging Tasks`):** any link target that is NOT an HTTP/HTTPS URL, NOT an anchor (`#...`), and NOT already absolute (`/...`) must be prefixed with `flightdeck/` — since cockpit.md lives in `flightdeck/` but AGENTS.md lives at repo root. This includes `./` and `../` targets (prefix as-is, no normalization). Example: `[checklists/foo.md](checklists/foo.md)` → `[checklists/foo.md](flightdeck/checklists/foo.md)`. Link text stays unchanged; only the path inside the parentheses is rewritten.

### Step 4: Write the regenerated AGENTS.md

Use Write to save.

- File missing: write `<flightdeck block>\n\n<!-- Hand-authored content below this line is preserved across emitter runs. -->\n`
- File had markers: pre-marker content + new flightdeck block + post-marker content
- File had no markers: flightdeck block + blank line + entire existing content (no footer comment — the existing content already occupies the hand-authored space)

### Step 5: Verify determinism (do NOT write again)

The transform must be deterministic — a hypothetical re-run would produce a byte-identical block. Don't actually re-run Steps 1–4 or re-write the file; instead self-check the block you just wrote against this checklist:

- `## Current focus` appears once, with the `Focus` value present and not duplicated.
- `## In Progress` rows match the cockpit AUTO region verbatim (same order, same count); empty region rendered as `None.`.
- `## Next` carries the cockpit body (or `None.`); not merged with `Focus`.
- Every relative link `](...)` inside the block carries the `flightdeck/` prefix — scan each one.
- No trailing whitespace on any line inside the markers; exactly one blank line between sections.

Any miss is a construction bug — fix the block directly, don't mask it by claiming a clean re-run.

### Step 6: Report

Report concisely:

```
─── 🌉 emit-agents-md ───
[Saved] AGENTS.md regenerated.
  Focus: <one-line>
  In Progress (active artifacts): <N>
  Next: <one-line, or none>
  Hanging tasks: <N>
  Hand-authored content preserved: <yes / no / n/a (file missing before)>
```

## Idempotency rules

- Read cockpit.md fields in a fixed order (Focus → In Progress → Next → Hanging Tasks). Don't reorder.
- Empty sections must produce the placeholder text — never be omitted (otherwise the second run might re-omit, but the first might have included, causing diffs).
- One blank line between sections inside the flightdeck block. No trailing whitespace inside markers.
- **Link prefixing is deterministic**: a relative link `(path)` always becomes `(flightdeck/path)` — no path normalization (e.g., do NOT collapse `flightdeck/../README.md` to `README.md`; emit the prefixed path). Determinism beats prettiness.

## Don't do

- **NEVER read or modify content OUTSIDE the fenced markers** — those blocks are the user's hand-authored prose; touching them clobbers their content (Step 2 already requires it be preserved verbatim).
- Don't add markers around pre-existing hand-authored content — leave it alone, add the flightdeck block above it.
- Don't include checklist / spec / artifact details in the regenerated block — those are linked, not embedded. AGENTS.md stays terse.
- Don't run this from a non-clean working tree without warning the user — mid-edit `cockpit.md` produces a stale snapshot.
