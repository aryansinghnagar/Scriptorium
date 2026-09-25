#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 CLI & Toolchain Bridge (scripts/lib/ui_gtk3/cli_bridge.py)
==========================================================================
Provides bridges between the GTK 3 interface and CLI scripts / external tools.
"""

import logging
import subprocess
from pathlib import Path

from lib.ui_gtk3.common import PROJECT_ROOT, _cached_which

logger = logging.getLogger("arcanum.ui_gtk3.cli_bridge")

try:
    from lib.config import (
        clear_backup_dest,
        get_active_docx_preset_name,
        get_backup_dest,
        get_docx_config,
        list_docx_presets,
        set_backup_dest,
        set_docx_option,
        set_docx_preset,
    )
    from lib.docx_sync import build_manuscript_docx, open_in_word_processor, sync_manuscript_docx
except Exception:
    try:
        from config import (
            clear_backup_dest,
            get_active_docx_preset_name,
            get_backup_dest,
            get_docx_config,
            list_docx_presets,
            set_backup_dest,
            set_docx_option,
            set_docx_preset,
        )
        from docx_sync import build_manuscript_docx, open_in_word_processor, sync_manuscript_docx
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


def launch_external_app(app_type: str, target_dir: str | Path) -> bool:
    """Launches Obsidian, novelWriter, or FocusWriter against target directory."""
    target = str(Path(target_dir).resolve())

    if app_type == "obsidian":
        if _cached_which("flatpak"):
            cmd = ["flatpak", "run", "md.obsidian.Obsidian", f"obsidian://open?path={target}"]
            try:
                subprocess.Popen(cmd)
                return True
            except Exception as e:
                logger.warning("Flatpak Obsidian launch failed: %s", e)
        if _cached_which("obsidian"):
            subprocess.Popen(["obsidian", target])
            return True

    elif app_type == "novelwriter":
        nwx_file = Path(target) / "nwProject.nwx"
        target_path = str(nwx_file) if nwx_file.exists() else target
        if _cached_which("flatpak"):
            cmd = ["flatpak", "run", "io.gitlab.novelwriter.novelWriter", target_path]
            try:
                subprocess.Popen(cmd)
                return True
            except Exception as e:
                logger.warning("Flatpak novelWriter launch failed: %s", e)
        if _cached_which("novelwriter"):
            subprocess.Popen(["novelwriter", target_path])
            return True

    # Generic workspace script fallback
    ws_script = PROJECT_ROOT / "scripts" / "open_workspace.sh"
    if ws_script.is_file():
        subprocess.Popen(["bash", str(ws_script), target])
        return True

    return False
