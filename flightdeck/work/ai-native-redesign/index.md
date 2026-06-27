# Index — AI-native redesign

## State

The AI-native reset is the active cutover work. The topic-package `index.md` handoff
migration has landed; the live tree now carries follow-up Codex cache-sync and mother-store
boundary work.

## Next

Verify, commit, and sync the plugin cache for the Codex cache helper plus mother-store
boundary updates. Continue release steps only after explicit user approval for CHANGELOG /
version bump / push.

## Read now

- skills/preflight/SKILL.md
- skills/preflight/concepts.md
- skills/preflight/operations.md
- skills/walkaround/SKILL.md
- README.md
- README.zh.md
- scripts/sync_codex_cache.ps1
- flightdeck/work/ai-native-redesign/plan.md
- flightdeck/knowledge/flightdeck/protocol/cockpit-bloat-topic-index.md
- flightdeck/knowledge/flightdeck/testing/local-plugin-testing.md

## Read if

- flightdeck/work/ai-native-redesign/design.md — if the active-package rationale needs
  archaeology.
- flightdeck/work/ai-native-redesign/coverage-check.md — if checking old AI-native spec
  coverage.
- flightdeck/work/ai-native-redesign/plans/stage-land-lifecycle.md — if revisiting the
  old stage/land lifecycle plan.

## Progress

Done:

- AI-native protocol core is live in `skills/preflight/` and `skills/walkaround/`.
- Routing headers are scanned eagerly and surfaced as In force / On call.
- Topic work package model moved from split `context.md` / `progress.md` toward a single
  topic `index.md` handoff board.
- Launch documents empty `work/` / `knowledge/` as future topic/domain homes, without
  creating sample content.
- Walkaround repairs malformed topic packages and root-level knowledge piles.
- The launch scaffold trap has been refreshed to the current scaffold path and contract.
- Cold-store semantics distinguish archived topic packages, parked idea seeds, and
  domain-routed global knowledge.

Current:

- Codex cache-sync helper, local-plugin-testing checklist update, and mother-store boundary
  protocol updates are uncommitted.
- Two Windows environment knowledge notes have been copied into global knowledge for
  cross-project discovery; active topic recovery still points only at local project files.

Verified:

- `git grep` found no remaining protocol recommendation to use `context.md` / `progress.md`
  as active entry files; remaining matches are legacy migration notes or unrelated paths.

Not done:

- Release notes / version bump / push, all gated by user approval.

## Open questions

- Release version is still undecided; current package version remains `3.0.0-alpha.5`.
- Push remains gated by user approval.

## Key facts

- Published surfaces stay English.
- User-facing deck content may stay in the user's language.
- Required active effort shape is now `index.md`; `design.md`, `plan.md`, and `plans/` are
  supporting files read only when the index points at them.
- Knowledge should live under `knowledge/<domain>/...`, not as a root-level pile.
- Launch copies `skills/launch/scaffold/flightdeck/` verbatim; keep that scaffold empty and
  pristine.
- Cold project storage distinguishes completed `archive/<topic>/` packages from light
  unstarted `ideas/<topic>/idea.md` seeds.
