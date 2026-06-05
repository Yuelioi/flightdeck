---
status: active
when_to_read: before passing any multiline string (commit message, heredoc, file content) to a native command through the Bash tool on this dual-shell repo
applies_to: [commit, git, bash, powershell, here-string, heredoc, multiline]
last_updated: 2026-06-05
recurrences: 3
resolved_by:
---

# PowerShell here-string (`@'...'@`) used in the Bash tool

## Signature
- symptom: `@ chore(flightdeck): …` (stray `@` prepended + multi-line subject, trailing `@` leaked into body)
- error_type: —
- where: Bash tool / git commit
- trigger: 多行串（commit message 等）经 Bash 工具传给原生命令时用了 PowerShell here-string `@'...'@`

## 症状/复现

ran `git commit -m @'…'@` through the **Bash** tool. Bash has no here-string, so it parsed
`@` as a literal char followed by a single-quoted string. The commit subject became
`@ chore(flightdeck): …` (stray `@` + a two-line subject) and a trailing `@` leaked into
the body. Needed a `git commit --amend` (via the PowerShell tool) to fix.

## 根因

(wrong model, not carelessness): this repo exposes BOTH a Bash tool and a PowerShell tool.
`@'...'@` is **PowerShell-only** syntax. I reached for the multiline-string idiom by habit
without first checking which shell the chosen tool actually runs — treating "the terminal"
as one environment when it is two.

## 修法

before passing any multiline string to a native command, pick the form by the tool's shell:
- **PowerShell tool** → here-string `@'...'@` (closing `'@` at column 0, no indent).
- **Bash tool** → a real heredoc (`git commit -F - <<'EOF' … EOF`) or `-F <file>`. **Never** `@'...'@` in Bash.
- Safest cross-shell: write the message to a file and `git commit -F <file>`.

**Promoted**: → [checklists/commits.md](../checklists/commits.md) §项目覆盖 (2026-06-03). Incident kept
as the record; if it recurs despite the checklist, escalate to project agent rules (AGENTS.md).

## Cases
3 (this session recorded; 2 prior user-reported, dates unlogged — the under-counting gap
that prompted auto-counting). **Hits the ≥3 promotion gate.**
- 2026-06-03 recorded this session
- (×2) prior user-reported, dates unlogged
