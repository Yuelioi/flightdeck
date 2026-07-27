# Restore proactive Knowledge discovery

## Goal

Make Flightdeck proactively discover and apply relevant project Knowledge during Work without
requiring the user to name `flightdeck/knowledge/` or restoring eager library loading.

## Status

Finished

## Current

Flightdeck now requires an explicit bounded Knowledge check before a newly started, recovered, or
materially changed Work action. The installed plugin matches source at
`3.0.0-alpha.7+codex.20260727123811`. Fresh-session checks proved both proactive relevant selection
and lazy irrelevant content.

## Next

None.

## Progress

- Replaced the implicit practice-question trigger with a mandatory path-first Knowledge check in
  the main skill and both Work start and recovery routes.
- Aligned root vocabulary, ADR-0026/0027, format guidance, the example, changelog, and English and
  Chinese READMEs.
- Validated the source skill, plugin, manifests, JSON, whitespace, and exact 18-file installed
  payload.
- In a fresh relevant session, inspected all eight topic paths, read exactly the four applicable
  skill/documentation/plugin/testing topics, and skipped the four unrelated bodies.
- In a fresh irrelevant fixture, inspected both available topic paths and read zero Knowledge
  bodies.

## References

- [Accepted Knowledge model](../../../docs/adr/0026-knowledge-is-a-demand-grown-project-playbook.md)
  — base Knowledge model, with discovery refined by ADR-0027.
- [Previous implementation Work](../implement-knowledge-playbook/index.md) — alpha.7 behavior and
  verification record.
- [Proactive discovery ADR](../../../docs/adr/0027-knowledge-discovery-is-proactive-and-bounded.md)
  — replacement for the implicit discovery trigger.
