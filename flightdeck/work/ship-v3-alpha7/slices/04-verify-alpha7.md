# Verify the alpha.7 package and release tree

## Outcome

The source package, installed payload, documentation, manifests, links, and recovery behavior are
verified and the tree is ready for the separately authorized release procedure.

## Current

A fresh Codex thread loaded the reinstalled skill and recovered this Slice through Deck, Work page,
context, Plan, Next, and live Git state without loading unrelated Work or References. Skill and
plugin validators, Claude manifest validation, 72-file Markdown link and whitespace scans, the
Deck-to-Next recovery chain, runtime-surface checks, Codex reinstall, 18-file source/install
equality, and Standards and Spec re-review also pass.

## Next

None.

## Verification

- [x] Skill, Codex plugin, Claude plugin, and JSON structure validation.
- [x] Markdown prose links, trailing whitespace, and runtime-free payload checks.
- [x] Codex cachebuster reinstall and exact source/install tree equality.
- [x] Independent Standards and Spec review with all findings resolved.
- [x] Fresh-thread recovery using the reinstalled plugin.

## References

- [ADR implementation map](../references/adr-implementation-map.md) — decision-by-decision
  implementation and verification traceability.
