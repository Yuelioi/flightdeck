# Publish Flightdeck v3.0.0-alpha.8

## Goal

Publish the locally exercised Knowledge playbook changes as `v3.0.0-alpha.8`, with aligned release
metadata, verified source and installed plugin payloads, a pushed `main` and annotated tag, and a
public GitHub prerelease.

## Status

Finished

## Current

Flightdeck v3.0.0-alpha.8 is published. Annotated tag `v3.0.0-alpha.8` and the public GitHub
prerelease expose verified release commit `34a4e95885588d3bf4b5af55a53f56d81727b181`, and remote
`main` contains that commit.

## Next

None.

## Progress

- Recovered the prior alpha.7 publication record and identified the two post-release commits.
- Selected `v3.0.0-alpha.8` as the next Version 3 prerelease.
- Aligned the three version surfaces and promoted the changelog entry with the 2026-08-02 date.
- Reinstalled Codex cache version `3.0.0-alpha.8+codex.20260802212946`; its 18-file payload exactly
  matches source and a fresh read-only session recovered this Work correctly.
- Verified release commit `34a4e95885588d3bf4b5af55a53f56d81727b181` across repository,
  manifest, link, package-boundary, installed-copy, and remote-availability gates.
- Atomically pushed `main` and the annotated alpha.8 tag, then published the GitHub prerelease.

## References

- [Forward-test skill behavior](../../knowledge/testing/forward-test-skills.md)
- [Keep installed skills self-contained](../../knowledge/skills/self-contained-packages.md)
- [Change every user-facing surface together](../../knowledge/documentation/change-all-surfaces.md)
- [Alpha.7 publication history](../publish-v3-alpha7/index.md)
