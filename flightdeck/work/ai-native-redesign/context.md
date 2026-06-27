# Context — AI-native redesign

## State

The AI-native reset is the active cutover work. The live protocol has moved from a cockpit-as-notebook model to topic work packages: `cockpit.md` is the project index, and active topic recovery lives in `work/<topic>/context.md`.

## Next

Verify the topic-package protocol diff, then continue the gated release path only after explicit user approval for CHANGELOG / version bump / push.

## Open questions

- Release version is still undecided; current package version remains `3.0.0-alpha.5`.
- Push remains gated by explicit user approval.

## Key facts

- Published surfaces stay English.
- User-facing deck content may stay in the user's language.
- New active effort shape: `context.md`, `design.md`, `plan.md`, `progress.md`, optional `plans/`.
- Knowledge should live under `knowledge/<domain>/...`, not as a root-level pile.