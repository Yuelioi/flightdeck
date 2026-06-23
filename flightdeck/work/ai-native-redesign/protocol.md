# flightdeck — deep protocol

Read on demand when the micro-core's one-liners aren't enough.

## Write gate

The micro-core rule: record only what changes how you act later, or that you'll
look up again. Concrete calls:

- RECORD: a bug + its root cause; a decision and why; a reusable procedure; a
  trap you'd otherwise hit again.
- SKIP: "ran the tests, they passed"; "explored the API, found nothing useful";
  "reran the build after a flake"; a log of steps with no durable conclusion.
- Borderline → ask: would a future session, cold, act differently for having
  this written? If no, skip.

## Incidents (traps)

A trap is a knowledge file whose title opens `# ⚠ <title>`, living in the domain
it belongs to. No fingerprint, no recurrence counter.

- On hitting a pitfall: write a `# ⚠ <title>` trap, placed by **scope** — project-
  specific → project `knowledge/<domain>/`; general lesson → `~/.flightdeck/knowledge/<domain>/`.
- On hitting it again: grep finds the existing trap → re-read it, do NOT rewrite.
- Once the fix is stable: crystallize it into a same-domain checklist
  (`# <X> checklist`) and let the trap fade. Location encodes scope, not count.

## uses.md shadowing

`uses.md` is a plain list — one `~/.flightdeck/`-relative path per line (a directory
entry subscribes the whole subtree; `#` comments; no YAML). preflight folds these
global files/dirs into the routing tree alongside local `knowledge/`.

- Conflict on the same relpath: the **local file shadows the global one entirely
  (replace, not merge)** → deterministic, zero-maintenance, two preflights give the
  same result. To extend a global file, read both yourself; the file-level rule
  stays replace.
- A subscribed global path that's missing/renamed: preflight emits one soft
  warning and continues — it does not fail.

## Vendoring

References to `~/.flightdeck` make the repo non-self-contained. When you need the
repo portable or shippable, **vendor**: snapshot the referenced global file into the
repo as a copy (a frozen reference), and drop the `uses.md` subscription for it. This
is opt-in and on-demand — the default is live subscription, no copy.

## Derived listing

When walking the tree for routing and `ls` + filenames aren't enough to decide
relevance, run a transient `derive-listing <area>`: grep each file's routing
header and print a one-shot directory to context. It is **never written to disk**
— transient, zero-maintenance, zero-drift. The trigger is AI judgment, not a count
or threshold.
