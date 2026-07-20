# Export CSV safely

Define a public row projection and stable column order instead of serializing persistence records.
Quote fields consistently, choose encoding from actual client requirements, and stream large result
sets. Preserve the same authorization and filters as the source view.

Spreadsheet programs may execute cells beginning with `=`, `+`, `-`, or `@`. Apply the project's
chosen neutralization policy to untrusted text before CSV quoting, and cover the behavior with
representative integration tests.
