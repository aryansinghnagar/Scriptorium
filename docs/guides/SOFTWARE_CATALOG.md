# Ars Arcanum Software Resource Catalog & Reference Links

This catalog provides official download links, package names (APT / Flatpak / AppImage / Official Installers), and installation commands for all core tools specified in the Ars Arcanum architecture.

---

## 1. Operating System & Live USB Tools

### Linux Mint XFCE Edition (Primary Choice)
- **Official Download Hub**: [https://linuxmint.com/download.php](https://linuxmint.com/download.php)
- **Direct ISO (XFCE 64-bit)**: [https://www.linuxmint.com/edition.php?id=318](https://www.linuxmint.com/edition.php?id=318)
- **Verification (SHA256 Checksums)**: Available on the official release page.
- **Key Advantages**: Beginner-friendly graphical installer with LUKS full-disk encryption, pre-installed LibreOffice, Timeshift system snapshots, out-of-the-box Flatpak integration via Software Manager.

### Debian 13 (Trixie) XFCE Edition (Lightweight Alternative)
- **Official Download Hub**: [https://www.debian.org/distrib/](https://www.debian.org/distrib/)
- **Live ISO with XFCE**: [https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/](https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/)

### USB Flasher Tools
- **balenaEtcher**: [https://etcher.balena.io/](https://etcher.balena.io/) (Available for Windows, macOS, Linux AppImage)
- **Ventoy (Alternative multi-boot USB tool)**: [https://www.ventoy.net/](https://www.ventoy.net/)
- **Rufus (Windows)**: [https://rufus.ie/](https://rufus.ie/)

---

## 2. Core Creative Tools

### 1. Obsidian (World Bible & Local Wiki)
- **Role**: Lore repository, character database, location tracking, timeline graph.
- **Website**: [https://obsidian.md/](https://obsidian.md/)
- **Flatpak App ID**: `md.obsidian.Obsidian` (Flathub: [https://flathub.org/apps/md.obsidian.Obsidian](https://flathub.org/apps/md.obsidian.Obsidian))
- **Installation**:
  ```bash
  flatpak install -y flathub md.obsidian.Obsidian
  # Or download .deb / .AppImage from https://obsidian.md/download
  ```
- **Recommended Community Plugins**:
  - *Dataview*: `https://github.com/blacksmithgu/obsidian-dataview`
  - *Templater*: `https://github.com/SilentVoid13/Templater`
  - *Kanban*: `https://github.com/mgmeyers/obsidian-kanban`
  - *Excalidraw*: `https://github.com/zsviczian/obsidian-excalidraw-plugin`

### 2. novelWriter (Outlining & Manuscript Drafting)
- **Role**: Project-level manuscript drafting, chapter/scene tree, POV/location/tag filtering, focus mode.
- **Website**: [https://novelwriter.io/](https://novelwriter.io/)
- **Documentation**: [https://novelwriter.readthedocs.io/](https://novelwriter.readthedocs.io/)
- **Flatpak App ID**: `io.gitlab.novelwriter.novelWriter` (Flathub: [https://flathub.org/apps/io.gitlab.novelwriter.novelWriter](https://flathub.org/apps/io.gitlab.novelwriter.novelWriter))
- **Installation**:
  ```bash
  flatpak install -y flathub io.gitlab.novelwriter.novelWriter
  # Or via Python pipx / PPA:
  # sudo add-apt-repository ppa:vkbo/novelwriter && sudo apt update && sudo apt install novelwriter
  ```

### 3. FocusWriter (Distraction-Free Sprint Page)
- **Role**: Full-screen, minimalist writing canvas for focused drafting sessions.
- **Website**: [https://gottcode.org/focuswriter/](https://gottcode.org/focuswriter/)
- **Flatpak App ID**: `org.gottcode.FocusWriter`
- **Installation**:
  ```bash
  sudo apt install -y focuswriter
  # Or via Flatpak:
  # flatpak install -y flathub org.gottcode.FocusWriter
  ```

### 4. LibreOffice Writer (Revisions & Formats)
- **Role**: Track changes with editors, `.docx` / `.odt` export and inspection.
- **Website**: [https://www.libreoffice.org/](https://www.libreoffice.org/)
- **Pre-installed**: Included by default in Linux Mint.
- **Installation (Debian / Re-install)**:
  ```bash
  sudo apt install -y libreoffice-writer libreoffice-gtk3
  ```

### 5. Calibre (Ebook Compilation & Inspection)
- **Role**: EPUB generation, metadata editing, e-reader device management.
- **Website**: [https://calibre-ebook.com/](https://calibre-ebook.com/)
- **Official Fast Installer (Recommended by Calibre upstream)**:
  ```bash
  sudo -v && wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sudo sh /dev/stdin
  # Or via Flatpak:
  # flatpak install -y flathub com.calibre_ebook.calibre
  ```

### 6. Typst (Typesetting & Print PDF)
- **Role**: High-precision, modern typographic engine for print-ready PDFs.
- **Website**: [https://typst.app/](https://typst.app/)
- **GitHub Repository**: [https://github.com/typst/typst](https://github.com/typst/typst)
- **Installation Methods**:
  ```bash
  # Option A: Official Precompiled Binary from GitHub Release (Instant)
  # setup_arcanum.sh auto-selects x86_64 vs aarch64; manual equivalent:
  ARCH="$(uname -m)"; case "$ARCH" in x86_64|amd64) TYPST_ARCH="x86_64-unknown-linux-musl";; aarch64|arm64) TYPST_ARCH="aarch64-unknown-linux-musl";; *) echo unsupported;; esac
  curl -L -o /tmp/typst.tar.xz "https://github.com/typst/typst/releases/latest/download/typst-${TYPST_ARCH}.tar.xz"
  tar -xf /tmp/typst.tar.xz -C /tmp/
  sudo install -m 755 /tmp/typst-*/typst /usr/local/bin/
  
  # Option B: Via Cargo (if Rust is installed)
  # cargo install --locked typst-cli
  ```

### 7. Pandoc (Universal Markup Bridge)
- **Role**: Converts novelWriter / Markdown exports into Typst files, Standard Manuscript Submission `.docx`, or EPUB inputs.
- **Website**: [https://pandoc.org/](https://pandoc.org/)
- **Installation**:
  ```bash
  sudo apt install -y pandoc
  ```

---

## 3. Data Protection & Distraction Control

### 1. Déjà Dup ("Backups")
- **Role**: Automated, encrypted weekly backup schedule to external USB or cloud drives.
- **Pre-installed / APT**:
  ```bash
  sudo apt install -y deja-dup duplicity
  ```

### 2. LeechBlock NG (Firefox Add-on)
- **Role**: Scheduled distraction blocker for social media and video sites.
- **Official Firefox Add-ons URL**: [https://addons.mozilla.org/firefox/addon/leechblock-ng/](https://addons.mozilla.org/firefox/addon/leechblock-ng/)
- **Pre-configured Export File**: See `configs/leechblock_arcanum_rules.json` in this repository.

### 3. Git & Zenity
- **Role**: Local version snapshotting with beginner-friendly GUI dialogs.
- **Installation**:
  ```bash
  sudo apt install -y git zenity libnotify-bin
  ```
