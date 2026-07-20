# Publish Flightdeck v3.0.0-alpha.7

## Outcome

The verified commit and tag are public, configured publication is complete, and only the explicitly
authorized obsolete local refs have been removed.

## Current

Remote `main` and annotated tag `v3.0.0-alpha.7` resolve to verified commit
`e9fd9396ca7b8bb7e3afbd96189dd1e68a11916f`. The public GitHub prerelease was published at
<https://github.com/Yuelioi/flightdeck/releases/tag/v3.0.0-alpha.7>. The five authorized local
feature/backup branches and one private Flightdeck checkpoint ref were removed without object
pruning.

## Next

None.

## Verification

- [x] Authorized obsolete local refs are removed without pruning objects.
- [x] Remote `main` resolves to the verified release commit.
- [x] Remote tag `v3.0.0-alpha.7` resolves to the verified release commit.
- [x] The configured publication surface exposes v3.0.0-alpha.7.
