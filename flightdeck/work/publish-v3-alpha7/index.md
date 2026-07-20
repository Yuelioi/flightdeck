# Publish Flightdeck v3.0.0-alpha.7

## Goal

Publish the verified alpha.7 tree as one squashed `v3.0.0-alpha.7` commit based on the current
`origin/main`, then complete the authorized ref cleanup, fast-forward push, tag, and publication.

## Status

Open

## Current

Release preparation is complete against freshly fetched `origin/main` at
`7e0f7a8199adfa883b6f36bda13a050a6986a0bd`. The complete feature tree and six authorized local
cleanup refs are inventoried, the changelog is release-dated, and all pre-candidate gates pass. No
alpha.7 commit, tag, push, ref cleanup, or publication has yet been performed.

## Next

Create the direct-child squash commit described by the
[release commit Slice](slices/02-create-release-commit.md), preserving exact feature-tree equality.

## Progress

- Created a separate release Work without reopening the Finished implementation Work.
- Confirmed ADR-0022 is the release procedure authority and the user authorized its release steps.
- Fetched `origin/main`, bounded the cleanup set, and passed every pre-candidate validation gate.

## References

- [ADR-0022](../../../docs/adr/0022-alpha7-publishes-one-squashed-commit.md) — required commit,
  verification, cleanup, push, tag, and publication order.
- [Alpha.7 ADR implementation map](../ship-v3-alpha7/references/adr-implementation-map.md) — release
  inputs and completed implementation evidence.
- [Finished implementation Work](../ship-v3-alpha7/index.md) — immutable implementation handoff.
