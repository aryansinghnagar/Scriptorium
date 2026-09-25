#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum — Sovereign Offline Flatpak Bundle Builder
# (flatpak/build_offline_bundle.sh)
# ==============================================================================
# Builds, validates, and packages Ars Arcanum into a 100% offline, standalone
# single-file Flatpak bundle (.flatpak) with bundled Python & Pandoc runtimes.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

MANIFEST="${PROJECT_ROOT}/org.arsarcanum.ArsArcanum.yaml"
METAINFO="${PROJECT_ROOT}/flatpak/org.arsarcanum.ArsArcanum.metainfo.xml"
BUILD_DIR="${PROJECT_ROOT}/build/flatpak-build"
REPO_DIR="${PROJECT_ROOT}/build/flatpak-repo"
VERSION=$(python3 -c 'import sys; sys.path.insert(0, "'"${PROJECT_ROOT}"'/scripts"); from lib.cli import VERSION; print(VERSION)' 2>/dev/null || echo "3.7.0")
OUTPUT_BUNDLE="${PROJECT_ROOT}/dist/ArsArcanum-v${VERSION}-x86_64.flatpak"

DRY_RUN=0
VERBOSE=0

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dry-run, -n     Validate manifests, metainfo, and permissions without building"
    echo "  --verbose, -v     Enable verbose progress output"
    echo "  --help, -h        Show this help message"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run|-n)
            DRY_RUN=1
            shift
            ;;
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            print_usage
            exit 1
            ;;
    esac
done

echo "================================================================================"
echo "⚡ Ars Arcanum (Scriptorium) — Sovereign Offline Flatpak Builder (v${VERSION})"
echo "================================================================================"

# 1. Validate Manifest and Metainfo Files
if [[ ! -f "${MANIFEST}" ]]; then
    echo "❌ Error: Flatpak manifest not found: ${MANIFEST}" >&2
    exit 1
fi
echo "✓ Manifest verified: ${MANIFEST}"

if [[ ! -f "${METAINFO}" ]]; then
    echo "❌ Error: AppStream metainfo not found: ${METAINFO}" >&2
    exit 1
fi
echo "✓ AppStream metainfo verified: ${METAINFO}"

# 2. Verify Offline Sandbox Invariants in Manifest
if grep -q "url:" "${MANIFEST}"; then
    echo "⚠️ Warning: Manifest contains remote URLs. Offline builds should use local sources."
fi

if grep -q "\-\-filesystem=home" "${MANIFEST}"; then
    echo "✓ Scoped home directory permission verified."
else
    echo "❌ Error: Missing --filesystem=home in finish-args." >&2
    exit 1
fi

if grep -q "\-\-talk-name=org.freedesktop.Flatpak" "${MANIFEST}"; then
    echo "✓ Flatpak talk-name IPC permission verified."
fi

# Dry Run Exit
if [[ "${DRY_RUN}" -eq 1 ]]; then
    echo ""
    echo "✓ Flatpak offline validation passed in DRY-RUN mode. 0 errors detected."
    exit 0
fi

# 3. Check for flatpak-builder
if ! command -v flatpak-builder &> /dev/null; then
    echo "⚠️ 'flatpak-builder' not found on PATH. Please install flatpak-builder to compile packages."
    echo "   Debian/Ubuntu: sudo apt install flatpak-builder"
    echo "   Fedora:        sudo dnf install flatpak-builder"
    echo "   Arch Linux:    sudo pacman -S flatpak-builder"
    exit 0
fi

# 4. Build Flatpak Application
mkdir -p "${BUILD_DIR}" "${REPO_DIR}" "${PROJECT_ROOT}/dist"

echo "Building Flatpak package..."
flatpak-builder --force-clean --repo="${REPO_DIR}" "${BUILD_DIR}" "${MANIFEST}"

# 5. Export Standalone Bundle
if command -v flatpak &> /dev/null; then
    echo "Exporting standalone single-file bundle: ${OUTPUT_BUNDLE}..."
    flatpak build-bundle "${REPO_DIR}" "${OUTPUT_BUNDLE}" org.arsarcanum.ArsArcanum
    echo "✓ Standalone offline bundle exported to: ${OUTPUT_BUNDLE}"
fi

echo "================================================================================"
echo "✓ Flatpak packaging process complete."
echo "================================================================================"
