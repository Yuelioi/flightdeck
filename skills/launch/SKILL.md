---
name: launch
description: Use when explicitly creating a flightdeck deck for the first time in a project that has none — copies the shipped scaffold (an empty cockpit.md + briefing.md + work/ + knowledge/). Script-free. Refuses if flightdeck/cockpit.md already exists. Triggered by /flightdeck:launch.
---

## Refuse if a deck already exists

If `flightdeck/cockpit.md` exists → print "A flightdeck deck already exists here."
and **STOP**. Never overwrite a live deck.

## Run this — copy the scaffold

Copy the `scaffold/flightdeck/` directory that ships beside this skill into the project
root, then replace `<project>` in the two `# …` headings with the project's name. That's
the whole job — **copy the scaffold, don't hand-author it.** The result under `flightdeck/`:

    cockpit.md     empty project index — Focus + ## In flight + ## Next + ## Open questions
    briefing.md    ## Conventions + ## Subscriptions (seed comments, empty to start)
    work/          empty (.gitkeep); future active work lives in work/<topic>/
    knowledge/     empty (.gitkeep); future knowledge lives under knowledge/<domain>/

## Report

Print the created layout. If the project isn't a git repo, add one line: zero-loss stays
off until you `git init` (persist commits the deck each turn — no repo, no guarantee).
Do not create a sample topic package during launch; `work/<topic>/` appears only when an
actual active effort starts.
Then close with the launch banner — `─── 🛠️ launch ───` followed by `deck created · run
/flightdeck:preflight to start`. It pairs with preflight's `🛫` and landing's `🛬`.
