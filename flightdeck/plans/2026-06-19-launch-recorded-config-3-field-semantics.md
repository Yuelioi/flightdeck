---
status: active
summary: Phase 3 of launch-recorded-config: wire the recorded rules.md frontmatter fields as direct reads — agents_md (auto|off) replaces landing's AGENTS.md file-existence probe (a deliberate compat break: emit-agents-md becomes one atomic action that regenerates the file AND flips the field to auto), and the runtime broken->hard-fail path is confirmed across the rituals; plus the one-time dogfood rules.md field stamp. Prose + one config edit, no Node/parity work.
last_updated: 2026-06-19
implements: specs/2026-06-19-launch-recorded-config.md
---

# Launch-recorded config — Phase 3: field-read semantics

> **For agentic workers:** implement task-by-task; each task carries its own verification gate. Steps use checkbox (`- [ ]`) syntax for tracking. This phase is **prose + one config edit** — no scripts change, no Node/parity work.

**Goal:** Make the two recorded `rules.md` frontmatter fields (`runtime`, `agents_md`) *behaviorally live* — read directly, never re-inferred (spec §5). The headline change is `agents_md`: landing stops **probing whether an `AGENTS.md` file exists** and instead **reads the recorded intent** (`auto` → regenerate; `off` → leave it). `/flightdeck:emit-agents-md` becomes **one atomic bootstrap action**: regenerate the file **and** flip the field to `auto`. The `runtime` broken→hard-fail path (protocol rule landed in Phase 2) is confirmed reachable from every script-calling ritual. Finally the dogfood deck's own `rules.md` is hand-stamped with the two fields (spec §6 — no migration script; one deck, done by hand).

**Compat break (deliberate, spec §5):** the semantics shift from *"look at file reality"* to *"look at recorded intent"*. A user who hand-deletes `AGENTS.md` while `agents_md: auto` will see it regenerated next landing (the file-deletion is no longer a stop signal). This is an accepted sharp edge — the field is visible in the pick-list / frontmatter, and editing `agents_md` (or re-running emit-agents-md) is the alignment lever. We do **not** add a "re-probe the file" bypass — that is exactly the inference being deleted.

**Out of scope (spec §3.4 — stays judgment, not a field):** knowledge classification, needs-verify, archivable, the `## Next`-empty fallback. Phase 4 (version bump) is its own plan.

---

## What "field read" means here (the resolution chain)

`agents_md` and `runtime` already resolve at **step 1** of [protocol § Rule resolution order](../../skills/preflight/protocol.md#rule-resolution-order) (frontmatter field, read directly). Phase 2 wired `runtime` dispatch + the broken→hard-fail rule into that section. Phase 3's remaining work is to **delete the competing inference path** for `agents_md` (the `AGENTS.md` file-existence probe that still lives in resolution-order step 3 + templates) and make `landing` / `emit-agents-md` honor the field.

| Field | Old (inference) | New (field read) | Touched by |
|---|---|---|---|
| `agents_md` | landing probes "does `AGENTS.md` exist?" → regen iff present | read `agents_md`: `auto`→regen, `off`→skip; emit-agents-md flips `off→auto` atomically | protocol.md, templates.md, landing, emit-agents-md |
| `runtime` | (Phase 2) per-session probe `uv/python/node` | read field → dispatch call form; missing→hard-fail | protocol.md (done P2); confirm each ritual references it |

---

## File structure (this phase touches)

| File | Responsibility | Action |
|---|---|---|
| `skills/preflight/protocol.md` | Rule resolution order | **modify**: drop the `emit_agents_md` file-probe from step 3 (Environment inference); `agents_md` is a step-1 field read |
| `skills/preflight/templates.md` | rules.md field reference | **modify**: rewrite the `emit_agents_md` bullet → `agents_md` field semantics (auto/off + the atomic emit-agents-md flip) |
| `skills/landing/SKILL.md` | landing step 9 | **modify**: gate AGENTS.md regen on `agents_md: auto` (no file-existence probe) |
| `skills/emit-agents-md/SKILL.md` | the emitter | **modify**: Step 0 reframe + a new step that flips `agents_md: off→auto` after writing; report the flip |
| `skills/walkaround/SKILL.md` | Audit 9 | **modify (light)**: read `agents_md` intent into the drift call (off+present / auto+absent are intent-vs-reality notes, not hard drift) |
| `flightdeck/rules.md` (dogfood) | this repo's own deck config | **modify**: stamp `runtime: uv` + `agents_md: auto` into frontmatter (spec §6 manual migration) |

> Verification class: **prose tasks** gated by `rg` (no-probe residue gone) + the English gate (`rg -lP '\p{Han}' skills scaffolds` empty) + the full pytest suite staying green + `flightdeck_lint` adding no new finding on the dogfood deck. No new parity test (no script changed).

---

### Task 1: protocol.md + templates.md — `agents_md` is a direct field read

Delete the surviving file-existence inference so `agents_md` resolves only as a step-1 frontmatter field.

**Files:** `skills/preflight/protocol.md`, `skills/preflight/templates.md`

- [ ] **Step 1: protocol.md Rule resolution order step 3.** Today step 3 reads *"Environment inference — `emit_agents_md`: does deck root already have `AGENTS.md`?"*. Remove the `emit_agents_md` probe (it is replaced by the `agents_md` field at step 1). Step 3 ("Environment inference") now has **no remaining entry** — collapse it: either delete the numbered item and renumber, or keep the heading with an explicit "(none — `runtime`/`agents_md` are recorded fields, `git` is a launch precondition)". Pick the renumber-and-delete option for a clean four→three list; keep the parenthetical git note somewhere in the section so the "git is a precondition, not a resolved item" fact survives.
- [ ] **Step 2: templates.md `emit_agents_md` bullet.** Rewrite line ~37 (`emit_agents_md → landing auto-regen only if deck root already has AGENTS.md; explicit command always creates`) to the field semantics: `agents_md: auto` → landing regenerates `AGENTS.md` when a rendered cockpit field changed; `agents_md: off` → landing never touches it; `/flightdeck:emit-agents-md` is the atomic bootstrap — it regenerates the file **and** flips the field to `auto` (so `off→auto` is a one-way intent record, never a per-run file probe). Keep the `runtime`/`agents_md` "recorded frontmatter fields" bullet (line ~36) consistent.
- [ ] **Step 3: Verify.** `rg -n 'does deck root already have|already have .?AGENTS|emit_agents_md.*exist' skills` → empty (no file-probe phrasing left). `rg -lP '\p{Han}' skills` → empty.

---

### Task 2: landing step 9 — gate regen on `agents_md: auto`

**Files:** `skills/landing/SKILL.md`

- [ ] **Step 1.** Rewrite step 9 (`Regenerate AGENTS.md if any cockpit field it renders changed this session … run /flightdeck:emit-agents-md`) to: **only when `agents_md: auto`** AND a rendered cockpit field (Focus / `## In Progress` / `## Next` / Hanging Tasks) changed this session → run `/flightdeck:emit-agents-md`; **`agents_md: off` → skip entirely** (do not probe for an `AGENTS.md` file, do not regenerate). State the field read explicitly so no reader reintroduces the file probe.
- [ ] **Step 2: Verify.** `rg -n 'agents_md' skills/landing/SKILL.md` shows the gate; full pytest green (landing has no test, but the suite must not regress); `rg -lP '\p{Han}' skills` empty.

---

### Task 3: emit-agents-md — atomic regenerate + field flip

The emitter becomes the single bootstrap path: it always regenerates, and it **records the intent** by flipping `agents_md` to `auto`.

**Files:** `skills/emit-agents-md/SKILL.md`

- [ ] **Step 1: Step 0 reframe.** Today Step 0 says the *"auto-regen only if AGENTS.md already exists"* rule applies to landing, not this command. Replace the file-existence framing with the field framing: this explicit command **always** regenerates regardless of field value; landing's auto-regen is gated by `agents_md` (Task 2). Keep the "explicit command is the only bootstrap path from a no-AGENTS.md start" point.
- [ ] **Step 2: Add the field-flip step (after Step 4 Write, before the determinism self-check).** After writing `AGENTS.md`, set `agents_md: auto` in `flightdeck/rules.md` frontmatter — the atomic bootstrap-intent record (spec §5: "create/regen the file AND flip the field to auto, no ordering dependency"). **Idempotent**: already `auto` → no-op; field absent → add it. This is a frontmatter edit (the skill edits `rules.md` directly; there is no script for it). Note it is a `rules.md` write, so the emitter is no longer read-only w.r.t. the deck — call this out.
- [ ] **Step 3: Report.** Add a line to the Step 6 report block: `agents_md: <was→now>` (e.g. `off → auto` on first bootstrap, `auto (unchanged)` thereafter).
- [ ] **Step 4: Verify.** `rg -n 'agents_md|already exist' skills/emit-agents-md/SKILL.md` shows the flip + no file-probe wording; `rg -lP '\p{Han}' skills` empty.

---

### Task 4: confirm `runtime` broken→hard-fail is reachable from every ritual

Phase 2 put the rule in [protocol § Rule resolution order](../../skills/preflight/protocol.md#rule-resolution-order) (Runtime dispatch paragraph). This task confirms each script-calling ritual *routes through* it — no new rule, just a reachability/pointer audit.

**Files (read; modify only where a pointer is missing):** `skills/landing/SKILL.md`, `skills/status/SKILL.md`, `skills/new/SKILL.md`, `skills/walkaround/SKILL.md`, `skills/launch/SKILL.md`

- [ ] **Step 1.** For each ritual, confirm its script-invocation prose says "call form per the recorded `runtime` ([protocol § Rule resolution order])" (added in Phase 2 for status/landing/new/walkaround/launch). Where a ritual invokes a script without that pointer, add the one-liner. Do **not** restate the hard-fail rule per-ritual (single source = protocol); a pointer suffices.
- [ ] **Step 2.** Confirm `preflight` (read-only) carries the `⚠ recorded runtime broken` non-blocking note path — it is stated in protocol § Runtime dispatch; if `skills/preflight/SKILL.md` runs a script step (e.g. `--verify-pending`) without acknowledging a broken runtime degrades to that note, add a one-line "(broken runtime → `⚠ recorded runtime broken`, continue read-only)".
- [ ] **Step 3: Verify.** `rg -n 'recorded runtime|per the recorded .?runtime' skills` shows the pointer in each script-calling ritual + the protocol rule; `rg -lP '\p{Han}' skills` empty.

---

### Task 5: stamp the dogfood `rules.md` fields (spec §6 manual migration)

This repo's own deck is the single deck that must carry the new fields for the reads to be live on it. No migration script — hand-edit (spec §6).

**Files:** `flightdeck/rules.md`

- [ ] **Step 1.** Add to the frontmatter (currently just `version: 3.0`): `runtime: uv` (this repo runs `uv run pytest` — uv is the reference runtime) and `agents_md: auto` (an `AGENTS.md` exists at repo root and landing has been regenerating it — `auto` preserves that behavior under the new field semantics). Resulting frontmatter: `version: 3.0` / `runtime: uv` / `agents_md: auto`.
- [ ] **Step 2: Steady-state priority reconcile (spec §2).** Scan the existing `### Rules` / `### Project conventions` prose for anything a field now governs (e.g. a sentence implying a runtime or AGENTS.md behavior). The current `### Rules` holds only the push rule and `### Project conventions` holds conventions — neither conflicts with the two fields, so this is a no-op confirm. Note it in the task close.
- [ ] **Step 3: Verify.** `uv run python scripts/flightdeck_lint.py flightdeck` → the `audit_settings` check (Phase 1) accepts `runtime: uv` + `agents_md: auto` as legal values (no new finding beyond the pre-existing `references/` dangling-refs). `node scripts/flightdeck_lint.js flightdeck` → same (parity). `flightdeck_index --check` still `clean`.

---

### Task 6: walkaround Audit 9 — read `agents_md` intent into the drift call (light)

**Files:** `skills/walkaround/SKILL.md`

- [ ] **Step 1.** Audit 9 compares a marker-bearing `AGENTS.md` against cockpit. Fold the field in (all **INFO**, walkaround never fixes): `agents_md: off` + `AGENTS.md` **present & drifted** → INFO "AGENTS.md present but `agents_md: off` (landing won't refresh it; run emit-agents-md or accept staleness)"; `agents_md: auto` + `AGENTS.md` **absent** → INFO "`agents_md: auto` but no AGENTS.md (next landing will create it)". Field-vs-reality is a heads-up, not a hard finding; keep it one or two sentences appended to the existing audit.
- [ ] **Step 2: Verify.** `rg -lP '\p{Han}' skills` empty; manual read of Audit 9.

---

### Task 7: Full-phase verification

- [ ] **Step 1: English gate** — `rg -lP '\p{Han}' skills scaffolds` empty.
- [ ] **Step 2: No-probe residue** — `rg -n 'does deck root already have|auto-regen only if|already have .?AGENTS' skills` empty (the file-existence inference is gone everywhere).
- [ ] **Step 3: Full suite (both interpreters)** — `uv run --with pytest pytest scripts/tests/ -q` green; `audit_settings` accepts the dogfood `runtime`/`agents_md` values.
- [ ] **Step 4: Lint adds nothing** — `flightdeck_lint flightdeck` (py + node) reports only the pre-existing vendored-`references/` dangling-refs; zero new finding on the touched skills + dogfood rules.md.
- [ ] **Step 5: Live field read on the dogfood deck** — run `/flightdeck:emit-agents-md`: it regenerates `AGENTS.md` and reports `agents_md: auto (unchanged)` (already auto); confirms the atomic flip is a no-op when already-auto and that the emitter honors the field path.
- [ ] **Step 6: Phase-3 done** — Tasks 1–6 committed + gates green → flip the phase plan `done` via `/flightdeck:status` (the ritual, not by hand). Phase 4 (version bump → `3.0.0-alpha.4` + CHANGELOG) is its own plan.

---

## Self-review (against the spec)

- **§5 `agents_md` field read replaces the file probe** → Task 1 (protocol + templates delete the inference), Task 2 (landing gates on the field), Task 3 (emit-agents-md atomic regen + `off→auto` flip). The compat break is stated, not hidden. ✅
- **§5 `runtime` broken→hard-fail** → the rule landed in Phase 2 (protocol § Runtime dispatch); Task 4 confirms reachability from every script-calling ritual + the preflight read-only `⚠ recorded runtime broken` note. No new rule, no restatement (single source). ✅
- **§2 steady-state priority (field > `### Rules` prose)** → Task 5 Step 2 reconciles the dogfood prose against the new fields (no-op here, but the check is the contract). ✅
- **§6 manual migration, one deck, no script** → Task 5 hand-stamps `flightdeck/rules.md`. ✅
- **§3.4 out-of-scope judgment knobs** → untouched (no field added for classification / needs-verify / archivable / Next-empty). ✅
- **No scripts change** → Tasks are prose + one frontmatter edit; `audit_settings` (Phase 1) already validates the field values, so the only "test" is the existing suite staying green + lint adding nothing. No new parity harness (nothing in the `.py`/`.js` twins changed). ✅
- **Placeholder scan** — every task names concrete files + the exact phrasing to delete/add; no "TBD"/"handle edge cases" left.
