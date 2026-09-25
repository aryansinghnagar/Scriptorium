#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 Main Window & Application Controller (scripts/lib/ui_gtk3/window.py)
====================================================================================
Modular desktop window coordinating 6 workflow studios, project selectors,
accelerator keymaps, and lifecycle event orchestration.
"""

import logging
import os
import re
import shutil
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from lib.ui_gtk3.cli_bridge import (
    build_manuscript_docx,
    clear_backup_dest,
    get_active_docx_preset_name,
    get_backup_dest,
    get_docx_config,
    list_docx_presets,
    open_in_word_processor,
    set_backup_dest,
    set_docx_option,
    set_docx_preset,
    sync_manuscript_docx,
)
from lib.ui_gtk3.common import (
    HAS_GTK,
    HOME_DIR,
    MANUSCRIPTS_DIR,
    PROJECT_ROOT,
    UNIVERSES_DIR,
    WORLDS_DIR,
    DialogHelpersMixin,
    Gdk,
    GLib,
    Gtk,
    _cached_which,
    setup_styles,
    toggle_high_contrast,
)
from lib.ui_gtk3.dialogs import SpeculativeDialogsMixin
from lib.ui_gtk3.studios.cosmos import CosmosStudioMixin
from lib.ui_gtk3.studios.diagnostics import DiagnosticsStudioMixin
from lib.ui_gtk3.studios.drafting import DraftingStudioMixin
from lib.ui_gtk3.studios.publishing import PublishingStudioMixin
from lib.ui_gtk3.studios.safety import SafetyStudioMixin
from lib.ui_gtk3.studios.speculative import SpeculativeStudioMixin
from lib.ui_gtk3.workers import WorkerMixin

logger = logging.getLogger("arcanum.ui_gtk3.window")


class ArcanumApp(
    Gtk.Window,
    WorkerMixin,
    DialogHelpersMixin,
    CosmosStudioMixin,
    DraftingStudioMixin,
    SpeculativeStudioMixin,
    PublishingStudioMixin,
    SafetyStudioMixin,
    DiagnosticsStudioMixin,
    SpeculativeDialogsMixin,
):
    """Main Ars Arcanum GTK 3 desktop application window."""

    def __init__(self, active_tab: str | None = None):
        if HAS_GTK and hasattr(Gtk.Window, "__init__"):
            super().__init__(title="Ars Arcanum — Sovereign Author & Worldbuilder Studio")
            self.set_default_size(1080, 740)
            if hasattr(Gtk, "WindowPosition"):
                self.set_position(Gtk.WindowPosition.CENTER)

        # Apply basic modern styling
        self.setup_styles()

        self.current_universe = None
        self.current_world_path = None
        self.current_manuscript_path = None
        self.current_selected_scene_file = None

        self.discovered_universes: list[str] = []
        self.discovered_worlds: list[tuple[str, str, str]] = []
        self.discovered_manuscripts: list[tuple[str, str, str]] = []

        self.combo_draft_vol = None
        self.combo_draft_list = None
        self.combo_diff_a = None
        self.combo_diff_b = None
        self.lbl_secure_dest = None

        self._world_lore_counts: dict = {}
        self._dialog_cache: dict = {}
        self._git_history_cache: dict = {}
        self._pulse_timer_id = None
        self._first_run_wizard_shown = False
        self._high_contrast_active = False

        if not HAS_GTK:
            return

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
        if hasattr(snap_btn, "get_style_context"):
            snap_btn.get_style_context().add_class("suggested-action")
        snap_btn.set_tooltip_text("Record a 1-click Git version milestone (Ctrl+S)")
        snap_btn.connect("clicked", self.on_quick_snapshot_clicked)
        header.pack_end(snap_btn)

        # Accessibility High-Contrast Toggle Button
        contrast_btn = Gtk.Button(label="👁️ High Contrast")
        contrast_btn.set_tooltip_text("Toggle high-contrast accessibility theme (Ctrl+H)")
        contrast_btn.connect("clicked", self.on_toggle_high_contrast_clicked)
        header.pack_end(contrast_btn)

        # Manual / Help button
        help_btn = Gtk.Button(label="📖 Field Manual")
        help_btn.set_tooltip_text("Open the Ars Arcanum Author's Field Manual (F1)")
        help_btn.connect("clicked", self.on_open_manual_clicked)
        header.pack_end(help_btn)

        # Top Project Selector Bar
        selector_bar = self.create_selector_bar()
        main_box.pack_start(selector_bar, False, False, 0)

        # 6-Studio Workspace Notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        main_box.pack_start(self.notebook, True, True, 0)

        # Create the 6 primary workflow studios
        self.tab_cosmos = self.create_cosmos_tab()
        self.tab_manuscript = self.create_manuscript_tab()
        self.tab_speculative = self.create_speculative_tab()
        self.tab_publishing = self.create_publishing_tab()
        self.tab_safety = self.create_safety_tab()
        self.tab_doctor = self.create_doctor_tab()

        self.notebook.append_page(self.tab_cosmos, Gtk.Label(label="🪐 Cosmos & Worlds"))
        self.notebook.append_page(self.tab_manuscript, Gtk.Label(label="✍️ Manuscripts & Drafting"))
        self.notebook.append_page(self.tab_speculative, Gtk.Label(label="🔮 Speculative Studio"))
        self.notebook.append_page(self.tab_publishing, Gtk.Label(label="📚 Publishing & Exports"))
        self.notebook.append_page(self.tab_safety, Gtk.Label(label="🔒 Snapshots & Backups"))
        self.notebook.append_page(self.tab_doctor, Gtk.Label(label="🩺 Diagnostics & Doctor"))

        if active_tab:
            tab_clean = active_tab.lower().strip()
            tab_map = {
                "cosmos": 0, "universe": 0, "universes": 0, "world": 0, "worlds": 0,
                "drafting": 1, "manuscript": 1, "manuscripts": 1, "novel": 1, "writing": 1, "write": 1,
                "comparator": 1, "diff": 1, "compare": 1, "redline": 1,
                "worldbuilding": 2, "speculative": 2, "engines": 2, "lore": 2, "magic": 2,
                "publishing": 3, "typesetting": 3, "export": 3, "publish": 3,
                "safety": 4, "backups": 4, "snapshots": 4, "backup": 4, "snapshot": 4, "git": 4,
                "doctor": 5, "diagnostics": 5, "health": 5, "check": 5
            }
            if tab_clean in tab_map:
                self.notebook.set_current_page(tab_map[tab_clean])

        # Bottom bar with status + pulse progress bar for long ops
        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.statusbar = Gtk.Statusbar()
        self.status_context = self.statusbar.get_context_id("main")
        bottom_bar.pack_start(self.statusbar, True, True, 0)

        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.set_pulse_step(0.05)
        self._progress_bar.set_no_show_all(True)
        bottom_bar.pack_start(self._progress_bar, False, False, 0)
        main_box.pack_start(bottom_bar, False, False, 0)

        # Setup keyboard accelerators
        self.setup_accelerators()

        # Run discovery off GTK main thread so startup is instant
        self._start_worker(self._async_refresh_all_discovery)
        self.check_first_run()

    def setup_styles(self, high_contrast: bool = False):
        setup_styles(high_contrast=high_contrast)

    def setup_accelerators(self):
        """Installs standard keyboard shortcuts (Ctrl+N, Ctrl+S, Ctrl+E, Ctrl+B, F1, Ctrl+H, Ctrl+R)."""
        if not HAS_GTK or Gdk is None:
            return
        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)

        # Helper to bind key combinations
        def _add_accel(key_val, mod_mask, callback):
            accel_group.connect(key_val, mod_mask, Gtk.AccelFlags.VISIBLE, lambda *args: callback(None))

        # Ctrl+N -> New Manuscript
        _add_accel(Gdk.KEY_n, Gdk.ModifierType.CONTROL_MASK, self.on_new_manuscript_clicked)
        # Ctrl+S -> Quick Snapshot
        _add_accel(Gdk.KEY_s, Gdk.ModifierType.CONTROL_MASK, self.on_quick_snapshot_clicked)
        # Ctrl+E -> Compile Book
        _add_accel(Gdk.KEY_e, Gdk.ModifierType.CONTROL_MASK, self.on_compile_clicked)
        # Ctrl+B -> Standalone Backup
        _add_accel(Gdk.KEY_b, Gdk.ModifierType.CONTROL_MASK, self.on_create_backup_clicked)
        # F1 -> Author's Field Manual
        _add_accel(Gdk.KEY_F1, Gdk.ModifierType(0), self.on_open_manual_clicked)
        # Ctrl+H -> High Contrast Mode Toggle
        _add_accel(Gdk.KEY_h, Gdk.ModifierType.CONTROL_MASK, self.on_toggle_high_contrast_clicked)
        # Ctrl+R -> Refresh Discovery
        _add_accel(Gdk.KEY_r, Gdk.ModifierType.CONTROL_MASK, lambda b: self.refresh_all_discovery())

    def on_toggle_high_contrast_clicked(self, btn=None):
        new_state = toggle_high_contrast()
        self._high_contrast_active = new_state
        self.set_status(f"High Contrast Mode {'Enabled' if new_state else 'Disabled'}")

    def set_status(self, message):
        if not hasattr(self, "statusbar") or self.statusbar is None:
            return
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
        btn_refresh.set_tooltip_text("Refresh discovered universes, worlds, and manuscripts (Ctrl+R)")
        btn_refresh.connect("clicked", lambda b: self.refresh_all_discovery())
        bar.pack_start(btn_refresh, False, False, 0)

        return bar

    # -------------------------------------------------------------------------
    # Discovery & State Synchronization
    # -------------------------------------------------------------------------
    def _async_refresh_all_discovery(self) -> None:
        """Run full discovery off the GTK main thread."""
        discovered_universes: list[str] = []
        if UNIVERSES_DIR.is_dir():
            for p in sorted(UNIVERSES_DIR.iterdir()):
                if p.is_dir() and not p.name.startswith("."):
                    discovered_universes.append(p.name)

        first_universe = discovered_universes[0] if discovered_universes else "Default-Universe"
        discovered_worlds: list[tuple[str, str, str]] = []
        u_dir = UNIVERSES_DIR / first_universe
        if u_dir.is_dir():
            for w in sorted(u_dir.iterdir()):
                if w.is_dir() and not w.name.startswith(".") and w.name not in ("Worlds", ".git"):
                    discovered_worlds.append((w.name, str(w), f"[{first_universe}] {w.name}"))
            u_worlds = u_dir / "Worlds"
            if u_worlds.is_dir():
                for w in sorted(u_worlds.iterdir()):
                    if w.is_dir() and not w.name.startswith("."):
                        discovered_worlds.append((w.name, str(w), f"[{first_universe}] {w.name}"))
        if WORLDS_DIR.is_dir():
            for w in sorted(WORLDS_DIR.iterdir()):
                if w.is_dir() and not w.name.startswith("."):
                    discovered_worlds.append((w.name, str(w), f"[Legacy] {w.name}"))

        discovered_manuscripts: list[tuple[str, str, str]] = []
        if MANUSCRIPTS_DIR.is_dir():
            for m in sorted(MANUSCRIPTS_DIR.iterdir()):
                if m.is_dir() and not m.name.startswith("."):
                    discovered_manuscripts.append((m.name, str(m), m.name))

        for tool in ("git", "pandoc", "typst", "python3"):
            _cached_which(tool)

        def _apply():
            self.discovered_universes = discovered_universes
            self.combo_universe.remove_all()
            if not discovered_universes:
                self.combo_universe.append("Default-Universe", "Default-Universe")
                self.current_universe = "Default-Universe"
            else:
                for name in discovered_universes:
                    self.combo_universe.append(name, name)
                if not self.current_universe or self.current_universe not in discovered_universes:
                    self.current_universe = discovered_universes[0]
                self.combo_universe.set_active_id(self.current_universe)

            self.discovered_worlds = discovered_worlds
            self.combo_world.remove_all()
            for _wname, wpath, label in discovered_worlds:
                self.combo_world.append(wpath, label)
            if discovered_worlds:
                self.combo_world.set_active(0)
                self.current_world_path = discovered_worlds[0][1]
            else:
                self.current_world_path = None

            self.discovered_manuscripts = discovered_manuscripts
            self.combo_manuscript.remove_all()
            for _mname, mpath, label in discovered_manuscripts:
                self.combo_manuscript.append(mpath, label)
            if discovered_manuscripts:
                self.combo_manuscript.set_active(0)
                self.current_manuscript_path = discovered_manuscripts[0][1]
            else:
                self.current_manuscript_path = None

            self.update_active_world_display()
            self.update_active_manuscript_display()
            self.update_toolchain_badges()
            self.check_first_run_wizard()

        if HAS_GTK and GLib is not None:
            GLib.idle_add(_apply)

    def refresh_all_discovery(self):
        """Synchronous discovery — used by explicit refresh button."""
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
                u_worlds = u_dir / "Worlds"
                if u_worlds.is_dir():
                    for w in sorted(u_worlds.iterdir()):
                        if w.is_dir() and not w.name.startswith("."):
                            self.discovered_worlds.append((w.name, str(w), f"[{self.current_universe}] {w.name}"))

        if WORLDS_DIR.is_dir():
            for w in sorted(WORLDS_DIR.iterdir()):
                if w.is_dir() and not w.name.startswith("."):
                    self.discovered_worlds.append((w.name, str(w), f"[Legacy] {w.name}"))

        for _wname, wpath, label in self.discovered_worlds:
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

        for _mname, mpath, label in self.discovered_manuscripts:
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
            if hasattr(self, "lbl_cosmos_heading"):
                self.lbl_cosmos_heading.set_markup(f"<span size='large' weight='bold'>World Lore Vault: {wname}</span>")
                self.lbl_cosmos_path.set_text(str(wpath))
                self.lbl_lore_stats.set_text("Counting lore entities…")
            self.set_status(f"Active World: {wname}")

            def _count_lore():
                try:
                    vault_mtime = wpath.stat().st_mtime
                except OSError:
                    vault_mtime = 0.0
                cache_key = (str(wpath), vault_mtime)
                if cache_key in self._world_lore_counts:
                    counts = self._world_lore_counts[cache_key]
                else:
                    counts = {}
                    for folder in ("Characters", "Locations", "Factions", "Magic-Technology",
                                   "Bestiary", "Artifacts", "Cosmology", "History", "Languages"):
                        fdir = wpath / folder
                        if not fdir.is_dir() and (wpath / "00-World-Bible" / folder).is_dir():
                            fdir = wpath / "00-World-Bible" / folder
                        if fdir.is_dir():
                            c = len([f for f in fdir.rglob("*.md")
                                     if not f.name.startswith(".") and "Template" not in f.name])
                            counts[folder] = c
                        else:
                            counts[folder] = 0
                    self._world_lore_counts[cache_key] = counts

                stats_str = "  •  ".join([f"<b>{k}</b>: {v}" for k, v in counts.items()])
                if HAS_GTK and GLib is not None and hasattr(self, "lbl_lore_stats"):
                    GLib.idle_add(
                        self.lbl_lore_stats.set_markup,
                        f"<b>Registered Lore Entities:</b>\n{stats_str}"
                    )

            self._start_worker(_count_lore)
        else:
            if hasattr(self, "lbl_cosmos_heading"):
                self.lbl_cosmos_heading.set_markup("<span size='large' weight='bold'>No World Lore Selected</span>")
                self.lbl_cosmos_path.set_text("Create a new world lore vault to begin worldbuilding.")
                self.lbl_lore_stats.set_text("No world lore vault active.")

    def update_active_manuscript_display(self):
        if self.current_manuscript_path and Path(self.current_manuscript_path).is_dir():
            mpath = Path(self.current_manuscript_path)
            mname = mpath.name
            if hasattr(self, "entry_pub_title"):
                self.entry_pub_title.set_text(mname)
            self.refresh_volume_options()
            self.refresh_draft_selectors()
            self.refresh_manuscript_analytics()
            self.refresh_snapshot_history()
            self.update_secure_dest_display()
            self.set_status(f"Active Manuscript: {mname}")
        else:
            if hasattr(self, "card_total_words") and hasattr(self.card_total_words, "val_label"):
                self.card_total_words.val_label.set_text("0")
                self.card_chapters.val_label.set_text("0")
            if hasattr(self, "manuscript_store"):
                self.manuscript_store.clear()
            self.refresh_draft_selectors()
            self.update_secure_dest_display()

    def refresh_volume_options(self):
        if not hasattr(self, "combo_pub_volume") or self.combo_pub_volume is None:
            return
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
        if not hasattr(self, "manuscript_store"):
            return
        self.manuscript_store.clear()
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            return

        if hasattr(self, "card_total_words") and hasattr(self.card_total_words, "val_label"):
            self.card_total_words.val_label.set_text("…")
            self.card_chapters.val_label.set_text("…")
        if HAS_GTK and GLib is not None:
            GLib.idle_add(self._show_progress)

        try:
            from lib.cache import count_words as _canonical_count
        except Exception:
            _FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

            def _canonical_count(text: str) -> int:
                clean = _FM.sub("", text)
                clean = re.sub(r"```.*?```", "", clean, flags=re.DOTALL)
                kept = [ln for ln in clean.splitlines()
                        if ln.strip() and not (ln.strip().startswith("@") and re.match(r"^@[A-Za-z0-9_-]+:", ln.strip())) and not ln.strip().startswith("%")]
                return len(re.findall(r"\b\w+\b", "\n".join(kept), flags=re.UNICODE))

        tpath = Path(target)
        ms_dir = tpath / "01-Manuscript" if (tpath / "01-Manuscript").is_dir() else tpath

        def _worker():
            rows: list[tuple] = []
            total_words = 0
            total_chapters = 0

            if ms_dir.is_dir():
                for book_dir in sorted(ms_dir.glob("Book-*")):
                    if not book_dir.is_dir():
                        continue
                    book_words = 0
                    book_key = book_dir.name
                    rows.append(("book", None, book_key, book_dir.name, "Volume", 0, str(book_dir)))

                    draft_dirs = sorted([d for d in book_dir.glob("Draft-*") if d.is_dir()])
                    if draft_dirs:
                        for draft_dir in draft_dirs:
                            d_words = 0
                            d_key = f"{book_key}/{draft_dir.name}"
                            rows.append(("draft", book_key, d_key, draft_dir.name, "Draft Version", 0, str(draft_dir)))
                            for sub in sorted(draft_dir.iterdir()):
                                if sub.is_dir() and not sub.name.startswith("."):
                                    act_words = 0
                                    a_key = f"{d_key}/{sub.name}"
                                    rows.append(("act", d_key, a_key, sub.name, "Act / Section", 0, str(sub)))
                                    for ch_file in sorted(sub.glob("*.md")):
                                        if ch_file.is_file() and not ch_file.name.startswith("."):
                                            try:
                                                content = ch_file.read_text(encoding="utf-8", errors="replace")
                                                wc = _canonical_count(content)
                                                act_words += wc
                                                total_chapters += 1
                                                rows.append(("ch", a_key, None, ch_file.name, "Scene / Chapter", wc, str(ch_file)))
                                            except Exception as ex:
                                                logger.warning("Error counting %s: %s", ch_file, ex)
                                    for i, r in enumerate(rows):
                                        if r[2] == a_key:
                                            rows[i] = (r[0], r[1], r[2], r[3], r[4], act_words, r[6])
                                    d_words += act_words
                            for i, r in enumerate(rows):
                                if r[2] == d_key:
                                    rows[i] = (r[0], r[1], r[2], r[3], r[4], d_words, r[6])
                            book_words += d_words
                    else:
                        for act_dir in sorted(book_dir.iterdir()):
                            if act_dir.is_dir() and not act_dir.name.startswith(".") and act_dir.name != "Outlines":
                                act_words = 0
                                a_key = f"{book_key}/{act_dir.name}"
                                rows.append(("act", book_key, a_key, act_dir.name, "Act / Section", 0, str(act_dir)))
                                for ch_file in sorted(act_dir.glob("*.md")):
                                    if ch_file.is_file() and not ch_file.name.startswith("."):
                                        try:
                                            content = ch_file.read_text(encoding="utf-8", errors="replace")
                                            wc = _canonical_count(content)
                                            act_words += wc
                                            total_chapters += 1
                                            rows.append(("ch", a_key, None, ch_file.name, "Scene / Chapter", wc, str(ch_file)))
                                        except Exception as ex:
                                            logger.warning("Error counting %s: %s", ch_file, ex)
                                for i, r in enumerate(rows):
                                    if r[2] == a_key:
                                        rows[i] = (r[0], r[1], r[2], r[3], r[4], act_words, r[6])
                                book_words += act_words
                    for i, r in enumerate(rows):
                        if r[2] == book_key:
                            rows[i] = (r[0], r[1], r[2], r[3], r[4], book_words, r[6])
                    total_words += book_words

            def _apply():
                self.manuscript_store.clear()
                iter_map: dict[str, object] = {}
                for _level, parent_key, key, item, type_, wc, filepath in rows:
                    parent_iter = iter_map.get(parent_key) if parent_key else None
                    wc_str = f"{wc:,} words" if wc else ""
                    it = self.manuscript_store.append(parent_iter, [item, type_, wc_str, filepath])
                    if key:
                        iter_map[key] = it
                if hasattr(self, "card_total_words") and hasattr(self.card_total_words, "val_label"):
                    self.card_total_words.val_label.set_text(f"{total_words:,}")
                    self.card_chapters.val_label.set_text(str(total_chapters))
                if hasattr(self, "manuscript_tree"):
                    self.manuscript_tree.expand_all()
                self._hide_progress()

            if HAS_GTK and GLib is not None:
                GLib.idle_add(_apply)

        self._start_worker(_worker)

    def refresh_snapshot_history(self):
        if not hasattr(self, "history_store"):
            return
        self.history_store.clear()
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            return
        wpath = Path(target)
        git_dir = wpath / ".git"
        if not git_dir.is_dir():
            return

        head_file = git_dir / "HEAD"
        try:
            head_mtime = head_file.stat().st_mtime if head_file.exists() else 0.0
        except OSError:
            head_mtime = 0.0
        cache_key = (str(wpath), head_mtime)

        if cache_key in self._git_history_cache:
            lines = self._git_history_cache[cache_key]
        else:
            try:
                res = subprocess.run(
                    ["git", "-C", str(wpath), "log", "-n", "15",
                     "--pretty=format:%h|%ad|%s", "--date=short"],
                    capture_output=True, text=True, check=True, timeout=15
                )
                lines = res.stdout.splitlines()
                self._git_history_cache[cache_key] = lines
            except Exception as e:
                logger.debug("Could not fetch git history: %s", e)
                lines = []

        for line in lines:
            parts = line.split("|", 2)
            if len(parts) == 3:
                self.history_store.append([parts[0], parts[1], parts[2]])

    def update_toolchain_badges(self):
        if not hasattr(self, "lbl_tool_git"):
            return
        tools = [
            ("git", self.lbl_tool_git),
            ("pandoc", self.lbl_tool_pandoc),
            ("typst", self.lbl_tool_typst),
            ("python3", self.lbl_tool_python),
        ]
        for cmd, badge in tools:
            path = _cached_which(cmd)
            if path:
                badge.status_label.set_markup("<span color='#2e7d32'><b>✓ Installed</b></span>")
            else:
                badge.status_label.set_markup("<span color='#d32f2f'><b>✗ Missing</b></span>")

    def check_first_run(self):
        flag_file = HOME_DIR / ".config" / "arcanum" / "first_run_done"
        if not flag_file.is_file() and not self.discovered_worlds and not self.discovered_manuscripts and HAS_GTK and GLib is not None:
            GLib.idle_add(self.show_welcome_dialog, flag_file)

    def check_first_run_wizard(self):
        if getattr(self, "_first_run_wizard_shown", False):
            return
        self._first_run_wizard_shown = True
        has_projects = bool(self.discovered_worlds or self.discovered_manuscripts)
        if not has_projects and HAS_GTK:
            dialog = Gtk.Dialog(title="Welcome to Ars Arcanum", parent=self, flags=0)
            dialog.set_default_size(520, 320)
            box = dialog.get_content_area()
            box.set_border_width(16)
            box.set_spacing(12)

            lbl_title = Gtk.Label()
            lbl_title.set_markup("<span size='large' weight='bold'>Welcome to Ars Arcanum Studio!</span>")
            lbl_title.set_xalign(0)
            box.pack_start(lbl_title, False, False, 0)

            lbl_desc = Gtk.Label(label="Ars Arcanum is your sovereign writing, worldbuilding, and publishing platform.\nHow would you like to begin?")
            lbl_desc.set_xalign(0)
            lbl_desc.set_line_wrap(True)
            box.pack_start(lbl_desc, False, False, 0)

            btn_demo = Gtk.Button(label="✨  Generate Sample Cosmos (Recommended)\nExplore a pre-configured fantasy cosmos with lore, characters & starter chapters")
            btn_demo.get_style_context().add_class("suggested-action")
            btn_demo.connect("clicked", lambda b: (dialog.response(Gtk.ResponseType.YES), dialog.destroy(), self.on_generate_demo_clicked(None)))
            box.pack_start(btn_demo, False, False, 4)

            btn_new = Gtk.Button(label="➕  Create Fresh Project\nStart a new blank Universe, World Lore Vault, or Manuscript")
            btn_new.connect("clicked", lambda b: (dialog.response(Gtk.ResponseType.OK), dialog.destroy(), self.on_new_universe_clicked(None)))
            box.pack_start(btn_new, False, False, 4)

            btn_skip = Gtk.Button(label="Skip / Explore Interface")
            btn_skip.connect("clicked", lambda b: (dialog.response(Gtk.ResponseType.CANCEL), dialog.destroy()))
            box.pack_start(btn_skip, False, False, 4)

            dialog.show_all()

    def show_welcome_dialog(self, flag_file=None):
        if not HAS_GTK:
            return
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
            "• Click '📖 Field Manual' (F1) in the top right anytime for complete guides.\n\n"
            "Happy Writing!"
        )
        dialog.run()
        dialog.destroy()
        if flag_file:
            try:
                flag_file.parent.mkdir(parents=True, exist_ok=True)
                flag_file.write_text("done\n", encoding="utf-8")
            except Exception:
                pass

    def on_open_manual_clicked(self, btn=None):
        manual_path = PROJECT_ROOT / "docs" / "AUTHOR_MANUAL.md"
        if manual_path.is_file():
            self._launch_detached(["xdg-open", str(manual_path)])
        else:
            self.show_error("Author's Field Manual not found.")

    def on_new_universe_clicked(self, btn=None):
        if not HAS_GTK:
            return
        dialog = Gtk.Dialog(title="New Narrative Universe", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        lbl = Gtk.Label(label="Enter name for new Universe container (e.g., 'Eldoria-Cosmos', 'Solaris-Prime'):")
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

    def on_new_world_clicked(self, btn=None):
        if not HAS_GTK:
            return
        dialog = Gtk.Dialog(title="New World Lore Vault", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK)
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
                    for name, path, _label in self.discovered_worlds:
                        if name == wname:
                            self.combo_world.set_active_id(path)
                            break

                self._start_worker(
                    self._run_async_command,
                    args=(cmd, f"World lore vault '{wname}' created successfully!", on_world_created),
                )
        dialog.destroy()

    def on_new_manuscript_clicked(self, btn=None):
        if not HAS_GTK:
            return
        dialog = Gtk.Dialog(title="New Manuscript Project", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK)
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
                    for name, path, _label in self.discovered_manuscripts:
                        if name == mname:
                            self.combo_manuscript.set_active_id(path)
                            break

                self._start_worker(
                    self._run_async_command,
                    args=(cmd, f"Manuscript '{mname}' created successfully!", on_ms_created),
                )
        dialog.destroy()

    def on_quick_snapshot_clicked(self, btn=None):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            self.show_error("Please select an active manuscript or world first.")
            return

        if not HAS_GTK:
            return
        dialog = Gtk.Dialog(title="Quick Version Snapshot", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK)
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

    def on_save_snapshot_clicked(self, btn=None):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            self.show_error("Please select an active project first.")
            return
        note = self.entry_snap_note.get_text().strip() if hasattr(self, "entry_snap_note") else ""
        if not note:
            note = f"Snapshot: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "save_snapshot.sh"), target, "--note", note]
        self.set_status("Saving version milestone snapshot...")
        self._start_worker(self._run_async_command, args=(cmd, "Snapshot recorded successfully!", self.refresh_snapshot_history))

    def on_create_backup_clicked(self, btn=None):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            self.show_error("Please select an active project first.")
            return
        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "backup_world.sh"), target]
        self.set_status("Creating standalone verified backup archive...")
        self._start_worker(self._run_async_command, args=(cmd, "Backup archive created with SHA-256 digest!"))

    def on_restore_clicked(self, btn=None):
        if not HAS_GTK:
            return
        dialog = Gtk.FileChooserDialog(
            title="Select Ars Arcanum Backup Archive",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Open", Gtk.ResponseType.OK)
        filter_tar = Gtk.FileFilter()
        filter_tar.set_name("Backup Archives (*.tar.gz)")
        filter_tar.add_pattern("*.tar.gz")
        dialog.add_filter(filter_tar)

        if dialog.run() == Gtk.ResponseType.OK:
            archive_path = dialog.get_filename()
            dialog.destroy()

            name_dialog = Gtk.Dialog(title="Restore Target Name", parent=self, flags=0)
            name_dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK)
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

    def on_compile_clicked(self, btn=None):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            self.show_error("Please select an active manuscript or world first.")
            return

        title = self.entry_pub_title.get_text().strip() if hasattr(self, "entry_pub_title") else ""
        if not title:
            title = Path(target).name
        author = self.entry_pub_author.get_text().strip() if hasattr(self, "entry_pub_author") else "Author Name"
        volume = self.combo_pub_volume.get_active_id() if hasattr(self, "combo_pub_volume") else "Book-01"
        volume = volume or "Book-01"
        paper_size = self.combo_paper_size.get_active_id() if hasattr(self, "combo_paper_size") else "us-trade"
        paper_size = paper_size or "us-trade"
        export_fmt = self.combo_pub_format.get_active_id() if hasattr(self, "combo_pub_format") else "book"
        export_fmt = export_fmt or "book"

        cmd = [
            "bash", str(PROJECT_ROOT / "scripts" / "export_book.sh"),
            target,
            "--title", title,
            "--author", author,
            "--book", volume,
            "--paper-size", paper_size,
            "--format", export_fmt
        ]

        if hasattr(self, "btn_compile"):
            self.btn_compile.set_sensitive(False)
        if hasattr(self, "pub_log_buffer"):
            self.pub_log_buffer.set_text(f"Starting compilation for '{title}' [{volume}] (format: {export_fmt})...\n")
        self.set_status(f"Compiling publication artifacts ({export_fmt})...")

        def _worker():
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if hasattr(self, "pub_log_buffer"):
                self._stream_process_to_log(proc, self.pub_log_buffer, self._append_log)
            proc.wait()
            if HAS_GTK and GLib is not None:
                GLib.idle_add(self._on_compile_done, proc.returncode)

        self._start_worker(_worker)

    def _append_log(self, buffer_obj, text):
        if buffer_obj:
            end_iter = buffer_obj.get_end_iter()
            buffer_obj.insert(end_iter, text)

    def _on_compile_done(self, returncode):
        if hasattr(self, "btn_compile"):
            self.btn_compile.set_sensitive(True)
        if returncode == 0:
            self.set_status("Artifacts compiled successfully!")
            if hasattr(self, "btn_open_pdf"):
                self.btn_open_pdf.set_sensitive(True)
                self.btn_open_epub.set_sensitive(True)
                self.btn_open_docx.set_sensitive(True)
        else:
            self.set_status("Compilation finished with warnings/errors.")

    def on_open_pdf_clicked(self, btn=None):
        target = self.current_manuscript_path or self.current_world_path
        if target:
            tpath = Path(target)
            pub_dir = tpath / "Exports" if (tpath / "Exports").is_dir() else tpath / "04-Publishing"
            pdfs = list(pub_dir.glob("*.pdf"))
            if pdfs:
                latest = max(pdfs, key=os.path.getmtime)
                self._launch_detached(["xdg-open", str(latest)])

    def on_open_epub_clicked(self, btn=None):
        target = self.current_manuscript_path or self.current_world_path
        if target:
            tpath = Path(target)
            pub_dir = tpath / "Exports" if (tpath / "Exports").is_dir() else tpath / "04-Publishing"
            epubs = list(pub_dir.glob("*.epub"))
            if epubs:
                latest = max(epubs, key=os.path.getmtime)
                self._launch_detached(["xdg-open", str(latest)])

    def on_open_docx_clicked(self, btn=None):
        target = self.current_manuscript_path or self.current_world_path
        if target:
            tpath = Path(target)
            pub_dir = tpath / "Exports" if (tpath / "Exports").is_dir() else tpath / "04-Publishing"
            docxs = list(pub_dir.glob("*.docx"))
            if docxs:
                latest = max(docxs, key=os.path.getmtime)
                self._launch_detached(["xdg-open", str(latest)])

    def on_add_volume_clicked(self, btn=None):
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

        if not HAS_GTK:
            return
        dialog = Gtk.Dialog(title="Add Manuscript Volume", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK)
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

    def on_generate_demo_clicked(self, btn=None):
        demo_uni = "Eldoria-Cosmos"
        demo_world = "Chronicles-of-Eldoria"
        demo_ms = "The-Sovereign-Scroll"
        self.set_status("Scaffolding demo cosmos and manuscript...")

        def _worker():
            subprocess.run(["bash", str(PROJECT_ROOT / "scripts" / "init_universe.sh"), demo_uni], capture_output=True, timeout=120)
            subprocess.run(["bash", str(PROJECT_ROOT / "scripts" / "init_world.sh"), demo_world, "--universe", demo_uni], capture_output=True, timeout=120)
            subprocess.run(["bash", str(PROJECT_ROOT / "scripts" / "init_manuscript.sh"), demo_ms, "--universe", demo_uni, "--world", demo_world], capture_output=True, timeout=120)
            if HAS_GTK and GLib is not None:
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

    def on_launch_obsidian(self, btn=None):
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

    def on_launch_novelwriter(self, btn=None):
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

    def on_launch_focuswriter(self, btn=None):
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

    def on_open_world_folder_clicked(self, btn=None):
        if self.current_world_path:
            self._launch_detached(["xdg-open", str(self.current_world_path)])

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

    def on_fork_draft_clicked(self, btn=None):
        target = self.current_manuscript_path
        if not target:
            self.show_error("Please select an active manuscript first.")
            return

        vol = self.combo_draft_vol.get_active_id() or "Book-01"
        if not HAS_GTK:
            return
        dialog = Gtk.Dialog(title="Fork New Manuscript Draft", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK)
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

    def on_view_redline_clicked(self, btn=None):
        target = self.current_manuscript_path
        if not target:
            self.show_error("Please select an active manuscript first.")
            return
        vol = self.combo_draft_vol.get_active_id() or "Book-01"
        draft_b = self.combo_diff_b.get_active_id() if hasattr(self, "combo_diff_b") else None
        draft_a = self.combo_diff_a.get_active_id() if hasattr(self, "combo_diff_a") else None
        if not draft_b or not draft_a:
            self.show_error("Please select both a target draft and a prior draft to compare.")
            return
        if draft_b == draft_a:
            self.show_error("Target draft and prior draft must be different to view changes.")
            return

        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "compare_drafts.sh"), target, draft_b, draft_a, "-b", vol, "--browser"]
        self.set_status(f"Generating Redline diff: {draft_a} vs {draft_b}...")
        self._start_worker(self._run_async_command, args=(cmd, "Redline diff opened in browser!"))

    def on_lo_compare_clicked(self, btn=None):
        target = self.current_manuscript_path
        if not target:
            self.show_error("Please select an active manuscript first.")
            return
        vol = self.combo_draft_vol.get_active_id() or "Book-01"
        draft_b = self.combo_diff_b.get_active_id() if hasattr(self, "combo_diff_b") else None
        draft_a = self.combo_diff_a.get_active_id() if hasattr(self, "combo_diff_a") else None
        if not draft_b or not draft_a:
            self.show_error("Please select both drafts.")
            return
        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "compare_drafts.sh"), target, draft_b, draft_a, "-b", vol, "--libreoffice"]
        self.set_status("Launching LibreOffice Writer Track Changes comparison...")
        self._start_worker(self._run_async_command, args=(cmd, "LibreOffice Writer comparison launched."))

    def on_select_secure_dest_clicked(self, btn=None):
        if not HAS_GTK:
            return
        dialog = Gtk.FileChooserDialog(
            title="Select External / USB Secure Backup Destination Directory",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Open", Gtk.ResponseType.OK)
        if dialog.run() == Gtk.ResponseType.OK:
            chosen = dialog.get_filename()
            dialog.destroy()
            if chosen:
                set_backup_dest(chosen)
                self.update_secure_dest_display()
                self.set_status(f"Secure backup destination updated: {chosen}")
        else:
            dialog.destroy()

    def on_clear_secure_dest_clicked(self, btn=None):
        clear_backup_dest()
        self.update_secure_dest_display()
        self.set_status("Secure backup destination cleared (local only).")

    def on_open_word_processor_clicked(self, btn=None):
        target = self.current_manuscript_path
        if not target:
            self.show_error("Please select an active manuscript first.")
            return
        vol = self.combo_draft_vol.get_active_id() if hasattr(self, "combo_draft_vol") else "Book-01"
        draft = self.combo_draft_list.get_active_id() if hasattr(self, "combo_draft_list") else None
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

    def on_sync_docx_clicked(self, btn=None):
        target = self.current_manuscript_path
        if not target:
            self.show_error("Please select an active manuscript first.")
            return
        draft = self.combo_draft_list.get_active_id() if hasattr(self, "combo_draft_list") else None
        self.set_status("Synchronizing DOCX and Markdown scenes...")

        def _do_sync():
            res = sync_manuscript_docx(Path(target), draft_name=draft)

            def _done():
                self.refresh_manuscript_analytics()
                msg = f"DOCX Sync Complete: {len(res.get('md_to_docx', []))} exported, {len(res.get('docx_to_md', []))} imported."
                self.set_status(msg)
                if HAS_GTK:
                    dialog = Gtk.MessageDialog(
                        transient_for=self, flags=0,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.OK,
                        text="DOCX Synchronization Complete"
                    )
                    dialog.format_secondary_text(f"• Markdown -> DOCX updated: {len(res.get('md_to_docx', []))}\n• DOCX -> Markdown imported: {len(res.get('docx_to_md', []))}\n• Errors: {len(res.get('errors', []))}")
                    dialog.run()
                    dialog.destroy()
            if HAS_GTK and GLib is not None:
                GLib.idle_add(_done)

        self._start_worker(_do_sync)

    def on_docx_settings_clicked(self, btn=None):
        if not HAS_GTK:
            return
        dialog = Gtk.Dialog(title="DOCX Manuscript Formatting & Submission Presets", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Apply", Gtk.ResponseType.APPLY)
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

        grid.attach(Gtk.Label(label="Formatting Preset:", xalign=0), 0, 0, 1, 1)
        combo_preset = Gtk.ComboBoxText()
        for pid, pinfo in presets.items():
            combo_preset.append(pid, pinfo["name"])
        combo_preset.set_active_id(active_preset)
        grid.attach(combo_preset, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Font Family:", xalign=0), 0, 1, 1, 1)
        combo_font = Gtk.ComboBoxText()
        for f in ["Times New Roman", "Georgia", "EB Garamond", "Libertinus Serif", "Courier Prime", "Arial"]:
            combo_font.append(f, f)
        combo_font.set_active_id(cfg.get("font_family", "Times New Roman"))
        grid.attach(combo_font, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Font Size (pt):", xalign=0), 0, 2, 1, 1)
        spin_sz = Gtk.SpinButton.new_with_range(9.0, 18.0, 0.5)
        spin_sz.set_value(float(cfg.get("font_size_pt", 12.0)))
        grid.attach(spin_sz, 1, 2, 1, 1)

        grid.attach(Gtk.Label(label="Line Spacing:", xalign=0), 0, 3, 1, 1)
        combo_ls = Gtk.ComboBoxText()
        combo_ls.append("2.0", "2.0x (Double Spaced - Standard Submission)")
        combo_ls.append("1.5", "1.5x (Classic Trade)")
        combo_ls.append("1.35", "1.35x (Modern Editorial)")
        combo_ls.append("1.0", "1.0x (Single Spaced)")
        cur_ls = str(cfg.get("line_spacing", 2.0))
        combo_ls.set_active_id(cur_ls if cur_ls in ("2.0", "1.5", "1.35", "1.0") else "2.0")
        grid.attach(combo_ls, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label="Margins (inches):", xalign=0), 0, 4, 1, 1)
        spin_mg = Gtk.SpinButton.new_with_range(0.5, 2.0, 0.1)
        spin_mg.set_value(float(cfg.get("margin_inches", 1.0)))
        grid.attach(spin_mg, 1, 4, 1, 1)

        grid.attach(Gtk.Label(label="Paragraph Indent (inches):", xalign=0), 0, 5, 1, 1)
        spin_id = Gtk.SpinButton.new_with_range(0.0, 1.5, 0.05)
        spin_id.set_value(float(cfg.get("first_line_indent_inches", 0.5)))
        grid.attach(spin_id, 1, 5, 1, 1)

        grid.attach(Gtk.Label(label="Scene Break Symbol:", xalign=0), 0, 6, 1, 1)
        entry_sb = Gtk.Entry()
        entry_sb.set_text(str(cfg.get("scene_break_symbol", "#")))
        grid.attach(entry_sb, 1, 6, 1, 1)

        box.pack_start(grid, False, False, 0)

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
                draft = self.combo_draft_list.get_active_id() if hasattr(self, "combo_draft_list") else None
                build_manuscript_docx(Path(self.current_manuscript_path), draft_name=draft)
        dialog.destroy()

    def show_error(self, message):
        if not HAS_GTK:
            print(f"[Error] {message}", file=sys.stderr)
            return
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()

    @staticmethod
    def _stream_process_to_log(proc, buffer_obj, append_fn, chunk_lines=50):
        buf = []
        try:
            for line in proc.stdout or []:
                buf.append(line)
                if len(buf) >= chunk_lines:
                    if HAS_GTK and GLib is not None:
                        GLib.idle_add(append_fn, buffer_obj, "".join(buf))
                    buf = []
        finally:
            if buf and HAS_GTK and GLib is not None:
                GLib.idle_add(append_fn, buffer_obj, "".join(buf))

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
            if HAS_GTK and GLib is not None:
                GLib.idle_add(self.set_status, "Error: command timed out.")
            return
        if HAS_GTK and GLib is not None:
            if res.returncode == 0:
                GLib.idle_add(self.set_status, success_msg)
            else:
                GLib.idle_add(self.set_status, f"Error: {res.stderr.strip() or 'Command failed'}")
            if callback:
                GLib.idle_add(callback)


# Compatibility alias
ScriptoriumApp = ArcanumApp


def run_gtk3_app(active_tab: str | None = None):
    """Entry point for launching the GTK 3 desktop application."""
    if not HAS_GTK:
        return False
    app = ArcanumApp(active_tab=active_tab)
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
    return True


def main():
    """Main CLI entry point for standalone GTK 3 execution."""
    if not HAS_GTK:
        print("[!] PyGObject / GTK 3 is not installed in the current Python environment.", file=sys.stderr)
        print("[i] Falling back to Zenity desktop control dashboard...", file=sys.stderr)
        sys.exit(2)

    run_gtk3_app()


if __name__ == "__main__":
    main()
