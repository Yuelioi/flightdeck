# Proactive Knowledge discovery context

## Observed problem

In alpha.7, agents commonly continue Work without inspecting relevant files under
`flightdeck/knowledge/`. Users must explicitly point the agent at the directory, which defeats the
playbook's purpose.

## Cause

The former rule said to search Knowledge only “when the current action raises a project-specific
practice question.” That decision was implicit and optional in practice: no recovery or start step
required the agent to evaluate Knowledge relevance or inspect the available subject/topic names.

## Decision

Starting, recovering, or materially changing a Work action triggers a bounded Knowledge check.
Relevant Work links are read first; otherwise the agent inspects subject/topic paths, searches
headings only within plausible subjects when needed, and reads clearly relevant guidance before
acting. Path inspection is routine, while unrelated document bodies remain lazy.

## Constraints

- Relevant Knowledge should be discovered without a user naming its directory.
- Discovery must remain bounded and relevance-driven; it must not preload every Knowledge document.
- Do not add indexes, registries, routing metadata, activation fields, or consultation receipts.
- Source skill, installed plugin behavior, English and Chinese documentation, format guidance, and
  architectural decisions must remain aligned.
