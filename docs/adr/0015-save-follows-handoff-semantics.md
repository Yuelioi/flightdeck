---
status: accepted
---

# Save follows handoff semantics

Flightdeck saves only when the facts a fresh session needs have materially changed or before a Work
or session switch. Slice detail, Plan completion, Work-level Current/Next, stable context, and deck
navigation update at their own semantic boundaries; small edits, intermediate commits, and repeated
verification do not trigger ceremonial rewrites.
