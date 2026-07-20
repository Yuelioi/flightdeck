# Flightdeck alpha.7 delivery context

## What matters

The published product line is Version 3 alpha. Flightdeck must remain a Markdown-only plugin whose
primary operator is one top-level AI session; child agents may contribute, but the top-level session
consolidates durable Work state. The repository currently contains a coherent accepted design and a
superseded v5 implementation, so delivery is a semantic replacement rather than an additive
compatibility project.

The final release commit and any push, tag, ref deletion, or publication remain outside ordinary
implementation. They occur only through the explicitly authorized release procedure in ADR-0022.

## Decisions

- ADR-0001 through ADR-0025 and the root `CONTEXT.md` are the design authority for this Work.
- The implementation remains manifests, one orchestration skill, progressively loaded Markdown
  guidance, templates, documentation, and examples; no runtime, CLI, schema, generator, or validator
  is added.
- The Work model uses Open, Finished, and Stopped lifecycle states; Focus remains navigation.
- Complex Work may use Plan-linked Decision and Delivery Slices, while the Work page remains the
  recovery root and Plan owns Slice completion.
- Next carries at most three immediate recovery links; there is no separate `Read now` section.
- Supported document-producing skills route Work-scoped outputs into the owning Work. Other outputs
  remain at their natural location and are linked.
- The obsolete `flightdeck-redesign` Work is removed because it specifies the superseded v5 model;
  Git retains its history.

## Terms

- **Alpha.7 implementation:** The repository changes that make every shipped surface agree with the
  accepted Version 3 alpha architecture.
- **Product surface:** A plugin instruction, template, public document, example, manifest, or
  repository instruction that teaches or identifies Flightdeck behavior.
