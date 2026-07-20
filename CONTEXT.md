# Flightdeck repository context

Flightdeck preserves enough repository-local context for a fresh AI session to continue meaningful
work without relying on prior chat. The published Version 3 alpha line is a Markdown skill package,
not a workflow runtime; abandoned internal runtime experiments do not create a new release line.

## Product language

- **AI-first work desk:** A repository work system whose primary operator is an AI that decides when
  to recover, route, and save durable state. Human readability exists for audit and correction, not
  as a requirement that people manually operate every document.
- **Top-level session:** The single AI session operating a repository through Flightdeck at a given
  time. It may coordinate child agents, but it alone consolidates their results into authoritative
  Work state.
- **Deck:** The repository landing page containing one Open Work list, exactly one Focus marker,
  and stable project links. It operates only at Work granularity and never points to a Stage,
  Slice, Step, or commit.
- **Work:** An independently focusable goal with stable context and value outside any other Work.
- **Open Work:** A Work whose goal is unresolved and remains resumable whether or not it is focused.
  _Avoid_: Active Work, Paused Work
- **Finished Work:** A Work whose goal and applicable acceptance checks are satisfied.
- **Stopped Work:** A Work whose goal remains unsatisfied but has been explicitly cancelled,
  superseded, or judged no longer valuable. It remains in place with the reason recorded.
- **Work page:** The `work/<id>/index.md` recovery root and authority for the Work's Goal, lifecycle
  Status, Current truth, Next action, and current execution pointer. Progress, References, and
  temporary Work rules appear only when useful.
- **Work context:** The required `context.md` containing only stable goal-specific facts,
  constraints, decisions, and terms. Its internal sections are optional and it never carries live
  progress.
- **Plan:** The optional ordered checklist for a complex Work and the authoritative completion
  rollup for its stages and Slices. A Slice exists only as an expanded Plan item; the Plan does not
  repeat the Work Goal, current execution pointer, or Slice-level detail.
- **Slice:** A deliverable and verifiable unit inside a Work whose execution may span sessions or
  commits. It expands one linked Plan item, preserves detailed progress without becoming an
  independently focused Work, and rolls completion back up to the Plan.
- **Slice page:** The human-readable Slice document containing its Outcome, Current truth, and
  concrete Next action, plus only the optional detail that the Slice actually needs.
- **Slice ordinal:** The two-digit prefix that keeps Slice files in human execution order in common
  file explorers. It is a navigation aid, not status, identity, or revision metadata.
- **Decision Slice:** A Slice whose verified outcome is one route-shaping decision. Completing it
  does not imply that the decided implementation has been delivered.
- **Delivery Slice:** A Slice whose verified outcome is an implemented or otherwise delivered
  result.
- **Wayfinding:** An optional early phase for a Work whose Goal is clear but whose delivery route is
  not. It resolves one Decision Slice at a time and leaves unformulated in-scope uncertainty as
  Not yet specified instead of inventing a complete plan.
- **Step:** A concrete action inside a Slice with no independent handoff value.
- **Work rule:** A temporary execution constraint that must be visible on every recovery and may
  appear on the Work page. Stable facts and constraints belong in Work context instead.
- **Reference:** Supporting input or output with independent reading value, such as a design,
  audit, research result, or test matrix. A Reference does not own execution progress.
- **Natural location:** The authoritative location required by the producing skill, external system,
  or repository convention when the output cannot obey the Work Output Contract. Flightdeck links
  fallback material there instead of copying it.
- **Work Output Contract:** The routing contract that places supported document-producing skill
  outputs inside their owning Work. Source changes, external-system records, and unsupported outputs
  remain at their natural location and are linked as fallbacks.
- **Upgrade review:** A best-effort AI review that interprets an older or divergent workspace as
  evidence and reshapes it to the current model. It is guided by semantic questions rather than a
  version compatibility contract.
- **Recovery link:** One of at most three local links written directly into Next because the linked
  file is required to perform that action. Other links remain lazy supporting material.
- **Recovery:** Loading the selected Work page and context, its optional low-resolution Plan, at
  most three links required by Next, and the live Git state before continuing execution.
- **Knowledge:** The project-level operating playbook: curated, current, positive guidance reused
  across future Work to answer how this project should approach a recurring situation. It is not
  task history, broad project memory, an architecture record, a glossary, or an enforceable rule.
- **Save:** Rewriting only the visible Work documents whose recovery meaning materially changed.
  It is triggered by handoff semantics rather than edits or commits and is neither a log nor an
  automatic Git operation.
- **Focus:** The single marked entry in the deck's Open Work list selected for the next recovery.
  Focus is navigation, not lifecycle state.

## Product boundaries

- AI operation is the primary path. Users express intent in ordinary language; lifecycle verbs,
  output routing, recovery checks, and document maintenance are internal skill behavior.
- Flightdeck assumes one top-level session per repository at a time. Child agents may perform
  coordinated parallel work, but independently started sessions receive no locks, claims, merge
  protocol, or compatibility guarantees from Flightdeck.
- The shipped implementation is Markdown plus host manifests; there is no production JS/TS, MCP,
  CLI, schema, generated state, or private Git history.
- Flightdeck orchestrates supported specialist methods through the Work Output Contract. It does not
  relocate source changes or external-system records and does not duplicate fallback outputs.
- Git is the repository's history. Commits, pushes, tags, and publication follow explicit project
  policy rather than Flightdeck ceremony; Save never implies a Git operation.
- English is the primary release language; `README.zh.md` is the maintained Chinese counterpart.
