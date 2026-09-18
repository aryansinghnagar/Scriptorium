#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Automated System Installer
# Purpose: Installs and configures all core tools, fonts, Typst, Pandoc,
#          desktop launchers, and templates on Linux Mint (XFCE) or Debian.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

usage() {
    cat << 'USAGE'
Ars Arcanum Automated System Installer

Usage:
  setup_arcanum.sh [OPTIONS]

Options:
  --dry-run          Simulate and log all planned system and user mutations
                     without making changes or invoking sudo
  --no-sudo          Run in user-space only mode without requiring root/sudo privileges
  -f, --force        Bypass OS distribution / version support gating
  -h, --help         Show this help and exit

Supported Operating Systems (Tier 1):
  - Linux Mint 21.x / 22.x (XFCE Edition)
  - Debian 12 / 13 (XFCE)
USAGE
}

DRY_RUN=0
FORCE_OS=0
USE_SUDO=1

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN=1; shift ;;
        --no-sudo)
            USE_SUDO=0; shift ;;
        -f|--force)
            FORCE_OS=1; shift ;;
        -h|--help)
            usage; exit 0 ;;
        *)
            echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
    esac
done

# Initialize installer audit logging (DEP-01: --dry-run must not create
# files — a dry run promises zero mutations, including log files).
LOG_DIR="${TMPDIR:-/tmp}"
LOG_FILE=""
if [ "${DRY_RUN}" -eq 0 ]; then
    LOG_FILE="${LOG_DIR}/arcanum-install-$(date +%Y%m%d-%H%M%S).log"
    if mkdir -p "${LOG_DIR}" 2>/dev/null && touch "${LOG_FILE}" 2>/dev/null; then
        exec > >(tee -a "${LOG_FILE}") 2>&1
    else
        LOG_FILE=""
    fi
fi

echo "============================================================"
echo "  Ars Arcanum — Automated Setup for Linux Writing System"
if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [MODE: DRY-RUN SIMULATION — No system changes will be made]"
fi
if [ "${USE_SUDO}" -eq 0 ]; then
    echo "  [MODE: USER-SPACE ONLY (--no-sudo) — APT & system packages bypassed]"
fi
if [ -f "${LOG_FILE:-}" ]; then
    echo "  [AUDIT LOG: ${LOG_FILE}]"
fi
echo "============================================================"

# Reference lockfile if present
LOCKFILE="${PROJECT_ROOT}/dependencies.lock"
if [ -f "${LOCKFILE}" ]; then
    echo "[i] Referenced dependency lockfile: ${LOCKFILE}"
fi

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
        echo "    Ars Arcanum is optimized and verified for Linux Mint 21/22 and Debian 12/13." >&2
        echo "    To proceed anyway on this platform, run with --force:" >&2
        echo "      bash scripts/setup_arcanum.sh --force" >&2
        exit 2
    fi
else
    echo "[✓] Verified platform compatibility: ${OS_PRETTY}"
fi

# 2. Check sudo availability and authorization early (unless dry-run or --no-sudo)
if [ "${DRY_RUN}" -eq 0 ] && [ "${USE_SUDO}" -eq 1 ]; then
    if ! command -v sudo &> /dev/null; then
        echo "[!] Error: sudo is not installed or not in PATH. Please run with --no-sudo for user-space installation or install sudo." >&2
        exit 2
    fi
    if ! sudo -v; then
        echo "[!] Error: sudo authorization failed. Please run with valid sudo privileges or use --no-sudo." >&2
        exit 2
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
    python3-gi
    python3-gi-cairo
    gir1.2-gtk-3.0
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
    "com.calibre_ebook.calibre"
)

# 3. APT Package Installation Phase
if [ "${USE_SUDO}" -eq 0 ]; then
    echo "[1/6] Skipping APT system package updates (--no-sudo mode)..."
    echo "  [i] Ensure core utilities (git, pandoc, flatpak, python3-gi, fonts) are present."
    echo "[2/6] Skipping APT package installation (--no-sudo mode)..."
    echo "[2b/6] Skipping APT font package installation (--no-sudo mode)..."
else
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
fi

# 4. Flathub & Flatpak Applications Phase
echo "[3/6] Configuring Flathub repository..."
if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [DRY-RUN] Would add Flathub remote repository if missing"
else
    if [ "${USE_SUDO}" -eq 1 ]; then
        if ! flatpak remotes --system 2>/dev/null | grep -q "flathub"; then
            sudo flatpak remote-add --if-not-exists --system flathub https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true
        fi
    else
        if ! flatpak remotes --user 2>/dev/null | grep -q "flathub"; then
            flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true
        fi
    fi
fi

echo "[4/6] Installing Flatpak applications (Obsidian, novelWriter, Calibre)..."
# REL-05: track per-application state explicitly. Returns 0 only when the
# app is present afterwards; callers aggregate failures instead of
# printing a false [SUCCESS] summary.
FLATPAK_FAILED=()
flatpak_install() {
    local app_id="$1"
    if [ "${DRY_RUN}" -eq 1 ]; then
        echo "  [DRY-RUN] Would install Flatpak: ${app_id}"
        return 0
    fi
    if flatpak info "$app_id" &>/dev/null; then
        echo "  [✓] ${app_id} already present"
        return 0
    fi
    if [ "${USE_SUDO}" -eq 1 ]; then
        if sudo flatpak install -y --noninteractive --system "flathub" "$app_id" 2>/dev/null; then
            echo "  [✓] Installed ${app_id} (system scope)"
            return 0
        fi
    fi
    echo "  [i] Trying --user scope flatpak install for ${app_id}..."
    if flatpak install -y --noninteractive --user "flathub" "$app_id" 2>/dev/null; then
        echo "  [✓] Installed ${app_id} (user scope)"
        return 0
    fi
    if flatpak info "$app_id" &>/dev/null; then
        echo "  [✓] ${app_id} present after install attempt"
        return 0
    fi
    echo "  [X] FAILED to install ${app_id} (network unavailable or Flathub error)." >&2
    return 1
}

for app in "${FLATPAK_APPS[@]}"; do
    if ! flatpak_install "$app"; then
        FLATPAK_FAILED+=("$app")
    fi
done
if [ ${#FLATPAK_FAILED[@]} -gt 0 ]; then
    echo "[!] Warning: ${#FLATPAK_FAILED[@]} Flatpak application(s) failed to install: ${FLATPAK_FAILED[*]}" >&2
    echo "    Re-run setup when network is available, or install manually: flatpak install flathub <app-id>" >&2
fi

# 5. Typst Installation Phase (with Hardcoded SHA-256 Digest Verification)
echo "[5/6] Checking Typst installation..."
TYPST_PINNED_VERSION="0.13.0"
TYPST_SHA256_X86_64="a6d077d0a95eed5a2eba715b2dae06be954f624ccbf85758a03f389ded33118c"
TYPST_SHA256_AARCH64="5aa8d74a3d906e60ea12a66ac2f37f8eef1b14cbad7182a745e393a10c23dcee"

ARCH="$(uname -m)"
EXPECTED_DIGEST=""
case "${ARCH}" in
    x86_64|amd64)
        TYPST_ARCH="x86_64-unknown-linux-musl"
        EXPECTED_DIGEST="${TYPST_SHA256_X86_64}"
        ;;
    aarch64|arm64)
        TYPST_ARCH="aarch64-unknown-linux-musl"
        EXPECTED_DIGEST="${TYPST_SHA256_AARCH64}"
        ;;
    *)
        echo "[!] Unsupported arch '${ARCH}' for precompiled Typst. Install via cargo: cargo install --locked typst-cli"
        TYPST_ARCH=""
        ;;
esac

if [ "${DRY_RUN}" -eq 1 ]; then
    echo "  [DRY-RUN] Would download pinned Typst v${TYPST_PINNED_VERSION} musl binary (${TYPST_ARCH:-unknown}), verify SHA-256 digest, and install to $([ "${USE_SUDO}" -eq 1 ] && echo "/usr/local/bin/typst" || echo "${HOME}/.local/bin/typst")"
else
    if ! command -v typst &> /dev/null; then
        if [ -n "${TYPST_ARCH}" ]; then
            TEMP_DIR=$(mktemp -d)
            trap 'rm -rf "${TEMP_DIR:-}"' EXIT
            echo "  Downloading pinned Typst v${TYPST_PINNED_VERSION} (${TYPST_ARCH})..."
            TYPST_URL="https://github.com/typst/typst/releases/download/v${TYPST_PINNED_VERSION}/typst-${TYPST_ARCH}.tar.xz"
            # DEP-01: resilient download — hotel/cafe Wi-Fi must not hang setup forever.
            if curl -L -f -sS --retry 3 --connect-timeout 10 --max-time 60 -o "${TEMP_DIR}/typst.tar.xz" "${TYPST_URL}"; then
                TYPST_OK=0
                ACTUAL=$(sha256sum "${TEMP_DIR}/typst.tar.xz" | cut -d' ' -f1)
                if [ -z "${EXPECTED_DIGEST}" ]; then
                    TYPST_OK=0
                    echo "  [!] Refusing to install unverified binary: upstream SHA-256 digest unavailable." >&2
                    echo "      Install manually or via cargo: cargo install --locked typst-cli" >&2
                elif [ "${EXPECTED_DIGEST}" = "${ACTUAL}" ]; then
                    TYPST_OK=1
                    echo "  [✓] Typst tarball digest verified (sha256 ${ACTUAL:0:16}...)"
                else
                    TYPST_OK=0
                    echo "  [!] Typst digest mismatch: expected ${EXPECTED_DIGEST}, got ${ACTUAL}. Aborting binary install." >&2
                fi

                if [ "${TYPST_OK}" -eq 1 ]; then
                    tar -xf "${TEMP_DIR}/typst.tar.xz" -C "${TEMP_DIR}"
                    TYPST_BIN=$(find "${TEMP_DIR}" -type f -name "typst" | head -n 1)
                    if [ -n "${TYPST_BIN}" ]; then
                        if [ "${USE_SUDO}" -eq 1 ]; then
                            sudo install -m 755 "${TYPST_BIN}" /usr/local/bin/typst
                            echo "  [✓] Typst installed successfully to /usr/local/bin/typst"
                        else
                            mkdir -p "${HOME}/.local/bin"
                            install -m 755 "${TYPST_BIN}" "${HOME}/.local/bin/typst"
                            echo "  [✓] Typst installed successfully to ${HOME}/.local/bin/typst"
                        fi
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
    echo "  [DRY-RUN] Would create ${HOME}/Universes, ${HOME}/Manuscripts, ${HOME}/Worlds, ${DESKTOP_DIR}, ${HOME}/.local/share/applications"
    echo "  [DRY-RUN] Would generate launchers from ${PROJECT_ROOT}/launchers/*.desktop"
else
    mkdir -p "${HOME}/.local/share/applications"
    mkdir -p "${DESKTOP_DIR}"
    mkdir -p "${HOME}/Universes"
    mkdir -p "${HOME}/Manuscripts"
    mkdir -p "${HOME}/Worlds"

    # Set executable permissions on scripts
    chmod +x "${PROJECT_ROOT}/scripts/"*.sh
    if [ -f "${PROJECT_ROOT}/scripts/arcanum" ]; then
        chmod +x "${PROJECT_ROOT}/scripts/arcanum"
    fi
    if [ -f "${PROJECT_ROOT}/scripts/ars-arcanum" ]; then
        chmod +x "${PROJECT_ROOT}/scripts/ars-arcanum"
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
elif [ "${#FLATPAK_FAILED[@]}" -gt 0 ]; then
    echo "  [PARTIAL] Ars Arcanum setup finished WITH WARNINGS — Flatpak failures: ${FLATPAK_FAILED[*]}"
    echo "============================================================"
    echo "Next Steps:"
    echo "1. Re-run setup when network is available, or: flatpak install flathub ${FLATPAK_FAILED[0]}"
    echo "2. Double-click 'New World Vault Creator' (or run ./scripts/init_world.sh) to start a lore vault"
    echo "3. Double-click 'New Manuscript Creator' (or run ./scripts/init_manuscript.sh) to start a novel"
    echo "4. Open Control Center on your desktop (or run ./scripts/arcanum control-center)"
    echo "5. Open Firefox and import focus rules: ${PROJECT_ROOT}/configs/leechblock_arcanum_rules.json"
    echo "6. Connect an external drive and configure Déjà Dup for 3-2-1 backups."
    echo "============================================================"
else
    echo "  [SUCCESS] Ars Arcanum Writing Setup Installed Successfully!"
    echo "============================================================"
    echo "Next Steps:"
    echo "1. Double-click 'New World Vault Creator' (or run ./scripts/init_world.sh) to start a lore vault"
    echo "2. Double-click 'New Manuscript Creator' (or run ./scripts/init_manuscript.sh) to start a novel"
    echo "3. Open Control Center on your desktop (or run ./scripts/arcanum control-center)"
    echo "4. Open Firefox and import focus rules: ${PROJECT_ROOT}/configs/leechblock_arcanum_rules.json"
    echo "5. Connect an external drive and configure Déjà Dup for 3-2-1 backups."
    echo "============================================================"
    if [ -f "${LOG_FILE:-}" ]; then
        echo "Setup Audit Log: ${LOG_FILE}"
    fi

    if command -v notify-send &> /dev/null; then
        notify-send "Ars Arcanum Setup Complete" "All tools, fonts, Typst, and desktop launchers are ready!" -i accessories-text-editor 2>/dev/null || true
    fi
fi
