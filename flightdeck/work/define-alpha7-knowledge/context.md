# Alpha.7 Knowledge design context

## Current facts

- Knowledge is project-wide, current, positive guidance reusable across future Work and organized
  as `flightdeck/knowledge/<subject>/<topic>.md`.
- Directory names, filenames, headings, and prose are the only current discovery surface; required
  metadata, kinds, activation rules, revisions, histories, and recheck ledgers are excluded.
- Recovery loads one Work progressively and leaves Knowledge lazy rather than preloading the
  library.
- Work owns goal-specific progress, context, Slices, and References. Root `CONTEXT.md` owns
  project-wide vocabulary, `docs/adr/` owns architectural decisions, and tests or validators own
  enforceable rules.
- Eight existing Knowledge documents state self-contained guidance for collaboration, documentation,
  plugins, skills, testing, Work recovery, and writing.

## Scope

This Work defines the semantic boundary and usage model for Knowledge. It may recommend later
documentation or skill changes, but the grilling phase does not modify the published alpha.7
contract before shared understanding is confirmed.

## Accepted decisions

- Knowledge's primary role is the project-level operating playbook: curated current positive
  guidance that helps future Work decide how this project approaches a recurring situation.
- Knowledge is not broad project memory, task history, architecture decisions, project vocabulary,
  or an enforceable rule store; those remain owned by Work, References, ADRs, root context, and
  tests or validators as appropriate.
- Work discovers Knowledge only when its current action raises a project-specific practice question.
  It reads an already linked Knowledge document first; otherwise it searches only the relevant
  subject, filenames, and headings. Recovery never scans or preloads the whole library.
- Knowledge advises Work judgment but does not mandate behavior or prove compliance. A Work may
  depart from it when the concrete situation warrants; rules that must be enforced belong in tests,
  validators, or repository instructions.
- A selected Knowledge document becomes a durable Work link only when a fresh session still needs
  the relationship. Put immediately required guidance in Next, continuing support in References,
  and leave ordinary consultations unrecorded. Never copy the guidance or create reading receipts.
- Promote a Work conclusion only when current evidence verifies it, another independent Work is
  reasonably likely to benefit, and it can be rewritten as self-contained project-specific positive
  guidance. Repetition in two separate Work is not a mechanical prerequisite.
- A Work that finds Knowledge contradicted by current reality owns immediate containment. Rewrite
  verified replacement guidance or remove only the disproven material and carry unresolved research
  in Work; Knowledge never keeps stale markers, versions, or recheck state.
- Each Knowledge file owns one independently searchable and applicable practice. Subject folders use
  natural project search terms and grow organically; split guidance that can be selected or changed
  independently, and do not add a fixed taxonomy, index, registry, or metadata catalog.
- Knowledge grows only from real Work conclusions that pass the promotion threshold. Alpha.7 does
  not pre-seed required subjects, empty folders, templates, or speculative starter guidance, and a
  missing subject is not itself evidence of a coverage gap.
