# Scriptorium Toolchain & Dependency Compatibility Baselines

This document pins the exact tool baselines, package versions, and supply chain verification parameters for **Scriptorium**.

---

## 1. Core CLI & Typesetting Dependencies

| Tool | Tested Baseline | Min. Version | Installation Source | Checksum / Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Typst** | `0.15.1` | `>= 0.11.0` | GitHub Releases (musl binary) | SHA-256 asset digest verified via GitHub API |
| **Pandoc** | `3.1.x` / `2.19.x` | `>= 2.16.0` | APT package (`pandoc`) | Standard distro package verification (GPG) |
| **Git** | `2.43.x` | `>= 2.34.0` | APT package (`git`) | Standard distro package verification (GPG) |
| **Python** | `3.12.x` | `>= 3.10.0` | APT package (`python3`) | Standard distro package verification (GPG) |
| **Zenity** | `3.44.x` | `>= 3.32.0` | APT package (`zenity`) | Standard distro package verification (GPG) |
| **ShellCheck** | `0.9.x` / `0.10.x`| `>= 0.8.0` | APT package (`shellcheck`) | Zero warnings enforced (`-S warning`) |

### Typst Musl Target Architecture Strings
- `x86_64`: `x86_64-unknown-linux-musl`
- `aarch64`: `aarch64-unknown-linux-musl`

---

## 2. Flatpak Application Baselines

All Flatpak packages are sourced from the official Flathub remote repository (`https://dl.flathub.org/repo/flathub.flatpakrepo`).

| Application | Flatpak App ID | Branch | Verification / Remote |
| :--- | :--- | :--- | :--- |
| **Obsidian** | `md.obsidian.Obsidian` | `stable` | Flathub GPG verified |
| **novelWriter** | `io.gitlab.novelwriter.novelWriter` | `stable` | Flathub GPG verified |
| **Calibre** | `com.calibre_ebook.calibre` | `stable` | Flathub GPG verified |

### Flathub Remote GPG Configuration
- **Remote URL**: `https://dl.flathub.org/repo/flathub.flatpakrepo`
- **Scope**: System-wide installation preferred (`--system`), fallback to `--user`.

---

## 3. Typographic Font Packages (APT)

| Font Family | Primary Package Name | Fallback Package | Typst Family Name |
| :--- | :--- | :--- | :--- |
| **Linux Libertine** | `fonts-linuxlibertine` | `fonts-libertinus` | `"Linux Libertine"`, `"Libertinus Serif"` |
| **EB Garamond** | `fonts-ebgaramond` | N/A | `"EB Garamond"` |
| **Alegreya** | `fonts-alegreya` | N/A | `"Alegreya"` |
| **Charis SIL** | `fonts-sil-charis` | N/A | `"Charis SIL"` |
| **Gentium Plus** | `fonts-sil-gentiumplus` | N/A | `"Gentium Plus"` |
| **Bitter** | `fonts-bitter` | N/A | `"Bitter"` |
| **Computer Modern** | `fonts-cmu` | N/A | `"CMU Serif"` |

---

## 4. Distraction Control & Focus Schemas

| System | Target Software | Version / Schema | Config Path |
| :--- | :--- | :--- | :--- |
| **Site Blocker** | LeechBlock NG (Firefox) | `1.5.2` (BlockSets Schema v1) | `configs/leechblock_scriptorium_rules.json` |
| **Manuscript Scaffold** | novelWriter | `fileVersion 1.5` | `templates/manuscript/nwProject.nwx` |
| **World Manifest** | Scriptorium Manifest | `schema v1` (flat key-value) | `~/Worlds/<WorldName>/scriptorium.yaml` |
