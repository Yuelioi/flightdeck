# Publish Flightdeck v3.0.0-alpha.7 plan

## Preparation

- [x] [Prepare the release candidate input](slices/01-prepare-release-candidate.md)

## Delivery

- [x] [Create the one-commit release candidate](slices/02-create-release-commit.md)
- [x] [Verify the release candidate](slices/03-verify-release-candidate.md)
- [x] [Publish the verified release](slices/04-publish-release.md)

## Acceptance

- [x] The release commit is based directly on the fetched `origin/main` and has the exact accepted
  feature tree.
- [x] All release gates pass against the release commit before remote mutation.
- [x] Authorized obsolete local refs are removed without rewriting history or pruning objects.
- [x] `main`, tag `v3.0.0-alpha.7`, and the configured publication surface expose the verified
  release.
