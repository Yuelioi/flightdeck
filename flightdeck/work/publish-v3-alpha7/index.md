# Publish Flightdeck v3.0.0-alpha.7

## Goal

Publish the verified alpha.7 tree as one squashed `v3.0.0-alpha.7` commit based on the current
`origin/main`, then complete the authorized ref cleanup, fast-forward push, tag, and publication.

## Status

Finished

## Current

Flightdeck v3.0.0-alpha.7 is published. Remote `main`, annotated tag `v3.0.0-alpha.7`, and the public
GitHub prerelease expose verified commit `e9fd9396ca7b8bb7e3afbd96189dd1e68a11916f`. The authorized
obsolete local refs are removed, while history and Git objects remain intact.

## Next

None.

## Progress

- Created a separate release Work without reopening the Finished implementation Work.
- Confirmed ADR-0022 is the release procedure authority and the user authorized its release steps.
- Fetched `origin/main`, bounded the cleanup set, and passed every pre-candidate validation gate.
- Created and verified one direct-child squash commit with exact accepted-tree equality.
- Removed five obsolete local feature/backup branches and one private Flightdeck checkpoint ref.
- Fast-forwarded remote `main`, pushed the annotated alpha.7 tag, and published the GitHub
  prerelease.
- Recreated two initial local commit-tree attempts whose messages were malformed; both objects are
  unreferenced and intentionally remain unpruned.

## References

- [ADR-0022](../../../docs/adr/0022-alpha7-publishes-one-squashed-commit.md) — required commit,
  verification, cleanup, push, tag, and publication order.
- [Alpha.7 ADR implementation map](../ship-v3-alpha7/references/adr-implementation-map.md) — release
  inputs and completed implementation evidence.
- [Finished implementation Work](../ship-v3-alpha7/index.md) — immutable implementation handoff.
