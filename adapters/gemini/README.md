# Adapter: Gemini CLI

**Status**: ⚠️ manifest in place, behaviorally untested

## What's in place

- [`gemini-extension.json`](../../gemini-extension.json) — Gemini CLI extension manifest pointing at `GEMINI.md` as context file.
- [`GEMINI.md`](../../GEMINI.md) — `@`-includes all four skill files (SKILL.md, folder-semantics.md, templates.md, exit-ritual.md).

## Install

```bash
gemini extensions install https://github.com/Yuelioi/flightdeck
```

Update later:

```bash
gemini extensions update flightdeck
```

## What "untested" means

Gemini CLI's extension mechanism loads `GEMINI.md` as project / session context. Our `GEMINI.md` uses the `@` include syntax to pull in the four skill files. This means Gemini sees all the protocol content directly, not as a discoverable "skill" with a trigger condition. What has **not** been verified:

- That Gemini honors the `@` include syntax and resolves all four files.
- That auto-triggering on `flightdeck/` works (Gemini may not have skill-trigger semantics — it may simply load the protocol every session).

## Likely Gemini-specific concerns

- **No conditional loading**: unlike Claude's skill triggers, Gemini may load the protocol unconditionally. This is fine for projects that have `flightdeck/` but adds noise for projects that don't.
- **Token cost**: GEMINI.md @-includes pull in ~2000+ words every session.

## How to verify (and flip the matrix to ✅ tested)

1. Install on Gemini CLI per the command above.
2. Open a project with `flightdeck/cockpit.md` populated.
3. Start a fresh session, ask "What were we doing?" — confirm the AI reads `cockpit.md` first.
4. Try one routing scenario from the README routing table.
5. Open a PR that:
   - Updates the README compatibility matrix `⚠️ untested` → `✅ tested`.
   - Pastes the verification transcript here.
   - Notes whether a conditional-load workaround is needed.

## Call-source detection (model_invocable gate)

**Mode: degraded (until verified).** This platform's manifest carries no per-skill
manual-only switch, so the soft gate ships via the shared `SKILL.md` body. Whether this
platform lets the skill body distinguish a user invocation from a model self-invoke is
**unverified**. Under 3.0 the default is **self-invocable**, so the common case needs no
detection; only a House-Rules restriction (`<ritual>: don't self-invoke; I run it manually`, or a pre-3.0
`model_invocable` omission honored for compat) needs source detection. Until verified, a
restricted ritual runs degraded — treated as manual-only, prompting even on an explicit
user invocation. See [protocol § Rule resolution order](../../skills/preflight/protocol.md#rule-resolution-order).
Flip this note to "formal" with a transcript when verified.

## Ritual coverage (GEMINI.md)

`GEMINI.md` `@`-includes only the **preflight** bundle (SKILL.md + protocol/folder-semantics/templates/exit-ritual). The non-preflight rituals — `landing`, `walkaround`, `emit-agents-md`, and now `status` — are **not** individually `@`-included, so their skill bodies aren't loaded on Gemini. This is a pre-existing, untested gap (the manifest is "behaviorally untested"), not specific to `status`. Wiring all rituals into `GEMINI.md` is tracked separately; `status` inherits the same posture as its siblings.
