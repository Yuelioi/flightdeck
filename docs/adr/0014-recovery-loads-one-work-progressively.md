---
status: accepted
---

# Recovery loads one Work progressively

Recovery selects an explicitly named Work or the deck Focus, reads its page and required context,
reads an existing low-resolution Plan, follows at most three local links in Next, and checks live
Git state before execution. It does not preload other Work, all Slices, all References, all
Knowledge, or Git history; a deck with Open Work has exactly one Focus and an empty deck has none.
