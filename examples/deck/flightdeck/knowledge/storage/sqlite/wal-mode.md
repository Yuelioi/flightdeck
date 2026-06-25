# Why notes-cli uses SQLite WAL mode

SUMMARY: the store opens in WAL mode so a long export can read while a write commits.
READ WHEN: touching the storage layer, or debugging a "database is locked" error.

---

The default rollback journal takes a write lock that blocks readers. Export streams every
row, which can take a while on a large store, so under the default journal a concurrent
`notes add` fails with "database is locked".

WAL (`PRAGMA journal_mode=WAL`) lets readers and one writer proceed at once — exactly the
export-while-adding case. Set it once when the connection opens; it persists on the file.

This file also shows two things about layout: knowledge nests as deep as the domain needs
(`knowledge/storage/sqlite/`), and a plain `# <title>` (no `⚠`, no `checklist`) is the
third knowledge kind — a decision/reference note, alongside traps and checklists.
