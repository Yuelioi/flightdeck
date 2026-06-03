---
status: active
summary: status advances only the executing artifact, so an implementing spec can land at pending while its plan is done
---

# `status` advances the plan but not its spec

The `status` skill targets exactly one artifact (the edited / executing one). Finishing or advancing a `plans/` artifact never advances the `specs/` artifact it `implements:`. Observed dogfooding 2.3: a spec sat at `pending` through its plan's whole `active → awaiting-review → done` run; the co-land cluster needed a manual spec→`done` nudge before the Land Routine would archive both cleanly.

**Revisit when**: touching the `status` skill's target-resolution (Step 2). Candidate enhancement: when flipping a plan to `done`/`awaiting-review`, *offer* to advance the spec it `implements:` — confirm-gated, never an automatic second-artifact flip (that would violate the one-artifact-high-confidence rule). Alternative: leave it to `landing` to reconcile a spec's status against its done plan.
