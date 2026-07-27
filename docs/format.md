# Flightdeck format and writing guide

Flightdeck documents are ordinary Markdown. Headings make recovery predictable, but there is no
parser schema, required frontmatter, revision ledger, or generated state.

## Deck

`flightdeck/deck.md` contains one Open Work list and a few stable project links:

```markdown
# Flightdeck

## Open Work

- **Focus:** [Ship alpha.7](work/ship-alpha7/index.md)
- [Improve examples](work/improve-examples/index.md)

## Project links

- [Repository context](../CONTEXT.md) — stable project vocabulary.
```

When Open Work exists, exactly one entry is marked Focus. An empty list has no Focus. Do not list
Finished or Stopped Work, local stages, Slices, commits, or historical logs here.

## Work page

Every `work/<id>/index.md` uses Goal, Status, Current, and Next. Progress, Work rules, and References
appear only when useful.

- **Goal:** the independently focusable outcome the Work exists to achieve;
- **Status:** `Open`, `Finished`, or `Stopped`;
- **Current:** the present Work-level truth, including a blocker when one exists;
- **Next:** one executable action and the current execution pointer, with at most three local links
  required to perform it;
- **Progress:** a short recent summary, not a permanent log;
- **Work rules:** temporary constraints every recovery must see;
- **References:** useful supporting material that remains lazy.

Use `None` for Next only after Work becomes Finished or Stopped. There is no `Read now` section:
immediate recovery links belong directly in the Next sentence.

## Work context

`context.md` is required and always read on recovery. Store only stable goal-specific facts,
constraints, decisions, and terms. Its internal headings are optional. Do not copy Current, Progress,
the complete Plan, or session narration into it.

Root `CONTEXT.md` remains the authority for project-wide language and product boundaries.

## Plan and Slices

Create `plan.md` only for meaningful stages, acceptance checks, or route uncertainty. The Plan owns
ordered completion; it does not repeat the Work Goal, Current, or current execution pointer.

```markdown
## Delivery

- [x] Define the public contract.
- [ ] [Deliver the streaming handler](slices/deliver-streaming-handler.md)
```

A Slice expands exactly one linked Plan item when its deliverable or decision needs durable detail.
Every Slice requires only Outcome, Current, and Next. Add Steps, Decisions, Verification, and
References when they carry real information. Do not add status frontmatter, revision metadata,
mandatory empty sections, a Slice map, or another completion rollup.

A Decision Slice records one route-shaping decision; a separate Delivery Slice implements it. When
the route is still foggy, an optional `Not yet specified` Plan section may hold in-scope uncertainty
without checkboxes until it can be formulated precisely.

## References and specialist outputs

Route supported Work-scoped research, specifications, reviews, and similar documents into
`work/<id>/references/`. Route Work-scoped domain meaning into `context.md`, and execution order into
the Plan and its Slices. Keep filenames descriptive and the References directory flat until volume
justifies a subject directory.

Source changes, prototypes or assets owned by source, external-system records, temporary files, and
unsupported third-party outputs stay at their authoritative location and are linked. Project-wide
language belongs in root `CONTEXT.md`; ADRs belong in `docs/adr/`.

## Recovery and Save

Recovery reads the selected Work page and context, an existing low-resolution Plan, at most three
local links from Next, and live Git state. Before execution it inspects Knowledge subject/topic
paths and reads only guidance relevant to the current action. It does not preload every Slice,
Reference, Knowledge document, historical Work, or Git history.

Save updates Slice detail, Plan completion, Work Current/Next, stable context, and Deck navigation
only when their own recovery meaning changed. Save edits Markdown only and does not imply a Git
operation.

## Knowledge

Treat `flightdeck/knowledge/` as the demand-grown project operating playbook. Put one independently
applicable, current positive practice under each organic `<subject>/<topic>.md` path. Use clear
headings, concise examples, and source links when helpful; do not pre-seed a taxonomy or starter set.

Before executing a new or recovered action, Work proactively checks for applicable Knowledge. It
reads relevant existing Work links first, inspects subject/topic paths against the request and
Work Goal, Current, and Next, then searches headings only inside plausible subjects when path names
are insufficient. Read matching guidance before acting; do not ask the user to locate the library.
Guidance is advisory. Put it in Next only when immediately required, under References when a fresh
session needs continuing support, and do not log ordinary consultation.

Promote a Work conclusion only when current evidence verifies it, another independent Work is
plausibly likely to benefit, and it can be rewritten as self-contained project-specific positive
guidance. Rewrite or remove disproven material and keep unresolved replacement research in Work.
Do not add required frontmatter, kinds, activation rules, routing fields, revisions, histories,
stale flags, recheck ledgers, trap classifications, or a Knowledge index or registry.
