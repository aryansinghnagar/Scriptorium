# Privacy Policy & User Data Protection in Ars Arcanum

**Last Updated:** September 2026  
**Project:** Ars Arcanum  
**Repository:** https://github.com/aryansinghnagar/Scriptorium

---

## 1. Core Privacy Philosophy

Ars Arcanum is built on a strict **local-first, zero-telemetry, privacy-by-design** philosophy. As a creative authoring platform, your worldbuilding, manuscripts, lore, notes, and creative output belong exclusively to you. 

- **100% Offline Operation:** All core utilities, CLI commands (`arcanum`), scaffolding scripts, typesetting bridges (Typst/Pandoc), diagnostic tools (`arcanum doctor`), and GUI dashboards run entirely on your local machine.
- **Zero Telemetry & Analytics:** Ars Arcanum contains zero analytics scripts, zero telemetry, zero error-reporting daemons, zero tracking pixels, and zero background network calls.
- **Zero Remote Dependency for Authoring:** No user registration, authentication, API keys, or cloud accounts are required to use any feature of Ars Arcanum.

---

## 2. Data Minimization & Express User Consent

Ars Arcanum adheres strictly to the principle of data minimization: it only touches and stores the minimum data necessary to function, and only with your express initiation and consent.

### What Ars Arcanum Stores on Your System
1. **User Creative Projects (`~/Universes/`, `~/Manuscripts/`):**
   - Created **only** when you invoke a creation command (e.g., `arcanum universe <name>`, `arcanum world <name>`, `arcanum manuscript <name>`, or the Control Center wizards).
   - Stored in standard, open formats (Markdown `.md`, YAML, and `.typ`) in user-accessible directories on your local filesystem.
2. **Local Version Snapshots (Git):**
   - Initialized locally in each world vault and manuscript repository.
   - Snapshot commits (`arcanum snapshot`) are saved strictly to the local `.git` repository on your drive.
   - Ars Arcanum **never** pushes your code, notes, or manuscripts to any remote server or cloud provider automatically. Remote syncing is entirely under your manual control.
3. **Local Performance Cache (`.arcanum_cache.json`):**
   - Created locally within universe and manuscript roots to accelerate word count reports and diagnostics (`--fast` mode).
   - Contains only file paths, file modification timestamps (mtime), SHA-256 content hashes, and token counts.
   - Contains no user metadata or network identifiers. It can be cleared at any time via `arcanum cache-clear` or manual deletion without affecting your documents.
4. **Local Configuration (`~/.config/ars-arcanum` or `~/.config/arcanum`):**
   - Optional local preference files (such as window geometry or default export presets) stored in standard XDG user configuration directories.

---

## 3. Network Usage Transparency

Ars Arcanum only uses network connections in two explicit, user-initiated circumstances:
1. **Installation & Setup (`setup_arcanum.sh`):**
   - If missing required system dependencies (e.g., Typst, fonts, Pandoc, Obsidian), package managers (`apt`, `flatpak`, `curl`) fetch official upstream open-source packages.
   - SHA-256 checksums are strictly verified for non-packaged binary releases (e.g., Typst binary fail-closed verification).
2. **Optional User-Configured Sync:**
   - If you choose to configure a remote Git repository (e.g., GitHub, GitLab, private Forgejo/Gitea server) or cloud backup endpoint (Restic / Borg), network traffic occurs solely between your machine and your chosen destination.

---

## 4. Diagnostics & Reporting

The diagnostic toolchain (`arcanum doctor` / `scripts/world_doctor.sh`):
- Operates 100% locally.
- Scans YAML frontmatter, Markdown syntax, and Wikilink relationships within your local workspace.
- Prints findings solely to your local standard output or GTK window.
- Never sends diagnostic logs or crash dumps over the network.

---

## 5. Security & Vulnerability Disclosures

Security inquiries and vulnerability reports are managed without exposing personal maintainer or contributor private details. Please report security issues via:
- **GitHub Private Vulnerability Advisories:** [https://github.com/aryansinghnagar/Scriptorium/security/advisories/new](https://github.com/aryansinghnagar/Scriptorium/security/advisories/new)

---

## 6. User Rights & Data Portability

- **Full Data Ownership:** You retain 100% ownership and copyright of everything you create within Ars Arcanum.
- **No Vendor Lock-In:** All content is saved in plain text Markdown and standard YAML frontmatter, readable by any text editor, standard Git client, or publishing pipeline.
- **Complete Erasure:** You can completely uninstall the toolkit at any time using `scripts/uninstall_arcanum.sh`. Your manuscript and universe files remain untouched in your home folder unless you explicitly choose to delete them.
