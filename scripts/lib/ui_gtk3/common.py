#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 Common Presentation Utilities (scripts/lib/ui_gtk3/common.py)
==============================================================================
Provides shared paths, GTK imports, toolpath caches, styles, and dialog helpers.
"""

import logging
import shutil
import subprocess
import tempfile
import webbrowser
from pathlib import Path

logger = logging.getLogger("arcanum.ui_gtk3")

# GTK 3 Availability & GObject Introspection
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gdk, GLib, Gtk
    HAS_GTK = True
except (ImportError, ValueError):
    HAS_GTK = False
    class _DummyGtk:
        class Window:
            def __init__(self, *args, **kwargs): pass
        class Box:
            def __init__(self, *args, **kwargs): pass
        class Dialog:
            def __init__(self, *args, **kwargs): pass
        class ScrolledWindow:
            def __init__(self, *args, **kwargs): pass
        class TextView:
            def __init__(self, *args, **kwargs): pass
        class Label:
            def __init__(self, *args, **kwargs): pass
        class Button:
            def __init__(self, *args, **kwargs): pass
        class Notebook:
            def __init__(self, *args, **kwargs): pass
        class HeaderBar:
            def __init__(self, *args, **kwargs): pass
        class Statusbar:
            def __init__(self, *args, **kwargs): pass
        class ProgressBar:
            def __init__(self, *args, **kwargs): pass
        class ComboBoxText:
            def __init__(self, *args, **kwargs): pass
        class TreeView:
            def __init__(self, *args, **kwargs): pass
        class ListStore:
            def __init__(self, *args, **kwargs): pass
        class TreeStore:
            def __init__(self, *args, **kwargs): pass
        class FileChooserDialog:
            def __init__(self, *args, **kwargs): pass
        class Entry:
            def __init__(self, *args, **kwargs): pass
        class MessageDialog:
            def __init__(self, *args, **kwargs): pass
        class Separator:
            def __init__(self, *args, **kwargs): pass
        class Image:
            def __init__(self, *args, **kwargs): pass
        class Frame:
            pass
        class Grid:
            pass
        class CssProvider:
            pass
        class StyleContext:
            pass
        class AccelGroup:
            pass
        PositionType = type("PositionType", (), {"TOP": 0, "BOTTOM": 1, "LEFT": 2, "RIGHT": 3})
        Orientation = type("Orientation", (), {"HORIZONTAL": 0, "VERTICAL": 1})
        WindowPosition = type("WindowPosition", (), {"CENTER": 1})
        ResponseType = type("ResponseType", (), {"OK": -5, "CANCEL": -6, "CLOSE": -7, "APPLY": -10})
        DialogFlags = type("DialogFlags", (), {"MODAL": 1, "DESTROY_WITH_PARENT": 2})
        MessageType = type("MessageType", (), {"INFO": 0, "WARNING": 1, "QUESTION": 2, "ERROR": 3})
        ButtonsType = type("ButtonsType", (), {"OK": 1, "CLOSE": 2, "CANCEL": 3, "YES_NO": 4, "OK_CANCEL": 5})
        STYLE_PROVIDER_PRIORITY_APPLICATION = 600
        STYLE_PROVIDER_PRIORITY_USER = 800
    Gtk = _DummyGtk()  # type: ignore[assignment]
    Gdk = None  # type: ignore[assignment]
    GLib = None  # type: ignore[assignment]

# Standard Filesystem Paths
HOME_DIR = Path.home()
UNIVERSES_DIR = HOME_DIR / "Universes"
MANUSCRIPTS_DIR = HOME_DIR / "Manuscripts"
WORLDS_DIR = HOME_DIR / "Worlds"
UI_GTK3_DIR = Path(__file__).resolve().parent
LIB_DIR = UI_GTK3_DIR.parent
SCRIPT_DIR = LIB_DIR.parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Module-level tool lookup cache
_TOOL_CACHE: dict[str, str | None] = {}

def _cached_which(cmd: str) -> str | None:
    if cmd not in _TOOL_CACHE:
        _TOOL_CACHE[cmd] = shutil.which(cmd)
    return _TOOL_CACHE[cmd]

def _flush_tool_cache() -> None:
    _TOOL_CACHE.clear()

# CSS Singleton guard & high-contrast state
_CSS_LOADED = False
_HIGH_CONTRAST_ACTIVE = False
_CSS_PROVIDER = None


def setup_styles(high_contrast: bool = False) -> None:
    """Applies modern desktop CSS styling and accessibility theme overrides."""
    global _CSS_LOADED, _CSS_PROVIDER, _HIGH_CONTRAST_ACTIVE
    if not HAS_GTK or Gdk is None:
        return

    _HIGH_CONTRAST_ACTIVE = high_contrast
    if _CSS_PROVIDER is None:
        _CSS_PROVIDER = Gtk.CssProvider()

    if high_contrast:
        css = b"""
        .title-label { font-size: 16px; font-weight: bold; color: #ffffff; }
        .section-header { font-size: 14px; font-weight: bold; color: #ffff00; }
        .card-box { background: #000000; border: 2px solid #ffffff; border-radius: 4px; padding: 10px; margin: 4px; color: #ffffff; }
        .stat-value { font-size: 20px; font-weight: bold; color: #00ff00; }
        .inspector-box { background: #000000; border: 2px solid #00ffff; border-radius: 4px; padding: 10px; color: #ffffff; }
        .danger-btn { background: #ff0000; color: #ffffff; font-weight: bold; }
        """
    else:
        css = b"""
        .title-label { font-size: 15px; font-weight: bold; }
        .section-header { font-size: 13px; font-weight: bold; color: #4a90d9; }
        .card-box { background: alpha(@theme_bg_color, 0.5); border: 1px solid alpha(@theme_fg_color, 0.15); border-radius: 6px; padding: 10px; margin: 4px; }
        .stat-value { font-size: 19px; font-weight: bold; color: #2e7d32; }
        .inspector-box { background: alpha(@theme_bg_color, 0.7); border: 1px solid alpha(#4a90d9, 0.3); border-radius: 6px; padding: 10px; }
        .danger-btn { background: #d32f2f; color: white; }
        """

    try:
        _CSS_PROVIDER.load_from_data(css)
        screen = Gdk.Screen.get_default()
        if screen:
            Gtk.StyleContext.add_provider_for_screen(screen, _CSS_PROVIDER, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        _CSS_LOADED = True
    except Exception as e:
        logger.debug("Could not apply GTK CSS styling: %s", e)


def toggle_high_contrast() -> bool:
    """Toggles high-contrast accessibility mode and returns new state."""
    global _HIGH_CONTRAST_ACTIVE
    new_state = not _HIGH_CONTRAST_ACTIVE
    setup_styles(high_contrast=new_state)
    return new_state


class DialogHelpersMixin:
    """Standard dialog shell construction and execution mixin."""

    def _create_dialog_shell(self, title: str, width: int = 680, height: int = 480):
        if not HAS_GTK:
            return None, None
        dialog = Gtk.Dialog(
            title=title,
            parent=self if isinstance(self, Gtk.Window) else None,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT
        )
        dialog.set_default_size(width, height)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        content_area = dialog.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_border_width(12)
        content_area.pack_start(box, True, True, 0)
        return dialog, box

    def _create_dialog_output_view(self):
        if not HAS_GTK:
            return None, None
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        view = Gtk.TextView()
        view.set_editable(False)
        view.set_cursor_visible(False)
        view.set_wrap_mode(Gtk.WrapMode.WORD)
        view.set_monospace(True)
        buf = view.get_buffer()
        scrolled.add(view)
        return scrolled, buf

    def _run_dialog_cmd(self, cmd: list[str], out_buf, status_msg: str | None = None) -> None:
        if status_msg and hasattr(self, "set_status"):
            self.set_status(status_msg)
        if out_buf:
            out_buf.set_text("Executing command...\n\n")

        def _worker():
            try:
                res = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=120
                )
                output = res.stdout if res.returncode == 0 else f"Error (exit code {res.returncode}):\n{res.stderr}\n{res.stdout}"
            except Exception as e:
                output = f"Execution failed: {e}"

            if HAS_GTK and GLib is not None:
                GLib.idle_add(lambda: out_buf.set_text(output) if out_buf else None)
                if hasattr(self, "set_status"):
                    GLib.idle_add(lambda: self.set_status("Ready"))

        if hasattr(self, "_start_worker"):
            self._start_worker(_worker)
        else:
            _worker()

    def _run_dialog_html_cmd(self, base_cmd: list[str], is_svg: bool = False, status_msg: str | None = None) -> None:
        if status_msg and hasattr(self, "set_status"):
            self.set_status(status_msg)

        suffix = ".svg" if is_svg else ".html"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_out:
            out_path = tmp_out.name

        cmd = list(base_cmd)
        if "--svg" in cmd or "--html" in cmd:
            if is_svg and "--svg" not in cmd:
                cmd.extend(["--svg", out_path])
            elif not is_svg and "--html" not in cmd:
                cmd.extend(["--html", out_path])
        else:
            flag = "--svg" if is_svg else "--html"
            cmd.extend([flag, out_path])

        def _worker():
            try:
                subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
                if Path(out_path).exists() and Path(out_path).stat().st_size > 0:
                    webbrowser.open(f"file://{out_path}")
            except Exception as e:
                logger.warning("Failed running HTML/SVG export command: %s", e)

            if hasattr(self, "set_status") and HAS_GTK and GLib is not None:
                GLib.idle_add(lambda: self.set_status("Ready"))

        if hasattr(self, "_start_worker"):
            self._start_worker(_worker)
        else:
            _worker()
