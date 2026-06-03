---
status: active
summary: 2.3 upgrade is invisible on existing decks (version stamps but no autonomy/commit_mode defaults appear); add a one-line preflight nudge on silent bump
---

# Preflight nudge when silently bumping an existing deck

When `preflight` silently bumps an existing deck `version` 2.2 → 2.3, the deck gains nothing visible: the full-auto `model_invocable` / `status_auto` defaults and `commit_mode` ship only via first-time-setup for *new* decks. A maintainer upgrading sees "version changed, behavior identical" and never learns the new toggles exist. Confirmed dogfooding 2.3 on flightdeck's own deck.

**Revisit when**: editing preflight Step 2 (migration detection, silent-bump branch). Idea: on a silent bump, print one line — e.g. `deck bumped 2.2 → 2.3; new autonomy / commit_mode toggles are opt-in — see MIGRATION 2.2→2.3`. One-time notice on the bump turn only, not every entry. Low cost, closes the discoverability gap.
