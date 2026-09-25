#!/usr/bin/env python3
"""
Ars Arcanum Desktop Application Facade (scripts/lib/ui_gtk3.py)
==============================================================
Backward-compatible wrapper exposing the modular `lib.ui_gtk3` package.
"""

import sys
from pathlib import Path

# Ensure library path resolution
_LIB_DIR = Path(__file__).resolve().parent
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

try:
    from lib.ui_gtk3 import (
        _CSS_LOADED,
        HAS_GTK,
        ArcanumApp,
        ScriptoriumApp,
        _cached_which,
        _flush_tool_cache,
        main,
        run_gtk3_app,
    )
    from lib.ui_gtk3.common import (
        HOME_DIR,
        MANUSCRIPTS_DIR,
        PROJECT_ROOT,
        SCRIPT_DIR,
        UNIVERSES_DIR,
        WORLDS_DIR,
    )
except ImportError:
    from ui_gtk3 import (
        _CSS_LOADED,
        HAS_GTK,
        ArcanumApp,
        ScriptoriumApp,
        _cached_which,
        _flush_tool_cache,
        main,
        run_gtk3_app,
    )
    from ui_gtk3.common import (
        HOME_DIR,
        MANUSCRIPTS_DIR,
        PROJECT_ROOT,
        SCRIPT_DIR,
        UNIVERSES_DIR,
        WORLDS_DIR,
    )

__all__ = [
    "HAS_GTK",
    "HOME_DIR",
    "MANUSCRIPTS_DIR",
    "PROJECT_ROOT",
    "SCRIPT_DIR",
    "UNIVERSES_DIR",
    "WORLDS_DIR",
    "_CSS_LOADED",
    "ArcanumApp",
    "ScriptoriumApp",
    "_cached_which",
    "_flush_tool_cache",
    "main",
    "run_gtk3_app",
]

if __name__ == "__main__":
    main()
