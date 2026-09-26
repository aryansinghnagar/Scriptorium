#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 Manuscripts & Drafting Studio (scripts/lib/ui_gtk3/studios/drafting.py)
========================================================================================
Provides Studio 2 tab interface for managing Novel Manuscripts, scene tags,
DOCX word processor sync, and draft redline diffing.
"""

import logging
import subprocess
import sys
from pathlib import Path

from lib.ui_gtk3.cli_bridge import (
    build_manuscript_docx,
    get_active_docx_preset_name,
    get_docx_config,
    launch_external_app,
    list_docx_presets,
    open_in_word_processor,
    set_docx_option,
    set_docx_preset,
    sync_manuscript_docx,
)
from lib.ui_gtk3.common import (
    HAS_GTK,
    MANUSCRIPTS_DIR,
    PROJECT_ROOT,
    GLib,
    Gtk,
)

logger = logging.getLogger("arcanum.ui_gtk3.studios.drafting")


class DraftingStudioMixin:
    """Mixin providing Manuscripts & Drafting Studio UI components and callbacks."""

    def create_manuscript_tab(self):
        tab = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        tab.set_border_width(12)

        # Left Column: Manuscript Outlines & File Tree
        left_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_col.set_size_request(340, -1)

        # Top Action Bar
        action_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_new_ms = Gtk.Button(label="➕ New Novel")
        btn_new_ms.connect("clicked", self.on_new_manuscript_clicked)
        action_bar.pack_start(btn_new_ms, True, True, 0)

        btn_add_vol = Gtk.Button(label="📖 Add Book")
        btn_add_vol.connect("clicked", self.on_add_volume_clicked)
        action_bar.pack_start(btn_add_vol, True, True, 0)

        left_col.pack_start(action_bar, False, False, 0)

        # Editor Launcher Buttons
        btn_nw = Gtk.Button(label="✍️ Open in novelWriter")
        btn_nw.get_style_context().add_class("suggested-action")
        btn_nw.connect("clicked", self.on_launch_novelwriter)
        left_col.pack_start(btn_nw, False, False, 0)

        btn_fw = Gtk.Button(label="🧘 Distraction-Free FocusWriter")
        btn_fw.connect("clicked", self.on_launch_focuswriter)
        left_col.pack_start(btn_fw, False, False, 0)

        # Manuscript Scene TreeView
        lbl_tree = Gtk.Label(label="<b>Manuscript Scenes & Chapters:</b>", use_markup=True, xalign=0)
        left_col.pack_start(lbl_tree, False, False, 0)

        scrolled_tree = Gtk.ScrolledWindow()
        scrolled_tree.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.tree_manuscript = Gtk.TreeView()
        self.model_manuscript = Gtk.TreeStore(str, str, str, str)  # Title, Words, Status, FullPath
        self.tree_manuscript.set_model(self.model_manuscript)

        col_title = Gtk.TreeViewColumn("Title / Scene", Gtk.CellRendererText(), text=0)
        col_words = Gtk.TreeViewColumn("Words", Gtk.CellRendererText(), text=1)
        col_status = Gtk.TreeViewColumn("Status", Gtk.CellRendererText(), text=2)
        self.tree_manuscript.append_column(col_title)
        self.tree_manuscript.append_column(col_words)
        self.tree_manuscript.append_column(col_status)

        selection = self.tree_manuscript.get_selection()
        selection.connect("changed", self.on_manuscript_tree_selection_changed)

        scrolled_tree.add(self.tree_manuscript)
        left_col.pack_start(scrolled_tree, True, True, 0)

        tab.pack_start(left_col, False, False, 0)

        # Right Column: Visual Scene Metadata Inspector & Word Sync
        right_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Word Processor Sync Toolbar
        docx_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_word = Gtk.Button(label="📝 Open in Word / LibreOffice")
        btn_word.connect("clicked", self.on_open_word_processor_clicked)
        docx_bar.pack_start(btn_word, True, True, 0)

        btn_sync = Gtk.Button(label="🔄 Sync Markdown ↔ DOCX")
        btn_sync.connect("clicked", self.on_sync_docx_clicked)
        docx_bar.pack_start(btn_sync, True, True, 0)

        btn_docx_cfg = Gtk.Button(label="⚙️ Presets")
        btn_docx_cfg.connect("clicked", self.on_docx_settings_clicked)
        docx_bar.pack_start(btn_docx_cfg, False, False, 0)

        right_col.pack_start(docx_bar, False, False, 0)

        # Scene Metadata Inspector Box
        inspector_frame = Gtk.Frame(label=" 🔍 Visual Scene Metadata Inspector ")
        inspector_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        inspector_box.set_border_width(10)

        self.lbl_inspector_file = Gtk.Label(label="<i>Select a chapter/scene .md file to inspect tags</i>", use_markup=True, xalign=0)
        inspector_box.pack_start(self.lbl_inspector_file, False, False, 0)

        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(6)

        grid.attach(Gtk.Label(label="POV Character (@pov):", xalign=0), 0, 0, 1, 1)
        self.entry_tag_pov = Gtk.Entry()
        grid.attach(self.entry_tag_pov, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Cast in Scene (@char):", xalign=0), 0, 1, 1, 1)
        self.entry_tag_char = Gtk.Entry()
        grid.attach(self.entry_tag_char, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Location (@location):", xalign=0), 0, 2, 1, 1)
        self.entry_tag_location = Gtk.Entry()
        grid.attach(self.entry_tag_location, 1, 2, 1, 1)

        grid.attach(Gtk.Label(label="Plot Thread (@thread):", xalign=0), 0, 3, 1, 1)
        self.entry_tag_thread = Gtk.Entry()
        grid.attach(self.entry_tag_thread, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label="Story Timeline (@time):", xalign=0), 0, 4, 1, 1)
        self.entry_tag_time = Gtk.Entry()
        grid.attach(self.entry_tag_time, 1, 4, 1, 1)

        grid.attach(Gtk.Label(label="Drafting Status (@status):", xalign=0), 0, 5, 1, 1)
        self.combo_tag_status = Gtk.ComboBoxText()
        for st in ["Draft", "Revision", "First Polish", "Final"]:
            self.combo_tag_status.append(st, st)
        self.combo_tag_status.set_active_id("Draft")
        grid.attach(self.combo_tag_status, 1, 5, 1, 1)

        inspector_box.pack_start(grid, False, False, 0)

        tag_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.btn_save_scene_tags = Gtk.Button(label="💾 Save Tags to Scene File")
        self.btn_save_scene_tags.get_style_context().add_class("suggested-action")
        self.btn_save_scene_tags.connect("clicked", self.on_save_scene_tags_clicked)
        self.btn_save_scene_tags.set_sensitive(False)
        tag_actions.pack_start(self.btn_save_scene_tags, True, True, 0)

        self.btn_read_scene_tags = Gtk.Button(label="🔄 Reload from Disk")
        self.btn_read_scene_tags.connect("clicked", self.on_read_scene_tags_clicked)
        self.btn_read_scene_tags.set_sensitive(False)
        tag_actions.pack_start(self.btn_read_scene_tags, True, True, 0)

        inspector_box.pack_start(tag_actions, False, False, 0)
        inspector_frame.add(inspector_box)
        right_col.pack_start(inspector_frame, False, False, 0)

        # Draft Forking & Redline Diff Box
        draft_frame = Gtk.Frame(label=" 🔀 Multi-Draft Revisions & Redline Comparator ")
        draft_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        draft_box.set_border_width(10)

        fork_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_fork = Gtk.Button(label="🌿 Fork Next Draft Version")
        btn_fork.connect("clicked", self.on_fork_draft_clicked)
        fork_row.pack_start(btn_fork, True, True, 0)
        draft_box.pack_start(fork_row, False, False, 0)

        diff_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        diff_row.pack_start(Gtk.Label(label="Compare:"), False, False, 0)
        self.combo_diff_a = Gtk.ComboBoxText()
        diff_row.pack_start(self.combo_diff_a, True, True, 0)
        diff_row.pack_start(Gtk.Label(label="against:"), False, False, 0)
        self.combo_diff_b = Gtk.ComboBoxText()
        diff_row.pack_start(self.combo_diff_b, True, True, 0)

        btn_view_diff = Gtk.Button(label="🔍 Visual Redline Diff")
        btn_view_diff.connect("clicked", self.on_view_redline_clicked)
        diff_row.pack_start(btn_view_diff, False, False, 0)

        btn_lo_diff = Gtk.Button(label="📄 LibreOffice Diff")
        btn_lo_diff.connect("clicked", self.on_lo_compare_clicked)
        diff_row.pack_start(btn_lo_diff, False, False, 0)

        draft_box.pack_start(diff_row, False, False, 0)
        draft_frame.add(draft_box)
        right_col.pack_start(draft_frame, True, True, 0)

        tab.pack_start(right_col, True, True, 0)
        return tab

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

            out_chunks = []
            if frontmatter_lines:
                out_chunks.append("\n".join(frontmatter_lines))
            if heading:
                out_chunks.append(heading)
            if tag_lines:
                out_chunks.append("\n".join(tag_lines))
            if body_lines:
                out_chunks.append("\n".join(body_lines).lstrip("\n"))

            new_text = "\n\n".join([c for c in out_chunks if c]) + "\n"
            file_path.write_text(new_text, encoding="utf-8")
            self.set_status(f"Saved metadata tags for {file_path.name}")
        except Exception as e:
            self.show_error(f"Error saving scene tags: {e}")

    def on_new_manuscript_clicked(self, btn):
        dialog = Gtk.Dialog(title="Scaffold New Novel Manuscript", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Create Novel", Gtk.ResponseType.OK)
        dialog.set_default_size(460, 260)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        box.pack_start(Gtk.Label(label="Manuscript Name (e.g. Way-of-Kings, Dune):", xalign=0), False, False, 0)
        entry_ms = Gtk.Entry()
        entry_ms.set_text("New-Novel")
        box.pack_start(entry_ms, False, False, 0)

        box.pack_start(Gtk.Label(label="Author Name:", xalign=0), False, False, 0)
        entry_author = Gtk.Entry()
        entry_author.set_text("Author Name")
        box.pack_start(entry_author, False, False, 0)

        dialog.show_all()
        res = dialog.run()
        ms_name = entry_ms.get_text().strip()
        author_name = entry_author.get_text().strip()
        dialog.destroy()

        if res == Gtk.ResponseType.OK and ms_name:
            def _worker():
                cmd = [
                    "bash",
                    str(PROJECT_ROOT / "scripts" / "arcanum"),
                    "new", "manuscript",
                    ms_name,
                    "--author", author_name
                ]
                subprocess.run(cmd, capture_output=True, text=True)
                if HAS_GTK and GLib is not None:
                    GLib.idle_add(self.refresh_all_discovery)
            self._start_worker(_worker)

    def on_add_volume_clicked(self, btn):
        if not self.current_manuscript_path:
            self.show_error("Please select an active manuscript first.")
            return

        dialog = Gtk.Dialog(title="Add Book / Volume to Manuscript", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Add Book", Gtk.ResponseType.OK)
        dialog.set_default_size(440, 200)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        box.pack_start(Gtk.Label(label="Volume Name (e.g. Book-02, Volume-02):", xalign=0), False, False, 0)
        entry_vol = Gtk.Entry()
        entry_vol.set_text("Book-02")
        box.pack_start(entry_vol, False, False, 0)

        dialog.show_all()
        res = dialog.run()
        vol_name = entry_vol.get_text().strip()
        dialog.destroy()

        if res == Gtk.ResponseType.OK and vol_name:
            def _worker():
                cmd = [
                    "bash",
                    str(PROJECT_ROOT / "scripts" / "arcanum"),
                    "volume",
                    Path(self.current_manuscript_path).name,
                    vol_name
                ]
                subprocess.run(cmd, capture_output=True, text=True)
                if HAS_GTK and GLib is not None:
                    GLib.idle_add(self.refresh_all_discovery)
            self._start_worker(_worker)

    def on_fork_draft_clicked(self, btn):
        if not self.current_manuscript_path:
            self.show_error("No active manuscript selected.")
            return

        dialog = Gtk.Dialog(title="Fork Next Draft Version", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Fork Draft", Gtk.ResponseType.OK)
        dialog.set_default_size(440, 200)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        box.pack_start(Gtk.Label(label="New Draft Name (e.g. Draft-02):", xalign=0), False, False, 0)
        entry_draft = Gtk.Entry()
        entry_draft.set_text("Draft-02")
        box.pack_start(entry_draft, False, False, 0)

        dialog.show_all()
        res = dialog.run()
        d_name = entry_draft.get_text().strip()
        dialog.destroy()

        if res == Gtk.ResponseType.OK and d_name:
            def _worker():
                cmd = [
                    "bash",
                    str(PROJECT_ROOT / "scripts" / "arcanum"),
                    "draft",
                    self.current_manuscript_path,
                    d_name
                ]
                subprocess.run(cmd, capture_output=True, text=True)
                if HAS_GTK and GLib is not None:
                    GLib.idle_add(self.refresh_all_discovery)
            self._start_worker(_worker)

    def on_launch_novelwriter(self, btn):
        if self.current_manuscript_path:
            launch_external_app("novelwriter", self.current_manuscript_path)
            self.set_status(f"Opening {Path(self.current_manuscript_path).name} in novelWriter...")
        else:
            self.show_error("No active manuscript selected.")

    def on_launch_focuswriter(self, btn):
        target = self.current_selected_scene_file or self.current_manuscript_path or str(MANUSCRIPTS_DIR)
        launch_external_app("focuswriter", target)
        self.set_status("Launching FocusWriter...")

    def on_open_word_processor_clicked(self, btn):
        if not self.current_manuscript_path:
            self.show_error("No active manuscript selected.")
            return
        draft = self.combo_draft_list.get_active_id() if self.combo_draft_list else "Draft-01"
        vol = self.combo_draft_vol.get_active_id() if self.combo_draft_vol else "Book-01"
        docx_file = Path(self.current_manuscript_path) / vol / draft / f"{draft}_Manuscript.docx"
        if not docx_file.exists():
            build_manuscript_docx(Path(self.current_manuscript_path), draft_name=draft)
        open_in_word_processor(docx_file)
        self.set_status(f"Opening {docx_file.name} in Word Processor...")

    def on_sync_docx_clicked(self, btn):
        if not self.current_manuscript_path:
            self.show_error("No active manuscript selected.")
            return
        draft = self.combo_draft_list.get_active_id() if self.combo_draft_list else "Draft-01"

        def _do_sync():
            res = sync_manuscript_docx(Path(self.current_manuscript_path), draft_name=draft)
            if HAS_GTK and GLib is not None:
                def _done():
                    dialog = Gtk.MessageDialog(
                        transient_for=self if isinstance(self, Gtk.Window) else None,
                        flags=0,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.OK,
                        text="DOCX Synchronization Complete"
                    )
                    dialog.format_secondary_text(
                        f"• Markdown -> DOCX updated: {len(res.get('md_to_docx', []))}\n"
                        f"• DOCX -> Markdown imported: {len(res.get('docx_to_md', []))}\n"
                        f"• Errors: {len(res.get('errors', []))}"
                    )
                    dialog.run()
                    dialog.destroy()
                GLib.idle_add(_done)
        self._start_worker(_do_sync)

    def on_docx_settings_clicked(self, btn):
        dialog = Gtk.Dialog(title="DOCX Manuscript Formatting & Submission Presets", parent=self if isinstance(self, Gtk.Window) else None, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Apply", Gtk.ResponseType.APPLY)
        dialog.set_default_size(520, 420)
        box = dialog.get_content_area()
        box.set_border_width(14)
        box.set_spacing(10)

        cfg = get_docx_config()
        active_preset = get_active_docx_preset_name()
        presets = list_docx_presets()

        lbl_desc = Gtk.Label(label="<b>Configure standard Word (.docx) formatting for MS Word, Google Docs & Submission:</b>", use_markup=True, xalign=0)
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

        lbl_info = Gtk.Label(xalign=0)
        lbl_info.set_line_wrap(True)

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
                draft = self.combo_draft_list.get_active_id() if self.combo_draft_list else "Draft-01"
                build_manuscript_docx(Path(self.current_manuscript_path), draft_name=draft)
        dialog.destroy()

    def on_view_redline_clicked(self, btn):
        if not self.current_manuscript_path:
            self.show_error("No active manuscript selected.")
            return
        d_a = self.combo_diff_a.get_active_id() if self.combo_diff_a else "Draft-01"
        d_b = self.combo_diff_b.get_active_id() if self.combo_diff_b else "Draft-02"
        vol = self.combo_draft_vol.get_active_id() if self.combo_draft_vol else "Book-01"
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "lib" / "manuscript_diff.py"),
            self.current_manuscript_path,
            d_b, d_a,
            "--book", vol
        ]
        self._run_dialog_html_cmd(cmd, is_svg=False, status_msg=f"Comparing {d_b} against {d_a}...")

    def on_lo_compare_clicked(self, btn):
        if not self.current_manuscript_path:
            self.show_error("No active manuscript selected.")
            return
        d_a = self.combo_diff_a.get_active_id() if self.combo_diff_a else "Draft-01"
        d_b = self.combo_diff_b.get_active_id() if self.combo_diff_b else "Draft-02"
        vol = self.combo_draft_vol.get_active_id() if self.combo_draft_vol else "Book-01"
        docx_a = Path(self.current_manuscript_path) / vol / d_a / f"{d_a}_Manuscript.docx"
        docx_b = Path(self.current_manuscript_path) / vol / d_b / f"{d_b}_Manuscript.docx"
        if not docx_a.exists():
            build_manuscript_docx(Path(self.current_manuscript_path), draft_name=d_a)
        if not docx_b.exists():
            build_manuscript_docx(Path(self.current_manuscript_path), draft_name=d_b)
        cmd = ["libreoffice", "--writer", str(docx_b), str(docx_a)]
        try:
            subprocess.Popen(cmd)
            self.set_status("Opening LibreOffice Document Comparison...")
        except Exception as e:
            self.show_error(f"Failed to launch LibreOffice: {e}")
