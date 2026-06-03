---
status: active
when_to_read: before changing the INDEX row format or the workflow `summary` field rules
applies_to: [index, summary, row-format, exit-ritual, status]
last_updated: 2026-06-03
---

# INDEX row summary can collide with the ` — ` field separator

**Symptom**: A workflow `summary` containing an em-dash (e.g. `implement the cache in three steps — wrapper, hook, metrics`) produces an INDEX row `- [file](file) — <status> — <summary>` in which the summary's own ` — ` is indistinguishable from the row's field delimiter. A naive parser splitting the row on ` — ` mis-segments status vs. summary. Observed while dogfooding 2.3 full-auto landing on a scratch deck.

**Root cause** (assumption, not carelessness): I assumed a one-line `summary` is safe to drop verbatim into the INDEX row, but the row format uses ` — ` as its own field separator (`status — summary`), and the template *recommends authors use dashes in summaries* (`no | [ ] or newlines — use commas/dashes`). The defensive escaping rule only covers `|`, never ` — `, so the two collide.

**Lesson**: When touching the INDEX row format ([exit-ritual.md § Row format](../../skills/preflight/exit-ritual.md)) or the summary constraint (templates.md), resolve the collision — either (a) forbid em-dash in `summary` (steer authors to commas), (b) switch the row delimiter to something summaries won't contain (e.g. `· ` or a tab), or (c) split only on the first two ` — ` when parsing. Rows are regenerated (not parsed) today, so this is latent — but any future INDEX-row parser inherits the ambiguity.
