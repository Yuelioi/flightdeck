# Manifest verification PR

Use this template when reporting end-to-end behavioral verification of one of flightdeck's plugin manifests (Codex CLI / Cursor / Gemini CLI). Claude Code is verified by the maintainer; the others are open for community verification.

## What I verified

**AI tool**: <Codex CLI / Cursor / Gemini CLI / other>
**Tool version**: <e.g., Codex CLI 0.42.1>
**Flightdeck version**: <e.g., 3.0.0-alpha.5>
**Test date**: YYYY-MM-DD

## Scenarios

For each scenario, mark the result:

- [ ] **S1 — Cold-start in a project with `flightdeck/`**: running `/flightdeck:preflight`, the AI reads `cockpit.md` first, glances at git, and reports the first `## Next` item without starting work.
- [ ] **S2 — Routing to knowledge**: a "why did X break?" prompt makes the AI walk `knowledge/<domain>/` and surface the matching `# ⚠` trap by its routing header — not a full-context dump.
- [ ] **S3 — Pitfall capture**: after hitting a pitfall, the AI writes a `# ⚠ <title>` trap under `knowledge/<domain>/` with a routing header (SUMMARY / READ WHEN) and a root cause.
- [ ] **S4 — Persist at turn end**: a turn that did real work rewrites `cockpit.md` to reflect now and makes one local commit; a pure-conversation turn commits nothing.
- [ ] **S5 — walkaround audit**: `/flightdeck:walkaround` surfaces drift (cockpit vs reality, orphaned `work/`, duplicate traps, missing routing headers) read-only, and fixes nothing.
- [ ] **S6 — Deckless launch**: in a directory with no `cockpit.md`, `/flightdeck:preflight` points to `/flightdeck:launch`, which seeds the skeleton (`cockpit.md` + `briefing.md` + `work/` + `knowledge/`).

Mark each `[x]` if pass, `[!]` with note if partial, `[ ]` if fail (and explain).

## Setup notes

How did you install flightdeck on this tool? (e.g., `gemini extensions install <repo-url>`, `/plugin install flightdeck@flightdeck-marketplace`, etc.)

Any setup friction?

## Transcript / evidence

Paste 2-5 short transcript excerpts showing AI behavior for the most interesting scenarios. Don't include full session dumps — just the moments that prove pass/fail.

## Manifest delta proposal (if any)

If you found a manifest field that should be added/removed/changed to make the tool work: describe it here. Maintainer will merge into `<.tool-plugin>/plugin.json` (or equivalent).

## What this PR proposes

- [ ] Update the compatibility matrix in [`README.md`](../../README.md#compatibility) to reflect verification results (`⚠️ untested` → `✅ tested`)
- [ ] (Optional) Patch the manifest based on findings

## Checklist

- [ ] I ran on a fresh session (no carry-over context)
- [ ] My evidence is reproducible from the manifest + a project with `flightdeck/`
- [ ] I've not embedded secrets / credentials in transcripts
