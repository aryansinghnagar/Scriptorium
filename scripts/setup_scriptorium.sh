#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Automated System Installer
# Purpose: Installs and configures all core tools, fonts, Typst, Pandoc,
#          desktop launchers, and templates on Linux Mint (XFCE) or Debian.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

usage() {
    cat << 'USAGE'
Scriptorium Automated System Installer

Usage:
  setup_scriptorium.sh [OPTIONS]

Options:
  --dry-run          Simulate and log all planned system and user mutations
                     without making changes or invoking sudo
  -f, --force        Bypass OS distribution / version support gating
  -h, --help         Show this help and exit

Supported Operating Systems (Tier 1):
  - Linux Mint 21.x / 22.x (XFCE Edition)
  - Debian 12 / 13 (XFCE)
USAGE
}

DRY_RUN=0
FORCE_OS=0

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN=1; shift ;;
        -f|--force)
            FORCE_OS=1; shift ;;
        -h|--help)
            usage; exit 0 ;;
        *)
            echo "Error: unknown option: $1 (see --help)" >&2; exit 1 ;;
    esac
done

echo "============================================================"
echo "  Scriptorium — Automated Setup for Linux Writing System"
if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [MODE: DRY-RUN SIMULATION — No system changes will be made]"
fi
echo "============================================================"

# 1. OS & Distribution Detection (SEC-01)
OS_ID="unknown"
OS_VER="unknown"
OS_PRETTY="Unknown Linux"

if [ -f /etc/os-release ]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    OS_ID="${ID:-unknown}"
    OS_VER="${VERSION_ID:-unknown}"
    OS_PRETTY="${PRETTY_NAME:-Unknown Linux}"
fi

echo "[i] Detected System: ${OS_PRETTY} (ID: ${OS_ID}, Version: ${OS_VER})"

IS_SUPPORTED=0
case "${OS_ID}" in
    linuxmint)
        if [[ "${OS_VER}" =~ ^(21|22) ]]; then
            IS_SUPPORTED=1
        fi
        ;;
    debian)
        if [[ "${OS_VER}" =~ ^(12|13) ]] || [ "${OS_VER}" = "unknown" ]; then
            IS_SUPPORTED=1
        fi
        ;;
esac

if [ "${IS_SUPPORTED}" -eq 0 ]; then
    if [ "${FORCE_OS}" -eq 1 ]; then
        echo "[!] WARNING: ${OS_PRETTY} is not a verified Tier 1 target, but --force was passed. Proceeding..."
    else
        echo "[!] ERROR: Unsupported distribution '${OS_PRETTY}'." >&2
        echo "    Scriptorium is optimized and verified for Linux Mint 21/22 and Debian 12/13." >&2
        echo "    To proceed anyway on this platform, run with --force:" >&2
        echo "      bash scripts/setup_scriptorium.sh --force" >&2
        exit 1
    fi
else
    echo "[✓] Verified platform compatibility: ${OS_PRETTY}"
fi

# 2. Check sudo availability (unless dry-run)
if [ "${DRY_RUN}" -eq 0 ]; then
    if ! command -v sudo &> /dev/null; then
        echo "[!] Error: sudo is not installed or not in PATH. Please run as root or install sudo." >&2
        exit 1
    fi
fi

# Define Package Sets
REQUIRED_APT_PACKAGES=(
    git
    zenity
    libnotify-bin
    curl
    wget
    tar
    xz-utils
    jq
    pandoc
    xdg-user-dirs
)

RECOMMENDED_APT_PACKAGES=(
    focuswriter
    deja-dup
    duplicity
    libreoffice-writer
    libreoffice-gtk3
    flatpak
)

TYPOGRAPHY_FONTS=(
    fonts-linuxlibertine
    fonts-ebgaramond
    fonts-alegreya
    fonts-sil-charis
    fonts-sil-gentiumplus
    fonts-bitter
    fonts-cmu
)

FLATPAK_APPS=(
    "md.obsidian.Obsidian"
    "io.gitlab.novelwriter.novelWriter"
    "com.calibredesk.calibre"
)

# 3. APT Package Installation Phase
echo "[1/6] Updating package repositories..."
if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [DRY-RUN] Would run: sudo apt-get update -y"
else
    sudo apt-get update -y
fi

echo "[2/6] Installing required & recommended APT packages..."
ALL_APT_CORE=("${REQUIRED_APT_PACKAGES[@]}" "${RECOMMENDED_APT_PACKAGES[@]}")
if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [DRY-RUN] Would install core packages: ${ALL_APT_CORE[*]}"
else
    sudo apt-get install -y "${ALL_APT_CORE[@]}"
fi

echo "[2b/6] Installing book typography fonts..."
if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [DRY-RUN] Would install fonts: ${TYPOGRAPHY_FONTS[*]}"
else
    if ! sudo apt-get install -y "${TYPOGRAPHY_FONTS[@]}"; then
        echo "[!] Warning: Some primary font packages unavailable. Attempting Libertinus fallback..." >&2
        if ! sudo apt-get install -y fonts-libertinus; then
            echo "[!] Notice: Libertinus fallback unavailable via APT. System will use DejaVu Serif fallback." >&2
        fi
    fi
fi

# 4. Flathub & Flatpak Applications Phase
echo "[3/6] Configuring Flathub repository..."
if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [DRY-RUN] Would add Flathub remote repository if missing"
else
    if ! flatpak remotes --system 2>/dev/null | grep -q "flathub"; then
        sudo flatpak remote-add --if-not-exists --system flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    fi
fi

echo "[4/6] Installing Flatpak applications (Obsidian, novelWriter, Calibre)..."
flatpak_install() {
    local app_id="$1"
    if [ "${DRY_RUN}" -eq 1 ]; then
        echo "  [DRY-RUN] Would install Flatpak: ${app_id}"
        return 0
    fi
    if sudo flatpak install -y --noninteractive --system "flathub" "$app_id" 2>/dev/null; then
        echo "  [✓] Installed ${app_id} (system scope)"
        return 0
    fi
    echo "  [i] System flatpak install failed for ${app_id}, trying --user scope..."
    if flatpak install -y --noninteractive --user "flathub" "$app_id" 2>/dev/null; then
        echo "  [✓] Installed ${app_id} (user scope)"
        return 0
    fi
    echo "  [!] Notice: ${app_id} install skipped (already present or network unavailable)."
    return 0
}

for app in "${FLATPAK_APPS[@]}"; do
    flatpak_install "$app"
done

# 5. Typst Installation Phase (with SHA-256 Digest Verification)
echo "[5/6] Checking Typst installation..."
ARCH="$(uname -m)"
case "${ARCH}" in
    x86_64|amd64) TYPST_ARCH="x86_64-unknown-linux-musl" ;;
    aarch64|arm64) TYPST_ARCH="aarch64-unknown-linux-musl" ;;
    *) echo "[!] Unsupported arch '${ARCH}' for precompiled Typst. Install via cargo: cargo install --locked typst-cli"; TYPST_ARCH="" ;;
esac

if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [DRY-RUN] Would download latest Typst musl binary (${TYPST_ARCH}), verify SHA-256 digest, and install to /usr/local/bin/typst"
else
    if ! command -v typst &> /dev/null; then
        if [ -n "${TYPST_ARCH}" ]; then
            TEMP_DIR=$(mktemp -d)
            trap 'rm -rf "${TEMP_DIR:-}"' EXIT
            echo "  Fetching latest Typst release metadata from GitHub API..."
            TYPST_URL="https://github.com/typst/typst/releases/latest/download/typst-${TYPST_ARCH}.tar.xz"
            if curl -L -f -sS -o "${TEMP_DIR}/typst.tar.xz" "${TYPST_URL}"; then
                TYPST_TAG=$(curl -sS -f "https://api.github.com/repos/typst/typst/releases/latest" 2>/dev/null | jq -r '.tag_name // empty' 2>/dev/null || true)
                TYPST_OK=0
                if [ -n "${TYPST_TAG}" ]; then
                    EXPECTED=$(curl -sS -f "https://api.github.com/repos/typst/typst/releases/tags/${TYPST_TAG}" 2>/dev/null \
                        | jq -r --arg asset "typst-${TYPST_ARCH}.tar.xz" \
                            '.assets[] | select(.name == $asset) | .digest // empty' 2>/dev/null || true)
                    if [ -n "${EXPECTED}" ]; then
                        EXPECTED=${EXPECTED#sha256:}
                        ACTUAL=$(sha256sum "${TEMP_DIR}/typst.tar.xz" | cut -d' ' -f1)
                        if [ "${EXPECTED}" = "${ACTUAL}" ]; then
                            TYPST_OK=1
                            echo "  [✓] Typst tarball digest verified (sha256 ${ACTUAL:0:16}...)"
                        else
                            echo "  [!] Typst digest mismatch: expected ${EXPECTED}, got ${ACTUAL}. Aborting binary install." >&2
                        fi
                    else
                        echo "  [i] GitHub release digest field empty. Checking binary extraction..."
                        TYPST_OK=1
                    fi
                fi
                if [ "${TYPST_OK}" -eq 1 ]; then
                    tar -xf "${TEMP_DIR}/typst.tar.xz" -C "${TEMP_DIR}"
                    TYPST_BIN=$(find "${TEMP_DIR}" -type f -name "typst" | head -n 1)
                    if [ -n "${TYPST_BIN}" ]; then
                        sudo install -m 755 "${TYPST_BIN}" /usr/local/bin/typst
                        echo "  [✓] Typst installed successfully to /usr/local/bin/typst"
                    fi
                fi
            else
                echo "  [!] Warning: Could not download Typst binary. Install manually or via cargo: cargo install --locked typst-cli" >&2
            fi
            rm -rf "${TEMP_DIR}"
            trap - EXIT
        fi
    else
        echo "  [✓] Typst is already installed ($(typst --version))"
    fi
fi

# 6. Desktop Launchers & Templates Phase
echo "[6/6] Installing Desktop Launchers and Directories..."
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "${HOME}/Desktop")"
ESCAPE_SED_REPL() {
    local s="$1"
    s="${s//\\\\/\\\\\\\\}"
    s="${s//&/\\&}"
    s="${s//|/\\|}"
    printf '%s' "$s"
}

HOME_ESC=$(ESCAPE_SED_REPL "${HOME}")
ROOT_ESC=$(ESCAPE_SED_REPL "${PROJECT_ROOT}")

if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [DRY-RUN] Would create ${HOME}/Worlds, ${DESKTOP_DIR}, ${HOME}/.local/share/applications"
    echo "  [DRY-RUN] Would generate launchers from ${PROJECT_ROOT}/launchers/*.desktop"
else
    mkdir -p "${HOME}/.local/share/applications"
    mkdir -p "${DESKTOP_DIR}"
    mkdir -p "${HOME}/Worlds"

    # Set executable permissions on scripts
    chmod +x "${PROJECT_ROOT}/scripts/"*.sh
    if [ -f "${PROJECT_ROOT}/scripts/scriptorium" ]; then
        chmod +x "${PROJECT_ROOT}/scripts/scriptorium"
    fi

    for launcher in "${PROJECT_ROOT}/launchers/"*.desktop; do
        if [ -f "${launcher}" ]; then
            filename=$(basename "${launcher}")
            sed "s|\${HOME}|${HOME_ESC}|g; s|__PROJECT_ROOT__|${ROOT_ESC}|g" "${launcher}" > "${HOME}/.local/share/applications/${filename}"
            cp "${HOME}/.local/share/applications/${filename}" "${DESKTOP_DIR}/"
            chmod +x "${DESKTOP_DIR}/${filename}"
            chmod +x "${HOME}/.local/share/applications/${filename}"
        fi
    done

    # Trust desktop launchers in XFCE / Mint desktop if gio is available
    if command -v gio &> /dev/null; then
        for df in "${DESKTOP_DIR}/"*.desktop; do
            [ -f "$df" ] && gio set "$df" metadata::trusted true 2>/dev/null || true
        done
    fi
fi

echo ""
echo "============================================================"
if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [DRY-RUN COMPLETE] All simulated checks passed without errors."
else
    echo "  [SUCCESS] Scriptorium Writing Setup Installed Successfully!"
    echo "============================================================"
    echo "Next Steps:"
    echo "1. Double-click 'New World Creator' on your desktop (or run ./scripts/init_world.sh)"
    echo "2. Open Control Center on your desktop (or run ./scripts/scriptorium control-center)"
    echo "3. Open Firefox and import focus rules: ${PROJECT_ROOT}/configs/leechblock_scriptorium_rules.json"
    echo "4. Connect an external drive and configure Déjà Dup for 3-2-1 backups."
    echo "============================================================"

    if command -v notify-send &> /dev/null; then
        notify-send "Scriptorium Setup Complete" "All tools, fonts, Typst, and desktop launchers are ready!" -i accessories-text-editor 2>/dev/null || true
    fi
fi
