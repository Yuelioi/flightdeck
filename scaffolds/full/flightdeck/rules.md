---
version: 3.0
disabled_folders: []     # the one structured toggle: listed folders never suggested / not flagged as orphans
---

## House rules

<!-- Deck-local flightdeck conventions + behavioral overrides. rules.md is mandatory — do not delete it.
     Defaults (override below): commit confirm-gated (asks Y/n); preflight/walkaround/emit-agents-md/status
     self-invoke; LANDING is manual (it archives + commits — opt in to auto); status auto-starts (idea→active)
     but does NOT auto-archive on done; git & emit inferred from .git / AGENTS.md presence; bundled scripts off.
     So out of the box nothing archives or commits without you. Tune everything via ### Autonomy overrides below.
     General project conventions belong in CLAUDE.md/AGENTS.md, not here. -->

### Project conventions

### Autonomy overrides
<!-- Omit a line = keep the default. To change a behavior, UNCOMMENT its phrase (one per line). -->

<!-- ── make me MORE autonomous (these are off/gated by default) ── -->
<!-- landing: self-invoke -->                 <!-- let me run /flightdeck:landing myself (default: you run it) -->
<!-- status: auto land -->                    <!-- auto-archive an artifact the moment it flips to done (default: off) -->
<!-- commit without asking -->                <!-- commit without the Y/n prompt (default: ask first) -->
<!-- run scripts -->                          <!-- use the bundled INDEX/lint scripts; add "with uv run" to pin a runtime (default: by hand) -->

<!-- ── make me LESS autonomous (these are on by default) ── -->
<!-- preflight: don't self-invoke; I run it manually -->    <!-- also: walkaround / emit-agents-md / status -->
<!-- status: don't auto start -->             <!-- don't auto-flip idea→active when work begins -->
<!-- don't auto-commit; leave changes for me / CI -->       <!-- never commit at all -->

<!-- ── environment (normally inferred — set only to override inference) ── -->
<!-- this deck doesn't use git; history in landed/HISTORY.md -->   <!-- force no-git mode -->
<!-- has AGENTS.md but don't auto-regen -->   <!-- keep AGENTS.md but stop regenerating it from cockpit -->
