# ⚠ CRLF breaks `^---$` header-terminator grep on Windows

SUMMARY: On Windows, git autocrlf checks deck files out as CRLF, so a strict `^---$` grep misses the routing-header terminator (`---\r` ≠ `---`); start-anchored greps still work.
READ WHEN: grepping deck routing headers, or writing/auditing tooling that detects the `---` terminator, on Windows or any CRLF checkout

---

The routing header ends with a line `---`. With CRLF line endings that line is
`---\r`, and `rg '^---$'` / `grep '^---$'` won't match it (`$` sits before the `\n`,
leaving the `\r` unmatched). It looks like "missing header terminator" when the
header is actually fine — a false alarm (hit during a walkaround self-check on the
migrated dogfood deck).

derive-listing's recipe is **start-anchored** (`^(# |SUMMARY:|READ WHEN:)`), so it's
unaffected — the `\r` lands after the matched text. Only exact end-anchored
terminator checks break.

Fix: use a CRLF-tolerant pattern — `rg '^---\r?$'` (or `grep -E '^---\r?$'`). Any
walkaround / routing tool that detects the header boundary must allow the optional
`\r`. Normalizing the deck to LF via `.gitattributes` also works, but the
grep-tolerant pattern is the portable fix.
