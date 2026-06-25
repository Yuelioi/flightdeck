# ⚠ Watch-mode tests hang under CI

SUMMARY: `pytest --watch` never exits in CI — no TTY, so it blocks for a keypress and the job times out instead of failing.
READ WHEN: a CI job that runs tests hangs or times out with no output.
RECHECK WHEN: the test runner or the CI image changes.

---

The watch plugin waits for a keypress to re-run. Under CI there's no TTY, so it blocks
forever and the job hits its wall-clock timeout — it looks like a hang, not a failure,
which sends you debugging the wrong thing.

Fix: in CI run the one-shot form (`pytest -q`), never the `--watch` form. If one script
serves both local and CI, guard it with `if [ -t 1 ]` (only watch when stdout is a TTY).
