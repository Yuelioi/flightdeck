---
status: accepted
---

# Durable Work requires real recovery value

Flightdeck creates Work only when the user explicitly asks, work is likely to cross sessions or
meaningful commits, specialist documents or independent context are needed, or rediscovery would be
costly. It reuses matching Open Work, creates a real Work context, adds Plan and Slices only as
complexity demands, and never prebuilds empty Work for ordinary short tasks.
