#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Uninstaller & Rollback Utility (SEC-02)
# Purpose: Safely removes Scriptorium desktop launchers, system binaries,
#          and optionally purges installed Flatpak applications.
# ==============================================================================

set -euo pipefail

usage() {
    cat << 'USAGE'
Scriptorium Uninstaller & Rollback Utility

Usage:
  uninstall_scriptorium.sh [OPTIONS]

Options:
  --dry-run          Simulate and log all removal operations without deleting files
  --purge-flatpaks   Also uninstall Flatpak apps (Obsidian, novelWriter, Calibre)
  -f, --force        Proceed without interactive confirmation
  -h, --help         Show this help and exit

Note: Your user writing projects in ~/Universes, ~/Manuscripts, and legacy
~/Worlds are NEVER deleted by this script.
USAGE
}

DRY_RUN=0
PURGE_FLATPAKS=0
FORCE_PROMPT=0

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN=1; shift ;;
        --purge-flatpaks)
            PURGE_FLATPAKS=1; shift ;;
        -f|--force)
            FORCE_PROMPT=1; shift ;;
        -h|--help)
            usage; exit 0 ;;
        *)
            echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
    esac
done

echo "============================================================"
echo "  Scriptorium — System Uninstaller & Rollback"
if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [MODE: DRY-RUN SIMULATION — No files will be deleted]"
fi
echo "============================================================"

if [ "${FORCE_PROMPT}" -eq 0 ] && [ "${DRY_RUN}" -eq 0 ]; then
    if [ -t 0 ]; then
        read -rp "Are you sure you want to uninstall Scriptorium launchers and components? [y/N]: " CONFIRM
        case "${CONFIRM:-n}" in
            y|Y|yes|YES) ;;
            *) echo "Uninstall canceled."; exit 0 ;;
        esac
    fi
fi

DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "${HOME}/Desktop")"
APP_DIR="${HOME}/.local/share/applications"

LAUNCHER_FILES=(
    "init-world.desktop"
    "init-manuscript.desktop"
    "export-book.desktop"
    "save-snapshot.desktop"
    "scriptorium-control-center.desktop"
)

echo "[1/3] Removing desktop launchers..."
for lf in "${LAUNCHER_FILES[@]}"; do
    # Remove from desktop
    if [ -f "${DESKTOP_DIR}/${lf}" ]; then
        if [ "${DRY_RUN}" -eq 1 ]; then
            echo "  [DRY-RUN] Would remove: ${DESKTOP_DIR}/${lf}"
        else
            rm -f "${DESKTOP_DIR}/${lf}"
            echo "  [✓] Removed ${DESKTOP_DIR}/${lf}"
        fi
    fi

    # Remove from applications menu
    if [ -f "${APP_DIR}/${lf}" ]; then
        if [ "${DRY_RUN}" -eq 1 ]; then
            echo "  [DRY-RUN] Would remove: ${APP_DIR}/${lf}"
        else
            rm -f "${APP_DIR}/${lf}"
            echo "  [✓] Removed ${APP_DIR}/${lf}"
        fi
    fi
done

echo "[2/3] Checking Typst binary..."
if [ -f "/usr/local/bin/typst" ]; then
    if [ "${DRY_RUN}" -eq 1 ]; then
        echo "  [DRY-RUN] Would remove: /usr/local/bin/typst"
    else
        if command -v sudo &>/dev/null; then
            echo "  Removing /usr/local/bin/typst (requires sudo)..."
            sudo rm -f "/usr/local/bin/typst"
            echo "  [✓] Removed /usr/local/bin/typst"
        else
            echo "  [!] sudo not available; please manually remove /usr/local/bin/typst if desired."
        fi
    fi
else
    echo "  [i] No Scriptorium-installed Typst binary found at /usr/local/bin/typst"
fi

echo "[3/3] Handling Flatpak applications..."
if [ "${PURGE_FLATPAKS}" -eq 1 ]; then
    FLATPAKS=("md.obsidian.Obsidian" "io.gitlab.novelwriter.novelWriter" "com.calibre_ebook.calibre")
    for app in "${FLATPAKS[@]}"; do
        if [ "${DRY_RUN}" -eq 1 ]; then
            echo "  [DRY-RUN] Would uninstall Flatpak: ${app}"
        else
            echo "  Uninstalling ${app}..."
            flatpak uninstall -y "$app" 2>/dev/null || true
        fi
    done
else
    echo "  [i] Flatpak applications retained (pass --purge-flatpaks to remove them)."
fi

echo ""
echo "============================================================"
if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [DRY-RUN COMPLETE] Rollback simulation finished successfully."
else
    echo "  [SUCCESS] Scriptorium uninstallation complete."
    echo "  User writing data in ~/Universes, ~/Manuscripts, and legacy ~/Worlds remains intact and preserved."
fi
echo "============================================================"
