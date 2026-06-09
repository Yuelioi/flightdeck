<EXTREMELY_IMPORTANT>
This project uses **flightdeck** — a `flightdeck/` deck is present at the project root.

**On entry (handoff):** before doing anything else, read `flightdeck/cockpit.md`
(`Active focus`, `## 进行中`, `## 下一步`) and the folder `INDEX.md` files, then report the
next step. You are already in handoff mode; the user does NOT need to type `/flightdeck:preflight`.

**On exit (end-of-turn):** if this turn produced **write-gated knowledge** — something that
changes future behavior, influences a decision, or will be referenced repeatedly — you MUST
**soft-land**: persist the knowledge + board state and print the「已保存」marker. Do not
answer-then-stop and leave the increment unpersisted. A **state-only** increment (board moved,
no new knowledge) → run a silent **checkpoint**. **No** increment → say nothing.

**Board-sync:** the mechanical part (`## 进行中` + each `INDEX.md` AUTO region) is welded by the
turn-end hook — the *judgment* parts (entry handoff, knowledge classification, `## 下一步` /
`Active focus`) are always yours.

Details → `/flightdeck:preflight` skill / protocol.
</EXTREMELY_IMPORTANT>
