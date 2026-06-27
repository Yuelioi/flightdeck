# Design — CSV export for `notes`

## Problem

Users want their notes in a spreadsheet. Today the only output is the terminal table.

## Approach

Add an `export` subcommand with a `--csv` flag. Reuse the existing note store; add a thin
formatter that maps each note to a CSV row (`id, created, title, body`).

## Decisions

- Stream rows instead of building the whole file in memory — note sets can be large.
- Quote every field (RFC 4180) rather than guessing when quoting is needed: simpler, safe.

<!-- Topic package files stay together under work/<topic>/. They are reached from cockpit/context, so they carry no routing header. -->
