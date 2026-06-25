# Reference deck

A minimal, correct flightdeck deck — the canonical shape, kept current at HEAD. It has
three jobs:

- **Format by example.** Every file here is a correct instance of a convention: the
  `cockpit.md` skeleton, the `briefing.md` two-section layout, a folder effort under
  `work/` with its design and plan co-located, a checklist knowledge file, and a `# ⚠`
  trap. Read the files, not a spec.
- **Migration / repair target.** `/flightdeck:walkaround` brings an older or drifted deck
  to this shape — preserving your content — so this deck is what it converges on.
- **Launch reference.** `/flightdeck:launch` seeds a deck shaped like this one, emptied
  of the example content.

It is itself a deck, so it is **testable**: `/flightdeck:walkaround` run against it
should report **clean**. If a convention changes and this deck isn't updated, that audit
fails — which is the point. A prose guide can't be tested; this can.

> The `flightdeck/` directory below is an example payload, not this repo's live deck.
> This repo's own deck lives at the repo root.
