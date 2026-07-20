# Add CSV export

## Goal

Let users download the currently filtered orders as a correctly encoded CSV file.

## Status

Open

## Current

The output contract is accepted and the service query is implemented. The HTTP handler and its
integration test remain.

## Next

Implement the streaming download handler through the
[current Delivery Slice](slices/03-add-streaming-handler.md).

## Progress

- Confirmed that export uses the visible filters rather than the complete order set.
- Defined UTF-8, header order, quoting, and filename behavior.
- Added the filtered export query and unit coverage.

## References

- [CSV safety guidance](../../knowledge/engineering/csv-export.md) — reusable spreadsheet and
  encoding considerations.
