# coverage-check — 3.0 rules → new protocol

Proves nothing **load-bearing** was dropped by accident: every 3.0 rule-category is
either carried into the new protocol, folded into automatic persist, replaced by a
new mechanism, or deliberately dropped **with a spec section justifying it**.

- disposition ∈ {carried → new protocol section · automatic → persist · replaced →
  new mechanism · dropped → spec 取舍/迁移 §}.
- "where": micro = `micro-core.md`; deep = `protocol.md`; spec = the redesign spec
  (`design.md`, sibling in this effort folder) §接受的取舍 / §迁移 表1·2·3 / §形态.

| 3.0 rule-category | disposition | where |
|---|---|---|
| status transitions (idea→active→done→archive→graduate→promotion) | dropped | spec 表3 + §位置即状态: location = state, two states only (active/done); idea & done move to `~/.flightdeck` |
| status `done` as a staged state + status/landing seam | automatic | micro persist: a work effort is done when moved out of `work/` to the cold store |
| forward-only status state machine + transition authority table | dropped | spec 表3: no status field; location encodes active/done, nuance → cockpit prose |
| INDEX.md (per-folder + root) + AUTO regions | dropped | spec 表2: INDEX 全删; routing = grep + walk tree + routing header |
| stage / land ritual (Stage + Land Routine) | automatic | spec 表1 (stage/landing → persist); micro persist (turn-end: scan for knowledge, rewrite cockpit, commit) |
| write gate | carried | micro invariant **Write gate** + deep §Write gate (RECORD/SKIP examples) |
| Pending Review (cockpit field) | replaced | spec §位置即状态: fine-grained states (reviewing/waiting) → cockpit "open questions" prose, not a field |
| Hanging Tasks (block session exit) | replaced | spec §位置即状态: blocked/waiting → cockpit prose (no folder/field) |
| Key Context (cockpit AUTO-adjacent field) | carried | micro layout: cockpit = focus + next + open questions (free-form, no AUTO region) |
| cockpit `## In Progress` AUTO region | dropped | spec 表2: cockpit free-form, AUTO 区丢; in-flight efforts = whatever is in `work/` |
| knowledge routing via `when_to_read` / `applies_to` | replaced | routing header `SUMMARY` / `READ WHEN` / `RECHECK WHEN` (micro invariant **Routing header**); old `when_to_update` → `RECHECK WHEN` |
| folder = kind (specs/plans/checklists/docs/incidents/references) | replaced | spec 表2: `work/` (in-flight) + `knowledge/<域>` (by domain); type via title line (`#` / `# ⚠` / `# … checklist`) |
| `specs/` (idea, unstarted design) | dropped | spec 表3: cold `~/.flightdeck/projects/<x>/ideas/` (out of project view) |
| archived artifacts (`archive/`, done specs/plans) | dropped | spec 表2/3: cold `~/.flightdeck/projects/<x>/archive/`; git log records it left |
| stale detection (`when_to_update` + `applies_to` on-exit ritual) | replaced | spec §零YAML: no stale field; freshness = mtime + body self-judgement + `RECHECK WHEN`; deep §Derived listing for routing |
| incident recurrence counter + promotion gates (fingerprint, recur sweep) | replaced | spec 表3 + deep §Incidents: no count; scope-based placement; recurrence = grep finds existing trap, re-read not rewrite; crystallize stable fix → same-domain checklist |
| incident error-library / `resolved_by` / `status: obsolete` / tombstone | replaced | spec 表3: obsolete knowledge = delete (git keeps history) or move cold; no tombstone, no drain-to-archive |
| supersession model (`supersedes` / `related` frontmatter edges) | dropped | spec 表2: 所有 frontmatter 删; relations become prose links in the body |
| `verify` marker (self-asserting done, non-blocking debt) | replaced | spec §位置即状态: "needs verification" is a fine-grained state → cockpit "open questions" prose |
| sync / vendoring subsystem (boundary marker, fingerprint, consumers, fanout) | replaced/dropped | spec 表1 (sync → 消失) + deep §uses.md shadowing + §Vendoring: live `uses.md` subscription (local shadows global, replace not merge); vendoring opt-in on-demand |
| conform / schema (canonical field set, gofmt-for-deck) | dropped | spec 表1: no schema to conform (zero YAML) |
| `new` (artifact stamping: frontmatter, naming, INDEX regen) | automatic | spec 表1: folded into persist (no status field to stamp, no frontmatter to apply) |
| `emit-agents-md` (AGENTS.md AUTO region) | dropped | spec 表1: protocol loaded by the preflight skill, not emitted to AGENTS.md; no AUTO region |
| recorded-config (`version` / `runtime` / `agents_md` in rules.md frontmatter) | dropped | spec 表2: rules.md recorded-config 删 (no script runtime / schema to record) |
| `rules.md` Project conventions / House Rules | carried | spec 表2: `rules.md` kept as a single file, read on preflight, stable (micro layout) |
| nested knowledge domains / areas | carried | spec 表3 + micro layout: `knowledge/<域>/<子域>/…`, folder tree = hierarchy = index |
| rule resolution order / source-of-truth precedence (multi-tier config) | dropped | spec 表2 + §形态: rules.md single file collapses the multi-tier config; precedence无需 |
| act-report-close loop · reversible/irreversible gate · undo ("rollback") channel | dropped | spec §冷热两层: git/undo 载体连带出局 (single-user; undo scenario ~never); persist just commits each turn |
| brand glyphs per command (banner cosmetics) | dropped | spec §剩纯执行 产品化: command surface = 2 (preflight + walkaround); banner/scaffold cosmetics descoped to productization |
| naming iron-rule (metaphor vs mainstream) | carried | meta-rule, still honored: the new verbs (preflight / persist / walkaround) keep plain, mainstream-legible names |
| derived listing (routing when ls+filenames insufficient) | replaced | deep §Derived listing: transient `derive-listing <area>`, AI-judged, never written to disk |
| two-layer protocol (micro-core always-loaded + deep on-demand) | carried | spec §协议两层: micro-core (`micro-core.md`) + deep (`protocol.md`), zero overlap |
| zero-loss recovery payload | carried | micro invariant **Zero-loss**: cockpit + rules + work + knowledge, all warm, committed each turn; cold store explicitly excluded |

## Orphan scan (Step 3)

Every row above has a non-empty disposition, and every `dropped` row cites a spec
section (§接受的取舍 / 迁移 表1·2·3 / §形态 / §冷热两层 / §剩纯执行). **Zero orphans** —
no 3.0 load-bearing rule is dropped without a spec 取舍 justifying it.
