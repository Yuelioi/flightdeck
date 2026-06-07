# Shared context-assembly helpers for flightdeck hooks (sourced, not executed).
# session-start injects this at entry; stop refreshes the Cursor rule file at
# turn end. Single source of truth for the bootstrap + cockpit-anchor payload so
# the two scripts never drift.

escape_for_json() {
  local s="$1"
  s="${s//\\/\\\\}"; s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"; s="${s//$'\r'/\\r}"; s="${s//$'\t'/\\t}"
  printf '%s' "$s"
}

# build_context PROJECT_DIR PLUGIN_ROOT
# Prints the bootstrap directive + (best-effort) live cockpit anchor to stdout.
# Returns 1 (no output) when the bootstrap is missing — a packaging bug that
# should degrade to silence, not inject a broken anchor.
build_context() {
  local project_dir="$1" plugin_root="$2"
  local bootstrap anchor="" cockpit focus next
  bootstrap="$(cat "${plugin_root}/skills/_shared/bootstrap.md" 2>/dev/null || true)"
  [ -n "$bootstrap" ] || return 1

  cockpit="${project_dir}/flightdeck/cockpit.md"
  if [ -s "$cockpit" ]; then
    focus="$(grep -m1 -E '^\*\*Active focus\*\*' "$cockpit" 2>/dev/null || true)"
    # The "## 下一步" section: from its heading to the next "## " heading.
    next="$(awk '/^## 下一步/{f=1;next} /^## /{f=0} f' "$cockpit" 2>/dev/null || true)"
    if [ -n "$focus" ] || [ -n "$next" ]; then
      anchor=$'\n\n<flightdeck-cockpit-anchor note="may lag last turn; reconcile via /flightdeck:preflight">\n'
      anchor+="${focus}"$'\n## 下一步:\n'"${next}"
      anchor+=$'\n</flightdeck-cockpit-anchor>'
    fi
  fi
  printf '%s' "${bootstrap}${anchor}"
}

# write_cursor_rules PROJECT_DIR CONTENT
# Cursor's stable-loading injection path: a rules file Cursor always applies,
# rather than the unreliable sessionStart additional_context (loading stability
# over elegance). Derived projection — gitignored, never hand-edited.
write_cursor_rules() {
  local rules_dir="$1/.cursor/rules"
  mkdir -p "$rules_dir" 2>/dev/null || return 0
  {
    printf -- '---\nalwaysApply: true\ndescription: "flightdeck cockpit handoff (auto-updated; do not edit)"\n---\n\n'
    printf '%s\n' "$2"
  } > "${rules_dir}/flightdeck-context.mdc" 2>/dev/null || return 0
}
