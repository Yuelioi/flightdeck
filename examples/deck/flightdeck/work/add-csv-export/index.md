# Index — add CSV export

## State

Design is drafted and the main plan is ready. Implementation should continue with the CSV
row formatter.

## Next

Implement the first unchecked step in `plan.md`.

## Read now

- plan.md
- design.md
- knowledge/git/commit-style.md

## Read if

- knowledge/storage/sqlite/wal-mode.md — if export needs database transaction behavior.
- knowledge/build/flaky-watch-mode.md — if tests fail only in watch mode.

## Progress

Done:

- Design drafted.
- Plan drafted.

Current:

- Implementing the CSV row formatter.

Verified:

- Not yet verified.

Not done:

- Formatter implementation.
- CLI integration.
- Export tests.

## Open questions

- Should export include archived notes by default, or require `--all`? (waiting on user)

## Key facts

- The active command is `notes export --format csv`.
- CSV escaping rules live in `design.md`.
