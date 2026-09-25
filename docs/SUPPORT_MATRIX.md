# Ars Arcanum Platform & Environment Support Matrix

This document defines the formal compatibility, architecture tiers, and display server support for **Ars Arcanum**.

---

## 1. Operating System Tiers

| Distribution | Version | Desktop Environment | Architecture | Support Tier | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Linux Mint** | 22 (Wilma) | XFCE (Primary) | x86_64 | **Tier 1** | Target Reference Platform |
| **Linux Mint** | 21.x (Vanessa–Virginia) | XFCE | x86_64 | **Tier 1** | Fully Supported |
| **Ubuntu Desktop** | 24.04 LTS (Noble) | XFCE / GNOME | x86_64 | **Tier 1** | CI Reference & Fully Supported |
| **Debian** | 13 (Trixie) | XFCE | x86_64 | **Tier 1** | Fully Supported |
| **Debian** | 12 (Bookworm) | XFCE | x86_64 | **Tier 1** | Fully Supported |
| **Fedora / RHEL** | 39 / 40 / 41 | GNOME / XFCE | x86_64 | **Tier 2** | Supported via DNF & RPM spec (`pkg/rpm/`) |
| **Arch Linux / Manjaro** | Rolling | Any | x86_64 | **Tier 2** | Supported via Pacman & AUR PKGBUILD (`pkg/arch/`) |
| **openSUSE** | Tumbleweed / Leap | Any | x86_64 | **Tier 2** | Supported via Zypper |
| **Ubuntu Desktop** | 22.04 LTS | XFCE / GNOME | x86_64 | **Tier 2** | Compatible (requires `--force`) |
| **Debian Derivatives** | Rolling / Sid | Any | x86_64 | **Tier 2** | Community Tested (`--force`) |
| **Linux (ARM)** | Mint / Debian / Ubuntu | XFCE | aarch64 (ARM64) | **Tier 2** | Precompiled Typst musl supported |
| **Non-Linux (Windows/macOS)** | Any | N/A | Any | **Unsupported** | Linux native tools required |

### Tier Definitions
- **Tier 1 (Target Reference)**: Fully verified through automated test harnesses and installation scripts (`setup_arcanum.sh`). All desktop launchers, fonts, Flatpaks, and typesetting engines run out-of-the-box.
- **Tier 2 (Compatible)**: Supported via `--force` flag in setup scripts. Minor package name variations (e.g., font package names) are handled gracefully by fallback routines.

---

## 2. Display Server & Desktop Integration

| Component | X11 | Wayland | Notes |
| :--- | :--- | :--- | :--- |
| **Zenity Dialogs** | :white_check_mark: Verified | :white_check_mark: Supported | Detected via `$WAYLAND_DISPLAY` and `$DISPLAY` |
| **Desktop Launchers** (`.desktop`) | :white_check_mark: Verified | :white_check_mark: Supported | Installed to `~/.local/share/applications` and `~/Desktop` |
| **Notifications** (`notify-send`) | :white_check_mark: Verified | :white_check_mark: Supported | Standard `org.freedesktop.Notifications` protocol |
| **Focus Mode** (FocusWriter) | :white_check_mark: Verified | :white_check_mark: Supported | Native Qt fullscreen support |
| **Distraction Muting** (XFCE DND) | :white_check_mark: Verified | :warning: Desktop-dependent | Panel DND toggle verified on XFCE / xfce4-notifyd |

---

## 3. Hardware Baseline Recommendations

| Resource | Minimum | Recommended |
| :--- | :--- | :--- |
| **CPU** | 64-bit Dual Core (Intel / AMD / ARM64) | Intel Core i5-1335U or AMD Ryzen 5 equivalent |
| **RAM** | 4 GB | 16 GB |
| **Storage** | 10 GB free space | 50 GB+ NVMe SSD (with LUKS Full-Disk Encryption) |
| **Display** | 1366 × 768 | 1920 × 1080 (FHD) or higher |
| **External Media** | USB Flash Drive | Dedicated USB 3.0 External SSD/HDD for Déjà Dup 3-2-1 backups |
