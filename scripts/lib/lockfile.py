#!/usr/bin/env python3
"""
Ars Arcanum File Locking & Concurrency Management (scripts/lib/lockfile.py)
==========================================================================
Provides fail-safe advisory file locking for world vaults and manuscripts.
Ensures coordinated access between CLI operations, background Git snapshots,
and the desktop Control Center.
"""

import json
import os
import sys
import time
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any

# Detect POSIX fcntl vs Windows msvcrt
HAS_FCNTL = False
HAS_MSVCRT = False
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    try:
        import msvcrt
        HAS_MSVCRT = True
    except ImportError:
        pass


class LockError(Exception):
    """Base exception for file locking errors."""
    pass


class LockTimeoutError(LockError):
    """Raised when acquiring a lock exceeds the timeout."""
    pass


class ArcanumLock(AbstractContextManager):
    """
    Advisory file lock context manager for world vaults and manuscript repositories.
    Guarantees cleanup on process exit or unexpected exceptions.
    """

    def __init__(
        self,
        lock_path: Path | str,
        timeout: float = 10.0,
        exclusive: bool = True,
        op_name: str = "operation"
    ) -> None:
        self.lock_path = Path(lock_path).resolve()
        self.timeout = max(0.0, timeout)
        self.exclusive = exclusive
        self.op_name = op_name
        self._fd: int | None = None
        self._is_locked = False

    def acquire(self) -> "ArcanumLock":
        """Attempts to acquire the file lock within the timeout window."""
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        start_time = time.monotonic()

        while True:
            try:
                # Open or create lock file with read/write access
                self._fd = os.open(str(self.lock_path), os.O_RDWR | os.O_CREAT, 0o600)

                if HAS_FCNTL:
                    flags = (fcntl.LOCK_EX if self.exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB
                    fcntl.flock(self._fd, flags)
                    self._is_locked = True
                elif HAS_MSVCRT:
                    msvcrt.locking(self._fd, msvcrt.LK_NBLCK, 1)
                    self._is_locked = True
                else:
                    # Fallback file descriptor allocation
                    self._is_locked = True

                # Write diagnostic metadata into the lock file
                try:
                    meta = {
                        "pid": os.getpid(),
                        "timestamp": time.time(),
                        "op_name": self.op_name,
                        "script": sys.argv[0] if sys.argv else "arcanum",
                    }
                    data = json.dumps(meta).encode("utf-8")
                    os.ftruncate(self._fd, 0)
                    os.lseek(self._fd, 0, os.SEEK_SET)
                    os.write(self._fd, data)
                except Exception:
                    pass

                return self

            except (BlockingIOError, OSError, PermissionError) as err:
                if self._fd is not None:
                    try:
                        os.close(self._fd)
                    except OSError:
                        pass
                    self._fd = None

                elapsed = time.monotonic() - start_time
                if elapsed >= self.timeout:
                    raise LockTimeoutError(
                        f"Timed out after {self.timeout:.1f}s waiting to acquire lock on '{self.lock_path}' "
                        f"(operation: '{self.op_name}')"
                    ) from err
                time.sleep(0.05)

    def release(self) -> None:
        """Releases the held lock and closes descriptor."""
        if self._fd is not None and self._is_locked:
            try:
                if HAS_FCNTL:
                    fcntl.flock(self._fd, fcntl.LOCK_UN)
                elif HAS_MSVCRT:
                    try:
                        os.lseek(self._fd, 0, os.SEEK_SET)
                        msvcrt.locking(self._fd, msvcrt.LK_UNLCK, 1)
                    except OSError:
                        pass
            except OSError:
                pass
            finally:
                try:
                    os.close(self._fd)
                except OSError:
                    pass
                self._fd = None
                self._is_locked = False

    def __enter__(self) -> "ArcanumLock":
        return self.acquire()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.release()


def acquire_world_lock(world_dir: Path | str, op_name: str = "world_write", timeout: float = 10.0) -> ArcanumLock:
    """Convenience helper to lock a world vault."""
    lock_file = Path(world_dir) / ".arcanum.lock"
    return ArcanumLock(lock_file, timeout=timeout, op_name=op_name)


def acquire_manuscript_lock(ms_dir: Path | str, op_name: str = "manuscript_write", timeout: float = 10.0) -> ArcanumLock:
    """Convenience helper to lock a manuscript workspace."""
    lock_file = Path(ms_dir) / ".arcanum.lock"
    return ArcanumLock(lock_file, timeout=timeout, op_name=op_name)
