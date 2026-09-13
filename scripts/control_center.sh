#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Control Center (Workstream 4.2)
# Purpose: Lightweight desktop GUI dashboard for universe/world switching and 1-click actions.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORLDS_BASE="${HOME}/Worlds"
UNIVERSES_BASE="${HOME}/Universes"

has_gui() {
    { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; } && command -v zenity &> /dev/null
}

if ! has_gui; then
    echo "Scriptorium Control Center requires a graphical display and Zenity."
    echo "Use the 'scriptorium' command line interface in terminal environments."
    exit 1
fi

mkdir -p "${UNIVERSES_BASE}"
mkdir -p "${WORLDS_BASE}"

# Discover all worlds
WORLDS_PATHS=()
while IFS= read -r -d '' d; do
    [ -d "$d" ] && WORLDS_PATHS+=("$d")
done < <(find "${UNIVERSES_BASE}" -mindepth 3 -maxdepth 3 -type d -path '*/Worlds/*' -print0 2>/dev/null)

while IFS= read -r -d '' d; do
    [ -d "$d" ] && WORLDS_PATHS+=("$d")
done < <(find "${WORLDS_BASE}" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)

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
        UNAME="$(basename "$(dirname "$(dirname "$w")")")"
        [ "$UNAME" = "home" ] || [ "$UNAME" = "aryan" ] && UNAME="Standalone"
        CHOICES+=("$WNAME" "Universe: ${UNAME}")
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
UNIVERSE_NAME="$(basename "$(dirname "$(dirname "${WORLD_DIR}")")")"
[ "$UNIVERSE_NAME" = "home" ] || [ "$UNIVERSE_NAME" = "aryan" ] && UNIVERSE_NAME="Standalone"

ACTION=$(zenity --list --title="Scriptorium Control Center — [${ACTIVE_WORLD} (${UNIVERSE_NAME})]" \
    --column="Action" --column="Description" \
    --width=540 --height=400 \
    "1. Write: Obsidian" "Open World Bible in Obsidian (Plugins & Lore)" \
    "2. Write: novelWriter" "Open Manuscript in novelWriter" \
    "3. Export Book" "Compile manuscript to print PDF and EPUB" \
    "4. Save Snapshot" "Record a point-in-time Git version" \
    "5. Backup Archive" "Create standalone verified .tar.gz backup" \
    "6. Run Diagnostics" "Check world consistency and system health" \
    "7. Word Count Report" "View manuscript progress analytics" \
    "8. New World" "Scaffold a brand new world" \
    "9. New Universe" "Create a new universe container" || true)

[ -z "${ACTION}" ] && exit 0

case "${ACTION}" in
    "1. Write: Obsidian")
        if command -v flatpak &>/dev/null && flatpak info md.obsidian.Obsidian &>/dev/null; then
            flatpak run md.obsidian.Obsidian "${WORLD_DIR}/00-World-Bible" &
        elif command -v obsidian &>/dev/null; then
            obsidian "${WORLD_DIR}/00-World-Bible" &
        else
            xdg-open "${WORLD_DIR}/00-World-Bible" &
        fi
        ;;
    "2. Write: novelWriter")
        NW_PROJ="${WORLD_DIR}/01-Manuscript/nwProject.nwx"
        if command -v flatpak &>/dev/null && flatpak info io.gitlab.novelwriter.novelWriter &>/dev/null; then
            flatpak run io.gitlab.novelwriter.novelWriter "${NW_PROJ}" &
        elif command -v novelwriter &>/dev/null; then
            novelwriter "${NW_PROJ}" &
        else
            xdg-open "${WORLD_DIR}/01-Manuscript" &
        fi
        ;;
    "3. Export Book")
        bash "${PROJECT_ROOT}/scripts/export_book.sh" "${WORLD_DIR}"
        ;;
    "4. Save Snapshot")
        bash "${PROJECT_ROOT}/scripts/save_snapshot.sh" --world "${ACTIVE_WORLD}"
        ;;
    "5. Backup Archive")
        bash "${PROJECT_ROOT}/scripts/backup_world.sh" --world "${ACTIVE_WORLD}"
        ;;
    "6. Run Diagnostics")
        REPORT=$(bash "${PROJECT_ROOT}/scripts/world_doctor.sh" "${WORLD_DIR}" 2>&1 || true)
        zenity --text-info --title="World Doctor — ${ACTIVE_WORLD}" \
            --width=600 --height=450 \
            --filename=<(printf '%s\n' "${REPORT}")
        ;;
    "7. Word Count Report")
        REPORT=$(bash "${PROJECT_ROOT}/scripts/wordcount_report.sh" "${WORLD_DIR}" 2>&1 || true)
        zenity --text-info --title="Wordcount Report — ${ACTIVE_WORLD}" \
            --width=600 --height=450 \
            --filename=<(printf '%s\n' "${REPORT}")
        ;;
    "8. New World")
        bash "${PROJECT_ROOT}/scripts/init_world.sh"
        ;;
    "9. New Universe")
        bash "${PROJECT_ROOT}/scripts/init_universe.sh"
        ;;
esac

exit 0
