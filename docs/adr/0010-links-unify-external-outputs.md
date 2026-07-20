---
status: superseded by ADR-0011
---

# Links unify external outputs

Flightdeck cannot perfectly force every specialist skill, source change, temporary handoff, branch,
or issue-tracker artifact into one physical directory because their owning contracts and systems
control those locations. The producing location remains authoritative and the Work page, Plan,
Slice, or References section links it; `work/<id>/references/` is only the default when the producer
allows the caller to choose and the material belongs exclusively to that Work.
