---
status: accepted
---

# Save does not create Git checkpoints

Flightdeck Save edits Markdown only and never stages, commits, pushes, tags, or branches. When Git
operations are authorized, related Work documents may accompany the code state they describe in
the same logical commit, but intermediate commits do not force a Save and Git hashes remain ordinary
verification evidence rather than revision identities.
