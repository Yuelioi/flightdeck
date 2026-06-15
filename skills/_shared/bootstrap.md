<EXTREMELY_IMPORTANT>
This project uses **flightdeck** — a `flightdeck/` deck is present at the project root.

**On entry (handoff):** before doing anything else, read `flightdeck/cockpit.md`
(`Active focus`, `## In Progress`, `## Next`) and the folder `INDEX.md` files, then report the
next step. You are already in handoff mode; the user does NOT need to type `/flightdeck:preflight`.

**On exit (end-of-turn):** an **execution turn** (you ran a flow or did real work) ends with
**exactly one soft-landing banner, last, after the prose** — `─── 🛬 soft landing ───` + key info
+ a "you can close anytime" line — so the user always has a visible safe-to-close signal. Scale the
body to the increment: **write-gated knowledge** (changes future behavior / a decision / referenced
repeatedly) → you MUST persist it + board state and report `[Saved]` (never answer-then-stop with the
increment unpersisted); **state-only** (board moved, no new knowledge) → checkpoint + one line; **no
new knowledge** → `[No change]` (an honest "nothing to save, board current"). Always carry `[Stage]`,
plus `[Pending]` when cockpit Pending Review is non-empty. A **pure conversation / clarification
turn** (no flow, no deck change) emits no banner. Full banner / reversible-action / undo / lifecycle
rules → protocol § Act-report-close loop.

**Board-sync:** the mechanical part (`## In Progress` + each `INDEX.md` AUTO region) is welded by the
turn-end hook — the *judgment* parts (entry handoff, knowledge classification, `## Next` /
`Active focus`) are always yours.

**Authoritative skills own their shape — DO NOT re-derive it.** When a skill declares itself the
authority for a product shape or flow (`/flightdeck:new` for artifact shape, `landing` for the wrap
ritual, `status` for transitions), you MUST NOT pre-read sibling files to "match format / learn style
/ verify naming" before invoking it — that is what the skill does for you. Supply only the input it asks for.

Details → `/flightdeck:preflight` skill / protocol.
</EXTREMELY_IMPORTANT>
