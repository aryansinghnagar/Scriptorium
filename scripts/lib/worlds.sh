#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Shared Discovery & Resolution Library
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
#   resolve_target_dir TARGET [UNIVERSE]
#                               -> universal absolute path resolver for target dirs
#
# Exported path roots:
#   UNIVERSES_BASE    (${HOME}/Universes)
#   MANUSCRIPTS_BASE  (${HOME}/Manuscripts)
#
# This file is sourced, never executed. It must stay silent (no output) and
# must never exit on its own.
# ==============================================================================

if [ -n "${ARCANUM_LIB_WORLDS_SOURCED:-}" ] || [ -n "${SCRIPTORIUM_LIB_WORLDS_SOURCED:-}" ]; then
    return 0
fi
ARCANUM_LIB_WORLDS_SOURCED=1
SCRIPTORIUM_LIB_WORLDS_SOURCED=1

UNIVERSES_BASE="${UNIVERSES_BASE:-${HOME}/Universes}"
MANUSCRIPTS_BASE="${MANUSCRIPTS_BASE:-${HOME}/Manuscripts}"
LEGACY_WORLDS_BASE="${LEGACY_WORLDS_BASE:-${HOME}/Worlds}"
# RES-01: set to 1 by resolvers when a name is ambiguous, so
# resolve_target_dir does not fall through to a different project type.
ARCANUM_RESOLVE_AMBIGUOUS=0

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
    local u_base="${UNIVERSES_BASE:-${HOME}/Universes}"
    if [ -n "$w" ]; then
        if [[ "$w" == "${leg_base}"* ]]; then
            printf '%s' "Legacy"
        elif [[ "$w" == "${u_base}"/* ]]; then
            local rel="${w#"${u_base}/"}"
            printf '%s' "${rel%%/*}"
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
# Populates VARNAME with every World Lore Vault under ~/Universes/<Universe>/<World>,
# legacy subfolder ~/Universes/<Universe>/Worlds/<World>, and legacy ~/Worlds/<World>
discover_worlds() {
    local -n __w_out="$1"
    local __w
    local u_base="${UNIVERSES_BASE:-${HOME}/Universes}"
    local leg_base="${LEGACY_WORLDS_BASE:-${HOME}/Worlds}"
    __w_out=()

    if [ -d "${u_base}" ]; then
        # 1. Direct universe worlds: ~/Universes/<Universe>/<World> (excluding Worlds and .git)
        while IFS= read -r -d '' __w; do
            [ -d "$__w" ] || continue
            local bname
            bname="$(basename "$__w")"
            if [ "$bname" = "Worlds" ] || [ "$bname" = ".git" ]; then
                continue
            fi
            __w_out+=("$__w")
        done < <(find "${u_base}" -mindepth 2 -maxdepth 2 -type d ! -name '.*' -print0 2>/dev/null | sort -z)

        # 2. Legacy subfolder worlds: ~/Universes/<Universe>/Worlds/<World>
        while IFS= read -r -d '' __w; do
            [ -d "$__w" ] || continue
            local bname
            bname="$(basename "$__w")"
            if [ "$bname" = ".git" ]; then
                continue
            fi
            __w_out+=("$__w")
        done < <(find "${u_base}" -mindepth 3 -maxdepth 3 -type d -path '*/Worlds/*' ! -name '.*' -print0 2>/dev/null | sort -z)
    fi

    # 3. Legacy root worlds: ~/Worlds/<World>
    if [ -d "${leg_base}" ]; then
        while IFS= read -r -d '' __w; do
            [ -d "$__w" ] || continue
            local bname
            bname="$(basename "$__w")"
            if [ "$bname" = ".git" ]; then
                continue
            fi
            __w_out+=("$__w")
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
# RES-01: ambiguous names fail closed. When TARGET matches worlds in more
# than one universe and no explicit UNIVERSE filter was given, prints all
# conflicting paths to stderr and returns empty so callers exit 2 instead
# of silently operating on the wrong project.
resolve_world_dir() {
    local target="${1:-}"
    local universe="${2:-}"
    local u_base="${UNIVERSES_BASE:-${HOME}/Universes}"
    local leg_base="${LEGACY_WORLDS_BASE:-${HOME}/Worlds}"
    local w resolved=""
    local -a __matches=()

    if [ -n "${target}" ]; then
        if [ -d "${target}" ]; then
            resolved="$(cd "${target}" && pwd)"
        elif [ -n "${universe}" ] && [ -d "${u_base}/${universe}/${target}" ]; then
            resolved="$(cd "${u_base}/${universe}/${target}" && pwd)"
        elif [ -n "${universe}" ] && [ -d "${u_base}/${universe}/Worlds/${target}" ]; then
            resolved="$(cd "${u_base}/${universe}/Worlds/${target}" && pwd)"
        else
            # 1. Search direct ~/Universes/<Universe>/<World>
            while IFS= read -r -d '' w; do
                [ -d "$w" ] || continue
                local bname
                bname="$(basename "$w")"
                if [ "$bname" = "Worlds" ] || [ "$bname" = ".git" ]; then
                    continue
                fi
                if [ "$bname" = "${target}" ]; then
                    __matches+=("$(cd "$w" && pwd)")
                fi
            done < <(find "${u_base}" -mindepth 2 -maxdepth 2 -type d ! -name '.*' -print0 2>/dev/null | sort -z)

            # 2. Search legacy subfolder ~/Universes/<Universe>/Worlds/<World>
            while IFS= read -r -d '' w; do
                [ -d "$w" ] || continue
                local bname
                bname="$(basename "$w")"
                if [ "$bname" = ".git" ]; then
                    continue
                fi
                if [ "$bname" = "${target}" ]; then
                    __matches+=("$(cd "$w" && pwd)")
                fi
            done < <(find "${u_base}" -mindepth 3 -maxdepth 3 -type d -path '*/Worlds/*' ! -name '.*' -print0 2>/dev/null | sort -z)

            # 3. Search legacy root ~/Worlds/<World>
            if [ -d "${leg_base}/${target}" ]; then
                __matches+=("$(cd "${leg_base}/${target}" && pwd)")
            fi

            if [ ${#__matches[@]} -eq 1 ]; then
                resolved="${__matches[0]}"
            elif [ ${#__matches[@]} -gt 1 ]; then
                {
                    echo "Error: Ambiguous world name '${target}' matches ${#__matches[@]} projects:"
                    for w in "${__matches[@]}"; do
                        echo "  - ${w}"
                    done
                    echo "Re-run with an explicit universe (e.g. --universe <Name>) or an absolute path."
                } >&2
                resolved=""
                ARCANUM_RESOLVE_AMBIGUOUS=1
            fi
        fi
    fi

    printf '%s' "${resolved}"
}

# resolve_manuscript_dir TARGET -> absolute manuscript path (or empty)
# RES-01: same ambiguity rule as worlds — multiple basename matches fail
# closed with a stderr listing instead of returning the first hit.
resolve_manuscript_dir() {
    local target="${1:-}"
    local m_base="${MANUSCRIPTS_BASE:-${HOME}/Manuscripts}"
    local resolved=""
    local -a __matches=()

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
                    __matches+=("$(cd "$m" && pwd)")
                fi
            done < <(find "${m_base}" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print0 2>/dev/null | sort -z)
            if [ ${#__matches[@]} -eq 1 ]; then
                resolved="${__matches[0]}"
            elif [ ${#__matches[@]} -gt 1 ]; then
                {
                    echo "Error: Ambiguous manuscript name '${target}' matches ${#__matches[@]} projects:"
                    for m in "${__matches[@]}"; do
                        echo "  - ${m}"
                    done
                    echo "Re-run with an absolute path."
                } >&2
                resolved=""
                ARCANUM_RESOLVE_AMBIGUOUS=1
            fi
        fi
    fi

    printf '%s' "${resolved}"
}

# resolve_target_dir TARGET [UNIVERSE] -> universal absolute path resolver
# Resolves a target name or path into an absolute path for a world lore vault,
# manuscript project, or universe directory. RES-01: command substitutions
# run resolvers in subshells, so ambiguity cannot propagate via globals.
# Instead, when no universe filter is given, pre-count world basename
# matches here: if >1, resolve_world_dir already printed the conflict list
# to stderr, and we return empty without falling through to a manuscript
# or universe with the same basename.
resolve_target_dir() {
    local target="${1:-}"
    local universe="${2:-}"
    local resolved=""

    if [ -n "${target}" ]; then
        if [ -d "${target}" ]; then
            resolved="$(cd "${target}" && pwd)"
        else
            if [ -n "${universe}" ]; then
                resolved="$(resolve_world_dir "${target}" "${universe}")"
                [ -z "${resolved}" ] && resolved="$(resolve_universe_dir "${target}")"
            fi
            if [ -z "${resolved}" ] || [ ! -d "${resolved}" ]; then
                resolved="$(resolve_manuscript_dir "${target}")"
            fi
            if { [ -z "${resolved}" ] || [ ! -d "${resolved}" ]; } && [ -z "${universe}" ]; then
                # Ambiguity pre-check: count world matches without resolving.
                local __u_base="${UNIVERSES_BASE:-${HOME}/Universes}"
                local __leg_base="${LEGACY_WORLDS_BASE:-${HOME}/Worlds}"
                local __n=0 __w
                while IFS= read -r -d '' __w; do
                    [ -d "$__w" ] || continue
                    [ "$(basename "$__w")" = "Worlds" ] && continue
                    [ "$(basename "$__w")" = ".git" ] && continue
                    [ "$(basename "$__w")" = "${target}" ] && __n=$((__n+1))
                done < <(find "${__u_base}" -mindepth 2 -maxdepth 2 -type d ! -name '.*' -print0 2>/dev/null | sort -z)
                while IFS= read -r -d '' __w; do
                    [ -d "$__w" ] || continue
                    [ "$(basename "$__w")" = ".git" ] && continue
                    [ "$(basename "$__w")" = "${target}" ] && __n=$((__n+1))
                done < <(find "${__u_base}" -mindepth 3 -maxdepth 3 -type d -path '*/Worlds/*' ! -name '.*' -print0 2>/dev/null | sort -z)
                [ -d "${__leg_base}/${target}" ] && __n=$((__n+1))
                if [ "${__n}" -gt 1 ]; then
                    resolved="$(resolve_world_dir "${target}" "${universe}")"
                    printf '%s' "${resolved}"
                    return 0
                fi
            fi
            if [ -z "${resolved}" ] || [ ! -d "${resolved}" ]; then
                resolved="$(resolve_world_dir "${target}" "${universe}")"
            fi
            if [ -z "${resolved}" ] || [ ! -d "${resolved}" ]; then
                resolved="$(resolve_universe_dir "${target}")"
            fi
        fi
    fi

    printf '%s' "${resolved}"
}

