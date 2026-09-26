#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 Safety & Backup Studio (scripts/lib/ui_gtk3/studios/safety.py)
==============================================================================
Provides Studio 5 tab interface for Git snapshots, 3-2-1 verified tar backups,
external drive replication, and disaster recovery restore drills.
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path

from lib.ui_gtk3.cli_bridge import (
    clear_backup_dest,
    get_backup_dest,
    set_backup_dest,
)
from lib.ui_gtk3.common import (
    HAS_GTK,
    PROJECT_ROOT,
    UNIVERSES_DIR,
    GLib,
    Gtk,
)

logger = logging.getLogger("arcanum.ui_gtk3.studios.safety")


class SafetyStudioMixin:
    """Mixin providing Vault Safety & Version History Studio UI components and callbacks."""

    def create_safety_tab(self):
        tab = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        tab.set_border_width(12)

        # Left Column: Actions & Configuration
        left_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_col.set_size_request(340, -1)

        # Git Snapshots Card
        snap_frame = Gtk.Frame(label=" 📷 Git Version History ")
        snap_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        snap_box.set_border_width(10)

        snap_box.pack_start(Gtk.Label(label="Milestone Commit Note:", xalign=0), False, False, 0)
        self.entry_snap_note = Gtk.Entry()
        self.entry_snap_note.set_placeholder_text("e.g. Finished Chapter 4 revision")
        snap_box.pack_start(self.entry_snap_note, False, False, 0)

        btn_snap = Gtk.Button(label="📷 Save Snapshot Milestone")
        btn_snap.get_style_context().add_class("suggested-action")
        btn_snap.connect("clicked", self.on_save_snapshot_clicked)
        snap_box.pack_start(btn_snap, False, False, 0)

        snap_frame.add(snap_box)
        left_col.pack_start(snap_frame, False, False, 0)

        # Backup & Disaster Recovery Card
        backup_frame = Gtk.Frame(label=" 🔒 Standalone Verified Backups ")
        backup_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        backup_box.set_border_width(10)

        btn_backup = Gtk.Button(label="📦 Create Verified .tar.gz Backup")
        btn_backup.connect("clicked", self.on_create_backup_clicked)
        backup_box.pack_start(btn_backup, False, False, 0)

        btn_restore = Gtk.Button(label="♻️ Restore Project from Archive")
        btn_restore.connect("clicked", self.on_restore_clicked)
        backup_box.pack_start(btn_restore, False, False, 0)

        # Secure Secondary Destination
        backup_box.pack_start(Gtk.Label(label="<b>Secondary Backup Destination (USB/Drive):</b>", use_markup=True, xalign=0), False, False, 0)
        self.lbl_secure_dest = Gtk.Label(label="<i>Not configured (local only)</i>", use_markup=True, xalign=0)
        self.lbl_secure_dest.set_line_wrap(True)
        backup_box.pack_start(self.lbl_secure_dest, False, False, 0)

        dest_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_sel_dest = Gtk.Button(label="📁 Choose Drive")
        btn_sel_dest.connect("clicked", self.on_select_secure_dest_clicked)
        dest_btn_box.pack_start(btn_sel_dest, True, True, 0)

        btn_clr_dest = Gtk.Button(label="✕ Clear")
        btn_clr_dest.connect("clicked", self.on_clear_secure_dest_clicked)
        dest_btn_box.pack_start(btn_clr_dest, False, False, 0)
        backup_box.pack_start(dest_btn_box, False, False, 0)

        backup_frame.add(backup_box)
        left_col.pack_start(backup_frame, False, False, 0)

        tab.pack_start(left_col, False, False, 0)

        # Right Column: Git Commit Timeline History
        right_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        lbl_history = Gtk.Label(label="<b>Recent Version Milestone History:</b>", use_markup=True, xalign=0)
        right_col.pack_start(lbl_history, False, False, 0)

        scrolled_hist = Gtk.ScrolledWindow()
        scrolled_hist.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.tree_history = Gtk.TreeView()
        self.model_history = Gtk.ListStore(str, str, str)  # Hash, Date, Message
        self.tree_history.set_model(self.model_history)

        col_hash = Gtk.TreeViewColumn("Hash", Gtk.CellRendererText(), text=0)
        col_date = Gtk.TreeViewColumn("Date / Time", Gtk.CellRendererText(), text=1)
        col_msg = Gtk.TreeViewColumn("Snapshot Message", Gtk.CellRendererText(), text=2)
        col_msg.set_expand(True)

        self.tree_history.append_column(col_hash)
        self.tree_history.append_column(col_date)
        self.tree_history.append_column(col_msg)

        scrolled_hist.add(self.tree_history)
        right_col.pack_start(scrolled_hist, True, True, 0)

        tab.pack_start(right_col, True, True, 0)
        self.update_secure_dest_display()
        return tab

    def on_quick_snapshot_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path or str(UNIVERSES_DIR)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        note = f"Quick Snapshot: {now_str}"
        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "arcanum"), "snapshot", target, "-m", note]

        def _worker():
            res = subprocess.run(cmd, capture_output=True, text=True)
            if HAS_GTK and GLib is not None:
                if res.returncode == 0:
                    GLib.idle_add(lambda: self.set_status(f"Quick Snapshot recorded for {Path(target).name}!"))
                    GLib.idle_add(self.refresh_snapshot_history)
                else:
                    GLib.idle_add(lambda: self.show_error(f"Snapshot failed:\n{res.stderr}"))

        self._start_worker(_worker)

    def on_save_snapshot_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path or str(UNIVERSES_DIR)
        note = self.entry_snap_note.get_text().strip() or f"Snapshot: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "arcanum"), "snapshot", target, "-m", note]

        def _worker():
            res = subprocess.run(cmd, capture_output=True, text=True)
            if HAS_GTK and GLib is not None:
                if res.returncode == 0:
                    GLib.idle_add(lambda: self.set_status(f"Snapshot saved: {note}"))
                    GLib.idle_add(self.refresh_snapshot_history)
                    GLib.idle_add(lambda: self.entry_snap_note.set_text(""))
                else:
                    GLib.idle_add(lambda: self.show_error(f"Snapshot failed:\n{res.stderr}"))

        self._start_worker(_worker)

    def on_create_backup_clicked(self, btn):
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            self.show_error("Please select an active World or Manuscript first.")
            return

        cmd = ["bash", str(PROJECT_ROOT / "scripts" / "arcanum"), "backup", target]
        self.set_status(f"Creating verified backup for {Path(target).name}...")

        def _worker():
            res = subprocess.run(cmd, capture_output=True, text=True)
            if HAS_GTK and GLib is not None:
                if res.returncode == 0:
                    GLib.idle_add(lambda: self.set_status("Backup completed and verified cleanly!"))
                else:
                    GLib.idle_add(lambda: self.show_error(f"Backup error:\n{res.stderr}"))

        self._start_worker(_worker)

    def on_restore_clicked(self, btn):
        dialog = Gtk.FileChooserDialog(
            title="Select Backup Archive (.tar.gz) to Restore",
            parent=self if isinstance(self, Gtk.Window) else None,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Restore", Gtk.ResponseType.OK)

        flt = Gtk.FileFilter()
        flt.set_name("Ars Arcanum Backup Archives (*.tar.gz)")
        flt.add_pattern("*.tar.gz")
        dialog.add_filter(flt)

        res = dialog.run()
        archive_path = dialog.get_filename()
        dialog.destroy()

        if res == Gtk.ResponseType.OK and archive_path:
            cmd = ["bash", str(PROJECT_ROOT / "scripts" / "arcanum"), "restore", archive_path]
            self.set_status(f"Restoring {Path(archive_path).name}...")

            def _worker():
                res_proc = subprocess.run(cmd, capture_output=True, text=True)
                if HAS_GTK and GLib is not None:
                    if res_proc.returncode == 0:
                        GLib.idle_add(self.refresh_all_discovery)
                        GLib.idle_add(lambda: self.set_status("Project restored successfully!"))
                    else:
                        GLib.idle_add(lambda: self.show_error(f"Restore error:\n{res_proc.stderr}"))

            self._start_worker(_worker)

    def on_select_secure_dest_clicked(self, btn):
        dialog = Gtk.FileChooserDialog(
            title="Choose Secondary Backup Destination (USB / Secondary Drive)",
            parent=self if isinstance(self, Gtk.Window) else None,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK)
        res = dialog.run()
        dest_path = dialog.get_filename()
        dialog.destroy()

        if res == Gtk.ResponseType.OK and dest_path:
            set_backup_dest(dest_path)
            self.update_secure_dest_display()
            self.set_status(f"Secondary backup destination set: {dest_path}")

    def on_clear_secure_dest_clicked(self, btn):
        clear_backup_dest()
        self.update_secure_dest_display()
        self.set_status("Secondary backup destination cleared (local only).")

    def update_secure_dest_display(self):
        if not self.lbl_secure_dest:
            return
        dest = get_backup_dest()
        if dest:
            self.lbl_secure_dest.set_markup(f"<code>{dest}</code>")
        else:
            self.lbl_secure_dest.set_markup("<i>Not configured (local backups only)</i>")

    def refresh_snapshot_history(self):
        if not self.model_history:
            return
        target = self.current_manuscript_path or self.current_world_path
        if not target or not (Path(target) / ".git").is_dir():
            self.model_history.clear()
            return

        def _worker():
            try:
                cmd = ["git", "-C", str(target), "log", "-n", "15", "--format=%h|%cr|%s"]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                entries = []
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        if "|" in line:
                            parts = line.split("|", 2)
                            entries.append(parts)
                if HAS_GTK and GLib is not None:
                    def _apply():
                        self.model_history.clear()
                        for h, d, m in entries:
                            self.model_history.append([h, d, m])
                    GLib.idle_add(_apply)
            except Exception as e:
                logger.debug("Error loading snapshot history: %s", e)

        self._start_worker(_worker)
