---
git: true                 # false → skills skip all git reconcile/commit steps
emit_agents_md: true      # false → emit-agents-md refuses (no-op)
disabled_folders: []      # e.g. [charts, debriefs]
disabled_gates: []        # e.g. [debrief-disposition]
model_invocable: []       # rituals the model may self-invoke; [] = all manual (/flightdeck:<x> only). e.g. [landing]
status_auto: []           # optional status transitions the status skill may auto-apply; [] = none (core create→pending / finish→awaiting-review still auto). add `start` / `land`.
---

## House rules

<!-- Free-prose project conventions every flightdeck skill must honor.
     Delete this file entirely to use defaults (git on, emit on, all folders/gates active). -->
