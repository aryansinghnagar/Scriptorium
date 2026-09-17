#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Shared Discovery & Resolution Library
# Purpose: Single source of truth for every entry-point script to locate
#          Universes (~/Universes/<Universe>), World Lore Vaults
#          (~/Universes/<Universe>/<World>), and Manuscript Projects
#          (~/Manuscripts/<Manuscript>).
#
# Provided helpers:
#   has_gui                     -> true when a graphical session + zenity exist
#   sanitize_name NAME [FALLBACK]
#                               -> filesystem/label-safe token (A-Za-z0-9_-)
#   universe_label WORLD_PATH   -> owning universe name
#   discover_universes VARNAME  -> populates VARNAME with ~/Universes/* dirs
#   discover_worlds VARNAME     -> populates VARNAME with ~/Universes/*/* dirs
#   discover_manuscripts VARNAME-> populates VARNAME with ~/Manuscripts/* dirs
#   resolve_universe_dir TARGET -> absolute universe path (or empty)
#   resolve_world_dir TARGET [UNIVERSE]
#                               -> absolute world lore vault path (or empty)
#   resolve_manuscript_dir TARGET
#                               -> absolute manuscript project path (or empty)
#
# Exported path roots:
#   UNIVERSES_BASE    (${HOME}/Universes)
#   MANUSCRIPTS_BASE  (${HOME}/Manuscripts)
#
# This file is sourced, never executed. It must stay silent (no output) and
# must never exit on its own.
# ==============================================================================

if [ -n "${SCRIPTORIUM_LIB_WORLDS_SOURCED:-}" ]; then
    return 0
fi
SCRIPTORIUM_LIB_WORLDS_SOURCED=1

UNIVERSES_BASE="${HOME}/Universes"
MANUSCRIPTS_BASE="${HOME}/Manuscripts"
LEGACY_WORLDS_BASE="${HOME}/Worlds"

# GUI detection works on both X11 and Wayland
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

# warn_if_legacy_root WORLD_PATH -> prints deprecation note to stderr if in legacy ~/Worlds
warn_if_legacy_root() {
    local target="${1:-}"
    local leg_base="${LEGACY_WORLDS_BASE:-${HOME}/Worlds}"
    if [ -n "${target}" ] && [[ "${target}" == "${leg_base}"* ]]; then
        echo "[!] Note: '${target}' lives under the legacy ~/Worlds root. Consider migrating to ~/Universes/<Universe>/<World>." >&2
    fi
}

# universe_label WORLD_PATH -> owning universe name
universe_label() {
    local w="${1:-}"
    local leg_base="${LEGACY_WORLDS_BASE:-${HOME}/Worlds}"
    if [ -n "$w" ]; then
        if [[ "$w" == "${leg_base}"* ]]; then
            printf '%s' "Legacy"
        else
            printf '%s' "$(basename "$(dirname "$w")")"
        fi
    fi
}

# discover_universes VARNAME
discover_universes() {
    local -n __u_out="$1"
    local __u
    local u_base="${UNIVERSES_BASE:-${HOME}/Universes}"
    __u_out=()
    while IFS= read -r -d '' __u; do
        [ -d "$__u" ] && __u_out+=("$__u")
    done < <(find "${u_base}" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print0 2>/dev/null | sort -z)
}

# discover_worlds VARNAME
# Populates VARNAME with every World Lore Vault under ~/Universes/<Universe>/<World>
# as well as legacy ~/Worlds/<World>
discover_worlds() {
    local -n __w_out="$1"
    local __w
    local u_base="${UNIVERSES_BASE:-${HOME}/Universes}"
    local leg_base="${LEGACY_WORLDS_BASE:-${HOME}/Worlds}"
    __w_out=()
    while IFS= read -r -d '' __w; do
        [ -d "$__w" ] && __w_out+=("$__w")
    done < <(find "${u_base}" -mindepth 2 -maxdepth 2 -type d ! -name '.*' -print0 2>/dev/null | sort -z)

    if [ -d "${leg_base}" ]; then
        while IFS= read -r -d '' __w; do
            [ -d "$__w" ] && __w_out+=("$__w")
        done < <(find "${leg_base}" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print0 2>/dev/null | sort -z)
    fi
}

# discover_manuscripts VARNAME
# Populates VARNAME with every Manuscript Project under ~/Manuscripts/<Manuscript>
discover_manuscripts() {
    local -n __m_out="$1"
    local __m
    local m_base="${MANUSCRIPTS_BASE:-${HOME}/Manuscripts}"
    __m_out=()
    while IFS= read -r -d '' __m; do
        [ -d "$__m" ] && __m_out+=("$__m")
    done < <(find "${m_base}" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print0 2>/dev/null | sort -z)
}

# resolve_universe_dir TARGET -> absolute universe path (or empty)
resolve_universe_dir() {
    local target="${1:-}"
    local u_base="${UNIVERSES_BASE:-${HOME}/Universes}"
    local resolved=""
    if [ -n "${target}" ]; then
        if [ -d "${target}" ]; then
            resolved="$(cd "${target}" && pwd)"
        elif [ -d "${u_base}/${target}" ]; then
            resolved="$(cd "${u_base}/${target}" && pwd)"
        fi
    fi
    printf '%s' "${resolved}"
}

# resolve_world_dir TARGET [UNIVERSE] -> absolute world path (or empty)
resolve_world_dir() {
    local target="${1:-}"
    local universe="${2:-}"
    local u_base="${UNIVERSES_BASE:-${HOME}/Universes}"
    local leg_base="${LEGACY_WORLDS_BASE:-${HOME}/Worlds}"
    local w resolved=""

    if [ -n "${target}" ]; then
        if [ -d "${target}" ]; then
            resolved="$(cd "${target}" && pwd)"
        elif [ -n "${universe}" ] && [ -d "${u_base}/${universe}/${target}" ]; then
            resolved="$(cd "${u_base}/${universe}/${target}" && pwd)"
        else
            while IFS= read -r -d '' w; do
                [ -d "$w" ] || continue
                if [ "$(basename "$w")" = "${target}" ]; then
                    resolved="$(cd "$w" && pwd)"
                    break
                fi
            done < <(find "${u_base}" -mindepth 2 -maxdepth 2 -type d ! -name '.*' -print0 2>/dev/null | sort -z)

            if [ -z "${resolved}" ] && [ -d "${leg_base}/${target}" ]; then
                resolved="$(cd "${leg_base}/${target}" && pwd)"
            fi
        fi
    fi

    printf '%s' "${resolved}"
}

# resolve_manuscript_dir TARGET -> absolute manuscript path (or empty)
resolve_manuscript_dir() {
    local target="${1:-}"
    local m_base="${MANUSCRIPTS_BASE:-${HOME}/Manuscripts}"
    local resolved=""

    if [ -n "${target}" ]; then
        if [ -d "${target}" ]; then
            resolved="$(cd "${target}" && pwd)"
        elif [ -d "${m_base}/${target}" ]; then
            resolved="$(cd "${m_base}/${target}" && pwd)"
        else
            local m
            while IFS= read -r -d '' m; do
                [ -d "$m" ] || continue
                if [ "$(basename "$m")" = "${target}" ]; then
                    resolved="$(cd "$m" && pwd)"
                    break
                fi
            done < <(find "${m_base}" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print0 2>/dev/null | sort -z)
        fi
    fi

    printf '%s' "${resolved}"
}

