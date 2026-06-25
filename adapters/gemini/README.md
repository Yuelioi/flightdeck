# Adapter: Gemini CLI

**Status**: ⚠️ manifest in place, behaviorally untested

## What's in place

- [`gemini-extension.json`](../../gemini-extension.json) — Gemini CLI extension manifest pointing at `GEMINI.md` as context file.
- [`GEMINI.md`](../../GEMINI.md) — `@`-includes the preflight protocol (`SKILL.md` + `concepts.md` + `operations.md`).

## Install

```bash
gemini extensions install https://github.com/Yuelioi/flightdeck
```

Update later:

```bash
gemini extensions update flightdeck
```

## What "untested" means

Gemini CLI's extension mechanism loads `GEMINI.md` as project / session context. Our `GEMINI.md` uses the `@` include syntax to pull in the protocol files. This means Gemini sees the protocol content directly, not as a discoverable "skill" with a trigger condition. What has **not** been verified:

- That Gemini honors the `@` include syntax and resolves both files.
- That auto-triggering on `flightdeck/` works (Gemini may not have skill-trigger semantics — it may simply load the protocol every session).

## Likely Gemini-specific concerns

- **No conditional loading**: unlike Claude's skill triggers, Gemini may load the protocol unconditionally. This is fine for projects that have `flightdeck/` but adds noise for projects that don't.
- **Token cost**: the `@`-includes pull the micro-core plus the on-demand companions in every session. Including only `SKILL.md` (the always-loaded micro-core) and leaving `concepts.md` / `operations.md` as on-demand reference would cut this.

## How to verify (and flip the matrix to ✅ tested)

1. Install on Gemini CLI per the command above.
2. Open a project with `flightdeck/cockpit.md` populated.
3. Start a fresh session, ask "What were we doing?" — confirm the AI reads `cockpit.md` first.
4. Try one routing scenario from the README routing table.
5. Open a PR that:
   - Updates the README compatibility matrix `⚠️ untested` → `✅ tested`.
   - Pastes the verification transcript here.
   - Notes whether a conditional-load workaround is needed.

## Invocation

The three verbs — `preflight` / `launch` / `walkaround` — are user-invoked; **persist** runs automatically as you work — at each turn / milestone that moves the board. On Gemini, `GEMINI.md` only `@`-includes the **preflight** protocol, so `launch` / `walkaround` aren't loaded inline — a pre-existing, untested gap (the manifest is "behaviorally untested"). Wiring the other verbs into `GEMINI.md` is tracked separately.
