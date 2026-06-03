---
status: active
when_to_read: before editing scaffolds/full/ or the preflight copy-the-scaffold first-time-setup
applies_to: [scaffolds, preflight, init, first-time-setup]
last_updated: 2026-06-03
---

# scaffolds/full/ ships verbatim — keep it pristine

**Symptom**: 3 AI-review `.txt` files were dropped into `scaffolds/full/flightdeck/debriefs/` as a scratch spot. Because the init-redesign makes `preflight` first-time-setup **copy `scaffolds/full/` verbatim** into each new deck, those txt would have been copied into every new user's `flightdeck/debriefs/`.

**Root cause** (assumption, not carelessness): I treated `scaffolds/full/` as an inert "template directory" — but under copy-the-scaffold it **is the shipped content**. Anything sitting in it (stray scratch, leftover files) becomes part of every freshly created deck.

**Lesson**: Keep `scaffolds/full/` **pristine** — each folder holds only its `INDEX.md` (empty AUTO region), plus the 3 contract files (`rules.md` + `cockpit.md` + `landed/HISTORY.md`). Never use it as a scratch location. Pre-ship check: `find scaffolds/full -type f` should list *only* `rules.md`, `cockpit.md`, `landed/HISTORY.md`, and each folder's `INDEX.md` — nothing else.
