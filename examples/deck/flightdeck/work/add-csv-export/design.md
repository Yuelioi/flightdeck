# Design — CSV export for `notes`

## Problem

Users want their notes in a spreadsheet. Today the only output is the terminal table.

## Approach

Add an `export` subcommand with a `--csv` flag. Reuse the existing note store; add a thin
formatter that maps each note to a CSV row (`id, created, title, body`).

## Decisions

- Stream rows instead of building the whole file in memory — note sets can be large.
- Quote every field (RFC 4180) rather than guessing when quoting is needed: simpler, safe.

<!-- An effort's design + plan live together in work/<effort>/ — not scattered into a
     separate docs/ tree. These are working artifacts, reached from the cockpit, so they
     carry no routing header (that's for knowledge/ files only). -->
