# Ship Flightdeck v3.0.0-alpha.7 plan

## Wayfinding

- [x] [Confirm the alpha.7 architecture and implementation delta](slices/01-confirm-alpha7-architecture.md)

## Delivery

- [x] [Rewrite the Flightdeck orchestration contract](slices/02-rewrite-orchestration.md)
- [x] [Align documentation, examples, and package metadata](slices/03-align-product-surfaces.md)
- [x] [Verify the alpha.7 package and release tree](slices/04-verify-alpha7.md)

## Acceptance

- [x] The skill, lifecycle branches, templates, docs, examples, manifests, and repository context
  describe the same Work, Plan, Slice, recovery, save, output-routing, and lifecycle semantics.
- [x] The package contains no production runtime, CLI, MCP server, schema, generator, hidden state,
  or required validator.
- [x] Markdown links, host manifests, source/install tree equality, and fresh-session recovery checks
  pass.
- [x] The final tree is ready for the separately authorized ADR-0022 release procedure.
