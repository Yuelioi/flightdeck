# Route specialist outputs

Use the owning Work as the document boundary for specialist methods that Flightdeck supports and
invokes. Do not create a second task store or handoff protocol.

- Put stable Work-scoped domain meaning and decisions in `context.md`.
- Put Work-scoped research, specifications, reviews, and similar durable documents under
  `work/<id>/references/` with descriptive names. Keep the directory flat until real volume makes a
  subject subdirectory clearer.
- Put ticketing or Wayfinding completion order in `plan.md`; create only the Decision or Delivery
  Slices that need independent recovery detail.
- Replace a separate handoff document with an ordinary Flightdeck save.
- Let execution skills modify source and the current Slice. Keep prototypes and required assets
  near their owning code when that is their authoritative location, and link them from the Work.
- Keep project-wide vocabulary in root `CONTEXT.md` and architectural decisions in `docs/adr/`.

Source changes, temporary files, external-system records, and outputs governed by an unsupported
third-party contract remain at their natural location and are linked without copying. When the
producer allows the caller to choose and the output is Work-scoped, route it into the owning Work.

After the specialist method returns, consolidate its durable result into the Work, Plan, current
Slice, context, or References according to those ownership rules, then apply save semantics.
