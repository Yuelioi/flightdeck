# scaffolds/full/ ships verbatim — keep it pristine

## Signature
- symptom: `stray scratch files left in scaffolds/full/ get copied verbatim into every new user's deck`
- error_type: —
- where: scaffolds/full/ + preflight copy-the-scaffold first-time-setup
- trigger: leaving any non-contract file (scratch / leftover) inside scaffolds/full/ when it is copied verbatim into a new deck

## 症状/复现

3 AI-review `.txt` files were dropped into `scaffolds/full/flightdeck/debriefs/` as a scratch spot.
Because the init-redesign makes `preflight` first-time-setup **copy `scaffolds/full/` verbatim**
into each new deck, those txt would have been copied into every new user's `flightdeck/debriefs/`.

## 根因

(assumption, not carelessness): I treated `scaffolds/full/` as an inert "template directory" — but
under copy-the-scaffold it **is the shipped content**. Anything sitting in it (stray scratch,
leftover files) becomes part of every freshly created deck.

## 修法

Keep `scaffolds/full/` **pristine** — each folder holds only its `INDEX.md` (empty AUTO region),
plus the 2 contract files (`rules.md` + `cockpit.md`). No `archive/` and no history-log file ship
(3.0 removed the separate landing log; `archive/` is created on demand at first land). Never use it
as a scratch location. Pre-ship check: `find scaffolds/full -type f` should list *only* `rules.md`,
`cockpit.md`, and each folder's `INDEX.md` — nothing else.

## Cases
- 2026-06-03 首次
