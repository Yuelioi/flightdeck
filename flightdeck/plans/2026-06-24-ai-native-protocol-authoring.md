---
status: done
summary: Author the new preflight skill's two-layer protocol — a ≤3000-char always-loaded micro-core plus an on-demand deep protocol.md — in English, validated against the redesign spec (budget/coverage/overlap/section-mapping all green) with a 3.0→new coverage check proving zero load-bearing rule dropped without a spec 取舍. Drafts land in work/ai-native-redesign/, unwired (wiring = later sub-plan #4).
last_updated: 2026-06-24
implements: specs/2026-06-23-ai-native-redesign.md
verify: human-read work/ai-native-redesign/{micro-core,protocol,coverage-check}.md English prose for tone + sense before wiring into skills/preflight/ (sub-plan #4)
---

# AI-native Protocol Authoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author the new `preflight` skill's two-layer protocol — a ~1-page **micro-core** (loaded into context when `/flightdeck:preflight` runs) plus an on-demand **deep `protocol.md`** — in English, validated against the redesign spec, with zero overlap between layers and no load-bearing 3.0 rule silently dropped.

**Architecture:** Two Markdown docs that ARE the new preflight skill's protocol text. The micro-core is the ~1-page always-loaded layer (two verbs + layout + invariants + a pointer to depth). The deep doc holds the details the micro-core defers (write-gate examples, incident scope+crystallize, uses shadowing, vendoring, derived-listing). Both are drafted in a staging effort folder so the running 3.0 deck is untouched; wiring them into an actual Claude Code skill (`skills/preflight/`) is a **later** sub-plan, out of scope here.

**Tech Stack:** Plain Markdown. Verification via shell (`wc -m`, ripgrep `rg`) and checklist review against the spec. No build/test framework.

This is sub-plan **#1 of 5** for the redesign (others: migration script · derive-listing · kill-old-skills/rewire-plugin · productization). It is self-contained: its deliverable is the validated protocol prose, reviewable on its own.

## Global Constraints

Every task implicitly includes these. Values copied from the spec + project `CLAUDE.md` / `rules.md`:

- **Publish surface = English.** All protocol prose, headings, anchors, examples are English (these ship to all users). Chinese appears only in conversation / commit-message body — never in the authored docs.
- **Protocol lives in the plugin skill.** It is NOT pasted into `CLAUDE.md`, NOT injected at session start, NOT placed in `~/.flightdeck`. "Loaded" = the preflight skill's text enters context when invoked; "not injected" = nothing auto-loads without running `preflight`.
- **Two layers, zero overlap.** Each fact lives in exactly one layer (micro-core OR deep), never both — this is the zero-drift guarantee. The micro-core states an invariant in one line; the deep doc elaborates; neither restates the other's role.
- **Micro-core ≈ 1 page.** Hard ceiling: 3000 characters (`wc -m`). It must still hold every decision in spec §形态.
- **Routing-header labels are capped at three:** `SUMMARY`, `READ WHEN`, `RECHECK WHEN` (this convention governs deck knowledge files the protocol describes — not the protocol docs themselves).
- **Two manual commands only:** `preflight` (entry) + `walkaround` (audit). Everything else is automatic (folded into turn-end persist) or gone.
- **Do not re-derive the shape.** The spec `flightdeck/specs/2026-06-23-ai-native-redesign.md` is the authority. Copy its decisions verbatim; do not invent new structure.

**Source of truth (read-only reference):** `flightdeck/specs/2026-06-23-ai-native-redesign.md`

---

### Task 1: Micro-core draft

The spec appendix already contains an authored English micro-core. This task lifts it into a standalone file and verifies it against budget + coverage. Low-risk first task that locks the always-loaded layer.

**Files:**
- Create: `flightdeck/work/ai-native-redesign/micro-core.md`
- Reference: `flightdeck/specs/2026-06-23-ai-native-redesign.md` (appendix「协议微核心初稿」 + §形态)

**Interfaces:**
- Produces: `micro-core.md` — the always-loaded protocol. Task 2's depth pointer and Task 3's gap-check both consume it. Section anchors used downstream: `Two verbs`, `Layout`, `Invariants`, `Depth`.

- [ ] **Step 1: Create the effort folder and the micro-core file**

Create `flightdeck/work/ai-native-redesign/micro-core.md` with exactly this content (lifted from the spec appendix, with the self-referential "see appendix" removed and the depth pointer made canonical):

```markdown
# flightdeck (micro-core)

Two verbs:
- **preflight** (on request — you run `/flightdeck:preflight`): load this
  protocol, read `flightdeck/cockpit.md`, `rules.md` and `uses.md`, then walk the
  tree (`ls` + grep) for whatever the task needs. Default load = cockpit.md only;
  everything else is lazy. Nothing is injected and it never auto-fires — if you
  never run preflight this session, flightdeck isn't engaged (nothing
  auto-persists), and just looking around costs nothing.
- **persist** (automatic, turn end): rewrite `cockpit.md`, write knowledge in
  place, `git commit` the project repo. A **work** effort is done when you move
  it out of `work/` into the cold store; the project's git log records it left.

Plus one audit command — **walkaround** (on request): sweep the deck for drift
(cockpit vs reality, orphaned work, duplicate traps, missing routing headers). It
is the only trust-but-verify net; nothing mechanical self-corrects.

Layout:
    <project>/flightdeck/            warm tier — git-tracked, committed each turn
      cockpit.md   now — in-flight efforts · focus + next · open questions
                   (rewritten each turn, kept small)
      rules.md     project house rules — single file, read on preflight, stable
      uses.md      one global path per line that this project subscribes to
      work/        in-flight multi-step efforts (one file or one folder each)
      knowledge/   persistent — nested by domain; type via title line
    ~/.flightdeck/                   cold tier — plain global dir, NOT git
      knowledge/                     cross-project knowledge (consulted via uses)
      projects/<x>/                  this project's cold store: archive/ + ideas/

Invariants:
- **Location is state.** In the project = live; moved into `~/.flightdeck` = cold
  (done/parked). No status field: in `work/` = active, moved out = done.
  Knowledge (`knowledge/`) is *resident*, not work: present = valid, deleted =
  dead; it has no lifecycle. Nuanced states (blocked/reviewing/waiting) live in
  cockpit prose, not folders.
- **Routing header** (the one lightweight convention — no YAML schema). Every
  knowledge file opens with a header ended by `---`: a title (`# <title>`;
  pitfall `# ⚠ <title>`; checklist `# <X> checklist`), then `SUMMARY:` (one
  line), `READ WHEN:` (when to route here), and optional `RECHECK WHEN:` (what it
  tracks — re-verify when that changes). Below `---` is free-form body. Routing
  reads only the header (cheap); freshness = mtime + body + RECHECK WHEN.
- **Write gate.** Record only what will change how you act later, or that you
  will look up again. Skip: one-off logs; a build that merely passed; exploration
  that concluded nothing; a re-run that added nothing.
- **Zero-loss covers the recovery payload** (cockpit.md + rules.md + work +
  knowledge — all warm, all in git): persist commits the project repo every turn,
  and `cockpit.md` must answer what you're doing / where you are / next / open
  questions. The cold store is kept but unversioned — out of the guarantee.

Depth (read on demand): the plugin's deep protocol file
(`skills/preflight/protocol.md`) — write-gate examples, incident
scope+crystallize rule, uses shadowing, vendoring, derived-listing.
```

- [ ] **Step 2: Verify the page budget**

Run: `wc -m flightdeck/work/ai-native-redesign/micro-core.md`
Expected: ≤ 3000 characters. If over, tighten prose (do not drop a decision) and re-run.

- [ ] **Step 3: Verify coverage (every §形态 decision is present)**

Run each and confirm a hit:
```bash
rg -n 'preflight|persist|walkaround' flightdeck/work/ai-native-redesign/micro-core.md   # both verbs + audit cmd
rg -n 'rules.md|uses.md|work/|knowledge/' flightdeck/work/ai-native-redesign/micro-core.md  # full layout
rg -n 'Location is state|Routing header|Write gate|Zero-loss' flightdeck/work/ai-native-redesign/micro-core.md  # 4 invariants
rg -n 'Depth .*protocol.md' flightdeck/work/ai-native-redesign/micro-core.md   # depth pointer
```
Expected: all four commands return matches. Any miss = a dropped decision; add it back.

- [ ] **Step 4: Verify it carries NO deep detail (no overlap with the deep layer)**

Run: `rg -n 'for example|e\.g\.|first time you hit|snapshot|derive-listing' flightdeck/work/ai-native-redesign/micro-core.md`
Expected: NO matches. The micro-core states invariants in one line only; examples and elaboration belong to the deep doc (Task 2). If any match, move it to Task 2.

- [ ] **Step 5: Commit**

```bash
git add flightdeck/work/ai-native-redesign/micro-core.md
git commit -m "draft(redesign): micro-core protocol layer"
```

---

### Task 2: Deep protocol draft

The five details the micro-core defers. This doc is plugin/skill content read on demand — it is NOT a deck knowledge file, so it takes normal headings, **no routing header**.

**Files:**
- Create: `flightdeck/work/ai-native-redesign/protocol.md`
- Reference: spec §「knowledge/」, §「uses.md」, §「写门」, §「剩纯执行」(derive-listing)

**Interfaces:**
- Consumes: `micro-core.md`'s Depth pointer, which names exactly these five topics.
- Produces: `protocol.md` with five top-level sections (`## Write gate`, `## Incidents (traps)`, `## uses.md shadowing`, `## Vendoring`, `## Derived listing`).

- [ ] **Step 1: Create `protocol.md` with the five sections**

Create `flightdeck/work/ai-native-redesign/protocol.md`. Write each section to encode exactly the spec's decision, with the concrete examples the micro-core omits. Required content per section:

```markdown
# flightdeck — deep protocol

Read on demand when the micro-core's one-liners aren't enough.

## Write gate

The micro-core rule: record only what changes how you act later, or that you'll
look up again. Concrete calls:

- RECORD: a bug + its root cause; a decision and why; a reusable procedure; a
  trap you'd otherwise hit again.
- SKIP: "ran the tests, they passed"; "explored the API, found nothing useful";
  "reran the build after a flake"; a log of steps with no durable conclusion.
- Borderline → ask: would a future session, cold, act differently for having
  this written? If no, skip.

## Incidents (traps)

A trap is a knowledge file whose title opens `# ⚠ <title>`, living in the domain
it belongs to. No fingerprint, no recurrence counter.

- On hitting a pitfall: write a `# ⚠ <title>` trap, placed by **scope** — project-
  specific → project `knowledge/<domain>/`; general lesson → `~/.flightdeck/knowledge/<domain>/`.
- On hitting it again: grep finds the existing trap → re-read it, do NOT rewrite.
- Once the fix is stable: crystallize it into a same-domain checklist
  (`# <X> checklist`) and let the trap fade. Location encodes scope, not count.

## uses.md shadowing

`uses.md` is a plain list — one `~/.flightdeck/`-relative path per line (a directory
entry subscribes the whole subtree; `#` comments; no YAML). preflight folds these
global files/dirs into the routing tree alongside local `knowledge/`.

- Conflict on the same relpath: the **local file shadows the global one entirely
  (replace, not merge)** → deterministic, zero-maintenance, two preflights give the
  same result. To extend a global file, read both yourself; the file-level rule
  stays replace.
- A subscribed global path that's missing/renamed: preflight emits one soft
  warning and continues — it does not fail.

## Vendoring

References to `~/.flightdeck` make the repo non-self-contained. When you need the
repo portable or shippable, **vendor**: snapshot the referenced global file into the
repo as a copy (a frozen reference), and drop the `uses.md` subscription for it. This
is opt-in and on-demand — the default is live subscription, no copy.

## Derived listing

When walking the tree for routing and `ls` + filenames aren't enough to decide
relevance, run a transient `derive-listing <area>`: grep each file's routing
header and print a one-shot directory to context. It is **never written to disk**
— transient, zero-maintenance, zero-drift. The trigger is AI judgment, not a count
or threshold.
```

Expand each section's prose as needed to read naturally, but do not add facts beyond the spec, and do not restate the micro-core's verbs/layout/invariants.

- [ ] **Step 2: Verify all five topics are present**

Run: `rg -n '^## (Write gate|Incidents|uses.md shadowing|Vendoring|Derived listing)' flightdeck/work/ai-native-redesign/protocol.md`
Expected: exactly five section headers, matching the names in the micro-core's Depth pointer.

- [ ] **Step 3: Verify cross-layer consistency (depth pointer ↔ deep sections)**

Confirm the five topics named in `micro-core.md`'s Depth line (`write-gate examples, incident scope+crystallize rule, uses shadowing, vendoring, derived-listing`) map 1:1 to the five `##` sections in `protocol.md`. Fix either side until they match exactly.

- [ ] **Step 4: Verify no re-statement of the micro-core (zero overlap)**

Run: `rg -n 'Two verbs|Layout:|Location is state|Zero-loss covers' flightdeck/work/ai-native-redesign/protocol.md`
Expected: NO matches. The deep doc elaborates; it never repeats the micro-core's structural statements.

- [ ] **Step 5: Commit**

```bash
git add flightdeck/work/ai-native-redesign/protocol.md
git commit -m "draft(redesign): deep protocol layer"
```

---

### Task 3: Gap-check against the 3.0 prose

The redesign cuts a lot. This task proves nothing **load-bearing** was dropped by accident — every 3.0 rule is either carried into the new protocol or deliberately dropped with a spec 取舍 justifying it.

**Files:**
- Create: `flightdeck/work/ai-native-redesign/coverage-check.md`
- Reference (read): `skills/preflight/protocol.md`, `skills/preflight/exit-ritual.md`, `skills/preflight/SKILL.md`, `skills/landing/SKILL.md`, `skills/status/SKILL.md`, `skills/walkaround/SKILL.md`, `skills/_shared/bootstrap.md`; the new `micro-core.md` + `protocol.md`; spec §「接受的取舍」+ §「迁移」.

**Interfaces:**
- Consumes: `micro-core.md`, `protocol.md` (Tasks 1–2).
- Produces: `coverage-check.md` — a table mapping each 3.0 rule-category to its disposition. No code consumes it; it is the review artifact gating "nothing important lost."

- [ ] **Step 1: Enumerate the 3.0 load-bearing rule-categories**

Read the reference skill files and list every load-bearing rule-category. At minimum cover: status transitions (idea→active→done→archive→graduate→promotion); INDEX semantics + AUTO regions; the stage/land ritual; the write gate; Pending Review; Hanging Tasks; knowledge routing (`when_to_read`/`applies_to`); the sync/vendoring subsystem; conform/schema; cockpit fields; `emit-agents-md`.

- [ ] **Step 2: Write the disposition table**

Create `flightdeck/work/ai-native-redesign/coverage-check.md`. For each rule-category, one row: `| 3.0 rule | disposition | where |` where disposition ∈ {carried → new protocol section, automatic → persist, dropped → spec 取舍 §, replaced → new mechanism}. Example rows:

```markdown
# coverage-check — 3.0 rules → new protocol

| 3.0 rule | disposition | where |
|---|---|---|
| status transitions (idea→…→promotion) | dropped | spec 取舍: location=state; idea/done → ~/.flightdeck |
| INDEX + AUTO regions | dropped | spec: routing = grep + walk; cockpit free-form |
| stage/land ritual | automatic | micro-core: persist (turn-end) |
| write gate | carried | micro-core invariant + protocol.md §Write gate |
| when_to_read / applies_to | replaced | routing header SUMMARY/READ WHEN/RECHECK WHEN |
| sync/vendoring subsystem | replaced/dropped | uses.md subscription; vendoring on-demand (protocol.md) |
| emit-agents-md | dropped | spec 表1: protocol loaded by skill, not emitted |
```

Fill a row for **every** category from Step 1.

- [ ] **Step 3: Flag any orphan**

Run: scan the table for any row whose disposition is empty or "dropped" **without** a spec section reference.
Expected: zero orphans. Any 3.0 rule that is dropped with no spec 取舍 justifying it is a real gap — surface it (it may mean the spec or the protocol needs a fix) rather than inventing a justification.

- [ ] **Step 4: Commit**

```bash
git add flightdeck/work/ai-native-redesign/coverage-check.md
git commit -m "draft(redesign): 3.0→new protocol coverage check"
```

---

## Self-Review

- **Spec coverage:** §形态 (two verbs, layout, cockpit, work/, knowledge/, uses.md, zero-YAML routing header, location=state, write gate, two-layer protocol, cold/hot boundary) → micro-core (Task 1) + deep (Task 2). §接受的取舍 + §迁移 rules → gap-check (Task 3). Productization, migration script, derive-listing implementation, kill-old-skills → explicitly out of scope (later sub-plans).
- **Placeholder scan:** micro-core content is given verbatim (Task 1); deep sections give concrete content + examples (Task 2); gap-check gives the method + example rows (Task 3). No "TBD"/"add appropriate"/"similar to".
- **Type/name consistency:** the five deep topics named in the micro-core Depth pointer == the five `##` sections in Task 2 == the five names verified in Task 2 Step 2/3. Routing-header labels `SUMMARY`/`READ WHEN`/`RECHECK WHEN` match the spec and Global Constraints. File paths consistent across tasks (`flightdeck/work/ai-native-redesign/`).
