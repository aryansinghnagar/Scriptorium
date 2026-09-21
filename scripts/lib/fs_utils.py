#!/usr/bin/env python3
"""
Ars Arcanum Filesystem & Atomic Storage Utilities (scripts/lib/fs_utils.py)
Provides crash-resilient transactional file writes and secure directory operations.
"""

import os
import tempfile
from pathlib import Path


def atomic_write(path: Path | str, data: str | bytes, encoding: str = "utf-8") -> None:
    """
    Safely and atomically writes data to path using a staged temporary file and os.replace.
    Ensures that interrupted writes never leave corrupted or truncated files.
    """
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    is_bytes = isinstance(data, (bytes, bytearray))
    mode = "wb" if is_bytes else "w"

    # Stage temporary file in the same directory to ensure same filesystem for os.replace
    prefix = f".{target.name}."
    fd, tmp_path_str = tempfile.mkstemp(dir=target.parent, prefix=prefix, suffix=".tmp")
    tmp_path = Path(tmp_path_str)

    try:
        if is_bytes:
            with os.fdopen(fd, mode) as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        else:
            with os.fdopen(fd, mode, encoding=encoding, newline="") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())

        # Preserve permissions of the original file if it exists
        if target.exists():
            try:
                os.chmod(tmp_path, target.stat().st_mode & 0o7777)
            except OSError:
                pass

        os.replace(tmp_path, target)

        # On POSIX systems, fsync parent directory to ensure directory entry is flushed
        if hasattr(os, "O_DIRECTORY"):
            try:
                dfd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(dfd)
                finally:
                    os.close(dfd)
            except Exception:
                pass
    except BaseException:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass
        raise
