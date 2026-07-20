# Flightdeck alpha.7 release context

## What matters

The release must publish the already verified alpha.7 product tree without reopening or extending
the Finished implementation Work. Release execution is authorized, including the commit, local ref
cleanup, fast-forward push, tag, and publication described by ADR-0022.

## Decisions

- The published history contains one `v3.0.0-alpha.7` commit whose parent is the then-current
  `origin/main` and whose tree matches the final feature tree.
- The release candidate is verified for tree equality and all release gates before any push or tag.
- Local v4/v5 feature, backup, and private Flightdeck refs are removed only after candidate
  verification succeeds.
- Development history is not rewritten and Git objects are not pruned.
- The Finished `ship-v3-alpha7` Work remains terminal and outside the Deck.

## Terms

- **Feature tree:** The complete repository state accepted for alpha.7, including the release Work
  documents required to carry this authorized procedure.
- **Release candidate:** The single squashed commit based directly on the fetched `origin/main`.
- **Publication:** The repository's configured release action after the commit and tag are pushed.
