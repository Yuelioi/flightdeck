# Implement the Knowledge playbook model

## Goal

Implement ADR-0026 across the Flightdeck orchestration contract and public documentation, then
verify the exact installed plugin behavior without changing Knowledge content or adding runtime
metadata.

## Status

Finished

## Current

ADR-0026 is implemented across the orchestration contract and public documentation. All source and
package gates pass, the installed Codex payload exactly matches source, and a fresh thread verified
progressive recovery plus link-first, bounded Knowledge discovery.

## Next

None.

## Progress

- Preserved the Finished research, alpha.7 implementation, and release Works.
- Audited current product surfaces against ADR-0026 and isolated the implementation delta.
- Aligned orchestration and English/Chinese/format documentation with the complete model.
- Updated the Codex cachebuster through the plugin helper and reinstalled an exact 18-file payload.
- Verified in a fresh Codex thread that the installed skill selected only the relevant plugin
  Knowledge practice without preloading the library.
- Confirmed the alpha.7 Work model, lifecycle, and files under `flightdeck/knowledge/` did not
  change; only the Skill rules governing Work-to-Knowledge interaction and their documentation did.
- The first direct runner command rejected an unsupported approval flag without changing the
  repository. The corrected ephemeral runner completed after its outer wait was interrupted and
  wrote only the verified terminal Work state.

## References

- [ADR-0026](../../../docs/adr/0026-knowledge-is-a-demand-grown-project-playbook.md) — accepted
  Knowledge behavior.
- [Knowledge library audit](../define-alpha7-knowledge/references/knowledge-library-audit.md) —
  current eight-file disposition.
- [Research Work](../define-alpha7-knowledge/index.md) — accepted terminology and decision trail.
