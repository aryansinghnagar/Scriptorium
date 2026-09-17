#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Control Center (Workstream 4.2)
# Purpose: Lightweight desktop GUI dashboard for universe/world switching and 1-click actions.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

# Prefer native GTK 3 desktop application if PyGObject is available
if command -v python3 &>/dev/null && [ -f "${SCRIPT_DIR}/scriptorium_app.py" ]; then
    set +e
    python3 "${SCRIPT_DIR}/scriptorium_app.py" "$@"
    APP_RC=$?
    set -e
    if [ "${APP_RC}" -ne 2 ]; then
        exit "${APP_RC}"
    fi
fi

if ! has_gui; then
    echo "Scriptorium Control Center requires a graphical display and Zenity (or PyGObject)."
    echo "Use the 'scriptorium' command line interface in terminal environments."
    exit 2
fi

mkdir -p "${UNIVERSES_BASE}"
mkdir -p "${MANUSCRIPTS_BASE}"
mkdir -p "${LEGACY_WORLDS_BASE}"

# Discover all worlds
discover_worlds WORLDS_PATHS

ACTIVE_WORLD_PATH=""

if [ ${#WORLDS_PATHS[@]} -eq 0 ]; then
    CHOICE=$(zenity --list --title="Scriptorium Control Center" \
        --text="No worlds found.\nWhat would you like to create?" \
        --column="Action" --column="Description" \
        --width=450 --height=220 \
        "1. Create New World" "Scaffold your first world" \
        "2. Create New Universe" "Create a narrative universe container" || true)
    case "${CHOICE}" in
        "1. Create New World")
            bash "${PROJECT_ROOT}/scripts/init_world.sh"
            exit 0 ;;
        "2. Create New Universe")
            bash "${PROJECT_ROOT}/scripts/init_universe.sh"
            exit 0 ;;
        *) exit 0 ;;
    esac
elif [ ${#WORLDS_PATHS[@]} -eq 1 ]; then
    ACTIVE_WORLD_PATH="${WORLDS_PATHS[0]}"
else
    CHOICES=()
    for w in "${WORLDS_PATHS[@]}"; do
        WNAME="$(basename "$w")"
        CHOICES+=("$WNAME" "Universe: $(universe_label "$w")")
    done
    CHOICES+=("+ Create New World" "Add a new world")
    CHOICES+=("+ Create New Universe" "Add a new universe container")

    SELECTED_CHOICE=$(zenity --list --title="Scriptorium — Select Active World" \
        --column="World Name" --column="Universe" \
        --width=460 --height=340 \
        "${CHOICES[@]}" || true)

    if [ -z "${SELECTED_CHOICE}" ]; then
        exit 0
    fi

    if [ "${SELECTED_CHOICE}" = "+ Create New World" ]; then
        bash "${PROJECT_ROOT}/scripts/init_world.sh"
        exit 0
    elif [ "${SELECTED_CHOICE}" = "+ Create New Universe" ]; then
        bash "${PROJECT_ROOT}/scripts/init_universe.sh"
        exit 0
    else
        for w in "${WORLDS_PATHS[@]}"; do
            if [ "$(basename "$w")" = "${SELECTED_CHOICE}" ]; then
                ACTIVE_WORLD_PATH="$w"
                break
            fi
        done
    fi
fi

if [ -z "${ACTIVE_WORLD_PATH}" ] || [ ! -d "${ACTIVE_WORLD_PATH}" ]; then
    exit 0
fi

WORLD_DIR="${ACTIVE_WORLD_PATH}"
ACTIVE_WORLD="$(basename "${WORLD_DIR}")"
UNIVERSE_NAME="$(universe_label "${WORLD_DIR}")"

ACTION=$(zenity --list --title="Scriptorium Control Center — [${ACTIVE_WORLD} (${UNIVERSE_NAME})]" \
    --column="Action" --column="Description" \
    --width=540 --height=400 \
    "1. Write: Obsidian" "Open World Bible in Obsidian (Plugins & Lore)" \
    "2. Write: novelWriter" "Open Manuscript in novelWriter" \
    "3. Export Book" "Compile manuscript to print PDF and EPUB" \
    "4. Generate Concordance" "Generate Dramatis Personae & Glossary back-matter" \
    "5. Add Manuscript Volume" "Scaffold a new book volume (Book-02, etc.)" \
    "6. Save Snapshot" "Record a point-in-time Git version" \
    "7. Backup Archive" "Create standalone verified .tar.gz backup" \
    "8. Run Diagnostics" "Check world consistency and system health" \
    "9. Word Count Report" "View manuscript progress analytics" \
    "10. New World" "Scaffold a brand new world" \
    "11. New Universe" "Create a new universe container" || true)

[ -z "${ACTION}" ] && exit 0

case "${ACTION}" in
    "1. Write: Obsidian")
        OBS_TARGET="${WORLD_DIR}"
        [ -d "${WORLD_DIR}/00-World-Bible" ] && OBS_TARGET="${WORLD_DIR}/00-World-Bible"
        if command -v flatpak &>/dev/null && flatpak info md.obsidian.Obsidian &>/dev/null; then
            flatpak run md.obsidian.Obsidian "${OBS_TARGET}" &
        elif command -v obsidian &>/dev/null; then
            obsidian "${OBS_TARGET}" &
        else
            xdg-open "${OBS_TARGET}" &
        fi
        ;;
    "2. Write: novelWriter")
        NW_PROJ=""
        if [ -f "${WORLD_DIR}/01-Manuscript/nwProject.nwx" ]; then
            NW_PROJ="${WORLD_DIR}/01-Manuscript/nwProject.nwx"
        elif [ -f "${WORLD_DIR}/nwProject.nwx" ]; then
            NW_PROJ="${WORLD_DIR}/nwProject.nwx"
        elif [ -d "${MANUSCRIPTS_BASE}/${ACTIVE_WORLD}" ] && [ -f "${MANUSCRIPTS_BASE}/${ACTIVE_WORLD}/nwProject.nwx" ]; then
            NW_PROJ="${MANUSCRIPTS_BASE}/${ACTIVE_WORLD}/nwProject.nwx"
        fi
        if [ -n "${NW_PROJ}" ]; then
            if command -v flatpak &>/dev/null && flatpak info io.gitlab.novelwriter.novelWriter &>/dev/null; then
                flatpak run io.gitlab.novelwriter.novelWriter "${NW_PROJ}" &
            elif command -v novelwriter &>/dev/null; then
                novelwriter "${NW_PROJ}" &
            else
                xdg-open "$(dirname "${NW_PROJ}")" &
            fi
        else
            zenity --info --title="Manuscript Project" --text="No novelWriter project found for '${ACTIVE_WORLD}'.\nCreate one with 'scriptorium manuscript <name>'." --width=400
        fi
        ;;
    "3. Export Book")
        bash "${PROJECT_ROOT}/scripts/export_book.sh" "${WORLD_DIR}"
        ;;
    "4. Generate Concordance")
        bash "${PROJECT_ROOT}/scripts/generate_concordance.sh" "${WORLD_DIR}"
        ;;
    "5. Add Manuscript Volume")
        bash "${PROJECT_ROOT}/scripts/add_book.sh" "${WORLD_DIR}"
        ;;
    "6. Save Snapshot")
        bash "${PROJECT_ROOT}/scripts/save_snapshot.sh" --world "${ACTIVE_WORLD}"
        ;;
    "7. Backup Archive")
        bash "${PROJECT_ROOT}/scripts/backup_world.sh" --world "${ACTIVE_WORLD}"
        ;;
    "8. Run Diagnostics")
        # TST-03: capture output AND exit code explicitly (no `|| true`
        # masking) so findings (exit 1) are visible in the dialog title.
        set +e
        REPORT=$(bash "${PROJECT_ROOT}/scripts/world_doctor.sh" "${WORLD_DIR}" 2>&1)
        DOCTOR_RC=$?
        set -e
        [ "${DOCTOR_RC}" -ne 0 ] && REPORT="[world_doctor exit ${DOCTOR_RC}]"$'\n'"${REPORT}"
        zenity --text-info --title="World Doctor — ${ACTIVE_WORLD}" \
            --width=600 --height=450 \
            --filename=<(printf '%s\n' "${REPORT}")
        ;;
    "9. Word Count Report")
        set +e
        REPORT=$(bash "${PROJECT_ROOT}/scripts/wordcount_report.sh" "${WORLD_DIR}" 2>&1)
        REPORT_RC=$?
        set -e
        [ "${REPORT_RC}" -ne 0 ] && REPORT="[wordcount exit ${REPORT_RC}]"$'\n'"${REPORT}"
        zenity --text-info --title="Wordcount Report — ${ACTIVE_WORLD}" \
            --width=600 --height=450 \
            --filename=<(printf '%s\n' "${REPORT}")
        ;;
    "10. New World")
        bash "${PROJECT_ROOT}/scripts/init_world.sh"
        ;;
    "11. New Universe")
        bash "${PROJECT_ROOT}/scripts/init_universe.sh"
        ;;
esac

exit 0
