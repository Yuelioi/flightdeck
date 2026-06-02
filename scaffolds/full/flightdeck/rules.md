---
version: 2.2              # REQUIRED — flightdeck release this deck conforms to; drives migration detection
git: true                 # false → skills skip all git reconcile/commit steps
emit_agents_md: true      # false → emit-agents-md refuses (no-op)
disabled_folders: []      # e.g. [charts, debriefs]
disabled_gates: []        # e.g. [debrief-disposition]
model_invocable: [preflight, landing, walkaround, emit-agents-md, status]   # full-auto: AI may self-invoke every ritual. [] = all manual (/flightdeck:<x> only).
status_auto: [start, land]   # auto-advance optional transitions: start (→active) + land (archive done→landed/). [] = none (core create→pending / finish→awaiting-review still auto).
commit_mode: confirm         # landing's commit step: manual (never commit) / confirm (ask Y/n, default) / auto (no prompt). The one human checkpoint left in full-auto.
---

## House rules

<!-- Free-prose project conventions every flightdeck skill must honor.
     This deck ships full-auto (see model_invocable / status_auto above). To go manual,
     set model_invocable: [] and status_auto: []. rules.md is mandatory — do not delete it. -->
