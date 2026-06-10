# Design philosophy

## Why a write gate

Most "AI memory" systems fail by **saving everything** — the signal drowns in a junk drawer the AI eventually gives up reading. flightdeck stores only what **changes future behavior, influences decisions, or gets referenced repeatedly**. Session logs, debug dumps, "let me just save this for later" — refused. The gate is the feature.

## Why a lifecycle, not a notes file

A static notes file (CLAUDE.md, project notes) is append-only — it rots. flightdeck is a state machine with gates:

- a new mistake → `incidents/` with mandatory root-cause analysis (forbidden phrasings: "forgot", "careless");
- the same mistake recurs → a 3-criterion promotion gate offers to elevate it to `checklists/` (always user-confirmed, never automatic);
- work ships → `status` advances to `done`; the landing ritual moves it to `archive/` once nothing active references it (`done` alone never auto-archives — status is orthogonal to location), and it stops being authoritative for current state.

The lifecycle is what prevents the junk-drawer failure mode that static rules files always succumb to.

## Why the 80-line cockpit ceiling

`cockpit.md` is read every session by both human and AI. At 80 lines it fits one screen and ~1k tokens. Past that, board-style files grow to 300–500 lines, the AI burns context just orienting, and humans stop reading them. The ceiling forces a real decision each time it's hit: does this earn a place in the entry point, or does it belong one folder deeper (`specs/`, `incidents/`) or out entirely?

## Why aviation

Session lifecycle, checklists under uncertainty, incident tracking, operator handoffs, controlled autonomy with periodic re-anchoring — these are aviation concepts, used as **structure**, not decoration.

> ✨ **Semantic clarity outranks thematic consistency.** The metaphor is used only where it sharpens operational intent. Folder names are chosen for clarity first — `specs/`, `plans/`, and `docs/` keep neutral names because no aviation term improves them. A word that fits the metaphor but reads confusingly is rejected.
