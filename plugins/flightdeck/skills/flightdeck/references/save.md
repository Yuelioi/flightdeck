# Save progress

A Flightdeck save rewrites the current handoff. It is not an event log and does not imply a Git
commit.

Save when recovery meaning materially changes, before switching Work or session, or at a durable
milestone. Do not rewrite documents merely because a small edit, test, or commit occurred.

1. Inspect the actual changes, verification, and live Git state.
2. Update the current Slice's Current, Next, decisions, steps, or evidence only when its local
   handoff changed.
3. Check completed Slice items in `plan.md` and adjust stage order only when the completion rollup
   changed. The Plan does not own Work Current or the current execution pointer.
4. Update the Work page's Current, Next, current execution pointer, and concise recent Progress when
   Work-level recovery meaning changed. Embed at most three immediately required local links in
   Next; keep all other useful links under References.
5. Update `context.md` only for stable goal-specific facts, constraints, decisions, or terms. Keep
   progress and session narration out of it.
6. Update the deck only for Work creation, Focus changes, or terminal lifecycle changes.
7. Add or revise Knowledge only for concise positive guidance reusable across future Work.

Before handing off, reread the dashboard as a fresh agent: it should reveal why the Work exists,
where it stands, what happens next, and which small set of files must be opened first.

Save edits Markdown only. Never stage, commit, push, tag, branch, or create a Git checkpoint unless
the user separately authorizes that Git operation.
