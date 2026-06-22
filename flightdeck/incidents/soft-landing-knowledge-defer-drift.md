---
status: active
when_to_read: deciding whether a turn that produced new knowledge (bug+root-cause / decision / reusable procedure) should soft-land and persist the incident now, or only checkpoint -- especially when tempted to defer the incident to a later batch landing because the plan is unfinished or unverified
applies_to: [skills/preflight/exit-ritual.md, skills/landing/SKILL.md, skills/preflight/protocol.md]
last_updated: 2026-06-22
resolved_by: skills/preflight/exit-ritual.md
---

# Knowledge-increment turn deferred to a batch landing

## Signature
- symptom: `knowledge increment (bug+root-cause / decision / procedure) parked only in the commit message + cockpit Pending Review, with the incident deferred to a later batch landing`
- error_type: —
- where: soft-landing / signal-3 classification (skills/preflight/exit-ritual.md)
- trigger: a turn produces new knowledge while a multi-step plan is mid-flight and/or the fix is not yet verified

## Symptom / repro

A turn discovers write-gated knowledge (a bug + root cause, a design decision, a reusable
procedure) but the plan it sits in is unfinished or the fix is not yet verified. Instead of
writing the incident, the turn parks the finding in the commit message body + a cockpit
`## Pending Review` line as a "write the incident later" TODO, and downgrades the turn to a
state-only checkpoint — deferring the routed incident to the eventual full `/flightdeck:landing`.

## Root cause

Persistence is AI-judgment-driven with **no mechanical backstop**. The turn-end hook welds
only the AUTO regions (`## In Progress` + each `INDEX.md`); it does NOT classify knowledge or
write incidents. So whether the incident is ever written rides entirely on the AI treating the
turn as a signal-3 soft-landing. The recurring rationalization — "plan unfinished / not yet
verified → too early to write the incident" — conflates *verification* (deferrable) with
*persistence* (not deferrable), and routes the turn to checkpoint, which by design does not
classify knowledge.

Consequence: the knowledge degrades to an unstructured form. It survives only in the commit
message (durable in git but **unrouted** — no `when_to_read` / `applies_to`, invisible to
retrieval) and in cockpit Pending Review (a fragile reminder). If the session ends before the
batch landing arrives, the routed incident is orphaned — recoverable only by a human
re-reading the commit message.

## Fix

A knowledge-increment turn **soft-lands and writes the incident in the same turn, even
mid-plan.** Unverified is not a reason to defer: write the incident with `status: active` and
stamp a `verify:` marker — the deterministic pending-verify scan re-surfaces it every preflight
until confirmed. **Verification is deferrable; persistence is not.**

Codified in `skills/preflight/exit-ritual.md`:
1. heuristic (a) gained a "**Persist at the discovering turn — never defer to a batch landing**"
   clause (covers the "batch it at landing" / "unverified so too early" rationalizations).
2. the signal-3 definition now states a turn that *also* advanced a plan task is **not** thereby
   state-only — the knowledge half makes it a soft-landing; both halves fire in the same turn.

## Cases
- 2026-06-22 first seen — a booyah-clone AE-automation session produced three findings
  (a `setLdtaFrac` coarse-divisor out-point truncation bug + fix, a mask-bbox geometry read-side
  gap, a displacement-map `tdpi` self-ref read-side finding) and parked them in the commit
  message + cockpit Pending with "待整个 plan landing 时各落一条 incident". Surfaced the
  no-mechanical-backstop gap and motivated the exit-ritual prose hardening above.
