#!/usr/bin/env python3
"""
Scriptorium Desktop Application Launcher & Controller (scripts/scriptorium_app.py)
================================================================================
Modern dynamic presentation launcher with adaptive Libadwaita / GTK 4 support
and seamless GTK 3 & Zenity desktop fallbacks for Linux Mint, Debian & Wayland/X11.
"""

import sys
import argparse
import logging
from pathlib import Path

logger = logging.getLogger("scriptorium_app")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))


def try_launch_adw() -> bool:
    """Attempts to launch modern Libadwaita / GTK 4 interface."""
    try:
        from lib.ui_adw import HAS_ADW, run_adw_app
        if HAS_ADW:
            return run_adw_app() == 0
    except Exception as e:
        logger.debug("Failed to launch Libadwaita / GTK 4 UI: %s", e)
    return False


def try_launch_gtk3() -> bool:
    """Attempts to launch standard GTK 3 interface."""
    try:
        from lib.ui_gtk3 import HAS_GTK, run_gtk3_app
        if HAS_GTK:
            return run_gtk3_app()
    except Exception as e:
        logger.debug("Failed to launch GTK 3 UI: %s", e)
    return False


def fallback_zenity() -> int:
    """Invokes lightweight Zenity dialog control dashboard."""
    zenity_script = SCRIPT_DIR / "control_center.sh"
    if zenity_script.is_file():
        import subprocess
        res = subprocess.run(["bash", str(zenity_script)])
        return res.returncode
    print("[!] PyGObject / GTK is not installed in the current Python environment.", file=sys.stderr)
    print("[i] Run 'bash scripts/control_center.sh' for the graphical Zenity dashboard.", file=sys.stderr)
    return 2


def main():
    parser = argparse.ArgumentParser(description="Scriptorium Desktop Studio")
    parser.add_argument("--gtk3", action="store_true", help="Force GTK 3 presentation layer")
    parser.add_argument("--adw", "--gtk4", action="store_true", help="Force GTK 4 / Libadwaita presentation layer")
    parser.add_argument("--check-ui", action="store_true", help="Probe and print available UI backends")
    args, unknown = parser.parse_known_args()

    if args.check_ui:
        has_adw = False
        has_gtk3 = False
        try:
            from lib.ui_adw import HAS_ADW
            has_adw = HAS_ADW
        except Exception as e:
            logger.debug("Libadwaita probe failed: %s", e)
        try:
            from lib.ui_gtk3 import HAS_GTK
            has_gtk3 = HAS_GTK
        except Exception as e:
            logger.debug("GTK 3 probe failed: %s", e)
        print(f"Libadwaita / GTK 4: {'AVAILABLE' if has_adw else 'NOT AVAILABLE'}")
        print(f"GTK 3 (PyGObject): {'AVAILABLE' if has_gtk3 else 'NOT AVAILABLE'}")
        sys.exit(0)

    # 1. If GTK 4 / Libadwaita forced or default
    if not args.gtk3:
        if try_launch_adw():
            sys.exit(0)

    # 2. GTK 3 Fallback
    if try_launch_gtk3():
        sys.exit(0)

    # 3. Headless / Zenity Fallback
    rc = fallback_zenity()
    sys.exit(rc)


if __name__ == "__main__":
    main()
