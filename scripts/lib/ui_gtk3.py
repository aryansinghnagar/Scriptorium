#!/usr/bin/env python3
"""
Ars Arcanum Desktop Application
================================
A native GTK 3 desktop application for authors, worldbuilders, and novelists.
Provides a unified, beginner-friendly interface for managing Universes,
World Lore Vaults (Obsidian), Manuscripts (novelWriter & Markdown),
Typst/Pandoc publishing, Git versioning, and standalone disaster recovery backups.
"""

import sys
import os
import subprocess
import shutil
import threading
import re
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("arcanum.ui_gtk3")

try:
    from lib.config import (
        get_backup_dest, set_backup_dest, clear_backup_dest,
        get_docx_config, set_docx_preset, set_docx_option,
        get_active_docx_preset_name, list_docx_presets
    )
    from lib.docx_sync import open_in_word_processor, sync_manuscript_docx, build_manuscript_docx
except Exception:
    try:
        from config import (
            get_backup_dest, set_backup_dest, clear_backup_dest,
            get_docx_config, set_docx_preset, set_docx_option,
            get_active_docx_preset_name, list_docx_presets
        )
        from docx_sync import open_in_word_processor, sync_manuscript_docx, build_manuscript_docx
    except Exception:
        def get_backup_dest(): return ""
        def set_backup_dest(p): return True
        def clear_backup_dest(): return True
        def get_docx_config(): return {}
        def set_docx_preset(p): return True
        def set_docx_option(k, v): return True
        def get_active_docx_preset_name(): return "standard-submission"
        def list_docx_presets(): return {}
        def open_in_word_processor(p): return True
        def sync_manuscript_docx(p, d=None): return {}
        def build_manuscript_docx(p, d=None): return {}

# Check GTK 3 availability
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk, GLib
    HAS_GTK = True
except (ImportError, ValueError):
    HAS_GTK = False
    class _DummyGtk:
        class Window:
            pass
    Gtk = _DummyGtk()

HOME_DIR = Path.home()
UNIVERSES_DIR = HOME_DIR / "Universes"
MANUSCRIPTS_DIR = HOME_DIR / "Manuscripts"
WORLDS_DIR = HOME_DIR / "Worlds"
LIB_DIR = Path(__file__).resolve().parent
SCRIPT_DIR = LIB_DIR.parent
PROJECT_ROOT = SCRIPT_DIR.parent

class ArcanumApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Ars Arcanum — Author & Worldbuilder Studio")
        self.set_default_size(1060, 720)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Apply basic modern styling
        self.setup_styles()

        self.current_universe = None
        self.current_world_path = None
        self.current_manuscript_path = None
        self.current_selected_scene_file = None

        self.discovered_universes = []
        self.discovered_worlds = []
        self.discovered_manuscripts = []

        self.combo_draft_vol = None
        self.combo_draft_list = None
        self.combo_diff_a = None
        self.combo_diff_b = None
        self.lbl_secure_dest = None

        # Main vertical container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # Header Bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Ars Arcanum"
        header.props.subtitle = "Sovereign Writing & Worldbuilding Studio"
        self.set_titlebar(header)

        # Quick Snapshot button in HeaderBar
        snap_btn = Gtk.Button(label="📷 Quick Snapshot")
        snap_btn.get_style_context().add_class("suggested-action")
        snap_btn.set_tooltip_text("Record a 1-click Git version milestone")
        snap_btn.connect("clicked", self.on_quick_snapshot_clicked)
        header.pack_end(snap_btn)

        # Manual / Help button
        help_btn = Gtk.Button(label="📖 Field Manual")
        help_btn.set_tooltip_text("Open the Ars Arcanum Author's Field Manual")
        help_btn.connect("clicked", self.on_open_manual_clicked)
        header.pack_end(help_btn)

        # Top Project Selector Bar
        selector_bar = self.create_selector_bar()
        main_box.pack_start(selector_bar, False, False, 0)

        # 5-Tab Notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        main_box.pack_start(self.notebook, True, True, 0)

        # Create the 5 tabs
        self.tab_cosmos = self.create_cosmos_tab()
        self.tab_manuscript = self.create_manuscript_tab()
        self.tab_publishing = self.create_publishing_tab()
        self.tab_safety = self.create_safety_tab()
        self.tab_doctor = self.create_doctor_tab()

        self.notebook.append_page(self.tab_cosmos, Gtk.Label(label="🪐 Universes & Worlds"))
        self.notebook.append_page(self.tab_manuscript, Gtk.Label(label="✍️ Manuscripts & Drafting"))
        self.notebook.append_page(self.tab_publishing, Gtk.Label(label="📚 Publishing & Exports"))
        self.notebook.append_page(self.tab_safety, Gtk.Label(label="🔒 Snapshots & Backups"))
        self.notebook.append_page(self.tab_doctor, Gtk.Label(label="🩺 Diagnostics & Doctor"))

        # Bottom Status Bar
        self.statusbar = Gtk.Statusbar()
        self.status_context = self.statusbar.get_context_id("main")
        main_box.pack_start(self.statusbar, False, False, 0)

        self.refresh_all_discovery()
        self.check_first_run()

    def setup_styles(self):
        css_provider = Gtk.CssProvider()
        css = b"""
        .title-label { font-size: 15px; font-weight: bold; }
        .section-header { font-size: 13px; font-weight: bold; color: #4a90d9; }
        .card-box { background: alpha(@theme_bg_color, 0.5); border: 1px solid alpha(@theme_fg_color, 0.15); border-radius: 6px; padding: 10px; margin: 4px; }
        .stat-value { font-size: 19px; font-weight: bold; color: #2e7d32; }
        .inspector-box { background: alpha(@theme_bg_color, 0.7); border: 1px solid alpha(#4a90d9, 0.3); border-radius: 6px; padding: 10px; }
        .danger-btn { background: #d32f2f; color: white; }
        """
        try:
            css_provider.load_from_data(css)
            screen = Gdk.Screen.get_default()
            if screen:
                Gtk.StyleContext.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        except Exception as e:
            logger.debug("Could not apply GTK CSS styling: %s", e)

    def set_status(self, message):
        self.statusbar.pop(self.status_context)
        self.statusbar.push(self.status_context, message)

    def create_selector_bar(self):
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bar.set_border_width(8)
        bar.get_style_context().add_class("card-box")

        # 1. Universe Selector
        lbl_uni = Gtk.Label(label="<b>Universe:</b>", use_markup=True)
        bar.pack_start(lbl_uni, False, False, 0)

        self.combo_universe = Gtk.ComboBoxText()
        self.combo_universe.connect("changed", self.on_universe_changed)
        bar.pack_start(self.combo_universe, False, False, 0)

        btn_new_uni = Gtk.Button(label="+ Universe")
        btn_new_uni.connect("clicked", self.on_new_universe_clicked)
        bar.pack_start(btn_new_uni, False, False, 0)

        bar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 4)

        # 2. World Lore Vault Selector
        lbl_world = Gtk.Label(label="<b>World Lore:</b>", use_markup=True)
        bar.pack_start(lbl_world, False, False, 0)

        self.combo_world = Gtk.ComboBoxText()
        self.combo_world.connect("changed", self.on_world_changed)
        bar.pack_start(self.combo_world, True, True, 0)

        btn_new_world = Gtk.Button(label="+ World")
        btn_new_world.connect("clicked", self.on_new_world_clicked)
        bar.pack_start(btn_new_world, False, False, 0)

        bar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 4)

        # 3. Manuscript Project Selector
        lbl_ms = Gtk.Label(label="<b>Manuscript:</b>", use_markup=True)
        bar.pack_start(lbl_ms, False, False, 0)

        self.combo_manuscript = Gtk.ComboBoxText()
        self.combo_manuscript.connect("changed", self.on_manuscript_changed)
        bar.pack_start(self.combo_manuscript, True, True, 0)

        btn_new_ms = Gtk.Button(label="+ Manuscript")
        btn_new_ms.get_style_context().add_class("suggested-action")
        btn_new_ms.connect("clicked", self.on_new_manuscript_clicked)
        bar.pack_start(btn_new_ms, False, False, 0)

        btn_refresh = Gtk.Button(label="🔄")
        btn_refresh.set_tooltip_text("Refresh discovered universes, worlds, and manuscripts")
        btn_refresh.connect("clicked", lambda b: self.refresh_all_discovery())
        bar.pack_start(btn_refresh, False, False, 0)

        return bar

    # -------------------------------------------------------------------------
    # TAB 1: Universes & Worlds (Worldbuilding Lore)
    # -------------------------------------------------------------------------
    def create_cosmos_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_border_width(16)
        scrolled.add(box)

        # Overview Header
        self.lbl_cosmos_heading = Gtk.Label()
        self.lbl_cosmos_heading.set_markup("<span size='large' weight='bold'>World Lore Overview</span>")
        self.lbl_cosmos_heading.set_xalign(0)
        box.pack_start(self.lbl_cosmos_heading, False, False, 0)

        self.lbl_cosmos_path = Gtk.Label(label="No world selected")
        self.lbl_cosmos_path.set_xalign(0)
        self.lbl_cosmos_path.set_selectable(True)
        box.pack_start(self.lbl_cosmos_path, False, False, 0)

        # Tool Launchers Grid
        grid_frame = Gtk.Frame(label=" Worldbuilding & Lore Launchers ")
        grid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        grid_box.set_border_width(12)
        grid_frame.add(grid_box)

        launchers_grid = Gtk.Grid()
        launchers_grid.set_column_spacing(12)
        launchers_grid.set_row_spacing(12)
        launchers_grid.set_row_homogeneous(True)
        launchers_grid.set_column_homogeneous(True)

        btn_obsidian = Gtk.Button(label="📖  Open World Bible\n(Obsidian Lore Vault)")
        btn_obsidian.connect("clicked", self.on_launch_obsidian)
        launchers_grid.attach(btn_obsidian, 0, 0, 1, 1)

        btn_files = Gtk.Button(label="📁  Browse World Vault\n(File Manager)")
        btn_files.connect("clicked", self.on_open_world_folder_clicked)
        launchers_grid.attach(btn_files, 1, 0, 1, 1)

        btn_concordance = Gtk.Button(label="📖  Generate Concordance\n(Dramatis Personae & Glossary)")
        btn_concordance.connect("clicked", self.on_generate_concordance_clicked)
        launchers_grid.attach(btn_concordance, 2, 0, 1, 1)

        grid_box.pack_start(launchers_grid, True, True, 0)
        box.pack_start(grid_frame, False, False, 0)

        # Lore Taxonomy Summary
        self.lore_summary_frame = Gtk.Frame(label=" World Lore Taxonomy Register ")
        self.lore_summary_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.lore_summary_box.set_border_width(12)
        self.lbl_lore_stats = Gtk.Label(label="Select a world lore vault to view registered entities.")
        self.lbl_lore_stats.set_xalign(0)
        self.lore_summary_box.pack_start(self.lbl_lore_stats, False, False, 0)
        self.lore_summary_frame.add(self.lore_summary_box)
        box.pack_start(self.lore_summary_frame, False, False, 0)

        # Jumpstart & Sample Cosmos Banner
        demo_frame = Gtk.Frame(label=" Jumpstart & Exploration ")
        demo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        demo_box.set_border_width(12)
        demo_frame.add(demo_box)

        lbl_demo = Gtk.Label()
        lbl_demo.set_markup("<b>New to Ars Arcanum?</b> Generate a sample cosmos (<i>The Chronicles of Eldoria</i>) with lore dossiers, bestiary creatures, magic disciplines, and starter chapters.")
        lbl_demo.set_line_wrap(True)
        demo_box.pack_start(lbl_demo, True, True, 0)

        btn_gen_demo = Gtk.Button(label="✨ Generate Demo Cosmos")
        btn_gen_demo.connect("clicked", self.on_generate_demo_clicked)
        demo_box.pack_start(btn_gen_demo, False, False, 0)

        box.pack_start(demo_frame, False, False, 0)

        return scrolled

    # -------------------------------------------------------------------------
    # TAB 2: Manuscripts & Drafting (with Visual Scene Metadata Inspector)
    # -------------------------------------------------------------------------
    def create_manuscript_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_border_width(14)
        scrolled.add(box)

        # Stats Cards Box
        stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        stats_box.set_homogeneous(True)

        self.card_total_words = self.create_stat_card("Total Words", "0", "Across all manuscript volumes")
        self.card_chapters = self.create_stat_card("Chapters / Scenes", "0", "Drafting files in project")
        self.card_pace = self.create_stat_card("Target Pace", "1,000 w/day", "Daily writing goal")

        stats_box.pack_start(self.card_total_words, True, True, 0)
        stats_box.pack_start(self.card_chapters, True, True, 0)
        stats_box.pack_start(self.card_pace, True, True, 0)
        box.pack_start(stats_box, False, False, 0)

        # Paned view: Left = Manuscript Hierarchy Tree, Right = Visual Scene Metadata Inspector
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_position(460)

        # Left: Tree Frame
        tree_frame = Gtk.Frame(label=" Manuscript Structure & Volumes ")
        tree_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        tree_vbox.set_border_width(8)
        tree_frame.add(tree_vbox)

        self.manuscript_store = Gtk.TreeStore(str, str, str, str) # Item, Type, Wordcount, FilePath
        self.manuscript_tree = Gtk.TreeView(model=self.manuscript_store)
        self.manuscript_tree.get_selection().connect("changed", self.on_manuscript_tree_selection_changed)

        col_item = Gtk.TreeViewColumn("Document / Section", Gtk.CellRendererText(), text=0)
        col_item.set_expand(True)
        self.manuscript_tree.append_column(col_item)

        col_type = Gtk.TreeViewColumn("Type", Gtk.CellRendererText(), text=1)
        col_type.set_min_width(85)
        self.manuscript_tree.append_column(col_type)

        col_wc = Gtk.TreeViewColumn("Words", Gtk.CellRendererText(), text=2)
        col_wc.set_min_width(80)
        self.manuscript_tree.append_column(col_wc)

        tree_scroll = Gtk.ScrolledWindow()
        tree_scroll.set_min_content_height(260)
        tree_scroll.add(self.manuscript_tree)
        tree_vbox.pack_start(tree_scroll, True, True, 0)

        ms_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_refresh_stats = Gtk.Button(label="🔄 Recalc")
        btn_refresh_stats.connect("clicked", lambda b: self.refresh_manuscript_analytics())
        ms_btns.pack_start(btn_refresh_stats, False, False, 0)

        btn_add_vol = Gtk.Button(label="+ Volume")
        btn_add_vol.get_style_context().add_class("suggested-action")
        btn_add_vol.connect("clicked", self.on_add_volume_clicked)
        ms_btns.pack_start(btn_add_vol, False, False, 0)

        btn_nw = Gtk.Button(label="✍️ novelWriter")
        btn_nw.connect("clicked", self.on_launch_novelwriter)
        ms_btns.pack_start(btn_nw, False, False, 0)

        btn_fw = Gtk.Button(label="⚡ FocusWriter")
        btn_fw.connect("clicked", self.on_launch_focuswriter)
        ms_btns.pack_start(btn_fw, False, False, 0)

        tree_vbox.pack_start(ms_btns, False, False, 0)
        paned.pack1(tree_frame, True, False)

        # Right: Visual Scene Metadata Inspector
        inspector_frame = Gtk.Frame(label=" Visual Scene Metadata Inspector ")
        inspector_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        inspector_box.set_border_width(10)
        inspector_frame.add(inspector_box)

        self.lbl_inspector_file = Gtk.Label(label="<i>Select a scene note from the tree to inspect tags</i>", use_markup=True)
        self.lbl_inspector_file.set_xalign(0)
        self.lbl_inspector_file.set_line_wrap(True)
        inspector_box.pack_start(self.lbl_inspector_file, False, False, 0)

        form_grid = Gtk.Grid()
        form_grid.set_column_spacing(8)
        form_grid.set_row_spacing(6)

        # @pov:
        form_grid.attach(Gtk.Label(label="POV (@pov):", xalign=0), 0, 0, 1, 1)
        self.entry_tag_pov = Gtk.Entry()
        self.entry_tag_pov.set_placeholder_text("Protagonist name (e.g. Kaelen)")
        form_grid.attach(self.entry_tag_pov, 1, 0, 1, 1)

        # @char:
        form_grid.attach(Gtk.Label(label="Cast (@char):", xalign=0), 0, 1, 1, 1)
        self.entry_tag_char = Gtk.Entry()
        self.entry_tag_char.set_placeholder_text("Characters in scene (e.g. Vance, Renée)")
        form_grid.attach(self.entry_tag_char, 1, 1, 1, 1)

        # @location:
        form_grid.attach(Gtk.Label(label="Location (@location):", xalign=0), 0, 2, 1, 1)
        self.entry_tag_location = Gtk.Entry()
        self.entry_tag_location.set_placeholder_text("Setting (e.g. Capital City, Archives)")
        form_grid.attach(self.entry_tag_location, 1, 2, 1, 1)

        # @thread:
        form_grid.attach(Gtk.Label(label="Subplot (@thread):", xalign=0), 0, 3, 1, 1)
        self.entry_tag_thread = Gtk.Entry()
        self.entry_tag_thread.set_placeholder_text("Narrative thread (e.g. Arcane Heist, Romance)")
        form_grid.attach(self.entry_tag_thread, 1, 3, 1, 1)

        # @time:
        form_grid.attach(Gtk.Label(label="Timeline (@time):", xalign=0), 0, 4, 1, 1)
        self.entry_tag_time = Gtk.Entry()
        self.entry_tag_time.set_placeholder_text("Chronology marker (e.g. 1422 3E, Night)")
        form_grid.attach(self.entry_tag_time, 1, 4, 1, 1)

        # @status:
        form_grid.attach(Gtk.Label(label="Status (@status):", xalign=0), 0, 5, 1, 1)
        self.combo_tag_status = Gtk.ComboBoxText()
        self.combo_tag_status.append("Draft", "Draft (In Progress)")
        self.combo_tag_status.append("Revision", "Revision (Self-Edit)")
        self.combo_tag_status.append("First Polish", "First Polish (Beta Ready)")
        self.combo_tag_status.append("Final", "Final (Proofread)")
        self.combo_tag_status.set_active_id("Draft")
        form_grid.attach(self.combo_tag_status, 1, 5, 1, 1)

        inspector_box.pack_start(form_grid, False, False, 0)

        # Inspector Action Buttons
        insp_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.btn_save_scene_tags = Gtk.Button(label="💾 Update Scene Header")
        self.btn_save_scene_tags.get_style_context().add_class("suggested-action")
        self.btn_save_scene_tags.connect("clicked", self.on_save_scene_tags_clicked)
        self.btn_save_scene_tags.set_sensitive(False)
        insp_btns.pack_start(self.btn_save_scene_tags, True, True, 0)

        self.btn_read_scene_tags = Gtk.Button(label="🔄 Read Tags")
        self.btn_read_scene_tags.connect("clicked", self.on_read_scene_tags_clicked)
        self.btn_read_scene_tags.set_sensitive(False)
        insp_btns.pack_start(self.btn_read_scene_tags, False, False, 0)

        inspector_box.pack_start(insp_btns, False, False, 0)

        paned.pack2(inspector_frame, True, False)
        box.pack_start(paned, True, True, 0)

        # Drafts & Revision Redline Comparator
        revisions_frame = Gtk.Frame(label=" Manuscript Draft Revisions & Redline Comparator ")
        rev_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        rev_vbox.set_border_width(10)
        revisions_frame.add(rev_vbox)

        # Row 1: Draft Management & Forking
        draft_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        draft_row.pack_start(Gtk.Label(label="<b>Volume:</b>", use_markup=True), False, False, 0)
        self.combo_draft_vol = Gtk.ComboBoxText()
        self.combo_draft_vol.connect("changed", lambda c: self.refresh_draft_selectors())
        draft_row.pack_start(self.combo_draft_vol, False, False, 0)

        draft_row.pack_start(Gtk.Label(label="<b>Drafts:</b>", use_markup=True), False, False, 4)
        self.combo_draft_list = Gtk.ComboBoxText()
        draft_row.pack_start(self.combo_draft_list, False, False, 0)

        btn_fork_draft = Gtk.Button(label="+ Fork New Draft")
        btn_fork_draft.get_style_context().add_class("suggested-action")
        btn_fork_draft.connect("clicked", self.on_fork_draft_clicked)
        draft_row.pack_start(btn_fork_draft, False, False, 0)

        rev_vbox.pack_start(draft_row, False, False, 0)

        # Row 2: Diff Comparison
        diff_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        diff_row.pack_start(Gtk.Label(label="<b>Compare:</b>", use_markup=True), False, False, 0)
        self.combo_diff_b = Gtk.ComboBoxText()  # Target / Newer
        diff_row.pack_start(self.combo_diff_b, False, False, 0)

        diff_row.pack_start(Gtk.Label(label="<i>against prior</i>", use_markup=True), False, False, 0)
        self.combo_diff_a = Gtk.ComboBoxText()  # Base / Older
        diff_row.pack_start(self.combo_diff_a, False, False, 0)

        btn_view_redline = Gtk.Button(label="📊 View Redline Changelog (Browser)")
        btn_view_redline.get_style_context().add_class("suggested-action")
        btn_view_redline.connect("clicked", self.on_view_redline_clicked)
        diff_row.pack_start(btn_view_redline, False, False, 0)

        btn_lo_diff = Gtk.Button(label="📝 LibreOffice Writer")
        btn_lo_diff.connect("clicked", self.on_lo_compare_clicked)
        diff_row.pack_start(btn_lo_diff, False, False, 0)

        rev_vbox.pack_start(diff_row, False, False, 0)

        # Row 3: Word Processor & DOCX Synchronization
        docx_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        docx_row.pack_start(Gtk.Label(label="<b>Word Processing:</b>", use_markup=True), False, False, 0)

        btn_open_word = Gtk.Button(label="📝 Open in Word Processor")
        btn_open_word.get_style_context().add_class("suggested-action")
        btn_open_word.set_tooltip_text("Open active draft .docx in Microsoft Word, Google Docs, or LibreOffice")
        btn_open_word.connect("clicked", self.on_open_word_processor_clicked)
        docx_row.pack_start(btn_open_word, False, False, 0)

        btn_sync_docx = Gtk.Button(label="🔄 Sync DOCX ↔ Markdown")
        btn_sync_docx.set_tooltip_text("Perform bidirectional synchronization between .docx files and Markdown scenes")
        btn_sync_docx.connect("clicked", self.on_sync_docx_clicked)
        docx_row.pack_start(btn_sync_docx, False, False, 0)

        btn_docx_settings = Gtk.Button(label="⚙️ DOCX Formatting...")
        btn_docx_settings.set_tooltip_text("Customize manuscript typography, line spacing, margins, and submission presets")
        btn_docx_settings.connect("clicked", self.on_docx_settings_clicked)
        docx_row.pack_start(btn_docx_settings, False, False, 0)

        rev_vbox.pack_start(docx_row, False, False, 0)
        box.pack_start(revisions_frame, False, False, 0)

        return scrolled

    def create_stat_card(self, title, default_val, subtitle):
        frame = Gtk.Frame()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_border_width(10)
        frame.add(box)

        lbl_t = Gtk.Label(label=title)
        lbl_t.get_style_context().add_class("section-header")
        lbl_t.set_xalign(0)
        box.pack_start(lbl_t, False, False, 0)

        lbl_v = Gtk.Label(label=default_val)
        lbl_v.get_style_context().add_class("stat-value")
        lbl_v.set_xalign(0)
        box.pack_start(lbl_v, False, False, 0)

        lbl_s = Gtk.Label(label=subtitle)
        lbl_s.set_xalign(0)
        box.pack_start(lbl_s, False, False, 0)

        frame.val_label = lbl_v
        return frame

    # -------------------------------------------------------------------------
    # TAB 3: Publishing Studio
    # -------------------------------------------------------------------------
    def create_publishing_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_border_width(16)
        scrolled.add(box)

        # Meta Form
        meta_frame = Gtk.Frame(label=" Book Metadata & Output Configuration ")
        form_grid = Gtk.Grid()
        form_grid.set_border_width(12)
        form_grid.set_column_spacing(12)
        form_grid.set_row_spacing(8)
        meta_frame.add(form_grid)

        form_grid.attach(Gtk.Label(label="Book Title:", xalign=0), 0, 0, 1, 1)
        self.entry_pub_title = Gtk.Entry()
        form_grid.attach(self.entry_pub_title, 1, 0, 2, 1)

        form_grid.attach(Gtk.Label(label="Author Name:", xalign=0), 0, 1, 1, 1)
        self.entry_pub_author = Gtk.Entry()
        self.entry_pub_author.set_text("Author Name")
        form_grid.attach(self.entry_pub_author, 1, 1, 2, 1)

        form_grid.attach(Gtk.Label(label="Volume Selection:", xalign=0), 0, 2, 1, 1)
        self.combo_pub_volume = Gtk.ComboBoxText()
        form_grid.attach(self.combo_pub_volume, 1, 2, 2, 1)

        form_grid.attach(Gtk.Label(label="Paper Trim Size:", xalign=0), 0, 3, 1, 1)
        self.combo_paper_size = Gtk.ComboBoxText()
        self.combo_paper_size.append("us-trade", "US Trade (6 × 9 in) — Standard Fiction")
        self.combo_paper_size.append("trade", "Trade (5.5 × 8.5 in) — Compact Novel")
        self.combo_paper_size.append("pocket", "Pocket (5 × 8 in) — Mass Market")
        self.combo_paper_size.set_active_id("us-trade")
        form_grid.attach(self.combo_paper_size, 1, 3, 2, 1)

        form_grid.attach(Gtk.Label(label="Export Format:", xalign=0), 0, 4, 1, 1)
        self.combo_pub_format = Gtk.ComboBoxText()
        self.combo_pub_format.append("book", "Print Book (Typst PDF + Pandoc EPUB)")
        self.combo_pub_format.append("submission", "Submission Manuscript (.docx) — Standard Industry Format")
        self.combo_pub_format.append("all", "Complete Package (PDF + EPUB + DOCX)")
        self.combo_pub_format.set_active_id("book")
        form_grid.attach(self.combo_pub_format, 1, 4, 2, 1)

        box.pack_start(meta_frame, False, False, 0)

        # Actions & Output
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.btn_compile = Gtk.Button(label="🚀 Compile Book (PDF / EPUB / DOCX)")
        self.btn_compile.get_style_context().add_class("suggested-action")
        self.btn_compile.connect("clicked", self.on_compile_clicked)
        action_box.pack_start(self.btn_compile, True, True, 0)

        self.btn_open_pdf = Gtk.Button(label="📄 Open PDF")
        self.btn_open_pdf.connect("clicked", self.on_open_pdf_clicked)
        self.btn_open_pdf.set_sensitive(False)
        action_box.pack_start(self.btn_open_pdf, False, False, 0)

        self.btn_open_epub = Gtk.Button(label="📱 Open EPUB")
        self.btn_open_epub.connect("clicked", self.on_open_epub_clicked)
        self.btn_open_epub.set_sensitive(False)
        action_box.pack_start(self.btn_open_epub, False, False, 0)

        self.btn_open_docx = Gtk.Button(label="📝 Open DOCX")
        self.btn_open_docx.connect("clicked", self.on_open_docx_clicked)
        self.btn_open_docx.set_sensitive(False)
        action_box.pack_start(self.btn_open_docx, False, False, 0)

        box.pack_start(action_box, False, False, 0)

        # Compilation Log
        log_frame = Gtk.Frame(label=" Compilation Ledger ")
        log_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        log_box.set_border_width(8)
        log_frame.add(log_box)

        self.pub_log_view = Gtk.TextView()
        self.pub_log_view.set_editable(False)
        self.pub_log_view.set_cursor_visible(False)
        self.pub_log_buffer = self.pub_log_view.get_buffer()

        log_scroll = Gtk.ScrolledWindow()
        log_scroll.set_min_content_height(180)
        log_scroll.add(self.pub_log_view)
        log_box.pack_start(log_scroll, True, True, 0)

        box.pack_start(log_frame, True, True, 0)

        return scrolled

    # -------------------------------------------------------------------------
    # TAB 4: Snapshots & Backups
    # -------------------------------------------------------------------------
    def create_safety_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_border_width(16)
        scrolled.add(box)

        # 1. Version Snapshot (Git) Card
        snap_frame = Gtk.Frame(label=" Version Milestone Snapshot (Git) ")
        snap_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        snap_box.set_border_width(10)
        snap_frame.add(snap_box)

        lbl_snap_info = Gtk.Label(label="Record an immutable version snapshot of your manuscript project and world lore.", xalign=0)
        snap_box.pack_start(lbl_snap_info, False, False, 0)

        snap_input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.entry_snap_note = Gtk.Entry()
        self.entry_snap_note.set_placeholder_text("Milestone note (e.g. 'Completed Chapter 4 draft')")
        snap_input_box.pack_start(self.entry_snap_note, True, True, 0)

        btn_save_snap = Gtk.Button(label="📷 Save Snapshot")
        btn_save_snap.get_style_context().add_class("suggested-action")
        btn_save_snap.connect("clicked", self.on_save_snapshot_clicked)
        snap_input_box.pack_start(btn_save_snap, False, False, 0)
        snap_box.pack_start(snap_input_box, False, False, 0)

        box.pack_start(snap_frame, False, False, 0)

        # 2. Standalone Archive Backup Card
        backup_frame = Gtk.Frame(label=" Standalone Disaster Recovery Archive (3-2-1 Backups) ")
        backup_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        backup_box.set_border_width(10)
        backup_frame.add(backup_box)

        lbl_b_info = Gtk.Label(label="Generate a standalone compressed .tar.gz archive with a SHA-256 cryptographic verification digest.", xalign=0)
        backup_box.pack_start(lbl_b_info, False, False, 0)

        backup_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_create_backup = Gtk.Button(label="📦 Create Standalone Backup Archive")
        btn_create_backup.connect("clicked", self.on_create_backup_clicked)
        backup_btns.pack_start(btn_create_backup, True, True, 0)

        btn_restore = Gtk.Button(label="♻️ Restore from Archive...")
        btn_restore.connect("clicked", self.on_restore_clicked)
        backup_btns.pack_start(btn_restore, False, False, 0)

        backup_box.pack_start(backup_btns, False, False, 0)
        box.pack_start(backup_frame, False, False, 0)

        # 3. Dual-Target Secure External / USB Backup Destination
        secure_frame = Gtk.Frame(label=" Dual-Target External & USB Backup Destination ")
        secure_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        secure_box.set_border_width(10)
        secure_frame.add(secure_box)

        lbl_s_info = Gtk.Label(label="Replicate verified backups automatically to an external USB drive, encrypted vault, or secondary disk path.", xalign=0)
        lbl_s_info.set_line_wrap(True)
        secure_box.pack_start(lbl_s_info, False, False, 0)

        self.lbl_secure_dest = Gtk.Label(label="<b>Secure Destination:</b> <i>None (Local 05-Backups/ only)</i>", use_markup=True)
        self.lbl_secure_dest.set_xalign(0)
        self.lbl_secure_dest.set_selectable(True)
        secure_box.pack_start(self.lbl_secure_dest, False, False, 0)

        sec_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_set_dest = Gtk.Button(label="📁 Choose External / USB Backup Directory...")
        btn_set_dest.connect("clicked", self.on_select_secure_dest_clicked)
        sec_btns.pack_start(btn_set_dest, True, True, 0)

        btn_clear_dest = Gtk.Button(label="✖ Clear Destination")
        btn_clear_dest.connect("clicked", self.on_clear_secure_dest_clicked)
        sec_btns.pack_start(btn_clear_dest, False, False, 0)

        secure_box.pack_start(sec_btns, False, False, 0)
        box.pack_start(secure_frame, False, False, 0)

        # 3. Snapshot History Log
        history_frame = Gtk.Frame(label=" Recent Milestone History ")
        hist_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        hist_box.set_border_width(8)
        history_frame.add(hist_box)

        self.history_store = Gtk.ListStore(str, str, str) # Hash, Date, Note
        self.history_tree = Gtk.TreeView(model=self.history_store)

        self.history_tree.append_column(Gtk.TreeViewColumn("Commit", Gtk.CellRendererText(), text=0))
        self.history_tree.append_column(Gtk.TreeViewColumn("Date & Time", Gtk.CellRendererText(), text=1))
        col_note = Gtk.TreeViewColumn("Snapshot Note", Gtk.CellRendererText(), text=2)
        col_note.set_expand(True)
        self.history_tree.append_column(col_note)

        hist_scroll = Gtk.ScrolledWindow()
        hist_scroll.set_min_content_height(160)
        hist_scroll.add(self.history_tree)
        hist_box.pack_start(hist_scroll, True, True, 0)

        box.pack_start(history_frame, True, True, 0)

        return scrolled

    # -------------------------------------------------------------------------
    # TAB 5: Diagnostics & Doctor
    # -------------------------------------------------------------------------
    def create_doctor_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_border_width(16)
        scrolled.add(box)

        # Toolchain Badges Box
        badges_frame = Gtk.Frame(label=" System & Toolchain Status ")
        badges_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        badges_box.set_border_width(10)
        badges_box.set_homogeneous(True)
        badges_frame.add(badges_box)

        self.lbl_tool_git = self.create_badge_item("Git VCS", "Checking...")
        self.lbl_tool_pandoc = self.create_badge_item("Pandoc Bridge", "Checking...")
        self.lbl_tool_typst = self.create_badge_item("Typst Typesetting", "Checking...")
        self.lbl_tool_python = self.create_badge_item("Python 3 Core", "Checking...")

        badges_box.pack_start(self.lbl_tool_git, True, True, 0)
        badges_box.pack_start(self.lbl_tool_pandoc, True, True, 0)
        badges_box.pack_start(self.lbl_tool_typst, True, True, 0)
        badges_box.pack_start(self.lbl_tool_python, True, True, 0)
        box.pack_start(badges_frame, False, False, 0)

        # Action bar
        doc_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_run_doc = Gtk.Button(label="🩺 Run Full System & Lore Diagnostics")
        btn_run_doc.get_style_context().add_class("suggested-action")
        btn_run_doc.connect("clicked", lambda b: self.run_diagnostics())
        doc_actions.pack_start(btn_run_doc, True, True, 0)

        btn_verify = Gtk.Button(label="🛡️ Run 7-Stage System Verification")
        btn_verify.connect("clicked", lambda b: self.run_verify_harness())
        doc_actions.pack_start(btn_verify, False, False, 0)

        box.pack_start(doc_actions, False, False, 0)

        # Diagnostics Output View
        report_frame = Gtk.Frame(label=" Diagnostic Findings & Lore Integrity ")
        report_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        report_box.set_border_width(8)
        report_frame.add(report_box)

        self.doc_log_view = Gtk.TextView()
        self.doc_log_view.set_editable(False)
        self.doc_log_view.set_cursor_visible(False)
        self.doc_log_buffer = self.doc_log_view.get_buffer()

        doc_scroll = Gtk.ScrolledWindow()
        doc_scroll.set_min_content_height(240)
        doc_scroll.add(self.doc_log_view)
        report_box.pack_start(doc_scroll, True, True, 0)

        box.pack_start(report_frame, True, True, 0)

        return scrolled

    def create_badge_item(self, name, status):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        lbl_n = Gtk.Label(label=f"<b>{name}</b>", use_markup=True)
        lbl_s = Gtk.Label(label=status)
        box.pack_start(lbl_n, False, False, 0)
        box.pack_start(lbl_s, False, False, 0)
        box.status_label = lbl_s
        return box

    # -------------------------------------------------------------------------
    # Discovery & State Updates
    # -------------------------------------------------------------------------
    def refresh_all_discovery(self):
        self.refresh_universes()
        self.refresh_worlds_for_universe()
        self.refresh_manuscripts()
        self.update_active_world_display()
        self.update_active_manuscript_display()
        self.update_toolchain_badges()

    def refresh_universes(self):
        self.discovered_universes = []
        self.combo_universe.remove_all()

        if UNIVERSES_DIR.is_dir():
            for p in sorted(UNIVERSES_DIR.iterdir()):
                if p.is_dir() and not p.name.startswith("."):
                    self.discovered_universes.append(p.name)
                    self.combo_universe.append(p.name, p.name)

        if not self.discovered_universes:
            self.combo_universe.append("Default-Universe", "Default-Universe")
            self.current_universe = "Default-Universe"
        else:
            if not self.current_universe or self.current_universe not in self.discovered_universes:
                self.current_universe = self.discovered_universes[0]
            self.combo_universe.set_active_id(self.current_universe)

    def refresh_worlds_for_universe(self):
        self.combo_world.remove_all()
        self.discovered_worlds = []

        if self.current_universe:
            u_dir = UNIVERSES_DIR / self.current_universe
            if u_dir.is_dir():
                for w in sorted(u_dir.iterdir()):
                    if w.is_dir() and not w.name.startswith(".") and w.name not in ("Worlds", ".git"):
                        self.discovered_worlds.append((w.name, str(w), f"[{self.current_universe}] {w.name}"))
                # Also check legacy subfolder
                u_worlds = u_dir / "Worlds"
                if u_worlds.is_dir():
                    for w in sorted(u_worlds.iterdir()):
                        if w.is_dir() and not w.name.startswith("."):
                            self.discovered_worlds.append((w.name, str(w), f"[{self.current_universe}] {w.name}"))

        if WORLDS_DIR.is_dir():
            for w in sorted(WORLDS_DIR.iterdir()):
                if w.is_dir() and not w.name.startswith("."):
                    self.discovered_worlds.append((w.name, str(w), f"[Legacy] {w.name}"))

        for wname, wpath, label in self.discovered_worlds:
            self.combo_world.append(wpath, label)

        if self.discovered_worlds:
            self.combo_world.set_active(0)
            self.current_world_path = self.discovered_worlds[0][1]
        else:
            self.current_world_path = None

    def refresh_manuscripts(self):
        self.combo_manuscript.remove_all()
        self.discovered_manuscripts = []

        if MANUSCRIPTS_DIR.is_dir():
            for m in sorted(MANUSCRIPTS_DIR.iterdir()):
                if m.is_dir() and not m.name.startswith("."):
                    self.discovered_manuscripts.append((m.name, str(m), m.name))

        for mname, mpath, label in self.discovered_manuscripts:
            self.combo_manuscript.append(mpath, label)

        if self.discovered_manuscripts:
            self.combo_manuscript.set_active(0)
            self.current_manuscript_path = self.discovered_manuscripts[0][1]
        else:
            self.current_manuscript_path = None

    def on_universe_changed(self, combo):
        active_id = combo.get_active_id()
        if active_id and active_id != self.current_universe:
            self.current_universe = active_id
            self.refresh_worlds_for_universe()
            self.update_active_world_display()

    def on_world_changed(self, combo):
        active_id = combo.get_active_id()
        if active_id:
            self.current_world_path = active_id
            self.update_active_world_display()

    def on_manuscript_changed(self, combo):
        active_id = combo.get_active_id()
        if active_id:
            self.current_manuscript_path = active_id
            self.update_active_manuscript_display()

    def update_active_world_display(self):
        if self.current_world_path and Path(self.current_world_path).is_dir():
            wpath = Path(self.current_world_path)
            wname = wpath.name
            self.lbl_cosmos_heading.set_markup(f"<span size='large' weight='bold'>World Lore Vault: {wname}</span>")
            self.lbl_cosmos_path.set_text(str(wpath))

            # Count registered lore entities
            counts = {}
            for folder in ("Characters", "Locations", "Factions", "Magic-Technology", "Bestiary", "Artifacts", "Cosmology", "History", "Languages"):
                fdir = wpath / folder
                if not fdir.is_dir() and (wpath / "00-World-Bible" / folder).is_dir():
                    fdir = wpath / "00-World-Bible" / folder
                if fdir.is_dir():
                    c = len([f for f in fdir.glob("*.md") if not f.name.startswith(".") and "Template" not in f.name])
                    counts[folder] = c
                else:
                    counts[folder] = 0

            stats_str = "  •  ".join([f"<b>{k}</b>: {v}" for k, v in counts.items()])
            self.lbl_lore_stats.set_markup(f"<b>Registered Lore Entities:</b>\n{stats_str}")
            self.set_status(f"Active World: {wname}")
        else:
            self.lbl_cosmos_heading.set_markup("<span size='large' weight='bold'>No World Lore Selected</span>")
            self.lbl_cosmos_path.set_text("Create a new world lore vault to begin worldbuilding.")
            self.lbl_lore_stats.set_text("No world lore vault active.")

    def update_active_manuscript_display(self):
        if self.current_manuscript_path and Path(self.current_manuscript_path).is_dir():
            mpath = Path(self.current_manuscript_path)
            mname = mpath.name
            self.entry_pub_title.set_text(mname)
            self.refresh_volume_options()
            self.refresh_draft_selectors()
            self.refresh_manuscript_analytics()
            self.refresh_snapshot_history()
            self.update_secure_dest_display()
            self.set_status(f"Active Manuscript: {mname}")
        else:
            self.card_total_words.val_label.set_text("0")
            self.card_chapters.val_label.set_text("0")
            self.manuscript_store.clear()
            self.refresh_draft_selectors()
            self.update_secure_dest_display()

    def refresh_volume_options(self):
        self.combo_pub_volume.remove_all()
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            return
        tpath = Path(target)
        ms_dir = tpath / "01-Manuscript" if (tpath / "01-Manuscript").is_dir() else tpath
        books = []
        if ms_dir.is_dir():
            for b in sorted(ms_dir.glob("Book-*")):
                if b.is_dir():
                    books.append(b.name)

        if books:
            for b in books:
                self.combo_pub_volume.append(b, f"Volume: {b}")
            if len(books) > 1:
                self.combo_pub_volume.append("all", "All Volumes (Omnibus)")
            self.combo_pub_volume.set_active(0)
        else:
            self.combo_pub_volume.append("Book-01", "Volume: Book-01")
            self.combo_pub_volume.set_active(0)

    def refresh_manuscript_analytics(self):
        self.manuscript_store.clear()
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            return

        # ANA-01: canonical counter shared with cache.py / wordcount_report.sh.
        try:
            from lib.cache import count_words as _canonical_count
        except Exception:
            try:
                from cache import count_words as _canonical_count  # type: ignore
            except Exception:
                import re as _re
                _FM = _re.compile(r"^---\s*\n(.*?)\n---\s*\n", _re.DOTALL)

                def _canonical_count(text: str) -> int:  # type: ignore
                    clean = _FM.sub("", text)
                    clean = _re.sub(r"```.*?```", "", clean, flags=_re.DOTALL)
                    kept = [ln for ln in clean.splitlines()
                            if ln.strip() and not (ln.strip().startswith("@") and _re.match(r"^@[A-Za-z0-9_-]+:", ln.strip())) and not ln.strip().startswith("%")]
                    return len(_re.findall(r"\b\w+\b", "\n".join(kept), flags=_re.UNICODE))

        tpath = Path(target)
        ms_dir = tpath / "01-Manuscript" if (tpath / "01-Manuscript").is_dir() else tpath
        total_words = 0
        total_chapters = 0

        def _process_act_dir(act_dir, parent_iter):
            nonlocal total_chapters
            act_words = 0
            a_iter = self.manuscript_store.append(parent_iter, [act_dir.name, "Act / Section", "", str(act_dir)])
            for ch_file in sorted(act_dir.glob("*.md")):
                if ch_file.is_file() and not ch_file.name.startswith("."):
                    try:
                        content = ch_file.read_text(encoding="utf-8", errors="replace")
                        wc = _canonical_count(content)
                        act_words += wc
                        total_chapters += 1
                        self.manuscript_store.append(a_iter, [ch_file.name, "Scene / Chapter", f"{wc:,} words", str(ch_file)])
                    except Exception as e:
                        logger.warning("Error calculating scene word count for %s: %s", ch_file, e)
            self.manuscript_store.set_value(a_iter, 2, f"{act_words:,} words")
            return act_words

        if ms_dir.is_dir():
            for book_dir in sorted(ms_dir.glob("Book-*")):
                if book_dir.is_dir():
                    book_words = 0
                    b_iter = self.manuscript_store.append(None, [book_dir.name, "Volume", "Calculating...", str(book_dir)])
                    
                    draft_dirs = sorted([d for d in book_dir.glob("Draft-*") if d.is_dir()])
                    if draft_dirs:
                        for draft_dir in draft_dirs:
                            d_words = 0
                            d_iter = self.manuscript_store.append(b_iter, [draft_dir.name, "Draft Version", "", str(draft_dir)])
                            for sub in sorted(draft_dir.iterdir()):
                                if sub.is_dir() and not sub.name.startswith("."):
                                    d_words += _process_act_dir(sub, d_iter)
                            self.manuscript_store.set_value(d_iter, 2, f"{d_words:,} words")
                            book_words += d_words
                    else:
                        for act_dir in sorted(book_dir.iterdir()):
                            if act_dir.is_dir() and not act_dir.name.startswith(".") and act_dir.name != "Outlines":
                                book_words += _process_act_dir(act_dir, b_iter)

                    self.manuscript_store.set_value(b_iter, 2, f"{book_words:,} words")
                    total_words += book_words

        self.card_total_words.val_label.set_text(f"{total_words:,}")
        self.card_chapters.val_label.set_text(str(total_chapters))
        self.manuscript_tree.expand_all()

    def refresh_snapshot_history(self):
        self.history_store.clear()
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            return
        wpath = Path(target)
        if (wpath / ".git").is_dir():
            try:
                res = subprocess.run(
                    ["git", "-C", str(wpath), "log", "-n", "15", "--pretty=format:%h|%ad|%s", "--date=short"],
                    capture_output=True, text=True, check=True, timeout=15
                )
                for line in res.stdout.splitlines():
                    parts = line.split("|", 2)
                    if len(parts) == 3:
                        self.history_store.append([parts[0], parts[1], parts[2]])
            except Exception as e:
                logger.debug("Could not fetch git history: %s", e)

    def update_toolchain_badges(self):
        tools = [
            ("git", self.lbl_tool_git),
            ("pandoc", self.lbl_tool_pandoc),
            ("typst", self.lbl_tool_typst),
            ("python3", self.lbl_tool_python),
        ]
        for cmd, badge in tools:
            path = shutil.which(cmd)
            if path:
                badge.status_label.set_markup("<span color='#2e7d32'><b>✓ Installed</b></span>")
            else:
                badge.status_label.set_markup("<span color='#d32f2f'><b>✗ Missing</b></span>")

    # -------------------------------------------------------------------------
    # Visual Scene Metadata Inspector Logic
    # -------------------------------------------------------------------------
    def on_manuscript_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is None:
            self.btn_save_scene_tags.set_sensitive(False)
            self.btn_read_scene_tags.set_sensitive(False)
            return

        file_path_str = model.get_value(treeiter, 3)
        if file_path_str and Path(file_path_str).is_file() and file_path_str.endswith(".md"):
            self.current_selected_scene_file = file_path_str
            self.lbl_inspector_file.set_markup(f"<b>Scene:</b> <code>{Path(file_path_str).name}</code>")
            self.btn_save_scene_tags.set_sensitive(True)
            self.btn_read_scene_tags.set_sensitive(True)
            self.load_scene_tags_from_file(file_path_str)
        else:
            self.current_selected_scene_file = None
            self.btn_save_scene_tags.set_sensitive(False)
            self.btn_read_scene_tags.set_sensitive(False)
            self.lbl_inspector_file.set_markup("<i>Select a chapter/scene .md file to inspect tags</i>")

    def load_scene_tags_from_file(self, file_path):
        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
            tags = {
                "pov": "", "char": "", "location": "",
                "thread": "", "time": "", "status": "Draft"
            }
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("@pov:"):
                    tags["pov"] = stripped[5:].strip()
                elif stripped.startswith("@char:") or stripped.startswith("@character:"):
                    tags["char"] = stripped.split(":", 1)[1].strip()
                elif stripped.startswith("@location:") or stripped.startswith("@focus:"):
                    tags["location"] = stripped.split(":", 1)[1].strip()
                elif stripped.startswith("@thread:") or stripped.startswith("@plot:"):
                    tags["thread"] = stripped.split(":", 1)[1].strip()
                elif stripped.startswith("@time:"):
                    tags["time"] = stripped[6:].strip()
                elif stripped.startswith("@status:"):
                    tags["status"] = stripped[8:].strip()

            self.entry_tag_pov.set_text(tags["pov"])
            self.entry_tag_char.set_text(tags["char"])
            self.entry_tag_location.set_text(tags["location"])
            self.entry_tag_thread.set_text(tags["thread"])
            self.entry_tag_time.set_text(tags["time"])
            self.combo_tag_status.set_active_id(tags["status"] if tags["status"] in ("Draft", "Revision", "First Polish", "Final") else "Draft")
        except Exception as e:
            self.set_status(f"Error reading scene tags: {e}")

    def on_read_scene_tags_clicked(self, btn):
        if self.current_selected_scene_file:
            self.load_scene_tags_from_file(self.current_selected_scene_file)
            self.set_status("Scene tags refreshed from file.")

    def on_save_scene_tags_clicked(self, btn):
        if not self.current_selected_scene_file:
            return
        file_path = Path(self.current_selected_scene_file)
        if not file_path.is_file():
            return

        pov = self.entry_tag_pov.get_text().strip()
        cast = self.entry_tag_char.get_text().strip()
        loc = self.entry_tag_location.get_text().strip()
        thread = self.entry_tag_thread.get_text().strip()
        t_marker = self.entry_tag_time.get_text().strip()
        status = self.combo_tag_status.get_active_id() or "Draft"

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            frontmatter_lines = []
            heading = ""
            body_lines = []

            i = 0
            n = len(lines)
            if n > 0 and lines[0].strip() == "---":
                frontmatter_lines.append(lines[0])
                i = 1
                while i < n and lines[i].strip() != "---":
                    frontmatter_lines.append(lines[i])
                    i += 1
                if i < n:
                    frontmatter_lines.append(lines[i])
                    i += 1

            # After frontmatter (if present), find optional heading and strip
            # only MANAGED @tags. DAT-01: all other `@` lines (custom tags
            # like @tag:/@theme:/@object:, aliases like @character:/@focus:/
            # @plot:, and comments) are preserved byte-for-byte in their
            # original order so saving metadata can never delete author data.
            MANAGED_PREFIXES = (
                "@pov:", "@char:", "@location:",
                "@thread:", "@time:", "@status:",
            )
            preserved_custom_tags = []
            seen_heading = False
            while i < n:
                line = lines[i]
                stripped = line.strip()
                if not seen_heading and stripped.startswith("#"):
                    heading = line
                    seen_heading = True
                    i += 1
                    continue
                lowered = stripped.lower()
                if any(lowered.startswith(p) for p in MANAGED_PREFIXES):
                    i += 1
                    continue
                if stripped.startswith("@"):
                    preserved_custom_tags.append(line)
                    i += 1
                    continue
                body_lines.append(line)
                i += 1

            # Build clean metadata tag header (managed fields first, then
            # preserved custom tags in original order).
            tag_lines = []
            if pov:
                tag_lines.append(f"@pov: {pov}")
            if cast:
                tag_lines.append(f"@char: {cast}")
            if loc:
                tag_lines.append(f"@location: {loc}")
            if thread:
                tag_lines.append(f"@thread: {thread}")
            if t_marker:
                tag_lines.append(f"@time: {t_marker}")
            if status:
                tag_lines.append(f"@status: {status}")
            tag_lines.extend(preserved_custom_tags)

            new_body = "\n".join(body_lines).lstrip("\n")
            parts = []
            if frontmatter_lines:
                parts.append("\n".join(frontmatter_lines))
                parts.append("")
            if heading:
                parts.append(heading)
                parts.append("")
            if tag_lines:
                parts.extend(tag_lines)
                parts.append("")
            if new_body:
                parts.append(new_body)

            final_text = "\n".join(parts).rstrip() + "\n"
            # DAT-01: atomic write with pre-save backup so a crash or
            # encoding error can never truncate the author's scene file.
            import tempfile as _tf
            backup_path = file_path.with_name(file_path.name + ".pre-tag-save.bak")
            try:
                backup_path.write_text(content, encoding="utf-8")
            except Exception:
                pass
            fd, tmp_name = _tf.mkstemp(dir=str(file_path.parent), prefix=file_path.name + ".", suffix=".tmp")
            try:
                with open(fd, "w", encoding="utf-8", newline="\n") as _fh:
                    _fh.write(final_text)
                os.replace(tmp_name, file_path)
            except Exception:
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass
                raise
            self.set_status(f"Saved metadata header for '{file_path.name}'.")
        except Exception as e:
            self.show_error(f"Failed to update scene tags: {e}")

    # -------------------------------------------------------------------------
    # Dialogs & Event Handlers
    # -------------------------------------------------------------------------
    def on_new_universe_clicked(self, btn):
        dialog = Gtk.Dialog(title="New Narrative Universe", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        lbl = Gtk.Label(label="Enter name for new Universe container (e.g., 'Cosmere', 'Solaris-Prime'):")
        box.pack_start(lbl, False, False, 0)

        entry = Gtk.Entry()
        entry.set_text("New-Universe")
        box.pack_start(entry, False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            name = entry.get_text().strip()
            if name:
                cmd = ["bash", str(PROJECT_ROOT / "scripts" / "init_universe.sh"), name]
                self.set_status(f"Creating universe '{name}'...")

                def on_universe_created():
                    self.current_universe = name
                    self.refresh_all_discovery()

                self._start_worker(
                    self._run_async_command,
                    args=(cmd, f"Universe '{name}' created successfully!", on_universe_created),
                )
        dialog.destroy()

    def on_new_world_clicked(self, btn):
        dialog = Gtk.Dialog(title="New World Lore Vault", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        lbl = Gtk.Label(label="Enter name for your new World Lore Vault (e.g., 'Eldoria'):")
        box.pack_start(lbl, False, False, 0)

        entry = Gtk.Entry()
        entry.set_text("My-New-World")
        box.pack_start(entry, False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            wname = entry.get_text().strip()
            if wname:
                cmd = ["bash", str(PROJECT_ROOT / "scripts" / "init_world.sh"), wname]
                if self.current_universe:
                    cmd.extend(["--universe", self.current_universe])
                self.set_status(f"Scaffolding world lore vault '{wname}'...")

                def on_world_created():
                    self.refresh_all_discovery()
                    for name, path, label in self.discovered_worlds:
                        if name == wname:
                            self.combo_world.set_active_id(path)
                            break

                self._start_worker(
                    self._run_async_command,
                    args=(cmd, f"World lore vault '{wname}' created successfully!", on_world_created),
                )
        dialog.destroy()

    def on_new_manuscript_clicked(self, btn):
        dialog = Gtk.Dialog(title="New Manuscript Project", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        lbl = Gtk.Label(label="Enter name for your new Manuscript Project (e.g., 'The-Last-Archon'):")
        box.pack_start(lbl, False, False, 0)

        entry = Gtk.Entry()
        entry.set_text("My-New-Novel")
        box.pack_start(entry, False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            mname = entry.get_text().strip()
            if mname:
                cmd = ["bash", str(PROJECT_ROOT / "scripts" / "init_manuscript.sh"), mname]
                if self.current_universe:
                    cmd.extend(["--universe", self.current_universe])
                if self.current_world_path:
                    cmd.extend(["--world", Path(self.current_world_path).name])
                self.set_status(f"Scaffolding manuscript project '{mname}'...")

                def on_ms_created():
                    self.refresh_all_discovery()
                    for name, path, label in self.discovered_manuscripts:
                        if name == mname:
                            self.combo_manuscript.set_active_id(path)
                            break

                self._start_worker(
                    self._run_async_command,
                    args=(cmd, f"Manuscript '{mname}' created successfully!", on_ms_created),
                )
        dialog.destroy()

    def on_quick_snapshot_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            self.show_error("Please select an active manuscript or world first.")
            return

        dialog = Gtk.Dialog(title="Quick Version Snapshot", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        lbl = Gtk.Label(label="Describe your progress (e.g., 'Finished Act 1 outline'):")
        box.pack_start(lbl, False, False, 0)

        entry = Gtk.Entry()
        entry.set_text(f"Snapshot: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        box.pack_start(entry, False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            note = entry.get_text().strip()
            cmd = ["bash", str(PROJECT_ROOT / "scripts" / "save_snapshot.sh"), target, "--note", note]
            self.set_status("Saving version snapshot...")
            self._start_worker(self._run_async_command, args=(cmd, "Snapshot recorded successfully!", self.refresh_snapshot_history))
        dialog.destroy()

    def on_save_snapshot_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            self.show_error("Please select an active project first.")
            return
        note = self.entry_snap_note.get_text().strip()
        if not note:
            note = f"Snapshot: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "save_snapshot.sh"), target, "--note", note]
        self.set_status("Saving version milestone snapshot...")
        self._start_worker(self._run_async_command, args=(cmd, "Snapshot recorded successfully!", self.refresh_snapshot_history))

    def on_create_backup_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            self.show_error("Please select an active project first.")
            return
        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "backup_world.sh"), target]
        self.set_status("Creating standalone verified backup archive...")
        self._start_worker(self._run_async_command, args=(cmd, "Backup archive created with SHA-256 digest!"))

    def on_restore_clicked(self, btn):
        dialog = Gtk.FileChooserDialog(
            title="Select Ars Arcanum Backup Archive",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        filter_tar = Gtk.FileFilter()
        filter_tar.set_name("Backup Archives (*.tar.gz)")
        filter_tar.add_pattern("*.tar.gz")
        dialog.add_filter(filter_tar)

        if dialog.run() == Gtk.ResponseType.OK:
            archive_path = dialog.get_filename()
            dialog.destroy()

            name_dialog = Gtk.Dialog(title="Restore Target Name", parent=self, flags=0)
            name_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
            box = name_dialog.get_content_area()
            box.set_border_width(12)
            box.pack_start(Gtk.Label(label="Enter name for restored project folder:"), False, False, 6)
            name_entry = Gtk.Entry()
            name_entry.set_text("Restored-Project")
            box.pack_start(name_entry, False, False, 6)
            name_dialog.show_all()

            if name_dialog.run() == Gtk.ResponseType.OK:
                target_name = name_entry.get_text().strip()
                cmd = ["bash", str(PROJECT_ROOT / "scripts" / "restore_world.sh"), "--archive", archive_path, "--target", target_name]
                if self.current_universe:
                    cmd.extend(["--universe", self.current_universe])
                self.set_status("Restoring project from archive...")
                self._start_worker(self._run_async_command, args=(cmd, "Project restored and verified successfully!", self.refresh_all_discovery))
            name_dialog.destroy()
        else:
            dialog.destroy()

    def on_compile_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            self.show_error("Please select an active manuscript or world first.")
            return

        title = self.entry_pub_title.get_text().strip() or "Book Title"
        author = self.entry_pub_author.get_text().strip() or "Author Name"
        volume = self.combo_pub_volume.get_active_id() or "Book-01"
        paper_size = self.combo_paper_size.get_active_id() or "us-trade"
        export_fmt = self.combo_pub_format.get_active_id() or "book"

        cmd = [
            "bash", str(PROJECT_ROOT / "scripts" / "export_book.sh"),
            target,
            "--title", title,
            "--author", author,
            "--book", volume,
            "--paper-size", paper_size,
            "--format", export_fmt
        ]

        self.btn_compile.set_sensitive(False)
        self.pub_log_buffer.set_text(f"Starting compilation for '{title}' [{volume}] (format: {export_fmt})...\n")
        self.set_status(f"Compiling publication artifacts ({export_fmt})...")

        def _worker():
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self._stream_process_to_log(proc, self.pub_log_buffer, self._append_log)
            proc.wait()
            GLib.idle_add(self._on_compile_done, proc.returncode)

        self._start_worker(_worker)

    def _append_log(self, buffer_obj, text):
        end_iter = buffer_obj.get_end_iter()
        buffer_obj.insert(end_iter, text)

    def _on_compile_done(self, returncode):
        self.btn_compile.set_sensitive(True)
        if returncode == 0:
            self.set_status("Artifacts compiled successfully!")
            self.btn_open_pdf.set_sensitive(True)
            self.btn_open_epub.set_sensitive(True)
            self.btn_open_docx.set_sensitive(True)
        else:
            self.set_status("Compilation finished with warnings/errors.")

    def on_open_pdf_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if target:
            tpath = Path(target)
            pub_dir = tpath / "Exports" if (tpath / "Exports").is_dir() else tpath / "04-Publishing"
            pdfs = list(pub_dir.glob("*.pdf"))
            if pdfs:
                latest = max(pdfs, key=os.path.getmtime)
                self._launch_detached(["xdg-open", str(latest)])

    def on_open_epub_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if target:
            tpath = Path(target)
            pub_dir = tpath / "Exports" if (tpath / "Exports").is_dir() else tpath / "04-Publishing"
            epubs = list(pub_dir.glob("*.epub"))
            if epubs:
                latest = max(epubs, key=os.path.getmtime)
                self._launch_detached(["xdg-open", str(latest)])

    def on_open_docx_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if target:
            tpath = Path(target)
            pub_dir = tpath / "Exports" if (tpath / "Exports").is_dir() else tpath / "04-Publishing"
            docxs = list(pub_dir.glob("*.docx"))
            if docxs:
                latest = max(docxs, key=os.path.getmtime)
                self._launch_detached(["xdg-open", str(latest)])

    def on_add_volume_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            self.show_error("Please select an active manuscript or world first.")
            return

        tpath = Path(target)
        ms_dir = tpath / "01-Manuscript" if (tpath / "01-Manuscript").is_dir() else tpath
        max_num = 0
        if ms_dir.is_dir():
            for b in ms_dir.glob("Book-*"):
                if b.is_dir():
                    m = re.match(r"Book-(\d+)", b.name)
                    if m:
                        max_num = max(max_num, int(m.group(1)))
        default_vol = f"Book-{max_num + 1:02d}"

        dialog = Gtk.Dialog(title="Add Manuscript Volume", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        lbl = Gtk.Label(label=f"Enter volume name for '{tpath.name}':")
        box.pack_start(lbl, False, False, 0)

        entry = Gtk.Entry()
        entry.set_text(default_vol)
        box.pack_start(entry, False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            vol_name = entry.get_text().strip()
            if vol_name:
                cmd = ["bash", str(PROJECT_ROOT / "scripts" / "add_book.sh"), target, vol_name]
                self.set_status(f"Scaffolding volume '{vol_name}'...")
                self._start_worker(self._run_async_command, args=(cmd, f"Volume '{vol_name}' created successfully!", self.refresh_after_add_volume))
        dialog.destroy()

    def refresh_after_add_volume(self):
        self.refresh_volume_options()
        self.refresh_manuscript_analytics()

    def on_generate_concordance_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            self.show_error("Please select an active manuscript or world first.")
            return

        volume = self.combo_pub_volume.get_active_id() or "all"
        cmd = [
            "bash", str(PROJECT_ROOT / "scripts" / "generate_concordance.sh"),
            target,
            "--book", volume
        ]
        self.set_status(f"Generating back-matter concordance for volume '{volume}'...")
        self.pub_log_buffer.set_text(f"Starting Concordance & Dramatis Personae generation [{volume}]...\n")

        def _worker():
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self._stream_process_to_log(proc, self.pub_log_buffer, self._append_log)
            proc.wait()
            if proc.returncode == 0:
                GLib.idle_add(self.set_status, "Concordance and Dramatis Personae generated successfully!")
                GLib.idle_add(self.refresh_manuscript_analytics)
            else:
                GLib.idle_add(self.set_status, "Concordance generation encountered warnings/errors.")

        self._start_worker(_worker)

    def run_diagnostics(self):
        self.doc_log_buffer.set_text("Running Ars Arcanum & World Doctor diagnostics...\n")
        self.set_status("Running diagnostics...")

        def _worker():
            cmd1 = ["bash", str(PROJECT_ROOT / "scripts" / "arcanum_doctor.sh")]
            if self.current_world_path:
                cmd1.extend(["--world", self.current_world_path])
            try:
                res1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=90)
                GLib.idle_add(self._append_log, self.doc_log_buffer, res1.stdout + "\n" + res1.stderr)
            except subprocess.TimeoutExpired:
                GLib.idle_add(self.set_status, "Diagnostics timed out after 90s.")
                return

            if self.current_world_path:
                cmd2 = ["bash", str(PROJECT_ROOT / "scripts" / "world_doctor.sh"), self.current_world_path]
                try:
                    res2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=120)
                    GLib.idle_add(self._append_log, self.doc_log_buffer, res2.stdout + "\n" + res2.stderr)
                except subprocess.TimeoutExpired:
                    GLib.idle_add(self._append_log, self.doc_log_buffer, "[!] world_doctor timed out after 120s; try --fast.\n")
            GLib.idle_add(self.set_status, "Diagnostics complete.")

        self._start_worker(_worker)

    def run_verify_harness(self):
        self.doc_log_buffer.set_text("Running full 7-stage verification suite...\n")
        self.set_status("Running verification harness...")

        def _worker():
            cmd = ["bash", str(PROJECT_ROOT / "scripts" / "verify.sh")]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self._stream_process_to_log(proc, self.doc_log_buffer, self._append_log)
            proc.wait()
            GLib.idle_add(self.set_status, "Verification run complete.")

        self._start_worker(_worker)

    def on_generate_demo_clicked(self, btn):
        demo_uni = "Cosmere-Prime"
        demo_world = "Chronicles-of-Eldoria"
        demo_ms = "The-Sovereign-Scroll"
        self.set_status("Scaffolding demo cosmos and manuscript...")

        def _worker():
            subprocess.run(["bash", str(PROJECT_ROOT / "scripts" / "init_universe.sh"), demo_uni], capture_output=True, timeout=120)
            subprocess.run(["bash", str(PROJECT_ROOT / "scripts" / "init_world.sh"), demo_world, "--universe", demo_uni], capture_output=True, timeout=120)
            subprocess.run(["bash", str(PROJECT_ROOT / "scripts" / "init_manuscript.sh"), demo_ms, "--universe", demo_uni, "--world", demo_world], capture_output=True, timeout=120)
            GLib.idle_add(self.refresh_all_discovery)
            GLib.idle_add(self.set_status, "Demo Cosmos & Manuscript created successfully!")

        self._start_worker(_worker)

    def _is_flatpak_installed(self, app_id):
        try:
            res = subprocess.run(["flatpak", "info", app_id], capture_output=True, timeout=10)
            return res.returncode == 0
        except Exception as e:
            logger.debug("Flatpak info probe failed for %s: %s", app_id, e)
            return False

    def _launch_in_background(self, chooser):
        self._start_worker(chooser)

    def on_launch_obsidian(self, btn):
        if not self.current_world_path:
            return
        bible = Path(self.current_world_path)

        def _launch():
            if self._is_flatpak_installed("md.obsidian.Obsidian"):
                self._launch_detached(["flatpak", "run", "md.obsidian.Obsidian", str(bible)])
            elif shutil.which("obsidian"):
                self._launch_detached(["obsidian", str(bible)])
            else:
                self._launch_detached(["xdg-open", str(bible)])

        self._launch_in_background(_launch)

    def on_launch_novelwriter(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            return
        tpath = Path(target)
        nw_proj = tpath / "nwProject.nwx"
        if not nw_proj.is_file() and (tpath / "01-Manuscript" / "nwProject.nwx").is_file():
            nw_proj = tpath / "01-Manuscript" / "nwProject.nwx"
        target_str = str(nw_proj) if nw_proj.is_file() else str(tpath)

        def _launch():
            if self._is_flatpak_installed("io.gitlab.novelwriter.novelWriter"):
                self._launch_detached(["flatpak", "run", "io.gitlab.novelwriter.novelWriter", target_str])
            elif shutil.which("novelwriter"):
                self._launch_detached(["novelwriter", target_str])
            else:
                self._launch_detached(["xdg-open", str(tpath)])

        self._launch_in_background(_launch)

    def on_launch_focuswriter(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            return
        tpath = Path(target)
        ms = tpath / "Book-01"
        if not ms.is_dir() and (tpath / "01-Manuscript" / "Book-01").is_dir():
            ms = tpath / "01-Manuscript" / "Book-01"

        def _launch():
            if shutil.which("focuswriter"):
                self._launch_detached(["focuswriter", str(ms)])
            else:
                self._launch_detached(["xdg-open", str(ms)])

        self._launch_in_background(_launch)

    def on_open_world_folder_clicked(self, btn):
        if self.current_world_path:
            self._launch_detached(["xdg-open", str(self.current_world_path)])

    def on_open_manual_clicked(self, btn):
        manual_path = PROJECT_ROOT / "docs" / "AUTHOR_MANUAL.md"
        if manual_path.is_file():
            self._launch_detached(["xdg-open", str(manual_path)])
        else:
            self.show_error("Author's Field Manual not found.")

    def check_first_run(self):
        flag_file = HOME_DIR / ".config" / "arcanum" / "first_run_done"
        if not flag_file.is_file() and not self.discovered_worlds and not self.discovered_manuscripts:
            GLib.idle_add(self.show_welcome_dialog, flag_file)

    def show_welcome_dialog(self, flag_file):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Welcome to Ars Arcanum!"
        )
        dialog.format_secondary_text(
            "Ars Arcanum is your private, local-first writing and worldbuilding studio.\n\n"
            "• Tab 1 (Universes & Worlds): Manage Obsidian World Lore Vaults directly.\n"
            "• Tab 2 (Manuscripts & Drafting): Organize scenes and inspect/write @pov, @char, @location, @thread, and @status tags visually.\n"
            "• Tab 3 (Publishing & Exports): Compile trade-quality print PDFs, EPUBs, and DOCX submission manuscripts.\n"
            "• Click '📖 Field Manual' in the top right anytime for complete guides.\n\n"
            "Happy Writing!"
        )
        dialog.run()
        dialog.destroy()
    def refresh_draft_selectors(self):
        if not hasattr(self, "combo_draft_vol") or self.combo_draft_vol is None:
            return
        
        target = self.current_manuscript_path
        if not target or not Path(target).is_dir():
            self.combo_draft_vol.remove_all()
            self.combo_draft_list.remove_all()
            self.combo_diff_a.remove_all()
            self.combo_diff_b.remove_all()
            return

        tpath = Path(target)
        cur_vol = self.combo_draft_vol.get_active_id()
        self.combo_draft_vol.remove_all()
        volumes = [b.name for b in sorted(tpath.glob("Book-*")) if b.is_dir()]
        if not volumes:
            volumes = ["Book-01"]
        for v in volumes:
            self.combo_draft_vol.append(v, v)
        
        if cur_vol and cur_vol in volumes:
            self.combo_draft_vol.set_active_id(cur_vol)
        else:
            self.combo_draft_vol.set_active(0)

        active_vol = self.combo_draft_vol.get_active_id() or "Book-01"
        book_dir = tpath / active_vol

        drafts = []
        if book_dir.is_dir():
            for d in sorted(book_dir.glob("Draft-*")):
                if d.is_dir():
                    drafts.append(d.name)
        if not drafts and (book_dir / "01_Act_I").is_dir():
            drafts = ["Draft-01 (Baseline)"]

        self.combo_draft_list.remove_all()
        self.combo_diff_a.remove_all()
        self.combo_diff_b.remove_all()

        for d in drafts:
            self.combo_draft_list.append(d, d)
            self.combo_diff_a.append(d, d)
            self.combo_diff_b.append(d, d)

        if drafts:
            self.combo_draft_list.set_active(len(drafts) - 1)
            self.combo_diff_b.set_active(len(drafts) - 1)
            self.combo_diff_a.set_active(0)

    def update_secure_dest_display(self):
        if not hasattr(self, "lbl_secure_dest") or self.lbl_secure_dest is None:
            return
        dest = get_backup_dest()
        if dest:
            self.lbl_secure_dest.set_markup(f"<b>Secure Destination:</b> <code>{dest}</code>")
        else:
            self.lbl_secure_dest.set_markup("<b>Secure Destination:</b> <i>None (Local 05-Backups/ only)</i>")

    def on_fork_draft_clicked(self, btn):
        target = self.current_manuscript_path
        if not target:
            self.show_error("Please select an active manuscript first.")
            return

        vol = self.combo_draft_vol.get_active_id() or "Book-01"
        dialog = Gtk.Dialog(title="Fork New Manuscript Draft", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        lbl = Gtk.Label(label=f"Enter identifier for new draft in {Path(target).name} ({vol}):")
        box.pack_start(lbl, False, False, 0)

        entry = Gtk.Entry()
        entry.set_text("Draft-02")
        box.pack_start(entry, False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            draft_name = entry.get_text().strip()
            if draft_name:
                cmd = ["bash", str(PROJECT_ROOT / "scripts" / "init_draft.sh"), target, draft_name, "-b", vol]
                self.set_status(f"Forking draft '{draft_name}'...")
                def _after_fork():
                    self.refresh_draft_selectors()
                    self.refresh_manuscript_analytics()
                self._start_worker(self._run_async_command, args=(cmd, f"Draft '{draft_name}' initialized!", _after_fork))
        dialog.destroy()

    def on_view_redline_clicked(self, btn):
        target = self.current_manuscript_path
        if not target:
            self.show_error("Please select an active manuscript first.")
            return
        vol = self.combo_draft_vol.get_active_id() or "Book-01"
        draft_b = self.combo_diff_b.get_active_id()
        draft_a = self.combo_diff_a.get_active_id()
        if not draft_b or not draft_a:
            self.show_error("Please select both a target draft and a prior draft to compare.")
            return
        if draft_b == draft_a:
            self.show_error("Target draft and prior draft must be different to view changes.")
            return

        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "compare_drafts.sh"), target, draft_b, draft_a, "-b", vol, "--browser"]
        self.set_status(f"Generating Redline diff: {draft_a} vs {draft_b}...")
        self._start_worker(self._run_async_command, args=(cmd, "Redline diff opened in browser!"))

    def on_lo_compare_clicked(self, btn):
        target = self.current_manuscript_path
        if not target:
            self.show_error("Please select an active manuscript first.")
            return
        vol = self.combo_draft_vol.get_active_id() or "Book-01"
        draft_b = self.combo_diff_b.get_active_id()
        draft_a = self.combo_diff_a.get_active_id()
        if not draft_b or not draft_a:
            self.show_error("Please select both drafts.")
            return
        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "compare_drafts.sh"), target, draft_b, draft_a, "-b", vol, "--libreoffice"]
        self.set_status("Launching LibreOffice Writer Track Changes comparison...")
        self._start_worker(self._run_async_command, args=(cmd, "LibreOffice Writer comparison launched."))

    def on_select_secure_dest_clicked(self, btn):
        dialog = Gtk.FileChooserDialog(
            title="Select External / USB Secure Backup Destination Directory",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        if dialog.run() == Gtk.ResponseType.OK:
            chosen = dialog.get_filename()
            dialog.destroy()
            if chosen:
                set_backup_dest(chosen)
                self.update_secure_dest_display()
                self.set_status(f"Secure backup destination updated: {chosen}")
        else:
            dialog.destroy()

    def on_clear_secure_dest_clicked(self, btn):
        clear_backup_dest()
        self.update_secure_dest_display()
        self.set_status("Secure backup destination cleared (local only).")

    def on_open_word_processor_clicked(self, btn):
        target = self.current_manuscript_path
        if not target:
            self.show_error("Please select an active manuscript first.")
            return
        vol = self.combo_draft_vol.get_active_id() or "Book-01"
        draft = self.combo_draft_list.get_active_id()
        mpath = Path(target)
        draft_dir = mpath / "01-Manuscript" / vol / draft if (mpath / "01-Manuscript" / vol / draft).is_dir() else (mpath / vol / draft if (mpath / vol / draft).is_dir() else mpath)
        
        target_docx = None
        if draft_dir.is_dir():
            cons = list(draft_dir.glob("*_Manuscript.docx"))
            if cons:
                target_docx = cons[0]
            else:
                docxs = list(draft_dir.rglob("*.docx"))
                if docxs:
                    target_docx = docxs[0]
                    
        if not target_docx:
            self.set_status("Compiling initial DOCX package...")
            build_manuscript_docx(mpath, draft_name=draft)
            if draft_dir.is_dir():
                cons = list(draft_dir.glob("*_Manuscript.docx"))
                if cons:
                    target_docx = cons[0]
                    
        if target_docx and target_docx.is_file():
            self.set_status(f"Opening {target_docx.name} in word processor...")
            open_in_word_processor(target_docx)
        else:
            self.show_error("Could not find or generate .docx manuscript.")

    def on_sync_docx_clicked(self, btn):
        target = self.current_manuscript_path
        if not target:
            self.show_error("Please select an active manuscript first.")
            return
        draft = self.combo_draft_list.get_active_id()
        self.set_status("Synchronizing DOCX and Markdown scenes...")
        def _do_sync():
            res = sync_manuscript_docx(Path(target), draft_name=draft)
            def _done():
                self.refresh_manuscript_analytics()
                msg = f"DOCX Sync Complete: {len(res['md_to_docx'])} exported, {len(res['docx_to_md'])} imported."
                self.set_status(msg)
                dialog = Gtk.MessageDialog(
                    transient_for=self, flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="DOCX Synchronization Complete"
                )
                dialog.format_secondary_text(f"• Markdown -> DOCX updated: {len(res['md_to_docx'])}\n• DOCX -> Markdown imported: {len(res['docx_to_md'])}\n• Errors: {len(res['errors'])}")
                dialog.run()
                dialog.destroy()
            GLib.idle_add(_done)
        self._start_worker(_do_sync)

    def on_docx_settings_clicked(self, btn):
        dialog = Gtk.Dialog(title="DOCX Manuscript Formatting & Submission Presets", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_APPLY, Gtk.ResponseType.APPLY)
        dialog.set_default_size(520, 420)
        box = dialog.get_content_area()
        box.set_border_width(14)
        box.set_spacing(10)

        cfg = get_docx_config()
        active_preset = get_active_docx_preset_name()
        presets = list_docx_presets()

        lbl_desc = Gtk.Label(label="<b>Configure standard Word (.docx) formatting for MS Word, Google Docs & Submission:</b>", use_markup=True)
        lbl_desc.set_xalign(0)
        box.pack_start(lbl_desc, False, False, 0)

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(8)

        # Preset Dropdown
        grid.attach(Gtk.Label(label="Formatting Preset:", xalign=0), 0, 0, 1, 1)
        combo_preset = Gtk.ComboBoxText()
        for pid, pinfo in presets.items():
            combo_preset.append(pid, pinfo["name"])
        combo_preset.set_active_id(active_preset)
        grid.attach(combo_preset, 1, 0, 1, 1)

        # Font Family
        grid.attach(Gtk.Label(label="Font Family:", xalign=0), 0, 1, 1, 1)
        combo_font = Gtk.ComboBoxText()
        for f in ["Times New Roman", "Georgia", "EB Garamond", "Libertinus Serif", "Courier Prime", "Arial"]:
            combo_font.append(f, f)
        combo_font.set_active_id(cfg.get("font_family", "Times New Roman"))
        grid.attach(combo_font, 1, 1, 1, 1)

        # Font Size
        grid.attach(Gtk.Label(label="Font Size (pt):", xalign=0), 0, 2, 1, 1)
        spin_sz = Gtk.SpinButton.new_with_range(9.0, 18.0, 0.5)
        spin_sz.set_value(float(cfg.get("font_size_pt", 12.0)))
        grid.attach(spin_sz, 1, 2, 1, 1)

        # Line Spacing
        grid.attach(Gtk.Label(label="Line Spacing:", xalign=0), 0, 3, 1, 1)
        combo_ls = Gtk.ComboBoxText()
        combo_ls.append("2.0", "2.0x (Double Spaced - Standard Submission)")
        combo_ls.append("1.5", "1.5x (Classic Trade)")
        combo_ls.append("1.35", "1.35x (Modern Editorial)")
        combo_ls.append("1.0", "1.0x (Single Spaced)")
        cur_ls = str(cfg.get("line_spacing", 2.0))
        combo_ls.set_active_id(cur_ls if cur_ls in ("2.0", "1.5", "1.35", "1.0") else "2.0")
        grid.attach(combo_ls, 1, 3, 1, 1)

        # Margins
        grid.attach(Gtk.Label(label="Margins (inches):", xalign=0), 0, 4, 1, 1)
        spin_mg = Gtk.SpinButton.new_with_range(0.5, 2.0, 0.1)
        spin_mg.set_value(float(cfg.get("margin_inches", 1.0)))
        grid.attach(spin_mg, 1, 4, 1, 1)

        # First Line Indent
        grid.attach(Gtk.Label(label="Paragraph Indent (inches):", xalign=0), 0, 5, 1, 1)
        spin_id = Gtk.SpinButton.new_with_range(0.0, 1.5, 0.05)
        spin_id.set_value(float(cfg.get("first_line_indent_inches", 0.5)))
        grid.attach(spin_id, 1, 5, 1, 1)

        # Scene Break Symbol
        grid.attach(Gtk.Label(label="Scene Break Symbol:", xalign=0), 0, 6, 1, 1)
        entry_sb = Gtk.Entry()
        entry_sb.set_text(str(cfg.get("scene_break_symbol", "#")))
        grid.attach(entry_sb, 1, 6, 1, 1)

        box.pack_start(grid, False, False, 0)

        # Description Label
        lbl_info = Gtk.Label()
        lbl_info.set_line_wrap(True)
        lbl_info.set_xalign(0)
        def _update_info_label(c):
            pid = c.get_active_id()
            if pid in presets:
                p = presets[pid]
                lbl_info.set_markup(f"<i>{p['description']}</i>")
                if pid != "custom":
                    combo_font.set_active_id(p["font_family"])
                    spin_sz.set_value(p["font_size_pt"])
                    combo_ls.set_active_id(str(p["line_spacing"]))
                    spin_mg.set_value(p["margin_inches"])
                    spin_id.set_value(p["first_line_indent_inches"])
                    entry_sb.set_text(p["scene_break_symbol"])
        combo_preset.connect("changed", _update_info_label)
        _update_info_label(combo_preset)
        box.pack_start(lbl_info, False, False, 0)

        dialog.show_all()
        res = dialog.run()
        if res == Gtk.ResponseType.APPLY:
            chosen_preset = combo_preset.get_active_id()
            if chosen_preset == "custom":
                set_docx_option("font_family", combo_font.get_active_id() or "Times New Roman")
                set_docx_option("font_size_pt", float(spin_sz.get_value()))
                set_docx_option("line_spacing", float(combo_ls.get_active_id() or "2.0"))
                set_docx_option("margin_inches", float(spin_mg.get_value()))
                set_docx_option("first_line_indent_inches", float(spin_id.get_value()))
                set_docx_option("scene_break_symbol", entry_sb.get_text().strip() or "#")
            else:
                set_docx_preset(chosen_preset)
            self.set_status(f"DOCX formatting updated to preset: {chosen_preset}")
            if self.current_manuscript_path:
                draft = self.combo_draft_list.get_active_id()
                build_manuscript_docx(Path(self.current_manuscript_path), draft_name=draft)
        dialog.destroy()

    def show_error(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()

    def _start_worker(self, target, args=()):
        threading.Thread(target=target, args=args, daemon=True).start()

    # UI-01: batched log streaming — one idle_add per 50-line chunk instead
    # of one per line, so `verify.sh` output cannot flood the GTK main loop.
    @staticmethod
    def _stream_process_to_log(proc, buffer_obj, append_fn, chunk_lines=50):
        buf = []
        try:
            for line in proc.stdout or []:
                buf.append(line)
                if len(buf) >= chunk_lines:
                    GLib.idle_add(append_fn, buffer_obj, "".join(buf))
                    buf = []
        finally:
            if buf:
                GLib.idle_add(append_fn, buffer_obj, "".join(buf))

    # UI-01: detached launcher — DEVNULL stdio + new session + reaper
    # thread, so xdg-open / flatpak / editor children never become zombies
    # and failures are logged instead of silent.
    @staticmethod
    def _launch_detached(argv):
        try:
            proc = subprocess.Popen(
                list(argv),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception as e:
            logger.warning("Failed to launch %s: %s", argv, e)
            return None

        def _reap():
            try:
                rc = proc.wait(timeout=30)
                if rc != 0:
                    logger.warning("Launcher %s exited with code %s", argv, rc)
            except Exception as e:
                logger.warning("Launcher %s wait failed: %s", argv, e)

        threading.Thread(target=_reap, daemon=True).start()
        return proc

    def _run_async_command(self, cmd, success_msg, callback=None, timeout=120):
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            GLib.idle_add(self.set_status, "Error: command timed out.")
            return
        if res.returncode == 0:
            GLib.idle_add(self.set_status, success_msg)
        else:
            GLib.idle_add(self.set_status, f"Error: {res.stderr.strip() or 'Command failed'}")
        if callback:
            GLib.idle_add(callback)

# Compatibility alias
ScriptoriumApp = ArcanumApp

def run_gtk3_app():
    if not HAS_GTK:
        return False
    app = ArcanumApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
    return True

def main():
    if not HAS_GTK:
        print("[!] PyGObject / GTK 3 is not installed in the current Python environment.", file=sys.stderr)
        print("[i] Falling back to Zenity desktop control dashboard...", file=sys.stderr)
        sys.exit(2)

    run_gtk3_app()

if __name__ == "__main__":
    main()

