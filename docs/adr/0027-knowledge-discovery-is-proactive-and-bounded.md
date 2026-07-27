---
status: accepted
---

# Knowledge discovery is proactive and bounded

Before executing a newly started or recovered Work action, Flightdeck inspects
`flightdeck/knowledge/` subject and topic paths without waiting for the user to identify the
library. Existing relevant Work links take priority. The current request plus Work Goal, Current,
and Next guide path selection; when names are insufficient, heading search stays inside plausible
subjects. Clearly relevant guidance is read before acting.

This refines ADR-0026's need-driven discovery trigger. Requiring the agent to first notice an
unstated “project-specific practice question” proved too implicit: agents often skipped Knowledge
entirely, making the playbook depend on manual user routing.

## Consequences

- Inspecting paths is a routine recovery and start step, while unrelated document bodies remain
  lazy.
- A missing or irrelevant library never blocks execution and never causes the agent to ask the
  user where Knowledge lives.
- Discovery remains metadata-free: no index, registry, taxonomy, routing field, activation rule,
  or consultation receipt is introduced.
