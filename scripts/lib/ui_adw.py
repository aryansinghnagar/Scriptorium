#!/usr/bin/env python3
"""
Ars Arcanum Modern GTK 4 / Libadwaita Presentation Layer (scripts/lib/ui_adw.py)
Implements adaptive modern desktop views, system dark-mode synchronization,
and responsive controls for GNOME / modern Linux desktops.
"""

import sys
import subprocess
import threading
import logging
from pathlib import Path

try:
    from lib.fs_utils import atomic_write
except ImportError:
    try:
        from fs_utils import atomic_write
    except ImportError:
        def atomic_write(path, data, encoding="utf-8"):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(data, (bytes, bytearray)):
                p.write_bytes(data)
            else:
                p.write_text(data, encoding=encoding)

logger = logging.getLogger("arcanum.ui_adw")

HAS_ADW = False
try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Gtk, Adw, GLib
    HAS_ADW = True
except (ImportError, ValueError):
    HAS_ADW = False

HOME_DIR = Path.home()
UNIVERSES_DIR = HOME_DIR / "Universes"
MANUSCRIPTS_DIR = HOME_DIR / "Manuscripts"
WORLDS_DIR = HOME_DIR / "Worlds"
SCRIPT_DIR = Path(__file__).resolve().parent.parent


def make_action_row(title: str, subtitle: str | None = None):
    """Creates an Adw.ActionRow with properly escaped Pango markup."""
    row = Adw.ActionRow()
    if HAS_ADW:
        row.set_title(GLib.markup_escape_text(title))
        if subtitle:
            row.set_subtitle(GLib.markup_escape_text(subtitle))
    return row


def make_pref_group(title: str, description: str | None = None):
    """Creates an Adw.PreferencesGroup with properly escaped Pango markup."""
    group = Adw.PreferencesGroup()
    if HAS_ADW:
        group.set_title(GLib.markup_escape_text(title))
        if description:
            group.set_description(GLib.markup_escape_text(description))
    return group


class ArcanumAppAdw:
    """Modern Libadwaita desktop application for Ars Arcanum."""

    def __init__(self, application=None, active_tab: str | None = None):
        if not HAS_ADW:
            raise RuntimeError("Libadwaita / GTK 4 is not available.")

        self.app = application
        self.window = Adw.ApplicationWindow(application=self.app, title="Ars Arcanum Studio")
        self.window.set_default_size(1100, 760)

        self.current_universe = None
        self.current_world_path = None
        self.current_manuscript_path = None

        # Main Box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Header Bar with View Switcher Title
        header = Adw.HeaderBar()
        self.view_stack = Adw.ViewStack()
        
        view_switcher_title = Adw.ViewSwitcherTitle()
        view_switcher_title.set_stack(self.view_stack)
        view_switcher_title.set_title("Ars Arcanum")
        view_switcher_title.set_subtitle("Author & Worldbuilder Studio")
        header.set_title_widget(view_switcher_title)

        # Snapshot quick button
        snap_btn = Gtk.Button(label="📷 Snapshot")
        snap_btn.add_css_class("suggested-action")
        snap_btn.connect("clicked", self._on_quick_snapshot)
        header.pack_end(snap_btn)

        main_box.append(header)

        # View Switcher Bar (for adaptive narrow screens)
        view_switcher_bar = Adw.ViewSwitcherBar()
        view_switcher_bar.set_stack(self.view_stack)

        # Pages in ViewStack
        self.page_cosmos = self._create_cosmos_page()
        self.page_drafting = self._create_drafting_page()
        self.page_speculative = self._create_speculative_page()
        self.page_publishing = self._create_publishing_page()
        self.page_safety = self._create_safety_page()
        self.page_diagnostics = self._create_diagnostics_page()

        self.view_stack.add_titled_with_icon(self.page_cosmos, "cosmos", "Universes", "folder-symbolic")
        self.view_stack.add_titled_with_icon(self.page_drafting, "drafting", "Drafting", "document-edit-symbolic")
        self.view_stack.add_titled_with_icon(self.page_speculative, "worldbuilding", "Speculative", "applications-science-symbolic")
        self.view_stack.add_titled_with_icon(self.page_publishing, "publishing", "Publishing", "applications-office-symbolic")
        self.view_stack.add_titled_with_icon(self.page_safety, "safety", "Safety & Git", "security-high-symbolic")
        self.view_stack.add_titled_with_icon(self.page_diagnostics, "diagnostics", "Doctor", "system-search-symbolic")

        if active_tab:
            tab_clean = active_tab.lower().strip()
            tab_map = {
                "cosmos": "cosmos", "universe": "cosmos", "universes": "cosmos", "world": "cosmos", "worlds": "cosmos",
                "drafting": "drafting", "manuscript": "drafting", "manuscripts": "drafting", "novel": "drafting", "writing": "drafting", "write": "drafting", "comparator": "drafting", "diff": "drafting", "compare": "drafting",
                "worldbuilding": "worldbuilding", "speculative": "worldbuilding", "engines": "worldbuilding", "lore": "worldbuilding", "magic": "worldbuilding",
                "publishing": "publishing", "typesetting": "publishing", "export": "publishing", "publish": "publishing",
                "safety": "safety", "backups": "safety", "snapshots": "safety", "backup": "safety", "snapshot": "safety", "git": "safety",
                "doctor": "diagnostics", "diagnostics": "diagnostics", "health": "diagnostics", "check": "diagnostics"
            }
            if tab_clean in tab_map:
                self.view_stack.set_visible_child_name(tab_map[tab_clean])

        main_box.append(self.view_stack)
        main_box.append(view_switcher_bar)

        # Status Bar / Toast Overlay (Attach main_box as child of overlay, then overlay to window)
        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(main_box)
        self.window.set_content(self.toast_overlay)

    def _show_toast(self, message: str):
        toast = Adw.Toast.new(message)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)

    def _create_cosmos_page(self) -> Gtk.Widget:
        page = Adw.PreferencesPage()
        group = make_pref_group("World Lore Vaults & Cartography", "Manage Obsidian worldbuilding vaults, maps, and codices")
        
        row_new_univ = make_action_row("Create New Universe", "Scaffold an overarching cosmos container")
        btn_u = Gtk.Button(label="New Universe")
        btn_u.set_valign(Gtk.Align.CENTER)
        btn_u.connect("clicked", lambda x: self._run_script_dialog("init_universe.sh", "Universe Name:"))
        row_new_univ.add_suffix(btn_u)
        group.add(row_new_univ)

        row_new_world = make_action_row("Create New World Vault", "Scaffold an Obsidian Lore Bible with full plugin suite")
        btn_w = Gtk.Button(label="New World")
        btn_w.set_valign(Gtk.Align.CENTER)
        btn_w.connect("clicked", lambda x: self._run_script_dialog("init_world.sh", "World Name:"))
        row_new_world.add_suffix(btn_w)
        group.add(row_new_world)

        row_map = make_action_row("Interactive Vector Cartography", "Generate SVG maps with hex grids and trade routes")
        btn_map = Gtk.Button(label="Open Map")
        btn_map.set_valign(Gtk.Align.CENTER)
        btn_map.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "cartography.py"), str(WORLDS_DIR)], "Map generated"))
        row_map.add_suffix(btn_map)
        group.add(row_map)

        row_codex = make_action_row("Export Static Lore Codex", "Compile searchable offline encyclopedia wiki")
        btn_codex = Gtk.Button(label="Export Codex")
        btn_codex.set_valign(Gtk.Align.CENTER)
        btn_codex.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "codex_export.py"), str(WORLDS_DIR)], "Codex exported"))
        row_codex.add_suffix(btn_codex)
        group.add(row_codex)

        page.add(group)
        return page

    def _create_drafting_page(self) -> Gtk.Widget:
        page = Adw.PreferencesPage()
        group = make_pref_group("Manuscript Projects & Narrative Craft", "Drafting workspaces, multi-track plot matrix & structural pacing")

        row_new_ms = make_action_row("Create New Manuscript", "Scaffold 3-Act novelWriter & Markdown workspace")
        btn_ms = Gtk.Button(label="New Manuscript")
        btn_ms.set_valign(Gtk.Align.CENTER)
        btn_ms.connect("clicked", lambda x: self._run_script_dialog("init_manuscript.sh", "Manuscript Name:"))
        row_new_ms.add_suffix(btn_ms)
        group.add(row_new_ms)

        row_add_vol = make_action_row("Add Book / Volume", "Add auto-incremented volume to existing manuscript")
        btn_vol = Gtk.Button(label="Add Volume")
        btn_vol.set_valign(Gtk.Align.CENTER)
        btn_vol.connect("clicked", lambda x: self._run_script_dialog("add_book.sh", "Target Manuscript:"))
        row_add_vol.add_suffix(btn_vol)
        group.add(row_add_vol)

        row_plot = make_action_row("Multi-Track Plot Grid", "Analyze subplot pacing and timeline health")
        btn_plot = Gtk.Button(label="Plot Matrix")
        btn_plot.set_valign(Gtk.Align.CENTER)
        btn_plot.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "plot_matrix.py"), str(MANUSCRIPTS_DIR)], "Plot Grid generated"))
        row_plot.add_suffix(btn_plot)
        group.add(row_plot)

        row_struct = make_action_row("Story Paradigm Enforcer", "Validate 3-Act, Save the Cat, and Hero's Journey beats")
        btn_struct = Gtk.Button(label="Structure")
        btn_struct.set_valign(Gtk.Align.CENTER)
        btn_struct.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "structure.py"), str(MANUSCRIPTS_DIR)], "Structure evaluated"))
        row_struct.add_suffix(btn_struct)
        group.add(row_struct)

        row_tts = make_action_row("Audio Proofreader (TTS)", "Listen to chapters with neural WebAudio playback")
        btn_tts = Gtk.Button(label="Audio Read")
        btn_tts.set_valign(Gtk.Align.CENTER)
        btn_tts.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "tts_reader.py"), str(MANUSCRIPTS_DIR)], "Audio Reader opened"))
        row_tts.add_suffix(btn_tts)
        group.add(row_tts)

        page.add(group)
        return page

    def _create_speculative_page(self) -> Gtk.Widget:
        page = Adw.PreferencesPage()
        group = make_pref_group("Speculative Fiction & Simulation Engines", "In-world modeling, tactical combat, and constraint verification")

        engines = [
            ("Astrophysics & Flight", "Relativistic Brachistochrone 1g transit, Lorentz dilation, orbits", "astrophysics.py", ["transit", "alpha-centauri"]),
            ("Hard Magic Constraints", "Affinity tier validation, reagent checks, fatigue curves", "magic_system.py", ["report"]),
            ("Dynastic Genealogies", "Mermaid family trees, succession claim validation", "genealogy.py", ["lineage", "House"]),
            ("Conlang Phonotactics", "Syllable word generator, historical sound shifts", "conlang.py", ["generate", "Solar Tongue"]),
            ("Pacing & Tension Arcs", "Prose mode analyzer, POV balance, tension curves", "pacing.py", ["pace"]),
            ("Journeys & Calendars", "Expedition calculator, multi-moon synodic cycles", "journey.py", ["150 km"]),
            ("Geopolitical Factions", "Alliance chord diagrams, Lanchester combat modeler", "factions.py", ["matrix"]),
            ("Economy & Tech Eras", "PPP commodity basket, price outlier scanner, tech era linter", "economy.py", ["check"]),
            ("Causal DAGs & Multiverse", "Timeline DAG visualizer, Novikov paradox checker", "causality.py", ["check"]),
            ("Climate & Trophic Webs", "Stellar flux insolation, Lindeman 10% trophic webs", "climate.py", ["--star-lum", "1.0"]),
            ("Earth Idioms & 6D Senses", "Immersion de-eponym linter, 6D sensory palette analyzer", "idioms.py", []),
            ("Ciphers & Prophecy Matrix", "Caesar/Vigenere/runes SVG cards, oracle fulfillment tracker", "cipher.py", ["runes", "Speak friend"]),
            ("Tactical Combat Simulator", "Turn-based battle simulator & blow-by-blow choreography log", "tactical_sim.py", ["sim"]),
            ("Focus Ambient Generator", "Procedural noise & binaural beat soundscapes", "ambient.py", ["generate"]),
        ]

        for title, desc, script, args in engines:
            row = make_action_row(title, desc)
            btn = Gtk.Button(label="Launch")
            btn.set_valign(Gtk.Align.CENTER)
            cmd = [sys.executable, str(SCRIPT_DIR / "lib" / script)] + args
            btn.connect("clicked", lambda x, c=cmd, t=title: self._run_bg(c, f"{t} executed"))
            row.add_suffix(btn)
            group.add(row)

        page.add(group)
        return page

    def _create_publishing_page(self) -> Gtk.Widget:
        page = Adw.PreferencesPage()
        group = make_pref_group("Pre-Flight Typesetting & Publishing Compliance", "Verification, ISBN barcodes, front matter & distribution packaging")

        row_preflight = make_action_row("Pre-Flight Typesetting Linter", "Check formatting, metadata, and print-on-demand compliance")
        btn_pref = Gtk.Button(label="Run Pre-Flight")
        btn_pref.set_valign(Gtk.Align.CENTER)
        btn_pref.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "preflight.py"), str(MANUSCRIPTS_DIR)], "Pre-Flight check complete"))
        row_preflight.add_suffix(btn_pref)
        group.add(row_preflight)

        row_barcode = make_action_row("ISBN-13 Barcode Generator", "Generate crisp vector SVG/PNG publishing barcode")
        btn_bar = Gtk.Button(label="Generate Barcode")
        btn_bar.set_valign(Gtk.Align.CENTER)
        btn_bar.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "barcode.py"), "978-0-345-39180-3"], "Barcode generated"))
        row_barcode.add_suffix(btn_bar)
        group.add(row_barcode)

        row_matter = make_action_row("Modular Front & Back Matter", "Build copyright, dedication, epigraph, and discussion questions")
        btn_mat = Gtk.Button(label="Build Matter")
        btn_mat.set_valign(Gtk.Align.CENTER)
        btn_mat.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "frontmatter_builder.py"), "build", str(MANUSCRIPTS_DIR)], "Front/Back matter scaffolded"))
        row_matter.add_suffix(btn_mat)
        group.add(row_matter)

        row_query = make_action_row("Submission Query Package", "Scaffold 1-page query letter, synopsis, and agent tracker")
        btn_qry = Gtk.Button(label="Scaffold Query")
        btn_qry.set_valign(Gtk.Align.CENTER)
        btn_qry.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "init_query.py"), str(MANUSCRIPTS_DIR)], "Query package scaffolded"))
        row_query.add_suffix(btn_qry)
        group.add(row_query)

        row_typ = make_action_row("Polish Smart Typography", "Normalize curly quotes, em-dashes, and ellipses")
        btn_typ = Gtk.Button(label="Polish Typography")
        btn_typ.set_valign(Gtk.Align.CENTER)
        btn_typ.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "typography_cleaner.py"), str(MANUSCRIPTS_DIR)], "Typography polished"))
        row_typ.add_suffix(btn_typ)
        group.add(row_typ)

        row_export = make_action_row("Export Complete Manuscript", "Build trade PDF, standard submission DOCX, and EPUB")
        btn_exp = Gtk.Button(label="Build Exports")
        btn_exp.add_css_class("suggested-action")
        btn_exp.set_valign(Gtk.Align.CENTER)
        btn_exp.connect("clicked", self._on_export_clicked)
        row_export.add_suffix(btn_exp)
        group.add(row_export)

        row_pkg = make_action_row("Package Distribution Release", "Bundle reader editions, submission archives, and ARCs")
        btn_pkg = Gtk.Button(label="Package Release")
        btn_pkg.set_valign(Gtk.Align.CENTER)
        btn_pkg.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "package_distribution.py"), str(MANUSCRIPTS_DIR)], "Release package created"))
        row_pkg.add_suffix(btn_pkg)
        group.add(row_pkg)

        page.add(group)
        return page

    def _create_safety_page(self) -> Gtk.Widget:
        page = Adw.PreferencesPage()
        group = make_pref_group("Multi-Tier Git & Disaster Recovery", "Version milestones and standalone encrypted backups")

        row_snap = make_action_row("Record Version Snapshot", "Atomic multi-tier Git milestone with message")
        btn_snap = Gtk.Button(label="Save Snapshot")
        btn_snap.set_valign(Gtk.Align.CENTER)
        btn_snap.connect("clicked", self._on_quick_snapshot)
        row_snap.add_suffix(btn_snap)
        group.add(row_snap)

        row_bak = make_action_row("Create Backup Tarball", "Standalone SHA-256 archive of worlds and manuscripts")
        btn_bak = Gtk.Button(label="Backup Now")
        btn_bak.set_valign(Gtk.Align.CENTER)
        btn_bak.connect("clicked", lambda x: self._run_bg([str(SCRIPT_DIR / "backup_world.sh")], "Backup created successfully"))
        row_bak.add_suffix(btn_bak)
        group.add(row_bak)

        page.add(group)
        return page

    def _create_diagnostics_page(self) -> Gtk.Widget:
        page = Adw.PreferencesPage()
        group = make_pref_group("Prose Audits, Voice Profiling & Continuity", "Dialogue mechanics, character voice bleed, and series continuity")

        row_styl = make_action_row("Dialogue Mechanics & Echoes", "Scan said-bookisms, adverb tags, and word echo fatigue")
        btn_styl = Gtk.Button(label="Audit Prose")
        btn_styl.set_valign(Gtk.Align.CENTER)
        btn_styl.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "stylistics.py"), "scan", str(MANUSCRIPTS_DIR)], "Prose craft audit completed"))
        row_styl.add_suffix(btn_styl)
        group.add(row_styl)

        row_voice = make_action_row("Character Voice Profiler", "Analyze vocabulary distinctiveness and detect voice bleed")
        btn_voice = Gtk.Button(label="Voice Profiler")
        btn_voice.set_valign(Gtk.Align.CENTER)
        btn_voice.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "voice.py"), str(MANUSCRIPTS_DIR)], "Voice Profiler scan complete"))
        row_voice.add_suffix(btn_voice)
        group.add(row_voice)

        row_mru = make_action_row("Scene Mechanics MRU Analyzer", "Motivation-Reaction Units and proactive scene balance")
        btn_mru = Gtk.Button(label="MRU Analyzer")
        btn_mru.set_valign(Gtk.Align.CENTER)
        btn_mru.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "scene_mechanics.py"), str(MANUSCRIPTS_DIR)], "MRU scan completed"))
        row_mru.add_suffix(btn_mru)
        group.add(row_mru)

        row_series = make_action_row("Series Cross-Book Continuity", "Track mortality and physical traits across multiple books")
        btn_series = Gtk.Button(label="Series Ledger")
        btn_series.set_valign(Gtk.Align.CENTER)
        btn_series.connect("clicked", lambda x: self._run_bg([sys.executable, str(SCRIPT_DIR / "lib" / "series_continuity.py"), str(MANUSCRIPTS_DIR)], "Series Continuity verified"))
        row_series.add_suffix(btn_series)
        group.add(row_series)

        row_doc = make_action_row("Run World Doctor", "Verify link integrity, YAML schemas, and chronology")
        btn_doc = Gtk.Button(label="Scan Lore")
        btn_doc.set_valign(Gtk.Align.CENTER)
        btn_doc.connect("clicked", lambda x: self._run_bg([str(SCRIPT_DIR / "world_doctor.sh"), "--fast"], "World Doctor scan complete"))
        row_doc.add_suffix(btn_doc)
        group.add(row_doc)

        row_con = make_action_row("Build Concordance", "Generate Dramatis Personae & Glossary back-matter")
        btn_con = Gtk.Button(label="Generate")
        btn_con.set_valign(Gtk.Align.CENTER)
        btn_con.connect("clicked", lambda x: self._run_bg([str(SCRIPT_DIR / "generate_concordance.sh")], "Concordance generated"))
        row_con.add_suffix(btn_con)
        group.add(row_con)

        row_cont = make_action_row("Check Semantic Continuity", "Flag character trait & narrative claim discrepancies")
        btn_cont = Gtk.Button(label="Check Continuity")
        btn_cont.set_valign(Gtk.Align.CENTER)
        btn_cont.connect("clicked", self._on_check_continuity)
        row_cont.add_suffix(btn_cont)
        group.add(row_cont)

        page.add(group)
        return page

    def _on_quick_snapshot(self, widget):
        self._run_bg([str(SCRIPT_DIR / "save_snapshot.sh"), "-m", "Quick Snapshot via Adw Studio"], "Snapshot saved successfully")

    def _on_export_clicked(self, widget):
        self._run_bg([str(SCRIPT_DIR / "export_book.sh")], "Export build completed")

    def _on_check_continuity(self, widget):
        cont_script = SCRIPT_DIR / "lib" / "continuity.py"
        if cont_script.is_file():
            self._run_bg([sys.executable, str(cont_script)], "Continuity scan completed")
        else:
            self._show_toast("Continuity engine module not found.")

    def _run_script_dialog(self, script_name: str, prompt: str):
        cmd = str(SCRIPT_DIR / script_name)
        self._run_bg([cmd], f"Executed {script_name}")

    def _run_bg(self, cmd: list, success_msg: str):
        def worker():
            try:
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode in (0, 3):
                    GLib.idle_add(self._show_toast, success_msg)
                else:
                    err = res.stderr.strip().splitlines()[-1] if res.stderr else "Operation completed"
                    GLib.idle_add(self._show_toast, f"Notice: {err}")
            except Exception as e:
                logger.error("Error executing command %s: %s", cmd, e)
                GLib.idle_add(self._show_toast, f"Error: {str(e)}")

        threading.Thread(target=worker, daemon=True).start()

    def present(self):
        self.window.present()


def run_adw_app(active_tab: str | None = None):
    if not HAS_ADW:
        return False
    app = Adw.Application(application_id="org.arsarcanum.ArsArcanum")
    
    def on_activate(application):
        win = ArcanumAppAdw(application, active_tab=active_tab)
        win.present()

    app.connect("activate", on_activate)
    return app.run([])
