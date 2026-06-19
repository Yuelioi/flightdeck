# Templates

Reusable file templates for `flightdeck/` files. Each template has a strict structure — deviation typically means the file should live in a different folder or be deleted.

> **Field semantics are canonical in [protocol.md § Frontmatter field reference](protocol.md#frontmatter-field-reference-canonical).** This file holds ready-to-paste blocks + per-template authoring rules; it does not redefine what a field *means* or which kinds require it.

---

## rules.md

```markdown
---
version: 3.0             # REQUIRED — static identity stamp written by launch (future migration anchor; no ritual reads it at runtime)
---

## House rules

### Project conventions

Deck-local flightdeck conventions only (e.g. "specs written in Chinese", "do not use references/").
General project conventions (code style, "branch before committing") belong in the project's agent instruction file (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`, per the running agent), NOT here.

### Rules

<!-- Behavior rules the AI maintains from your natural-language requests. Leave empty;
     tell the AI a persistent preference and it appends a free-prose rule here (source + date),
     e.g. "- ask before committing (you, 2026-06-16)". No magic-string syntax. -->
```

### Authoring notes

- **Mandatory file** — part of the minimal contract (`rules.md` + `cockpit.md`). Must exist and carry `version` — the **only** structured field. Behavior resolves via [protocol § Rule resolution order](protocol.md#rule-resolution-order) (deck `### Rules` → environment inference → built-in default / skill judgment).
- **`version` is deck identity, not a toggle.** Records the flightdeck release this deck conforms to — a static stamp written by `launch`, the future (3.0→3.1) migration anchor. **No ritual reads or bumps it at runtime.**
- **`### Rules` is AI-authored, not a toggle catalog (3.0).** There is no magic-string vocabulary. When you state a persistent preference, the AI appends a free-prose rule here (with source/date) and honors it above the default. What used to be toggles are now inference / default / skill-judgment, each overridable by a deck rule:
  - `git` → inferred: git-backed iff an ancestor `.git` exists **and** the deck is not gitignored; a deck rule (e.g. "this deck doesn't use git") overrides.
  - `emit_agents_md` → `landing` auto-regen **only if** deck root already has `AGENTS.md`; explicit `/flightdeck:emit-agents-md` **always** creates (the only bootstrap path from a no-`AGENTS.md` start).
  - `commit` → **local commit auto, push asks** (local reversible; push outward). A deck rule can ask-before-commit or disable auto-commit; under no-git there is no commit regardless.
  - ritual self-invocation → **all five rituals always self-invoke**; archiving is **landing's judgment** (not a toggle); `scripts` inferred from runtime; no `disabled_folders`.
- **Authority**: **the project's agent instruction file (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`) > deck `### Rules` > defaults.** General project conventions belong in that agent file, not here. Conflicts among deck rules are the user's responsibility (no auto-resolution).
- **Malformed YAML or unparseable frontmatter** → warn and fall back to all defaults; never hard-fail.
- **Read first**: every entry skill reads `rules.md` before acting and resolves behavior per Rule resolution order.
- **`synced: true`（vendored 文件标记）** — 仅出现在从母库同步下来的 checklists/docs 文件。布尔标记，无路径；母库固定 `~/.flightdeck`，源文件 relpath 恒等于消费端自身 relpath，故不需存路径。由 `/flightdeck:sync` 写入；`flightdeck_index.py --sync-status` 消费。母库文件本体**不携带**此字段（母库文件是源头，不是消费副本）。
- **`consumers`（母库专属注册表）** — 仅出现在母库文件（`~/.flightdeck` 下）的 frontmatter，单行 JSON 数组，记录已注册的消费 deck 路径列表。`--register-consumer` 写入、`--prune-consumers` 清理、`--list-consumers` 只读。`/flightdeck:sync --fanout` 据此扇出到所有下游。消费副本**禁止**携带此字段（walkaround Audit 15 检测非法实例）。

---

## spec frontmatter

```markdown
---
status: idea          # idea / active / done (idea = unstarted, no date prefix; flip to active to start)
summary: <one-line gist>     # recommended; single-line plain text — no | [ ] or newlines. Drives the INDEX row. ⚠ Do NOT use ` — ` (a space-padded em-dash): the INDEX row uses it as the field delimiter, so a summary containing it causes column ambiguity. Use a colon, comma, or hyphen instead.
last_updated: YYYY-MM-DD     # recommended; auto-bumped by status/landing on a real change (not typos)
note: <one-line diagnostic>  # optional; "why it hasn't moved" (blocker / pending reason). Rendered in cockpit In Progress + walkaround as [note: …]
supersedes: <path>           # optional; forward edge to the workflow artifact this replaces (path relative to flightdeck root)
related: [<path>, ...]       # optional; weak links — shared premise / blast-radius, NOT supersedes or implements
# optional: graduate: true
#   — 结构性设计稿完工后本体变身常驻 docs；命中"约束后续开发/大概率反复参考"判据时
#     由 /flightdeck:new 或 plan 执行中提示打标；landing 负责将 done 的 graduate 本体改写搬入 docs/
# optional: verify: <one-line how-to-verify>  — field present = owes verification (an add-on marker on done/stale; preflight surfaces it); delete the field once verified
---
```

(An idea-stage spec usually carries only `status: idea` + `summary`; the rest are for longer-lived active specs.)

---

## plan frontmatter

```markdown
---
status: active               # idea / active / done
summary: <one-line gist>     # recommended; single-line plain text — no | [ ] or newlines. ⚠ Do NOT use ` — ` (a space-padded em-dash): the INDEX row uses it as the field delimiter, so a summary containing it causes column ambiguity. Use a colon, comma, or hyphen instead.Drives the INDEX row.
last_updated: YYYY-MM-DD     # recommended; auto-bumped by status/landing
note: <one-line diagnostic>  # optional; "why it hasn't moved". Rendered in cockpit In Progress + walkaround as [note: …]
implements: specs/<x>.md     # optional; path relative to flightdeck root; absent → walkaround flags "orphan plan"
supersedes: <path>           # optional; forward edge to the artifact this replaces
related: [<path>, ...]       # optional; weak cross-links
# optional: verify: <one-line how-to-verify>  — field present = owes verification (an add-on marker on done/stale; preflight surfaces it); delete the field once verified
---
```

**Plan body — progress pointer (`## Progress`).** A plan tracks execution progress with a single **pointer**, not per-task checkboxes:

```markdown
## Progress

current: Task 3 — wire the checkpoint subpath into landing SKILL.md
```

- `current:` names the next-to-execute (or in-progress) task. A **checkpoint** advances it at each plan-task boundary (see [exit-ritual § Checkpoint](exit-ritual.md#checkpoint--lightweight-board-sync-subpath)); cockpit `## Next` quotes it.
- It lives in the plan **body**, not frontmatter — so `flightdeck_index.py` does not parse it and `## In Progress` stays a pure `status: active` projection (no script change).
- When every task is finished, `current:` reads `done — ready to land` and the plan flips `status: done`.

---

## knowledge frontmatter — incident / checklist / reference

```markdown
---
status: active            # active / stale / obsolete
                          # stale=pending-review (suspected outdated, or new-but-unverified, distinguished by the verify field); obsolete=dead, awaiting-archive drain state
when_to_read: <one-line trigger>
applies_to: [<tag>, <source/path>, ...]   # mixed: plain words = routing tags; entries with / = source paths, used in stale detection (to keep fresh, include at least one path)
last_updated: YYYY-MM-DD
# optional: when_to_update: <what kind of change would make me wrong>
#   — a concrete trigger event, not a blanket condition; contains ≥1 specific noun/path, no "any/all"
#   GOOD: changed the plugin load protocol / touched hooks/stop.sh
#   BAD:  on any change
# optional (incidents/checklists): skip_when: <one-line "when NOT to read this">
# incidents only: recurrences: 1   # auto-bumped at landing on a clear recurrence; renders to INDEX as `recur: N` when > 1
# incidents only: resolved_by:     # empty = not yet root-fixed; fill commit SHA / test id = retirement basis (then flip status: obsolete)
# optional: verify: <one-line how-to-verify>  — field present = owes verification (an add-on marker on done/stale; preflight surfaces it); delete the field once verified
---
```

---

## docs frontmatter

```markdown
---
status: active            # active / stale / obsolete
                          # stale=pending-review (suspected outdated, or new-but-unverified, distinguished by the verify field); obsolete=dead, awaiting-archive drain state
when_to_read: <one-line trigger>
applies_to: [<tag>, <source/path>, ...]   # mixed: plain words = routing tags; entries with / = source paths, used in stale detection (to keep fresh, include at least one path)
last_updated: YYYY-MM-DD
summary: <one-line gist>  # optional but recommended; drives INDEX row
# optional: when_to_update: <what kind of change would make me wrong>
#   — a concrete trigger event, not a blanket condition; contains ≥1 specific noun/path, no "any/all"
#   GOOD: changed the plugin load protocol / touched hooks/stop.sh
#   BAD:  on any change
# optional: verify: <one-line how-to-verify>  — field present = owes verification (an add-on marker on done/stale; preflight surfaces it); delete the field once verified
---
```

**Naming**: `<topic>.md` — no date prefix (docs are stable references, not log entries). Examples: `runtime.md`, `folder-semantics.md`, `glossary.md`.

**Fields**: same lifecycle set as incident/checklist (`status` / `when_to_read` / `applies_to` / `last_updated`), plus an optional `summary` that drives the INDEX row — prefer it to `when_to_read` for the row when the doc is general-reference rather than situational.

---

## INDEX.md — per folder

```markdown
# <folder>/ — INDEX

<!-- AUTO:<folder> -->
- [<file>](<file>) — <status> — <one-line summary>
<!-- /AUTO -->

<!-- optional hand-maintained area (grouping notes for multi-file topics); AI does not touch -->
```

For a workflow row (`specs/` `plans/`) the `<one-line summary>` is the file's `summary` frontmatter, copied verbatim (with `|` pipe-escaped) — the row is **derived from `summary`**, not hand-written; see [exit-ritual.md § INDEX regeneration](exit-ritual.md#index-regeneration--scope-rules) for the row-building rule. A file with no `summary` produces a row with the summary segment omitted. Rows in `incidents/` `checklists/` `references/` add `when_to_read` / `applies_to`. `implements`, `supersedes`, `related`, `note` do NOT go into the INDEX. (`specs/INDEX` groups its AUTO region by status — see [folder-semantics § specs/](folder-semantics.md#specs--designs).)

---

## INDEX.md — area (nested folder inside a knowledge folder)

Used for nested sub-folders within a knowledge folder, e.g. `docs/<area>/INDEX.md`.

```markdown
---
purpose: <one-line description of what this area covers>
last_updated: YYYY-MM-DD
---

# <folder>/<area> — INDEX

<!-- AUTO:<area> -->
- [<file>](<file>) — <status> — <one-line summary>
<!-- /AUTO -->
```

**Frontmatter fields** (`purpose` + `last_updated`) are read by `flightdeck_index` to render the parent folder's INDEX area row — keep them accurate.

**AUTO marker convention (critical — prevents first-regen drift)**: use the **area folder name** as the kind in `<!-- AUTO:<area> -->`. For example, `docs/runtime/INDEX.md` uses `<!-- AUTO:runtime -->`. This matches the marker that `flightdeck_index` emits when regenerating the area INDEX (it uses the area folder name as the kind). Using any other string will cause a spurious drift report on the first regeneration.

---

## status flow (recommended, not enforced)

Status values (by kind) + location semantics are canonical in [protocol § Status ⟂ location](protocol.md#status--location-two-orthogonal-axes) — not restated here.

---

## incident-report body

`/flightdeck:new incident` scaffolds this shape; fill the `<...>` placeholders. The `## Signature` block is **body, not frontmatter** — it stays out of the per-session routing face (preflight loads only INDEX rows), yet is grep-able and is what `flightdeck_index.py --match-signature` parses for deterministic recurrence dedup.

```markdown
# <one-line topic>

## Signature
- symptom: `<error text verbatim / observable symptom>`   # grep anchor; key:value line (the script parses it)
- error_type: <exception class / error code, or —>
- where: <function / file / subsystem>
- trigger: <what action / scenario provokes it>

## Symptom / repro
<how the user / test / build actually observed it; steps to reproduce>

## Root cause
(FORBIDDEN: "forgot", "careless", "didn't notice" — must be a wrong assumption / wrong model / wrong process)
I assumed X, but in reality Y.

## Fix
The specific next-time action. Not "be careful". Concrete behavior or check.

## Cases
- YYYY-MM-DD first          ← first line written at create time
- YYYY-MM-DD recurrence, <one line>   ← appended on recurrence; keep only the most recent N
```

### Rules

- **`## Signature` is a hard 4-key schema — only `symptom` / `error_type` / `where` / `trigger`.** It exists *only* for hit-rate (grep + fingerprint); resist growing it into a second hidden frontmatter. Do not add keys for environment / version discrimination (e.g. Pydantic v1 vs v2 same-symptom-different-cause) — fold that into `trigger` or the body. Deliberate trade-off: same symptom across versions may share a fingerprint, disambiguated by `trigger` / the AI fuzzy layer.
- **`symptom`** holds the actual string AI/grep will see (error text verbatim / exception class), not an abstract narrative title. May be multi-line (indent or `|` for a stack trace). It is the human-read / grep anchor; the fingerprint is **computed** from it — authors never hand-write a fingerprint.
- **`error_type: —` is a first-class case, not a degenerate one.** UI misalignment / perf regression / deadlock / data corruption have no natural error_type; the incident reduces to `symptom + where`, as expected.
- **Cases:** write the first line **at create time**. `recurrences` (frontmatter) is the **authoritative lifetime count**; the `## Cases` list keeps only the **most recent N lines** (order of single digits ~ a dozen) — so line count ≤ `recurrences`, and `recurrences` wins when they differ.
- **One file per topic.** A recurrence appends a Case line (with its session date) **and** bumps the `recurrences` frontmatter counter. **Landing does this automatically** on a clear same-incident match (deterministic `--match-signature` first; ambiguous → asks); `recurrences` renders into the INDEX row as `recur: N`, so the count is visible without opening the file. On a regression (a `status: obsolete` incident recurring), landing revives it: flip back to `active`, clear `resolved_by`, mark the Case "regression — original root-fix no longer holds", and keep accumulating `recurrences` (never reset).
- **Forbidden root causes**: "forgot", "careless", "didn't notice", "rushed". These hide the real model error.
- **Status field** (`active` / `stale` / `obsolete` — stale=pending-review (suspected outdated, or new-but-unverified, distinguished by the verify field); obsolete=dead, awaiting-archive drain state):
  - `active` — still applies to the current codebase
  - `stale` — auto-flipped by the ritual when a `when_to_update` condition is matched (suspected-outdated), or set at write time when a `verify` field is present (unverified new output); needs author review before flipping back to `active`
  - `obsolete` — the underlying constraint no longer exists (framework upgraded, code removed); landing drains it to `archive/` (knowledge analog of workflow `done`)
- **Promotion path**: incident reports promote in two stages — first to `checklists/` (after a 3-criterion gate at `landing`), then to project agent rules (only if the checklist is also ignored and the incident continues to recur). Full gate criteria in [protocol.md § Incident promotion gates](protocol.md#incident-promotion-gates).
- **Frontmatter `when_to_read` + `applies_to` are REQUIRED** (not optional). An incident report without them fails the routing check and is reported as a hanging task. They let AI grep for relevance without loading the full file — same pattern as skill SKILL.md `description`. Examples:
  - `when_to_read: "before designing a recursive parser"` / `applies_to: [parser, recursion, stack-depth]`
  - `when_to_read: "before adding a new migration"` / `applies_to: [migration, schema, postgres]`
  - Keep tags **short and concrete** — `[parser, recursion]` beats `[code-quality, architecture]`. Generic tags don't help AI choose.
  - **Path entries opt into stale detection** — an `applies_to` entry containing `/` (e.g. `src/parser/lexer.py`) is treated as a source path and prefix-matched against changed paths at landing; tags-only = no stale detection for this artifact.
- **Frontmatter `last_updated`**: bump on every meaningful change (Case append / status flip / advice rewrite). Lets AI judge staleness: a `last_updated` 2 years ago about a removed module is probably obsolete — promote to `status: obsolete` or delete. Lets users sort by recency when triaging.

---

## checklist body

```markdown
# <topic> checklist

## When to follow this

<2-3 line description of the situation this checklist handles>

## Steps

1. <command or check>
2. <command or check>
3. ...

## Verification

- <how to confirm each step worked>

## Common pitfalls

- <known trap and how to avoid it>
```

### Rules

- **One file per topic** (e.g. `verify.md`, `release.md`, `re-fixture.md`).
- **Frontmatter `when_to_read` + `applies_to` are REQUIRED** (not optional). A checklist without them fails the routing check — same hard-fail rule as incident reports. See [protocol.md § Frontmatter requirements](protocol.md#frontmatter-requirements-hard-fail).
- **Frontmatter `last_updated`**: bump every time the checklist content actually changes (not for typo fixes). Lets AI / users judge staleness: a build checklist last touched 2 years ago in a fast-moving project is suspect.
- **Promotion rule**: a process becomes a checklist **on the second occurrence**. First time is ad-hoc; second time is the pattern worth recording.
- **No date prefix** — checklists are stable resources, not log entries.

---

## spec body (idea stage)

```markdown
# <rough idea>

<one-line gist; flip status idea → active when it's worth starting>
```

### Rules

- An idea-stage spec (`status: idea`) is a one-liner — no date prefix, no `implements:`. Starting it = flip `status: idea → active` (auto-adds the `YYYY-MM-DD-` prefix); a fuller design body grows in once active.
- If an idea has been sitting > 6 months and no trigger has fired, **delete it** (git log keeps the history; note the reason in the commit body). An idea that never finds its moment is not high-signal.

---

## External review feedback (no template)

There is **no debrief template** — `debriefs/` was removed. External review feedback is transient: keep the raw text in project-root `tmp/` (gitignored), then fold the **disposition** (adopt / reject / defer) into the reviewed spec's own `## Review notes` section. The raw feedback is discarded once dispositioned. See [folder-semantics § External review feedback](folder-semantics.md#external-review-feedback-no-folder).

---

## cockpit.md

```markdown
# Cockpit — <project>

Updated: YYYY-MM-DD · <who> · Stage: <lifecycle stage>

Focus: <one coarse thread label, ≤~100 chars> → <current spec/plan link>

Pointers: config → rules.md · conventions → <file> · artifacts → folder INDEXes · history → archive/

## Next

<single concrete next action> → <plan link>   (progress detail lives in the plan's ## Progress)

## In Progress

<!-- AUTO:inprogress -->
- [<spec/plan>](<path>) — <truncated summary head, ≤80 chars> [note: <if present>]
<!-- /AUTO -->

## Key Context

- <load-bearing literal a next session needs to resume; or - (none)>

## Pending Review

- <[topic] what changed · how to verify → after verification passes: how to commit / next step. Drains when reviewed. Or - (none)>

## Hanging Tasks

- [ ] <open item blocking a clean landing>
```

### Rules

- **`Updated` is a freshness stamp, not a changelog** — `Updated: <date> · <who> · Stage: <stage>` only. **No "what I did this session" narrative** — history is `git log` + the commit message + the spec/plan body. (Field roles are authoritative in [exit-ritual § Cockpit update](exit-ritual.md#cockpit-update--what-changes); this template only fixes shape + caps.)
- **`Focus` is one coarse thread label + a link** — `Focus: <label> → <current spec/plan link>`, ≤~100 chars. **No goal / criteria / method / invariants** — those live in the spec body (durable invariants → `rules.md`). It is the coarse session thread; `## Next` is the fine concrete step.
- **`Pointers` is thin navigation, hand-maintained (not AUTO)** — only jump anchors (config / conventions / folder INDEXes / archive), never content; the content lives at the target. Omit the line if a deck has nothing worth pinning.
- **`## In Progress` is an AUTO region** — derived from every `status: active` spec/plan (same `<!-- AUTO -->` mechanism as INDEX, regenerated by `status` / `landing`). **Do not hand-edit** it; a hand edit is overwritten on the next regen. The literal marker is `<!-- AUTO:inprogress -->` … `<!-- /AUTO -->` (`flightdeck_index.py` emits exactly this string). Each row mirrors the INDEX row format but renders a **truncated summary head** (≤80 chars + ellipsis; full text stays in the spec); if a file carries `note:`, append `[note: …]`.
- **`## Next` is the next concrete *single* action + a plan link** — AI-maintained, auto-written at landing (and on `idea→active` / a milestone). Keep it to one step; **progress checklists, rationale/citation lists, and milestone links belong in the plan's `## Progress`**, not here (they are not loaded every ritual). The user adjusts it by directing the AI, not by hand-editing.
- **`## Key Context` is the recovery slot — agent-judged, not AUTO.** The load-bearing literals a *next* session needs to resume: the file path under edit, a failing test name, an error string, a key function/value. Same maintenance model as `## Next` (AI-written at checkpoint/landing, not script-generated). Keep it to **literals, not prose**; nothing to carry → `- (none)`. Distinct from a knowledge artifact's body (that is durable knowledge; this is cockpit's transient resume hint) — both stress load-bearing literals, different layers.
  - **Per-entry drain (apply at landing).** An entry is **cleared** when the literal it points to no longer needs carrying forward: its target has been archived, has graduated into `docs/`, or the next session simply won't need it. An entry is **shrunk** when it has grown past a literal: a long entry collapses to a one-line pointer (link + hook); two same-source entries merge into one. The 80-line cap below is the ceiling, not the discipline — prune per-entry first.
- **`## Pending Review` is the sign-off queue — agent-judged, not AUTO.** Things the AI completed and self-judged done but you haven't eyeballed/approved yet (fits the AI-drives-autonomously, you-check-in-periodically loop). Each row: `- [<artifact/topic>] <what changed · how to look/verify> → after verification passes: <how to commit / next step>` — recording the post-verify action makes recovery **board-only** (next preflight knows what to do once you sign off, without the conversation). **Non-blocking** (you can land with items still queued — unlike `Hanging Tasks`) and **subjective** (human sign-off — unlike `verify:`, which is an objective run/test). It is also the home where landing surfaces a stale-knowledge `pending-review` note (a `stale` artifact awaiting your re-review), and it feeds the soft-landing/landing banner's `[Pending]` field when non-empty ([protocol § Act-report-close loop](protocol.md#act-report-close-loop)). **Drain:** an item is removed when you sign off, or at the next landing once you confirm; nothing queued → `- (none)`.
- **Accumulator-drain principle.** Every non-AUTO section that *accumulates* (`Key Context`, `Pending Review`) MUST have an explicit drain condition, or it rots into a junk drawer. Draining is a judgment step, so it runs at **landing** (which already rewrites cockpit by judgment), not at the mechanical checkpoint. `walkaround` only flags a suspected-stale / oversized `Key Context` as a non-blocking INFO — it never drains.
- **Length cap + role-creep check.** 80 lines is the hard ceiling — past it, trim immediately. Beyond line count, each field has a soft cap and a role (no changelog in `Updated`, no goal/criteria in `Focus`, no progress checklist in `## Next`); the authoritative per-field density + role-creep check runs at landing — see [exit-ritual § Length check](exit-ritual.md#cockpit-update--what-changes). `## In Progress` is AUTO and usually short; piled-up `active` is itself a focus-loss signal (walkaround INFO, never blocks).
- **Keep `summary` short — it is a row descriptor, not an abstract.** `summary` feeds both the folder INDEX and cockpit `## In Progress` (both loaded every session); keep it to ≤~1–2 lines / ~200 chars. In Progress renders only a truncated head, but a bloated `summary` still costs in the INDEX.
- **`Focus` is current state**, not history.
- **Hanging Tasks block landing** — resolve, or explicitly defer with a date.
- **History does not live in cockpit.** Durable record = the `archive/` folder + `git log`. A landed artifact leaves `## In Progress` automatically; it is not logged in cockpit.
- **No metric tracking duplicated elsewhere** — link to the single source.
- **No version stamp in cockpit.** The deck-conformance version lives in `rules.md` `version:` and is managed by `walkaround`. cockpit is pure focus.

---

## Cross-folder reference syntax

When one file references another, use a markdown link with a one-word hook:

```markdown
Known trap: [v2-aelayer structure](incidents/v2-aelayer-structure.md)
Procedure: [verify before commit](checklists/verify.md)
Decision: [why we chose splice over rewrite](archive/specs/2025-12-01-write-strategy.md)
```

Why this matters:
- The reader (human or AI) can jump straight to the source of truth.
- Single authoritative location — no duplication.
- When the linked file moves, the broken link is visible and fixable.

**Forbidden**: pasting facts inline that exist elsewhere ("we use splice not rewrite because..."). Link, do not copy.

---

## Spec evolution markers (optional convention)

When amending a long-lived spec — especially **backlog specs** that gain items over multiple sessions, or **specs revised after review disposition** (external feedback folded into the spec's `## Review notes`) — mark new / modified / removed items with prefix tags so the change history is grep-able and merge-friendly:

- **`ADDED:`** — new item or section.
- **`MODIFIED:`** — existing item changed. Note the old + new state inline if the change isn't self-evident.
- **`REMOVED:`** — item dropped. Strike-through (`~~text~~`) or comment-out rather than deleting outright, so the audit trail survives.

Example from a revised backlog spec:

```
- ADDED: B7 — cache layer with TTL on read-heavy endpoints.
- MODIFIED: B3 — switched from polling to webhook (was: 5s poll loop).
- REMOVED: ~~B5 server-side rendering~~ (rejected after benchmarks; rejected approach noted in commit log).
```

### Rules

- **Optional.** Small one-shot specs (single-session, no review round) don't need delta markers. The cost of adding them outweighs the benefit at that scale.
- **Apply only to substantive changes.** Typo fixes don't earn a marker; an item's scope shifting does.
- **REMOVED keeps history.** Strike-through preserves the audit trail; outright deletion makes it impossible to see "what we considered and rejected". The audit trail is the whole point.
- **Markers compose with `status:` frontmatter.** A spec can be `status: active` (with a `note:` blocker reason) AND have an `ADDED:` line in its body. Status applies to the artifact; markers apply to items within.
