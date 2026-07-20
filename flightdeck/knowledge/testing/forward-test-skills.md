# Forward-test skill behavior

Text search and schema validation can prove naming and packaging invariants, but they do not prove
that an agent will follow the intended method.

Test meaningful skill changes from a fresh prompt with no authoring-session context. Inspect which
instructions were loaded, what files were read or written, and whether the produced handoff matches
the user-facing contract. Include ambiguous and interrupted cases when they are important. Run the
same checks against the installed copy, because source-tree success does not prove shipped behavior.
