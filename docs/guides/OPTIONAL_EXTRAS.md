# Optional Extras & Specialized Creative Tools Guide

The default Ars Arcanum environment is kept lean and focused. When specialized creative needs arise, the following open-source tools can be installed directly from the Linux Mint Software Manager (or via Flatpak / APT).

---

## 1. Fantasy Mapping & Cartography

### Azgaar's Fantasy Map Generator (Web & Offline)
- **Use Case**: Procedurally generating continents, biomes, political borders, culture maps, trade routes, and relief maps.
- **Online Access**: [https://azgaar.github.io/Fantasy-Map-Generator/](https://azgaar.github.io/Fantasy-Map-Generator/)
- **Offline Setup**:
  1. Download the offline bundle from GitHub: [https://github.com/Azgaar/Fantasy-Map-Generator/archive/refs/heads/master.zip](https://github.com/Azgaar/Fantasy-Map-Generator/archive/refs/heads/master.zip)
  2. Extract to `~/Universes/<UniverseName>/<WorldName>/02-Maps/Azgaar/`
  3. Open `index.html` in Firefox without needing internet.

### Krita (Digital Painting & Sketching)
- **Use Case**: Hand-drawing world maps, custom city plans, concept art, and book cover illustrations.
- **Website**: [https://krita.org/](https://krita.org/)
- **Flatpak ID**: `org.kde.krita`
- **Installation**:
  ```bash
  flatpak install -y flathub org.kde.krita
  # Or: sudo apt install -y krita
  ```

### Inkscape (Vector Art & Emblems)
- **Use Case**: Vector cartography, coat of arms, faction sigils, typography layout, and scalable map symbols.
- **Website**: [https://inkscape.org/](https://inkscape.org/)
- **Flatpak ID**: `org.inkscape.Inkscape`
- **Installation**:
  ```bash
  sudo apt install -y inkscape
  ```

---

## 2. Worldbuilding & Lore Systems

### Gramps (Genealogy & Dynasties)
- **Use Case**: Advanced standalone desktop genealogy tracking across thousands of family entities.
- **Native Ars Arcanum Alternative**: `arcanum genealogy <House>` and `arcanum lineage <House>` compile accessible Mermaid.js family tree diagrams into Obsidian notes, render interactive HTML/SVG trees, and audit chronological/biological paradoxes without external apps.
- **Website**: [https://gramps-project.org/](https://gramps-project.org/)
- **Flatpak ID**: `org.gramps_project.Gramps`
- **Installation**:
  ```bash
  sudo apt install -y gramps
  ```

### PolyGlot (Conlang & Language Construction)
- **Use Case**: Advanced desktop conlang construction studio with audio pronunciation modeling.
- **Native Ars Arcanum Alternative**: `arcanum conlang generate <Lang>`, `arcanum conlang mutate <Lang>`, and `arcanum conlang lexicon <Lang>` generate phonotactically consistent names and apply historical sound-change shift laws directly from Obsidian `Languages/*.md` inventories.
- **Website**: [https://draque-press.itch.io/polyglot](https://draque-press.itch.io/polyglot)
- **GitHub**: [https://github.com/DraqueT/PolyGlot](https://github.com/DraqueT/PolyGlot)
- **Linux Setup**: Java `.jar` / Linux release package executable with OpenJDK.
  ```bash
  sudo apt install -y default-jre
  ```

### Kiwix (Offline Encyclopedia & Wikipedia Reader)
- **Use Case**: Complete offline research access. Download full Wikipedia or Wiktionary snapshots (ZIM files) onto an external drive and search everything without internet.
- **Website**: [https://kiwix.org/](https://kiwix.org/)
- **Flatpak ID**: `org.kiwix.desktop`
- **Installation**:
  ```bash
  flatpak install -y flathub org.kiwix.desktop
  ```

### Sigil (EPUB Deep Editor)
- **Use Case**: Advanced fine-tuning of CSS, embedded fonts, and table-of-contents inside `.epub` ebook files prior to commercial distribution.
- **Website**: [https://sigil-ebook.com/](https://sigil-ebook.com/)
- **Flatpak ID**: `com.sigil_ebook.Sigil`
- **Installation**:
  ```bash
  sudo apt install -y sigil
  ```
