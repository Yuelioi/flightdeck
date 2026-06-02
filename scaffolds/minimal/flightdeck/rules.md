---
version: 2.2              # REQUIRED — flightdeck release this deck conforms to; drives migration detection
git: true                 # false → skills skip all git reconcile/commit steps
emit_agents_md: true      # false → emit-agents-md refuses (no-op)
disabled_folders: []      # e.g. [charts, debriefs]
disabled_gates: []        # e.g. [debrief-disposition]
model_invocable: []       # rituals the model may self-invoke; [] = all manual (/flightdeck:<x> only). e.g. [landing]
status_auto: []           # optional status transitions the status skill may auto-apply; [] = none. add `start` / `land`.
---

## House rules

<!-- Free-prose project conventions every flightdeck skill must honor. -->
