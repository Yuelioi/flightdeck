# cold store shape

SUMMARY: Cold project storage should preserve completed topic packages in `archive/<topic>/`, keep parked ideas as light `ideas/<topic>/idea.md` seeds, and keep global knowledge domain-routed without making active topics depend on global paths.
READ WHEN: before changing archive / ideas / global knowledge semantics, or when migrating cold-store content
RECHECK WHEN: the topic work package shape or Subscriptions semantics changes

---

Cold storage is outside the zero-loss guarantee, so it must not become a second active
workspace. Its job is recovery-by-choice:

- `archive/<topic>/` keeps the whole completed topic package together for archaeology.
- `ideas/<topic>/idea.md` keeps unstarted work light so parked ideas do not look active.
- `~/.flightdeck/knowledge/<domain>/...` keeps reusable global knowledge routable the same
  way project knowledge is routed.

Do not bulk-move legacy global root files casually: other decks may subscribe to those exact
paths. When the affected live project briefings are visible through
`~/.flightdeck/projects/<slug>/`, it is reasonable to move root files into domains and repoint
those briefings in the same pass. Skip cold project slugs whose live briefing path no longer
exists rather than guessing.

Global knowledge is for discovery and standing cross-project behavior. Active topic recovery
should not depend on `~/.flightdeck/knowledge/...` paths: if a topic needs shared knowledge to
resume, materialize the relevant content into project-local `flightdeck/knowledge/<domain>/...`
and point the topic index there. That keeps the warm recovery payload self-contained even
when the mother store is reorganized.
