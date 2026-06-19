---
status: active
summary: flightdeck_new.py defaults date to local (datetime.date.today) but the .js twin uses UTC (Date.toISOString) — parity breaks across the local/UTC midnight window
when_to_read: before changing flightdeck_new/_init default date handling, or when test_parity_init_new fails with a 1-day date diff
applies_to: [scripts/flightdeck_new.py, scripts/flightdeck_new.js, scripts/tests/test_parity_init_new.py]
last_updated: 2026-06-20
resolved_by:
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

Not yet fixed (found 2026-06-20 while landing deck-format-conform). Candidate: make the `.js`
default match Python's local date — derive `YYYY-MM-DD` from local components, e.g.
`` `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}` ``
instead of `toISOString()`. Verify by re-running `test_parity_init_new.py` inside the offset
window (or with the system clock faked to it). Same audit applies to any other `.js` port that
defaults a date via `toISOString()`.

## Cases
- 2026-06-20 first seen — surfaced as a red `test_stamp_plan_and_index` during the
  deck-format-conform landing; diagnosed as pre-existing (orthogonal to the conform work).
