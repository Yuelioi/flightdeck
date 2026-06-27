# cockpit bloat belongs in topic index

SUMMARY: When cockpit starts carrying one topic's design, progress, key context, or read list, move that material into `work/<topic>/index.md` and keep cockpit as the project chooser.
READ WHEN: when cockpit becomes noisy, exceeds quick-scan size, or mixes project-level focus with one topic's detailed state
RECHECK WHEN: the topic work package shape or preflight recovery path changes

---

The failure mode is subtle: cockpit is supposed to recover the session, so adding more
details feels safe. Past a small threshold it becomes a second notebook, and the next
preflight has to parse global focus, topic state, design rationale, progress, read
dependencies, and blockers from one file.

The repair is structural, not editorial:

- `cockpit.md` says what can be resumed: focus, in-flight topic packages, project-level
  next, cross-topic open questions.
- `work/<topic>/index.md` says how to resume the chosen topic: state, next, read now, read
  if, progress, verification, blockers, and key facts.
- `design.md`, `plan.md`, and `plans/` hold long supporting material and are read only when
  `index.md` points at them.
- Reusable bugs, traps, and procedures still go to `knowledge/<domain>/...`, not to the
  topic index.
