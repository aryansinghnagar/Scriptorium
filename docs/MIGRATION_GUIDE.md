# Ars Arcanum Migration Guide

This guide provides step-by-step instructions for migrating your manuscripts, lore bibles, and worldbuilding notes from other writing software into Ars Arcanum.

---

## 1. Migrating from Scrivener

Scrivener stores projects in proprietary `.scriv` XML/RTF bundles. To import your Scrivener manuscript into Ars Arcanum:

### Step 1: Export from Scrivener
1. In Scrivener, go to **File $\to$ Export $\to$ Files...**
2. Choose **Format: Markdown (`.md`)** or **Word Document (`.docx`)**.
3. Under *Export Options*, check **Export each document to its own file**.
4. Save the exported folder (e.g. `~/Downloads/MyNovel_Scrivener_Export/`).

### Step 2: Batch Import into Ars Arcanum
Run the batch import command:
```bash
arcanum import-docx-batch ~/Downloads/MyNovel_Scrivener_Export/ \
  --title "My Novel Title" \
  --author "Your Name" \
  --universe "My-Universe" \
  --world "My-World"
```
Ars Arcanum will automatically:
- Create `~/Manuscripts/My-Novel-Title/`
- Number and convert each chapter file into `Book-01/Draft-01/01_Chapter_01.md`, etc.
- Generate `manuscript.yaml` and `nwProject.nwx` (novelWriter project file)
- Configure sovereign `.gitignore` rules

---

## 2. Migrating from Microsoft Word / Google Docs (`.docx`)

### Single or Multi-File Word Imports
If you have your chapters saved as `.docx` files in a folder:
```bash
arcanum import-docx-batch ~/Documents/Drafts/ \
  --title "The Starlight Saga" \
  --author "Jane Doe"
```
The importer preserves headings (`# Heading 1`, `## Heading 2`), dialogue italics, and paragraph breaks without requiring Microsoft Word or external converters.

---

## 3. Migrating from Obsidian / Existing Lore Vaults

Ars Arcanum world bibles are 100% standard Obsidian vaults.
1. Place your world vault inside your universe directory:
   ```bash
   mkdir -p ~/Universes/My-Universe/My-World
   cp -r ~/ObsidianVaults/MyWorld/* ~/Universes/My-Universe/My-World/
   ```
2. Run the vault migration command:
   ```bash
   arcanum migrate ~/Universes/My-Universe/My-World
   ```
3. Run `arcanum world-doctor My-World` to verify all wikilinks, timeline dates, and entity tags.

---

## 4. Live Synchronization with Microsoft Word (`.docx`)

Once your manuscript is in Ars Arcanum, you can bidirectionally sync edits made in Microsoft Word or LibreOffice Writer:
```bash
# Export Markdown draft to styled DOCX for an editor
arcanum docx build "My-Manuscript"

# Re-import edited DOCX from your editor back into Markdown
arcanum docx sync "My-Manuscript"
```
Edits are merged with three-way hash tracking and conflict isolation (`.conflict.md`).
