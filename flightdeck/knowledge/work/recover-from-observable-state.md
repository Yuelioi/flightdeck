# Recover interrupted work from observable state

A handoff can describe only what was saved. Conversation reasoning that never reached a file cannot
be reconstructed safely, and a stale handoff must not be presented as current truth.

After a suspected interruption, compare the Work page with repository status, diffs, commits,
relevant files, and test evidence. Preserve unrelated changes and mark uncertain ownership or lost
rationale as an open question instead of guessing. Rewrite the Work page's Current, Next, execution
pointer, and useful Progress from what the evidence proves; update current Slice detail and Plan
completion or order only when that evidence changed them, then continue.

Dirty state alone does not prove that the focused Work advanced.
