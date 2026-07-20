# Add the streaming HTTP handler

## Outcome

The export endpoint streams authorized, filtered rows as the accepted CSV response without
buffering the complete result.

## Current

The filtered export query and unit coverage are complete. No HTTP handler or integration test
currently exercises the streaming response.

## Next

Implement the handler against the [CSV output contract](../references/output-format.md).

## Verification

- The integration test proves response headers, filtering, authorization, formula neutralization,
  and streaming behavior.
