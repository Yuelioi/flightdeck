<EXTREMELY_IMPORTANT>
This project uses **flightdeck** — a `flightdeck/` deck is present at the project root.

**On entry (handoff, from turn 0):** before doing anything else, take over per the
`/flightdeck:preflight` protocol — read `flightdeck/cockpit.md` (`Active focus`, `## 进行中`,
`## 下一步`) and the folder `INDEX.md` files, then report the next step. You are already in
*handoff* mode; the user does NOT need to type `/flightdeck:preflight` for you to read the
cockpit and continue the prior thread.

**On exit (end-of-turn, before returning control):** if this turn produced **write-gated
knowledge** — something that changes future behavior, influences a decision, or will be
referenced repeatedly (protocol § Write gate; transient byproducts and pure Q&A do NOT count) —
you MUST **soft-land** before you stop: persist the knowledge + board state and print the
「已保存」marker. Do not answer-then-stop and leave the increment unpersisted. A **state-only**
increment (board moved, no new knowledge) → run a silent **checkpoint** instead. **No** increment
→ say nothing.

This directive is the single source of truth shared across every host (Claude Code, Cursor,
Gemini, Codex). The mechanical part of board-sync (`## 进行中` + each `INDEX.md` AUTO region) is
additionally welded by a Stop hook on Claude Code — but the *judgment* parts above (entry handoff,
knowledge classification, `## 下一步` / `Active focus`) are always yours.
</EXTREMELY_IMPORTANT>
