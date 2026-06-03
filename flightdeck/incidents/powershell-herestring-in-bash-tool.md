---
status: active
when_to_read: before passing any multiline string (commit message, heredoc, file content) to a native command through the Bash tool on this dual-shell repo
applies_to: [commit, git, bash, powershell, here-string, heredoc, multiline]
last_updated: 2026-06-03
---

# PowerShell here-string (`@'...'@`) used in the Bash tool

**Recurrences**: 3 — sessions: 2026-06-03 (recorded) + 2 prior (user-reported, dates unlogged — this incident is why counts now get logged). **Hits the ≥3 promotion gate.**

**Symptom**: ran `git commit -m @'…'@` through the **Bash** tool. Bash has no here-string, so it parsed `@` as a literal char followed by a single-quoted string. The commit subject became `@ chore(flightdeck): …` (stray `@` + a two-line subject) and a trailing `@` leaked into the body. Needed a `git commit --amend` (via the PowerShell tool) to fix.

**Root cause** (wrong model, not carelessness): this repo exposes BOTH a Bash tool and a PowerShell tool. `@'...'@` is **PowerShell-only** syntax. I reached for the multiline-string idiom by habit without first checking which shell the chosen tool actually runs — treating "the terminal" as one environment when it is two.

**Lesson**: before passing any multiline string to a native command, pick the form by the tool's shell:
- **PowerShell tool** → here-string `@'...'@` (closing `'@` at column 0, no indent).
- **Bash tool** → a real heredoc (`git commit -F - <<'EOF' … EOF`) or `-F <file>`. **Never** `@'...'@` in Bash.
- Safest cross-shell: write the message to a file and `git commit -F <file>`.

**Promoted**: → [checklists/commits.md](../checklists/commits.md) §项目覆盖 (2026-06-03). Incident kept as the record; if it recurs despite the checklist, escalate to project agent rules (AGENTS.md).
