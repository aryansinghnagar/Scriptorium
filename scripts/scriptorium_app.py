#!/usr/bin/env python3
"""
Scriptorium Desktop Application
================================
A native GTK 3 desktop application for authors, worldbuilders, and novelists.
Provides a unified, beginner-friendly interface for managing Universes, Worlds,
Obsidian World Bibles, novelWriter drafting, Typst/Pandoc publishing, Git versioning,
and standalone disaster recovery backups.
"""

import sys
import os
import subprocess
import threading
import json
import re
from pathlib import Path

# Check GTK 3 availability
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk, GLib, Pango
    HAS_GTK = True
except (ImportError, ValueError):
    HAS_GTK = False
    class _DummyGtk:
        class Window: pass
    Gtk = _DummyGtk()

HOME_DIR = Path.home()
UNIVERSES_DIR = HOME_DIR / "Universes"
WORLDS_DIR = HOME_DIR / "Worlds"
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

class ScriptoriumApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Scriptorium — Author & Worldbuilder Studio")
        self.set_default_size(980, 680)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Apply basic modern styling
        self.setup_styles()

        self.current_universe = None
        self.current_world_path = None
        self.discovered_universes = []
        self.discovered_worlds = []

        # Main vertical container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # Header Bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Scriptorium"
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
        help_btn.set_tooltip_text("Open the Scriptorium Author's Field Manual")
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
        self.tab_writing = self.create_writing_tab()
        self.tab_publishing = self.create_publishing_tab()
        self.tab_safety = self.create_safety_tab()
        self.tab_doctor = self.create_doctor_tab()

        self.notebook.append_page(self.tab_cosmos, Gtk.Label(label="🪐 Cosmos & Projects"))
        self.notebook.append_page(self.tab_writing, Gtk.Label(label="✍️ Writing & Analytics"))
        self.notebook.append_page(self.tab_publishing, Gtk.Label(label="📚 Publishing Studio"))
        self.notebook.append_page(self.tab_safety, Gtk.Label(label="🔒 Vault Safety"))
        self.notebook.append_page(self.tab_doctor, Gtk.Label(label="🩺 Doctor Diagnostics"))

        # Bottom Status Bar
        self.statusbar = Gtk.Statusbar()
        self.status_context = self.statusbar.get_context_id("main")
        main_box.pack_start(self.statusbar, False, False, 0)

        self.refresh_universe_and_worlds()
        self.check_first_run()

    def setup_styles(self):
        css_provider = Gtk.CssProvider()
        css = b"""
        .title-label { font-size: 16px; font-weight: bold; }
        .section-header { font-size: 13px; font-weight: bold; color: #4a90d9; }
        .card-box { background: alpha(@theme_bg_color, 0.5); border: 1px solid alpha(@theme_fg_color, 0.15); border-radius: 6px; padding: 12px; margin: 6px; }
        .stat-value { font-size: 20px; font-weight: bold; color: #2e7d32; }
        .danger-btn { background: #d32f2f; color: white; }
        """
        try:
            css_provider.load_from_data(css)
            screen = Gdk.Screen.get_default()
            if screen:
                Gtk.StyleContext.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        except Exception:
            pass

    def set_status(self, message):
        self.statusbar.pop(self.status_context)
        self.statusbar.push(self.status_context, message)

    def create_selector_bar(self):
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        bar.set_border_width(10)
        bar.get_style_context().add_class("card-box")

        lbl_uni = Gtk.Label(label="<b>Universe:</b>", use_markup=True)
        bar.pack_start(lbl_uni, False, False, 0)

        self.combo_universe = Gtk.ComboBoxText()
        self.combo_universe.connect("changed", self.on_universe_changed)
        bar.pack_start(self.combo_universe, False, False, 0)

        btn_new_uni = Gtk.Button(label="+ New Universe")
        btn_new_uni.connect("clicked", self.on_new_universe_clicked)
        bar.pack_start(btn_new_uni, False, False, 0)

        bar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 5)

        lbl_world = Gtk.Label(label="<b>Active World:</b>", use_markup=True)
        bar.pack_start(lbl_world, False, False, 0)

        self.combo_world = Gtk.ComboBoxText()
        self.combo_world.connect("changed", self.on_world_changed)
        bar.pack_start(self.combo_world, True, True, 0)

        btn_new_world = Gtk.Button(label="+ New World")
        btn_new_world.get_style_context().add_class("suggested-action")
        btn_new_world.connect("clicked", self.on_new_world_clicked)
        bar.pack_start(btn_new_world, False, False, 0)

        btn_refresh = Gtk.Button(label="🔄")
        btn_refresh.set_tooltip_text("Refresh discovered universes and worlds")
        btn_refresh.connect("clicked", lambda b: self.refresh_universe_and_worlds())
        bar.pack_start(btn_refresh, False, False, 0)

        return bar

    # -------------------------------------------------------------------------
    # TAB 1: Cosmos & Projects
    # -------------------------------------------------------------------------
    def create_cosmos_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_border_width(18)
        scrolled.add(box)

        # Overview Header
        self.lbl_cosmos_heading = Gtk.Label()
        self.lbl_cosmos_heading.set_markup("<span size='large' weight='bold'>Cosmos Overview</span>")
        self.lbl_cosmos_heading.set_xalign(0)
        box.pack_start(self.lbl_cosmos_heading, False, False, 0)

        self.lbl_cosmos_path = Gtk.Label(label="No world selected")
        self.lbl_cosmos_path.set_xalign(0)
        self.lbl_cosmos_path.set_selectable(True)
        box.pack_start(self.lbl_cosmos_path, False, False, 0)

        # Tool Launchers Grid
        grid_frame = Gtk.Frame(label=" Creative Studio Launchers ")
        grid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        grid_box.set_border_width(14)
        grid_frame.add(grid_box)

        launchers_grid = Gtk.Grid()
        launchers_grid.set_column_spacing(12)
        launchers_grid.set_row_spacing(12)
        launchers_grid.set_row_homogeneous(True)
        launchers_grid.set_column_homogeneous(True)

        btn_obsidian = Gtk.Button(label="📖  Open World Bible\n(Obsidian Vault)")
        btn_obsidian.connect("clicked", self.on_launch_obsidian)
        launchers_grid.attach(btn_obsidian, 0, 0, 1, 1)

        btn_novelwriter = Gtk.Button(label="✍️  Drafting Studio\n(novelWriter / Longform)")
        btn_novelwriter.connect("clicked", self.on_launch_novelwriter)
        launchers_grid.attach(btn_novelwriter, 1, 0, 1, 1)

        btn_focuswriter = Gtk.Button(label="⚡  Sprint Canvas\n(FocusWriter Distraction-Free)")
        btn_focuswriter.connect("clicked", self.on_launch_focuswriter)
        launchers_grid.attach(btn_focuswriter, 2, 0, 1, 1)

        btn_libreoffice = Gtk.Button(label="📝  Editorial Revisions\n(LibreOffice Writer)")
        btn_libreoffice.connect("clicked", self.on_launch_libreoffice)
        launchers_grid.attach(btn_libreoffice, 0, 1, 1, 1)

        btn_calibre = Gtk.Button(label="📱  Ebook Inspector\n(Calibre Reader)")
        btn_calibre.connect("clicked", self.on_launch_calibre)
        launchers_grid.attach(btn_calibre, 1, 1, 1, 1)

        btn_files = Gtk.Button(label="📁  Browse World Folder\n(File Manager)")
        btn_files.connect("clicked", self.on_open_folder_clicked)
        launchers_grid.attach(btn_files, 2, 1, 1, 1)

        grid_box.pack_start(launchers_grid, True, True, 0)
        box.pack_start(grid_frame, False, False, 0)

        # Jumpstart & Sample Cosmos Banner
        demo_frame = Gtk.Frame(label=" Jumpstart & Exploration ")
        demo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        demo_box.set_border_width(12)
        demo_frame.add(demo_box)

        lbl_demo = Gtk.Label()
        lbl_demo.set_markup("<b>New to Scriptorium?</b> Generate a complete sample world (<i>The Chronicles of Eldoria</i>) with pre-built lore, bestiary, magic systems, and starter chapters.")
        lbl_demo.set_line_wrap(True)
        demo_box.pack_start(lbl_demo, True, True, 0)

        btn_gen_demo = Gtk.Button(label="✨ Generate Demo Cosmos")
        btn_gen_demo.connect("clicked", self.on_generate_demo_clicked)
        demo_box.pack_start(btn_gen_demo, False, False, 0)

        box.pack_start(demo_frame, False, False, 0)

        return scrolled

    # -------------------------------------------------------------------------
    # TAB 2: Writing & Analytics
    # -------------------------------------------------------------------------
    def create_writing_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_border_width(18)
        scrolled.add(box)

        # Stats Cards Box
        stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        stats_box.set_homogeneous(True)

        self.card_total_words = self.create_stat_card("Total Words", "0", "Across all active volumes")
        self.card_chapters = self.create_stat_card("Chapters / Scenes", "0", "Structured draft files")
        self.card_pace = self.create_stat_card("Target Pace", "1,000 w/day", "Daily drafting goal")

        stats_box.pack_start(self.card_total_words, True, True, 0)
        stats_box.pack_start(self.card_chapters, True, True, 0)
        stats_box.pack_start(self.card_pace, True, True, 0)
        box.pack_start(stats_box, False, False, 0)

        # Volume Progress Section
        tree_frame = Gtk.Frame(label=" Manuscript Structure & Analytics ")
        tree_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        tree_vbox.set_border_width(10)
        tree_frame.add(tree_vbox)

        # Tree View for Manuscript Hierarchy
        self.manuscript_store = Gtk.TreeStore(str, str, str) # Item, Type, Wordcount
        self.manuscript_tree = Gtk.TreeView(model=self.manuscript_store)

        renderer_item = Gtk.CellRendererText()
        col_item = Gtk.TreeViewColumn("Document / Section", renderer_item, text=0)
        col_item.set_expand(True)
        self.manuscript_tree.append_column(col_item)

        renderer_type = Gtk.CellRendererText()
        col_type = Gtk.TreeViewColumn("Type", renderer_type, text=1)
        col_type.set_min_width(100)
        self.manuscript_tree.append_column(col_type)

        renderer_wc = Gtk.CellRendererText()
        col_wc = Gtk.TreeViewColumn("Word Count", renderer_wc, text=2)
        col_wc.set_min_width(100)
        self.manuscript_tree.append_column(col_wc)

        tree_scroll = Gtk.ScrolledWindow()
        tree_scroll.set_min_content_height(240)
        tree_scroll.add(self.manuscript_tree)
        tree_vbox.pack_start(tree_scroll, True, True, 0)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_refresh_stats = Gtk.Button(label="🔄 Recalculate Word Counts")
        btn_refresh_stats.connect("clicked", lambda b: self.refresh_manuscript_analytics())
        btn_box.pack_start(btn_refresh_stats, False, False, 0)

        btn_add_vol = Gtk.Button(label="📚 Add New Volume")
        btn_add_vol.get_style_context().add_class("suggested-action")
        btn_add_vol.connect("clicked", self.on_add_volume_clicked)
        btn_box.pack_start(btn_add_vol, False, False, 0)

        btn_open_drafting = Gtk.Button(label="✍️ Open in novelWriter")
        btn_open_drafting.connect("clicked", self.on_launch_novelwriter)
        btn_box.pack_start(btn_open_drafting, False, False, 0)

        tree_vbox.pack_start(btn_box, False, False, 0)
        box.pack_start(tree_frame, True, True, 0)

        return scrolled

    def create_stat_card(self, title, default_val, subtitle):
        frame = Gtk.Frame()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_border_width(12)
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
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_border_width(18)
        scrolled.add(box)

        # Meta Form
        meta_frame = Gtk.Frame(label=" Book Metadata & Output Configuration ")
        form_grid = Gtk.Grid()
        form_grid.set_border_width(14)
        form_grid.set_column_spacing(14)
        form_grid.set_row_spacing(10)
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

        box.pack_start(meta_frame, False, False, 0)

        # Actions & Output
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.btn_compile = Gtk.Button(label="🚀 Compile Book (PDF & EPUB)")
        self.btn_compile.get_style_context().add_class("suggested-action")
        self.btn_compile.connect("clicked", self.on_compile_clicked)
        action_box.pack_start(self.btn_compile, True, True, 0)

        self.btn_concordance = Gtk.Button(label="📖 Generate Concordance")
        self.btn_concordance.set_tooltip_text("Generate Dramatis Personae & Glossary back-matter from World Bible lore")
        self.btn_concordance.connect("clicked", self.on_generate_concordance_clicked)
        action_box.pack_start(self.btn_concordance, False, False, 0)

        self.btn_open_pdf = Gtk.Button(label="📄 Open PDF")
        self.btn_open_pdf.connect("clicked", self.on_open_pdf_clicked)
        self.btn_open_pdf.set_sensitive(False)
        action_box.pack_start(self.btn_open_pdf, False, False, 0)

        self.btn_open_epub = Gtk.Button(label="📱 Open EPUB")
        self.btn_open_epub.connect("clicked", self.on_open_epub_clicked)
        self.btn_open_epub.set_sensitive(False)
        action_box.pack_start(self.btn_open_epub, False, False, 0)

        box.pack_start(action_box, False, False, 0)

        # Compilation Log
        log_frame = Gtk.Frame(label=" Compilation Ledger ")
        log_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        log_box.set_border_width(10)
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
    # TAB 4: Vault Safety
    # -------------------------------------------------------------------------
    def create_safety_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_border_width(18)
        scrolled.add(box)

        # 1. Version Snapshot (Git) Card
        snap_frame = Gtk.Frame(label=" Version Milestone Snapshot (Git) ")
        snap_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        snap_box.set_border_width(12)
        snap_frame.add(snap_box)

        lbl_snap_info = Gtk.Label(label="Record an immutable version snapshot of your manuscript and lore notes.", xalign=0)
        snap_box.pack_start(lbl_snap_info, False, False, 0)

        snap_input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
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
        backup_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        backup_box.set_border_width(12)
        backup_frame.add(backup_box)

        lbl_b_info = Gtk.Label(label="Generate a standalone compressed .tar.gz archive with a SHA-256 cryptographic verification digest.", xalign=0)
        backup_box.pack_start(lbl_b_info, False, False, 0)

        backup_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_create_backup = Gtk.Button(label="📦 Create Standalone Backup Archive")
        btn_create_backup.connect("clicked", self.on_create_backup_clicked)
        backup_btns.pack_start(btn_create_backup, True, True, 0)

        btn_restore = Gtk.Button(label="♻️ Restore World from Archive...")
        btn_restore.connect("clicked", self.on_restore_clicked)
        backup_btns.pack_start(btn_restore, False, False, 0)

        backup_box.pack_start(backup_btns, False, False, 0)
        box.pack_start(backup_frame, False, False, 0)

        # 3. Snapshot History Log
        history_frame = Gtk.Frame(label=" Recent Milestone History ")
        hist_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        hist_box.set_border_width(10)
        history_frame.add(hist_box)

        self.history_store = Gtk.ListStore(str, str, str) # Hash, Date, Note
        self.history_tree = Gtk.TreeView(model=self.history_store)

        self.history_tree.append_column(Gtk.TreeViewColumn("Commit", Gtk.CellRendererText(), text=0))
        self.history_tree.append_column(Gtk.TreeViewColumn("Date & Time", Gtk.CellRendererText(), text=1))
        col_note = Gtk.TreeViewColumn("Snapshot Note", Gtk.CellRendererText(), text=2)
        col_note.set_expand(True)
        self.history_tree.append_column(col_note)

        hist_scroll = Gtk.ScrolledWindow()
        hist_scroll.set_min_content_height(180)
        hist_scroll.add(self.history_tree)
        hist_box.pack_start(hist_scroll, True, True, 0)

        box.pack_start(history_frame, True, True, 0)

        return scrolled

    # -------------------------------------------------------------------------
    # TAB 5: Doctor Diagnostics
    # -------------------------------------------------------------------------
    def create_doctor_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_border_width(18)
        scrolled.add(box)

        # Toolchain Badges Box
        badges_frame = Gtk.Frame(label=" System & Toolchain Status ")
        badges_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        badges_box.set_border_width(12)
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
        doc_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
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
        report_box.set_border_width(10)
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
    # Core Operations & Data Discovery
    # -------------------------------------------------------------------------
    def refresh_universe_and_worlds(self):
        self.discovered_universes = []
        self.discovered_worlds = []

        self.combo_universe.remove_all()
        self.combo_world.remove_all()

        # Discover Universes
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

        # Discover Worlds in current universe + standalone Worlds/
        self.refresh_worlds_for_universe()

    def refresh_worlds_for_universe(self):
        self.combo_world.remove_all()
        self.discovered_worlds = []

        # Check Universe Worlds
        if self.current_universe:
            u_worlds = UNIVERSES_DIR / self.current_universe / "Worlds"
            if u_worlds.is_dir():
                for w in sorted(u_worlds.iterdir()):
                    if w.is_dir() and not w.name.startswith("."):
                        self.discovered_worlds.append((w.name, str(w), f"[{self.current_universe}] {w.name}"))

        # Check Standalone Worlds
        if WORLDS_DIR.is_dir():
            for w in sorted(WORLDS_DIR.iterdir()):
                if w.is_dir() and not w.name.startswith("."):
                    self.discovered_worlds.append((w.name, str(w), f"[Standalone] {w.name}"))

        for wname, wpath, label in self.discovered_worlds:
            self.combo_world.append(wpath, label)

        if self.discovered_worlds:
            self.combo_world.set_active(0)
            self.current_world_path = self.discovered_worlds[0][1]
        else:
            self.current_world_path = None
            self.update_active_world_display()

    def on_universe_changed(self, combo):
        active_id = combo.get_active_id()
        if active_id and active_id != self.current_universe:
            self.current_universe = active_id
            self.refresh_worlds_for_universe()

    def on_world_changed(self, combo):
        active_id = combo.get_active_id()
        if active_id:
            self.current_world_path = active_id
            self.update_active_world_display()

    def update_active_world_display(self):
        if self.current_world_path and Path(self.current_world_path).is_dir():
            wpath = Path(self.current_world_path)
            wname = wpath.name
            self.lbl_cosmos_heading.set_markup(f"<span size='large' weight='bold'>World: {wname}</span>")
            self.lbl_cosmos_path.set_text(str(wpath))
            self.entry_pub_title.set_text(wname)
            self.refresh_volume_options()
            self.refresh_manuscript_analytics()
            self.refresh_snapshot_history()
            self.update_toolchain_badges()
            self.set_status(f"Active World: {wname}")
        else:
            self.lbl_cosmos_heading.set_markup("<span size='large' weight='bold'>No World Selected</span>")
            self.lbl_cosmos_path.set_text("Create a new world to begin writing.")
            self.set_status("No world selected.")

    def refresh_volume_options(self):
        self.combo_pub_volume.remove_all()
        if not self.current_world_path:
            return
        ms_dir = Path(self.current_world_path) / "01-Manuscript"
        books = []
        if ms_dir.is_dir():
            for b in sorted(ms_dir.glob("Book-*")):
                if b.is_dir():
                    books.append(b.name)

        if books:
            for b in books:
                self.combo_pub_volume.append(b, f"Volume: {b}")
            if len(books) > 1:
                self.combo_pub_volume.append("all", "All Books (Complete Omnibus)")
            self.combo_pub_volume.set_active(0)
        else:
            self.combo_pub_volume.append("Book-01", "Volume: Book-01")
            self.combo_pub_volume.set_active(0)

    def refresh_manuscript_analytics(self):
        self.manuscript_store.clear()
        if not self.current_world_path:
            self.card_total_words.val_label.set_text("0")
            self.card_chapters.val_label.set_text("0")
            return

        ms_dir = Path(self.current_world_path) / "01-Manuscript"
        total_words = 0
        total_chapters = 0

        if ms_dir.is_dir():
            for book_dir in sorted(ms_dir.glob("Book-*")):
                if book_dir.is_dir():
                    book_words = 0
                    b_iter = self.manuscript_store.append(None, [book_dir.name, "Volume", "Calculating..."])
                    for act_dir in sorted(book_dir.iterdir()):
                        if act_dir.is_dir():
                            act_words = 0
                            a_iter = self.manuscript_store.append(b_iter, [act_dir.name, "Act / Section", ""])
                            for ch_file in sorted(act_dir.glob("*.md")):
                                if ch_file.is_file():
                                    try:
                                        content = ch_file.read_text(encoding="utf-8", errors="ignore")
                                        # strip tags
                                        lines = [l for l in content.splitlines() if not l.startswith("@") and not l.startswith("%")]
                                        wc = len(" ".join(lines).split())
                                        act_words += wc
                                        total_chapters += 1
                                        self.manuscript_store.append(a_iter, [ch_file.name, "Scene / Chapter", f"{wc:,} words"])
                                    except Exception:
                                        pass
                            self.manuscript_store.set_value(a_iter, 2, f"{act_words:,} words")
                            book_words += act_words
                    self.manuscript_store.set_value(b_iter, 2, f"{book_words:,} words")
                    total_words += book_words

        self.card_total_words.val_label.set_text(f"{total_words:,}")
        self.card_chapters.val_label.set_text(str(total_chapters))
        self.manuscript_tree.expand_all()

    def refresh_snapshot_history(self):
        self.history_store.clear()
        if not self.current_world_path:
            return
        wpath = Path(self.current_world_path)
        if (wpath / ".git").is_dir():
            try:
                res = subprocess.run(
                    ["git", "-C", str(wpath), "log", "-n", "15", "--pretty=format:%h|%ad|%s", "--date=short"],
                    capture_output=True, text=True, check=True
                )
                for line in res.stdout.splitlines():
                    parts = line.split("|", 2)
                    if len(parts) == 3:
                        self.history_store.append([parts[0], parts[1], parts[2]])
            except Exception:
                pass

    def update_toolchain_badges(self):
        tools = [
            ("git", self.lbl_tool_git),
            ("pandoc", self.lbl_tool_pandoc),
            ("typst", self.lbl_tool_typst),
            ("python3", self.lbl_tool_python),
        ]
        for cmd, badge in tools:
            path = subprocess.run(["which", cmd], capture_output=True, text=True).stdout.strip()
            if path:
                badge.status_label.set_markup("<span color='#2e7d32'><b>✓ Installed</b></span>")
            else:
                badge.status_label.set_markup("<span color='#d32f2f'><b>✗ Missing</b></span>")

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
                    self.refresh_universe_and_worlds()

                threading.Thread(
                    target=self._run_async_command,
                    args=(cmd, f"Universe '{name}' created successfully!", on_universe_created),
                ).start()
        dialog.destroy()

    def on_new_world_clicked(self, btn):
        dialog = Gtk.Dialog(title="New World Project", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        lbl = Gtk.Label(label="Enter title for your new novel/world (e.g., 'Eldoria'):")
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
                self.set_status(f"Scaffolding world '{wname}'...")

                def on_world_created():
                    self.refresh_universe_and_worlds()
                    # Select the newly created world
                    for name, path, label in self.discovered_worlds:
                        if name == wname:
                            self.combo_world.set_active_id(path)
                            break

                threading.Thread(
                    target=self._run_async_command,
                    args=(cmd, f"World '{wname}' created successfully!", on_world_created),
                ).start()
        dialog.destroy()

    def on_quick_snapshot_clicked(self, btn):
        if not self.current_world_path:
            self.show_error("Please select an active world first.")
            return

        dialog = Gtk.Dialog(title="Quick Version Snapshot", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        lbl = Gtk.Label(label="Describe your progress (e.g., 'Finished Act 1 outline'):")
        box.pack_start(lbl, False, False, 0)

        entry = Gtk.Entry()
        entry.set_text(f"Snapshot: {subprocess.run(['date', '+%Y-%m-%d %H:%M'], capture_output=True, text=True).stdout.strip()}")
        box.pack_start(entry, False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            note = entry.get_text().strip()
            cmd = ["bash", str(PROJECT_ROOT / "scripts" / "save_snapshot.sh"), "--world", self.current_world_path, "--note", note]
            self.set_status("Saving version snapshot...")
            threading.Thread(target=self._run_async_command, args=(cmd, "Snapshot recorded successfully!")).start()
        dialog.destroy()

    def on_save_snapshot_clicked(self, btn):
        if not self.current_world_path:
            self.show_error("Please select an active world first.")
            return
        note = self.entry_snap_note.get_text().strip()
        if not note:
            note = f"Snapshot: {subprocess.run(['date', '+%Y-%m-%d %H:%M'], capture_output=True, text=True).stdout.strip()}"
        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "save_snapshot.sh"), "--world", self.current_world_path, "--note", note]
        self.set_status("Saving version milestone snapshot...")
        threading.Thread(target=self._run_async_command, args=(cmd, "Snapshot recorded successfully!", self.refresh_snapshot_history)).start()

    def on_create_backup_clicked(self, btn):
        if not self.current_world_path:
            self.show_error("Please select an active world first.")
            return
        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "backup_world.sh"), "--world", self.current_world_path]
        self.set_status("Creating standalone verified backup archive...")
        threading.Thread(target=self._run_async_command, args=(cmd, "Backup archive created with SHA-256 digest!")).start()

    def on_restore_clicked(self, btn):
        dialog = Gtk.FileChooserDialog(
            title="Select Scriptorium Backup Archive",
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
            box.pack_start(Gtk.Label(label="Enter name for restored world folder:"), False, False, 6)
            name_entry = Gtk.Entry()
            name_entry.set_text("Restored-World")
            box.pack_start(name_entry, False, False, 6)
            name_dialog.show_all()

            if name_dialog.run() == Gtk.ResponseType.OK:
                target_name = name_entry.get_text().strip()
                cmd = ["bash", str(PROJECT_ROOT / "scripts" / "restore_world.sh"), "--archive", archive_path, "--target", target_name]
                if self.current_universe:
                    cmd.extend(["--universe", self.current_universe])
                self.set_status("Restoring world from archive...")
                threading.Thread(target=self._run_async_command, args=(cmd, "World restored and verified successfully!", self.refresh_universe_and_worlds)).start()
            name_dialog.destroy()
        else:
            dialog.destroy()

    def on_compile_clicked(self, btn):
        if not self.current_world_path:
            self.show_error("Please select an active world first.")
            return

        title = self.entry_pub_title.get_text().strip() or "Book Title"
        author = self.entry_pub_author.get_text().strip() or "Author Name"
        volume = self.combo_pub_volume.get_active_id() or "Book-01"
        paper_size = self.combo_paper_size.get_active_id() or "us-trade"

        cmd = [
            "bash", str(PROJECT_ROOT / "scripts" / "export_book.sh"),
            self.current_world_path,
            "--title", title,
            "--author", author,
            "--book", volume,
            "--paper-size", paper_size
        ]

        self.btn_compile.set_sensitive(False)
        self.pub_log_buffer.set_text(f"Starting compilation for '{title}' [{volume}]...\n")
        self.set_status("Compiling print PDF and EPUB...")

        def _worker():
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                GLib.idle_add(self._append_log, self.pub_log_buffer, line)
            proc.wait()
            GLib.idle_add(self._on_compile_done, proc.returncode)

        threading.Thread(target=_worker).start()

    def _append_log(self, buffer_obj, text):
        end_iter = buffer_obj.get_end_iter()
        buffer_obj.insert(end_iter, text)

    def _on_compile_done(self, returncode):
        self.btn_compile.set_sensitive(True)
        if returncode == 0:
            self.set_status("Book compiled successfully!")
            self.btn_open_pdf.set_sensitive(True)
            self.btn_open_epub.set_sensitive(True)
        else:
            self.set_status("Compilation finished with warnings/errors.")

    def on_open_pdf_clicked(self, btn):
        if self.current_world_path:
            pub_dir = Path(self.current_world_path) / "04-Publishing"
            pdfs = list(pub_dir.glob("*.pdf"))
            if pdfs:
                latest = max(pdfs, key=os.path.getmtime)
                subprocess.Popen(["xdg-open", str(latest)])

    def on_open_epub_clicked(self, btn):
        if self.current_world_path:
            pub_dir = Path(self.current_world_path) / "04-Publishing"
            epubs = list(pub_dir.glob("*.epub"))
            if epubs:
                latest = max(epubs, key=os.path.getmtime)
                subprocess.Popen(["xdg-open", str(latest)])

    def on_add_volume_clicked(self, btn):
        if not self.current_world_path:
            self.show_error("Please select an active world first.")
            return

        wpath = Path(self.current_world_path)
        ms_dir = wpath / "01-Manuscript"
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

        lbl = Gtk.Label(label=f"Enter volume name for '{wpath.name}':")
        box.pack_start(lbl, False, False, 0)

        entry = Gtk.Entry()
        entry.set_text(default_vol)
        box.pack_start(entry, False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            vol_name = entry.get_text().strip()
            if vol_name:
                cmd = ["bash", str(PROJECT_ROOT / "scripts" / "add_book.sh"), self.current_world_path, vol_name]
                self.set_status(f"Scaffolding volume '{vol_name}'...")
                threading.Thread(target=self._run_async_command, args=(cmd, f"Volume '{vol_name}' created successfully!", self.refresh_after_add_volume)).start()
        dialog.destroy()

    def refresh_after_add_volume(self):
        self.refresh_volume_options()
        self.refresh_manuscript_analytics()

    def on_generate_concordance_clicked(self, btn):
        if not self.current_world_path:
            self.show_error("Please select an active world first.")
            return

        volume = self.combo_pub_volume.get_active_id() or "all"
        cmd = [
            "bash", str(PROJECT_ROOT / "scripts" / "generate_concordance.sh"),
            self.current_world_path,
            "--book", volume
        ]
        self.set_status(f"Generating back-matter concordance for volume '{volume}'...")
        self.pub_log_buffer.set_text(f"Starting Concordance & Dramatis Personae generation [{volume}]...\n")

        def _worker():
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                GLib.idle_add(self._append_log, self.pub_log_buffer, line)
            proc.wait()
            if proc.returncode == 0:
                GLib.idle_add(self.set_status, "Concordance and Dramatis Personae generated successfully!")
                GLib.idle_add(self.refresh_manuscript_analytics)
            else:
                GLib.idle_add(self.set_status, "Concordance generation encountered warnings/errors.")

        threading.Thread(target=_worker).start()

    def run_diagnostics(self):
        if not self.current_world_path:
            self.show_error("Please select an active world first.")
            return
        self.doc_log_buffer.set_text("Running Scriptorium & World Doctor diagnostics...\n")
        self.set_status("Running diagnostics...")

        def _worker():
            cmd1 = ["bash", str(PROJECT_ROOT / "scripts" / "scriptorium_doctor.sh"), "--world", self.current_world_path]
            res1 = subprocess.run(cmd1, capture_output=True, text=True)
            GLib.idle_add(self._append_log, self.doc_log_buffer, res1.stdout + "\n" + res1.stderr)

            cmd2 = ["bash", str(PROJECT_ROOT / "scripts" / "world_doctor.sh"), self.current_world_path]
            res2 = subprocess.run(cmd2, capture_output=True, text=True)
            GLib.idle_add(self._append_log, self.doc_log_buffer, res2.stdout + "\n" + res2.stderr)
            GLib.idle_add(self.set_status, "Diagnostics complete.")

        threading.Thread(target=_worker).start()

    def run_verify_harness(self):
        self.doc_log_buffer.set_text("Running full 7-stage verification suite...\n")
        self.set_status("Running verification harness...")

        def _worker():
            cmd = ["bash", str(PROJECT_ROOT / "scripts" / "verify.sh")]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                GLib.idle_add(self._append_log, self.doc_log_buffer, line)
            proc.wait()
            GLib.idle_add(self.set_status, "Verification run complete.")

        threading.Thread(target=_worker).start()

    def on_generate_demo_clicked(self, btn):
        demo_uni = "Cosmere-Prime"
        demo_world = "Chronicles-of-Eldoria"
        self.set_status("Scaffolding demo cosmos...")

        def _worker():
            subprocess.run(["bash", str(PROJECT_ROOT / "scripts" / "init_universe.sh"), demo_uni], capture_output=True)
            subprocess.run(["bash", str(PROJECT_ROOT / "scripts" / "init_world.sh"), demo_world, "--universe", demo_uni], capture_output=True)
            GLib.idle_add(self.refresh_universe_and_worlds)
            GLib.idle_add(self.set_status, "Demo Cosmos 'The Chronicles of Eldoria' created successfully!")

        threading.Thread(target=_worker).start()

    def _is_flatpak_installed(self, app_id):
        try:
            res = subprocess.run(["flatpak", "info", app_id], capture_output=True)
            return res.returncode == 0
        except Exception:
            return False

    def on_launch_obsidian(self, btn):
        if self.current_world_path:
            bible = Path(self.current_world_path) / "00-World-Bible"
            if self._is_flatpak_installed("md.obsidian.Obsidian"):
                subprocess.Popen(["flatpak", "run", "md.obsidian.Obsidian", str(bible)])
            elif subprocess.run(["which", "obsidian"], capture_output=True).stdout:
                subprocess.Popen(["obsidian", str(bible)])
            else:
                subprocess.Popen(["xdg-open", str(bible)])

    def on_launch_novelwriter(self, btn):
        if self.current_world_path:
            nw_proj = Path(self.current_world_path) / "01-Manuscript" / "nwProject.nwx"
            target = str(nw_proj) if nw_proj.is_file() else str(Path(self.current_world_path) / "01-Manuscript")
            if self._is_flatpak_installed("io.gitlab.novelwriter.novelWriter"):
                subprocess.Popen(["flatpak", "run", "io.gitlab.novelwriter.novelWriter", target])
            elif subprocess.run(["which", "novelwriter"], capture_output=True).stdout:
                subprocess.Popen(["novelwriter", target])
            else:
                subprocess.Popen(["xdg-open", str(Path(self.current_world_path) / "01-Manuscript")])

    def on_launch_focuswriter(self, btn):
        if self.current_world_path:
            ms = Path(self.current_world_path) / "01-Manuscript" / "Book-01"
            if subprocess.run(["which", "focuswriter"], capture_output=True).stdout:
                subprocess.Popen(["focuswriter", str(ms)])
            else:
                subprocess.Popen(["xdg-open", str(ms)])

    def on_launch_libreoffice(self, btn):
        if subprocess.run(["which", "libreoffice"], capture_output=True).stdout:
            subprocess.Popen(["libreoffice", "--writer"])
        else:
            subprocess.Popen(["xdg-open", str(HOME_DIR)])

    def on_launch_calibre(self, btn):
        if self._is_flatpak_installed("com.calibre_ebook.calibre"):
            subprocess.Popen(["flatpak", "run", "com.calibre_ebook.calibre"])
        elif self._is_flatpak_installed("com.calibredesk.calibre"):
            subprocess.Popen(["flatpak", "run", "com.calibredesk.calibre"])
        elif subprocess.run(["which", "calibre"], capture_output=True).stdout:
            subprocess.Popen(["calibre"])
        else:
            subprocess.Popen(["xdg-open", str(HOME_DIR)])

    def on_open_folder_clicked(self, btn):
        if self.current_world_path:
            subprocess.Popen(["xdg-open", str(self.current_world_path)])

    def on_open_manual_clicked(self, btn):
        manual_path = PROJECT_ROOT / "docs" / "AUTHOR_MANUAL.md"
        if manual_path.is_file():
            subprocess.Popen(["xdg-open", str(manual_path)])
        else:
            self.show_error("Author's Field Manual not found.")

    def check_first_run(self):
        flag_file = HOME_DIR / ".config" / "scriptorium" / "first_run_done"
        if not flag_file.is_file() and not self.discovered_worlds:
            GLib.idle_add(self.show_welcome_dialog, flag_file)

    def show_welcome_dialog(self, flag_file):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Welcome to Scriptorium!"
        )
        dialog.format_secondary_text(
            "Scriptorium is your private, local-first writing and worldbuilding studio.\n\n"
            "• Use Tab 1 (Cosmos) to switch projects or generate the sample Eldoria world.\n"
            "• Use Tab 3 (Publishing) to compile trade-quality print PDFs and EPUBs in 1 click.\n"
            "• Click '📖 Field Manual' in the top right anytime for guides.\n\n"
            "Happy Writing!"
        )
        dialog.run()
        dialog.destroy()
        flag_file.parent.mkdir(parents=True, exist_ok=True)
        flag_file.touch()

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

    def _run_async_command(self, cmd, success_msg, callback=None):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            GLib.idle_add(self.set_status, success_msg)
        else:
            GLib.idle_add(self.set_status, f"Error: {res.stderr.strip() or 'Command failed'}")
        if callback:
            GLib.idle_add(callback)

def main():
    if not HAS_GTK:
        print("[!] PyGObject / GTK 3 is not installed in the current Python environment.", file=sys.stderr)
        print("[i] Falling back to Zenity desktop control dashboard...", file=sys.stderr)
        sys.exit(2)

    app = ScriptoriumApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
