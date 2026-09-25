"""
Ars Arcanum GTK 3 Presentation Package (scripts/lib/ui_gtk3)
============================================================
Modular desktop interface for sovereign authoring and speculative worldbuilding.
"""

import sys
from pathlib import Path

# Ensure library path resolution
_LIB_DIR = Path(__file__).resolve().parent.parent
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

try:
    from lib.ui_gtk3.common import _CSS_LOADED, HAS_GTK, _cached_which, _flush_tool_cache
    from lib.ui_gtk3.window import ArcanumApp, ScriptoriumApp, main, run_gtk3_app
except ImportError:
    from ui_gtk3.common import _CSS_LOADED, HAS_GTK, _cached_which, _flush_tool_cache
    from ui_gtk3.window import ArcanumApp, ScriptoriumApp, main, run_gtk3_app

__all__ = [
    "HAS_GTK",
    "_CSS_LOADED",
    "ArcanumApp",
    "ScriptoriumApp",
    "_cached_which",
    "_flush_tool_cache",
    "main",
    "run_gtk3_app",
]
