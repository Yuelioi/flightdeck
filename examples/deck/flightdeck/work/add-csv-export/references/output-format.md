# CSV output contract

The endpoint returns `text/csv; charset=utf-8` with a UTF-8 BOM. The attachment filename contains
the export date. Columns appear in this order: order ID, created time, customer, status, and total.

Fields follow RFC 4180 quoting. Values beginning with spreadsheet formula prefixes are escaped
according to the repository's CSV safety guidance.
