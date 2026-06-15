# Manifest verification PR

Use this template when reporting end-to-end behavioral verification of one of flightdeck's plugin manifests (Codex CLI / Cursor / Gemini CLI). Claude Code is verified by the maintainer; the others are open for community verification.

## What I verified

**AI tool**: <Codex CLI / Cursor / Gemini CLI / other>
**Tool version**: <e.g., Codex CLI 0.42.1>
**Flightdeck version**: <e.g., 1.2.0>
**Test date**: YYYY-MM-DD

## Scenarios from the release-gate spec

The full scenario specs are in `flightdeck/archive/specs/2026-05-23-v1.0-release-gate.md`. For each scenario, mark the result:

- [ ] **S1 — Cold-start in a project with `flightdeck/`**: AI reads `cockpit.md` first, reconciles against git, executes the first `## Next` item.
- [ ] **S2 — Bug + root cause → `incidents/`**: AI uses the incident template, banned root-cause language ("forgot" / "careless") absent, `status` frontmatter present.
- [ ] **S3 — Ambiguous classification**: AI applies first-match-wins heuristic or asks user with structured options.
- [ ] **S4 — Status + INDEX upkeep at landing**: AI writes `status:` frontmatter on each new/changed artifact and regenerates the affected folder's `INDEX.md` so it matches the files on disk.
- [ ] **S5 — Review feedback without disposition**: AI keeps raw feedback in project-root `tmp/` and folds its disposition (adopt / reject / defer) into the reviewed spec's `## 评审纪要`; if unable to dispose, adds a hanging task to `cockpit.md`; refuses clean landing until acknowledged.
- [ ] **S6 — Default-brainstorm trap**: AI <=1 brainstorm invocation, >=3 direct classifications.

Mark each `[x]` if pass, `[!]` with note if partial, `[ ]` if fail (and explain).

## Setup notes

How did you install flightdeck on this tool? (e.g., `gemini extensions install <repo-url>`, `/plugin install flightdeck@flightdeck-marketplace`, etc.)

Any setup friction?

## Transcript / evidence

Paste 2-5 short transcript excerpts showing AI behavior for the most interesting scenarios. Don't include full session dumps — just the moments that prove pass/fail.

## Manifest delta proposal (if any)

If you found a manifest field that should be added/removed/changed to make the tool work: describe it here. Maintainer will merge into `<.tool-plugin>/plugin.json` (or equivalent).

## What this PR proposes

- [ ] Update the capability x tool matrix in `flightdeck/archive/specs/2026-05-23-v1.0-release-gate.md` to reflect verification results
- [ ] (Optional) Patch the manifest based on findings
- [ ] (Optional) Add a tool-specific incident to `flightdeck/incidents/` if a host-specific bug was found

## Checklist

- [ ] I read the release-gate spec scenarios
- [ ] I ran on a fresh subagent / fresh session (no carry-over context)
- [ ] My evidence is reproducible from the manifest + a project with `flightdeck/`
- [ ] I've not embedded secrets / credentials in transcripts
