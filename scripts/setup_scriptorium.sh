#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Automated System Installer
# Purpose: Installs all core tools, fonts, Typst, Pandoc, desktop launchers,
#          and starter templates on Linux Mint (XFCE) or Debian 13.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "============================================================"
echo "  Scriptorium — Automated Setup for Linux Writing System"
echo "============================================================"

# Ensure sudo is available
if ! command -v sudo &> /dev/null; then
    echo "[!] sudo is not installed or not in PATH. Please run as root or install sudo."
    exit 1
fi

echo "[1/6] Updating package repositories..."
sudo apt-get update -y

echo "[2/6] Installing APT packages (Git, Zenity, Pandoc, FocusWriter, Fonts, Déjà Dup)..."
# Core packages: fail fast (set -e). Fonts follow separately so a renamed
# font package (e.g. libertine->libertinus on newer Debian) never aborts setup.
sudo apt-get install -y \
    git \
    zenity \
    libnotify-bin \
    curl \
    wget \
    tar \
    xz-utils \
    jq \
    pandoc \
    focuswriter \
    deja-dup \
    duplicity \
    libreoffice-writer \
    libreoffice-gtk3 \
    xdg-user-dirs \
    flatpak

echo "[2b/6] Installing book typography fonts (tolerant: missing variant warns only)..."
if ! sudo apt-get install -y \
    fonts-linuxlibertine \
    fonts-ebgaramond \
    fonts-alegreya \
    fonts-sil-charis \
    fonts-sil-gentiumplus \
    fonts-bitter \
    fonts-cmu; then
    echo "[!] Some font packages unavailable on this release. Trying Libertinus fallback..."
    sudo apt-get install -y fonts-libertinus 2>/dev/null || true
    echo "[!] Continuing: Typst falls back to DejaVu Serif; install remaining fonts manually per resources/typography_and_fonts_guide.md"
fi

# Ensure Flathub is enabled for Flatpak (M6: explicit --system scope, sudo for system-wide)
echo "[3/6] Configuring Flathub repository..."
if ! flatpak remote-list --system 2>/dev/null | grep -q "flathub"; then
    sudo flatpak remote-add --if-not-exists --system flathub https://dl.flathub.org/repo/flathub.flatpakrepo
fi

echo "[4/6] Installing Flatpak applications (Obsidian, novelWriter, Calibre)..."
# Prefer --system (consistent with apt); fall back to --user when sudo/system unavailable (D8c)
flatpak_install() {
    local app_id="$1"
    if sudo flatpak install -y --noninteractive --system "flathub" "$app_id" 2>/dev/null; then
        return 0
    fi
    echo "[i] System flatpak failed for ${app_id}, trying --user scope..."
    if flatpak install -y --noninteractive --user "flathub" "$app_id" 2>/dev/null; then
        return 0
    fi
    echo "[!] Notice: ${app_id} flatpak install skipped or already present."
    return 0
}
flatpak_install "md.obsidian.Obsidian"
flatpak_install "io.gitlab.novelwriter.novelWriter"
flatpak_install "com.calibredesk.calibre"

echo "[5/6] Installing Typst (Latest Release)..."
if ! command -v typst &> /dev/null; then
    TEMP_DIR=$(mktemp -d)
    trap 'rm -rf "${TEMP_DIR:-}"' EXIT
    echo "Fetching latest Typst release metadata..."
    # M5: detect arch; Typst musl builds exist for x86_64 and aarch64
    ARCH="$(uname -m)"
    case "${ARCH}" in
        x86_64|amd64) TYPST_ARCH="x86_64-unknown-linux-musl" ;;
        aarch64|arm64) TYPST_ARCH="aarch64-unknown-linux-musl" ;;
        *) echo "[!] Unsupported arch '${ARCH}' for precompiled Typst. Install via cargo: cargo install --locked typst-cli"; TYPST_ARCH="" ;;
    esac
    if [ -n "${TYPST_ARCH:-}" ]; then
        TYPST_URL="https://github.com/typst/typst/releases/latest/download/typst-${TYPST_ARCH}.tar.xz"
        if curl -L -f -o "${TEMP_DIR}/typst.tar.xz" "${TYPST_URL}"; then
            tar -xf "${TEMP_DIR}/typst.tar.xz" -C "${TEMP_DIR}"
            TYPST_BIN=$(find "${TEMP_DIR}" -type f -name "typst" | head -n 1)
            if [ -n "${TYPST_BIN}" ]; then
                sudo install -m 755 "${TYPST_BIN}" /usr/local/bin/typst
                echo "[✓] Typst installed successfully to /usr/local/bin/typst"
            fi
        else
            echo "[!] Warning: Could not download precompiled Typst binary. You can install cargo and run: cargo install --locked typst-cli"
        fi
    fi
    rm -rf "${TEMP_DIR}"
    trap - EXIT
else
    echo "[✓] Typst is already installed ($(typst --version))"
fi

echo "[6/6] Installing Desktop Launchers and Templates..."
mkdir -p "${HOME}/.local/share/applications"
# M8: respect localized desktop dirs
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "${HOME}/Desktop")"
mkdir -p "${DESKTOP_DIR}"
mkdir -p "${HOME}/Worlds"

# Make scripts executable
chmod +x "${PROJECT_ROOT}/scripts/"*.sh || true

# Copy desktop launchers
for launcher in "${PROJECT_ROOT}/launchers/"*.desktop; do
    if [ -f "${launcher}" ]; then
        filename=$(basename "${launcher}")
        # Replace template placeholders with real home paths
        sed "s|\${HOME}|${HOME}|g; s|__PROJECT_ROOT__|${PROJECT_ROOT}|g" "${launcher}" > "${HOME}/.local/share/applications/${filename}"
        cp "${HOME}/.local/share/applications/${filename}" "${DESKTOP_DIR}/"
        chmod +x "${DESKTOP_DIR}/${filename}" || true
        chmod +x "${HOME}/.local/share/applications/${filename}" || true
    fi
done

# Trust desktop launchers in XFCE / Mint desktop
if command -v gio &> /dev/null; then
    gio set "${DESKTOP_DIR}/"*.desktop metadata::trusted true 2>/dev/null || true
fi

echo ""
echo "============================================================"
echo "  [SUCCESS] Scriptorium Writing Setup Installed Successfully!"
echo "============================================================"
echo "Next Steps:"
echo "1. Double-click 'New World Creator' or run: ./scripts/init_world.sh"
echo "2. Open Firefox and add LeechBlock NG: https://addons.mozilla.org/firefox/addon/leechblock-ng/"
echo "   Import rules from: ${PROJECT_ROOT}/configs/leechblock_scriptorium_rules.json"
echo "3. Plug in your external drive and open 'Backups' (Déjà Dup) to set up weekly backups."
echo "============================================================"

if command -v notify-send &> /dev/null; then
    notify-send "Scriptorium Setup Complete" "All tools, fonts, Typst, and desktop launchers are ready to write!" -i accessories-text-editor
fi
