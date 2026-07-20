---
status: accepted
---

# Plan owns Slice completion

The Work page owns overall Current and Next, the Plan owns stage order and top-level Slice
completion, and each Slice owns only its internal steps, decisions, evidence, and handoff. This
deliberate split provides a readable rollup without recreating a map or duplicating Slice status.
Every Slice must be linked as an expanded Plan item; an unlisted `slices/` directory is an implicit
map and is not a valid recovery structure.
