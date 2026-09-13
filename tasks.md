# Master Task Graph: Scriptorium Resource Collection & Implementation

## Task Checklist

### 1. Project Governance, Specifications & Policies (M0)
- [x] Create `SECURITY.md` (Formal vulnerability disclosure policy & 72-hour SLA)
- [x] Create `docs/SUPPORT_MATRIX.md` (OS tiers, architectures, display server matrix)
- [x] Create `docs/COMPATIBILITY.md` (Toolchain baselines, binary digests, Flatpak pins)
- [x] Create `.editorconfig` (Consistent line endings, UTF-8, indentation standards)
- [x] Clean `README.md` boilerplate and update with unified CLI & Control Center docs (AUD-03)
- [x] Pin CI actions in `.github/workflows/ci.yml` by immutable 40-char commit SHAs (AUD-04)

### 2. Software Resource Catalog & Documentation
- [x] Create `resources/software_catalog.md` (All core tools, download URLs, Flatpak/Apt commands, verification hashes)
- [x] Create `resources/optional_extras_guide.md` (Azgaar, Krita, Inkscape, Gramps, PolyGlot, Sigil, Kiwix)
- [x] Create `resources/typography_and_fonts_guide.md` (High-quality open fonts: Linux Libertine, EB Garamond, Alegreya, etc.)

### 3. Hardened Automation Scripts & Desktop Launchers (M1 / M4)
- [x] Harden `scripts/setup_scriptorium.sh` (OS gating, `--dry-run` simulation, categorized dependencies, elimination of `|| true`) (SEC-01, REL-02)
- [x] Create `scripts/uninstall_scriptorium.sh` (Clean rollback and uninstaller) (SEC-02)
- [x] Harden `scripts/init_world.sh` (Transactional staging, valid novelWriter XML, error trapping) (REL-01, UX-01)
- [x] Harden `scripts/export_book.sh` (Independent Pandoc error trapping, artifact size validation) (AUD-02)
- [x] Create `scripts/save_snapshot.sh` (One-click Git snapshot saver with desktop notification)
- [x] Create `scripts/scriptorium` (Unified CLI entrypoint dispatcher)
- [x] Create `scripts/control_center.sh` & `launchers/scriptorium-control-center.desktop` (GUI desktop control dashboard)
- [x] Create desktop launchers (`export-book.desktop`, `save-snapshot.desktop`, `init-world.desktop`)

### 4. Data Protection & Verified Disaster Recovery (M2)
- [x] Create `scripts/backup_world.sh` (Standalone compressed tarball archives with SHA-256 manifests) (REL-03)
- [x] Create `scripts/restore_world.sh` (Verified restore engine with hash checks and staging) (REL-03)
- [x] Update `templates/manuscript/nwProject.nwx` (Valid novelWriter fileVersion 1.5 XML schema) (UX-01)
- [x] Create `tests/fixtures/` (Unicode, multi-volume, novelWriter tag, and Typst special character fixtures)

### 5. Diagnostics & Domain Toolchain (M3)
- [x] Create `scripts/scriptorium_doctor.sh` (Unified System, Toolchain, Workspace, World, and Backup diagnostics)
- [x] Harden `scripts/world_doctor.sh` (Timeline chronological checks, entity schema validation, WLD-101..107 codes)
- [x] Enhance `scripts/wordcount_report.sh` (Manuscript analytics, volume/act aggregation, JSON & Markdown output)

### 6. Obsidian World Bible & Manuscript Starter Packs
- [x] Create Obsidian World Bible templates (Characters, Locations, Factions, Magic-Technology, History, Languages, Templates)
- [x] Create novelWriter Manuscript templates (Three-act structural outline, starter chapters in Book-01)
- [x] Create Typst typesetting book templates (`templates/typst/book_template.typ`, `preview_sample.typ`)
- [x] Create focus configs (`configs/leechblock_scriptorium_rules.json`, `xfce_dnd_setup.md`, `deja_dup_backup_guide.md`)

### 7. Narrative Universe Architecture & Out-of-the-Box Obsidian Suite (M5)
- [x] Create `scripts/init_universe.sh` (Universe scaffolding & Git repository initialization)
- [x] Enhance `scripts/init_world.sh` with `--universe` support and multi-tier Git repository setup (Universe -> World -> Manuscript)
- [x] Update `scripts/save_snapshot.sh` to traverse and snapshot multi-tier Git repositories
- [x] Update `scripts/scriptorium` CLI facade with `universe` command and `--universe` forwarding
- [x] Pre-configure Obsidian plugin configs: `dataview`, `longform`, `metadata-menu`, `calendarium`, `storyteller-suite`, `storyline`, `novel-word-count`, `obsidian-git`, `templater-obsidian`, `obsidian-style-settings`
- [x] Pre-configure strict Metadata Menu schemas in `templates/world-bible/Templates/fileClasses/` (`Character`, `Location`, `Faction`, `TimelineEvent`)
- [x] Configure automated Obsidian Git auto-commit (10-minute interval + save backup)
- [x] Declutter repository: safely delete legacy `audit_artifacts/`, `Plans/`, and `docs/archive/`
- [x] Document ADR-013 (Multi-Tier Git Architecture) and ADR-014 (Obsidian Plugin Suite) in `decisions.md`

### 8. Next-Gen Authoring & Worldbuilding Enhancements (M6–M10)
- [x] Enhance `scripts/export_book.sh` with `-b, --book <Volume>` selector, interactive GUI volume picker, and omnibus option (M6, ADR-015)
- [x] Update `scripts/scriptorium` CLI facade to forward `--book` flag (M6)
- [x] Enhance `templates/typst/book_template.typ` with ornamental scene breaks mapping and unindented paragraph helpers (M7)
- [x] Create `templates/world-bible/Bestiary/Creature-Flora-Fauna-Template.md` and `Templates/fileClasses/Creature.md` (M8, ADR-016)
- [x] Create `templates/world-bible/Artifacts/Artifact-Relic-Template.md` and `Templates/fileClasses/Artifact.md` (M8, ADR-016)
- [x] Create `templates/world-bible/Cosmology/Deity-Cosmology-Template.md` and `Templates/fileClasses/Cosmology.md` (M8, ADR-016)
- [x] Update `templates/world-bible/Templates/World-Bible-Index.md` with Bestiary, Artifacts, and Cosmology Dataview tables (M8)
- [x] Update `scripts/world_doctor.sh` to validate `creature`, `artifact`, and `cosmology` entity types (M8)
- [x] Update `scripts/init_world.sh` to scaffold `Bestiary/`, `Artifacts/`, and `Cosmology/` folders (M8)
- [x] Add transient `.git/index.lock` wait-and-retry helper to `scripts/save_snapshot.sh` (M9)
- [x] Add `Universe-Index.md` generation in `scripts/init_universe.sh` (M9)
- [x] Document ADR-015 and ADR-016 in `decisions.md` (M10)

### 9. Unified GTK 3 Desktop Application & Author's Field Manual (M11)
- [x] Create `scripts/scriptorium_app.py` (Python 3 / PyGObject GTK 3 native desktop control center with 5-tab author workflow) (ADR-017)
- [x] Update `scripts/control_center.sh` with seamless GTK 3 launch and Zenity fallback
- [x] Implement First-Flight onboarding welcoming dialog and 1-click demo cosmos (*"The Chronicles of Eldoria"*)
- [x] Create `docs/AUTHOR_MANUAL.md` (Visual 8-chapter plain-English author handbook)
- [x] Document ADR-017 (Unified Python GTK Desktop Control Center & Author Onboarding Architecture) in `decisions.md`

### 10. Verification & Release Gates
- [x] Expand `scripts/verify.sh` 7-stage verification suite with Python compilation, Author Manual check, Universe/World lifecycle, expanded taxonomy, and multi-volume tests
- [x] Pass all automated checks via `bash scripts/verify.sh` (`ALL-CHECKS-PASS`)
- [ ] Final live acceptance test on physical Linux Mint / Debian desktop


