# Publish Flightdeck v3.0.0-alpha.8

## Goal

Publish the locally exercised Knowledge playbook changes as `v3.0.0-alpha.8`, with aligned release
metadata, verified source and installed plugin payloads, a pushed `main` and annotated tag, and a
public GitHub prerelease.

## Status

Open

## Current

Freshly fetched `origin/main` remains at alpha.7 commit `e9fd9396ca7b8bb7e3afbd96189dd1e68a11916f`
and is an ancestor of local `main`. Alpha.8 version and changelog surfaces are aligned in the
uncommitted release tree. Source, manifest, link, package, reinstall, payload-equality, and fresh
recovery checks pass.

## Next

Create the release commit, then verify that exact commit through the [verification
Slice](slices/02-verify-release.md), following the project guidance for [testing the installed
plugin](../../knowledge/plugins/test-installed-copy.md).

## Progress

- Recovered the prior alpha.7 publication record and identified the two post-release commits.
- Selected `v3.0.0-alpha.8` as the next Version 3 prerelease.
- Aligned the three version surfaces and promoted the changelog entry with the 2026-08-02 date.
- Reinstalled Codex cache version `3.0.0-alpha.8+codex.20260802212946`; its 18-file payload exactly
  matches source and a fresh read-only session recovered this Work correctly.

## References

- [Forward-test skill behavior](../../knowledge/testing/forward-test-skills.md)
- [Keep installed skills self-contained](../../knowledge/skills/self-contained-packages.md)
- [Change every user-facing surface together](../../knowledge/documentation/change-all-surfaces.md)
- [Alpha.7 publication history](../publish-v3-alpha7/index.md)
