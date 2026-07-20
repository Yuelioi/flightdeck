---
status: accepted
---

# Alpha 7 publishes one squashed commit

After alpha.7 is fully implemented and verified, a fresh release branch from the then-current
`origin/main` will squash the final feature tree into one `v3.0.0-alpha.7` commit, prove tree
equality, and rerun release gates before any authorized fast-forward push or tag. Only after that
verification will local v4/v5 feature, backup, and private Flightdeck refs be removed; no history
rewrite or object pruning occurs during development.
