# Ship Flightdeck v3.0.0-alpha.7

## Goal

Implement and verify the accepted Markdown-only, AI-first Flightdeck architecture, then prepare the
repository tree for the v3.0.0-alpha.7 release process.

## Status

Finished

## Current

The accepted alpha.7 architecture is implemented consistently across the orchestration skill,
branch references, templates, public documentation, examples, Knowledge, security policy, and
package metadata. All planned verification, including genuinely fresh-thread recovery through the
reinstalled plugin, passes. Every accepted ADR is linked to its implementation and verification
evidence. The tree is ready for the separately authorized release procedure.

## Next

None.

## Progress

- Recovered and accepted the 24 existing architecture decisions.
- Added the single-top-level-session boundary as ADR-0025.
- Audited the ADR corpus against the current repository and isolated implementation drift.
- Retired the finished v5 redesign Work whose rules contradict the alpha.7 design.
- Rewrote the skill contract, progressive branches, templates, docs, examples, and versioned host
  surfaces for alpha.7.
- Reinstalled Codex plugin `3.0.0-alpha.7+codex.20260720122656`; its 18-file payload matches source.
- Completed independent Standards and Spec reviews and resolved both reported consistency issues.
- Confirmed a fresh Codex thread recovers the focused Work through Deck, Work context, Plan, Next,
  and live Git state without loading unrelated durable material.

## References

- [ADR implementation map](references/adr-implementation-map.md) — traces every accepted decision
  to its implementation and verification evidence.
- [Architecture implementation review](references/adr-implementation-review.md) — accepted design
  consistency and the concrete implementation delta.
- [Implementation review](references/implementation-review.md) — final Standards and Spec findings
  plus their resolution.
- [Repository context](../../../CONTEXT.md) — canonical product language and boundaries.
- [Architecture decisions](../../../docs/adr/) — accepted alpha.7 decisions.
