# ⚠ launch scaffold ships verbatim

SUMMARY: `skills/launch/scaffold/flightdeck/` ships verbatim to users — careless edits break first-time setup.
READ WHEN: before editing `skills/launch/scaffold/` or the first-time-setup / launch flow

---

## Signature

- symptom: `stray scratch files left in skills/launch/scaffold/ get copied verbatim into every new user's deck`
- error_type: —
- where: skills/launch/scaffold/ + launch copy-the-scaffold first-time setup
- trigger: leaving any non-contract file (scratch / leftover) inside skills/launch/scaffold/ when it is copied verbatim into a new deck

## 症状/复现

3 AI-review `.txt` files were dropped into the shipped scaffold as a scratch spot. Because
launch first-time setup **copies `skills/launch/scaffold/flightdeck/` verbatim** into each
new deck, those files would have been copied into every new user's `flightdeck/`.

## 根因

(assumption, not carelessness): I treated the scaffold as an inert "template directory" —
but under copy-the-scaffold it **is the shipped content**. Anything sitting in it (stray
scratch, leftover files) becomes part of every freshly created deck.

## 修法

Keep `skills/launch/scaffold/flightdeck/` **pristine**. It should contain only the launch
contract: `cockpit.md`, `briefing.md`, `work/.gitkeep`, and `knowledge/.gitkeep`. Do not
ship sample topic packages, sample knowledge, archives, old `INDEX.md` files, or scratch
material. Never use it as a scratch location. Pre-ship check: list the scaffold files and
verify that only those four contract files are present.

## Cases

- 2026-06-03 首次
