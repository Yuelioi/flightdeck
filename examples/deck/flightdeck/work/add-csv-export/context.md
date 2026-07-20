# Add CSV export context

## What matters

Exports must reflect the filters visible to the requesting user and must apply the same authorization
scope as the order list. Large exports cannot buffer the complete result in memory.

## Decisions

- Stream rows through the existing order query cursor.
- Use UTF-8 with a BOM because spreadsheet interoperability is part of the product requirement.
- Keep column order stable and independent of database field order.

## Terms

- **Visible filters:** The validated filter object used by the current order list.
- **Export row:** The explicit public projection, not the persistence record.
