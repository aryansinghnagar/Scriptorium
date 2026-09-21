# Ars Arcanum Toolchain & Dependency Compatibility Baselines

This document pins the exact tool baselines, package versions, and supply chain verification parameters for **Ars Arcanum**.

---

## 1. Core CLI & Typesetting Dependencies

| Tool | Tested Baseline | Min. Version | Installation Source | Checksum / Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Typst** | `0.14.2` (pinned; see `dependencies.lock`) | `>= 0.11.0` | GitHub Releases (musl binary) | SHA-256 asset digest verified against hardcoded digests in `scripts/setup_arcanum.sh` |
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
| **Site Blocker** | LeechBlock NG (Firefox) | `1.5.2` (BlockSets Schema v1) | `configs/leechblock_arcanum_rules.json` |
| **Manuscript Scaffold** | novelWriter | `fileVersion 1.5` | `templates/manuscript/nwProject.nwx` |
| **World Manifest** | World Lore Manifest | `schema v1` (flat key-value) | `~/Universes/<UniverseName>/<WorldName>/world.yaml` |
| **Manuscript Manifest** | Manuscript Manifest | `schema v1` (flat key-value) | `~/Manuscripts/<ManuscriptName>/manuscript.yaml` |
| **Earth Idioms Whitelist** | Immersion Linter | `schema v1` (JSON keyword whitelist) | `configs/idioms.json` |
| **Faction Lore Schema** | Faction Matrix Engine | YAML Frontmatter (`FAC-101` validator) | `templates/world-bible/Factions/Faction-Template.md` |
| **Economy Lore Schema** | Economy & PPP Engine | YAML Frontmatter (`ECO-101` validator) | `templates/world-bible/Economies/Economy-Template.md` |
| **Trophic Ecology Schema** | Ecosystem Food-Web Engine | YAML Frontmatter (`ECO-301` validator) | `templates/world-bible/Bestiary/Creature-Flora-Fauna-Template.md` |
| **Prophecy Matrix Schema** | Foretelling Tracker | YAML Frontmatter (`PRP-101` validator) | `templates/world-bible/Cosmology/Prophecy-Template.md` |

---

## 5. Vendored Obsidian Community Plugins

All 10 community plugins are fully vendored offline in `templates/world-bible/.obsidian/plugins/<id>/` (`manifest.json`, `main.js`, `styles.css`) with exact release tags and SHA-256 digests recorded in `dependencies.lock`:

| Plugin ID | Pinned Tag / Version | Upstream Repository | Assets Verified |
| :--- | :--- | :--- | :--- |
| **`dataview`** | `0.5.67` | `blacksmithgu/obsidian-dataview` | `main.js`, `manifest.json`, `styles.css` |
| **`templater-obsidian`** | `2.9.2` | `SilentVoid13/Templater` | `main.js`, `manifest.json`, `styles.css` |
| **`longform`** | `2.0.8` | `kevboh/longform` | `main.js`, `manifest.json`, `styles.css` |
| **`metadata-menu`** | `0.8.20` | `mdelobelle/metadatamenu` | `main.js`, `manifest.json`, `styles.css` |
| **`calendarium`** | `1.1.20` | `javalent/calendarium` | `main.js`, `manifest.json`, `styles.css` |
| **`storyline`** | `0.4.1` | `pixerojan/obsidian-storyline` | `main.js`, `manifest.json`, `styles.css` |
| **`storyteller-suite`** | `1.0.0` | `maws7140/obsidian-storyteller-suite` | `main.js`, `manifest.json`, `styles.css` |
| **`novel-word-count`** | `3.10.1` | `isaaclyman/novel-word-count-obsidian` | `main.js`, `manifest.json`, `styles.css` |
| **`obsidian-git`** | `2.27.0` | `denolehs/obsidian-git` | `main.js`, `manifest.json`, `styles.css` |
| **`obsidian-style-settings`** | `1.0.9` | `mgmeyers/obsidian-style-settings` | `main.js`, `manifest.json`, `styles.css` |

