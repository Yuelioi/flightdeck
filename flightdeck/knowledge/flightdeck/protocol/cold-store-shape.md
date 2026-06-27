# cold store shape

SUMMARY: Cold project storage should preserve completed topic packages in `archive/<topic>/`, keep parked ideas as light `ideas/<topic>/idea.md` seeds, and keep global knowledge domain-routed.
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
paths. Prefer compatibility first, then propose domain migration when a deck explicitly opts
in or walkaround can see the impact.
