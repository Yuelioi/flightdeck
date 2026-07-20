---
status: accepted
---

# Flightdeck assumes one top-level session

Flightdeck assumes that only one top-level AI session operates a repository at a time, avoiding
cross-session locks, claims, merge protocols, and compatibility behavior that the product's
Markdown source of truth cannot reliably provide. That session may coordinate child agents for
parallel work, but it remains responsible for consolidating their results into authoritative Work,
Plan, and Slice state; independently started top-level sessions are outside the supported model.
