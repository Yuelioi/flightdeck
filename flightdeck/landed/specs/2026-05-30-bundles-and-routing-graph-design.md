# RFC: Bundles & Routing Graph — scaling flightdeck beyond flat files

> **Status**: implemented in v1.1.0 (2026-05-30). Archived.
> **⚠ Bundle mechanism later REMOVED by the 2.0 entry-collapse rewrite (2026-06-01)** — `protocol.md` now states "No bundle README". The bundle-only fields **`bundle` / `reading_order` / `scope` / `non_goals` are NOT live fields**; only `skip_when` (negative routing) survives. Canonical field set: [protocol.md § Frontmatter field reference](../../../skills/preflight/protocol.md#frontmatter-field-reference-canonical). Do not read this RFC as a live design.
> **Targets**: `skills/workflow/folder-semantics.md`, `skills/workflow/SKILL.md`, `skills/walkaround/SKILL.md`, `CHANGELOG.md` + `VERSION` + plugin manifests.
> **Type**: additive (post-v1.0 additive-only window) → minor bump.

## Implementation note (2026-05-30, v1.1.0)

Shipped. Deviations from the RFC as written, for the record:

- **Proposal H (adapter sync) re-targeted.** The RFC assumed the `adapters/{claude,codex,cursor,gemini}/` files carry model prompt. They don't — they are install/verification docs. The real cross-platform prompt is the shared `skills/workflow/` files (Claude/Codex/Cursor load them directly; `GEMINI.md` @-includes `SKILL.md` + `folder-semantics.md`). Since `folder-semantics.md` is only loaded on demand, the core semantics (decision table, graph-routing/reachability, bundle contract, `skip_when`) were synced into the **always-loaded `SKILL.md`** instead. No adapter README took routing content.
- **`reading_order` made an explicit reachability edge.** A contradiction surfaced during review: the bundle contract lists leaves in `reading_order` frontmatter, but Audit 9's reachability was links-only — so well-formed bundles would false-positive as orphans. Fixed in `folder-semantics.md`, `SKILL.md`, and walkaround Audit 9: `reading_order` entries count as edges; a leaf missing from `reading_order` is the orphan.
- **Scaffolds unchanged.** Pre-seeding bundle scaffolding violates the "add structure on demand" principle; bundles are created when a topic needs them, not scaffolded.
- **Plugin manifests bumped** (`.claude-plugin` plugin + marketplace, `.codex-plugin`, `.cursor-plugin`, `gemini-extension.json`) to `1.1.0` alongside `VERSION`, to avoid version drift.
- **Proposal F (structured data)** documented only; not exercised (awaiting a concrete need, as planned).

## Motivation (from real failure cases)

1. A multi-file evergreen reference set was filed under `specs/` — but it is not a *design to be implemented*, it is a *long-lived operational convention*. `specs/` vs `checklists/` vs `sketches/` boundaries are fuzzy.
2. A custom root-level file was never linked from any entry → no session ever read it → silent invisibility. Humans spot this in an IDE; AI almost never does.
3. After moving a reference set into a subfolder, it was unclear whether subfolders are routed or are a first-class concept at all.

**Diagnosis**: flightdeck's *routing* model is already recursive (frontmatter grep descends into subdirectories), but its *semantic* model is still stuck in the "flat markdown file" era. This RFC adds two first-class concepts: **bundles** and the **routing graph**.

**Reference studied**: `nextlevelbuilder/ui-ux-pro-max-skill` (a 326-file skill) — its "thin entry + load-on-demand + explicit skip" organization is the model for scaling without chaos.

## Two reframes (write these into folder-semantics as anchors)

1. **"file" → "bundle"**: a directory can be a single cohesive knowledge unit, not just a pile of independent `.md` files.
2. **"filesystem-routed" → "graph-routed"**: *a file not reachable from any entry effectively does not exist.* Flightdeck routes by a reachability graph, not by filesystem enumeration.

## Borrowed from ui-ux-pro-max

| Pattern | Their implementation | Adopted as |
| --- | --- | --- |
| Thin entry + data split | `SKILL.md` is a priority table / quick-ref; the 161 palettes live in `data/*.csv`, queried on demand ("Scripts do not read this table") | Bundle = README router + on-demand leaves; bulk data lives in sidecar structured files |
| Strong frontmatter + Must/Recommended/**Skip** | Explicit when-to-use, when-NOT-to-use, decision criteria | New optional `skip_when` field (negative routing) — flightdeck currently only has positive routing |
| Separation of concerns | data / scripts / templates | Bundle internally splits router (README) vs detail (leaves) |

## Proposals

### A. Bundles as a first-class concept

- **Definition**: a subfolder `<folder>/<name>/` is a *bundle*. It MUST contain a `README.md` acting as the **bundle contract**.
- **The README is a contract, not just an entry.** Frontmatter MUST include:
  ```yaml
  ---
  bundle: true
  when_to_read: <one-line trigger>
  applies_to: [<short tag>, ...]
  reading_order: [01-foo.md, 02-bar.md, ...]   # the leaf list + order
  last_updated: YYYY-MM-DD
  # optional: skip_when, scope, non_goals
  ---
  ```
  The body SHOULD state **purpose / scope / non-goals / reading order**. Without this, a bundle decays back into "a folder with many `.md` files".
- **Leaf rules** (a *leaf* = any content/chapter file in the bundle other than the README; the README is the router, everything else is a leaf):
  - Leaves MUST NOT carry routing frontmatter (`when_to_read` / `applies_to`). Otherwise a recursive grep matches them directly and breaks the single-entry guarantee. Walkaround flags such "over-reaching" leaves.
  - **Freshness lives on the bundle.** Leaf `last_updated` is OPTIONAL; the README's `last_updated` is the authoritative freshness for the bundle. (Required-on-every-leaf invites metadata decay / pseudo-freshness.)
  - **Inheritance, stated explicitly**: *bundle child documents inherit routing semantics from the README unless explicitly overridden.*
  - Leaf-to-leaf references use **relative paths**; walkaround's existing dangling-reference audit covers them, so renames/moves that break internal links surface.
- **No nested bundles**: a bundle MUST NOT contain a sub-bundle. One routing boundary per bundle.
- **Evolution slot**: discovery currently uses recursive frontmatter grep; the bundle contract reserves room for a future explicit `routing index` so today's convention doesn't lock it out.

### B. Routing graph / reachability

- An **orphan** = a file not reachable from any known entry. Entries form a routing graph: `cockpit.md`, `INDEX.md`, `manifest.md`, and any bundle README.
- Custom folders / root files are ALLOWED, but MUST be reachable (linked from some entry); otherwise walkaround flags them as orphans. Do NOT forbid custom files — flightdeck's strength is *extensible conventions*, not a locked taxonomy.
- Anchor line for semantics: **"Flightdeck is graph-routed, not filesystem-routed; unreachable = nonexistent."**

### C. Folder boundary decision (kills `specs/` misuse)

Decision table (place near the top of folder-semantics):

| Kind | Lifecycle | Goes in |
| --- | --- | --- |
| Uncommitted idea | not started | `sketches/` |
| A design to implement | one-shot, archived after shipping | `specs/` |
| Long-lived operational reference / standard / checklist | evergreen | `checklists/` |

- **Wording fix**: do not say "checklists contain conventions" (a checklist reads as steps/gates). Say: **"`checklists/` holds reusable checklists, conventions, and reference standards — operational reference."**
- **No `references/` folder**: considered splitting evergreen reference out of `checklists/`, but it overlaps `checklists/` heavily (both are *authored* reference) and just adds a folder. Clear division instead: **`checklists/` = authored operational reference; `charts/` = imported external material (others' code / RFCs / articles).**

### D. Walkaround: new integrity checks (pure markdown, no CLI)

Surface, never auto-fix ("audit is a linter, not a formatter"). Extend the existing audit set:
1. **Bundle-aware frontmatter** (extend Audit 1): a `checklists/` or `incident-reports/` entry may be a bundle (subfolder + README). Check: subfolder has a `README.md`; README carries the contract frontmatter (`bundle: true` + `reading_order` + routing fields); leaves do NOT carry routing fields (over-reaching leaf = CRITICAL); `reading_order` matches the actual leaf files.
2. **Orphans** (new): parse markdown links in every entry, diff against actual `.md` files, report any not reachable from any entry — including custom root files.
3. **Stray files** (new): a file inside a routed folder missing required frontmatter, or a file matching no known folder semantics. (Dead links are already covered by the existing dangling-reference audit.)
4. **INDEX prompt** (new, INFO): when ≥2 bundles exist and there is no `INDEX.md`, suggest creating one (not a hard requirement).
- A known-good **whitelist** must be spelled out in the audit (entries, folders, repo-level files like `.gitignore` / `README.md`).
- **First-run note**: an existing project's first walkaround may list many issues — advise gradual cleanup, not all-at-once.

### E. `skip_when` — negative routing (new, OPTIONAL field)

Flightdeck only has positive routing (`applies_to` / `when_to_read`). Add an OPTIONAL frontmatter field **`skip_when`** (one line: "when NOT to read this") to cut "maybe relevant" token waste — mirrors ui-ux-pro-max's "Skip" section. Optional = absence is fine; walkaround does not enforce it.

### F. Structured data (optional, low priority)

`.csv` / `.json` is allowed ONLY inside a bundle and ONLY with a sidecar `README.md` router stating "query on demand, do not read fully". Structured files MUST NEVER be the primary entry (preserves AI readability + git reviewability). Not pushed until a concrete need appears.

### G. INDEX.md — soft prompt, never required

Stays a suggestion. Quantified trigger: **≥2 bundles and no `INDEX.md`** → walkaround prompts (wording may be strong: "discoverability degrades badly") but never blocks.

### H. Adapter / scaffold sync (required)

Bundle README semantics MUST reach each platform adapter's prompt, or models won't obey. After folder-semantics lands: sync bundle / decision-table / reachability / `skip_when` into the claude/codex/cursor/gemini adapters + scaffolds. Stray/orphan checks stay walkaround-only (not duplicated into adapters).

## Decisions (all settled)

- Leaf `last_updated`: **optional** (freshness on the README).
- `skip_when`: **add, optional**.
- `references/`: **not introduced** (overlaps `checklists/`).

## Implementation order

C (decision table — smallest change) → A (bundle definition) → B (reachability/graph) → D (walkaround checks) → E (`skip_when`) → G (INDEX prompt) → H (adapter/scaffold sync, last). F on demand. Bump `CHANGELOG.md` [Unreleased] + `VERSION` (minor).
