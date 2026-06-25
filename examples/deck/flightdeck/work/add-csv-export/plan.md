# Plan — CSV export for `notes`

- [ ] Add the CSV row formatter (`id, created, title, body`) with RFC 4180 quoting
- [ ] Wire up `notes export --csv` to stream rows to stdout
- [ ] Add `--all` to include archived notes (default: active only) — pending the open question
- [ ] Tests: a note containing commas, quotes, and newlines round-trips through export

<!-- The - [ ] checkboxes belong to whatever runs the plan (e.g. superpowers'
     executing-plans); flightdeck tracks the effort by its location in work/, not by
     ticking these boxes. -->
