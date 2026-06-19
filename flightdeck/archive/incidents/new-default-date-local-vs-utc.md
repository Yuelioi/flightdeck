---
status: obsolete
summary: flightdeck_new.py defaults date to local (datetime.date.today) but the .js twin uses UTC (Date.toISOString) — parity breaks across the local/UTC midnight window
when_to_read: before changing flightdeck_new/_init default date handling, or when test_parity_init_new fails with a 1-day date diff
applies_to: [scripts/flightdeck_new.py, scripts/flightdeck_new.js, scripts/tests/test_parity_init_new.py]
last_updated: 2026-06-20
resolved_by: 9da21d2
---

# flightdeck_new default date: py local vs js UTC breaks parity

## Signature
- symptom: `test_parity_init_new.py::NewParity::test_stamp_plan_and_index AssertionError — py deck has 2026-06-20-do-x.md, js deck has 2026-06-19-do-x.md`
- error_type: AssertionError
- where: flightdeck_new default-date fallback (.py vs .js)
- trigger: run flightdeck_new without `--date` while local time and UTC are on different calendar days (e.g. UTC+8 early morning)

## Symptom / repro

`uv run pytest scripts/tests/test_parity_init_new.py` fails on `test_stamp_plan_and_index`
with a one-day diff in the stamped filename / `last_updated`. The test stamps a `plan`
without `--date`, so both ports fall back to their default "today". They disagree by a day
whenever the run happens inside the local-vs-UTC midnight gap. Deterministic — not a flake —
for the whole offset window (the China-morning hours, where local is already the next date
but UTC is still the previous one).

## Root cause

The two ports compute the default date from different clocks:

- `scripts/flightdeck_new.py:100` — `datetime.date.today().isoformat()` → **local** date.
- `scripts/flightdeck_new.js:92` — `new Date().toISOString().slice(0, 10)` → **UTC** date.

The byte-parity contract requires identical output; defaulting from wall-clock with *mismatched
timezone semantics* violates it. The parity harness deliberately pins `--date` for most cases
(spec §3.3 "dates via --date, never wall-clock"), but `test_stamp_plan_and_index` exercises the
**default** path and so exposes the divergence. (`flightdeck_conform` is unaffected — it carries
no wall-clock date at all.)

## Fix

Fixed 2026-06-20 (`9da21d2`). Both `.js` ports now derive the default date from **local**
components (`getFullYear` / `getMonth` / `getDate`, zero-padded) via a `todayIso()` helper,
matching Python's `datetime.date.today().isoformat()`. Both `flightdeck_new.js` and the other
offender found in the audit, `flightdeck_init.js`, were switched off `toISOString()`. Guard:
`test_parity_init_new.py::NewParity::test_stamp_plan_and_index` (new default path, already
present) + a new `InitParity::test_seed_default_date` (init default path) — both compare the
py/js trees with no `--date`, so a future UTC regression goes red.

## Cases
- 2026-06-20 first seen — surfaced as a red `test_stamp_plan_and_index` during the
  deck-format-conform landing; diagnosed as pre-existing (orthogonal to the conform work).
