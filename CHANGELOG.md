# Changelog

Notable user-facing changes are recorded here.

## v3.0.0-alpha.7 — 2026-07-20

### Added

- Added Plan-linked Decision and Delivery Slices for durable execution detail.
- Added optional Wayfinding with one decision at a time and `Not yet specified` uncertainty.
- Added the Work Output Contract for supported specialist documents.
- Added AI-judged workspace upgrades and a short root `AGENTS.md` activation instruction.

### Changed

- Made the top-level AI session the primary operator while keeping Markdown human-auditable.
- Replaced Active/Paused with Open, Finished, and Stopped; Focus remains Deck navigation.
- Made the Work page authoritative for Goal, lifecycle, Current, Next, and the execution pointer,
  while the Plan owns ordered Slice completion.
- Moved immediate recovery links into Next and limited progressive recovery to one Work, its
  context and Plan, at most three Next links, and live Git state.
- Continued the published Version 3 alpha line instead of assigning release meaning to abandoned
  internal v4/v5 experiments.

### Removed

- Removed the separate `Read now` section, duplicate Slice maps, claims, blocker graphs, and
  workflow-style lifecycle metadata.
- Removed automatic Git checkpoints, migration compatibility promises, and multi-session
  coordination behavior.

## v3.0.0-alpha.6 — 2026-06-29

Released the previous AI-native protocol design. Alpha.7 replaces its runtime and protocol model
with the Markdown-only Flightdeck architecture; historical detail remains in Git.
