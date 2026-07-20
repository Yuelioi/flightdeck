# Verify the alpha.7 release candidate

## Outcome

The exact candidate commit passes every source, host, link, recovery, packaging, and installed-copy
gate required for alpha.7.

## Current

The exact release commit passed repository cleanliness and whitespace checks; Skill, Codex plugin,
Claude marketplace, and Claude plugin validation; five-file JSON and version alignment; 85-file
Markdown prose-link validation with 169 local targets; the 18-file runtime-free payload boundary;
and exact source/install equality.

## Next

None.

## Verification

- [x] Repository and Markdown validation pass.
- [x] Host manifests and package boundaries pass.
- [x] Source and installed Codex payloads are equal.
- [x] The candidate remains one commit ahead of the fetched `origin/main` with the expected tree.
