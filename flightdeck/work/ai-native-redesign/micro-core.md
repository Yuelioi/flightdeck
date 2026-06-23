# flightdeck (micro-core)

Two verbs:
- **preflight** (on request — you run `/flightdeck:preflight`): load this
  protocol, read `cockpit.md`, `rules.md` and `uses.md`, then walk the tree (`ls`
  + grep) for what's needed. Default load = cockpit.md only, rest lazy. Nothing is
  injected, it never auto-fires — skip preflight this session and it's
  disengaged (nothing auto-persists); looking around is free.
- **persist** (automatic, turn end): rewrite `cockpit.md`, write knowledge in
  place, `git commit` the project repo. A **work** effort is done when you move it
  out of `work/` to the cold store; git log records it left.

Plus one audit command — **walkaround** (on request): sweep for drift
(cockpit vs reality, orphaned work, duplicate traps, missing headers). The only
trust-but-verify net; nothing mechanical self-corrects.

Layout:
    <project>/flightdeck/   warm tier — git-tracked, committed each turn
      cockpit.md   now — in-flight efforts · focus + next · open questions
                   (rewritten each turn, kept small)
      rules.md     project house rules — read on preflight, stable
      uses.md      one global path per line this project subscribes to
      work/        in-flight multi-step efforts (one file or folder each)
      knowledge/   persistent — nested by domain; type via title line
    ~/.flightdeck/   cold tier — plain global dir, NOT git
      knowledge/     cross-project knowledge (consulted via uses)
      projects/<x>/  this project's cold store: archive/ + ideas/

Invariants:
- **Location is state.** In the project = live; moved into `~/.flightdeck` = cold
  (done/parked). No status field: in `work/` = active, moved out = done.
  Knowledge (`knowledge/`) is *resident*, not work: present = valid, deleted =
  dead — no lifecycle. Nuanced states (blocked/reviewing/waiting) live in cockpit
  prose, not folders.
- **Routing header** (the one lightweight convention, no YAML schema). Every
  knowledge file opens with a header ended by `---`: a title (`# <title>`; pitfall
  `# ⚠ <title>`; checklist `# <X> checklist`), then `SUMMARY:` (one line), `READ
  WHEN:` (when to route here), optional `RECHECK WHEN:` (what it tracks — re-verify
  when that changes). Below `---`: free-form body. Routing reads only the header
  (cheap); freshness = mtime + body + RECHECK WHEN.
- **Write gate.** Record only what will change how you act later, or that you'll
  look up again. Skip: one-off logs; a build that passed; exploration that found
  nothing; a re-run that added nothing.
- **Zero-loss covers the recovery payload** (cockpit.md + rules.md + work +
  knowledge — all warm, all in git): persist commits the repo every turn;
  `cockpit.md` must answer what you're doing / where you are / next / open
  questions. The cold store is kept but unversioned — out of the guarantee.

Depth (`skills/preflight/protocol.md`, read on demand): write-gate examples,
incident scope+crystallize rule, uses shadowing, vendoring, derived-listing.
