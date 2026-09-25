#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 Speculative & Craft Dialogs (scripts/lib/ui_gtk3/dialogs.py)
============================================================================
Provides modal dialog interfaces for all 30 speculative, craft, and publishing engines.
"""

import sys
from pathlib import Path

from lib.ui_gtk3.common import (
    MANUSCRIPTS_DIR,
    PROJECT_ROOT,
    WORLDS_DIR,
    Gtk,
)


class SpeculativeDialogsMixin:
    """Mixin providing all 30 craft and speculative dialog launchers."""

    # -------------------------------------------------------------------------
    # Speculative Fiction Engines (Wave 1–12)
    # -------------------------------------------------------------------------
    def open_astrophysics_dialog(self):
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "astrophysics.py"), "transit", "--accel", "9.81", "--distance", "4.24"]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Launching Relativistic Astrophysics Modeler...")

    def open_magic_dialog(self):
        target_w = self.current_world_path or str(WORLDS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "magic_system.py"), "report", target_w]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Verifying Hard Magic System Constraints...")

    def open_genealogy_dialog(self):
        target_w = self.current_world_path or str(WORLDS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "genealogy.py"), "html", target_w]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Compiling Dynastic Lineage DAGs...")

    def open_conlang_dialog(self):
        dialog, box = self._create_dialog_shell("Conlang Phonotactics & Lexicon Studio", 720, 480)
        lbl = Gtk.Label(label="Generate phonotactic lexicons, apply sound-law shifts, and export dictionaries.")
        box.pack_start(lbl, False, False, 0)
        btn = Gtk.Button(label="🗣️ Generate Syllable Lexicon")
        btn.get_style_context().add_class("suggested-action")
        scrolled, out_buf = self._create_dialog_output_view()
        box.pack_start(btn, False, False, 0)
        box.pack_start(scrolled, True, True, 0)

        def _do_gen():
            cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "conlang.py"), "gen", "High-Elvish", "--count", "30"]
            self._run_dialog_cmd(cmd, out_buf, "Generating conlang words...")

        btn.connect("clicked", lambda b: _do_gen())
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def open_pacing_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "pacing.py"), target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Analyzing Prose Pacing & Dialogue Density...")

    def open_journey_calendar_dialog(self):
        target_w = self.current_world_path or str(WORLDS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "calendar.py"), "calc", target_w, "--day", "142"]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Computing Planetary Calendar & Moon Syzygy...")

    def open_factions_logistics_dialog(self):
        target_w = self.current_world_path or str(WORLDS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "factions.py"), "matrix", target_w]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Evaluating Geopolitical Alliances & War Logistics...")

    def open_economy_tech_dialog(self):
        target_w = self.current_world_path or str(WORLDS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "economy.py"), "matrix", target_w]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Calculating Macroeconomic PPP Matrix...")

    def open_causality_dialog(self):
        target_w = self.current_world_path or str(WORLDS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "causality.py"), "report", target_w]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Validating Causal DAGs & Paradoxes...")

    def open_climate_ecology_dialog(self):
        target_w = self.current_world_path or str(WORLDS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "ecology.py"), "web", target_w]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Modeling Planetary Climate & Food-Web Pyramids...")

    def open_idioms_senses_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "senses.py"), target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Analyzing 6D Sensory Grounding Palette...")

    def open_cipher_prophecy_dialog(self):
        dialog, box = self._create_dialog_shell("In-World Ciphers & Phonetic Runes", 720, 480)
        grid = Gtk.Grid()
        grid.set_column_spacing(8)
        grid.set_row_spacing(6)
        grid.attach(Gtk.Label(label="Plaintext:", xalign=0), 0, 0, 1, 1)
        entry_text = Gtk.Entry()
        entry_text.set_text("The secret of the silver spire lies within.")
        grid.attach(entry_text, 1, 0, 1, 1)
        box.pack_start(grid, False, False, 0)

        btn_enc = Gtk.Button(label="🔐 Encode Vigenere / Runes")
        btn_enc.get_style_context().add_class("suggested-action")
        scrolled, out_buf = self._create_dialog_output_view()
        box.pack_start(btn_enc, False, False, 0)
        box.pack_start(scrolled, True, True, 0)

        def _do_enc():
            txt = entry_text.get_text().strip() or "Secret"
            cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "cipher.py"), "encode", "vigenere", txt, "--key", "ARCANUM"]
            self._run_dialog_cmd(cmd, out_buf, "Encoding cipher...")

        btn_enc.connect("clicked", lambda b: _do_enc())
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    # -------------------------------------------------------------------------
    # Craft, Editorial, Publishing & Operations Dialogs
    # -------------------------------------------------------------------------
    def open_stylistics_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "stylistics.py"), "scan", target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Running Stylistics & Dialogue Mechanics audit...")

    def open_voice_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "voice.py"), target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Profiling character voice fingerprints...")

    def open_typography_dialog(self):
        dialog, box = self._create_dialog_shell("Smart Typography Normalizer", 720, 450)
        lbl = Gtk.Label(label="Normalizes curly typographic quotes (“ ” ‘ ’), em-dashes (—), en-dashes (–), and ellipses (…).")
        box.pack_start(lbl, False, False, 0)
        btn = Gtk.Button(label="✨ Polish Manuscript Typography (In-Place)")
        btn.get_style_context().add_class("suggested-action")
        scrolled, out_buf = self._create_dialog_output_view()
        box.pack_start(btn, False, False, 0)
        box.pack_start(scrolled, True, True, 0)

        def _do_polish():
            target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
            cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "typography_cleaner.py"), target, "-i"]
            self._run_dialog_cmd(cmd, out_buf, "Polishing typography...")

        btn.connect("clicked", lambda b: _do_polish())
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def open_scene_mechanics_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "scene_mechanics.py"), target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Analyzing Scene Mechanics & MRU flow...")

    def open_plot_matrix_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "plot_matrix.py"), target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Generating Multi-Track Plot Grid...")

    def open_structure_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "structure.py"), target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Evaluating Story Paradigm Structure...")

    def open_ambient_dialog(self):
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "ambient.py"), "generate", "rainy_library"]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Launching Focus Soundscape Studio...")

    def open_preflight_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "preflight.py"), target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Running Pre-Flight Publishing Linter...")

    def open_barcode_dialog(self):
        dialog, box = self._create_dialog_shell("ISBN-13 Barcode Generator", 680, 420)
        grid = Gtk.Grid()
        grid.set_column_spacing(8)
        grid.set_row_spacing(6)
        grid.attach(Gtk.Label(label="ISBN Number:", xalign=0), 0, 0, 1, 1)
        entry_isbn = Gtk.Entry()
        entry_isbn.set_text("978-0-345-39180-3")
        grid.attach(entry_isbn, 1, 0, 1, 1)
        box.pack_start(grid, False, False, 0)

        btn_gen = Gtk.Button(label="🏷️ Generate Vector SVG Barcode")
        btn_gen.get_style_context().add_class("suggested-action")
        scrolled, out_buf = self._create_dialog_output_view()
        box.pack_start(btn_gen, False, False, 0)
        box.pack_start(scrolled, True, True, 0)

        def _do_gen():
            isbn = entry_isbn.get_text().strip() or "978-0-345-39180-3"
            cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "barcode.py"), isbn]
            self._run_dialog_cmd(cmd, out_buf, "Generating barcode...")

        btn_gen.connect("clicked", lambda b: _do_gen())
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def open_frontmatter_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        dialog, box = self._create_dialog_shell("Modular Front & Back Matter Builder", 720, 460)
        lbl = Gtk.Label(label=f"Scaffold standard publishing front/back matter into {Path(target).name}.")
        box.pack_start(lbl, False, False, 0)
        btn = Gtk.Button(label="📚 Scaffold Front & Back Matter")
        btn.get_style_context().add_class("suggested-action")
        scrolled, out_buf = self._create_dialog_output_view()
        box.pack_start(btn, False, False, 0)
        box.pack_start(scrolled, True, True, 0)

        def _do_build():
            cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "frontmatter_builder.py"), "build", target]
            self._run_dialog_cmd(cmd, out_buf, "Building front & back matter...")

        btn.connect("clicked", lambda b: _do_build())
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def open_query_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        dialog, box = self._create_dialog_shell("Query Letter & Submission Package Scaffolder", 720, 460)
        lbl = Gtk.Label(label=f"Scaffold 1-page query letter, synopsis, and agent tracker into {Path(target).name}/Submissions/.")
        box.pack_start(lbl, False, False, 0)
        btn = Gtk.Button(label="📝 Scaffold Submission Package")
        btn.get_style_context().add_class("suggested-action")
        scrolled, out_buf = self._create_dialog_output_view()
        box.pack_start(btn, False, False, 0)
        box.pack_start(scrolled, True, True, 0)

        def _do_query():
            cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "init_query.py"), target]
            self._run_dialog_cmd(cmd, out_buf, "Scaffolding query package...")

        btn.connect("clicked", lambda b: _do_query())
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def open_cartography_dialog(self):
        target = self.current_world_path or str(WORLDS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "cartography.py"), target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Launching Interactive Vector Cartography Viewer...")

    def open_codex_dialog(self):
        target = self.current_world_path or str(WORLDS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "codex_export.py"), target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Compiling Static World Wiki Codex...")

    def open_series_continuity_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "series_continuity.py"), target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Checking Series Cross-Book Continuity...")

    def open_tactical_sim_dialog(self):
        dialog, box = self._create_dialog_shell("Dynamic Tactical Combat Simulator", 800, 560)
        grid = Gtk.Grid()
        grid.set_column_spacing(8)
        grid.set_row_spacing(6)
        grid.attach(Gtk.Label(label="Terrain:", xalign=0), 0, 0, 1, 1)
        combo_t = Gtk.ComboBoxText()
        combo_t.append("open_field", "Open Field")
        combo_t.append("castle_walls", "Castle Walls")
        combo_t.append("dense_forest", "Dense Forest")
        combo_t.append("dungeon_corridor", "Dungeon Corridor")
        combo_t.set_active_id("open_field")
        grid.attach(combo_t, 1, 0, 1, 1)
        box.pack_start(grid, False, False, 0)

        btn_sim = Gtk.Button(label="⚔️ Run Tactical Skirmish (Narrative Log)")
        btn_sim.get_style_context().add_class("suggested-action")
        scrolled, out_buf = self._create_dialog_output_view()
        box.pack_start(btn_sim, False, False, 0)
        box.pack_start(scrolled, True, True, 0)

        def _do_sim():
            t_id = combo_t.get_active_id() or "open_field"
            cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "tactical_sim.py"), "sim", "--terrain", t_id, "--narrative"]
            self._run_dialog_cmd(cmd, out_buf, "Simulating combat...")

        btn_sim.connect("clicked", lambda b: _do_sim())
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def open_package_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        dialog, box = self._create_dialog_shell("Multi-Platform Distribution Packager", 720, 480)
        lbl = Gtk.Label(label=f"Bundle {Path(target).name} into Reader Edition, Submission Package, and ARC.")
        box.pack_start(lbl, False, False, 0)
        btn = Gtk.Button(label="📦 Package All Release Archives")
        btn.get_style_context().add_class("suggested-action")
        scrolled, out_buf = self._create_dialog_output_view()
        box.pack_start(btn, False, False, 0)
        box.pack_start(scrolled, True, True, 0)

        def _do_pkg():
            cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "package_distribution.py"), target, "-t", "all"]
            self._run_dialog_cmd(cmd, out_buf, "Packaging release archives...")

        btn.connect("clicked", lambda b: _do_pkg())
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def open_portfolio_dialog(self):
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "portfolio.py")]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Generating Portfolio Hub...")

    def open_tts_dialog(self):
        target = self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        base_cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "tts_reader.py"), target]
        self._run_dialog_html_cmd(base_cmd, is_svg=False, status_msg="Launching Audio Proofreader...")
