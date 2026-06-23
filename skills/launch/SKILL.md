---
name: launch
description: Use when explicitly creating a flightdeck deck for the first time in a project that has none — seeds the new-form skeleton (cockpit.md + rules.md + uses.md + work/ + knowledge/). Script-free. Refuses if flightdeck/cockpit.md already exists. Triggered by /flightdeck:launch.
---

## Refuse if a deck already exists

If `flightdeck/cockpit.md` exists → print "A flightdeck deck already exists here."
and **STOP**. Never overwrite a live deck.

## Run this — seed the new-form skeleton

The new form has no schema, no INDEX, no script runtime to record — so creation is
just writing a few files. flightdeck runs without git, but the **zero-loss guarantee
only holds when the project is a git repo committed each turn** (persist's job) — so
`git init` the project if it isn't one. See [../preflight/protocol.md](../preflight/protocol.md).

Create under `flightdeck/`:

- `cockpit.md` — seed with `# Cockpit — <project>` and one line naming the current
  focus. Keep it **free-form** — no fixed schema, no `Updated:` field (git already
  knows when/who). It only has to answer, in whatever shape fits: what you're doing /
  where you are / next / open questions. It's the recovery payload, rewritten each
  turn, kept small.
- `rules.md` — `## House rules` with a one-line note that it holds project house
  rules + AI-maintenance preferences; read on preflight, stable.
- `uses.md` — a comment line explaining it lists one `~/.flightdeck`-relative path
  per line that this project subscribes to (`#` comments; empty to start).
- `work/` and `knowledge/` — empty directories (add a `.gitkeep` if your VCS needs
  it to track an empty dir).

## Final report

Print the created layout and point the user at `/flightdeck:preflight` to start a
session. The protocol itself loads when they run preflight — nothing is injected.
