#!/usr/bin/env python3
"""
Ars Arcanum Bootstrap Utilities (scripts/lib/_bootstrap.py)
===========================================================
Shared bootstrap module providing:
1. Universal UTF-8 stream re-encoding for POSIX/Windows CLI safety.
2. Standardized sys.path insertion for domain engines.
3. Fail-safe export of atomic_write primitive.
4. Common CLI execution helpers.
"""

import sys
from pathlib import Path
from typing import Any

# 1. UTF-8 standard stream re-encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 2. Path resolution
LIB_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = LIB_DIR.parent
PROJECT_ROOT = SCRIPTS_DIR.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

# 3. Fail-safe atomic_write export
try:
    from lib.fs_utils import atomic_write
except ImportError:
    try:
        from fs_utils import atomic_write  # type: ignore[no-redef]
    except ImportError:
        def atomic_write(path: Path | str, data: Any, encoding: str = "utf-8") -> None:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(data, (bytes, bytearray)):
                p.write_bytes(data)
            else:
                p.write_text(str(data), encoding=encoding)


# 4. Volume and identifier validation helpers (Path Traversal Defense)
def validate_volume_name(vol: str) -> str:
    """Validate volume identifier against path traversal and forbidden characters.

    Returns the validated volume name or raises ValueError.
    """
    if not vol:
        raise ValueError("Volume name cannot be empty.")
    if vol in ("all", "ALL", "all-books", "omnibus"):
        return vol
    if ".." in vol or "/" in vol or "\\" in vol:
        raise ValueError(f"Invalid volume name '{vol}': path traversal characters ('..', '/', '\\') are not allowed.")
    import re

    if not re.match(r"^[A-Za-z0-9_-]+$", vol):
        raise ValueError(f"Invalid volume name '{vol}': only alphanumeric characters, hyphens, and underscores allowed.")
    return vol


def sanitize_identifier(name: str, fallback: str = "item") -> str:
    """Sanitize a name to a safe filesystem identifier token [A-Za-z0-9_-]."""
    import re

    safe = re.sub(r"[^A-Za-z0-9_-]", "", name or "")
    return safe or fallback


__all__ = [
    "LIB_DIR",
    "PROJECT_ROOT",
    "SCRIPTS_DIR",
    "atomic_write",
    "sanitize_identifier",
    "validate_volume_name",
]
