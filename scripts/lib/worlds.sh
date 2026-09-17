#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Shared World-Discovery Library (Q-01)
# Purpose: Single source of truth for every entry-point script that needs to
#          locate worlds, resolve user input to a world directory, or render
#          universe labels. Previously this ~40-line block was copy-pasted
#          across five scripts (with partial copies in five more), which is
#          how the hardcoded-username heuristic bug had to be fixed in four
#          places at once.
#
# Provided helpers:
#   has_gui                     -> true when a graphical session + zenity exist
#   sanitize_name NAME [FALLBACK]
#                               -> filesystem/label-safe token (A-Za-z0-9_-)
#   universe_label WORLD_PATH   -> owning universe name, or "Standalone" for
#                                  worlds under the legacy ~/Worlds root
#                                  (structural detection: path prefix, never
#                                  identity-based)
#   warn_if_legacy_root PATH     -> one-line deprecation nudge on stderr when
#                                  PATH sits under the legacy ~/Worlds root;
#                                  used by resolve_world_dir and by callers
#                                  after auto-selecting a discovered world
#                                  so the nudge fires on every path (N-03)
#   discover_worlds VARNAME     -> populates VARNAME (array) with every world
#                                  under ~/Universes/*/Worlds/* followed by
#                                  ~/Worlds/* (legacy)
#   resolve_world_dir TARGET [UNIVERSE]
#                               -> echoes the absolute path of the world
#                                  identified by TARGET; empty when unresolved
#
# Resolution order (documented contract):
#   1. TARGET is an existing directory path
#   2. TARGET is a bare name beneath an explicit UNIVERSE
#   3. TARGET is a unique basename under ~/Universes/*/Worlds/ (canonical)
#   4. TARGET is a bare name under the legacy ~/Worlds root
# Resolving through the legacy root prints a one-line deprecation note to
# stderr (Q-03): the canonical layout is ~/Universes/<Universe>/Worlds.
#
# Exported path roots (kept under their historical names so callers do not
# churn):
#   WORLDS_BASE     legacy root  (${HOME}/Worlds)
#   UNIVERSES_BASE  canonical root (${HOME}/Universes)
#
# This file is sourced, never executed. It must stay silent (no output) and
# must never exit on its own.
# ==============================================================================

if [ -n "${SCRIPTORIUM_LIB_WORLDS_SOURCED:-}" ]; then
    return 0
fi
SCRIPTORIUM_LIB_WORLDS_SOURCED=1

WORLDS_BASE="${HOME}/Worlds"
UNIVERSES_BASE="${HOME}/Universes"

# GUI detection works on both X11 and Wayland (M7)
has_gui() {
    { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; } && command -v zenity &> /dev/null
}

# sanitize_name NAME [FALLBACK] -> safe token for filenames and labels
sanitize_name() {
    local safe
    safe="$(printf '%s' "${1:-}" | tr -cd 'A-Za-z0-9_-')"
    [ -z "${safe}" ] && safe="${2:-}"
    printf '%s' "${safe}"
}

# universe_label WORLD_PATH -> owning universe name or "Standalone"
# Standalone detection is structural (path prefix), not identity-based, so it
# is correct for every user, not just the original developer (F-03).
universe_label() {
    local w="${1:-}"
    case "$w" in
        "${WORLDS_BASE}"|"${WORLDS_BASE}/"*)
            printf 'Standalone' ;;
        *)
            printf '%s' "$(basename "$(dirname "$(dirname "$w")")")" ;;
    esac
}

# warn_if_legacy_root WORLD_PATH -> deprecation nudge on stderr (Q-03)
# Single site for the legacy-root message. resolve_world_dir calls it after
# by-name resolution, and every caller that auto-selects a discovered world
# calls it after selection, so a bare invocation that lands on a legacy world
# is nudged too — previously only by-name resolution warned (N-03).
warn_if_legacy_root() {
    case "${1:-}" in
        "${WORLDS_BASE}"|"${WORLDS_BASE}/"*)
            echo "[i] Note: '${1}' uses the legacy ~/Worlds root; the canonical layout is ~/Universes/<Universe>/Worlds." >&2
            ;;
    esac
}

# discover_worlds VARNAME
# Populates VARNAME (an array) with every world directory found under the
# canonical ~/Universes/*/Worlds/* layout, followed by the legacy ~/Worlds/*
# root. NUL-delimited iteration keeps filenames with spaces/newlines intact.
discover_worlds() {
    local -n __discover_out="$1"
    local __d
    __discover_out=()
    while IFS= read -r -d '' __d; do
        [ -d "$__d" ] && __discover_out+=("$__d")
    done < <(find "${UNIVERSES_BASE}" -mindepth 3 -maxdepth 3 -type d -path '*/Worlds/*' -print0 2>/dev/null)
    while IFS= read -r -d '' __d; do
        [ -d "$__d" ] && __discover_out+=("$__d")
    done < <(find "${WORLDS_BASE}" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
}

# resolve_world_dir TARGET [UNIVERSE] -> absolute world path (or empty)
# Callers decide how to fail when nothing is echoed. See the resolution
# contract in the header comment above.
resolve_world_dir() {
    local target="${1:-}"
    local universe="${2:-}"
    local w resolved=""

    if [ -n "${target}" ]; then
        if [ -d "${target}" ]; then
            resolved="$(cd "${target}" && pwd)"
        elif [ -n "${universe}" ] && [ -d "${UNIVERSES_BASE}/${universe}/Worlds/${target}" ]; then
            resolved="$(cd "${UNIVERSES_BASE}/${universe}/Worlds/${target}" && pwd)"
        else
            # Canonical basename search across all Universes
            while IFS= read -r -d '' w; do
                [ -d "$w" ] || continue
                if [ "$(basename "$w")" = "${target}" ]; then
                    resolved="$(cd "$w" && pwd)"
                    break
                fi
            done < <(find "${UNIVERSES_BASE}" -mindepth 3 -maxdepth 3 -type d -path '*/Worlds/*' -print0 2>/dev/null)
            # Legacy root fallback (deprecated layout)
            if [ -z "${resolved}" ] && [ -d "${WORLDS_BASE}/${target}" ]; then
                resolved="$(cd "${WORLDS_BASE}/${target}" && pwd)"
            fi
        fi
    fi

    # Q-03: gentle deprecation nudge when resolution went through ~/Worlds
    warn_if_legacy_root "${resolved}"

    printf '%s' "${resolved}"
}
