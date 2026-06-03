#!/usr/bin/env bash
# Install all flightdeck skills into your AI tool's skills directory.
#
# Installs preflight + landing + walkaround + emit-agents-md.
#
# Usage:
#   ./install.sh                          # auto-detect AI tool, install skills
#   ./install.sh --tool=claude            # explicit AI tool
#   ./install.sh --scaffold               # also scaffold flightdeck/ (full layout; --scaffold value deprecated/ignored in 3.x, flag removed in 4.0)
#   ./install.sh --tool=claude --force    # overwrite existing install
#
# Supported (active):  claude
# Stub (PRs welcome):  codex, cursor, gemini

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skills_source="$repo_root/skills"

tool="auto"
scaffold="none"
force="false"

# parse args
for arg in "$@"; do
    case "$arg" in
        --tool=*)     tool="${arg#--tool=}" ;;
        --scaffold=*) scaffold="${arg#--scaffold=}" ;;
        --force)      force="true" ;;
        -h|--help)
            head -n 12 "$0" | tail -n 11
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg" >&2
            exit 1
            ;;
    esac
done

if [[ ! -d "$skills_source" ]]; then
    echo "Skills source not found: $skills_source" >&2
    exit 1
fi

detect_tool() {
    if [[ -d "$HOME/.claude" ]]; then
        echo "claude"
        return
    fi
    if [[ -d "$HOME/.agents" ]]; then
        echo "codex"
        return
    fi
    echo ""
}

confirm_overwrite() {
    local target="$1"
    if [[ -e "$target" && "$force" != "true" ]]; then
        echo "Target already exists: $target"
        read -r -p "Overwrite? [y/N] " answer
        case "$answer" in
            y|Y) return 0 ;;
            *)   return 1 ;;
        esac
    fi
    return 0
}

install_claude() {
    local skills_dir="$HOME/.claude/skills"
    mkdir -p "$skills_dir"
    local installed=()
    for src in "$skills_source"/*/; do
        local skill_name
        skill_name="$(basename "$src")"
        local target="$skills_dir/$skill_name"
        if ! confirm_overwrite "$target"; then
            echo "Skipped: $skill_name"
            continue
        fi
        rm -rf "$target"
        cp -R "$src" "$target"
        installed+=("$skill_name")
    done
    if [[ ${#installed[@]} -gt 0 ]]; then
        echo "Installed skills: ${installed[*]}"
        echo "Target dir: $skills_dir"
        echo "Verify: in a Claude Code session, run /flightdeck:preflight or check the skill list."
    fi
}

install_stub() {
    local tool_name="$1"
    local adapter_readme="$repo_root/adapters/$tool_name/README.md"
    echo ""
    echo "Adapter '$tool_name' is a stub (no active install logic yet)."
    echo "See: $adapter_readme"
    echo "PRs welcome."
    echo ""
}

invoke_scaffold() {
    local variant="$1"
    local source="$repo_root/scaffolds/$variant/flightdeck"
    local target="$(pwd)/flightdeck"

    if [[ ! -d "$source" ]]; then
        echo "Scaffold variant not found: $source" >&2
        return 1
    fi

    if ! confirm_overwrite "$target"; then
        echo "Scaffold skipped."
        return
    fi

    rm -rf "$target"
    cp -R "$source" "$target"
    echo "Scaffolded: $target ($variant)"
}

# --- main ---

if [[ "$tool" == "auto" ]]; then
    tool="$(detect_tool)"
    if [[ -z "$tool" ]]; then
        echo "Could not auto-detect an AI tool. Specify with --tool=<claude|codex|cursor|gemini>." >&2
        exit 1
    fi
    echo "Auto-detected: $tool"
fi

case "$tool" in
    claude) install_claude ;;
    codex)  install_stub codex ;;
    cursor) install_stub cursor ;;
    gemini) install_stub gemini ;;
    *)
        echo "Unknown tool: $tool" >&2
        exit 1
        ;;
esac

if [[ "$scaffold" != "none" ]]; then
    if [[ "$scaffold" != "full" ]]; then
        echo "warning: --scaffold=$scaffold is deprecated (3.x) and ignored; the full layout is always installed; the --scaffold flag is removed in 4.0." >&2
    fi
    invoke_scaffold "full"
fi

echo ""
echo "Done."
