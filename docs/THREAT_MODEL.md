# Ars Arcanum Threat Model & Security Posture (STRIDE-Lite)

**Version:** 1.6.0  
**Scope:** Core CLI (`arcanum`), Scaffolding Scripts, Python Library Engines (`scripts/lib/`), GTK Control Center, Typesetting Bridges (Typst/Pandoc), and Storage/Backup Subsystems.  
**Target Environment:** Local single-user Linux desktop workstations (Ubuntu, Linux Mint, Debian, Arch, Fedora).

---

## 1. System Architecture & Trust Boundaries

Ars Arcanum operates exclusively as a **local-first desktop platform**. It does not expose public network ports, run persistent daemon listeners, or transmit user prose or metadata to cloud backends.

### Key Trust Boundaries:
1. **User Working Tree (`~/Universes/`, `~/Manuscripts/`)**: Trusted local filesystem where author prose, notes, and manifests are stored and versioned via local Git.
2. **Untrusted External Inputs**:
   - Word Documents (`.docx`) imported from beta readers, co-authors, or editors.
   - Restored Backup Archives (`.tar.gz`) from external or shared drives.
   - Markdown notes containing arbitrary user text, YAML frontmatter, and WikiLinks (`[[...]]`).
   - Community Obsidian Plugin configurations (`.obsidian/`).
3. **Privileged Installer Surface**: `setup_arcanum.sh` (the only script invoking `sudo` for system dependencies).
4. **Offline Viewing Sandbox**: Generated static HTML visualization reports and charts opened in local web browsers.

```
[ External DOCX / Backup Archives / Community Plugins ] (Untrusted)
                         │
                         ▼ (Sanitization & Validation Barrier)
[ Ars Arcanum Core Engines: docx_sync, world_doctor, restore_world, cli ]
                         │
                         ▼ (Atomic Writes & Local Git)
[ Local Author Workspaces: ~/Universes, ~/Manuscripts ] (Trusted)
```

---

## 2. STRIDE-Lite Threat Analysis & Mitigations

### 1. Spoofing Identity (S)
* **Threat S1: Git Author Spoofing during Scaffolding.**
  - *Risk:* Automated scaffolding commits using an arbitrary or misleading identity (e.g. `maintainers@arsarcanum.local`), overwriting author attribution.
  - *Mitigation:* Scaffolding scripts query `git config user.name` and `git config user.email`. If configured, the user's authentic local Git identity is used. If unset, a neutral tool identity (`Ars Arcanum Studio <arcanum@local>`) is applied.
* **Threat S2: Desktop Launcher Impersonation.**
  - *Risk:* Malicious `.desktop` files masquerading as Ars Arcanum studio tools.
  - *Mitigation:* Launchers are installed directly to `${HOME}/.local/share/applications/` from hardcoded template sources with explicit paths and trusted metadata via `gio set metadata::trusted true`.

### 2. Tampering with Data (T)
* **Threat T1: Power Loss or Crash during File Write (Data Corruption).**
  - *Risk:* Mid-write crashes corrupting manuscripts, chapters, or world manifests.
  - *Mitigation:* All write operations across all library modules use `atomic_write()` (`scripts/lib/fs_utils.py`), writing to a temporary file in the same parent directory, flushing, syncing (`fsync`), and atomically replacing via `os.replace`.
* **Threat T2: Silent Prose Loss during DOCX ↔ Markdown Synchronization.**
  - *Risk:* Asymmetrical mtime updates causing newer Markdown prose to be overwritten by older DOCX files.
  - *Mitigation:* Three-way SHA-256 state tracking (`.sync_state.json`). If both Markdown and DOCX diverge independently, the engine refuses in-place overwrite and branches to `<chapter>.conflict_<timestamp>.md`.
* **Threat T3: Backup Archive Tampering.**
  - *Risk:* Accidental corruption or byte alteration in `.tar.gz` backups.
  - *Mitigation:* Every archive generation emits a companion `.sha256` digest sidecar verified before any restoration drill.

### 3. Repudiation (R)
* **Threat R1: Untracked Draft Modifications.**
  - *Risk:* Authors unable to identify what changed between draft revisions.
  - *Mitigation:* Automatic draft milestone snapshotting (`arcanum draft`) and fine-grained visual redline diff reporting (`manuscript_diff.py`).
* **Threat R2: Ambiguous Upgrade Path.**
  - *Risk:* Untracked schema alterations causing silent engine parsing failures.
  - *Mitigation:* Explicit `schema_version` declarations in `universe.yaml`, `world.yaml`, and `manuscript.yaml`, paired with verified automated migrations (`arcanum migrate`).

### 4. Information Disclosure / Privacy (I)
* **Threat I1: Telemetry & Prose Leakage.**
  - *Risk:* Unintentional transmission of author creative work, character names, or system telemetry over the network.
  - *Mitigation:* Strict zero-telemetry architecture. Core engines perform 0 network calls. External CDN references are prohibited in generated HTML and codebase.
* **Threat I2: Path & Username Leakage in Bug Reports.**
  - *Risk:* Sensitive user home directory paths, system usernames, or private novel titles exposed when submitting diagnostic logs.
  - *Mitigation:* `arcanum doctor --report` (`diagnostics.py`) automatically sanitizes and redacts local home directory paths (`~`) and usernames before emitting triage markdown bundles.

### 5. Denial of Service (D)
* **Threat D1: Malicious Archive Extraction (Tar-Bomb / Symlink Traversal).**
  - *Risk:* An untrusted backup archive attempting path traversal (`../../etc/passwd`) or symlink overwrites during restoration.
  - *Mitigation:* `restore_world.sh` verifies all archive members using Python `tarfile` before extraction, explicitly rejecting symlinks, hardlinks, absolute paths, and parent traversals (`..`), extracting only regular files and directories.
* **Threat D2: Large File Read Exhaustion.**
  - *Risk:* Extremely large files causing out-of-memory errors in linters or parsers.
  - *Mitigation:* `read_capped()` enforces a 2MB per-file read threshold across analysis engines with user-facing warnings upon truncation.
* **Threat D3: XML Entity Expansion (Billion Laughs / Quadratic Blowup).**
  - *Risk:* Malicious DOCX XML files containing recursive entity definitions.
  - *Mitigation:* Safe standard XML extraction without external entity resolution, combined with file size verification.

### 6. Elevation of Privilege (E)
* **Threat E1: Installer Privilege Abuse.**
  - *Risk:* System installer executing unvetted scripts or modifying unauthorized system paths with root permissions.
  - *Mitigation:* `setup_arcanum.sh` restricts `sudo` exclusively to explicit package manager calls (`apt-get install` with declared package lists) and verified Typst musl binary installation. All author workspaces, desktop launchers, and configuration files are written under user `${HOME}` without root elevation.

---

## 3. Content Security Policy (CSP) Baseline

All static HTML reports generated by Ars Arcanum (e.g. cartography, codex wiki, causal DAGs, timeline graphs, and audio proofreader players) must declare the following strict offline Content Security Policy:

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
```

- **`default-src 'none'`**: Disallows any external network requests, fonts, or tracking frames.
- **`style-src 'unsafe-inline'`**: Allows self-contained inline CSS styles.
- **`script-src 'unsafe-inline'`**: Restricts JavaScript execution to self-contained inline logic (e.g. SVG zoom/pan or WebAudio synthesizer) without loading remote scripts.
- **`img-src data:`**: Allows embedded base64 images and vector icons.

---

## 4. Security Incident Response SLA

Vulnerabilities are managed via **GitHub Private Vulnerability Reporting**:
- Initial triage acknowledgment: **≤ 72 hours**
- Fix deployment: **≤ 30 days**
