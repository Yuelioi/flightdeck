# Add CSV export plan

## Delivery

- [x] Define the output and authorization contract.
- [x] Implement the filtered export query.
- [ ] [Add the streaming HTTP handler](slices/03-add-streaming-handler.md).
- [ ] Add integration coverage and user-facing documentation.

## Acceptance

- [ ] Response columns and filename match the accepted contract.
- [ ] Filters and authorization match the order list.
- [ ] Large exports stream without retaining all rows.
- [ ] Spreadsheet-formula cells are neutralized.
