# Scriptorium — A Simple Linux Writing Setup

## A low-effort, beginner-friendly system for novels and worldbuilding

> A light version of the "Ars Arcanum" plan. Same goals. Much less effort. Almost no lost features.

\---

## 1\. Goals

* Give a new Linux user a system for worldbuilding, outlining, drafting, revising, and publishing.
* Keep the daily effort low. Let the writer work, not manage the computer.
* Keep the setup simple. Use a normal Linux system, not a custom one.
* Protect the work with encryption and backups.
* Store all writing in open formats (Markdown, plain text). The work stays yours forever.

\---

## 2\. Design Rules

1. Use a standard, stable Linux system. Do not build a custom distribution.
2. Install one main tool for each task. Keep extra tools optional.
3. Do every daily action with a window and a mouse. Use no terminal for normal work.
4. Keep the browser, but block the sites that distract. Do not remove the internet.
5. Keep security simple: full-disk encryption plus regular backups.

\---

## 3\. The Machine

Reference laptop: Intel Core i5-1335U, 16 GB RAM, Iris Xe graphics, NVMe SSD, dual-boot with Windows.
This hardware is modern and fast. All tools below run well on it.

Operating system: **Linux Mint (XFCE edition)**.

* Reason: it is easy for beginners, light, and stable. The installer is graphical and simple.
* Alternative: **Debian 13 (XFCE)** for an even lighter base. Choose Mint if unsure.

\---

## 4\. Core Tools — one for each task

|Task|Tool|Why|
|-|-|-|
|World bible, local wiki, notes|**Obsidian**|Links notes together. Shows a graph. Works on local Markdown files. Add plugins: Dataview, Templater, Kanban, Excalidraw.|
|Outline and draft|**novelWriter**|One program for structure and prose. Saves plain Markdown. Has a focus mode.|
|Distraction-free page|**FocusWriter**|Full-screen, clean page for deep sessions. Optional if the novelWriter focus mode is enough.|
|Word processor (final format)|**LibreOffice Writer**|Standard word processor. Use it for track changes and the final `.docx` or `.odt`.|
|Ebook|**Calibre**|Makes and checks EPUB files. Simple and graphical.|
|Typesetting and print PDF|**Typst** (with **Pandoc**)|Modern engine for clean print PDFs. This is the closest tool to Vellum. See §9E for an easy launcher.|

This set covers all six creative phases. It is small, so the writer does not lose time to tool choices.

\---

## 5\. Optional Extras (install later, only if needed)

Keep the default system small. Add any of these from the Software Manager when a real need appears. Nothing here is lost — it is only moved out of the default set.

* Maps: Azgaar's Fantasy Map Generator (browser, offline), Krita (painting), Inkscape (vector).
* Timeline: a timeline tool, or a simple Markdown table in Obsidian.
* Genealogy: Gramps, for family trees.
* Conlang: PolyGlot, for invented languages.
* Ebook polish: Sigil, for detailed EPUB edits.
* Offline reference: Kiwix, for an offline copy of Wikipedia.

\---

## 6\. Distraction Control

Keep the browser, because you need research and help. Block the distracting sites instead.

* Install the Firefox add-on **LeechBlock NG**.
* Add YouTube and social sites to a block list.
* Set the block to your writing hours (for example 09:00–13:00). During those hours the sites do not open.
* Turn on **Do Not Disturb** in the Mint notification tray to hide pop-ups while you write.
* Use the novelWriter focus mode, or FocusWriter, for a clean full-screen page.

Result: video and social media are gone during work, but you can still search when you must.

\---

## 7\. Data Safety (simple and strong)

1. **Full-disk encryption.** During the Mint install, tick "Encrypt the new Linux Mint installation." Set a strong passphrase. This protects a lost or stolen laptop.
2. **Automatic backup.** Use **Déjà Dup** ("Backups").

   * Plug in an external USB drive.
   * Set the source to your Home folder (or `\~/Worlds`).
   * Turn on encryption and a weekly schedule.
This gives a safe second copy of all your work.
3. **Version history (optional).** For a full history of every change, use Git through a one-click launcher. See §9F. This step is optional.

This is the 3-2-1 rule in a simple form: your disk, an external drive, and (later, if you want) an off-site copy.

\---

## 8\. Folder Structure

Make one folder for each world. Keep all its parts together.

```
\~/Worlds/<WorldName>/
├── 00-World-Bible/        → Open this folder as an Obsidian vault
│   ├── Characters/
│   ├── Locations/
│   ├── Factions/
│   ├── Magic-Technology/
│   ├── History/
│   ├── Languages/
│   └── Templates/
├── 01-Manuscript/         → Open this folder as a novelWriter project
│   ├── Book-01/
│   └── Outlines/
├── 02-Maps/
├── 03-Art/
├── 04-Publishing/         → Exported PDF and EPUB files
└── 05-Backups/
```

Everything is plain Markdown in one folder, so the tools connect naturally. Obsidian reads the world bible. novelWriter reads the manuscript. One backup saves it all.

\---

## 9\. Install and Setup — step by step

All steps use a window and a mouse. Follow them in order.

**A. Install Linux Mint**

1. On another computer, download the Linux Mint XFCE ISO file.
2. Write the ISO to a USB stick with **balenaEtcher** (a simple graphical tool).
3. Back up the Windows files first. A disk resize always has some risk.
4. Start the laptop from the USB stick.
5. Start the installer. Choose "Install alongside Windows" for dual-boot.
6. Tick "Encrypt the new Linux Mint installation." Set a passphrase.
7. Create your user account. Finish the install and restart.

**B. Install the tools (no terminal)**

1. Open **Software Manager**.
2. Install: **Obsidian**, **novelWriter**, **FocusWriter**, **Calibre**, **Déjà Dup**. (LibreOffice is already there.)
3. Open **Firefox**. Add the **LeechBlock NG** add-on.

**C. Set up your world**

1. Make the folder structure from §8. Use the file manager, or ask me for a one-click script.
2. Open Obsidian. Choose "Open folder as vault." Select `00-World-Bible`.
3. In Obsidian settings, turn on community plugins. Install Dataview, Templater, Kanban, and Excalidraw.
4. Open novelWriter. Create a new project in `01-Manuscript`.

**D. Turn on backups**

1. Plug in a USB drive.
2. Open **Backups (Déjà Dup)**. Set the source to your Home folder. Turn on encryption and a weekly schedule.

**E. Optional — nicer print PDFs with Typst**
Do this only when you want book-quality PDFs.

* Ask me for one desktop launcher named "Export Book." You double-click it, choose a project, and it makes a print-ready PDF with Typst and Pandoc.
* Until then, use this simple path: export from novelWriter to ODT → open in LibreOffice → export a PDF. For an ebook, open the file in Calibre → convert to EPUB.

**F. Optional — version history with Git**

* Ask me for a "Save Snapshot" launcher. One click records the current state of your world. You can return to any earlier version later.

\---

## 10\. Daily Workflow

1. Open your world folder.
2. Plan and research in Obsidian (world bible, notes, links).
3. Outline and write in novelWriter. Turn on focus mode.
4. Revise in the same Markdown files.
5. Export a book when ready (§9E).
6. Let Déjà Dup back up your work each week.

There is little to manage. Most of your time goes to the story.

\---

## 11\. What We Kept, and What We Cut

**Kept (few compromises):**

* Worldbuilding, local wiki, outlining, drafting, revising, typesetting, and ebook — all present.
* Open formats, one connected folder, encryption, and backups.
* Distraction-free writing and a block on video and social sites.

**Cut (to save effort and risk):**

* The custom distribution. A stock system needs no special maintenance.
* Per-app AppArmor, Secure Boot keys, USBGuard, and the paranoid firewall. Encryption plus backups give strong, simple safety.
* Duplicate tools. One tool per task removes doubt.
* The full browser removal. A blocked browser keeps research and help available.

\---

> Start small. Add extras only when a real need appears. Keep the writing in Markdown, and the work will outlive every tool on this list.

