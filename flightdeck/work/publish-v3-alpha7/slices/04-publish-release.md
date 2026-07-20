# Publish Flightdeck v3.0.0-alpha.7

## Outcome

The verified commit and tag are public, configured publication is complete, and only the explicitly
authorized obsolete local refs have been removed.

## Current

Not yet started.

## Next

After candidate verification passes, remove the authorized local refs, fast-forward `main`, push
it, create and push `v3.0.0-alpha.7`, perform the configured publication, and verify the remote
result.

## Verification

- [ ] Authorized obsolete local refs are removed without pruning objects.
- [ ] Remote `main` resolves to the verified release commit.
- [ ] Remote tag `v3.0.0-alpha.7` resolves to the verified release commit.
- [ ] The configured publication surface exposes v3.0.0-alpha.7.
