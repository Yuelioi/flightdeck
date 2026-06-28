# knowledge self-contained checklist

SUMMARY: Always make knowledge files self-contained; never make the durable lesson depend on spec, plan, topic-package, or archive links.
READ WHEN: before writing or editing any flightdeck knowledge file

---

Knowledge is the stable library. Specs, plans, topic package files, and archived work are
lifecycle artifacts: they move, get renamed, get compressed, or leave the warm recovery
payload. A knowledge file that only says "see that plan" is not durable enough to route a
future session.

Before saving a knowledge file:

- Copy the stable conclusion, decision, root cause, or procedure into the knowledge body.
- Include enough local context that the file is useful without opening the originating
  topic package.
- Avoid load-bearing links or pointers to specs, plans, active topic files, or archived work.
- Use source artifacts only as archaeology; do not make them dependencies for applying the
  knowledge.
