# Verify the alpha.8 release

## Outcome

The exact release commit passes source, manifest, link, package-boundary, and installed-copy checks.

## Current

Release commit `34a4e95885588d3bf4b5af55a53f56d81727b181` passes whitespace and cleanliness
checks; four-file JSON and version alignment; strict Claude plugin and marketplace validation; 116
Markdown files with 210 local prose links; the 18-file runtime-free package boundary; exact
source/install SHA-256 equality; and fresh installed-plugin recovery.

## Next

None.

## Verification

- [x] Repository and Markdown checks pass.
- [x] Codex and Claude manifests plus marketplace metadata validate and align.
- [x] The plugin remains a self-contained Markdown-only package.
- [x] The installed Codex payload exactly matches the source package.
