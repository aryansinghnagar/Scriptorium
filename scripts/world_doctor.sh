#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum World Doctor (D-01 / Workstream 3.2)
# Purpose: Consistency checker for the Obsidian World Bible. Verifies wiki-link
#          integrity, typed frontmatter references, orphaned entities,
#          duplicate identities, and timeline chronology.
#
# Usage:
#   world_doctor.sh [WORLD_DIR] [OPTIONS]
#
# Options:
#   -m, --manuscript NAME  Specify manuscript project for cross-validation
#   --fast                 Accelerate scans using mtime-keyed in-memory caching
#   --json                 Emit a machine-readable JSON report instead of text
#   -h, --help             Show this help
#
# Exit codes:
#   0  no findings / consistent world
#   1  findings reported (broken links, orphans, dangling references, etc.)
#   2  usage or environment error (world dir missing, python3 missing)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Shared world discovery, resolution, and GUI helpers (Q-01, F-05)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Ars Arcanum World Doctor (D-01 / Workstream 3.2)
Purpose: Consistency checker for the Obsidian World Bible. Verifies wiki-link
         integrity, typed frontmatter references, orphaned entities,
         duplicate identities, and timeline chronology.

Usage:
  world_doctor.sh [WORLD_DIR] [OPTIONS]

Options:
  -m, --manuscript NAME  Specify manuscript project for cross-validation
  --fast                 Accelerate scans using mtime-keyed in-memory caching
  --json                 Emit a machine-readable JSON report instead of text
  -h, --help             Show this help

Exit codes:
  0  no findings / consistent world
  1  findings reported (broken links, orphans, dangling references, etc.)
  2  usage or environment error (world dir missing, python3 missing)
USAGE
}

WORLD_DIR=""
MANUSCRIPT_DIR_CLI=""
OUTPUT_JSON=0
USE_FAST_CACHE=0
while [ $# -gt 0 ]; do
    case "$1" in
        --fast) USE_FAST_CACHE=1; shift ;;
        --json) OUTPUT_JSON=1; shift ;;
        -m|--manuscript)
            [ $# -ge 2 ] || { echo "Error: --manuscript requires a value." >&2; exit 2; }
            MANUSCRIPT_DIR_CLI="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
        *) WORLD_DIR="$1"; shift ;;
    esac
done

if [ -z "${WORLD_DIR}" ]; then
    discover_worlds FOUND_WORLDS
    if [ ${#FOUND_WORLDS[@]} -eq 1 ]; then
        WORLD_DIR="${FOUND_WORLDS[0]}"
        warn_if_legacy_root "${WORLD_DIR}"
    elif [ ${#FOUND_WORLDS[@]} -gt 1 ]; then
        {
            echo "Multiple worlds discovered — specify one:"
            for w in "${FOUND_WORLDS[@]}"; do
                echo "  - $(basename "$w")  [$(universe_label "$w")]  ${w}"
            done
            echo "Usage: world_doctor.sh <WORLD_DIR|WORLD_NAME> [--json]"
        } >&2
        exit 2
    else
        echo "Error: no worlds found under ~/Universes or ~/Worlds. Create one first (arcanum world <name>)." >&2
        exit 2
    fi
else
    RESOLVED="$(resolve_world_dir "${WORLD_DIR}")"
    if [ -n "${RESOLVED}" ]; then
        WORLD_DIR="${RESOLVED}"
    fi
fi

if [ ! -d "${WORLD_DIR}" ]; then
    echo "Error: world directory not found: ${WORLD_DIR}" >&2
    exit 2
fi

if [ -d "${WORLD_DIR}/00-World-Bible" ]; then
    BIBLE_DIR="${WORLD_DIR}/00-World-Bible"
elif [ -d "${WORLD_DIR}/Characters" ] || [ -f "${WORLD_DIR}/world.yaml" ] || [ -d "${WORLD_DIR}/.obsidian" ]; then
    BIBLE_DIR="${WORLD_DIR}"
else
    echo "Error: no World Bible lore found in ${WORLD_DIR} (is this an Ars Arcanum world?)" >&2
    exit 2
fi

MANUSCRIPT_DIR=""
if [ -n "${MANUSCRIPT_DIR_CLI}" ]; then
    RESOLVED_MS="$(resolve_manuscript_dir "${MANUSCRIPT_DIR_CLI}")"
    [ -n "${RESOLVED_MS}" ] && MANUSCRIPT_DIR="${RESOLVED_MS}"
fi

if [ -z "${MANUSCRIPT_DIR}" ]; then
    if [ -d "${WORLD_DIR}/01-Manuscript" ]; then
        MANUSCRIPT_DIR="${WORLD_DIR}/01-Manuscript"
    else
        WNAME="$(basename "${WORLD_DIR}")"
        discover_manuscripts FOUND_MS
        for m in "${FOUND_MS[@]}"; do
            m_manifest="${m}/manuscript.yaml"
            [ -f "${m_manifest}" ] || m_manifest="${m}/arcanum.yaml"
            [ -f "${m_manifest}" ] || m_manifest="${m}/scriptorium.yaml"
            if [ -f "${m_manifest}" ]; then
                mw=$(sed -n -E 's/^world:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "${m_manifest}" | head -n 1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                if [ "$mw" = "$WNAME" ]; then
                    MANUSCRIPT_DIR="$m"
                    break
                fi
            fi
        done
    fi
fi

# Delegate directly to modular Python engine
PY_ARGS=("${BIBLE_DIR}")
if [ -n "${MANUSCRIPT_DIR}" ]; then
    PY_ARGS+=("-m" "${MANUSCRIPT_DIR}")
fi
if [ "${OUTPUT_JSON}" -eq 1 ]; then
    PY_ARGS+=("--json")
fi
if [ "${USE_FAST_CACHE}" -eq 1 ]; then
    PY_ARGS+=("--fast")
fi

exec python3 "${SCRIPT_DIR}/lib/world_doctor.py" "${PY_ARGS[@]}"
