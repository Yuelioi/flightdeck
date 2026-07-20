# Verify the alpha.7 release candidate

## Outcome

The exact candidate commit passes every source, host, link, recovery, packaging, and installed-copy
gate required for alpha.7.

## Current

Not yet started.

## Next

After the candidate exists, rerun the release gates against its exact tree and stop before any
remote mutation if a check fails.

## Verification

- [ ] Repository and Markdown validation pass.
- [ ] Host manifests and package boundaries pass.
- [ ] Source and installed Codex payloads are equal.
- [ ] The candidate remains one commit ahead of the fetched `origin/main` with the expected tree.
