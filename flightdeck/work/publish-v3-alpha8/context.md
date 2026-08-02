# Flightdeck alpha.8 release context

## What matters

The release packages the already committed Knowledge playbook work and the proactive discovery fix
that have been exercised locally for several days. Release execution is authorized, including
release-metadata edits, commit, push, annotated tag, and GitHub prerelease publication.

## Constraints

- Continue the Version 3 alpha line as `v3.0.0-alpha.8`.
- Preserve the two existing focused commits; do not rewrite published history or squash local work.
- Treat `plugins/flightdeck/` as the source package and verify the installed Codex payload.
- Keep the Codex and Claude manifests plus the Claude marketplace version aligned at alpha.8; a
  Codex development cachebuster may use SemVer build metadata only while testing.
- Fetch and verify the remote base before any push, then publish only a fast-forward update.
- The public release is a prerelease and uses the alpha.8 changelog entry as its notes.

## Terms

- **Release commit:** The final version-alignment commit on local `main` after the two functional
  commits.
- **Installed payload:** The host-installed copy used to prove that package links and files survive
  installation rather than only working in the source tree.
