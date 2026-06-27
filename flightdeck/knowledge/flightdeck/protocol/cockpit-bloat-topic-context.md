# cockpit bloat belongs in topic context

SUMMARY: When cockpit starts carrying a topic's design, progress, and key context, split that material into `work/<topic>/context.md` / `design.md` / `progress.md` and keep cockpit as the project index.
READ WHEN: when cockpit becomes noisy, exceeds quick-scan size, or mixes project-level focus with one topic's detailed state
RECHECK WHEN: the topic work package shape or preflight recovery path changes

---

The failure mode is subtle: cockpit is supposed to recover the session, so adding more details feels safe. Past a small threshold it becomes a second notebook, and the next preflight has to parse global focus, topic state, design rationale, progress, and blockers from one file.

The repair is structural, not editorial:

- `cockpit.md` says where to go: focus, in-flight topic packages, project-level next, cross-topic open questions.
- `work/<topic>/context.md` says how to resume that topic: state, next, blockers, key facts.
- `design.md` holds why and tradeoffs.
- `progress.md` holds a compressed done/current/verified/not-done summary.
- Reusable bugs, traps, and procedures still go to `knowledge/<domain>/...`, not to topic progress.