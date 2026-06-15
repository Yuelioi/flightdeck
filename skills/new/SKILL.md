---
name: new
description: Create a new flightdeck deck artifact (spec / plan / incident / checklist / reference / doc) with correct per-kind frontmatter, naming, and auto-regenerated INDEX/cockpit — use this instead of hand-writing the file. Triggered by /flightdeck:new.
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
| reference | `references/` |
| doc | `docs/` |

**Naming:** `[<date>-]<slug>.md`. Add the `<YYYY-MM-DD>-` prefix **iff `status != idea`**;
an `idea` artifact is **dateless**. Exception: a **`doc` is always dateless** regardless of
status (standing reference, not a dated event). **Never auto-append `-design`** — `new-artifact.md` ✓,
not `new-artifact-design.md` (only if "design" is genuinely part of your slug).
**slug rule:** lowercase ascii, digits, hyphens only (`^[a-z0-9-]+$`). To make a slug from
a title: drop non-ascii, spaces → `-`, lowercase, keep `a-z0-9-`.

**Per-kind frontmatter**
- workflow (`spec` / `plan`): `status` + **`summary` (required** — it drives the INDEX row; `flightdeck_index` needs it) + `last_updated` (omit for `idea`) + `implements:` (plan, optional).
- knowledge (`incident` / `checklist` / `reference` / `doc`): `status` + `when_to_read` + `applies_to: [..]` + `last_updated` (all required); `summary` optional.

**Default status:** workflow → `idea` (park; flip to `active` to start — that adds the date prefix). knowledge → `active` (knowledge is consumable the moment it exists; that's why its default differs from workflow's).

**`incident` extra contract (error library):**
- **Dedup before you create.** An incident is an error-library entry — before authoring one, **first check it isn't already recorded**: grep the error text into `incidents/` and/or run `flightdeck_index.py <deck> --match-signature "<symptom>" [--sig-error-type <TYPE>]`. A fingerprint hit → **append a `## [Case N]` to the existing file instead of creating a new one** (see [protocol § Hit path](../preflight/protocol.md#hit-path--check-the-error-library-before-writing-a-new-incident)). Only create when there is no match.
- **Fill the `## Signature` block after creating.** The incident scaffold ships a `## Signature` block — fill its **four keys and only those four** (`symptom` / `error_type` / `where` / `trigger`); this is a **hard boundary** (no severity / owner / component / … — adding a key needs its own spec). `symptom` is the human-readable / grep anchor (the real error string, may be multi-line); `error_type: —` is a first-class case for non-exception problems (UI / perf / data). The fingerprint is computed from it — the author never hand-writes a fingerprint.

**After writing:** run `uv run <flightdeck-pkg>/scripts/flightdeck_index.py <deck>` to
regenerate INDEX + cockpit. An `active` workflow artifact projects into cockpit `## In Progress`;
an `idea` does not.

**If the target file already exists:** the script refuses; by hand, pick a different slug
or remove/rename the existing file first.

**Graduate question (spec only — ask proactively):** immediately after creating a `spec`,
judge whether it meets **either** of these criteria (lenient; the user's yes/no is the gate,
not a mechanical check):

- **约束后续开发** — defines a rule / contract / interface that future code must obey
  (error-code table, i18n-key convention, plugin protocol, design tokens, …).
- **大概率被反复参考** — will be opened for repeated look-up rather than read once and forgotten.

Negative examples — these look like design specs but **do NOT qualify** unless they also
set a durable rule the codebase must obey:
- One-off bugfix design / post-mortem spec
- A migration-sequencing spec (ordering steps for a one-time migration)
- A throwaway experiment / probe design
- A specific feature's implementation plan (no lasting contract)

If the spec plausibly hits either criterion, **ask the user: "这份 spec 要标记为 graduate？"**
(English: "Mark this spec `graduate: true`?"). On yes, write `graduate: true` into the
spec's frontmatter.

**Flag window:** `graduate: true` can be set at creation time (here) **or at any point
during the spec's active life** — mid-plan-execution is fine. The gate is the user's
yes/no; flightdeck does not re-detect at completion time. A missed flag is the user's
responsibility; there is no completion-time auto-detection fallback.

**`when_to_update` for knowledge artifacts (docs / references):** when authoring a `doc`
or `reference` that will be referenced repeatedly, consider adding a `when_to_update` field
to the frontmatter — a one-phrase "what kind of change would make this doc wrong". This
opts the artifact into stale detection (the rituals auto-flip `status: stale` when a
matching change is detected). See `skills/preflight/templates.md` for the format and
good/bad examples. Graduate-out docs **must** carry `when_to_update` (omitting it opts
the doc out of stale detection immediately, defeating the point).

## Report

壳建好、正文写入后，按统一 banner（[protocol § Act-report-close loop](../preflight/protocol.md#act-report-close-loop)）末尾报告：

```
─── ✍️ new ───
[Saved] <kind>: <path>
```

这枚 banner **就是** new 的用户可见报告——不要再复述脚本的 `created … at …` 原始 stdout。standalone 调用出此 banner；作为更大 flow 的子步时并入外层 banner。

## Relationship to landing

`landing` already knows the knowledge-artifact convention and creates incidents/checklists
during the wrap ritual. `/flightdeck:new` is **usable for knowledge but not the required
path** there — both share the same frontmatter truth; use whichever fits the moment.
