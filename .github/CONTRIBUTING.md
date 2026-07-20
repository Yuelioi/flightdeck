# Contributing to Flightdeck

Flightdeck is intentionally small. Contributions should improve fresh-session recovery or reduce
the amount of process a human must maintain. Do not add a runtime, schema, generated index, routing
field, or parallel workflow state system without repeated real-world failures that the host's
normal file and Git tools cannot handle simply.

## Working on the skill

1. Read `../CONTEXT.md`, `../plugins/flightdeck/skills/flightdeck/SKILL.md`, and the relevant
   lifecycle reference.
2. Keep the main skill concise and disclose branch-specific procedure through references.
3. Keep the shared plugin self-contained; do not create host-specific copies without a real host
   difference.
4. Validate the skill plus both Codex and Claude manifests.
5. Reinstall the local plugin and forward-test behavior from a fresh prompt.
6. Update English and Chinese docs together when the user-facing contract changes.

The source of truth is `../plugins/flightdeck/`; it contains both host manifests and one shared skill.
Keep commits focused and imperative. Pull requests should state the user-visible change, recovery
scenario exercised, installed-plugin result, documentation impact, and any privacy or security
considerations.

## Decisions and support

Flightdeck uses a maintainer-led model. Routine skill and documentation improvements are decided in
review; changes to the Work model, plugin boundary, privacy expectations, or supported hosts need a
written design decision and fresh-session evidence. Only the maintainer publishes tags,
marketplaces, or releases.

Use repository issues for usage questions, reproducible skill behavior, documentation corrections,
host loading problems, and design proposals. Include the host version, natural-language request,
small synthetic deck, and actual files produced. Report vulnerabilities through
[the private security process](SECURITY.md), not a public issue. Support is best-effort and does not
include recovery of reasoning that was never written to a Work.

By contributing, you agree that your contribution is licensed under the repository's MIT License
and follows the [Code of Conduct](CODE_OF_CONDUCT.md).
