# Align documentation, examples, and package metadata

## Outcome

Every public and host-facing surface teaches or identifies the same Version 3 alpha.7 product that
the shipped skill implements.

## Current

Complete. English and Chinese README files, the format and upgrade guides, changelog, example deck,
security policies, agent metadata, and Codex/Claude manifests now describe Version 3 alpha.7 and
the same Work, Plan, Slice, recovery, lifecycle, and routing semantics.

## Next

None.

## Verification

- All four JSON manifests and marketplace files parse successfully.
- The stale-contract scan finds old terminology only where migration history explicitly names it.
