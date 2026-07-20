---
status: accepted
---

# Slices are durable Work units

Complex Work keeps resumable execution detail in linked Slice documents instead of expanding
`plan.md` into a task log or relying on Git history to reconstruct semantic state. The Plan remains
the ordered overview, the current Slice is linked directly from Next, and no separate map duplicates
the Plan.
