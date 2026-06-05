---
name: new
description: Create a new flightdeck deck artifact (spec / plan / incident / checklist / chart / doc) with correct per-kind frontmatter, naming, and auto-regenerated INDEX/cockpit — use this instead of hand-writing the file. Triggered by /flightdeck:new.
---

# Flightdeck New — author a deck artifact

The **authoring entry**. When you (or an external authoring skill like brainstorming /
writing-plans) need to produce a deck artifact, use this instead of hand-deriving the
location, frontmatter, naming, and INDEX/cockpit regen. It is the single authority for
**how a deck artifact is shaped** — the fast path stamps it via a script; the fallback
below is the same contract for hand-authoring.

**Shell-first handoff:** create the shell here first, then write the body into the
returned path. Don't write content elsewhere and move it afterward.

## Fast path (a Python runtime is reachable)

```
uv run <flightdeck-pkg>/scripts/flightdeck_new.py <deck> <kind> \
    --slug <kebab-slug> --title "<Title>" [--status idea|active|done] \
    [--summary "..."] [--implements specs/<x>.md] \
    [--when-to-read "..."] [--applies-to tag1,tag2]
```

It prints the created path. Then write the artifact body into that file.

## Authoring contract (also the no-runtime fallback — do this by hand)

**kind → folder**

| kind | folder |
|---|---|
| spec | `specs/` |
| plan | `plans/` |
| incident | `incidents/` |
| checklist | `checklists/` |
| chart | `references/` |
| doc | `docs/` |

**Naming:** `[<date>-]<slug>.md`. Add the `<YYYY-MM-DD>-` prefix **iff `status != idea`**;
an `idea` artifact is **dateless**. Exception: a **`doc` is always dateless** regardless of
status (standing reference, not a dated event). **Never auto-append `-design`** — `new-artifact.md` ✓,
not `new-artifact-design.md` (only if "design" is genuinely part of your slug).
**slug rule:** lowercase ascii, digits, hyphens only (`^[a-z0-9-]+$`). To make a slug from
a title: drop non-ascii, spaces → `-`, lowercase, keep `a-z0-9-`.

**Per-kind frontmatter**
- workflow (`spec` / `plan`): `status` + **`summary` (required** — it drives the INDEX row; `flightdeck_index` needs it) + `last_updated` (omit for `idea`) + `implements:` (plan, optional).
- knowledge (`incident` / `checklist` / `chart` / `doc`): `status` + `when_to_read` + `applies_to: [..]` + `last_updated` (all required); `summary` optional.

**Default status:** workflow → `idea` (park; flip to `active` to start — that adds the date prefix). knowledge → `active` (knowledge is consumable the moment it exists; that's why its default differs from workflow's).

**After writing:** run `uv run <flightdeck-pkg>/scripts/flightdeck_index.py <deck>` to
regenerate INDEX + cockpit. An `active` workflow artifact projects into cockpit `## 进行中`;
an `idea` does not.

**If the target file already exists:** the script refuses; by hand, pick a different slug
or remove/rename the existing file first.

## Relationship to landing

`landing` already knows the knowledge-artifact convention and creates incidents/checklists
during the wrap ritual. `/flightdeck:new` is **usable for knowledge but not the required
path** there — both share the same frontmatter truth; use whichever fits the moment.
